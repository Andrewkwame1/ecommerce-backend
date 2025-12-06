"""
Test settings for Django e-commerce project
Used for running tests in CI/CD and local test environments
"""

import os
from datetime import timedelta
from .base import *  # noqa: F401, F403

# Override settings for testing
DEBUG = True

# Use a test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # In-memory database for speed
        'ATOMIC_REQUESTS': True,
    }
}

# Use simple in-memory cache for tests (faster)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ecommerce-test-cache',
        'TIMEOUT': 300,
    }
}

# Use eager task execution for Celery (synchronous)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+locmem://'

# Session configuration for tests
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Security settings - relaxed for testing
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1']
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email backend for tests (capture emails in memory)
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Frontend URL for test email verification links
FRONTEND_URL = 'http://localhost:3000'

# Logging - reduced output for cleaner test results
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
        'level': 'WARNING',  # Only show warnings and errors
    },
}

# Use MD5 password hasher for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use simple JWT backend for tests
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# Shorter token lifetimes for tests
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Disable migrations for faster test runs (optional)
# Uncomment to use test fixtures instead of migrations
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()
