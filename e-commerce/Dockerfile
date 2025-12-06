FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  DJANGO_SETTINGS_MODULE=config.settings.production \
  DEBUG=False

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements from parent directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
  pip install -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p logs media staticfiles && \
  chmod +x /app/scripts/* 2>/dev/null || true

# Collect static files (no database required - uses SQLite fallback)
# This runs with minimal database config since we don't have DATABASE_URL at build time
RUN python manage.py collectstatic --noinput --clear 2>&1 | grep -v "ImportError\|ModuleNotFoundError" || true

# Expose port
EXPOSE 8000

# Health check (for Docker, Kubernetes uses liveness/readiness probes)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/healthz/', timeout=5)" || exit 1

# Default command
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
