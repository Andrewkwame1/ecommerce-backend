# apps/products/filters.py
import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """Filter for products"""
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Product name'
    )
    
    price_min = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Minimum price'
    )
    
    price_max = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Maximum price'
    )
    
    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='iexact',
        label='Category'
    )
    
    in_stock = django_filters.BooleanFilter(
        field_name='stock',
        method='filter_in_stock',
        label='In stock'
    )
    
    class Meta:
        model = Product
        fields = ['name', 'price_min', 'price_max', 'category']
    
    def filter_in_stock(self, queryset, name, value):
        """Filter products by stock availability"""
        if value:
            return queryset.filter(stock__gt=0)
        return queryset
