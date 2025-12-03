#!/bin/bash

echo "Starting Railway deployment..."

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput || exit 1

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Load seed data if needed
echo "Loading seed data..."
python manage.py loaddata seed_data.json 2>/dev/null || echo "No seed data to load"

# Start gunicorn
echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 4 \
  --threads 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
