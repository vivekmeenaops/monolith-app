"""Shopping cart routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, CartItem, Product
from auth import get_current_user

cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')


@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    """Get user's cart."""
    user_id = get_jwt_identity()
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    total = sum(item.product.final_price * item.quantity for item in cart_items if item.product)
    
    return jsonify({
        'items': [item.to_dict() for item in cart_items],
        'total': float(total),
        'item_count': len(cart_items)
    }), 200


@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add item to cart."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('product_id'):
        return jsonify({'error': 'product_id is required'}), 400
    
    product = Product.query.get(data['product_id'])
    if not product or not product.is_active:
        return jsonify({'error': 'Product not found'}), 404
    
    quantity = data.get('quantity', 1)
    if quantity < 1:
        return jsonify({'error': 'Quantity must be at least 1'}), 400
    
    if product.stock_quantity < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    # Check if item already in cart
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product.id).first()
    
    if cart_item:
        # Update quantity
        new_quantity = cart_item.quantity + quantity
        if product.stock_quantity < new_quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        cart_item.quantity = new_quantity
    else:
        # Add new item
        cart_item = CartItem(
            user_id=user_id,
            product_id=product.id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Item added to cart',
        'item': cart_item.to_dict()
    }), 201


@cart_bp.route('/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    """Update cart item quantity."""
    user_id = get_jwt_identity()
    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404
    
    data = request.get_json()
    quantity = data.get('quantity')
    
    if quantity is None or quantity < 1:
        return jsonify({'error': 'Valid quantity is required'}), 400
    
    if cart_item.product.stock_quantity < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    cart_item.quantity = quantity
    db.session.commit()
    
    return jsonify({
        'message': 'Cart item updated',
        'item': cart_item.to_dict()
    }), 200


@cart_bp.route('/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """Remove item from cart."""
    user_id = get_jwt_identity()
    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed from cart'}), 200


@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """Clear all items from cart."""
    user_id = get_jwt_identity()
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return jsonify({'message': 'Cart cleared'}), 200
