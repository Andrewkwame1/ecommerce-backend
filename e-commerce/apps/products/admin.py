from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductVariant, Review, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model"""
    list_display = ['name', 'slug', 'parent', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at']


class ProductImageInline(admin.TabularInline):
    """Inline admin for ProductImage"""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


class ProductVariantInline(admin.TabularInline):
    """Inline admin for ProductVariant"""
    model = ProductVariant
    extra = 1
    fields = ['name', 'sku', 'price', 'quantity', 'is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for Product model"""
    list_display = ['name', 'sku', 'category', 'price', 'quantity_status', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'category', 'track_inventory', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'average_rating_display']
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        ('Product Info', {'fields': ('id', 'name', 'slug', 'description', 'category')}),
        ('Pricing', {'fields': ('price', 'compare_price', 'cost_price')}),
        ('Inventory', {'fields': ('sku', 'barcode', 'quantity', 'track_inventory', 'low_stock_threshold')}),
        ('Specifications', {'fields': ('weight', 'dimensions')}),
        ('SEO', {'fields': ('meta_title', 'meta_description')}),
        ('Status', {'fields': ('is_active', 'is_featured', 'average_rating_display')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def quantity_status(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: orange;">Low ({} units)</span>', obj.quantity)
        elif obj.is_in_stock:
            return format_html('<span style="color: green;">{} units</span>', obj.quantity)
        else:
            return format_html('<span style="color: red;">Out of Stock</span>')
    quantity_status.short_description = 'Stock Status'
    
    def average_rating_display(self, obj):
        rating = obj.average_rating
        return format_html('<span>{:.1f} ⭐ ({} reviews)</span>', rating, obj.reviews.filter(is_approved=True).count())
    average_rating_display.short_description = 'Average Rating'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin for ProductImage model"""
    list_display = ['product', 'alt_text', 'is_primary', 'order']
    list_filter = ['is_primary', 'product']
    search_fields = ['product__name', 'alt_text']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin for ProductVariant model"""
    list_display = ['product', 'name', 'sku', 'quantity', 'is_active']
    list_filter = ['is_active', 'product']
    search_fields = ['product__name', 'name', 'sku']
    readonly_fields = ['id', 'created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for Review model"""
    list_display = ['product', 'user', 'rating', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['is_approved', 'is_verified_purchase', 'rating', 'created_at']
    search_fields = ['product__name', 'user__email', 'title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Review', {'fields': ('id', 'product', 'user', 'rating', 'title', 'comment')}),
        ('Status', {'fields': ('is_approved', 'is_verified_purchase')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin for Wishlist model"""
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['id', 'created_at']
