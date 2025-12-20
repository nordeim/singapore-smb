"""
Payments URL routing.
"""
from django.urls import path

from apps.payments.views import (
    CreatePaymentIntentView,
    PaymentMethodsView,
    PaymentStatusView,
)
from apps.payments.webhooks import StripeWebhookView, HitPayWebhookView


app_name = 'payments'


urlpatterns = [
    # API endpoints
    path('create-intent/', CreatePaymentIntentView.as_view(), name='create-intent'),
    path('methods/', PaymentMethodsView.as_view(), name='payment-methods'),
    path('status/<uuid:order_id>/', PaymentStatusView.as_view(), name='payment-status'),
    
    # Webhooks
    path('webhooks/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('webhooks/hitpay/', HitPayWebhookView.as_view(), name='hitpay-webhook'),
]
