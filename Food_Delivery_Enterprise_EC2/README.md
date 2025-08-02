# Enterprise Food Delivery System v3.0

A production-grade food delivery platform with advanced task processing, real-time notifications, analytics pipelines, and enterprise-level monitoring.

## Features

### Core Functionality
- **Order Management**: Complete order lifecycle with workflow tracking
- **Restaurant Management**: Restaurant profiles, menus, and order management
- **Customer Management**: Customer profiles and order history
- **Menu Management**: Dynamic menu items with availability tracking

### Enterprise Task Processing
- **Multi-stage Order Processing**: 5-stage workflow with progress tracking
- **Real-time Notifications**: Multi-channel notification system
- **Analytics Pipeline**: Business intelligence and reporting
- **ML Recommendation Training**: Automated model training
- **External Service Integration**: Payment gateways, delivery tracking
- **System Monitoring**: Health checks and performance metrics

### Advanced Celery Features
- **Task Routing**: Dedicated queues for different task types
- **Priority Management**: Task prioritization system
- **Retry Logic**: Sophisticated error handling and retry mechanisms
- **Rate Limiting**: Controlled task execution rates
- **Monitoring**: Real-time task monitoring with Flower

### Production Deployment
- **EC2 Deployment**: Complete AWS EC2 setup script
- **Redis Integration**: Production Redis configuration
- **Nginx Proxy**: Load balancing and SSL termination
- **Systemd Services**: Automated service management
- **Health Monitoring**: Comprehensive health checks

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI API   │    │   Celery Beat   │    │   Flower UI     │
│   (Port 8000)   │    │   (Scheduler)   │    │   (Port 5555)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Redis Broker  │
                    │   (Port 6379)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Celery Workers │
                    │  (Multi-Queue)  │
                    └─────────────────┘
```

## Quick Start

### Local Development

1. **Clone and Setup**
```bash
git clone <repository>
cd Food_Delivery_Enterprise_EC2
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Database Setup**
```bash
python -c "from database import init_db; init_db()"
```

4. **Start Services**
```bash
# Terminal 1: FastAPI Application
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Redis (if not running)
redis-server

# Terminal 3: Celery Worker
celery -A celery_app worker --loglevel=info

# Terminal 4: Celery Beat (Scheduler)
celery -A celery_app beat --loglevel=info

# Terminal 5: Flower Monitoring
celery -A celery_app flower --port=5555
```

### EC2 Deployment

1. **Launch EC2 Instance**
   - Instance Type: t2.micro (Free tier)
   - AMI: Ubuntu Server 22.04 LTS
   - Security Groups: Allow SSH (22), HTTP (80), HTTPS (443)

2. **Deploy Application**
```bash
# Upload files to EC2
scp -r . ubuntu@your-ec2-ip:/home/ubuntu/food-delivery-enterprise/

# SSH into EC2
ssh ubuntu@your-ec2-ip

# Run deployment script
cd food-delivery-enterprise
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```

3. **Access Services**
   - API: `http://your-ec2-ip:8000`
   - API Docs: `http://your-ec2-ip:8000/docs`
   - Flower Monitoring: `http://your-ec2-ip:5555`

## API Endpoints

### Order Management
- `POST /orders/` - Create new order
- `GET /orders/{order_id}` - Get order details
- `PUT /orders/{order_id}/status` - Update order status

### Workflow Management
- `POST /workflows/order-processing/{order_id}` - Start order processing
- `GET /workflows/order/{order_id}/status` - Get workflow status
- `POST /workflows/order/{order_id}/cancel` - Cancel workflow

### Notification Campaigns
- `POST /campaigns/notifications/create` - Create notification campaign
- `GET /campaigns/{campaign_id}/status` - Get campaign status
- `POST /campaigns/{campaign_id}/pause` - Pause campaign

### Analytics Pipeline
- `POST /analytics/generate-report/{report_type}` - Generate analytics report
- `GET /analytics/pipeline-status` - Get pipeline health
- `POST /analytics/ml-training/trigger` - Trigger ML training

### System Monitoring
- `GET /celery/workers/health` - Worker health status
- `GET /celery/queues/metrics` - Queue performance metrics
- `GET /celery/tasks/failed` - Failed task analysis
- `POST /celery/workers/scale/{queue_name}` - Auto-scale workers

### Restaurant Management
- `POST /restaurants/` - Create restaurant
- `GET /restaurants/` - List all restaurants
- `GET /restaurants/{restaurant_id}` - Get restaurant details

### Customer Management
- `POST /customers/` - Create customer
- `GET /customers/` - List all customers
- `GET /customers/{customer_id}` - Get customer details

