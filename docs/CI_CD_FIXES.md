# CI/CD Fixes - Database Migration & Configuration Issues

**Date:** December 5, 2025  
**Issue:** `django.core.exceptions.ImproperlyConfigured: settings.DATABASES is improperly configured`  
**Status:** ✅ FIXED

---

## Problem Summary

The GitHub Actions CI/CD pipeline was failing during the `python manage.py migrate --noinput` step with the error:

```
django.core.exceptions.ImproperlyConfigured: settings.DATABASES is improperly configured. 
Please supply the ENGINE value.
```

### Root Causes

1. **Empty Test Settings:** `config/settings/test.py` was empty - no database configuration
2. **Missing DATABASE_URL:** CI workflow wasn't setting `DATABASE_URL` environment variable
3. **Fragile Database Detection:** `production.py` relied on `dj_database_url` import which could fail silently

---

## Solutions Implemented

### 1. ✅ Created Complete Test Settings (`config/settings/test.py`)

**What was fixed:**
- Added PostgreSQL database configuration for CI environment
- Configured in-memory cache (faster than Redis for tests)
- Set up Celery with eager task execution (synchronous)
- Configured test-specific security settings
- Added email backend for capturing test emails
- Optimized logging to reduce noise in test output

**Key Configuration:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'ecommerce'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 0,  # Don't persist connections in tests
    }
}

# Use simple in-memory cache for tests (faster)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ecommerce-test-cache',
    }
}

# Use eager Celery execution (synchronous)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = 'memory://'
```

---

### 2. ✅ Enhanced Production Database Configuration (`config/settings/production.py`)

**What was improved:**
- Initialize `DATABASES = {}` before conditional checks (prevents undefined variable error)
- Priority-based configuration:
  1. DATABASE_URL environment variable (Render, Heroku, Railway)
  2. Explicit DB_* environment variables (custom deployments)
  3. SQLite fallback (standalone deployments)
- Added manual URL parsing fallback if `dj_database_url` fails to import
- Added `atomic_requests=True` for data integrity
- Better error handling with descriptive comments

**New Logic:**
```python
DATABASES = {}

# Check if DATABASE_URL is provided (Render PostgreSQL addon)
if os.getenv('DATABASE_URL'):
    # Try to use dj-database-url if available
    if dj_database_url:
        DATABASES = {
            'default': dj_database_url.config(
                default=os.getenv('DATABASE_URL'),
                conn_max_age=600,
                atomic_requests=True
            )
        }
    else:
        # Fallback: parse DATABASE_URL manually
        # DATABASE_URL format: postgresql://user:password@host:port/dbname
        import urllib.parse
        db_url = os.getenv('DATABASE_URL')
        if db_url.startswith('postgresql://'):
            parsed = urllib.parse.urlparse(db_url)
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': parsed.path.lstrip('/'),
                    'USER': parsed.username,
                    'PASSWORD': parsed.password,
                    'HOST': parsed.hostname,
                    'PORT': parsed.port or 5432,
                    'ATOMIC_REQUESTS': True,
                    'CONN_MAX_AGE': 600,
                }
            }

# If still no database configured, try explicit env vars
if not DATABASES and os.getenv('DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'ecommerce'),
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'ATOMIC_REQUESTS': True,
            'CONN_MAX_AGE': 600,
        }
    }

# Fallback to SQLite if nothing else is configured
if not DATABASES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
```

---

### 3. ✅ Updated CI Workflow (`.github/workflows/ci.yml`)

**What was added:**
- Set `DATABASE_URL` environment variable in addition to individual DB_* vars
- Ensures migrations can parse the DATABASE_URL in production.py fallback logic
- Provides complete environment setup for migration step

**Changes:**
```yaml
- name: Set up environment variables
  run: |
    # ... existing vars ...
    echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ecommerce" >> $GITHUB_ENV
    # ... rest of vars ...

- name: Run database migrations
  run: python manage.py migrate --noinput
  env:
    DJANGO_SETTINGS_MODULE: config.settings.test
    DATABASE_URL: ${{ env.DATABASE_URL }}
