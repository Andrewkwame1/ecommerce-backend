"""
Caching Utilities and Algorithms

Provides efficient caching strategies for common operations:
- Product listing caching
- Category hierarchy caching
- Cache invalidation patterns
- TTL management
"""

from django.core.cache import cache
from functools import wraps
import hashlib
import json


class CacheManager:
    """Manages cache operations with efficient strategies"""
    
    # Cache TTL constants (in seconds)
    TTL_SHORT = 300  # 5 minutes
    TTL_MEDIUM = 3600  # 1 hour
    TTL_LONG = 86400  # 24 hours
    
    # Cache key prefixes
    PREFIX_CATEGORY = 'category'
    PREFIX_PRODUCT = 'product'
    PREFIX_WISHLIST = 'wishlist'
    PREFIX_CART = 'cart'
    PREFIX_ORDER = 'order'
    PREFIX_REVIEW = 'review'
    
    @staticmethod
    def make_cache_key(*args, **kwargs) -> str:
        """
        Generate consistent cache key from parameters.
        
        Algorithm: Uses hashing to create fixed-length keys for any input.
        
        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments
            
        Returns:
            Cache key string
        """
        key_data = f"{':'.join(str(arg) for arg in args)}:{json.dumps(kwargs, sort_keys=True)}"
        # Use hash for consistent key length regardless of input
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    def cache_result(key: str, ttl: int = TTL_SHORT):
        """
        Decorator for caching function results.
        
        Algorithm: Memoization pattern with configurable TTL.
        
        Args:
            key: Cache key prefix
            ttl: Time to live in seconds
            
        Returns:
            Decorated function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = CacheManager.make_cache_key(key, *args, **kwargs)
                cached = cache.get(cache_key)
                
                if cached is not None:
                    return cached
                
                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator
    
    @staticmethod
    def invalidate_pattern(pattern: str) -> int:
        """
        Invalidate all cache keys matching pattern.
        
        Algorithm: Pattern-based cache invalidation.
        Note: Django's default cache doesn't support pattern deletion,
        so we use a workaround for Redis backends.
        
        Args:
            pattern: Cache key pattern
            
        Returns:
            Number of keys deleted (approximate)
        """
        try:
            # For Redis backend
            from django.core.cache import caches
            
            cache_obj = caches['default']
            # Check if it's a Redis cache by checking for client attribute
            if hasattr(cache_obj, '_client') or hasattr(cache_obj, '_cache'):
                try:
                    # Try to get Redis client for pattern deletion
                    if hasattr(cache_obj, '_cache'):
                        client = cache_obj._cache
                    elif hasattr(cache_obj, '_client'):
                        client = cache_obj._client()
                    else:
                        return 0
                    
                    keys = client.keys(f"*{pattern}*")
                    if keys:
                        return client.delete(*keys)
                except (AttributeError, TypeError):
                    pass
        except (ImportError, AttributeError):
            pass
        
        return 0
    
    @staticmethod
    def clear_product_cache(product_id: str = None):
        """Clear product-related caches"""
        if product_id:
            # Clear specific product cache
            cache.delete(f"{CacheManager.PREFIX_PRODUCT}:{product_id}")
            cache.delete(f"{CacheManager.PREFIX_PRODUCT}_detail:{product_id}")
        else:
            # Clear all product caches (pattern-based for Redis)
            CacheManager.invalidate_pattern(CacheManager.PREFIX_PRODUCT)
    
    @staticmethod
    def clear_category_cache(category_id: str = None):
        """Clear category-related caches"""
        if category_id:
            cache.delete(f"{CacheManager.PREFIX_CATEGORY}:{category_id}")
        else:
            # Clear all category caches
            cache.delete(f"{CacheManager.PREFIX_CATEGORY}:list")
            CacheManager.invalidate_pattern(CacheManager.PREFIX_CATEGORY)
    
    @staticmethod
    def clear_user_caches(user_id: str):
        """Clear all user-specific caches"""
        CacheManager.invalidate_pattern(f"user:{user_id}")
        CacheManager.invalidate_pattern(f"{CacheManager.PREFIX_WISHLIST}:{user_id}")
        CacheManager.invalidate_pattern(f"{CacheManager.PREFIX_CART}:{user_id}")
        CacheManager.invalidate_pattern(f"{CacheManager.PREFIX_ORDER}:{user_id}")


class QueryCacheStrategy:
    """Efficient query caching for common patterns"""
    
    @staticmethod
    def get_categories_hierarchical(use_cache: bool = True):
        """
        Get hierarchical categories with caching.
        
        Algorithm: Single query with prefetch_related for hierarchy.
        Caches entire hierarchy to reduce database queries.
        
        Args:
            use_cache: Whether to use cache
            
        Returns:
            List of root categories with prefetched children
        """
        cache_key = f"{CacheManager.PREFIX_CATEGORY}:hierarchical"
        
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        
        from apps.products.models import Category
        from django.db.models import Prefetch
        
        # Optimized query with prefetch
        categories = Category.objects.filter(
            is_active=True,
            parent__isnull=True
        ).prefetch_related(
            Prefetch(
                'children',
                queryset=Category.objects.filter(is_active=True).prefetch_related(
                    Prefetch('children', queryset=Category.objects.filter(is_active=True))
                )
            )
        )
        
        result = list(categories)
        if use_cache:
            cache.set(cache_key, result, CacheManager.TTL_MEDIUM)
        
        return result
    
    @staticmethod
    def get_products_featured(use_cache: bool = True, limit: int = 10):
        """
        Get featured products with caching.
        
        Algorithm: Single query with select_related for efficiency.
        
        Args:
            use_cache: Whether to use cache
            limit: Maximum number of products
            
        Returns:
            List of featured products
        """
        cache_key = f"{CacheManager.PREFIX_PRODUCT}:featured:{limit}"
        
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        
        from apps.products.models import Product
        
        products = Product.objects.filter(
            is_active=True,
            is_featured=True
        ).select_related(
            'category'
        ).prefetch_related(
            'images'
        ).only(
            'id', 'name', 'slug', 'price', 'quantity', 'category_id'
        )[:limit]
        
        result = list(products)
        if use_cache:
            cache.set(cache_key, result, CacheManager.TTL_SHORT)
        
        return result
