from celery import shared_task
from django.core.cache import cache
from django.db import models
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_low_stock_products():
    """Check for products with low stock and create notifications"""
    try:
        from apps.products.models import Product
        from apps.notifications.models import Notification
        from apps.users.models import User
        
        # Get all low stock products
        low_stock_products = Product.objects.filter(
            track_inventory=True,
            quantity__lte=models.F('low_stock_threshold'),
            quantity__gt=0,
            is_active=True
        )
        
        # Get admin users
        admins = User.objects.filter(is_staff=True)
        
        for product in low_stock_products:
            # Create notification for each admin
            for admin in admins:
                Notification.objects.get_or_create(
                    user=admin,
                    notification_type='in_app',
                    defaults={
                        'subject': f'Low Stock Alert: {product.name}',
                        'message': f'{product.name} has only {product.quantity} units left in stock.',
                        'status': 'pending',
                        'data': {'product_id': str(product.id)}
                    }
                )
        
        logger.info(f"Low stock check completed. Found {low_stock_products.count()} products")
        return f"Checked {low_stock_products.count()} low stock products"
        
    except Exception as e:
        logger.error(f"Error checking low stock products: {str(e)}")
        raise


@shared_task
def cleanup_expired_tokens():
    """Remove expired email verification and password reset tokens"""
    try:
        from apps.users.models import EmailVerificationToken, PasswordResetToken
        from django.utils import timezone
        
        # Delete expired verification tokens
        EmailVerificationToken.objects.filter(expires_at__lt=timezone.now()).delete()
        
        # Delete expired or used password reset tokens
        PasswordResetToken.objects.filter(
            models.Q(expires_at__lt=timezone.now()) | models.Q(is_used=True)
        ).delete()
        
        logger.info("Token cleanup completed")
        return "Expired tokens cleaned up"
        
    except Exception as e:
        logger.error(f"Error cleaning up tokens: {str(e)}")
        raise


@shared_task
def invalidate_product_cache():
    """Invalidate product cache"""
    try:
        cache.delete('products_list')
        logger.info("Product cache invalidated")
        return "Product cache cleared"
        
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}")
        raise
