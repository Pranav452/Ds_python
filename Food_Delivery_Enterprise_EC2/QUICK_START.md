# Quick Start Guide - Enterprise Food Delivery System

## Prerequisites

- Python 3.11+
- Redis Server
- Git

## Local Development Setup (5 minutes)

### 1. Clone and Setup
```bash
cd Food_Delivery_Enterprise_EC2
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python -c "from database import init_db; init_db()"
```

### 3. Start Services (5 terminals)

**Terminal 1 - FastAPI Application:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Redis (if not running):**
```bash
redis-server
```

**Terminal 3 - Celery Worker:**
```bash
celery -A celery_app worker --loglevel=info
```

**Terminal 4 - Celery Beat (Scheduler):**
```bash
celery -A celery_app beat --loglevel=info
```

**Terminal 5 - Flower Monitoring:**
```bash
celery -A celery_app flower --port=5555
```

### 4. Access Services
- **API Documentation**: http://localhost:8000/docs
- **Flower Monitoring**: http://localhost:5555
- **Health Check**: http://localhost:8000/health

## EC2 Deployment (15 minutes)

### 1. Launch EC2 Instance
- **Instance Type**: t2.micro (Free tier)
- **AMI**: Ubuntu Server 22.04 LTS
- **Security Groups**: 
  - SSH (22)
  - HTTP (80)
  - HTTPS (443)
  - Custom (8000, 5555)

### 2. Upload Files
```bash
scp -r . ubuntu@your-ec2-ip:/home/ubuntu/food-delivery-enterprise/
```

### 3. Deploy
```bash
ssh ubuntu@your-ec2-ip
cd food-delivery-enterprise
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```

### 4. Access Production
- **API**: http://your-ec2-ip:8000
- **API Docs**: http://your-ec2-ip:8000/docs
- **Flower**: http://your-ec2-ip:5555

## Quick Test

### 1. Create Test Data
```bash
# Create a restaurant
curl -X POST "http://localhost:8000/restaurants/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Restaurant",
    "cuisine_type": "Italian",
    "address": "123 Main St",
    "phone": "555-0123",
    "email": "test@restaurant.com"
  }'

# Create a customer
curl -X POST "http://localhost:8000/customers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-0124",
    "address": "456 Oak Ave"
  }'

# Create menu items
curl -X POST "http://localhost:8000/menu-items/" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": 1,
    "name": "Margherita Pizza",
    "description": "Classic tomato and mozzarella",
    "price": 15.99,
    "category": "Pizza"
  }'
```

### 2. Test Order Processing
```bash
# Create an order
curl -X POST "http://localhost:8000/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "restaurant_id": 1,
    "delivery_address": "789 Pine St",
    "order_items": [
      {
        "menu_item_id": 1,
        "quantity": 2,
        "unit_price": 15.99,
        "special_instructions": "Extra cheese"
      }
    ]
  }'
```

### 3. Monitor Tasks
- Visit http://localhost:5555 to see task execution
- Check order workflow progress
- Monitor system health

## Key Features to Test

### 1. Order Workflow
- Create order → Triggers 5-stage processing
- Check workflow status: `GET /workflows/order/{order_id}/status`
- Monitor progress in Flower UI

### 2. Notifications
- Update order status → Triggers notifications
- Create notification campaign: `POST /campaigns/notifications/create`
- Monitor campaign progress

### 3. Analytics
- Generate reports: `POST /analytics/generate-report/daily_report`
- Check pipeline status: `GET /analytics/pipeline-status`
- Trigger ML training: `POST /analytics/ml-training/trigger`

### 4. System Monitoring
- Health check: `GET /health`
- Worker status: `GET /celery/workers/health`
- Queue metrics: `GET /celery/queues/metrics`

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
```bash
# Start Redis
redis-server

# Test connection
redis-cli ping
```

2. **Celery Worker Not Starting**
```bash
# Check Redis connection
redis-cli ping

# Start worker with debug
celery -A celery_app worker --loglevel=debug
```

3. **Database Issues**
```bash
# Reinitialize database
python -c "from database import init_db; init_db()"
```

### Health Check Script
```bash
# Run comprehensive health check
./health_check.sh
```

## Next Steps

1. **Customize Configuration**
   - Update `.env` file with your settings
   - Change default passwords
   - Configure Redis for production

2. **Add SSL/TLS**
   - Install SSL certificates
   - Configure Nginx for HTTPS
   - Update security groups

3. **Set Up Monitoring**
   - Configure CloudWatch alarms
   - Set up log monitoring
   - Implement automated backups

4. **Scale Production**
   - Add more Celery workers
   - Configure load balancing
   - Set up database clustering

## Support

- **Documentation**: See README.md for detailed information
- **API Docs**: http://localhost:8000/docs
- **Flower Monitoring**: http://localhost:5555
- **Health Check**: http://localhost:8000/health

## Quick Commands Reference

```bash
# Start all services locally
./start_local.sh

# Deploy to EC2
./deploy_ec2.sh

# Health check
./health_check.sh

# View logs
sudo journalctl -u food-delivery-api -f
sudo journalctl -u food-delivery-worker -f

# Restart services
sudo systemctl restart food-delivery-api food-delivery-worker

# Test API
curl http://localhost:8000/health
``` 