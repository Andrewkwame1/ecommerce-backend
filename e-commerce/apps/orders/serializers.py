from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory
from apps.users.serializers import AddressSerializer
from apps.products.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'price', 'quantity', 'subtotal', 'created_at'
        ]
        read_only_fields = ['id', 'product_name', 'product_sku', 'subtotal', 'created_at']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for order status history"""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'note', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_by_name', 'created_at']


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order list view"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display', 'total_amount',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'status_display', 'created_at', 'updated_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer for order detail view"""
    
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_be_cancelled = serializers.SerializerMethodField(method_name='get_can_be_cancelled')
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display', 'subtotal',
            'tax', 'shipping_cost', 'discount', 'total_amount', 'shipping_address',
            'billing_address', 'tracking_number', 'shipped_at', 'delivered_at',
            'notes', 'items', 'status_history', 'can_be_cancelled', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'status_display', 'items', 'status_history',
            'created_at', 'updated_at'
        ]
    
    def get_can_be_cancelled(self, obj) -> bool:
        """Check if order can be cancelled."""
        return obj.can_be_cancelled
