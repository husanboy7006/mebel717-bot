const tg = window.Telegram.WebApp;
tg.expand();

let allCategories = [];
let allProducts = [];
let activeCategoryId = null;
let cart = {}; // { productId: { product, quantity } }
let isCartView = false;

// Helper function to format price
const formatPrice = (price) => {
    return Number(price).toLocaleString('uz-UZ') + " so'm";
};

// Calculate cart totals - single source of truth
const getCartTotals = () => {
    let totalItems = 0;
    let totalPrice = 0;
    const keys = Object.keys(cart);
    for (let i = 0; i < keys.length; i++) {
        const item = cart[keys[i]];
        const q = Number(item.quantity);
        const p = Number(item.product.price);
        totalItems += q;
        totalPrice += p * q;
    }
    return { totalItems, totalPrice };
};

// Update Telegram MainButton - SYNCHRONOUS, no debounce
const updateMainButton = () => {
    const { totalItems, totalPrice } = getCartTotals();
    
    if (totalItems > 0) {
        const text = isCartView
            ? '✅ Buyurtma berish (' + formatPrice(totalPrice) + ')'
            : '🛒 Savat (' + formatPrice(totalPrice) + ')';
        tg.MainButton.setParams({ text: text, is_visible: true });
    } else {
        tg.MainButton.hide();
        if (isCartView) toggleCartView();
    }
};

// Handle MainButton click
tg.MainButton.onClick(() => {
    if (!isCartView) {
        toggleCartView();
    } else {
        const data = JSON.stringify(Object.values(cart));
        tg.sendData(data);
    }
});

// Handle BackButton click
tg.BackButton.onClick(() => {
    if (isCartView) {
        toggleCartView();
    }
});

const toggleCartView = () => {
    isCartView = !isCartView;
    const tabs = document.getElementById('tabsContainer');
    const products = document.getElementById('productsGrid');
    const cartView = document.getElementById('cartView');
    
    if (isCartView) {
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

// Render Categories
const renderCategories = () => {
    const tabsContainer = document.getElementById('categoryTabs');
    tabsContainer.innerHTML = '';
    
    const availableCategories = allCategories.filter(cat => 
        allProducts.some(p => p.category_id === cat.id && p.stock > 0)
    );
    
    if(availableCategories.length === 0) return;
    
    if(activeCategoryId === null) {
        activeCategoryId = availableCategories[0].id;
    }
    
    availableCategories.forEach(cat => {
        const li = document.createElement('li');
        li.className = 'tab ' + (cat.id === activeCategoryId ? 'active' : '');
        li.textContent = cat.name;
        li.onclick = () => {
            activeCategoryId = cat.id;
            renderCategories();
            renderProducts();
        };
        tabsContainer.appendChild(li);
    });
};

const createProductCard = (product, qty) => {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    const imgUrl = product.image_id ? '/api/image/' + product.image_id : 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=';
    
    let actionHtml = '';
    if (qty === 0) {
        actionHtml = '<button class="add-btn" onclick="addToCart(' + product.id + ')">Qo\'shish</button>';
    } else {
        actionHtml = '<div class="qty-controls">' +
            '<button class="qty-btn" onclick="updateQty(' + product.id + ', -1)">-</button>' +
            '<span class="qty-val">' + qty + '</span>' +
            '<button class="qty-btn" onclick="updateQty(' + product.id + ', 1)">+</button>' +
            '</div>';
    }
    
    card.innerHTML = '<img src="' + imgUrl + '" class="product-img" alt="' + product.name + '" loading="lazy">' +
        '<div class="product-info">' +
            '<div class="product-name">' + product.name + '</div>' +
            '<div class="product-desc">' + (product.description || '') + '</div>' +
            '<div class="product-price">' + formatPrice(product.price) + '</div>' +
            '<div id="action-' + product.id + '">' + actionHtml + '</div>' +
        '</div>';
    return card;
};

// Render Products
const renderProducts = () => {
    const grid = document.getElementById('productsGrid');
    grid.innerHTML = '';
    
    const filteredProducts = allProducts.filter(p => p.category_id === activeCategoryId && p.stock > 0);
    
    if (filteredProducts.length === 0) {
        grid.innerHTML = '<div class="loading">Bu toifada mahsulot yo\'q</div>';
        return;
    }
    
    filteredProducts.forEach(product => {
        const cartItem = cart[product.id];
        const qty = cartItem ? cartItem.quantity : 0;
        grid.appendChild(createProductCard(product, qty));
    });
};

// Render Cart
const renderCart = () => {
    const grid = document.getElementById('cartGrid');
    grid.innerHTML = '';
    
    const cartItems = Object.values(cart);
    
    if (cartItems.length === 0) {
        grid.innerHTML = '<div class="loading">Savatcha bo\'sh</div>';
        return;
    }
    
    cartItems.forEach(item => {
        grid.appendChild(createProductCard(item.product, item.quantity));
    });
};

// Cart logic - update qty FIRST, then render, then update button SYNCHRONOUSLY
window.addToCart = (productId) => {
    const product = allProducts.find(p => p.id === productId);
    if (!product) return;
    
    cart[productId] = { product: product, quantity: 1 };
    renderProducts();
    updateMainButton();
    tg.HapticFeedback.impactOccurred('light');
};

window.updateQty = (productId, delta) => {
    if (!cart[productId]) return;
    const product = cart[productId].product;
    
    const newQty = cart[productId].quantity + delta;
    
    if (newQty <= 0) {
        delete cart[productId];
    } else if (newQty > product.stock) {
        tg.showAlert('Kechirasiz, omborda faqat ' + product.stock + ' ta bor.');
        return;
    } else {
        cart[productId].quantity = newQty;
    }
    
    if (isCartView) {
        renderCart();
    } else {
        renderProducts();
    }
    updateMainButton();
    tg.HapticFeedback.impactOccurred('light');
};

window.clearCart = () => {
    cart = {};
    if (isCartView) toggleCartView();
    renderProducts();
    updateMainButton();
    tg.HapticFeedback.notificationOccurred('warning');
};

// Fetch data
const initApp = async () => {
    try {
        const res = await fetch('/api/data', {
            headers: {
                'Bypass-Tunnel-Reminder': 'true'
            }
        });
        const data = await res.json();
        allCategories = data.categories;
        allProducts = data.products;
        
        renderCategories();
        renderProducts();
        tg.ready();
    } catch(e) {
        document.getElementById('productsGrid').innerHTML = '<div class="loading">Ma\'lumotlarni yuklashda xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.</div>';
    }
};

initApp();
