# apps/orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderListCreateView.as_view(), name='order_list'),
    path('<uuid:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<uuid:pk>/cancel/', views.CancelOrderView.as_view(), name='cancel_order'),
]
