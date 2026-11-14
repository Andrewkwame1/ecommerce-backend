from django.contrib import admin
from django.utils.html import format_html
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notification model"""
    list_display = ['user', 'notification_type', 'subject', 'status_badge', 'created_at']
    list_filter = ['notification_type', 'status', 'created_at']
    search_fields = ['user__email', 'subject']
    readonly_fields = ['id', 'created_at', 'sent_at']
    
    fieldsets = (
        ('Notification', {'fields': ('id', 'user', 'notification_type', 'subject', 'message')}),
        ('Status', {'fields': ('status', 'sent_at')}),
        ('Data', {'fields': ('data',)}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'sent': 'green',
            'failed': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
