"""User authentication and management routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import db, User, Address
from email_validator import validate_email, EmailNotValidError

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
user_bp = Blueprint('users', __name__, url_prefix='/api/users')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'username', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate email
    try:
        validate_email(data['email'])
    except EmailNotValidError:
        return jsonify({'error': 'Invalid email address'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 409
    
    # Create new user
    user = User(
        email=data['email'],
        username=data['username'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone=data.get('phone')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user."""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    
    return jsonify({'access_token': access_token}), 200


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'phone' in data:
        user.phone = data['phone']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200


@user_bp.route('/addresses', methods=['GET'])
@jwt_required()
def get_addresses():
    """Get user addresses."""
    user_id = get_jwt_identity()
    addresses = Address.query.filter_by(user_id=user_id).all()
    
    return jsonify([addr.to_dict() for addr in addresses]), 200


@user_bp.route('/addresses', methods=['POST'])
@jwt_required()
def add_address():
    """Add new address."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['street', 'city', 'state', 'pincode']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # If this is the first address or marked as default, make it default
    if data.get('is_default') or Address.query.filter_by(user_id=user_id).count() == 0:
        # Remove default from other addresses
        Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
        data['is_default'] = True
    
    address = Address(
        user_id=user_id,
        address_type=data.get('address_type', 'home'),
        street=data['street'],
        city=data['city'],
        state=data['state'],
        pincode=data['pincode'],
        country=data.get('country', 'India'),
        is_default=data.get('is_default', False)
    )
    
    db.session.add(address)
    db.session.commit()
    
    return jsonify({
        'message': 'Address added successfully',
        'address': address.to_dict()
    }), 201


@user_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    """Update address."""
    user_id = get_jwt_identity()
    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    
    if not address:
        return jsonify({'error': 'Address not found'}), 404
    
    data = request.get_json()
    
    # If setting as default, remove default from others
    if data.get('is_default'):
        Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
    
    # Update fields
    for field in ['address_type', 'street', 'city', 'state', 'pincode', 'country', 'is_default']:
        if field in data:
            setattr(address, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Address updated successfully',
        'address': address.to_dict()
    }), 200


@user_bp.route('/addresses/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    """Delete address."""
    user_id = get_jwt_identity()
    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    
    if not address:
        return jsonify({'error': 'Address not found'}), 404
    
    db.session.delete(address)
    db.session.commit()
    
    return jsonify({'message': 'Address deleted successfully'}), 200
