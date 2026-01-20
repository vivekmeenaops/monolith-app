"""Initialize database with sample data."""
import sys
from app import create_app
from models import db, User, Category, Product, Address


def init_db():
    """Initialize database with sample data."""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Check if data already exists
        if User.query.first():
            print("Database already initialized!")
            return
        
        print("Creating sample data...")
        
        # Create admin user
        admin = User(
            email='admin@flipkart.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            phone='9999999999',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create regular users
        user1 = User(
            email='john@example.com',
            username='john_doe',
            first_name='John',
            last_name='Doe',
            phone='9876543210'
        )
        user1.set_password('password123')
        db.session.add(user1)
        
        user2 = User(
            email='jane@example.com',
            username='jane_smith',
            first_name='Jane',
            last_name='Smith',
            phone='9876543211'
        )
        user2.set_password('password123')
        db.session.add(user2)
        
        db.session.commit()
        print(f"Created {User.query.count()} users")
        
        # Create categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic items and gadgets'},
            {'name': 'Fashion', 'description': 'Clothing and accessories'},
            {'name': 'Home & Kitchen', 'description': 'Home and kitchen appliances'},
            {'name': 'Books', 'description': 'Books and magazines'},
            {'name': 'Sports', 'description': 'Sports and fitness equipment'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.session.add(category)
            categories.append(category)
        
        db.session.commit()
        print(f"Created {Category.query.count()} categories")
        
        # Create products
        products_data = [
            {
                'name': 'iPhone 15 Pro',
                'description': 'Latest Apple iPhone with advanced camera system',
                'price': 129900,
                'discount_percentage': 10,
                'category_id': categories[0].id,
                'brand': 'Apple',
                'stock_quantity': 50,
                'sku': 'IPHONE15PRO',
                'image_url': 'https://via.placeholder.com/300x300?text=iPhone+15+Pro',
                'rating': 4.5
            },
            {
                'name': 'Samsung Galaxy S24',
                'description': 'Premium Android smartphone with AI features',
                'price': 99900,
                'discount_percentage': 15,
                'category_id': categories[0].id,
                'brand': 'Samsung',
                'stock_quantity': 75,
                'sku': 'GALAXYS24',
                'image_url': 'https://via.placeholder.com/300x300?text=Galaxy+S24',
                'rating': 4.3
            },
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Premium noise cancelling headphones',
                'price': 29990,
                'discount_percentage': 20,
                'category_id': categories[0].id,
                'brand': 'Sony',
                'stock_quantity': 100,
                'sku': 'SONYWH1000XM5',
                'image_url': 'https://via.placeholder.com/300x300?text=Sony+Headphones',
                'rating': 4.7
            },
            {
                'name': 'Levi\'s Men\'s Jeans',
                'description': 'Classic fit denim jeans',
                'price': 2999,
                'discount_percentage': 30,
                'category_id': categories[1].id,
                'brand': 'Levi\'s',
                'stock_quantity': 200,
                'sku': 'LEVIS501',
                'image_url': 'https://via.placeholder.com/300x300?text=Levis+Jeans',
                'rating': 4.2
            },
            {
                'name': 'Nike Air Max Shoes',
                'description': 'Comfortable running shoes with air cushioning',
                'price': 8999,
                'discount_percentage': 25,
                'category_id': categories[1].id,
                'brand': 'Nike',
                'stock_quantity': 150,
                'sku': 'NIKEAIRMAX',
                'image_url': 'https://via.placeholder.com/300x300?text=Nike+Air+Max',
                'rating': 4.6
            },
            {
                'name': 'Instant Pot Duo',
                'description': '7-in-1 electric pressure cooker',
                'price': 6999,
                'discount_percentage': 15,
                'category_id': categories[2].id,
                'brand': 'Instant Pot',
                'stock_quantity': 80,
                'sku': 'INSTANTPOT7IN1',
                'image_url': 'https://via.placeholder.com/300x300?text=Instant+Pot',
                'rating': 4.5
            },
            {
                'name': 'Philips Air Fryer',
                'description': 'Healthier cooking with rapid air technology',
                'price': 9999,
                'discount_percentage': 20,
                'category_id': categories[2].id,
                'brand': 'Philips',
                'stock_quantity': 60,
                'sku': 'PHILIPSAIRFRYER',
                'image_url': 'https://via.placeholder.com/300x300?text=Air+Fryer',
                'rating': 4.4
            },
            {
                'name': 'Atomic Habits by James Clear',
                'description': 'Bestselling book on building good habits',
                'price': 399,
                'discount_percentage': 10,
                'category_id': categories[3].id,
                'brand': 'Penguin Random House',
                'stock_quantity': 500,
                'sku': 'ATOMICHABITS',
                'image_url': 'https://via.placeholder.com/300x300?text=Atomic+Habits',
                'rating': 4.8
            },
            {
                'name': 'Yoga Mat Premium',
                'description': 'Non-slip exercise mat for yoga and fitness',
                'price': 1299,
                'discount_percentage': 15,
                'category_id': categories[4].id,
                'brand': 'FitGear',
                'stock_quantity': 300,
                'sku': 'YOGAMATPREM',
                'image_url': 'https://via.placeholder.com/300x300?text=Yoga+Mat',
                'rating': 4.1
            },
            {
                'name': 'Dumbbells Set 10kg',
                'description': 'Adjustable dumbbells for home workout',
                'price': 2499,
                'discount_percentage': 20,
                'category_id': categories[4].id,
                'brand': 'PowerFit',
                'stock_quantity': 120,
                'sku': 'DUMBBELL10KG',
                'image_url': 'https://via.placeholder.com/300x300?text=Dumbbells',
                'rating': 4.3
            },
        ]
        
        for prod_data in products_data:
            product = Product(**prod_data)
            db.session.add(product)
        
        db.session.commit()
        print(f"Created {Product.query.count()} products")
        
        # Create sample addresses
        address1 = Address(
            user_id=user1.id,
            address_type='home',
            street='123 Main Street, Apt 4B',
            city='Mumbai',
            state='Maharashtra',
            pincode='400001',
            country='India',
            is_default=True
        )
        db.session.add(address1)
        
        address2 = Address(
            user_id=user1.id,
            address_type='work',
            street='456 Business Park',
            city='Mumbai',
            state='Maharashtra',
            pincode='400002',
            country='India',
            is_default=False
        )
        db.session.add(address2)
        
        db.session.commit()
        print(f"Created {Address.query.count()} addresses")
        
        print("\n✅ Database initialized successfully!")
        print("\nSample Credentials:")
        print("Admin - Email: admin@flipkart.com, Password: admin123")
        print("User 1 - Email: john@example.com, Password: password123")
        print("User 2 - Email: jane@example.com, Password: password123")


if __name__ == '__main__':
    init_db()