```

---

## Database Configuration Priority (Updated)

### On Render.com (Production)
```
1. DATABASE_URL env var (Render provides automatically)
   ↓
2. dj_database_url.config() parses it
   ↓
3. DATABASES configured ✅
```

### On Other Platforms (Heroku, Railway, etc.)
```
1. DATABASE_URL env var (platform provides)
   ↓
2. dj_database_url.config() parses it
   ↓
3. DATABASES configured ✅
```

### Custom Deployments
```
1. DATABASE_URL env var (if provided)
   ↓
2. Explicit DB_HOST, DB_USER, DB_PASSWORD vars
   ↓
3. DATABASES configured ✅
```

### Local/Standalone
```
1. No DATABASE_URL or DB_* vars
   ↓
2. Falls back to SQLite
   ↓
3. DATABASES uses sqlite3 backend ✅
```

---

## Testing the Fixes Locally

### 1. Test with SQLite (no database required)
```bash
cd e-commerce
python manage.py migrate --noinput
# Should work without any database setup
```

### 2. Test with PostgreSQL (requires running PostgreSQL)
```bash
cd e-commerce

# Set DATABASE_URL
export DATABASE_URL=postgresql://postgres:password@localhost:5432/ecommerce

# Run migrations
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py migrate --noinput
```

### 3. Test CI locally (simulate GitHub Actions)
```bash
cd e-commerce

# Set all environment variables like CI does
export DJANGO_SECRET_KEY=test-secret-key
export DJANGO_SETTINGS_MODULE=config.settings.test
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ecommerce
export DB_NAME=ecommerce
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_HOST=localhost
export DB_PORT=5432

# Run migrations
python manage.py migrate --noinput

# Run tests
pytest --cov=. -v
```

---

## Files Modified

| File | Changes |
|------|---------|
| `config/settings/test.py` | Created complete test settings configuration |
| `config/settings/production.py` | Enhanced database configuration with fallbacks |
| `.github/workflows/ci.yml` | Added DATABASE_URL environment variable |

---

## Deployment Instructions

### For Render.com
1. Render automatically sets `DATABASE_URL` when you add PostgreSQL addon
2. Set Django settings module: `DJANGO_SETTINGS_MODULE=config.settings.production`
3. No additional configuration needed

### For Heroku
1. Add PostgreSQL addon (sets `DATABASE_URL` automatically)
2. Set `DJANGO_SETTINGS_MODULE=config.settings.production`
3. Deploy normally

### For Docker/docker-compose
1. Set `DATABASE_URL` or individual DB_* variables
2. Or leave empty for SQLite fallback
3. Migrations will run automatically

---

## Benefits of These Changes

✅ **Robustness:** Multiple fallback mechanisms for database configuration  
✅ **Flexibility:** Works with different deployment platforms (Render, Heroku, Railway, etc.)  
✅ **CI/CD Ready:** GitHub Actions can run migrations without manual setup  
✅ **Local Development:** Works with or without a database  
✅ **Production Safe:** Never uses hardcoded credentials, always from environment  
✅ **Migration Ready:** Supports both platform-provided DATABASE_URL and explicit DB_* vars  

---

## Troubleshooting

### If migrations still fail:

1. **Check environment variables are set:**
   ```bash
   echo $DATABASE_URL
   echo $DJANGO_SETTINGS_MODULE
   ```

2. **Verify database connection:**
   ```bash
   python manage.py shell
   from django.db import connection
   connection.ensure_connection()  # Should not raise error
   ```

3. **Check settings module exists:**
   ```bash
   python manage.py --settings=config.settings.test help
   ```

4. **Check for syntax errors in settings:**
   ```bash
   python -c "import config.settings.production; print('OK')"
   python -c "import config.settings.test; print('OK')"
   ```

---

## Summary

The CI/CD pipeline will now successfully:
1. ✅ Run database migrations in GitHub Actions
2. ✅ Configure the correct database based on environment
3. ✅ Fall back gracefully if DATABASE_URL is not provided
4. ✅ Support multiple deployment platforms
5. ✅ Work with local development (SQLite fallback)

**Status:** Ready for deployment ✅

