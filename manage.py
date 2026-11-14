#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Respect an explicit DJANGO_SETTINGS_MODULE (Dockerfile / hosting platform),
    # otherwise auto-detect: production on a cloud platform, development locally.
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        is_production = any(
            os.getenv(var)
            for var in ('DATABASE_URL', 'RENDER', 'VERCEL', 'VERCEL_ENV', 'AWS_LAMBDA_FUNCTION_NAME')
        )
        settings_module = 'config.settings.production' if is_production else 'config.settings.development'
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
