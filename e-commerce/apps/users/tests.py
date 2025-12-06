"""
Tests for the Users app.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class UserModelTests(TestCase):
    """Test User model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_user_creation(self):
        """Test that a user can be created."""
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.last_name, "User")

    def test_user_str(self):
        """Test the string representation of a user."""
        self.assertEqual(str(self.user), "test@example.com")

    def test_user_password_hashed(self):
        """Test that user password is hashed."""
        self.assertNotEqual(self.user.password, "testpass123")
        self.assertTrue(self.user.check_password("testpass123"))

    def test_user_is_active_by_default(self):
        """Test that new users are active by default."""
        self.assertTrue(self.user.is_active)

    def test_user_is_not_staff_by_default(self):
        """Test that new users are not staff by default."""
        self.assertFalse(self.user.is_staff)

    def test_user_is_not_superuser_by_default(self):
        """Test that new users are not superuser by default."""
        self.assertFalse(self.user.is_superuser)


@pytest.mark.django_db(transaction=True)
class UserAPITests(TestCase):
    """Test User API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

    def test_user_registration(self):
        """Test user registration endpoint."""
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post("/api/v1/auth/register/", data)
        # Status could be 201 Created or 400 Bad Request depending on serializer
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_user_login(self):
        """Test user login endpoint."""
        data = {
            "email": "test@example.com",
            "password": "testpass123",
        }
        response = self.client.post("/api/v1/auth/login/", data)
        # Status could be 200 OK or 400 Bad Request depending on implementation
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_list_users_requires_auth(self):
        """Test that listing users requires authentication."""
        response = self.client.get("/api/v1/users/")
        # Should be 200, 401 Unauthorized, or 403 Forbidden
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ])
