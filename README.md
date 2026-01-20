# Flipkart Monolith E-commerce Application

A production-ready, smaller version of a Flipkart-like e-commerce platform built with a modular monolithic architecture using Flask, PostgreSQL, Redis, and Docker.

## 🚀 Features

- **User Management**: Registration, authentication with JWT, profile management, and address management
- **Product Catalog**: Browse products with filtering, search, pagination, and sorting
- **Category Management**: Hierarchical product categories
- **Shopping Cart**: Add, update, and remove items from cart
- **Order Management**: Place orders, view order history, track orders, cancel orders
- **Product Reviews**: Users can rate and review products
- **Admin Panel**: Manage products, categories, and orders (admin-only endpoints)
- **Performance**: 
  - Redis caching for improved response times
  - Rate limiting to prevent abuse
  - Connection pooling for database optimization
  - Optimized to handle 500-600 concurrent users
- **Monitoring**: Prometheus metrics endpoint for monitoring
- **Security**: JWT authentication, password hashing, CORS, rate limiting

## 🏗️ Architecture

### Modular Monolithic Design

```
monolith-app/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── models.py             # Database models (SQLAlchemy)
├── auth.py               # Authentication utilities
├── routes/               # API routes (modular)
│   ├── user_routes.py    # User & auth endpoints
│   ├── product_routes.py # Product & category endpoints
│   ├── cart_routes.py    # Shopping cart endpoints
│   └── order_routes.py   # Order management endpoints
├── init_db.py            # Database initialization script
├── requirements.txt      # Python dependencies
├── Dockerfile            # Multi-stage Docker build
├── docker-compose.yml    # Docker services orchestration
├── nginx.conf            # Nginx reverse proxy config
└── deploy.sh             # Deployment automation script
```

### Technology Stack

- **Backend**: Flask 3.0, Python 3.11
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Web Server**: Gunicorn with Gevent workers
- **Reverse Proxy**: Nginx
- **Authentication**: JWT (Flask-JWT-Extended)
- **Monitoring**: Prometheus metrics
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- Git

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
cd monolith-app
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration (optional for local dev)
# For production, set strong SECRET_KEY and JWT_SECRET_KEY
```

### 3. Build and Start

```bash
# Make deploy script executable
chmod +x deploy.sh

# Build Docker images
./deploy.sh build

# Start all services
./deploy.sh start

# Initialize database with sample data
./deploy.sh init
```

### 4. Access the Application

- **API Base URL**: http://localhost:5000
- **Via Nginx**: http://localhost:80
- **Health Check**: http://localhost:5000/health
- **Metrics**: http://localhost:5000/metrics

## 📖 API Documentation

### Authentication Endpoints

#### Register User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "9876543210"
}
```

#### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Refresh Token
```bash
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

### Product Endpoints

#### Get All Products
```bash
GET /api/products?page=1&per_page=20&category_id=1&search=phone&min_price=1000&max_price=50000&sort_by=price&sort_order=asc
```

#### Get Product Details
```bash
GET /api/products/{product_id}
```

#### Create Product (Admin Only)
```bash
POST /api/products
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Product Name",
  "description": "Product description",
  "price": 9999,
  "discount_percentage": 10,
  "category_id": 1,
  "brand": "Brand Name",
  "stock_quantity": 100,
  "sku": "PROD123",
  "image_url": "https://example.com/image.jpg"
}
```

### Cart Endpoints

#### Get Cart
```bash
GET /api/cart
Authorization: Bearer <access_token>
```

#### Add to Cart
```bash
POST /api/cart/add
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}
```

#### Update Cart Item
```bash
PUT /api/cart/update/{item_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "quantity": 3
}
```

#### Remove from Cart
```bash
DELETE /api/cart/remove/{item_id}
Authorization: Bearer <access_token>
```

### Order Endpoints

#### Create Order
```bash
POST /api/orders
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "address_id": 1,
  "payment_method": "COD"
}
```

#### Get User Orders
```bash
GET /api/orders?page=1&per_page=10
Authorization: Bearer <access_token>
```

#### Get Order Details
```bash
GET /api/orders/{order_id}
Authorization: Bearer <access_token>
```

#### Cancel Order
```bash
POST /api/orders/{order_id}/cancel
Authorization: Bearer <access_token>
```

### Category Endpoints

#### Get All Categories
```bash
GET /api/categories
```

#### Create Category (Admin Only)
```bash
POST /api/categories
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Category Name",
  "description": "Category description",
  "parent_id": null
}
```

### User Endpoints

#### Get Profile
```bash
GET /api/users/profile
Authorization: Bearer <access_token>
```

#### Update Profile
```bash
PUT /api/users/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "9876543210"
}
```

#### Get Addresses
```bash
GET /api/users/addresses
Authorization: Bearer <access_token>
```

#### Add Address
```bash
POST /api/users/addresses
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "address_type": "home",
  "street": "123 Main Street",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400001",
  "country": "India",
  "is_default": true
}
```

## 🧪 Sample Credentials

After running `./deploy.sh init`, use these credentials:

**Admin User:**
- Email: `admin@flipkart.com`
- Password: `admin123`

**Regular User 1:**
- Email: `john@example.com`
- Password: `password123`

**Regular User 2:**
- Email: `jane@example.com`
- Password: `password123`

## 🛠️ Management Commands

```bash
# View logs
./deploy.sh logs