### Menu Management
- `POST /menu-items/` - Create menu item
- `GET /menu-items/` - List menu items

## Task Categories

### Order Processing Pipeline
- **process_order_workflow**: Multi-stage order processing (5 stages)
- **update_order_status**: Real-time status updates with notifications

### Real-time Notifications
- **send_realtime_notifications**: Multi-channel notification system
- **bulk_notification_campaign**: Marketing campaigns with segmentation

### Analytics and Reporting
- **generate_business_analytics**: Comprehensive business reports
- **ml_recommendation_training**: ML model training pipeline

### External Service Integration
- **sync_payment_gateway**: Payment provider synchronization
- **update_delivery_tracking**: Real-time GPS tracking updates

### Production Monitoring
- **system_health_check**: System resource monitoring
- **cleanup_old_tasks**: Task cleanup and maintenance

## Queue Configuration

| Queue | Priority | Purpose | Rate Limit |
|-------|----------|---------|------------|
| orders | 10 | Order processing | 10/min |
| payments | 9 | Payment processing | 20/min |
| delivery | 7 | Delivery tracking | 15/min |
| notifications | 6 | Real-time notifications | 100/min |
| monitoring | 5 | System health checks | 12/hour |
| maintenance | 3 | Task cleanup | 2/hour |
| analytics | 2 | Business analytics | 2/hour |
| ml_processing | 1 | ML model training | 1/hour |

## Monitoring and Health Checks

### Health Check Endpoint
```bash
curl http://your-server:8000/health
```

### Flower Monitoring
- URL: `http://your-server:5555`
- Features: Real-time task monitoring, worker status, queue metrics

### System Health Script
```bash
./health_check.sh
```

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///./food_delivery_enterprise.db

# Redis
REDIS_URL=redis://:password@localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://:password@localhost:6379/0
CELERY_RESULT_BACKEND=redis://:password@localhost:6379/0

# Application
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=production

# Security
CELERY_SECURITY_KEY=your-secret-key
```

### Redis Configuration
- Memory limit: 256MB
- Persistence: RDB snapshots
- Security: Password authentication
- Performance: Optimized for Celery

## Troubleshooting

### Common Issues

1. **Redis Connection Issues**
```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis connection
redis-cli -a your_password ping

# Restart Redis
sudo systemctl restart redis-server
```

2. **Celery Worker Issues**
```bash
# Check worker status
sudo systemctl status food-delivery-worker

# View worker logs
sudo journalctl -u food-delivery-worker -f

# Restart worker
sudo systemctl restart food-delivery-worker
```

3. **API Issues**
```bash
# Check API status
sudo systemctl status food-delivery-api

# View API logs
sudo journalctl -u food-delivery-api -f

# Test API health
curl http://localhost:8000/health
```

### Performance Optimization

1. **Worker Scaling**
```bash
# Scale specific queue workers
curl -X POST "http://localhost:8000/celery/workers/scale/orders?count=2"
```

2. **Queue Monitoring**
```bash
# Check queue metrics
curl http://localhost:8000/celery/queues/metrics
```

3. **System Resources**
```bash
# Monitor system health
curl http://localhost:8000/analytics/pipeline-status
```

## Security Considerations

1. **Change Default Passwords**
   - Redis password in `/etc/redis/redis.conf`
   - Celery security key in `.env`
   - Database credentials

2. **SSL/TLS Configuration**
   - Install SSL certificates
   - Configure Nginx for HTTPS
   - Update security groups

3. **Firewall Configuration**
   - Restrict access to necessary ports only
   - Use security groups in AWS
   - Enable UFW firewall

4. **Monitoring and Alerting**
   - Set up CloudWatch alarms
   - Configure log monitoring
   - Implement automated backups

## Development

### Adding New Tasks
1. Define task in `tasks.py`
2. Add routing in `celery_app.py`
3. Create API endpoint in `main.py`
4. Add schemas in `schemas.py`
5. Update CRUD operations in `crud.py`

### Database Migrations
```bash
# For schema changes, update models.py and run:
python -c "from database import init_db; init_db()"
```

### Testing
```bash
# Run health checks
./health_check.sh

# Test API endpoints
curl http://localhost:8000/docs

# Monitor tasks
curl http://localhost:5555/
```

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs: `sudo journalctl -u service-name -f`
3. Test individual components
4. Verify configuration files

## Version History

- **v3.0.0**: Enterprise task processing with EC2 deployment
- **v2.0.0**: Advanced caching and monitoring
- **v1.0.0**: Basic food delivery system 