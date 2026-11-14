from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.models import Product, ProductVariant


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items"""
    
    product = serializers.SerializerMethodField(method_name='get_product')
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )
    variant = serializers.SerializerMethodField(method_name='get_variant')
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        write_only=True,
        source='variant',
        required=False,
        allow_null=True
    )
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'variant', 'variant_id',
            'quantity', 'price', 'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'price', 'total_price', 'created_at', 'updated_at']
    
    def get_product(self, obj) -> dict:
        """Get product details for cart item."""
        from apps.products.serializers import ProductListSerializer
        return ProductListSerializer(obj.product).data
    
    def get_variant(self, obj) -> dict | None:
        """Get variant details for cart item."""
        if obj.variant:
            from apps.products.serializers import ProductVariantSerializer
            return ProductVariantSerializer(obj.variant).data
        return None
    
    def get_total_price(self, obj) -> str:
        """Calculate total price for cart item."""
        return str(obj.total_price)


class CartSerializer(serializers.ModelSerializer):
    """Serializer for cart"""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField(method_name='get_total_items')
    subtotal = serializers.SerializerMethodField(method_name='get_subtotal')
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_items(self, obj) -> int:
        """Calculate total number of items in cart."""
        return obj.total_items
    
    def get_subtotal(self, obj) -> str:
        """Calculate subtotal of all items in cart."""
        return str(obj.subtotal)