# Restart services
./deploy.sh restart

# Stop services
./deploy.sh stop

# Clean up (removes all containers and volumes)
./deploy.sh clean
```

## 📊 Performance & Scalability

### Optimizations for 500-600 Concurrent Users

1. **Database Connection Pooling**
   - Pool size: 20 connections
   - Max overflow: 40 connections
   - Pool timeout: 30 seconds

2. **Gunicorn Configuration**
   - 4 Gevent workers
   - 1000 worker connections per worker
   - Total capacity: 4000 concurrent connections

3. **Redis Caching**
   - API response caching
   - Session management
   - Rate limiting storage

4. **Nginx Load Balancing**
   - Reverse proxy for SSL termination
   - Request buffering
   - Static file serving (if needed)

5. **Rate Limiting**
   - 200 requests per day per IP
   - 50 requests per hour per IP
   - 10 requests per second with burst of 20

### Load Testing

To test the application under load, use tools like Apache Bench or Locust:

```bash
# Install Apache Bench
# macOS: brew install httpd
# Ubuntu: apt-get install apache2-utils

# Simple load test (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost/health
```

## 🔒 Security Features

- **Password Hashing**: Werkzeug password hashing
- **JWT Authentication**: Secure token-based auth
- **CORS Protection**: Configurable origins
- **Rate Limiting**: Prevent API abuse
- **SQL Injection Protection**: SQLAlchemy ORM
- **Non-root Docker Container**: Enhanced container security
- **Environment Variables**: Sensitive data protection

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps db

# View database logs
docker-compose logs db

# Recreate database
docker-compose down -v
docker-compose up -d
./deploy.sh init
```

### Application Not Starting

```bash
# Check application logs
docker-compose logs app

# Rebuild without cache
docker-compose build --no-cache app
docker-compose up -d
```

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill the process or change port in docker-compose.yml
```

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:5000/health
```

### Prometheus Metrics
```bash
curl http://localhost:5000/metrics
```

## 🔄 Database Migrations

For production, use Alembic for database migrations:

```bash
# Generate migration
docker-compose exec app flask db migrate -m "Description"

# Apply migration
docker-compose exec app flask db upgrade
```

## 📦 Production Deployment

### Environment Variables for Production

Update `.env` file with production values:

```env
FLASK_ENV=production
SECRET_KEY=<generate-strong-random-key>
JWT_SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/0
CORS_ORIGINS=https://yourdomain.com
```

### SSL/TLS Configuration

Update `nginx.conf` to include SSL certificates:

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... rest of configuration
}
```

## 🧰 Tech Stack Details

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | Flask 3.0 | Lightweight and flexible |
| Database | PostgreSQL 15 | Reliable RDBMS |
| Cache | Redis 7 | In-memory data store |
| WSGI Server | Gunicorn | Production-grade WSGI |
| Worker Type | Gevent | Async worker for concurrency |
| Reverse Proxy | Nginx | Load balancing, SSL |
| ORM | SQLAlchemy | Database abstraction |
| Auth | JWT | Stateless authentication |
| Monitoring | Prometheus | Metrics collection |

## 📝 License

This is a sample application for demonstration purposes.

## 🤝 Contributing

This is a demonstration project. Feel free to fork and modify as needed.

## 📞 Support

For issues or questions, check the logs:
```bash
./deploy.sh logs
```

---

**Built with ❤️ for production-ready e-commerce solutions**
