"""
HitPay payment gateway adapter.

Supports Singapore-specific payment methods:
- PayNow (QR code)
- GrabPay
- ShopeePay
- Credit/Debit Cards
"""
import hashlib
import hmac
import logging
from decimal import Decimal
from typing import Optional, Dict, Any

from django.conf import settings

from apps.payments.gateways.base import PaymentGatewayAdapter, PaymentIntent, PaymentResult
from apps.payments.exceptions import (
    PaymentIntentError, PaymentCaptureError, PaymentRefundError,
    WebhookVerificationError, PaymentGatewayError,
)


logger = logging.getLogger(__name__)


class HitPayAdapter(PaymentGatewayAdapter):
    """
    HitPay payment gateway adapter for Singapore payments.
    
    HitPay is a Singapore-based payment gateway that supports
    PayNow, GrabPay, and other local payment methods.
    """
    
    name = 'hitpay'
    supported_methods = ['paynow', 'grabpay', 'shopee_pay', 'card']
    
    # API endpoints
    SANDBOX_URL = 'https://api.sandbox.hit-pay.com/v1'
    PRODUCTION_URL = 'https://api.hit-pay.com/v1'
    
    def __init__(self):
        """Initialize HitPay client."""
        self._httpx = None
    
    @property
    def api_url(self) -> str:
        """Get API URL based on sandbox setting."""
        is_sandbox = getattr(settings, 'HITPAY_SANDBOX', True)
        return self.SANDBOX_URL if is_sandbox else self.PRODUCTION_URL
    
    @property
    def api_key(self) -> str:
        """Get API key from settings."""
        return getattr(settings, 'HITPAY_API_KEY', '')
    
    @property
    def salt(self) -> str:
        """Get HMAC salt for webhook verification."""
        return getattr(settings, 'HITPAY_SALT', '')
    
    @property
    def httpx(self):
        """Lazy load httpx."""
        if self._httpx is None:
            try:
                import httpx
                self._httpx = httpx
            except ImportError:
                raise PaymentGatewayError("httpx package not installed")
        return self._httpx
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers."""
        return {
            'X-BUSINESS-API-KEY': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
        }
    
    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        order_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        payment_method: str = None,
        redirect_url: str = None,
        webhook_url: str = None,
    ) -> PaymentIntent:
        """
        Create a HitPay payment request.
        
        Returns a PaymentIntent with a payment_url for redirect.
        """
        try:
            data = {
                'amount': str(amount),
                'currency': currency.upper(),
                'reference_number': order_id,
                'name': f'Order {order_id}',
            }
            
            if redirect_url:
                data['redirect_url'] = redirect_url
            if webhook_url:
                data['webhook'] = webhook_url
            if payment_method:
                data['payment_methods[]'] = payment_method
            
            response = self.httpx.post(
                f'{self.api_url}/payment-requests',
                headers=self._get_headers(),
                data=data,
                timeout=30.0,
            )
            
            if response.status_code != 201:
                logger.error(f"HitPay error: {response.text}")
                raise PaymentIntentError(f"HitPay API error: {response.status_code}")
            
            result = response.json()
            
            logger.info(f"Created HitPay payment request {result['id']} for order {order_id}")
            
            return PaymentIntent(
                id=result['id'],
                client_secret='',  # HitPay uses redirect
                amount=amount,
                currency=currency,
                status=result.get('status', 'pending'),
                gateway=self.name,
                metadata=metadata or {},
                payment_url=result.get('url'),
            )
            
        except self.httpx.HTTPError as e:
            logger.error(f"HitPay request error: {e}")
            raise PaymentIntentError(str(e))
    
    def capture_payment(
        self,
        payment_intent_id: str,
    ) -> PaymentResult:
        """
        Check HitPay payment status.
        
        HitPay payments are captured automatically on completion.
        This method retrieves the current status.
        """
        try:
            response = self.httpx.get(
                f'{self.api_url}/payment-requests/{payment_intent_id}',
                headers=self._get_headers(),
                timeout=30.0,
            )
            
            if response.status_code != 200:
                raise PaymentCaptureError(f"HitPay status error: {response.status_code}")
            
            result = response.json()
            
            is_completed = result.get('status') == 'completed'
            
            return PaymentResult(
                success=is_completed,
                payment_id=result['id'],
                gateway_reference=result.get('payment_id', result['id']),
                amount=Decimal(result.get('amount', '0')),
                currency=result.get('currency', 'SGD'),
            )
            
        except self.httpx.HTTPError as e:
            logger.error(f"HitPay status error: {e}")
            raise PaymentCaptureError(str(e))
    
    def refund_payment(
        self,
        payment_id: str,
        amount: Decimal,
        reason: str = '',
    ) -> PaymentResult:
        """
        Refund a HitPay payment.
        """
        try:
            data = {
                'payment_id': payment_id,
                'amount': str(amount),
            }
            
            response = self.httpx.post(
                f'{self.api_url}/refund',
                headers=self._get_headers(),
                data=data,
                timeout=30.0,
            )
            
            if response.status_code not in [200, 201]:
                logger.error(f"HitPay refund error: {response.text}")
                raise PaymentRefundError(f"HitPay refund error: {response.status_code}")
            
            result = response.json()
            
            logger.info(f"Created HitPay refund for payment {payment_id}")
            
            return PaymentResult(
                success=result.get('status') in ['pending', 'succeeded'],
                payment_id=result.get('id', payment_id),
                gateway_reference=result.get('id', ''),
                amount=amount,
            )
            
        except self.httpx.HTTPError as e:
            logger.error(f"HitPay refund error: {e}")
            raise PaymentRefundError(str(e))
    
    def verify_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        Verify HitPay webhook HMAC signature.
        """
        try:
            # Parse payload to get sorted parameters
            import urllib.parse
            params = urllib.parse.parse_qs(payload.decode('utf-8'))
            
            # Sort parameters and build signature string
            sorted_params = sorted(
                (k, v[0] if isinstance(v, list) else v)
                for k, v in params.items()
                if k != 'hmac'
            )
            
            signature_string = ''.join(f'{k}{v}' for k, v in sorted_params)
            
            # Calculate expected HMAC
            expected_hmac = hmac.new(
                self.salt.encode('utf-8'),
                signature_string.encode('utf-8'),
                hashlib.sha256,
            ).hexdigest()
            
            if not hmac.compare_digest(expected_hmac, signature):
                raise WebhookVerificationError("HMAC signature mismatch")
            
            return True
            
        except Exception as e:
            logger.warning(f"HitPay webhook verification failed: {e}")
            raise WebhookVerificationError(str(e))
    
    def parse_webhook_event(
        self,
        payload: bytes,
    ) -> Dict[str, Any]:
        """Parse HitPay webhook payload."""
        import urllib.parse
        params = urllib.parse.parse_qs(payload.decode('utf-8'))
        
        # Extract first value from each list
        data = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}
        
        return {
            'event_type': 'payment.' + data.get('status', 'unknown'),
            'payment_id': data.get('payment_id'),
            'payment_request_id': data.get('payment_request_id'),
            'reference_number': data.get('reference_number'),
            'status': data.get('status'),
            'amount': data.get('amount'),
            'currency': data.get('currency', 'SGD'),
        }
    
    def generate_paynow_qr(
        self,
        amount: Decimal,
        order_id: str,
    ) -> str:
        """
        Generate a PayNow QR code data string.
        
        Note: This creates a payment request specifically for PayNow.
        
        Returns:
            QR code data string for PayNow
        """
        intent = self.create_payment_intent(
            amount=amount,
            currency='SGD',
            order_id=order_id,
            payment_method='paynow',
        )
        
        # HitPay provides QR data in the response for PayNow
        return intent.payment_url or ''
