const tg = window.Telegram.WebApp;
tg.expand();

// Application State
const state = {
    categories: [],
    products: [],
    activeCategoryId: null,
    cart: {}, // productId -> { product, quantity }
    isCartView: false
};

// Formatting utilities
const formatPrice = (price) => {
    return Number(price).toLocaleString('uz-UZ') + " so'm";
};

// Core Logic: Calculate Totals
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

// UI: Update MainButton
const updateMainButton = () => {
    const { items, total } = getCartTotals();
    
    if (items > 0) {
        const text = state.isCartView
            ? '✅ Buyurtma berish (' + formatPrice(total) + ')'
            : '🛒 Savat (' + formatPrice(total) + ')';
        
        tg.MainButton.setParams({
            text: text,
            is_visible: true,
            color: state.isCartView ? '#31b545' : '#248bed'
        });
    } else {
        tg.MainButton.hide();
        if (state.isCartView) toggleCartView();
    }
};

// UI: Update Product Counters Everywhere
const updateProductUI = (productId) => {
    const item = state.cart[productId];
    const qty = item ? item.quantity : 0;
    
    // Find all containers for this product (could be in catalog and cart)
    const containers = document.querySelectorAll('.action-container-' + productId);
    containers.forEach(container => {
        const product = state.products.find(p => p.id == productId);
        if (!product) return;
        
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

// Actions
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
    const product = item.product;
    
    if (newQty <= 0) {
        delete state.cart[productId];
        if (state.isCartView) {
            renderCart(); // Full re-render needed for cart view cleanup
        } else {
            updateProductUI(productId);
        }
    } else if (newQty > product.stock) {
        tg.showAlert('Omborda faqat ' + product.stock + ' ta mahsulot bor.');
        return;
    } else {
        item.quantity = newQty;
        updateProductUI(productId);
    }
    
    updateMainButton();
    tg.HapticFeedback.impactOccurred('light');
};

window.clearCart = () => {
    if (confirm("Savatchani bo'shatmoqchimisiz?")) {
        state.cart = {};
        if (state.isCartView) toggleCartView();
        renderProducts();
        updateMainButton();
        tg.HapticFeedback.notificationOccurred('warning');
    }
};

// UI: Navigation
const toggleCartView = () => {
    state.isCartView = !state.isCartView;
    const tabs = document.getElementById('tabsContainer');
    const products = document.getElementById('productsGrid');
    const cartView = document.getElementById('cartView');
    
    if (state.isCartView) {
        tabs.style.display = 'none';
        products.style.display = 'none';
        cartView.style.display = 'block';
        tg.BackButton.show();
        renderCart();
    } else {
        tabs.style.display = 'block';
        products.style.display = 'grid';
        cartView.style.display = 'none';
        tg.BackButton.hide();
        renderProducts();
    }
    updateMainButton();
};

// Event Listeners
tg.MainButton.onClick(() => {
    if (!state.isCartView) {
        toggleCartView();
    } else {
        const data = JSON.stringify(Object.values(state.cart));
        tg.sendData(data);
    }
});

tg.BackButton.onClick(() => {
    if (state.isCartView) toggleCartView();
});

// UI: Rendering
const createProductCard = (product) => {
    const cartItem = state.cart[product.id];
    const qty = cartItem ? cartItem.quantity : 0;
    const imgUrl = product.image_id ? '/api/image/' + product.image_id : 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=';
    
    const card = document.createElement('div');
    card.className = 'product-card';
    
    let actionHtml = '';
    if (qty === 0) {
        actionHtml = '<button class="add-btn" onclick="addToCart(' + product.id + ')">Qo\'shish</button>';
    } else {
        actionHtml = 
            '<div class="qty-controls">' +
            '<button class="qty-btn" onclick="updateQty(' + product.id + ', -1)">-</button>' +
            '<span class="qty-val">' + qty + '</span>' +
            '<button class="qty-btn" onclick="updateQty(' + product.id + ', 1)">+</button>' +
            '</div>';
    }
    
    card.innerHTML = 
        '<img src="' + imgUrl + '" class="product-img" alt="' + product.name + '" loading="lazy">' +
        '<div class="product-info">' +
            '<div class="product-name">' + product.name + '</div>' +
            '<div class="product-desc">' + (product.description || '') + '</div>' +
            '<div class="product-price">' + formatPrice(product.price) + '</div>' +
            '<div class="action-container-' + product.id + '">' + actionHtml + '</div>' +
        '</div>';
    return card;
};

const renderCategories = () => {
    const tabsContainer = document.getElementById('categoryTabs');
    tabsContainer.innerHTML = '';
    
    // Filter out categories without in-stock products
    const validCategories = state.categories.filter(cat => 
        state.products.some(p => p.category_id == cat.id && p.stock > 0)
    );
    
    if (validCategories.length === 0) return;
    if (state.activeCategoryId === null) state.activeCategoryId = validCategories[0].id;
    
    validCategories.forEach(cat => {
        const li = document.createElement('li');
        li.className = 'tab ' + (cat.id == state.activeCategoryId ? 'active' : '');
        li.textContent = cat.name;
        li.onclick = () => {
            state.activeCategoryId = cat.id;
            renderCategories();
            renderProducts();
        };
        tabsContainer.appendChild(li);
    });
};

const renderProducts = () => {
    const grid = document.getElementById('productsGrid');
    grid.innerHTML = '';
    
    const filtered = state.products.filter(p => p.category_id == state.activeCategoryId && p.stock > 0);
    if (filtered.length === 0) {
        grid.innerHTML = '<div class="loading">Bu bo\'limda mahsulotlar yo\'q.</div>';
        return;
    }
    
    filtered.forEach(p => grid.appendChild(createProductCard(p)));
};

const renderCart = () => {
    const grid = document.getElementById('cartGrid');
    grid.innerHTML = '';
    
    const items = Object.values(state.cart);
    if (items.length === 0) {
        grid.innerHTML = '<div class="loading">Savatcha bo\'sh.</div>';
        return;
    }
    
    items.forEach(item => grid.appendChild(createProductCard(item.product)));
};

// App Initialization
const init = async () => {
    try {
        const res = await fetch('/api/data', { headers: { 'Bypass-Tunnel-Reminder': 'true' } });
        const data = await res.json();
        state.categories = data.categories;
        state.products = data.products;
        
        renderCategories();
        renderProducts();
        tg.ready();
    } catch (e) {
        console.error(e);
        document.getElementById('productsGrid').innerHTML = '<div class="loading">Yuklashda xatolik yuz berdi.</div>';
    }
};

init();
