"""
Production settings for Django e-commerce project
Used when deployed on Railway, AWS, or other production servers
"""

import os
import sys
import logging
import urllib.parse
from datetime import timedelta

from .base import *  # noqa: F401, F403
from .base import BASE_DIR

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# Override base settings for production
DEBUG = False  # ALWAYS False in production - never trust environment variables
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'change-me-in-production')

# Parse ALLOWED_HOSTS from environment or use wildcard for cloud deployments
# CRITICAL: Render passes ALLOWED_HOSTS env var but we need to override it for production
# We want wildcard to accept any host on Render's reverse proxy
# The reverse proxy handles the actual security
ALLOWED_HOSTS_ENV = os.getenv('ALLOWED_HOSTS', '')
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME', '')

# Production ALLOWED_HOSTS configuration:
# Option 1: If RENDER_EXTERNAL_HOSTNAME is set (Render platform), use it
# Option 2: If custom ALLOWED_HOSTS env var is set, use it
# Option 3: Fallback to wildcard for unknown deployments (Reverse proxy validates)
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, 'localhost', '127.0.0.1']
elif ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(',') if host.strip()]
else:
    # Wildcard is safe here because reverse proxy (Render/nginx) validates actual requests
    ALLOWED_HOSTS = ['*']

# Debug logging for ALLOWED_HOSTS configuration
debug_mode = '--debug' in sys.argv or '--pdb' in sys.argv
logger_msg = (
    f"[PRODUCTION CONFIG] "
    f"DEBUG={DEBUG}, "
    f"ALLOWED_HOSTS={ALLOWED_HOSTS}, "
    f"ALLOWED_HOSTS_ENV='{ALLOWED_HOSTS_ENV}', "
    f"RENDER_EXTERNAL_HOSTNAME='{RENDER_EXTERNAL_HOSTNAME}'"
)
if debug_mode or os.getenv('DJANGO_LOG_LEVEL') == 'DEBUG':
    print(logger_msg, file=sys.stderr)
else:
    # Use syslog for production
    logging.info(logger_msg)

# ===== DATABASE CONFIGURATION =====
# Priority order:
# 1. DATABASE_URL (Render, Heroku, Railway PostgreSQL addon)
# 2. Explicit DB_* environment variables
# 3. Fallback to SQLite

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
        # Fallback: parse DATABASE_URL manually if dj_database_url not available
        # DATABASE_URL format: postgresql://user:password@host:port/dbname
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
                    'OPTIONS': {
                        'connect_timeout': 10,
                    }
                }
            }

# If still no database configured, try explicit env vars
if not DATABASES and os.getenv('DB_HOST') and os.getenv('DB_HOST') != 'localhost':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'ecommerce'),
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'ATOMIC_REQUESTS': True,
            'CONN_MAX_AGE': 600,
            'OPTIONS': {
                'connect_timeout': 10,
            }
        }
    }

# If still no database configured, fallback to SQLite
if not DATABASES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# ===== REDIS/CACHE CONFIGURATION =====
# Use Redis for caching and sessions in production if available
# Fall back to local memory cache if Redis is not available
REDIS_URL = os.getenv('REDIS_URL', '')

if REDIS_URL:
    # If Redis is configured, use it
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            },
            'KEY_PREFIX': 'ecommerce',
            'TIMEOUT': 3600,  # 1 hour default
        }
    }
else:
    # Fall back to in-memory cache for Render without Redis add-on
    # This is suitable for single-instance deployments
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'ecommerce-cache',
            'TIMEOUT': 3600,  # 1 hour default
        }
    }

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ===== SECURITY SETTINGS =====
# HTTPS/SSL REDIRECT CONFIGURATION
# 
# IMPORTANT: SECURE_SSL_REDIRECT is DISABLED (False) because:
#   1. Render's reverse proxy already handles HTTPS
#   2. All traffic to Django is already https via the reverse proxy
#   3. The X-Forwarded-Proto header tells us if the original request was https
#   4. Enabling SECURE_SSL_REDIRECT would cause redirect loops on Render
#
# Instead, we:
#   - Trust the X-Forwarded-Proto header from the reverse proxy
#   - Set SECURE_PROXY_SSL_HEADER to let Django know about HTTPS
#   - Set cookie security flags to ensure secure cookie transmission
#
# This is the correct approach for reverse proxy deployments (Render, Heroku, AWS ALB, etc.)

