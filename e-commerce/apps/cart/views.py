from rest_framework import status, generics, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from apps.products.models import Product, ProductVariant


class CartDetailView(generics.RetrieveAPIView):
    """Get cart details with optimized queries"""
    
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Optimize cart retrieval: get_or_create is atomic and efficient
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    def retrieve(self, request, *args, **kwargs):
        """Override to prefetch cart items with products and variants"""
        instance = self.get_object()
        
        # Prefetch related products and variants to avoid N+1 queries
        instance.items.all().select_related('product', 'variant').prefetch_related('product__images')
        
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)


class AddToCartView(generics.CreateAPIView):
    """Add item to cart with efficient upsert logic"""
    
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        
        product_id = self.request.data.get('product_id')
        variant_id = self.request.data.get('variant_id')
        quantity = int(self.request.data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        variant = None
        
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id)
        
        # Use get_or_create for atomic upsert operation (more efficient)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Item exists, increment quantity
            cart_item.quantity += quantity
            cart_item.save()


class CartItemUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Update or remove cart item with optimized queries"""
    
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only get cart items for the current user
        return CartItem.objects.filter(
            cart__user=self.request.user
        ).select_related('product', 'variant')


class ClearCartView(generics.GenericAPIView):
    """Clear all items from cart"""
    
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.clear()
        return Response({'message': 'Cart cleared successfully'}, status=status.HTTP_200_OK)
