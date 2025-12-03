"""
WSGI config for e-commerce project.
"""
import os
from django.core.wsgi import get_wsgi_application

# Use production settings if DJANGO_SETTINGS_MODULE is already set (by Docker/Platform)
# Otherwise, auto-detect based on environment
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    # Default to production for cloud deployments, development for local
    settings = 'config.settings.production' if os.getenv('RENDER') or os.getenv('DATABASE_URL') else 'config.settings.development'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)

application = get_wsgi_application()
