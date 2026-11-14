from rest_framework import status, generics, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Prefetch

from .models import Order, OrderItem, OrderStatusHistory
from .serializers import OrderListSerializer, OrderDetailSerializer
from apps.cart.models import Cart
from apps.users.models import Address
from apps.products.models import Product
from utils.pagination import StandardPagination


class OrderListCreateView(generics.ListCreateAPIView):
    """List user orders and create new order (checkout) with optimized queries"""
    
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        # Prevent errors during schema generation with AnonymousUser
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        
        # Optimize: prefetch related items, status history, and user
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('product', 'variant')),
            Prefetch('status_history', queryset=OrderStatusHistory.objects.order_by('-created_at')),
        ).select_related(
            'shipping_address', 'billing_address'
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderDetailSerializer
        return OrderListSerializer
    
    @transaction.atomic
    def perform_create(self, serializer):
        """Create order from cart with transaction safety"""
        user = self.request.user
        cart = get_object_or_404(Cart, user=user)
        
        # Get addresses
        shipping_address_id = self.request.data.get('shipping_address_id')
        billing_address_id = self.request.data.get('billing_address_id')
        
        shipping_address = get_object_or_404(Address, id=shipping_address_id, user=user)
        billing_address = get_object_or_404(Address, id=billing_address_id, user=user)
        
        # Calculate totals
        from decimal import Decimal
        
        subtotal = cart.subtotal
        tax = subtotal * Decimal('0.1')  # 10% tax
        shipping_cost = Decimal('5.0') if subtotal > 0 else Decimal('0.0')
        discount = Decimal('0.0')
        
        total_amount = subtotal + tax + shipping_cost - discount
        
        # Create order
        order = Order.objects.create(
            user=user,
            status='pending',
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            discount=discount,
            total_amount=total_amount,
            shipping_address=shipping_address,
            billing_address=billing_address
        )
        
        # Batch create order items (more efficient than individual creates)
        cart_items = cart.items.select_related('product', 'variant')
        order_items = []
        
        for cart_item in cart_items:
            order_items.append(OrderItem(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                product_name=cart_item.product.name,
                product_sku=cart_item.variant.sku if cart_item.variant else cart_item.product.sku,
                price=cart_item.price,
                quantity=cart_item.quantity
            ))
            
            # Update product quantity (track inventory changes)
            if cart_item.product.track_inventory:
                cart_item.product.quantity -= cart_item.quantity
        
        # Bulk create order items
        OrderItem.objects.bulk_create(order_items)
        
        # Bulk update products (more efficient)
        Product.objects.bulk_update(
            [item.product for item in cart_items if item.product.track_inventory],
            ['quantity']
        )
        
        # Clear cart
        cart.clear()
        
        # Create order status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            note='Order created'
        )


class OrderDetailView(generics.RetrieveAPIView):
    """Get order details with optimized queries"""
    
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Optimize: prefetch all related data
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('product', 'variant')),
            Prefetch('status_history', queryset=OrderStatusHistory.objects.order_by('-created_at'))
        ).select_related('shipping_address', 'billing_address')


class CancelOrderView(generics.GenericAPIView):
    """Cancel order with proper inventory restoration"""
    
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        
        if not order.can_be_cancelled:
            return Response(
                {'error': 'Order cannot be cancelled at this stage'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Return inventory (bulk update for efficiency)
        order_items = order.items.select_related('product')
        
        for order_item in order_items:
            if order_item.product.track_inventory:
                order_item.product.quantity += order_item.quantity
        
        # Bulk update all products at once (more efficient)
        Product.objects.bulk_update(
            [item.product for item in order_items if item.product.track_inventory],
            ['quantity']
        )
        
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            note='Order cancelled by user',
            created_by=request.user
        )
        
        return Response(
            {'message': 'Order cancelled successfully'},
            status=status.HTTP_200_OK
        )
