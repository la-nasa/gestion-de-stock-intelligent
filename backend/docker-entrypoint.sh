#!/bin/bash
set -e

echo "========================================"
echo "IUC Inventory System - Backend"
echo "========================================"
echo "Environment: ${DJANGO_SETTINGS_MODULE}"
echo "Database: ${DATABASE_URL}"
echo "========================================"

# Function to wait for database
wait_for_db() {
    echo "Waiting for database..."
    while ! nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do
        sleep 1
    done
    echo "Database is ready!"
}

# Function to wait for Redis
wait_for_redis() {
    echo "Waiting for Redis..."
    while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
        sleep 1
    done
    echo "Redis is ready!"
}

# Function to run migrations
run_migrations() {
    echo "Running database migrations..."
    python manage.py migrate --noinput
    echo "Migrations completed!"
}

# Function to collect static files
collect_static() {
    echo "Collecting static files..."
    python manage.py collectstatic --noinput --clear
    echo "Static files collected!"
}

# Function to create superuser if needed
create_superuser() {
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        echo "Creating superuser..."
        python manage.py createsuperuser --noinput || true
        echo "Superuser created!"
    fi
}

# Main execution
wait_for_db
wait_for_redis

if [ "$1" = "gunicorn" ]; then
    run_migrations
    collect_static
    create_superuser
fi

echo "Starting application..."
exec "$@"
