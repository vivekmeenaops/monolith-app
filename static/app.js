// Flipkart Clone - Frontend JavaScript
const API_BASE_URL = window.location.origin;

// State Management
const state = {
    token: localStorage.getItem('token'),
    user: null,
    cart: [],
    products: [],
    categories: []
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

async function initializeApp() {
    if (state.token) {
        await loadUserProfile();
        await loadCart();
    }
    await loadProducts();
    updateUI();
}

// Event Listeners
function setupEventListeners() {
    // Search
    document.getElementById('searchBtn')?.addEventListener('click', handleSearch);
    document.getElementById('searchInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });

    // Auth Buttons
    document.getElementById('loginBtn')?.addEventListener('click', () => openModal('loginModal'));
    document.getElementById('signupBtn')?.addEventListener('click', () => openModal('signupModal'));
    document.getElementById('logoutBtn')?.addEventListener('click', handleLogout);
    document.getElementById('profileBtn')?.addEventListener('click', () => openModal('profileModal'));
    document.getElementById('cartBtn')?.addEventListener('click', () => openModal('cartModal'));

    // Modal Close Buttons
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', () => closeModal(btn.closest('.modal').id));
    });

    // Click outside modal to close
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal(modal.id);
        });
    });

    // Forms
    document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
    document.getElementById('signupForm')?.addEventListener('submit', handleSignup);
}

// API Calls
async function apiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'API call failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        showAlert(error.message, 'error');
        throw error;
    }
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        const data = await apiCall('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({
                email: formData.get('email'),
                password: formData.get('password')
            })
        });

        state.token = data.access_token;
        localStorage.setItem('token', data.access_token);
        
        await loadUserProfile();
        await loadCart();
        
        closeModal('loginModal');
        showAlert('Login successful!', 'success');
        updateUI();
    } catch (error) {
        console.error('Login failed:', error);
    }
}

async function handleSignup(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    if (formData.get('password') !== formData.get('confirmPassword')) {
        showAlert('Passwords do not match', 'error');
        return;
    }

    try {
        await apiCall('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify({
                username: formData.get('username'),
                email: formData.get('email'),
                password: formData.get('password'),
                full_name: formData.get('fullName'),
                phone: formData.get('phone')
            })
        });

        showAlert('Registration successful! Please login.', 'success');
        closeModal('signupModal');
        openModal('loginModal');
    } catch (error) {
        console.error('Signup failed:', error);
    }
}

function handleLogout() {
    state.token = null;
    state.user = null;
    state.cart = [];
    localStorage.removeItem('token');
    updateUI();
    showAlert('Logged out successfully', 'success');
}

async function loadUserProfile() {
    try {
        const data = await apiCall('/api/users/profile');
        state.user = data;
    } catch (error) {
        console.error('Failed to load profile:', error);
        handleLogout();
    }
}

// Products
async function loadProducts(category = null, search = null) {
    try {
        let endpoint = '/api/products';
        const params = new URLSearchParams();
        
        if (category) params.append('category', category);
        if (search) params.append('search', search);
        
        if (params.toString()) endpoint += `?${params.toString()}`;

        const data = await apiCall(endpoint);
        state.products = data.products || [];
        renderProducts();
    } catch (error) {
        console.error('Failed to load products:', error);
    }
}

function renderProducts() {
    const container = document.getElementById('productsGrid');
    if (!container) return;

    if (state.products.length === 0) {
        container.innerHTML = '<div class="empty-cart"><p>No products found</p></div>';
        return;
    }

    container.innerHTML = state.products.map(product => `
        <div class="product-card" data-product-id="${product.id}">
            <div class="product-image">${getProductIcon(product.category)}</div>
            <div class="product-info">
                <div class="product-name">${escapeHtml(product.name)}</div>
                <div class="product-price">₹${product.price.toFixed(2)}</div>
                <div class="product-rating">
                    <span class="rating-badge">
                        ★ ${product.rating || 4.0}
                    </span>
                    <span class="text-gray">(${Math.floor(Math.random() * 1000)} reviews)</span>
                </div>
                <div class="product-stock">
                    ${product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                </div>
                <button 
                    class="add-to-cart-btn" 
                    onclick="addToCart(${product.id})"
                    ${product.stock === 0 || !state.token ? 'disabled' : ''}
                >
                    ${!state.token ? 'Login to Buy' : product.stock === 0 ? 'Out of Stock' : 'Add to Cart'}
                </button>
            </div>
        </div>
    `).join('');
}

