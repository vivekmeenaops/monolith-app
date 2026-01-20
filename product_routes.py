"""Product and category routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, func
from models import db, Product, Category, Review
from auth import admin_required, get_current_user

product_bp = Blueprint('products', __name__, url_prefix='/api/products')
category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')


# Category Routes
@category_bp.route('/', methods=['GET'])
def get_categories():
    """Get all categories."""
    categories = Category.query.filter_by(is_active=True).all()
    return jsonify([cat.to_dict() for cat in categories]), 200


@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get category by ID."""
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    return jsonify(category.to_dict()), 200


@category_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required()
def create_category():
    """Create new category (admin only)."""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Category name is required'}), 400
    
    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Category already exists'}), 409
    
    category = Category(
        name=data['name'],
        description=data.get('description'),
        parent_id=data.get('parent_id')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'message': 'Category created successfully',
        'category': category.to_dict()
    }), 201


# Product Routes
@product_bp.route('/', methods=['GET'])
def get_products():
    """Get all products with filtering and pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Build query
    query = Product.query.filter_by(is_active=True)
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            or_(
                Product.name.ilike(search_pattern),
                Product.description.ilike(search_pattern),
                Product.brand.ilike(search_pattern)
            )
        )
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Apply sorting
    sort_column = getattr(Product, sort_by, Product.created_at)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'products': [product.to_dict() for product in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID."""
    product = Product.query.get(product_id)
    
    if not product or not product.is_active:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify(product.to_dict()), 200


@product_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required()
def create_product():
    """Create new product (admin only)."""
    data = request.get_json()
    
    required_fields = ['name', 'price', 'category_id', 'sku']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    if Product.query.filter_by(sku=data['sku']).first():
        return jsonify({'error': 'SKU already exists'}), 409
    
    product = Product(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        discount_percentage=data.get('discount_percentage', 0),
        category_id=data['category_id'],
        brand=data.get('brand'),
        stock_quantity=data.get('stock_quantity', 0),
        sku=data['sku'],
        image_url=data.get('image_url')
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'message': 'Product created successfully',
        'product': product.to_dict()
    }), 201


@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_product(product_id):
    """Update product (admin only)."""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    updatable_fields = ['name', 'description', 'price', 'discount_percentage', 
                       'category_id', 'brand', 'stock_quantity', 'image_url', 'is_active']
    
    for field in updatable_fields:
        if field in data:
            setattr(product, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Product updated successfully',
        'product': product.to_dict()
    }), 200


@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_product(product_id):
    """Delete product (admin only) - soft delete."""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    product.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Product deleted successfully'}), 200


# Review Routes
@product_bp.route('/<int:product_id>/reviews', methods=['GET'])
def get_product_reviews(product_id):
    """Get reviews for a product."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    pagination = Review.query.filter_by(product_id=product_id)\
        .order_by(Review.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'reviews': [review.to_dict() for review in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@product_bp.route('/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def add_review(product_id):
    """Add a review for a product."""
    user = get_current_user()
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.get_json()
    
    if not data.get('rating') or not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Check if user already reviewed this product
    existing_review = Review.query.filter_by(user_id=user.id, product_id=product_id).first()
    if existing_review:
        return jsonify({'error': 'You have already reviewed this product'}), 409
    
    review = Review(
        user_id=user.id,
        product_id=product_id,
        rating=data['rating'],
        title=data.get('title'),
        comment=data.get('comment')
    )
    
    db.session.add(review)
    
    # Update product rating
    avg_rating = db.session.query(func.avg(Review.rating)).filter_by(product_id=product_id).scalar()
    review_count = Review.query.filter_by(product_id=product_id).count() + 1
    
    product.rating = avg_rating
    product.review_count = review_count
    
    db.session.commit()
    
    return jsonify({
        'message': 'Review added successfully',
        'review': review.to_dict()
    }), 201
