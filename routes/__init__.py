"""Routes package initialization."""
from .user_routes import auth_bp, user_bp
from .product_routes import product_bp, category_bp
from .cart_routes import cart_bp
from .order_routes import order_bp

__all__ = ['auth_bp', 'user_bp', 'product_bp', 'category_bp', 'cart_bp', 'order_bp']
