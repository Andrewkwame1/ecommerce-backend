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
RUN pip install --upgrade pip setuptools wheel && \
  pip install -r requirements.txt

# Copy the e-commerce project to /app
COPY e-commerce/ .

# Create necessary directories
RUN mkdir -p logs media staticfiles && \
  chmod +x /app/scripts/* 2>/dev/null || true

# Collect static files (migrations happen at startup via railway_startup.sh)
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# Expose port
EXPOSE 8000

# Default command - use startup script for Railway
CMD ["bash", "scripts/railway_startup.sh"]
