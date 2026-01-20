"""Order management routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import secrets
from models import db, Order, OrderItem, CartItem, Product, Address
from auth import get_current_user, admin_required

order_bp = Blueprint('orders', __name__, url_prefix='/api/orders')


def generate_order_number():
    """Generate unique order number."""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    random_suffix = secrets.token_hex(4).upper()
    return f'ORD-{timestamp}-{random_suffix}'


@order_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    """Create order from cart."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Get cart items
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Validate stock availability
    for item in cart_items:
        if item.product.stock_quantity < item.quantity:
            return jsonify({
                'error': f'Insufficient stock for {item.product.name}'
            }), 400
    
    # Get shipping address
    address_id = data.get('address_id')
    if address_id:
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        if not address:
            return jsonify({'error': 'Invalid address'}), 400
        shipping_address = f"{address.street}, {address.city}, {address.state} - {address.pincode}, {address.country}"
    else:
        return jsonify({'error': 'Shipping address is required'}), 400
    
    # Calculate total
    total_amount = sum(item.product.final_price * item.quantity for item in cart_items)
    
    # Create order
    order = Order(
        order_number=generate_order_number(),
        user_id=user_id,
        total_amount=total_amount,
        shipping_address=shipping_address,
        payment_method=data.get('payment_method', 'COD'),
        status='pending',
        payment_status='pending'
    )
    
    db.session.add(order)
    db.session.flush()  # Get order ID
    
    # Create order items and update stock
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.final_price
        )
        db.session.add(order_item)
        
        # Update stock
        cart_item.product.stock_quantity -= cart_item.quantity
    
    # Clear cart
    CartItem.query.filter_by(user_id=user_id).delete()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Order created successfully',
        'order': order.to_dict()
    }), 201


@order_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """Get user's orders."""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Order.query.filter_by(user_id=user_id)\
        .order_by(Order.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'orders': [order.to_dict() for order in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@order_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get order details."""
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify(order.to_dict()), 200


@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """Cancel order."""
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if order.status not in ['pending', 'confirmed']:
        return jsonify({'error': 'Order cannot be cancelled'}), 400
    
    # Restore stock
    for item in order.items:
        item.product.stock_quantity += item.quantity
    
    order.status = 'cancelled'
    db.session.commit()
    
    return jsonify({
        'message': 'Order cancelled successfully',
        'order': order.to_dict()
    }), 200


@order_bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
@admin_required()
def update_order_status(order_id):
    """Update order status (admin only)."""
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    
    if 'status' in data:
        valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
        if data['status'] not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        order.status = data['status']
    
    if 'payment_status' in data:
        valid_payment_statuses = ['pending', 'completed', 'failed', 'refunded']
        if data['payment_status'] not in valid_payment_statuses:
            return jsonify({'error': 'Invalid payment status'}), 400
        order.payment_status = data['payment_status']
    
    if 'tracking_number' in data:
        order.tracking_number = data['tracking_number']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Order updated successfully',
        'order': order.to_dict()
    }), 200


@order_bp.route('/all', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_orders():
    """Get all orders (admin only)."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = Order.query
    
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Order.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'orders': [order.to_dict() for order in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200
