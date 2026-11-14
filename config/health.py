"""
Health check endpoints for Kubernetes liveness and readiness probes.
"""
from django.http import JsonResponse  # type: ignore
from django.db import connection  # type: ignore
from django.core.cache import cache  # type: ignore
import logging

logger = logging.getLogger(__name__)


def healthz(request):
    """
    Liveness probe - checks if the application is running.
    Returns 200 if the application is alive, 503 otherwise.
    """
    try:
        return JsonResponse({
            'status': 'healthy',
            'service': 'ecommerce-api'
        }, status=200)
    except Exception as e:
        logger.error(f"Liveness probe failed: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)


def ready(request):
    """
    Readiness probe - checks if the application is ready to serve traffic.
    Verifies database and cache connectivity.
    """
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Check cache connectivity (if Redis is configured)
        try:
            cache.set('health_check', 'ok', 10)
            cache.get('health_check')
        except Exception:
            # Cache is optional, log warning but don't fail
            logger.warning("Cache health check failed, but continuing")
        
        return JsonResponse({
            'status': 'ready',
            'database': 'connected',
            'service': 'ecommerce-api'
        }, status=200)
    except Exception as e:
        logger.error(f"Readiness probe failed: {str(e)}")
        return JsonResponse({
            'status': 'not ready',
            'error': str(e)
        }, status=503)


def startup(request):
    """
    Startup probe - checks if the application has finished starting up.
    Used for applications with long startup times.
    """
    try:
        # Perform basic checks
        from django.apps import apps  # type: ignore
        apps.check_apps_ready()
        
        return JsonResponse({
            'status': 'started',
            'service': 'ecommerce-api'
        }, status=200)
    except Exception as e:
        logger.error(f"Startup probe failed: {str(e)}")
        return JsonResponse({
            'status': 'starting',
            'error': str(e)
        }, status=503)


