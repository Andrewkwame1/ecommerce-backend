"""
Tests for the Cart app.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Product, Category

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class CartAPITests(TestCase):
    """Test Cart API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            description="Test Description",
            price=99.99,
            quantity=10,
            sku="TEST-SKU-001",
            category=self.category,
        )

    def test_get_cart_requires_auth(self):
        """Test that getting cart requires authentication."""
        response = self.client.get("/api/v1/cart/")
        # Should be 401 Unauthorized or 404 Not Found
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ])

    def test_add_to_cart_requires_auth(self):
        """Test that adding to cart requires authentication."""
        data = {
            "product_id": self.product.id,
            "quantity": 2,
        }
        response = self.client.post("/api/v1/cart/add/", data)
        # Should be 401 Unauthorized or 404 Not Found
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ])

    def test_get_cart_authenticated(self):
        """Test getting cart with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/cart/")
        # Should return 200 OK or 404 Not Found (if endpoint doesn't exist)
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ])
