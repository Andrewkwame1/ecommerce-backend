from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db.models import Prefetch

from .models import Category, Product, Review, Wishlist
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ReviewSerializer, WishlistSerializer
)
from apps.orders.models import OrderItem
from utils.pagination import StandardPagination


class CategoryListView(generics.ListAPIView):
    """List product categories with optimized queries and caching"""
    
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        # Prevent errors during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Category.objects.none()
        
        # Use cache for category list (expensive hierarchical query)
        cache_key = 'categories_list_root'
        categories = cache.get(cache_key)
        
        if categories is None:
            # Query optimization: only get root categories with select_related
            categories = Category.objects.filter(
                is_active=True, 
                parent__isnull=True
            ).prefetch_related(
                Prefetch('children', queryset=Category.objects.filter(is_active=True))
            )
            # Cache for 1 hour
            cache.set(cache_key, list(categories), 3600)
            return categories
        
        return categories


class ProductListView(generics.ListAPIView):
    """List products with optimized queries, filtering, searching, and pagination"""
    
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']
    pagination_class = StandardPagination
    
    def get_queryset(self):
        # Query optimization: use select_related for foreign keys
        queryset = Product.objects.filter(is_active=True).select_related(
            'category'
        ).prefetch_related(
            'images',  # Prefetch related images to avoid N+1
            Prefetch('reviews', queryset=Review.objects.filter(is_approved=True))
        ).only(
            'id', 'name', 'slug', 'price', 'compare_price', 'quantity',
            'is_featured', 'is_active', 'category_id'
        )
        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    """Get product details with caching and optimized queries"""
    
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        # Use prefetch_related to avoid N+1 queries on related objects
        return Product.objects.filter(is_active=True).select_related(
            'category'
        ).prefetch_related(
            'images',
            'variants',
            Prefetch('reviews', queryset=Review.objects.filter(is_approved=True).select_related('user'))
        )
    
    def retrieve(self, request, *args, **kwargs):
        # Implement caching for product details (for anonymous users)
        slug = kwargs.get('slug')
        cache_key = f'product_detail_{slug}'
        
        if not request.user.is_authenticated:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        data = serializer.data
        
        # Cache for 5 minutes (for anonymous users only)
        if not request.user.is_authenticated:
            cache.set(cache_key, data, 300)
        
        return Response(data)



class ProductReviewListCreateView(generics.ListCreateAPIView):
    """List and create product reviews with optimized queries"""
    
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        # Prevent errors during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        
        product_slug = self.kwargs['slug']
        product = get_object_or_404(Product, slug=product_slug)
        
        # Optimize query: select_related user to avoid N+1
        return Review.objects.filter(
            product=product, 
            is_approved=True
        ).select_related('user').order_by('-created_at')
    
    def perform_create(self, serializer):
        product_slug = self.kwargs['slug']
        product = get_object_or_404(Product, slug=product_slug)
        
        # Check if user has purchased this product (exists() is more efficient than count())
        is_verified = OrderItem.objects.filter(
            order__user=self.request.user,
            product=product
        ).exists()
        
        serializer.save(user=self.request.user, product=product, is_verified_purchase=is_verified)
        
        # Invalidate product detail cache when review is created
        cache_key = f'product_detail_{product_slug}'
        cache.delete(cache_key)


@extend_schema(
    request=None,
    responses=WishlistSerializer
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_wishlist(request, slug):
    """Add/remove product from wishlist with optimized query"""
    
    product = get_object_or_404(Product, slug=slug)
    
    # Use get_or_create for atomic operation (more efficient than try/except)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user, 
        product=product
    )
    
    if not created:
        # Item already existed, so delete it
        wishlist_item.delete()
        return Response({
            'message': 'Product removed from wishlist',
            'in_wishlist': False
        }, status=status.HTTP_200_OK)
    else:
        # Item was just created
        return Response({
            'message': 'Product added to wishlist',
            'in_wishlist': True
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    request=None,
    responses=WishlistSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_wishlist(request):
    """Get user's wishlist with optimized queries and pagination"""
    
    # Optimize: select_related product and its category
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('product', 'product__category').prefetch_related(
        'product__images'
    ).order_by('-created_at')
    
    # Apply pagination
    paginator = StandardPagination()
    paginated_items = paginator.paginate_queryset(wishlist_items, request)
    serializer = WishlistSerializer(paginated_items, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)
