from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_pending_notifications():
    """Send all pending notifications"""
    try:
        from apps.notifications.models import Notification
        from django.utils import timezone
        
        pending_notifications = Notification.objects.filter(status='pending', notification_type='email')
        
        for notification in pending_notifications:
            try:
                send_mail(
                    subject=notification.subject,
                    message=notification.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[notification.user.email],
                    fail_silently=False,
                )
                
                # Mark as sent
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()
                
                logger.info(f"Notification sent to {notification.user.email}")
                
            except Exception as e:
                # Mark as failed
                notification.status = 'failed'
                notification.save()
                logger.error(f"Failed to send notification: {str(e)}")
        
        return f"Processed {pending_notifications.count()} pending notifications"
        
    except Exception as e:
        logger.error(f"Error sending pending notifications: {str(e)}")
        raise


@shared_task
def create_notification(user_id, notification_type, subject, message, data=None):
    """Create and optionally send a notification"""
    try:
        from apps.notifications.models import Notification
        from apps.users.models import User
        
        user = User.objects.get(id=user_id)
        
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            subject=subject,
            message=message,
            status='pending',
            data=data or {}
        )
        
        logger.info(f"Notification created for {user.email}")
        return f"Notification created for {user.email}"
        
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise
