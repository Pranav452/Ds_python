#!/bin/bash

# Enterprise Food Delivery System - EC2 Deployment Script
# This script sets up a production-ready environment on AWS EC2

set -e  # Exit on any error

echo "Starting Enterprise Food Delivery System deployment..."

# ==================== SYSTEM UPDATE AND BASIC SETUP ====================

echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "Installing essential packages..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip git curl wget unzip

# ==================== REDIS INSTALLATION AND CONFIGURATION ====================

echo "Installing Redis..."
sudo apt install -y redis-server

echo "Configuring Redis for production..."
sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup

# Create production Redis configuration
sudo tee /etc/redis/redis.conf > /dev/null << 'EOF'
# Network
bind 127.0.0.1
port 6379
timeout 300

# General
daemonize yes
pidfile /var/run/redis/redis-server.pid
loglevel notice
logfile /var/log/redis/redis-server.log

# Snapshotting
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /var/lib/redis

# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru

# Security
requirepass your_secure_redis_password

# Performance
tcp-keepalive 60
tcp-backlog 511
EOF

echo "Starting Redis service..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
echo "Testing Redis connection..."
redis-cli -a your_secure_redis_password ping

# ==================== APPLICATION SETUP ====================

echo "Setting up application directory..."
cd /home/ubuntu
mkdir -p food-delivery-enterprise
cd food-delivery-enterprise

# Copy application files (assuming they're uploaded or cloned)
# For this script, we'll assume the files are already in the directory

echo "Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# ==================== ENVIRONMENT CONFIGURATION ====================

echo "Creating environment configuration..."
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=sqlite:///./food_delivery_enterprise.db

# Redis Configuration
REDIS_URL=redis://:your_secure_redis_password@localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://:your_secure_redis_password@localhost:6379/0
CELERY_RESULT_BACKEND=redis://:your_secure_redis_password@localhost:6379/0

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=production

# Security
CELERY_SECURITY_KEY=your-super-secret-celery-key-change-this-in-production

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Monitoring
FLOWER_PORT=5555
EOF

# ==================== DATABASE INITIALIZATION ====================

echo "Initializing database..."
source venv/bin/activate
python -c "
from database import init_db
init_db()
print('Database initialized successfully')
"

# ==================== SYSTEMD SERVICE CONFIGURATION ====================

echo "Creating systemd services..."

# FastAPI Service
sudo tee /etc/systemd/system/food-delivery-api.service > /dev/null << 'EOF'
[Unit]
Description=Food Delivery Enterprise API
After=network.target redis.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/food-delivery-enterprise
Environment=PATH=/home/ubuntu/food-delivery-enterprise/venv/bin
ExecStart=/home/ubuntu/food-delivery-enterprise/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Celery Worker Service
sudo tee /etc/systemd/system/food-delivery-worker.service > /dev/null << 'EOF'
[Unit]
Description=Food Delivery Enterprise Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/food-delivery-enterprise
Environment=PATH=/home/ubuntu/food-delivery-enterprise/venv/bin
ExecStart=/home/ubuntu/food-delivery-enterprise/venv/bin/celery -A celery_app worker --loglevel=info --concurrency=4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Celery Beat Service
sudo tee /etc/systemd/system/food-delivery-beat.service > /dev/null << 'EOF'
[Unit]
Description=Food Delivery Enterprise Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/food-delivery-enterprise
Environment=PATH=/home/ubuntu/food-delivery-enterprise/venv/bin
ExecStart=/home/ubuntu/food-delivery-enterprise/venv/bin/celery -A celery_app beat --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Flower Monitoring Service
sudo tee /etc/systemd/system/food-delivery-flower.service > /dev/null << 'EOF'
[Unit]
Description=Food Delivery Enterprise Flower Monitor
After=network.target redis.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/food-delivery-enterprise
Environment=PATH=/home/ubuntu/food-delivery-enterprise/venv/bin
ExecStart=/home/ubuntu/food-delivery-enterprise/venv/bin/celery -A celery_app flower --port=5555
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# ==================== NGINX CONFIGURATION ====================

