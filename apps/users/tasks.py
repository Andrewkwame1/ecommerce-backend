# apps/users/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_verification_email(self, user_id, token):
    """Send email verification link to user"""
    try:
        from .models import User
        
        user = User.objects.get(id=user_id)
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
        
        subject = 'Verify Your Email Address'
        html_message = render_to_string('emails/verify_email.html', {
            'user': user,
            'verification_url': verification_url,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {user.email}")
        return f"Email sent to {user.email}"
        
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_id, token):
    """Send password reset link to user"""
    try:
        from .models import User
        
        user = User.objects.get(id=user_id)
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
        
        subject = 'Reset Your Password'
        html_message = render_to_string('emails/reset_password.html', {
            'user': user,
            'reset_url': reset_url,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent to {user.email}")
        return f"Email sent to {user.email}"
        
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_id):
    """Send welcome email after verification"""
    try:
        from .models import User
        
        user = User.objects.get(id=user_id)
        
        subject = 'Welcome to Our E-commerce Store!'
        html_message = render_to_string('emails/welcome.html', {
            'user': user,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        return f"Welcome email sent to {user.email}"
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")
        raise self.retry(exc=e, countdown=60)