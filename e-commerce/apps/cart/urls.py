# apps/cart/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartDetailView.as_view(), name='cart_detail'),
    path('items/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('items/<uuid:pk>/', views.CartItemUpdateDeleteView.as_view(), name='cart_item_update'),
    path('clear/', views.ClearCartView.as_view(), name='clear_cart'),
]
