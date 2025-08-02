# Zomato-like Food Delivery System with Celery Integration

A comprehensive food delivery system built with FastAPI, Celery background tasks, and Redis caching. This system demonstrates advanced backend engineering concepts including asynchronous task processing, caching, and AWS EC2 deployment.

## Features

- **Restaurant Management**: CRUD operations for restaurants with SQLAlchemy ORM
- **Celery Background Tasks**: Asynchronous processing for time-consuming operations
- **Redis Caching**: High-performance caching layer
- **Task Monitoring**: Real-time task status tracking and progress monitoring
- **Worker Management**: Celery worker status monitoring and control
- **AWS EC2 Ready**: Deployment scripts and configuration for cloud hosting

## Background Tasks

### 1. Restaurant Report Generation
- Generates comprehensive analytics for specific cuisine types
- Progress tracking: 0% → 25% → 50% → 75% → 100%
- Returns total restaurants, average ratings, popular price ranges, top restaurants

### 2. Restaurant Data Synchronization
- Syncs restaurant information with external APIs
- Updates ratings and reviews from third-party sources
- Simulates Google Maps, Yelp API integration

### 3. Notification System
- Sends notifications for new restaurants, updates, and rating changes
- Supports email, SMS, and push notification simulation
- Configurable notification types and recipients

## API Endpoints

### Restaurant Management
- `POST /restaurants/` - Create new restaurant
- `GET /restaurants/` - List all restaurants
- `GET /restaurants/{id}` - Get specific restaurant
- `PUT /restaurants/{id}` - Update restaurant
- `DELETE /restaurants/{id}` - Delete restaurant

### Task Management
- `POST /tasks/generate-report/{cuisine_type}` - Start report generation
- `GET /tasks/status/{task_id}` - Check task status and progress
- `GET /tasks/list` - List all active tasks
- `DELETE /tasks/cancel/{task_id}` - Cancel running task
- `POST /restaurants/{id}/sync` - Trigger data synchronization
- `GET /workers/status` - Check Celery worker status

## Project Structure

```
zomato_v1_celery/
├── main.py                 # FastAPI application
├── database.py             # Database configuration
├── models.py               # SQLAlchemy models
├── schemas.py              # Pydantic schemas
├── crud.py                 # CRUD operations
├── celery_app.py           # Celery configuration
├── tasks.py                # Background tasks
├── worker.py               # Celery worker entry point
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd zomato_v1_celery
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Redis**
   ```bash
   # Install Redis (Ubuntu/Debian)
   sudo apt-get install redis-server
   
   # Start Redis
   sudo systemctl start redis-server
   ```

4. **Environment Variables**
   Create a `.env` file:
   ```
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   DATABASE_URL=sqlite:///./restaurants.db
   ```

## Running the Application

### 1. Start Redis Server
```bash
redis-server
```

### 2. Start Celery Worker
```bash
celery -A celery_app worker --loglevel=info --concurrency=2
```

### 3. Start FastAPI Application
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start Flower (Optional - for monitoring)
```bash
celery -A celery_app flower --port=5555
```

## Usage Examples

### Create a Restaurant
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

### Generate Restaurant Report
```bash
curl -X POST "http://localhost:8000/tasks/generate-report/Italian"
```

### Check Task Status
```bash
curl "http://localhost:8000/tasks/status/{task_id}"
```

### Sync Restaurant Data
```bash
curl -X POST "http://localhost:8000/restaurants/1/sync"
```

### Check Worker Status
```bash
curl "http://localhost:8000/workers/status"
```

## AWS EC2 Deployment

### Prerequisites
- AWS EC2 instance (t2.micro for free tier)
- Ubuntu 20.04 LTS
- Security group with ports 22, 80, 8000, 6379, 5555 open

### Deployment Steps

1. **Connect to EC2 instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

2. **Update system**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Install dependencies**
   ```bash
   sudo apt install python3-pip python3-venv redis-server nginx -y
   ```

4. **Clone application**
   ```bash
   git clone <repository-url>
   cd zomato_v1_celery
   ```

5. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Configure Redis**
   ```bash
   sudo systemctl enable redis-server
   sudo systemctl start redis-server
   ```

7. **Create systemd services**

   **FastAPI Service** (`/etc/systemd/system/zomato-api.service`):
   ```ini
   [Unit]
   Description=Zomato API
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/zomato_v1_celery
   Environment=PATH=/home/ubuntu/zomato_v1_celery/venv/bin
   ExecStart=/home/ubuntu/zomato_v1_celery/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   **Celery Worker Service** (`/etc/systemd/system/zomato-worker.service`):
   ```ini
   [Unit]
   Description=Zomato Celery Worker
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/zomato_v1_celery
   Environment=PATH=/home/ubuntu/zomato_v1_celery/venv/bin
   ExecStart=/home/ubuntu/zomato_v1_celery/venv/bin/celery -A celery_app worker --loglevel=info
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

8. **Start services**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable zomato-api
   sudo systemctl enable zomato-worker
   sudo systemctl start zomato-api
   sudo systemctl start zomato-worker
   ```

9. **Configure Nginx** (optional)
   ```bash
   sudo nano /etc/nginx/sites-available/zomato
   ```
   
   Add configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

10. **Enable site**
    ```bash
    sudo ln -s /etc/nginx/sites-available/zomato /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    ```

## Monitoring and Logs

### Check Service Status
```bash
sudo systemctl status zomato-api
sudo systemctl status zomato-worker
```

### View Logs
```bash
sudo journalctl -u zomato-api -f
sudo journalctl -u zomato-worker -f
```

### Flower Monitoring
Access Flower dashboard at `http://your-ec2-ip:5555` for real-time task monitoring.

## Task Status Tracking

The system tracks task status with the following states:
- `PENDING`: Task queued but not started
- `PROCESSING`: Task currently running
- `SUCCESS`: Task completed successfully
- `FAILURE`: Task failed with error
- `CANCELLED`: Task was cancelled by user

## Performance Considerations

- **Concurrency**: Celery workers configured with 2 concurrent processes
- **Rate Limiting**: Tasks have rate limits to prevent overload
- **Timeouts**: Tasks have 30-minute time limits with 25-minute soft limits
- **Retries**: Failed tasks automatically retry up to 3 times
- **Caching**: Redis used for both message broker and result backend

## Security Notes

- Use environment variables for sensitive configuration
- Implement proper authentication and authorization
- Use HTTPS in production
- Configure firewall rules appropriately
- Regular security updates for dependencies

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis server is running: `sudo systemctl status redis-server`
   - Check Redis configuration: `redis-cli ping`

2. **Celery Worker Not Starting**
   - Check worker logs: `sudo journalctl -u zomato-worker -f`
   - Verify Redis connection in celery configuration

3. **Task Not Executing**
   - Check worker status: `GET /workers/status`
   - Verify task is properly queued in Redis

4. **Database Issues**
   - Check database file permissions
   - Verify SQLAlchemy configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes and demonstrates advanced backend engineering concepts. 