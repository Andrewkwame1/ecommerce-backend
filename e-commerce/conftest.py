"""Pytest configuration for Django tests."""
import os
import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
django.setup()


def pytest_collection_modifyitems(items):
    """Auto-mark all TestCase-based tests with django_db marker."""
    for item in items:
        if item.cls and hasattr(item.cls, '_testMethodName'):
            # This is a Django TestCase
            item.add_marker(pytest.mark.django_db(transaction=True))





