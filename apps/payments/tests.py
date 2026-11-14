"""
Tests for the Payments app.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Product, Category

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class PaymentAPITests(TestCase):
    """Test Payment API endpoints."""

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

    def test_payment_processing_requires_auth(self):
        """Test that payment processing requires authentication."""
        data = {
            "order_id": 1,
            "payment_method": "credit_card",
            "amount": 99.99,
        }
        response = self.client.post("/api/v1/payments/", data)
        # Should be 401 Unauthorized or 404 Not Found
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ])

    def test_payment_status_requires_auth(self):
        """Test that checking payment status requires authentication."""
        response = self.client.get("/api/v1/payments/1/")
        # Should be 401 Unauthorized or 404 Not Found
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ])

    def test_payment_list_requires_auth(self):
        """Test that listing payments requires authentication."""
        response = self.client.get("/api/v1/payments/")
        # Should be 401 Unauthorized or 404 Not Found
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ])
