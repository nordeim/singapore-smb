"""
Gateway adapter tests.
"""
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
import uuid

from apps.payments.gateways.base import PaymentIntent, PaymentResult
from apps.payments.gateways.stripe_adapter import StripeAdapter
from apps.payments.gateways.hitpay_adapter import HitPayAdapter
from apps.payments.exceptions import PaymentIntentError, WebhookVerificationError


class TestPaymentIntent:
    """Tests for PaymentIntent dataclass."""
    
    def test_create_payment_intent(self):
        """Test creating a payment intent."""
        intent = PaymentIntent(
            id='pi_test123',
            client_secret='pi_test123_secret',
            amount=Decimal('100.00'),
            currency='SGD',
            status='pending',
            gateway='stripe',
        )
        
        assert intent.id == 'pi_test123'
        assert intent.amount == Decimal('100.00')
        assert intent.gateway == 'stripe'


class TestPaymentResult:
    """Tests for PaymentResult dataclass."""
    
    def test_create_success_result(self):
        """Test creating a success result."""
        result = PaymentResult(
            success=True,
            payment_id='ch_test123',
            gateway_reference='ch_test123',
            amount=Decimal('100.00'),
        )
        
        assert result.success is True
        assert result.payment_id == 'ch_test123'
    
    def test_create_failure_result(self):
        """Test creating a failure result."""
        result = PaymentResult(
            success=False,
            payment_id='',
            gateway_reference='',
            error_message='Card declined',
        )
        
        assert result.success is False
        assert result.error_message == 'Card declined'


class TestStripeAdapter:
    """Tests for Stripe adapter."""
    
    @patch('apps.payments.gateways.stripe_adapter.settings')
    def test_adapter_initialization(self, mock_settings):
        """Test adapter initializes correctly."""
        mock_settings.STRIPE_SECRET_KEY = 'sk_test_key'
        
        adapter = StripeAdapter()
        
        assert adapter.name == 'stripe'
        assert 'card' in adapter.supported_methods
    
    @patch('apps.payments.gateways.stripe_adapter.StripeAdapter.stripe')
    @patch('apps.payments.gateways.stripe_adapter.settings')
    def test_create_payment_intent(self, mock_settings, mock_stripe):
        """Test creating a Stripe payment intent."""
        mock_settings.STRIPE_SECRET_KEY = 'sk_test_key'
        
        mock_intent = MagicMock()
        mock_intent.id = 'pi_test123'
        mock_intent.client_secret = 'pi_test123_secret'
        mock_intent.status = 'requires_payment_method'
        mock_stripe.PaymentIntent.create.return_value = mock_intent
        
        adapter = StripeAdapter()
        adapter._stripe = mock_stripe
        
        intent = adapter.create_payment_intent(
            amount=Decimal('100.00'),
            currency='SGD',
            order_id=str(uuid.uuid4()),
        )
        
        assert intent.id == 'pi_test123'
        assert intent.gateway == 'stripe'
    
    @patch('apps.payments.gateways.stripe_adapter.StripeAdapter.stripe')
    @patch('apps.payments.gateways.stripe_adapter.settings')
    def test_capture_payment(self, mock_settings, mock_stripe):
        """Test capturing a payment."""
        mock_settings.STRIPE_SECRET_KEY = 'sk_test_key'
        
        mock_intent = MagicMock()
        mock_intent.id = 'pi_test123'
        mock_intent.status = 'succeeded'
        mock_intent.amount = 10000
        mock_intent.currency = 'sgd'
        mock_stripe.PaymentIntent.retrieve.return_value = mock_intent
        
        adapter = StripeAdapter()
        adapter._stripe = mock_stripe
        
        result = adapter.capture_payment('pi_test123')
        
        assert result.success is True
        assert result.amount == Decimal('100.00')


class TestHitPayAdapter:
    """Tests for HitPay adapter."""
    
    @patch('apps.payments.gateways.hitpay_adapter.settings')
    def test_adapter_initialization(self, mock_settings):
        """Test adapter initializes correctly."""
        mock_settings.HITPAY_API_KEY = 'test_key'
        mock_settings.HITPAY_SANDBOX = True
        
        adapter = HitPayAdapter()
        
        assert adapter.name == 'hitpay'
        assert 'paynow' in adapter.supported_methods
    
    def test_sandbox_url(self):
        """Test sandbox URL is used in sandbox mode."""
        with patch('apps.payments.gateways.hitpay_adapter.settings') as mock_settings:
            mock_settings.HITPAY_SANDBOX = True
            
            adapter = HitPayAdapter()
            
            assert 'sandbox' in adapter.api_url
    
    @patch('apps.payments.gateways.hitpay_adapter.settings')
    def test_verify_webhook_signature(self, mock_settings):
        """Test webhook signature verification."""
        mock_settings.HITPAY_SALT = 'test_salt'
        
        adapter = HitPayAdapter()
        
        # Invalid signature should raise error
        with pytest.raises(WebhookVerificationError):
            adapter.verify_webhook(
                payload=b'status=completed&hmac=invalid',
                signature='invalid',
            )
