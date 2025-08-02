# Quick Start Guide - Zomato Food Delivery System

This guide will help you get the Zomato-like food delivery system up and running quickly.

## Prerequisites

- Python 3.8+
- Redis Server
- Git

## Option 1: Local Development Setup

### 1. Clone and Setup
```bash
git clone <repository-url>
cd zomato_v1_celery
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Redis
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis

# Windows
# Download Redis from https://redis.io/download
```

### 4. Start Services

**Terminal 1 - Start Celery Worker:**
```bash
celery -A celery_app worker --loglevel=info --concurrency=2
```

**Terminal 2 - Start FastAPI Application:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Start Flower Monitoring (Optional):**
```bash
celery -A celery_app flower --port=5555
```

### 5. Test the Application
- API Documentation: http://localhost:8000/docs
- Flower Monitoring: http://localhost:5555

## Option 2: Docker Setup

### 1. Using Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Access Services
- API: http://localhost:8000
- Flower: http://localhost:5555
- Nginx Proxy: http://localhost

## Option 3: AWS EC2 Deployment

### 1. Launch EC2 Instance
- Use Ubuntu 20.04 LTS
- t2.micro (free tier)
- Security Group: Open ports 22, 80, 8000, 6379, 5555

### 2. Connect and Deploy
```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Clone repository
git clone <repository-url>
cd zomato_v1_celery

# Make deployment script executable
chmod +x deploy_ec2.sh

# Run deployment
./deploy_ec2.sh
```

### 3. Access Services
- API: http://your-ec2-ip:8000
- Flower: http://your-ec2-ip:5555
- Nginx: http://your-ec2-ip

## Quick API Tests

### 1. Create a Restaurant
```bash
curl -X POST "http://localhost:8000/restaurants/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pizza Palace",
    "cuisine_type": "Italian",
    "address": "123 Main St, City",
    "phone": "+1-555-0123",
    "rating": 4.5,
    "price_range": "$$",
    "description": "Best pizza in town"
  }'
```

### 2. Generate Restaurant Report
```bash
curl -X POST "http://localhost:8000/tasks/generate-report/Italian"
```

### 3. Check Task Status
```bash
# Get the task_id from the previous response
curl "http://localhost:8000/tasks/status/{task_id}"
```

### 4. Check Worker Status
```bash
curl "http://localhost:8000/workers/status"
```

## Monitoring and Management

### Health Check
```bash
# Local
curl http://localhost:8000/

# Docker
docker-compose exec api curl http://localhost:8000/

# EC2
curl http://your-ec2-ip:8000/
```

### View Logs
```bash
# Local
# Check terminal outputs

# Docker
docker-compose logs api
docker-compose logs worker
docker-compose logs flower

# EC2
sudo journalctl -u zomato-api -f
sudo journalctl -u zomato-worker -f
sudo journalctl -u zomato-flower -f
```

### Restart Services
```bash
# Local
# Stop and restart terminals

# Docker
docker-compose restart

# EC2
sudo systemctl restart zomato-api zomato-worker zomato-flower
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```bash
   # Check Redis status
   redis-cli ping
   
   # Restart Redis
   sudo systemctl restart redis-server
   ```

2. **Celery Worker Not Starting**
   ```bash
   # Check Redis connection
   redis-cli ping
   
   # Restart worker
   pkill -f celery
   celery -A celery_app worker --loglevel=info
   ```

3. **Port Already in Use**
   ```bash
   # Find process using port
   lsof -i :8000
   
   # Kill process
   kill -9 <PID>
   ```

### Performance Tips

1. **Increase Worker Concurrency**
   ```bash
   celery -A celery_app worker --concurrency=4
   ```

2. **Monitor Resource Usage**
   ```bash
   # Check CPU/Memory
   htop
   
   # Check disk usage
   df -h
   ```

3. **Scale Workers**
   ```bash
   # Start multiple workers
   celery -A celery_app worker --concurrency=2 -n worker1@%h
   celery -A celery_app worker --concurrency=2 -n worker2@%h
   ```

## Next Steps

1. **Add Authentication**: Implement JWT authentication
2. **Database Migration**: Use Alembic for database migrations
3. **Testing**: Add unit and integration tests
4. **CI/CD**: Set up GitHub Actions for automated deployment
5. **Monitoring**: Add Prometheus and Grafana for metrics
6. **Load Balancing**: Use multiple API instances with load balancer

## Support

For issues and questions:
- Check the main README.md for detailed documentation
- Review the API documentation at http://localhost:8000/docs
- Monitor logs for error messages
- Use Flower dashboard for task monitoring 