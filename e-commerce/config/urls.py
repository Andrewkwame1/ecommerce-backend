 # config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .health import healthz, ready, startup

# Simple root view
@csrf_exempt
def root_view(request):
    return JsonResponse({
        'message': 'E-Commerce API is running',
        'docs_url': '/api/docs/',
        'api_v1': '/api/v1/'
    })

urlpatterns = [
    # Health check endpoints (these should be accessed first and don't need authentication)
    path('healthz/', healthz, name='healthz'),
    path('ready/', ready, name='ready'),
    path('startup/', startup, name='startup'),
    
    # Root path - simple message instead of redirect
    path('', root_view, name='root'),
    
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API Routes
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/cart/', include('apps.cart.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
