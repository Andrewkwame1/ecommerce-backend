from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductVariant, Review, Wishlist


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(method_name='get_children')
    product_count = serializers.SerializerMethodField(method_name='get_product_count')
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent', 'children', 'product_count']
    
    def get_children(self, obj) -> list:
        """Get active child categories."""
        if obj.children.filter(is_active=True).exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []
    
    def get_product_count(self, obj) -> int:
        """Count active products in this category."""
        return obj.products.filter(is_active=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']


class ProductVariantSerializer(serializers.ModelSerializer):
    effective_price = serializers.SerializerMethodField(method_name='get_effective_price')
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'price', 'effective_price', 'quantity', 'attributes', 'is_active']
    
    def get_effective_price(self, obj) -> str:
        """Get effective price of variant."""
        return str(obj.effective_price)


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(method_name='get_user_name')
    
    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'title', 'comment', 'is_verified_purchase', 'created_at']
        read_only_fields = ['user_name', 'is_verified_purchase', 'created_at']
    
    def get_user_name(self, obj) -> str:
        """Get user's display name."""
        return obj.user.get_full_name() or obj.user.email.split('@')[0]


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list (lighter)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField(method_name='get_primary_image')
    discount_percentage = serializers.SerializerMethodField(method_name='get_discount_percentage')
    average_rating = serializers.SerializerMethodField(method_name='get_average_rating')
    review_count = serializers.SerializerMethodField(method_name='get_review_count')
    is_in_stock = serializers.SerializerMethodField(method_name='get_is_in_stock')
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'compare_price', 'discount_percentage',
            'category_name', 'primary_image', 'is_in_stock', 'average_rating',
            'review_count', 'is_featured'
        ]
    
    def get_primary_image(self, obj) -> str | None:
        """Get primary product image URL."""
        image = obj.images.filter(is_primary=True).first()
        if image and self.context.get('request'):
            return self.context['request'].build_absolute_uri(image.image.url)
        return None
    
    def get_discount_percentage(self, obj) -> int:
        """Calculate discount percentage."""
        return obj.discount_percentage
    
    def get_average_rating(self, obj) -> float:
        """Get average rating of product."""
        return obj.average_rating
    
    def get_review_count(self, obj) -> int:
        """Count approved reviews."""
        return obj.reviews.filter(is_approved=True).count()
    
    def get_is_in_stock(self, obj) -> bool:
        """Check if product is in stock."""
        return obj.is_in_stock


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail (complete)"""
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    discount_percentage = serializers.SerializerMethodField(method_name='get_discount_percentage')
    average_rating = serializers.SerializerMethodField(method_name='get_average_rating')
    is_in_stock = serializers.SerializerMethodField(method_name='get_is_in_stock')
    is_low_stock = serializers.SerializerMethodField(method_name='get_is_low_stock')
    is_in_wishlist = serializers.SerializerMethodField(method_name='get_is_in_wishlist')
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'price', 'compare_price',
            'discount_percentage', 'sku', 'quantity', 'is_in_stock', 'is_low_stock',
            'weight', 'dimensions', 'images', 'variants', 'reviews', 'average_rating',
            'is_featured', 'meta_title', 'meta_description', 'is_in_wishlist',
            'created_at', 'updated_at'
        ]
    
    def get_discount_percentage(self, obj) -> int:
        """Calculate discount percentage."""
        return obj.discount_percentage
    
    def get_average_rating(self, obj) -> float:
        """Get average product rating."""
        return obj.average_rating
    
    def get_is_in_stock(self, obj) -> bool:
        """Check if product is in stock."""
        return obj.is_in_stock
    
    def get_is_low_stock(self, obj) -> bool:
        """Check if product is low on stock."""
        return obj.is_low_stock
    
    def get_is_in_wishlist(self, obj) -> bool:
        """Check if product is in user's wishlist."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, product=obj).exists()
        return False


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
    
    def get_product_image(self, obj) -> str | None:
        primary_image = obj.product.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image.url
        return None
