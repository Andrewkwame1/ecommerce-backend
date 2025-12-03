# Railway Deployment Guide

## Problem: ModuleNotFoundError: No module named 'config'

This occurs when the Docker/application working directory isn't properly configured for Python to find the Django project's `config` module.

## Solution

### Step 1: Fix Project Structure for Railway

Your current structure:
```
alx-project-nexus/
├── e-commerce/          (this is the Django project root)
│   ├── config/
│   ├── apps/
│   ├── manage.py
│   └── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

For Railway to work, you need a flatter structure. Move the Django project contents to the root:

```bash
cd /path/to/alx-project-nexus

# Backup first
cp -r e-commerce e-commerce-backup

# Copy Django files to root
cp -r e-commerce/* .
cp -r e-commerce/.gitignore .

# Keep e-commerce folder for reference but it's no longer needed
# You can delete it later: rm -rf e-commerce
```

### Step 2: Update Dockerfile for Root Level Deployment

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

COPY . .

RUN mkdir -p logs media staticfiles && \
    python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "120"]
```

### Step 3: Create `railway.json` (Railway Configuration)

```json
{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "startCommand": "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120"
  }
}
```

### Step 4: Set Environment Variables on Railway

Go to your Railway project dashboard and set these variables:

```
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=your-long-random-secret-key
ALLOWED_HOSTS=yourdomain.railway.app
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://user:password@host:6379/0
CELERY_BROKER_URL=amqp://user:password@host:5672//
```

### Step 5: Create `.env.production` (for local testing)

```env
DEBUG=False
SECRET_KEY=your-django-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.railway.app

# Database
POSTGRES_DB=ecommerce
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
DB_HOST=postgres.railway.internal
DB_PORT=5432

# Redis
REDIS_URL=redis://:password@redis.railway.internal:6379/0

# Celery
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq.railway.internal:5672//
CELERY_RESULT_BACKEND=redis://:password@redis.railway.internal:6379/1

# Stripe
STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
```

### Step 6: Update `config/settings/production.py`

```python
import os
from pathlib import Path
from .base import *

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'ecommerce'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Redis/Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/1')

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

### Step 7: Migration Script for Railway

Create `scripts/railway_startup.sh`:

```bash
#!/bin/bash

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'changeme')
END

# Start gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120
```

Make it executable:
```bash
chmod +x scripts/railway_startup.sh
```

Update your `railway.json`:
```json
{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "startCommand": "bash scripts/railway_startup.sh"
  }
}
```

## Quick Deployment Checklist

- [ ] Move Django files from `e-commerce/` to project root
- [ ] Update Dockerfile to work from root level
- [ ] Create `railway.json` with correct configuration
- [ ] Set all environment variables in Railway dashboard
- [ ] Update `config/settings/production.py` with environment variables
- [ ] Create/update startup script
- [ ] Test locally: `docker build -t test . && docker run -p 8000:8000 test`
- [ ] Push to GitHub
- [ ] Connect to Railway via GitHub
- [ ] Monitor logs in Railway dashboard

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'config'`
- Ensure PYTHONPATH is set correctly
- Check Dockerfile WORKDIR
- Verify gunicorn command points to correct module path

### Error: `No such file or directory: '/app/manage.py'`
- Django files not in correct location
- Dockerfile COPY commands don't match actual file structure

### Error: Database connection refused
- Check DATABASE_URL environment variable
- Ensure database service is connected in Railway
- Verify credentials are correct

### Error: `collectstatic` fails
- Make sure STATIC_ROOT is writable
- Check file permissions on app directory
- Remove `--noinput` flag for debugging

## Monitor Deployment

View logs in Railway:
```
railway logs -f
```

SSH into container:
```
railway shell
```

Check running processes:
```
railway run ps aux
```
