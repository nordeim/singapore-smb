"""
Zetta Solution Access Point Client for InvoiceNow.

Integrates with Zetta's PEPPOL InvoiceNow API:
https://www.zetta-solution.com/peppol
https://zettapeppol.com
"""
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

from django.conf import settings


logger = logging.getLogger(__name__)


@dataclass
class APSubmissionResult:
    """Result from Access Point submission."""
    
    success: bool
    reference: str
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class APStatusResult:
    """Status query result from Access Point."""
    
    status: str  # pending, delivered, acknowledged, rejected
    delivery_timestamp: Optional[str] = None
    acknowledgments: list = None
    
    def __post_init__(self):
        if self.acknowledgments is None:
            self.acknowledgments = []


class ZettaAccessPointClient:
    """
    Client for Zetta Solution's InvoiceNow Access Point.
    
    Handles:
    - Document submission to PEPPOL network
    - Delivery status polling
    - Acknowledgment retrieval
    - Error handling and retries
    
    API Documentation: Contact Zetta Solution for API specs
    Portal: https://zettapeppol.com/InvoiceNow/
    """
    
    # Default endpoints (production)
    DEFAULT_API_URL = 'https://zettapeppol.com/api/v1'
    
    # Sandbox endpoint for testing
    SANDBOX_API_URL = 'https://sandbox.zettapeppol.com/api/v1'
    
    def __init__(self, api_key: str = None, sandbox: bool = False):
        """
        Initialize Zetta AP client.
        
        Args:
            api_key: Zetta API key (defaults to settings.PEPPOL_AP_KEY)
            sandbox: Use sandbox environment
        """
        self.api_key = api_key or getattr(settings, 'PEPPOL_AP_KEY', '')
        self.sandbox = sandbox
        self._httpx = None
    
    @property
    def api_url(self) -> str:
        """Get API base URL."""
        if self.sandbox:
            return self.SANDBOX_API_URL
        return getattr(settings, 'PEPPOL_AP_URL', self.DEFAULT_API_URL)
    
    @property
    def httpx(self):
        """Lazy load httpx client."""
        if self._httpx is None:
            try:
                import httpx
                self._httpx = httpx
            except ImportError:
                raise ImportError("httpx package required for PEPPOL AP integration")
        return self._httpx
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers."""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/xml',
            'Accept': 'application/json',
            'X-Sender-ID': getattr(settings, 'PEPPOL_SENDER_ID', ''),
        }
    
    def submit_document(
        self,
        xml_content: str,
        document_id: str,
        receiver_id: str,
    ) -> APSubmissionResult:
        """
        Submit UBL document to PEPPOL network via Zetta AP.
        
        Args:
            xml_content: Signed UBL XML content
            document_id: Our internal document ID (PEPPOL ID)
            receiver_id: Receiver's PEPPOL participant ID
            
        Returns:
            APSubmissionResult with submission status
        """
        if not self.api_key:
            logger.warning("No PEPPOL AP key configured, simulating submission")
            return self._simulate_submission(document_id)
        
        try:
            response = self.httpx.post(
                f'{self.api_url}/documents',
                headers=self._get_headers(),
                content=xml_content.encode('utf-8'),
                params={
                    'documentId': document_id,
                    'receiverId': receiver_id,
                },
                timeout=60.0,
            )
            
            if response.status_code in [200, 201, 202]:
                result = response.json()
                logger.info(f"Successfully submitted document {document_id} to Zetta AP")
                
                return APSubmissionResult(
                    success=True,
                    reference=result.get('reference', document_id),
                    message_id=result.get('messageId'),
                    raw_response=result,
                )
            else:
                logger.error(f"Zetta AP submission failed: {response.status_code} - {response.text}")
                return APSubmissionResult(
                    success=False,
                    reference=document_id,
                    error_message=f"HTTP {response.status_code}: {response.text}",
                )
                
        except Exception as e:
            logger.error(f"Zetta AP submission error: {e}")
            return APSubmissionResult(
                success=False,
                reference=document_id,
                error_message=str(e),
            )
    
    def get_status(self, reference: str) -> APStatusResult:
        """
        Get delivery status for a submitted document.
        
        Args:
            reference: Submission reference from submit_document
            
        Returns:
            APStatusResult with current status
        """
        if not self.api_key:
            logger.warning("No PEPPOL AP key configured, simulating status")
            return self._simulate_status(reference)
        
        try:
            response = self.httpx.get(
                f'{self.api_url}/documents/{reference}/status',
                headers=self._get_headers(),
                timeout=30.0,
            )
            
            if response.status_code == 200:
                result = response.json()
                return APStatusResult(
                    status=result.get('status', 'pending'),
                    delivery_timestamp=result.get('deliveredAt'),
                    acknowledgments=result.get('acknowledgments', []),
                )
            else:
                return APStatusResult(status='unknown')
                
        except Exception as e:
            logger.error(f"Zetta AP status error: {e}")
            return APStatusResult(status='error')
    
    def get_acknowledgments(self, reference: str) -> list:
        """
        Get acknowledgments (MDN, application responses) for a document.
        
        Args:
            reference: Submission reference
            
        Returns:
            List of acknowledgment dictionaries
        """
        if not self.api_key:
            return self._simulate_acknowledgments(reference)
        
        try:
            response = self.httpx.get(
                f'{self.api_url}/documents/{reference}/acknowledgments',
                headers=self._get_headers(),
                timeout=30.0,
            )
            
            if response.status_code == 200:
                return response.json().get('acknowledgments', [])
            return []
            
        except Exception as e:
            logger.error(f"Zetta AP acknowledgment error: {e}")
            return []
    
    # =========================================================================
    # Simulation methods for testing without API key
    # =========================================================================
    
    def _simulate_submission(self, document_id: str) -> APSubmissionResult:
        """Simulate successful submission for testing."""
        import uuid
        
        logger.info(f"[SIMULATED] Document {document_id} submitted to Zetta AP")
        
        return APSubmissionResult(
            success=True,
            reference=f"ZETTA-{uuid.uuid4().hex[:12].upper()}",
            message_id=f"MSG-{uuid.uuid4().hex[:8].upper()}",
            raw_response={
                'status': 'accepted',
                'simulation': True,
            },
        )
    
    def _simulate_status(self, reference: str) -> APStatusResult:
        """Simulate status check for testing."""
        from datetime import datetime
        
        logger.info(f"[SIMULATED] Status check for {reference}")
        
        return APStatusResult(
            status='delivered',
            delivery_timestamp=datetime.now().isoformat(),
            acknowledgments=[
                {
                    'type': 'delivery',
                    'code': 'AP',
                    'timestamp': datetime.now().isoformat(),
                }
            ],
        )
    
    def _simulate_acknowledgments(self, reference: str) -> list:
        """Simulate acknowledgments for testing."""
        from datetime import datetime
        
        logger.info(f"[SIMULATED] Acknowledgments for {reference}")
        
        return [
            {
                'type': 'delivery',
                'responseCode': 'AP',
                'description': 'Document delivered successfully',
                'receivedAt': datetime.now().isoformat(),
            },
        ]