echo "Installing and configuring Nginx..."
sudo apt install -y nginx

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/food-delivery-enterprise > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    # API Proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Flower Monitoring
    location /flower {
        proxy_pass http://127.0.0.1:5555;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/food-delivery-enterprise /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# ==================== FIREWALL CONFIGURATION ====================

echo "Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # API (if needed externally)
sudo ufw allow 5555/tcp  # Flower (if needed externally)

sudo ufw --force enable

# ==================== LOGGING CONFIGURATION ====================

echo "Setting up logging..."
sudo mkdir -p /var/log/food-delivery-enterprise
sudo chown ubuntu:ubuntu /var/log/food-delivery-enterprise

# Create logrotate configuration
sudo tee /etc/logrotate.d/food-delivery-enterprise > /dev/null << 'EOF'
/var/log/food-delivery-enterprise/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload food-delivery-api
        systemctl reload food-delivery-worker
    endscript
}
EOF

# ==================== MONITORING SETUP ====================

echo "Setting up monitoring scripts..."

# Health check script
cat > /home/ubuntu/food-delivery-enterprise/health_check.sh << 'EOF'
#!/bin/bash

# Health check script for the food delivery system

echo "=== Food Delivery Enterprise Health Check ==="
echo "Timestamp: $(date)"

# Check if services are running
echo "Checking services..."
services=("food-delivery-api" "food-delivery-worker" "food-delivery-beat" "food-delivery-flower" "redis-server" "nginx")

for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "✓ $service is running"
    else
        echo "✗ $service is not running"
    fi
done

# Check API health
echo "Checking API health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is responding"
else
    echo "✗ API is not responding"
fi

# Check Redis
echo "Checking Redis..."
if redis-cli -a your_secure_redis_password ping > /dev/null 2>&1; then
    echo "✓ Redis is responding"
else
    echo "✗ Redis is not responding"
fi

# Check disk space
echo "Checking disk space..."
df -h / | tail -1

# Check memory usage
echo "Checking memory usage..."
free -h

echo "=== Health check completed ==="
EOF

chmod +x /home/ubuntu/food-delivery-enterprise/health_check.sh

# ==================== START SERVICES ====================

echo "Starting services..."

# Reload systemd
sudo systemctl daemon-reload

# Start and enable services
sudo systemctl start food-delivery-api
sudo systemctl enable food-delivery-api

sudo systemctl start food-delivery-worker
sudo systemctl enable food-delivery-worker

sudo systemctl start food-delivery-beat
sudo systemctl enable food-delivery-beat

sudo systemctl start food-delivery-flower
sudo systemctl enable food-delivery-flower

sudo systemctl start nginx
sudo systemctl enable nginx

# ==================== VERIFICATION ====================

echo "Verifying deployment..."

# Wait for services to start
sleep 10

# Check service status
echo "Service status:"
sudo systemctl status food-delivery-api --no-pager
sudo systemctl status food-delivery-worker --no-pager
sudo systemctl status nginx --no-pager

# Test API
echo "Testing API..."
curl -f http://localhost:8000/ || echo "API test failed"

# Test Flower
echo "Testing Flower monitoring..."
curl -f http://localhost:5555/ || echo "Flower test failed"

# ==================== DEPLOYMENT COMPLETE ====================

echo "=== Enterprise Food Delivery System Deployment Complete ==="
echo ""
echo "Services deployed:"
echo "- FastAPI Application: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "- API Documentation: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/docs"
echo "- Flower Monitoring: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5555"
echo ""
echo "Health check: ./health_check.sh"
echo ""
echo "Useful commands:"
echo "- View API logs: sudo journalctl -u food-delivery-api -f"
echo "- View worker logs: sudo journalctl -u food-delivery-worker -f"
echo "- Restart services: sudo systemctl restart food-delivery-api food-delivery-worker"
echo "- Check Redis: redis-cli -a your_secure_redis_password"
echo ""
echo "Remember to:"
echo "1. Change default passwords in .env file"
echo "2. Set up SSL certificates for production"
echo "3. Configure monitoring and alerting"
echo "4. Set up automated backups"
echo ""
echo "Deployment completed successfully!" 