#!/bin/bash
set -e

echo "Starting entrypoint script..."

# Run migrations in the background (don't block startup)
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.production" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput || echo "Migration warning: could not run migrations"
fi

# Start the application
echo "Starting Gunicorn..."
exec "$@"
