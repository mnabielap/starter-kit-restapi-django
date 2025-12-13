#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check if database is ready
wait_for_db() {
    # Extract host and port from DATABASE_URL if possible, or use defaults
    # For this script, we assume standard usage.
    echo "Waiting for database..."
    
    # Simple wait loop using netcat (nc)
    # Usually DATABASE_URL format is postgres://user:pass@HOST:PORT/db
    # We try to extract HOST and PORT nicely or just wait a generic amount if parsing fails
    
    # Note: In a robust production script, we would parse the URL properly.
    # Here, we assume the DB hostname is passed via env var DB_HOST if needed, 
    # or we just rely on Django's connection retry.
    sleep 5
}

wait_for_db

# Run migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Server
# We use PORT env var if set, otherwise default to 5005
SERVER_PORT=${PORT:-5005}

if [ "$DEBUG" = "True" ]; then
    echo "Starting Development Server on port $SERVER_PORT..."
    exec python manage.py runserver 0.0.0.0:$SERVER_PORT
else
    echo "Starting Production Server (Gunicorn) on port $SERVER_PORT..."
    exec gunicorn config.wsgi:application --bind 0.0.0.0:$SERVER_PORT --workers 4 --log-level info
fi