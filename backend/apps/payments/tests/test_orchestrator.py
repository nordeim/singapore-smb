"""
Payment orchestrator tests.
"""
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
import uuid

from apps.payments.services import PaymentOrchestrator
from apps.payments.exceptions import PaymentGatewayError
from apps.commerce.tests.factories import OrderFactory
from apps.accounts.tests.factories import CompanyFactory


class TestPaymentOrchestrator:
    """Tests for PaymentOrchestrator service."""
    
    def test_get_available_methods_with_stripe(self):
        """Test getting methods when Stripe is configured."""
        with patch('apps.payments.services.payment_orchestrator.settings') as mock:
            mock.STRIPE_SECRET_KEY = 'sk_test_key'
            mock.HITPAY_API_KEY = ''
            
            methods = PaymentOrchestrator.get_available_methods()
            
            assert 'card' in methods
            assert 'apple_pay' in methods
    
    def test_get_available_methods_with_hitpay(self):
        """Test getting methods when HitPay is configured."""
        with patch('apps.payments.services.payment_orchestrator.settings') as mock:
            mock.STRIPE_SECRET_KEY = ''
            mock.HITPAY_API_KEY = 'hp_test_key'
            
            methods = PaymentOrchestrator.get_available_methods()
            
            assert 'paynow' in methods
            assert 'grabpay' in methods
    
    def test_get_gateway_for_method_card(self):
        """Test getting Stripe gateway for card."""
        gateway = PaymentOrchestrator.get_gateway_for_method('card')
        
        assert gateway.name == 'stripe'
    
    def test_get_gateway_for_method_paynow(self):
        """Test getting HitPay gateway for PayNow."""
        gateway = PaymentOrchestrator.get_gateway_for_method('paynow')
        
        assert gateway.name == 'hitpay'
    
    def test_get_gateway_for_unknown_method(self):
        """Test error for unknown payment method."""
        with pytest.raises(PaymentGatewayError):
            PaymentOrchestrator.get_gateway_for_method('unknown')


@pytest.mark.django_db
class TestPaymentOrchestatorIntegration:
    """Integration tests for payment orchestrator."""
    
    @patch('apps.payments.services.payment_orchestrator.PaymentOrchestrator.get_gateway_for_method')
    def test_create_payment_intent(self, mock_get_gateway):
        """Test creating a payment intent for an order."""
        from apps.payments.gateways.base import PaymentIntent
        
        mock_gateway = MagicMock()
        mock_gateway.name = 'stripe'
        mock_gateway.create_payment_intent.return_value = PaymentIntent(
            id='pi_test',
            client_secret='secret',
            amount=Decimal('100.00'),
            currency='SGD',
            status='pending',
            gateway='stripe',
        )
        mock_get_gateway.return_value = mock_gateway
        
        order = OrderFactory()
        
        intent = PaymentOrchestrator.create_payment_intent(
            order=order,
            payment_method='card',
        )
        
        assert intent.id == 'pi_test'
        assert intent.gateway == 'stripe'
        mock_gateway.create_payment_intent.assert_called_once()
