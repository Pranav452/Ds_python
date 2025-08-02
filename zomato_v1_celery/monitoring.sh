#!/bin/bash

# Zomato Food Delivery System - Monitoring Script
# This script monitors the health of all services

echo "=== Zomato Food Delivery System - Health Check ==="
echo "Timestamp: $(date)"
echo ""

# Check system resources
echo "=== System Resources ==="
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{print $5}')"
echo ""

# Check Redis
echo "=== Redis Status ==="
if systemctl is-active --quiet redis-server; then
    echo "Redis: RUNNING"
    redis-cli ping > /dev/null 2>&1 && echo "Redis Connection: OK" || echo "Redis Connection: FAILED"
else
    echo "Redis: STOPPED"
fi
echo ""

# Check FastAPI service
echo "=== FastAPI Service ==="
if systemctl is-active --quiet zomato-api; then
    echo "FastAPI Service: RUNNING"
    curl -f http://localhost:8000/ > /dev/null 2>&1 && echo "API Health Check: OK" || echo "API Health Check: FAILED"
else
    echo "FastAPI Service: STOPPED"
fi
echo ""

# Check Celery worker
echo "=== Celery Worker ==="
if systemctl is-active --quiet zomato-worker; then
    echo "Celery Worker: RUNNING"
    curl -f http://localhost:8000/workers/status > /dev/null 2>&1 && echo "Worker Status Check: OK" || echo "Worker Status Check: FAILED"
else
    echo "Celery Worker: STOPPED"
fi
echo ""

# Check Flower monitoring
echo "=== Flower Monitoring ==="
if systemctl is-active --quiet zomato-flower; then
    echo "Flower Service: RUNNING"
    curl -f http://localhost:5555/ > /dev/null 2>&1 && echo "Flower Health Check: OK" || echo "Flower Health Check: FAILED"
else
    echo "Flower Service: STOPPED"
fi
echo ""

# Check Nginx
echo "=== Nginx ==="
if systemctl is-active --quiet nginx; then
    echo "Nginx: RUNNING"
    nginx -t > /dev/null 2>&1 && echo "Nginx Configuration: OK" || echo "Nginx Configuration: FAILED"
else
    echo "Nginx: STOPPED"
fi
echo ""

# Check recent logs for errors
echo "=== Recent Error Logs (Last 10 lines) ==="
echo "FastAPI Errors:"
sudo journalctl -u zomato-api --since "5 minutes ago" | grep -i error | tail -5 || echo "No recent errors"
echo ""

echo "Celery Worker Errors:"
sudo journalctl -u zomato-worker --since "5 minutes ago" | grep -i error | tail -5 || echo "No recent errors"
echo ""

echo "Flower Errors:"
sudo journalctl -u zomato-flower --since "5 minutes ago" | grep -i error | tail -5 || echo "No recent errors"
echo ""

# Check active tasks
echo "=== Active Tasks ==="
curl -s http://localhost:8000/tasks/list 2>/dev/null | python3 -m json.tool || echo "Could not fetch active tasks"
echo ""

# Check worker status
echo "=== Worker Status ==="
curl -s http://localhost:8000/workers/status 2>/dev/null | python3 -m json.tool || echo "Could not fetch worker status"
echo ""

echo "=== Health Check Complete ===" 