# DO NOT redirect to HTTPS - reverse proxy handles it
SECURE_SSL_REDIRECT = False

# Trust X-Forwarded-Proto header from Render's reverse proxy
# This tells Django that the original request was over HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Security cookies - ALWAYS use secure flag in production
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CSRF trusted origins - which hosts can make cross-origin requests
# Dynamically build from ALLOWED_HOSTS to support multiple deployments
CSRF_TRUSTED_ORIGINS = []

# Add all ALLOWED_HOSTS with https:// prefix
for host in ALLOWED_HOSTS:
    if host != '*':
        # Add both specific domain and wildcard subdomain versions
        CSRF_TRUSTED_ORIGINS.append(f'https://{host}')
        if not host.startswith('*.'):
            CSRF_TRUSTED_ORIGINS.append(f'https://*.{host}')

# Add common deployment platform patterns
CSRF_TRUSTED_ORIGINS.extend([
    'https://ecommerce-backend-1-v60x.onrender.com',
    'https://*.onrender.com',  # Any Render subdomain
    'https://*.herokuapp.com',  # Heroku subdomains
    'https://*.railway.app',    # Railway subdomains
    'http://localhost:3000',    # Local frontend development
    'http://localhost:8000',    # Local API development
    'http://127.0.0.1:3000',    # Local frontend (IP)
    'http://127.0.0.1:8000',    # Local API (IP)
])

# Remove duplicates while preserving order
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))

# Additional security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS (HTTP Strict Transport Security) - Optional for maximum security
# Warning: Only enable after testing HTTPS thoroughly
# Once enabled in browser, it caches for SECURE_HSTS_SECONDS (1 year default)
SECURE_HSTS_SECONDS = 31536000  # 1 year - ONLY enable if HTTPS is permanent
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ===== STATIC & MEDIA FILES =====
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Use WhiteNoise for efficient static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ===== CELERY CONFIGURATION =====
# Use environment variables if available, but provide safe defaults
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'memory://')
# Use cache+locmem as result backend fallback for Render
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'cache+locmem://')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
# Disable celery in production if no broker is configured
CELERY_TASK_ALWAYS_EAGER = True if CELERY_BROKER_URL == 'memory://' else False

# ===== LOGGING =====
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)

# ===== EMAIL CONFIGURATION =====
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@ecommerce.com')

# ===== STRIPE CONFIGURATION =====
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')

# ===== CORS CONFIGURATION =====
# Parse CORS origins from environment variable
CORS_ALLOWED_ORIGINS_STR = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000'
)
CORS_ALLOWED_ORIGINS = [
    origin.strip() 
    for origin in CORS_ALLOWED_ORIGINS_STR.split(',') 
    if origin.strip()
]

# Add common patterns for different environments
if RENDER_EXTERNAL_HOSTNAME:
    CORS_ALLOWED_ORIGINS.extend([
        f'https://{RENDER_EXTERNAL_HOSTNAME}',
        'https://*.onrender.com',
    ])

# CORS settings for API endpoints
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_EXPOSE_HEADERS = [
    'content-length',
    'x-json-response',
]
CORS_MAX_AGE = 86400  # 24 hours

# ===== JWT CONFIGURATION =====

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JTI_CLAIM': 'jti',
    'TOKEN_TYPE_CLAIM': 'token_type',

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_BLACKLIST_CLASSES': ('rest_framework_simplejwt.token_blacklist.models.OutstandingToken', 'rest_framework_simplejwt.token_blacklist.models.BlacklistedToken',),
}

# ===== REST FRAMEWORK CONFIGURATION =====
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}

# ===== ADMINS & MANAGERS =====
ADMINS = [
    ('Admin', os.getenv('ADMIN_EMAIL', 'admin@ecommerce.com')),
]
MANAGERS = ADMINS
