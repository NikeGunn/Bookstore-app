#!/bin/bash
# Script to back up PostgreSQL database from Docker container

# Read environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Set default values if not provided in .env
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
DB_NAME=${DB_NAME:-postgres}
DB_CONTAINER=${DB_CONTAINER:-"pyhon-store-v2_db_1"}

# Create backup directory if it doesn't exist
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# Create filename with timestamp
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILENAME="$BACKUP_DIR/${DB_NAME}_backup_$DATE.sql"

echo "Creating database backup: $BACKUP_FILENAME"

# Run pg_dump inside the PostgreSQL container
docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME > $BACKUP_FILENAME

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully"
    
    # Compress the backup
    gzip $BACKUP_FILENAME
    echo "Backup compressed: $BACKUP_FILENAME.gz"
    
    # Delete backups older than 30 days
    find $BACKUP_DIR -name "*.gz" -type f -mtime +30 -delete
    echo "Removed backups older than 30 days"
else
    echo "Backup failed"
    exit 1
fi
