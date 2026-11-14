"""
Inventory Management Algorithms and Utilities

This module provides efficient algorithms for:
- Stock tracking and updates
- Low stock alerts
- Inventory allocation
- Bulk inventory operations
"""

from django.db.models import F, Q
from django.db import transaction
from apps.products.models import Product, ProductVariant


class InventoryManager:
    """Manages inventory operations with efficient algorithms"""
    
    @staticmethod
    def allocate_stock(product_id: str, quantity: int, variant_id: str = None) -> bool:
        """
        Allocate stock from inventory using atomic operation.
        
        Algorithm: Uses database-level F expressions to ensure atomicity
        and avoid race conditions in concurrent environments.
        
        Args:
            product_id: UUID of product
            quantity: Quantity to allocate
            variant_id: Optional UUID of variant
            
        Returns:
            True if allocation successful, False otherwise
        """
        if variant_id:
            # Allocate from variant
            updated = ProductVariant.objects.filter(
                id=variant_id,
                quantity__gte=quantity,
                is_active=True
            ).update(quantity=F('quantity') - quantity)
            return updated > 0
        else:
            # Allocate from product
            updated = Product.objects.filter(
                id=product_id,
                quantity__gte=quantity,
                track_inventory=True
            ).update(quantity=F('quantity') - quantity)
            return updated > 0
    
    @staticmethod
    def deallocate_stock(product_id: str, quantity: int, variant_id: str = None) -> bool:
        """
        Return stock to inventory using atomic operation.
        
        Algorithm: Uses F expressions for safe concurrent updates.
        
        Args:
            product_id: UUID of product
            quantity: Quantity to return
            variant_id: Optional UUID of variant
            
        Returns:
            True if deallocation successful, False otherwise
        """
        if variant_id:
            # Return to variant
            updated = ProductVariant.objects.filter(
                id=variant_id,
                is_active=True
            ).update(quantity=F('quantity') + quantity)
            return updated > 0
        else:
            # Return to product
            updated = Product.objects.filter(
                id=product_id,
                track_inventory=True
            ).update(quantity=F('quantity') + quantity)
            return updated > 0
    
    @staticmethod
    def get_low_stock_products(threshold: int = None) -> list:
        """
        Get all products that are below stock threshold.
        
        Algorithm: Uses database-level filtering and only() to minimize
        data transfer. O(n) complexity with database optimization.
        
        Args:
            threshold: Optional custom threshold (uses model default if None)
            
        Returns:
            List of low stock products
        """
        query = Product.objects.filter(
            track_inventory=True,
            is_active=True
        ).filter(
            Q(quantity__lte=F('low_stock_threshold')) if threshold is None
            else Q(quantity__lte=threshold)
        ).only('id', 'name', 'sku', 'quantity', 'low_stock_threshold').values_list(
            'id', 'name', 'sku', 'quantity'
        )
        
        return list(query)
    
    @staticmethod
    @transaction.atomic
    def bulk_adjust_stock(adjustments: list) -> dict:
        """
        Bulk adjust stock for multiple products/variants.
        
        Algorithm: Uses batch update for efficiency (single database query).
        
        Args:
            adjustments: List of dicts with 'product_id', 'quantity', 'variant_id' (optional)
            
        Returns:
            Dictionary with success count and failed updates
        """
        success_count = 0
        failed = []
        
        for adj in adjustments:
            product_id = adj.get('product_id')
            quantity = adj.get('quantity', 0)
            variant_id = adj.get('variant_id')
            
            try:
                if variant_id:
                    updated = ProductVariant.objects.filter(
                        id=variant_id
                    ).update(quantity=F('quantity') + quantity)
                else:
                    updated = Product.objects.filter(
                        id=product_id
                    ).update(quantity=F('quantity') + quantity)
                
                if updated > 0:
                    success_count += 1
                else:
                    failed.append(adj)
            except Exception as e:
                failed.append({**adj, 'error': str(e)})
        
        return {
            'success': success_count,
            'failed': failed,
            'total': len(adjustments)
        }
    
    @staticmethod
    def check_availability(product_id: str, quantity: int, variant_id: str = None) -> bool:
        """
        Check if sufficient stock is available.
        
        Algorithm: Single database query with exists() for O(1) complexity.
        
        Args:
            product_id: UUID of product
            quantity: Required quantity
            variant_id: Optional UUID of variant
            
        Returns:
            True if sufficient stock available, False otherwise
        """
        if variant_id:
            return ProductVariant.objects.filter(
                id=variant_id,
                quantity__gte=quantity,
                is_active=True
            ).exists()
        else:
            return Product.objects.filter(
                id=product_id,
                quantity__gte=quantity,
                track_inventory=True
            ).exists()
    
    @staticmethod
    def get_inventory_status(product_id: str, variant_id: str = None) -> dict:
        """
        Get detailed inventory status for a product/variant.
        
        Algorithm: Single optimized database query.
        
        Args:
            product_id: UUID of product
            variant_id: Optional UUID of variant
            
        Returns:
            Dictionary with inventory details
        """
        if variant_id:
            data = ProductVariant.objects.filter(
                id=variant_id
            ).values(
                'id', 'product__name', 'name', 'sku', 'quantity', 'is_active'
            ).first()
            
            if data:
                return {
                    'sku': data['sku'],
                    'product_name': data['product__name'],
                    'variant_name': data['name'],
                    'quantity': data['quantity'],
                    'is_active': data['is_active'],
                    'in_stock': data['quantity'] > 0
                }
        else:
            data = Product.objects.filter(
                id=product_id
            ).values(
                'id', 'name', 'sku', 'quantity', 'track_inventory', 'low_stock_threshold', 'is_active'
            ).first()
            
            if data:
                quantity = data['quantity']
                threshold = data['low_stock_threshold']
                return {
                    'sku': data['sku'],
                    'product_name': data['name'],
                    'quantity': quantity,
                    'track_inventory': data['track_inventory'],
                    'in_stock': quantity > 0,
                    'low_stock': 0 < quantity <= threshold,
                    'is_active': data['is_active']
                }
        
        return {}