// Cart
async function loadCart() {
    if (!state.token) return;

    try {
        const data = await apiCall('/api/cart');
        state.cart = data.items || [];
        updateCartUI();
    } catch (error) {
        console.error('Failed to load cart:', error);
    }
}

async function addToCart(productId) {
    if (!state.token) {
        showAlert('Please login to add items to cart', 'error');
        openModal('loginModal');
        return;
    }

    try {
        await apiCall('/api/cart/add', {
            method: 'POST',
            body: JSON.stringify({
                product_id: productId,
                quantity: 1
            })
        });

        await loadCart();
        showAlert('Added to cart!', 'success');
    } catch (error) {
        console.error('Failed to add to cart:', error);
    }
}

async function updateCartQuantity(itemId, quantity) {
    try {
        if (quantity === 0) {
            await removeFromCart(itemId);
            return;
        }

        await apiCall(`/api/cart/update/${itemId}`, {
            method: 'PUT',
            body: JSON.stringify({ quantity })
        });

        await loadCart();
    } catch (error) {
        console.error('Failed to update cart:', error);
    }
}

async function removeFromCart(itemId) {
    try {
        await apiCall(`/api/cart/remove/${itemId}`, {
            method: 'DELETE'
        });

        await loadCart();
        showAlert('Item removed from cart', 'success');
    } catch (error) {
        console.error('Failed to remove from cart:', error);
    }
}

function updateCartUI() {
    const cartCount = document.getElementById('cartCount');
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');

    if (cartCount) {
        const totalItems = state.cart.reduce((sum, item) => sum + item.quantity, 0);
        cartCount.textContent = totalItems;
        cartCount.style.display = totalItems > 0 ? 'flex' : 'none';
    }

    if (cartItems) {
        if (state.cart.length === 0) {
            cartItems.innerHTML = '<div class="empty-cart"><p>Your cart is empty</p></div>';
            if (cartTotal) cartTotal.style.display = 'none';
        } else {
            cartItems.innerHTML = state.cart.map(item => `
                <div class="cart-item">
                    <div class="cart-item-image">${getProductIcon(item.product.category)}</div>
                    <div class="cart-item-details">
                        <div class="cart-item-name">${escapeHtml(item.product.name)}</div>
                        <div class="cart-item-price">₹${item.product.price.toFixed(2)}</div>
                        <div class="cart-item-actions">
                            <button class="quantity-btn" onclick="updateCartQuantity(${item.id}, ${item.quantity - 1})">−</button>
                            <span class="quantity-display">${item.quantity}</span>
                            <button class="quantity-btn" onclick="updateCartQuantity(${item.id}, ${item.quantity + 1})">+</button>
                            <button class="remove-btn" onclick="removeFromCart(${item.id})">🗑️</button>
                        </div>
                    </div>
                </div>
            `).join('');

            if (cartTotal) {
                const total = state.cart.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
                cartTotal.innerHTML = `
                    <div class="cart-total">
                        <span>Total:</span>
                        <span>₹${total.toFixed(2)}</span>
                    </div>
                    <button class="btn-primary" onclick="checkout()">Proceed to Checkout</button>
                `;
                cartTotal.style.display = 'block';
            }
        }
    }
}

