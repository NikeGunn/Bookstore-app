#!/bin/bash

# Wait for the database to be ready
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for database..."
    
    # Extract host and port from DATABASE_URL
    if [[ $DATABASE_URL == postgresql* ]]; then
        # Extract the host and port from DATABASE_URL
        host=$(echo $DATABASE_URL | sed -E 's/^postgresql:\/\/([^:]+):([^@]+)@([^:]+):([^\/]+)\/(.+)$/\3/')
        port=$(echo $DATABASE_URL | sed -E 's/^postgresql:\/\/([^:]+):([^@]+)@([^:]+):([^\/]+)\/(.+)$/\4/')
        
        # Handle default port if not extracted correctly
        if [ -z "$port" ]; then
            port=5432
        fi
        
        # Wait for the database
        while ! nc -z $host $port; do
            echo "Database is unavailable - sleeping"
            sleep 2
        done
        
        echo "Database is up - continuing..."
    fi
fi

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if environment variables are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput
fi

# Create sample data if requested
if [ "$CREATE_SAMPLE_DATA" = "1" ]; then
    echo "Creating sample data..."
    python manage.py create_sample_data
fi

# Start server
echo "Starting server..."
if [ "$DEBUG" = "1" ]; then
    python manage.py runserver 0.0.0.0:8000
else
    gunicorn bookstore_api.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
fi
