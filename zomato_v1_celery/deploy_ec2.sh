#!/bin/bash

# Zomato Food Delivery System - AWS EC2 Deployment Script
# This script automates the deployment of the application on AWS EC2

set -e

echo "Starting Zomato Food Delivery System deployment on AWS EC2..."

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y python3-pip python3-venv redis-server nginx git curl

# Start and enable Redis
echo "Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Create application directory
echo "Setting up application directory..."
APP_DIR="/home/ubuntu/zomato_v1_celery"
mkdir -p $APP_DIR
cd $APP_DIR

# Create Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service files
echo "Creating systemd services..."

# FastAPI service
sudo tee /etc/systemd/system/zomato-api.service > /dev/null <<EOF
[Unit]
Description=Zomato Food Delivery API
After=network.target redis-server.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=CELERY_BROKER_URL=redis://localhost:6379/0
Environment=CELERY_RESULT_BACKEND=redis://localhost:6379/0
ExecStart=$APP_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Celery worker service
sudo tee /etc/systemd/system/zomato-worker.service > /dev/null <<EOF
[Unit]
Description=Zomato Celery Worker
After=network.target redis-server.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=CELERY_BROKER_URL=redis://localhost:6379/0
Environment=CELERY_RESULT_BACKEND=redis://localhost:6379/0
ExecStart=$APP_DIR/venv/bin/celery -A celery_app worker --loglevel=info --concurrency=2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Flower monitoring service (optional)
sudo tee /etc/systemd/system/zomato-flower.service > /dev/null <<EOF
[Unit]
Description=Zomato Flower Monitoring
After=network.target redis-server.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=CELERY_BROKER_URL=redis://localhost:6379/0
Environment=CELERY_RESULT_BACKEND=redis://localhost:6379/0
ExecStart=$APP_DIR/venv/bin/celery -A celery_app flower --port=5555
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/zomato > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    # API proxy
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Flower monitoring
    location /flower {
        proxy_pass http://localhost:5555;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/zomato /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Reload systemd and start services
echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable zomato-api
sudo systemctl enable zomato-worker
sudo systemctl enable zomato-flower
sudo systemctl enable nginx

sudo systemctl start zomato-api
sudo systemctl start zomato-worker
sudo systemctl start zomato-flower
sudo systemctl restart nginx

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Check service status
echo "Checking service status..."
sudo systemctl status zomato-api --no-pager -l
sudo systemctl status zomato-worker --no-pager -l
sudo systemctl status zomato-flower --no-pager -l
sudo systemctl status nginx --no-pager -l

# Test API endpoints
echo "Testing API endpoints..."
sleep 5

# Test basic endpoint
curl -f http://localhost:8000/ || echo "API not responding"

# Test worker status
curl -f http://localhost:8000/workers/status || echo "Worker status endpoint not responding"

echo ""
echo "Deployment completed successfully!"
echo ""
echo "Service URLs:"
echo "- API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "- Flower Monitoring: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5555"
echo "- Nginx Proxy: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "Useful commands:"
echo "- Check API logs: sudo journalctl -u zomato-api -f"
echo "- Check worker logs: sudo journalctl -u zomato-worker -f"
echo "- Check flower logs: sudo journalctl -u zomato-flower -f"
echo "- Restart services: sudo systemctl restart zomato-api zomato-worker zomato-flower"
echo "" 