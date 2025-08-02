#!/bin/bash

# Restaurant Menu System v3.0 - EC2 Deployment Script
# This script deploys the containerized restaurant system on AWS EC2

set -e

# Configuration
PROJECT_NAME="restaurant-containerized-cloud-db"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
EC2_USER="ubuntu"
EC2_KEY_PATH="~/.ssh/your-key.pem"
EC2_INSTANCE_IP="your-ec2-ip"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Check if required files exist
check_files() {
    log "Checking required files..."
    
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        error "Docker Compose file not found: $DOCKER_COMPOSE_FILE"
        exit 1
    fi
    
    if [ ! -f "$ENV_FILE" ]; then
        error "Environment file not found: $ENV_FILE"
        exit 1
    fi
    
    if [ ! -f "Dockerfile" ]; then
        error "Dockerfile not found"
        exit 1
    fi
    
    log "All required files found"
}

# Install Docker and Docker Compose on EC2
install_docker() {
    log "Installing Docker and Docker Compose on EC2..."
    
    ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_INSTANCE_IP << 'EOF'
        # Update system
        sudo apt-get update
        
        # Install required packages
        sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
        
        # Add Docker's official GPG key
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # Add Docker repository
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Install Docker
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        
        # Add user to docker group
        sudo usermod -aG docker $USER
        
        # Install Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        # Start Docker service
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Verify installation
        docker --version
        docker-compose --version
EOF
    
    log "Docker installation completed"
}

# Copy project files to EC2
copy_files() {
    log "Copying project files to EC2..."
    
    # Create project directory on EC2
    ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_INSTANCE_IP "mkdir -p ~/$PROJECT_NAME"
    
    # Copy files to EC2
    scp -i $EC2_KEY_PATH -r . $EC2_USER@$EC2_INSTANCE_IP:~/$PROJECT_NAME/
    
    log "Files copied successfully"
}

# Configure environment
configure_environment() {
    log "Configuring environment..."
    
    ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_INSTANCE_IP << 'EOF'
        cd ~/$PROJECT_NAME
        
        # Create .env file from example if it doesn't exist
        if [ ! -f .env ]; then
            cp .env.example .env
            warning "Please update the .env file with your production configuration"
        fi
        
        # Set proper permissions
        chmod 600 .env
        chmod +x deploy_ec2.sh
EOF
    
    log "Environment configured"
}

# Build and deploy containers
deploy_containers() {
    log "Building and deploying containers..."
    
    ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_INSTANCE_IP << 'EOF'
        cd ~/$PROJECT_NAME
        
        # Stop existing containers
        docker-compose down || true
        
        # Remove old images
        docker system prune -f
        
        # Build and start containers
        docker-compose up -d --build
        
        # Wait for services to be ready
        echo "Waiting for services to start..."
        sleep 30
        
        # Check container status
        docker-compose ps
        
        # Check logs
        echo "Container logs:"
        docker-compose logs --tail=20
EOF
    
    log "Containers deployed successfully"
}

# Configure firewall and security
configure_security() {
    log "Configuring security settings..."
    
    ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_INSTANCE_IP << 'EOF'
        # Configure UFW firewall
        sudo ufw allow 22/tcp
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        sudo ufw allow 8000/tcp
        sudo ufw allow 5555/tcp  # Flower monitoring
        sudo ufw --force enable
        
        # Configure Docker daemon
        sudo tee /etc/docker/daemon.json > /dev/null << 'DOCKER_EOF'
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    }
}
DOCKER_EOF
        
        # Restart Docker daemon
        sudo systemctl restart docker
EOF
    
    log "Security configuration completed"
}

# Setup monitoring and logging
setup_monitoring() {
    log "Setting up monitoring and logging..."
    
    ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_INSTANCE_IP << 'EOF'
        cd ~/$PROJECT_NAME
        
        # Create log directory
        mkdir -p logs
        
        # Setup log rotation
        sudo tee /etc/logrotate.d/restaurant-system > /dev/null << 'LOGROTATE_EOF'
/home/ubuntu/restaurant-containerized-cloud-db/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
LOGROTATE_EOF
        
        # Create monitoring script
        cat > monitor.sh << 'MONITOR_EOF'
#!/bin/bash

# Health check
curl -f http://localhost/health || echo "Health check failed"

# Container status
docker-compose ps

# Resource usage
echo "=== Resource Usage ==="
docker stats --no-stream

# Disk usage
echo "=== Disk Usage ==="
df -h

# Memory usage
echo "=== Memory Usage ==="
free -h
MONITOR_EOF
        
        chmod +x monitor.sh
EOF
    
    log "Monitoring setup completed"
}

# Setup backup and restore
setup_backup() {
    log "Setting up backup and restore..."
    
    ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_INSTANCE_IP << 'EOF'
        cd ~/$PROJECT_NAME
        
        # Create backup script
        cat > backup.sh << 'BACKUP_EOF'
#!/bin/bash

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U restaurant_user restaurant_db > $BACKUP_DIR/db_backup_$DATE.sql

# Backup Redis data
docker cp restaurant-containerized-cloud-db_redis_1:/data/dump.rdb $BACKUP_DIR/redis_backup_$DATE.rdb

# Backup application logs
tar -czf $BACKUP_DIR/logs_backup_$DATE.tar.gz logs/

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
BACKUP_EOF
        
        chmod +x backup.sh
        
        # Setup cron job for daily backup
        (crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/$PROJECT_NAME/backup.sh") | crontab -
EOF
    
    log "Backup setup completed"
}

# Test deployment
test_deployment() {
    log "Testing deployment..."
    
    ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_INSTANCE_IP << 'EOF'
        cd ~/$PROJECT_NAME
        
        # Test health endpoint
        echo "Testing health endpoint..."
        curl -f http://localhost/health
        
        # Test API endpoints
        echo "Testing API endpoints..."
        curl -f http://localhost/restaurants/
        
        # Check container health
        echo "Checking container health..."
        docker-compose ps
        
        # Check logs for errors
        echo "Checking for errors in logs..."
        docker-compose logs | grep -i error || echo "No errors found"
EOF
    
    log "Deployment testing completed"
}

# Main deployment function
main() {
    log "Starting Restaurant Menu System v3.0 deployment..."
    
    # Check if EC2 instance is accessible
    if ! ssh -i $EC2_KEY_PATH -o ConnectTimeout=10 $EC2_USER@$EC2_INSTANCE_IP "echo 'Connection successful'" 2>/dev/null; then
        error "Cannot connect to EC2 instance. Please check your configuration."
        exit 1
    fi
    
    check_files
    install_docker
    copy_files
    configure_environment
    configure_security
    deploy_containers
    setup_monitoring
    setup_backup
    test_deployment
    
    log "Deployment completed successfully!"
    log "Application is available at: http://$EC2_INSTANCE_IP"
    log "API Documentation: http://$EC2_INSTANCE_IP/docs"
    log "Flower Monitoring: http://$EC2_INSTANCE_IP:5555"
    
    warning "Please update the .env file with your production configuration"
    warning "Don't forget to configure your cloud database connection"
}

# Run main function
main "$@" 