"""Pytest configuration for Django tests."""
import os
import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
django.setup()

# Auto-use django_db marker for all tests
@pytest.fixture(scope="session")
def django_db_setup():
    """Setup Django database for tests."""
    pass


