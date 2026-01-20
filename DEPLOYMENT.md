# Flipkart Monolith - Complete Deployment Guide

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Performance Tuning](#performance-tuning)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 20 GB
- **OS**: Linux (Ubuntu 20.04+), macOS, Windows with WSL2

### Recommended for 500-600 Users
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **OS**: Linux (Ubuntu 22.04 LTS)

### Software Requirements
- Docker: 20.10+
- Docker Compose: 2.0+
- Python: 3.11+ (for local dev)
- PostgreSQL: 15+ (if not using Docker)
- Redis: 7+ (if not using Docker)

## Local Development Setup

### Option 1: Using Docker (Recommended)

```bash
# 1. Navigate to project directory
cd monolith-app

# 2. Copy environment file
cp .env.example .env

# 3. Build and start services
chmod +x deploy.sh
./deploy.sh build
./deploy.sh start

# 4. Initialize database
./deploy.sh init

# 5. Test the application
python3 test_api.py
```

### Option 2: Local Python Environment

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up PostgreSQL and Redis
# Install PostgreSQL and create database
createdb flipkart_db

# Update .env file with local database URL
DATABASE_URL=postgresql://localhost/flipkart_db
REDIS_URL=redis://localhost:6379/0

# 4. Initialize database
python init_db.py

# 5. Run application
python app.py
```

## Docker Deployment

### Single Server Deployment

#### Step 1: Prepare Server

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### Step 2: Deploy Application

```bash
# Clone/Copy application to server
git clone <your-repo> /opt/flipkart-app
cd /opt/flipkart-app/monolith-app

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Generate secure keys
python3 -c "import secrets; print(secrets.token_hex(32))"  # For SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"  # For JWT_SECRET_KEY

# Build and start
./deploy.sh build
./deploy.sh start
./deploy.sh init
```

#### Step 3: Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### SSL/TLS Configuration

#### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Update nginx.conf
# Add SSL configuration:
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # ... rest of configuration
}

# Mount certificates in docker-compose.yml
volumes:
  - /etc/letsencrypt:/etc/letsencrypt:ro
```

## Production Deployment

### Environment Configuration

```env
# Production .env
FLASK_ENV=production
SECRET_KEY=<64-char-random-string>
JWT_SECRET_KEY=<64-char-random-string>

# Database (use managed service recommended)
DATABASE_URL=postgresql://user:pass@db-host:5432/dbname

# Redis (use managed service recommended)
REDIS_URL=redis://redis-host:6379/0

# CORS - your domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate limiting
RATELIMIT_STORAGE_URL=redis://redis-host:6379/1
```

### Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_cart_user ON cart_items(user_id);

-- Analyze tables
ANALYZE products;
ANALYZE orders;
ANALYZE users;
```

### Scaling Configuration

#### Horizontal Scaling (Multiple App Instances)

Update `docker-compose.yml`:

```yaml
services:
  app:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

#### Nginx Load Balancing

```nginx
upstream app_backend {
    least_conn;
    server app1:5000 max_fails=3 fail_timeout=30s;
    server app2:5000 max_fails=3 fail_timeout=30s;
    server app3:5000 max_fails=3 fail_timeout=30s;
}
```

## Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### Deployment Files

#### 1. ConfigMap for Environment

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: flipkart-config
data:
  FLASK_ENV: "production"
  DATABASE_URL: "postgresql://user:pass@postgres-service:5432/flipkart"
  REDIS_URL: "redis://redis-service:6379/0"
```

#### 2. Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flipkart-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flipkart
  template:
    metadata:
      labels:
        app: flipkart
    spec:
      containers:
      - name: app
        image: flipkart-monolith:latest
        ports:
        - containerPort: 5000
        envFrom:
        - configMapRef:
            name: flipkart-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

#### 3. Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: flipkart-service
spec:
  type: LoadBalancer
  selector:
    app: flipkart
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
```

#### 4. HPA (Horizontal Pod Autoscaler)

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: flipkart-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: flipkart-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace flipkart

# Apply configurations
kubectl apply -f k8s/ -n flipkart

# Check status
kubectl get pods -n flipkart
kubectl get services -n flipkart
```

## Performance Tuning

### Application Tuning

#### 1. Gunicorn Workers

```python
# For CPU-bound: workers = (2 × CPU cores) + 1
# For I/O-bound: workers = (4 × CPU cores) + 1

# Update Dockerfile CMD:
CMD ["gunicorn", "--bind", "0.0.0.0:5000", 
     "--workers", "8",  # Adjust based on CPU
     "--worker-class", "gevent",
     "--worker-connections", "1000",
     "--timeout", "120",
     "app:create_app()"]
```

#### 2. Database Connection Pool

```python
# config.py
SQLALCHEMY_POOL_SIZE = 30  # Increase for more concurrent users
SQLALCHEMY_MAX_OVERFLOW = 60
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_POOL_RECYCLE = 1800
```

#### 3. Redis Configuration

```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
timeout 300
tcp-keepalive 60
```

### Database Tuning (PostgreSQL)

```sql
-- postgresql.conf
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10485kB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
```

## Monitoring & Logging

### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
```

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'flipkart-app'
    static_configs:
      - targets: ['app:5000']
```

### Application Logs

```bash
# View logs
docker-compose logs -f app

# Export logs to file
docker-compose logs app > app.log

# Use ELK Stack for production
# Elasticsearch + Logstash + Kibana
```

## Backup & Recovery

### Database Backup

```bash
# Automated daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"

docker-compose exec -T db pg_dump -U flipkart_user flipkart_db | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

### Database Restore

```bash
# Restore from backup
gunzip < backup_20260120.sql.gz | docker-compose exec -T db psql -U flipkart_user flipkart_db
```

### Automated Backup with Cron

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/flipkart-app/backup.sh
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```bash
# Check database status
docker-compose ps db
docker-compose logs db

# Restart database
docker-compose restart db
```

#### 2. Out of Memory

```bash
# Check memory usage
docker stats

# Increase container memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

#### 3. High CPU Usage

```bash
# Identify bottleneck
docker stats
docker-compose logs app | grep -i error

# Check for slow queries
docker-compose exec db psql -U flipkart_user -d flipkart_db -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

#### 4. Port Already in Use

```bash
# Find process
sudo lsof -i :5000
sudo lsof -i :80

# Kill process or change port
```

### Performance Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Basic test
ab -n 1000 -c 100 http://localhost/health

# Load test with auth
ab -n 1000 -c 100 -H "Authorization: Bearer TOKEN" http://localhost/api/products
```

### Health Checks

```bash
# Application health
curl http://localhost/health

# Database health
docker-compose exec db pg_isready -U flipkart_user

# Redis health
docker-compose exec redis redis-cli ping
```

## Security Checklist

- [ ] Strong SECRET_KEY and JWT_SECRET_KEY set
- [ ] CORS configured with specific origins
- [ ] SSL/TLS certificates installed
- [ ] Firewall configured (UFW/iptables)
- [ ] Database credentials secured
- [ ] Rate limiting enabled
- [ ] Regular security updates
- [ ] Backup system in place
- [ ] Monitoring and alerting configured
- [ ] Non-root Docker containers

## Maintenance

### Regular Tasks

**Daily:**
- Monitor application logs
- Check error rates
- Verify backups

**Weekly:**
- Review performance metrics
- Check disk space
- Update dependencies (if needed)

**Monthly:**
- Security patches
- Database optimization
- Clean old logs

---

**For additional support, refer to README.md or check application logs**
