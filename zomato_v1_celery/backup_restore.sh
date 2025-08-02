#!/bin/bash

# Zomato Food Delivery System - Backup and Restore Script
# This script handles backup and restore operations for the application

set -e

BACKUP_DIR="/home/ubuntu/backups"
APP_DIR="/home/ubuntu/zomato_v1_celery"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

backup() {
    echo "Creating backup of Zomato Food Delivery System..."
    
    # Create backup archive
    BACKUP_FILE="$BACKUP_DIR/zomato_backup_$DATE.tar.gz"
    
    # Backup application files
    tar -czf $BACKUP_FILE \
        --exclude="$APP_DIR/venv" \
        --exclude="$APP_DIR/__pycache__" \
        --exclude="$APP_DIR/*.pyc" \
        --exclude="$APP_DIR/.git" \
        -C /home/ubuntu zomato_v1_celery
    
    # Backup database
    if [ -f "$APP_DIR/restaurants.db" ]; then
        cp "$APP_DIR/restaurants.db" "$BACKUP_DIR/restaurants_$DATE.db"
    fi
    
    # Backup Redis data (if possible)
    if command -v redis-cli &> /dev/null; then
        redis-cli BGSAVE > /dev/null 2>&1 || echo "Redis backup not available"
    fi
    
    echo "Backup completed: $BACKUP_FILE"
    echo "Database backup: $BACKUP_DIR/restaurants_$DATE.db"
    
    # List recent backups
    echo ""
    echo "Recent backups:"
    ls -la $BACKUP_DIR/zomato_backup_*.tar.gz | tail -5
}

restore() {
    if [ -z "$1" ]; then
        echo "Usage: $0 restore <backup_file>"
        echo "Available backups:"
        ls -la $BACKUP_DIR/zomato_backup_*.tar.gz
        exit 1
    fi
    
    BACKUP_FILE=$1
    
    if [ ! -f "$BACKUP_FILE" ]; then
        echo "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    echo "Restoring from backup: $BACKUP_FILE"
    
    # Stop services
    echo "Stopping services..."
    sudo systemctl stop zomato-api zomato-worker zomato-flower || true
    
    # Backup current installation
    echo "Creating backup of current installation..."
    mv $APP_DIR "${APP_DIR}_backup_$(date +%Y%m%d_%H%M%S)" || true
    
    # Extract backup
    echo "Extracting backup..."
    tar -xzf $BACKUP_FILE -C /home/ubuntu
    
    # Restore database if available
    DB_BACKUP=$(echo $BACKUP_FILE | sed 's/zomato_backup_/restaurants_/g' | sed 's/.tar.gz/.db/g')
    if [ -f "$DB_BACKUP" ]; then
        echo "Restoring database..."
        cp "$DB_BACKUP" "$APP_DIR/restaurants.db"
    fi
    
    # Reinstall dependencies
    echo "Reinstalling dependencies..."
    cd $APP_DIR
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Restart services
    echo "Restarting services..."
    sudo systemctl daemon-reload
    sudo systemctl start zomato-api zomato-worker zomato-flower
    
    echo "Restore completed successfully!"
}

cleanup() {
    echo "Cleaning up old backups..."
    
    # Keep only last 5 backups
    BACKUP_COUNT=$(ls $BACKUP_DIR/zomato_backup_*.tar.gz 2>/dev/null | wc -l)
    
    if [ $BACKUP_COUNT -gt 5 ]; then
        echo "Removing old backups..."
        ls -t $BACKUP_DIR/zomato_backup_*.tar.gz | tail -n +6 | xargs rm -f
        ls -t $BACKUP_DIR/restaurants_*.db | tail -n +6 | xargs rm -f
    fi
    
    echo "Cleanup completed!"
}

list_backups() {
    echo "Available backups:"
    echo ""
    echo "Application backups:"
    ls -la $BACKUP_DIR/zomato_backup_*.tar.gz 2>/dev/null || echo "No application backups found"
    echo ""
    echo "Database backups:"
    ls -la $BACKUP_DIR/restaurants_*.db 2>/dev/null || echo "No database backups found"
}

case "$1" in
    backup)
        backup
        ;;
    restore)
        restore "$2"
        ;;
    cleanup)
        cleanup
        ;;
    list)
        list_backups
        ;;
    *)
        echo "Usage: $0 {backup|restore <file>|cleanup|list}"
        echo ""
        echo "Commands:"
        echo "  backup   - Create a new backup"
        echo "  restore  - Restore from a backup file"
        echo "  cleanup  - Remove old backups (keep last 5)"
        echo "  list     - List available backups"
        exit 1
        ;;
esac 