from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
import stripe
import json

from .models import Payment
from .serializers import PaymentSerializer
from apps.orders.models import Order, OrderStatusHistory


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(generics.GenericAPIView):
    """Create payment intent for Stripe"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        order_id = request.data.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Amount in cents
                currency='usd',
                metadata={'order_id': str(order.id)},
                description=f'Payment for order {order.order_number}'
            )
            
            # Create payment record
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'payment_method': 'stripe',
                    'amount': order.total_amount,
                    'status': 'pending'
                }
            )
            
            return Response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmPaymentView(generics.GenericAPIView):
    """Confirm payment"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        order_id = request.data.get('order_id')
        payment_intent_id = request.data.get('payment_intent_id')
        
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        try:
            # Retrieve payment intent
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                # Update payment
                payment = Payment.objects.get(order=order)
                payment.status = 'completed'
                payment.transaction_id = intent.id
                payment.payment_date = timezone.now()
                payment.metadata = {
                    'stripe_payment_intent': intent.id,
                    'stripe_charge_id': intent.latest_charge
                }
                payment.save()
                
                # Update order status
                order.status = 'processing'
                order.save()
                
                # Create status history
                OrderStatusHistory.objects.create(
                    order=order,
                    status='processing',
                    note='Payment confirmed. Order processing started.'
                )
                
                return Response({
                    'message': 'Payment confirmed successfully',
                    'order_id': str(order.id)
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Payment not completed',
                    'status': intent.status
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Handle successful payment
        pass
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        # Handle failed payment
        pass
    
    return JsonResponse({'status': 'success'}, status=200)


class StripeWebhookView(APIView):
    """Alternative webhook handler using DRF"""
    
    permission_classes = [permissions.AllowAny]
    
    @csrf_exempt
    def post(self, request):
        return stripe_webhook(request)
