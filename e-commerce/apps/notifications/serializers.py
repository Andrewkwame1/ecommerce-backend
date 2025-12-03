from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notification"""
    
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'type_display', 'subject', 'message',
            'status', 'status_display', 'data', 'created_at', 'sent_at'
        ]
        read_only_fields = ['id', 'type_display', 'status_display', 'created_at', 'sent_at']
