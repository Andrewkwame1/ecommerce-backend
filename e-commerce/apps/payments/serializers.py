from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_method', 'payment_method_display', 'transaction_id',
            'amount', 'status', 'status_display', 'payment_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'transaction_id', 'status', 'status_display', 'payment_date', 'created_at', 'updated_at']
