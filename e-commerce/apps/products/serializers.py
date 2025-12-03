from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductVariant, Review, Wishlist


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent', 'children', 'product_count']
    
    def get_children(self, obj):
        if obj.children.filter(is_active=True).exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']


class ProductVariantSerializer(serializers.ModelSerializer):
    effective_price = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'price', 'effective_price', 'quantity', 'attributes', 'is_active']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'title', 'comment', 'is_verified_purchase', 'created_at']
        read_only_fields = ['user_name', 'is_verified_purchase', 'created_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email.split('@')[0]


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list (lighter)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    discount_percentage = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'compare_price', 'discount_percentage',
            'category_name', 'primary_image', 'is_in_stock', 'average_rating',
            'review_count', 'is_featured'
        ]
    
    def get_primary_image(self, obj):
        image = obj.images.filter(is_primary=True).first()
        if image:
            return self.context['request'].build_absolute_uri(image.image.url)
        return None
    
    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail (complete)"""
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    discount_percentage = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    is_in_wishlist = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'price', 'compare_price',
            'discount_percentage', 'sku', 'quantity', 'is_in_stock', 'is_low_stock',
            'weight', 'dimensions', 'images', 'variants', 'reviews', 'average_rating',
            'is_featured', 'meta_title', 'meta_description', 'is_in_wishlist',
            'created_at', 'updated_at'
        ]
    
    def get_is_in_wishlist(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, product=obj).exists()
        return False


# apps/products/views.py
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.db.models import Q, Avg

from .models import Category, Product, Review, Wishlist
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ReviewSerializer
)
from .filters import ProductFilter


class CategoryListView(generics.ListAPIView):
    """List all active categories"""
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True, parent=None)  # Only root categories
    
    def list(self, request, *args, **kwargs):
        # Cache categories for 1 hour
        cache_key = 'categories_list'
        categories = cache.get(cache_key)
        
        if not categories:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            categories = serializer.data
            cache.set(cache_key, categories, 3600)
        
        return Response(categories)


class ProductListView(generics.ListAPIView):
    """List products with filtering, search, and sorting"""
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Filter by category slug if provided
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter featured products
        is_featured = self.request.query_params.get('featured')
        if is_featured:
            queryset = queryset.filter(is_featured=True)
        
        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    """Get product details by slug"""
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category').prefetch_related(
            'images', 'variants', 'reviews__user'
        )
    
    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        cache_key = f'product_detail_{slug}'
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data and not request.user.is_authenticated:
            # Return cached data for anonymous users
            return Response(cached_data)
        
        # Get fresh data
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Cache for 5 minutes
        if not request.user.is_authenticated:
            cache.set(cache_key, data, 300)
        
        return Response(data)


class ProductReviewListCreateView(generics.ListCreateAPIView):
    """List and create product reviews"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return Review.objects.filter(
            product__slug=slug,
            is_approved=True
        ).select_related('user')
    
    def perform_create(self, serializer):
        product = Product.objects.get(slug=self.kwargs.get('slug'))
        serializer.save(user=self.request.user, product=product)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_wishlist(request, slug):
    """Add or remove product from wishlist"""
    try:
        product = Product.objects.get(slug=slug, is_active=True)
        wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
        
        if wishlist_item:
            wishlist_item.delete()
            return Response({
                'message': 'Product removed from wishlist',
                'in_wishlist': False
            })
        else:
            Wishlist.objects.create(user=request.user, product=product)
            return Response({
                'message': 'Product added to wishlist',
                'in_wishlist': True
            }, status=status.HTTP_201_CREATED)
    
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_wishlist(request):
    """Get user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    products = [item.product for item in wishlist_items]
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)


# apps/products/filters.py
import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """Filter for products"""
    
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    
    class Meta:
        model = Product
        fields = ['category', 'is_featured']
    
    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(quantity__gt=0)
        return queryset


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlist items"""
    product_id = serializers.CharField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'product_id', 'product_name', 'product_image', 'product_price', 'created_at']
        read_only_fields = ['created_at']
    
    def get_product_image(self, obj):
        primary_image = obj.product.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image.url
        return None
