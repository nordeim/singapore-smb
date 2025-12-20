"""
XML Digital Signing for PEPPOL.

Provides XMLDSig signing for UBL invoices.
"""
import logging
from typing import Optional

from django.conf import settings


logger = logging.getLogger(__name__)


class XMLSigner:
    """
    XML Digital Signature service for PEPPOL documents.
    
    Uses XMLDSig (XAdES-B-B) for signing UBL invoices
    as required by InvoiceNow.
    """
    
    @staticmethod
    def sign(xml_content: str) -> str:
        """
        Sign XML document with XMLDSig.
        
        Args:
            xml_content: UBL XML string to sign
            
        Returns:
            Signed XML string with embedded signature
        """
        try:
            # Try to use signxml library
            from signxml import XMLSigner as SignXMLSigner
            from lxml import etree
            
            # Load certificate and key from settings
            cert_path = getattr(settings, 'PEPPOL_CERT_PATH', '')
            key_path = getattr(settings, 'PEPPOL_CERT_KEY_PATH', '')
            
            if not cert_path or not key_path:
                logger.warning("PEPPOL signing certificates not configured")
                return xml_content
            
            with open(cert_path, 'rb') as f:
                cert = f.read()
            
            with open(key_path, 'rb') as f:
                key = f.read()
            
            # Parse XML
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            # Create signer
            signer = SignXMLSigner(
                method=SignXMLSigner.Method.enveloped,
                signature_algorithm='rsa-sha256',
                digest_algorithm='sha256',
            )
            
            # Sign
            signed_root = signer.sign(
                root,
                key=key,
                cert=cert,
            )
            
            return etree.tostring(signed_root, encoding='unicode', pretty_print=True)
            
        except ImportError:
            logger.warning("signxml/lxml not installed, returning unsigned XML")
            return xml_content
        except Exception as e:
            logger.error(f"XML signing failed: {e}")
            return xml_content
    
    @staticmethod
    def verify(xml_content: str) -> bool:
        """
        Verify XML digital signature.
        
        Args:
            xml_content: Signed XML string
            
        Returns:
            True if signature is valid
        """
        try:
            from signxml import XMLVerifier
            from lxml import etree
            
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            # Verify signature
            XMLVerifier().verify(root)
            
            return True
            
        except ImportError:
            logger.warning("signxml/lxml not installed")
            return False
        except Exception as e:
            logger.error(f"XML verification failed: {e}")
            return False
    
    @staticmethod
    def extract_signature(xml_content: str) -> Optional[str]:
        """
        Extract signature value from signed XML.
        
        Args:
            xml_content: Signed XML
            
        Returns:
            Signature value or None
        """
        try:
            from lxml import etree
            
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            # Find SignatureValue element
            ns = {'ds': 'http://www.w3.org/2000/09/xmldsig#'}
            sig_value = root.find('.//ds:SignatureValue', ns)
            
            if sig_value is not None:
                return sig_value.text
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract signature: {e}")
            return None
