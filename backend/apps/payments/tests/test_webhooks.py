"""
Webhook handler tests.
"""
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json

from django.test import RequestFactory
from rest_framework import status

from apps.payments.webhooks import StripeWebhookView, HitPayWebhookView


class TestStripeWebhook:
    """Tests for Stripe webhook handler."""
    
    @pytest.fixture
    def factory(self):
        return RequestFactory()
    
    @patch('apps.payments.webhooks.StripeAdapter')
    @patch('apps.payments.webhooks.PaymentOrchestrator')
    def test_successful_payment_webhook(self, mock_orchestrator, mock_adapter_class, factory):
        """Test handling successful payment webhook."""
        mock_adapter = MagicMock()
        mock_adapter.verify_webhook.return_value = True
        mock_adapter.parse_webhook_event.return_value = {
            'event_type': 'payment_intent.succeeded',
            'payment_intent_id': 'pi_test123',
            'metadata': {'order_id': 'order123'},
        }
        mock_adapter_class.return_value = mock_adapter
        
        payload = json.dumps({
            'type': 'payment_intent.succeeded',
            'data': {'object': {'id': 'pi_test123'}},
        })
        
        request = factory.post(
            '/webhooks/stripe/',
            payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_sig',
        )
        request._body = payload.encode()
        
        view = StripeWebhookView.as_view()
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
    
    @patch('apps.payments.webhooks.StripeAdapter')
    def test_invalid_signature_webhook(self, mock_adapter_class, factory):
        """Test rejecting invalid signature."""
        from apps.payments.exceptions import WebhookVerificationError
        
        mock_adapter = MagicMock()
        mock_adapter.verify_webhook.side_effect = WebhookVerificationError("Invalid")
        mock_adapter_class.return_value = mock_adapter
        
        payload = b'{}'
        
        request = factory.post(
            '/webhooks/stripe/',
            payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='invalid',
        )
        request._body = payload
        
        view = StripeWebhookView.as_view()
        response = view(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestHitPayWebhook:
    """Tests for HitPay webhook handler."""
    
    @pytest.fixture
    def factory(self):
        return RequestFactory()
    
    @patch('apps.payments.webhooks.HitPayAdapter')
    @patch('apps.payments.webhooks.PaymentOrchestrator')
    def test_successful_payment_webhook(self, mock_orchestrator, mock_adapter_class, factory):
        """Test handling successful payment webhook."""
        mock_adapter = MagicMock()
        mock_adapter.verify_webhook.return_value = True
        mock_adapter.parse_webhook_event.return_value = {
            'event_type': 'payment.completed',
            'payment_request_id': 'req123',
            'status': 'completed',
            'reference_number': 'order123',
        }
        mock_adapter_class.return_value = mock_adapter
        
        payload = b'status=completed&hmac=valid_hmac&reference_number=order123'
        
        request = factory.post(
            '/webhooks/hitpay/',
            payload,
            content_type='application/x-www-form-urlencoded',
        )
        request._body = payload
        
        view = HitPayWebhookView.as_view()
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
