from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_order_confirmation(self, order_id):
    """Send order confirmation email"""
    try:
        from apps.orders.models import Order
        
        order = Order.objects.get(id=order_id)
        
        subject = f'Order Confirmation - {order.order_number}'
        html_message = render_to_string('emails/order_confirmation.html', {
            'order': order,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Order confirmation email sent for {order.order_number}")
        return f"Confirmation email sent for {order.order_number}"
        
    except Exception as e:
        logger.error(f"Failed to send order confirmation email: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_order_shipped(self, order_id):
    """Send order shipped notification"""
    try:
        from apps.orders.models import Order
        
        order = Order.objects.get(id=order_id)
        
        subject = f'Your Order Has Been Shipped - {order.order_number}'
        html_message = render_to_string('emails/order_shipped.html', {
            'order': order,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Order shipped email sent for {order.order_number}")
        return f"Shipped email sent for {order.order_number}"
        
    except Exception as e:
        logger.error(f"Failed to send order shipped email: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_order_delivered(self, order_id):
    """Send order delivered notification"""
    try:
        from apps.orders.models import Order
        
        order = Order.objects.get(id=order_id)
        
        subject = f'Your Order Has Been Delivered - {order.order_number}'
        html_message = render_to_string('emails/order_delivered.html', {
            'order': order,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Order delivered email sent for {order.order_number}")
        return f"Delivered email sent for {order.order_number}"
        
    except Exception as e:
        logger.error(f"Failed to send order delivered email: {str(e)}")
        raise self.retry(exc=e, countdown=60)