async function checkout() {
    if (state.cart.length === 0) {
        showAlert('Your cart is empty', 'error');
        return;
    }

    try {
        const data = await apiCall('/api/orders/checkout', {
            method: 'POST',
            body: JSON.stringify({
                shipping_address: 'Default Address',
                payment_method: 'COD'
            })
        });

        showAlert('Order placed successfully!', 'success');
        await loadCart();
        closeModal('cartModal');
    } catch (error) {
        console.error('Checkout failed:', error);
    }
}

// Search
function handleSearch() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput?.value.trim();
    
    if (query) {
        loadProducts(null, query);
    } else {
        loadProducts();
    }
}

// Category Filter
function filterByCategory(category) {
    loadProducts(category);
}

// UI Helpers
function updateUI() {
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const profileBtn = document.getElementById('profileBtn');
    const cartBtn = document.getElementById('cartBtn');

    if (state.token && state.user) {
        loginBtn?.classList.add('d-none');
        signupBtn?.classList.add('d-none');
        logoutBtn?.classList.remove('d-none');
        profileBtn?.classList.remove('d-none');
        cartBtn?.classList.remove('d-none');
    } else {
        loginBtn?.classList.remove('d-none');
        signupBtn?.classList.remove('d-none');
        logoutBtn?.classList.add('d-none');
        profileBtn?.classList.add('d-none');
        cartBtn?.classList.add('d-none');
    }
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Load profile data if opening profile modal
        if (modalId === 'profileModal' && state.user) {
            loadProfileData();
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

function showAlert(message, type = 'success') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} active`;
    alert.textContent = message;
    alert.style.position = 'fixed';
    alert.style.top = '80px';
    alert.style.right = '20px';
    alert.style.zIndex = '3000';
    alert.style.minWidth = '300px';
    alert.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';

    document.body.appendChild(alert);

    setTimeout(() => {
        alert.remove();
    }, 3000);
}

function loadProfileData() {
    if (!state.user) return;

    document.getElementById('profileName').textContent = state.user.full_name || 'N/A';
    document.getElementById('profileEmail').textContent = state.user.email || 'N/A';
    document.getElementById('profilePhone').textContent = state.user.phone || 'N/A';
    document.getElementById('profileUsername').textContent = state.user.username || 'N/A';

    // Load orders
    loadOrders();
}

async function loadOrders() {
    try {
        const data = await apiCall('/api/orders');
        const ordersContainer = document.getElementById('ordersList');
        
        if (!ordersContainer) return;

        if (!data.orders || data.orders.length === 0) {
            ordersContainer.innerHTML = '<div class="empty-cart"><p>No orders yet</p></div>';
            return;
        }

        ordersContainer.innerHTML = data.orders.map(order => `
            <div class="order-card">
                <div class="order-header">
                    <div>
                        <div class="order-id">Order #${order.id}</div>
                        <div class="text-gray" style="font-size: 12px;">
                            ${new Date(order.created_at).toLocaleDateString()}
                        </div>
                    </div>
                    <span class="order-status status-${order.status.toLowerCase()}">
                        ${order.status}
                    </span>
                </div>
                <div class="order-items">
                    ${order.items.map(item => `
                        <div class="order-item">
                            <span>${escapeHtml(item.product.name)} × ${item.quantity}</span>
                            <span>₹${(item.price * item.quantity).toFixed(2)}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="order-total">
                    <span>Total</span>
                    <span>₹${order.total_amount.toFixed(2)}</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load orders:', error);
    }
}

// Utility Functions
function getProductIcon(category) {
    const icons = {
        'Electronics': '📱',
        'Fashion': '👕',
        'Home': '🏠',
        'Books': '📚',
        'Sports': '⚽',
        'Beauty': '💄',
        'Toys': '🧸',
        'Food': '🍕'
    };
    return icons[category] || '📦';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add CSS class helper
const style = document.createElement('style');
style.textContent = '.d-none { display: none !important; }';
document.head.appendChild(style);
