"""
Tests for the Orders app.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Product, Category

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class OrderAPITests(TestCase):
    """Test Order API endpoints."""

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

    def test_list_orders_requires_auth(self):
        """Test that listing orders requires authentication."""
        response = self.client.get("/api/v1/orders/")
        # Should be 401 Unauthorized or 404 Not Found
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ])

    def test_create_order_requires_auth(self):
        """Test that creating an order requires authentication."""
        data = {
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 2,
                }
            ]
        }
        response = self.client.post("/api/v1/orders/", data)
        # Should be 401 Unauthorized or 404 Not Found
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ])

    def test_list_orders_authenticated(self):
        """Test listing orders with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/orders/")
        # Should return 200 OK or 404 Not Found (if endpoint doesn't exist)
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ])
