const tg = window.Telegram.WebApp;
tg.expand();

let allCategories = [];
let allProducts = [];
let activeCategoryId = null;
let cart = {}; // { productId: { product, quantity } }

// Helper function to format price
const formatPrice = (price) => {
    return price.toLocaleString('uz-UZ') + " so'm";
};

// Update Telegram MainButton
const updateMainButton = () => {
    const totalItems = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
    const totalPrice = Object.values(cart).reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
    
    if (totalItems > 0) {
        tg.MainButton.text = `Buyurtma berish (${formatPrice(totalPrice)})`;
        tg.MainButton.show();
    } else {
        tg.MainButton.hide();
    }
};

// Handle MainButton click
tg.MainButton.onClick(() => {
    // Send data back to the bot
    const data = JSON.stringify(Object.values(cart));
    tg.sendData(data);
});

// Render Categories
const renderCategories = () => {
    const tabsContainer = document.getElementById('categoryTabs');
    tabsContainer.innerHTML = '';
    
    // Only show categories that have products in stock
    const availableCategories = allCategories.filter(cat => 
        allProducts.some(p => p.category_id === cat.id && p.stock > 0)
    );
    
    if(availableCategories.length === 0) return;
    
    if(activeCategoryId === null) {
        activeCategoryId = availableCategories[0].id;
    }
    
    availableCategories.forEach(cat => {
        const li = document.createElement('li');
        li.className = `tab ${cat.id === activeCategoryId ? 'active' : ''}`;
        li.textContent = cat.name;
        li.onclick = () => {
            activeCategoryId = cat.id;
            renderCategories();
            renderProducts();
        };
        tabsContainer.appendChild(li);
    });
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
        
        const card = document.createElement('div');
        card.className = 'product-card';
        
        const imgUrl = product.image_id ? `/api/image/${product.image_id}` : 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=';
        
        let actionHtml = '';
        if (qty === 0) {
            actionHtml = `<button class="add-btn" onclick="addToCart(${product.id})">Qo'shish</button>`;
        } else {
            actionHtml = `
                <div class="qty-controls">
                    <button class="qty-btn" onclick="updateQty(${product.id}, -1)">-</button>
                    <span class="qty-val">${qty}</span>
                    <button class="qty-btn" onclick="updateQty(${product.id}, 1)">+</button>
                </div>
            `;
        }
        
        card.innerHTML = `
            <img src="${imgUrl}" class="product-img" alt="${product.name}" loading="lazy">
            <div class="product-info">
                <div class="product-name">${product.name}</div>
                <div class="product-desc">${product.description || ''}</div>
                <div class="product-price">${formatPrice(product.price)}</div>
                <div id="action-${product.id}">
                    ${actionHtml}
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
};

// Cart logic
window.addToCart = (productId) => {
    const product = allProducts.find(p => p.id === productId);
    if (!product) return;
    
    cart[productId] = { product, quantity: 1 };
    renderProducts();
    updateMainButton();
    tg.HapticFeedback.impactOccurred('light');
};

window.updateQty = (productId, delta) => {
    const product = allProducts.find(p => p.id === productId);
    if (!product || !cart[productId]) return;
    
    const newQty = cart[productId].quantity + delta;
    
    if (newQty <= 0) {
        delete cart[productId];
    } else if (newQty > product.stock) {
        tg.showAlert(`Kechirasiz, omborda faqat ${product.stock} ta bor.`);
        return;
    } else {
        cart[productId].quantity = newQty;
    }
    
    renderProducts();
    updateMainButton();
    tg.HapticFeedback.impactOccurred('light');
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
