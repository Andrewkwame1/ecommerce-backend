FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Set work directory - point to e-commerce directory
WORKDIR /app

# Copy requirements from e-commerce directory
COPY e-commerce/requirements.txt .
RUN pip install --upgrade pip setuptools wheel --root-user-action=ignore && \
  pip install -r requirements.txt --root-user-action=ignore

# Copy the e-commerce project to /app
COPY e-commerce/ .

# Create necessary directories
RUN mkdir -p logs media staticfiles static

# Collect static files
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# Expose port
EXPOSE 8000

# Set production Django settings
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Default command - run migrations and start gunicorn
# Using JSON array format to ensure proper signal handling (SIGTERM)
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4 --threads 2 --timeout 120"]
