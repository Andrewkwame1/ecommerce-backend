# apps/payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create-intent/', views.CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('confirm/', views.ConfirmPaymentView.as_view(), name='confirm_payment'),
    path('webhook/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
]
