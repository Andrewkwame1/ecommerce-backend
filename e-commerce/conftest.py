"""Pytest configuration for Django tests."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
django.setup()

# pytest-django will automatically use DJANGO_SETTINGS_MODULE

