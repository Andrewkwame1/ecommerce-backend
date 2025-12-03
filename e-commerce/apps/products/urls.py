# apps/products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<slug:slug>/reviews/', views.ProductReviewListCreateView.as_view(), name='product_reviews'),
    path('<slug:slug>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/me/', views.user_wishlist, name='user_wishlist'),
]
