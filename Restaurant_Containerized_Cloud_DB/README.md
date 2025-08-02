# Restaurant Menu System v3.0 - Containerized with Cloud Database

A sophisticated, containerized restaurant menu system with cloud database integration, advanced task processing, and production-ready deployment infrastructure.

## 🚀 Features

- **Containerized Architecture**: Multi-stage Docker builds with uv package manager
- **Cloud Database Integration**: Support for AWS RDS, Google Cloud SQL, Azure Database, Supabase, Neon
- **Advanced Task Processing**: Celery with Redis for background job processing
- **Production Deployment**: Docker Compose orchestration with Nginx reverse proxy
- **Monitoring & Observability**: Flower for Celery monitoring, structured logging
- **Database Migrations**: Alembic for professional schema management
- **Security**: Non-root containers, SSL/TLS support, rate limiting
- **Scalability**: Connection pooling, load balancing, health checks

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   FastAPI App   │    │  Celery Worker  │
│   (Port 80/443) │    │   (Port 8000)   │    │   (Background)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Redis Cache   │
                    │   (Port 6379)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Cloud Database  │
                    │  (PostgreSQL)   │
                    └─────────────────┘
```

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Cloud database instance (AWS RDS, Supabase, etc.)
- AWS EC2 instance (for production deployment)

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Restaurant_Containerized_Cloud_DB
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Configure Cloud Database

Update the `.env` file with your cloud database credentials:

```bash
# For AWS RDS
DATABASE_URL=postgresql://user:password@your-rds-endpoint:5432/dbname
DATABASE_SSL_MODE=require

# For Supabase
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# For Neon
DATABASE_URL=postgresql://user:password@ep-example-123456.us-east-1.aws.neon.tech/dbname
```

### 4. Run with Docker Compose

```bash
# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Access the Application

- **API Documentation**: http://localhost/docs
- **Health Check**: http://localhost/health
- **Flower Monitoring**: http://localhost:5555
- **Metrics**: http://localhost/metrics

## 🐳 Docker Configuration

### Multi-stage Dockerfile

The Dockerfile uses a multi-stage build for optimized production images:

```dockerfile
# Builder stage with uv package manager
FROM python:3.11-slim as builder
# Install dependencies using uv

# Runtime stage
FROM python:3.11-slim as runtime
# Copy built application with non-root user
```

### Docker Compose Services

- **app**: FastAPI application
- **redis**: Redis cache and Celery broker
- **celery-worker**: Background task processing
- **celery-beat**: Scheduled tasks
- **flower**: Celery monitoring
- **nginx**: Reverse proxy and load balancer
- **postgres**: Local database (for development)

## 🗄️ Database Configuration

### Cloud Database Options

1. **AWS RDS PostgreSQL**
   ```bash
   DATABASE_URL=postgresql://user:password@your-rds-endpoint:5432/dbname
   DATABASE_SSL_MODE=require
   ```

2. **Supabase**
   ```bash
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```

3. **Neon**
   ```bash
   DATABASE_URL=postgresql://user:password@ep-example-123456.us-east-1.aws.neon.tech/dbname
   ```

### Database Migrations

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## 🚀 Production Deployment

### AWS EC2 Deployment

1. **Configure EC2 Instance**
   ```bash
   # Update deploy_ec2.sh with your EC2 details
   EC2_INSTANCE_IP="your-ec2-ip"
   EC2_KEY_PATH="~/.ssh/your-key.pem"
   ```

2. **Run Deployment Script**
   ```bash
   chmod +x deploy_ec2.sh
   ./deploy_ec2.sh
   ```

### Manual Deployment Steps

1. **Install Docker on EC2**
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose
   sudo usermod -aG docker $USER
   ```

2. **Copy Project Files**
   ```bash
   scp -r . ubuntu@your-ec2-ip:~/restaurant-system/
   ```

3. **Configure Environment**
   ```bash
   ssh ubuntu@your-ec2-ip
   cd restaurant-system
   cp .env.example .env
   # Edit .env with production settings
   ```

4. **Deploy Containers**
   ```bash
   docker-compose up -d --build
   ```

## 📊 Monitoring and Observability

### Health Checks

- **Application Health**: `GET /health`
- **System Metrics**: `GET /metrics`
- **Container Health**: Docker health checks

### Logging

Structured logging with JSON format:

```python
import structlog

logger = structlog.get_logger()
logger.info("Order processed", order_id=123, status="completed")
```

### Monitoring Tools

- **Flower**: Celery task monitoring at `/flower`
- **Prometheus**: Metrics collection
- **Grafana**: Dashboard visualization (optional)

## 🔧 Development

### Local Development

```bash
# Install uv package manager
pip install uv

# Install dependencies
uv sync

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run Celery worker
celery -A celery_app worker --loglevel=info

# Run Celery beat
celery -A celery_app beat --loglevel=info
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📚 API Documentation

### Core Endpoints

- `POST /users/` - Create user
- `GET /restaurants/` - List restaurants
- `POST /orders/` - Create order
- `GET /orders/{order_id}` - Get order details
- `POST /reviews/` - Create review

### System Endpoints

- `GET /health` - Health check
- `GET /metrics` - System metrics
- `POST /analytics/generate` - Generate analytics report

## 🔒 Security Features

- **Non-root containers**: All containers run as non-root users
- **SSL/TLS**: Nginx configured for HTTPS
- **Rate limiting**: API rate limiting with Nginx
- **CORS**: Configurable CORS policies
- **Input validation**: Pydantic schema validation
- **SQL injection protection**: SQLAlchemy ORM

## 📈 Performance Optimization

- **Connection pooling**: Database connection pooling
- **Redis caching**: Session and data caching
- **Background processing**: Celery for async tasks
- **Load balancing**: Nginx reverse proxy
- **Health checks**: Container and application health monitoring

## 🛡️ Backup and Recovery

### Automated Backups

```bash
# Manual backup
./backup.sh

# Automated daily backups (configured in deploy script)
# Runs daily at 2 AM
```

### Backup Contents

- Database dumps (PostgreSQL)
- Redis data snapshots
- Application logs
- Configuration files

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database URL in .env
   # Verify SSL settings for cloud databases
   # Test connection manually
   ```

2. **Celery Tasks Not Processing**
   ```bash
   # Check Redis connection
   # Verify Celery worker is running
   # Check Flower monitoring interface
   ```

3. **Container Health Checks Failing**
   ```bash
   # Check container logs
   docker-compose logs app
   
   # Verify health check endpoint
   curl http://localhost/health
   ```

### Debug Commands

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f app

# Access container shell
docker-compose exec app bash

# Check database connection
docker-compose exec app python -c "from database import check_db_connection; print(check_db_connection())"
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:

- Create an issue in the repository
- Check the documentation at `/docs`
- Review the troubleshooting section

---

**Version**: 3.0.0  
**Last Updated**: 2024  
**Python Version**: 3.11+  
**Docker Version**: 20.10+ 