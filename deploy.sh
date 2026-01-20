#!/bin/bash

# Flipkart Monolith - Build and Deployment Script

set -e

echo "🚀 Flipkart Monolith - Build and Deployment Script"
echo "=================================================="

# Function to display usage
usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       - Build Docker images"
    echo "  start       - Start all services"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  logs        - View application logs"
    echo "  init        - Initialize database with sample data"
    echo "  clean       - Remove all containers and volumes"
    echo "  test        - Run tests"
    echo ""
    exit 1
}

# Build Docker images
build() {
    echo "📦 Building Docker images..."
    docker-compose build --no-cache
    echo "✅ Build completed!"
}

# Start services
start() {
    echo "🚀 Starting services..."
    docker-compose up -d
    echo "⏳ Waiting for services to be healthy..."
    sleep 10
    docker-compose ps
    echo ""
    echo "✅ Services started!"
    echo "📍 Application URL: http://localhost:5000"
    echo "📍 Nginx URL: http://localhost:80"
    echo "📍 Health Check: http://localhost:5000/health"
    echo "📍 Metrics: http://localhost:5000/metrics"
}

# Stop services
stop() {
    echo "🛑 Stopping services..."
    docker-compose down
    echo "✅ Services stopped!"
}

# Restart services
restart() {
    echo "🔄 Restarting services..."
    stop
    start
}

# View logs
logs() {
    echo "📋 Viewing logs (Ctrl+C to exit)..."
    docker-compose logs -f app
}

# Initialize database
init_db() {
    echo "🗄️  Initializing database..."
    docker-compose exec app python init_db.py
    echo "✅ Database initialized!"
}

# Clean up
clean() {
    echo "🧹 Cleaning up..."
    docker-compose down -v
    docker system prune -f
    echo "✅ Cleanup completed!"
}

# Run tests
test() {
    echo "🧪 Running tests..."
    docker-compose exec app python -m pytest tests/ -v
    echo "✅ Tests completed!"
}

# Main script
case "${1:-}" in
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    init)
        init_db
        ;;
    clean)
        clean
        ;;
    test)
        test
        ;;
    *)
        usage
        ;;
esac
