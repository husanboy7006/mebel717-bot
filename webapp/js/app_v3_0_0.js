const tg = window.Telegram.WebApp;
tg.expand();

const state = {
    categories: [],
    products: [],
    activeCategoryId: null,
    cart: {}, // productId -> { product, quantity }
    isCartView: false
};

const formatPrice = (price) => {
    return Number(price).toLocaleString('uz-UZ') + " so'm";
};

const getCartTotals = () => {
    let items = 0;
    let total = 0;
    Object.values(state.cart).forEach(item => {
        const q = Number(item.quantity);
        const p = Number(item.product.price);
        items += q;
        total += p * q;
    });
    return { items, total };
};

// MAIN BUTTON CODE REMOVED AS REQUESTED. 
// We will rewrite this part together or use an alternative.
const updateMainButton = () => {
    const { items, total } = getCartTotals();
    
    // WebApp ichidagi narxni yangilab turamiz (bu aniq ishlaydi)
    const totalEl = document.getElementById('total-price-display');
    if (totalEl) {
        totalEl.textContent = items > 0 ? 'Jami: ' + formatPrice(total) : '';
    }

    // Telegram MainButton hozircha o'chiq holatda bo'ladi yoki minimal ishlaydi
    if (items > 0) {
        tg.MainButton.text = state.isCartView ? "Buyurtma berish" : "Savatchaga o'tish";
        tg.MainButton.show();
    } else {
        tg.MainButton.hide();
    }
};

const updateProductUI = (productId) => {
    const item = state.cart[productId];
    const qty = item ? item.quantity : 0;
    const containers = document.querySelectorAll('.action-container-' + productId);
    containers.forEach(container => {
        if (qty === 0) {
            container.innerHTML = '<button class="add-btn" onclick="addToCart(' + productId + ')">Qo\'shish</button>';
        } else {
            container.innerHTML = 
                '<div class="qty-controls">' +
                '<button class="qty-btn" onclick="updateQty(' + productId + ', -1)">-</button>' +
                '<span class="qty-val">' + qty + '</span>' +
                '<button class="qty-btn" onclick="updateQty(' + productId + ', 1)">+</button>' +
                '</div>';
        }
    });
};

window.addToCart = (productId) => {
    const product = state.products.find(p => p.id == productId);
    if (!product) return;
    state.cart[productId] = { product, quantity: 1 };
    updateProductUI(productId);
    updateMainButton();
    tg.HapticFeedback.impactOccurred('light');
};

window.updateQty = (productId, delta) => {
    const item = state.cart[productId];
    if (!item) return;
    const newQty = item.quantity + delta;
    if (newQty <= 0) {
        delete state.cart[productId];
        if (state.isCartView) { renderCart(); } else { updateProductUI(productId); }
    } else {
        item.quantity = newQty;
        updateProductUI(productId);
    }
    updateMainButton();
    tg.HapticFeedback.impactOccurred('light');
};

window.clearCart = () => {
    state.cart = {};
    if (state.isCartView) toggleCartView();
    renderProducts();
    updateMainButton();
};

const toggleCartView = () => {
    state.isCartView = !state.isCartView;
    document.getElementById('tabsContainer').style.display = state.isCartView ? 'none' : 'block';
    document.getElementById('productsGrid').style.display = state.isCartView ? 'none' : 'grid';
    document.getElementById('cartView').style.display = state.isCartView ? 'block' : 'none';
    
    if (state.isCartView) {
        tg.BackButton.show();
        renderCart();
    } else {
        tg.BackButton.hide();
        renderProducts();
    }
    updateMainButton();
};

tg.MainButton.onClick(() => {
    if (!state.isCartView) {
        toggleCartView();
    } else {
        tg.sendData(JSON.stringify(Object.values(state.cart)));
    }
});

tg.BackButton.onClick(() => {
    if (state.isCartView) toggleCartView();
});

const createProductCard = (product) => {
    const cartItem = state.cart[product.id];
    const qty = cartItem ? cartItem.quantity : 0;
    const imgUrl = product.image_id ? '/api/image/' + product.image_id : 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=';
    const card = document.createElement('div');
    card.className = 'product-card';
    card.innerHTML = 
        '<img src="' + imgUrl + '" class="product-img" alt="' + product.name + '">' +
        '<div class="product-info">' +
            '<div class="product-name">' + product.name + '</div>' +
            '<div class="product-desc">' + (product.description || '') + '</div>' +
            '<div class="product-price">' + formatPrice(product.price) + '</div>' +
            '<div class="action-container-' + product.id + '">' + 
                (qty === 0 ? '<button class="add-btn" onclick="addToCart(' + product.id + ')">Qo\'shish</button>' : 
                '<div class="qty-controls"><button class="qty-btn" onclick="updateQty(' + product.id + ', -1)">-</button><span class="qty-val">' + qty + '</span><button class="qty-btn" onclick="updateQty(' + product.id + ', 1)">+</button></div>') +
            '</div>' +
        '</div>';
    return card;
};

const renderCategories = () => {
    const container = document.getElementById('categoryTabs');
    container.innerHTML = '';
    const valid = state.categories.filter(c => state.products.some(p => p.category_id == c.id));
    if (valid.length === 0) return;
    if (state.activeCategoryId === null) state.activeCategoryId = valid[0].id;
    valid.forEach(c => {
        const li = document.createElement('li');
        li.className = 'tab ' + (c.id == state.activeCategoryId ? 'active' : '');
        li.textContent = c.name;
        li.onclick = () => { state.activeCategoryId = c.id; renderCategories(); renderProducts(); };
        container.appendChild(li);
    });
};

const renderProducts = () => {
    const grid = document.getElementById('productsGrid');
    grid.innerHTML = '';
    state.products.filter(p => p.category_id == state.activeCategoryId).forEach(p => grid.appendChild(createProductCard(p)));
};

const renderCart = () => {
    const grid = document.getElementById('cartGrid');
    grid.innerHTML = '';
    Object.values(state.cart).forEach(item => grid.appendChild(createProductCard(item.product)));
};

const init = async () => {
    try {
        const res = await fetch('/api/data', { headers: { 'Bypass-Tunnel-Reminder': 'true' } });
        const data = await res.json();
        state.categories = data.categories;
        state.products = data.products;
        renderCategories();
        renderProducts();
        tg.ready();
    } catch (e) { console.error(e); }
};

init();
