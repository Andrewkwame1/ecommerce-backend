from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.models import Product, ProductVariant


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items"""
    
    product = serializers.SerializerMethodField()
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )
    variant = serializers.SerializerMethodField()
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        write_only=True,
        source='variant',
        required=False,
        allow_null=True
    )
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'variant', 'variant_id',
            'quantity', 'price', 'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'price', 'total_price', 'created_at', 'updated_at']
    
    def get_product(self, obj):
        from apps.products.serializers import ProductListSerializer
        return ProductListSerializer(obj.product).data
    
    def get_variant(self, obj):
        if obj.variant:
            from apps.products.serializers import ProductVariantSerializer
            return ProductVariantSerializer(obj.variant).data
        return None


class CartSerializer(serializers.ModelSerializer):
    """Serializer for cart"""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
