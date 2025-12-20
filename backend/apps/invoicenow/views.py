"""InvoiceNow API views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.invoicenow.models import PEPPOLInvoice, PEPPOLAcknowledgment
from apps.invoicenow.serializers import (
    PEPPOLInvoiceSerializer, PEPPOLInvoiceListSerializer,
    PEPPOLAcknowledgmentSerializer, PrepareInvoiceSerializer,
    SubmissionStatusSerializer,
)
from apps.invoicenow.services import PEPPOLService


class PEPPOLInvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for PEPPOL invoices.
    
    Endpoints:
    - GET /peppol-invoices/ - List PEPPOL invoices
    - GET /peppol-invoices/{id}/ - Get detail
    - POST /peppol-invoices/{id}/validate/ - Validate invoice
    - POST /peppol-invoices/{id}/sign/ - Sign invoice
    - POST /peppol-invoices/{id}/submit/ - Submit to AP
    """
    
    queryset = PEPPOLInvoice.objects.all()
    serializer_class = PEPPOLInvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PEPPOLInvoice.objects.filter(
            invoice__company=self.request.user.company
        ).select_related('invoice').order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PEPPOLInvoiceListSerializer
        return PEPPOLInvoiceSerializer
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate PEPPOL invoice."""
        peppol_invoice = self.get_object()
        
        is_valid, errors = PEPPOLService.validate_invoice(peppol_invoice)
        
        return Response({
            'is_valid': is_valid,
            'errors': errors,
        })
    
    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        """Sign PEPPOL invoice."""
        peppol_invoice = self.get_object()
        
        try:
            peppol_invoice = PEPPOLService.sign_invoice(peppol_invoice)
            return Response(PEPPOLInvoiceSerializer(peppol_invoice).data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit PEPPOL invoice to Access Point."""
        peppol_invoice = self.get_object()
        
        try:
            peppol_invoice = PEPPOLService.submit_invoice(peppol_invoice)
            return Response(PEPPOLInvoiceSerializer(peppol_invoice).data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PrepareInvoiceView(APIView):
    """Prepare an accounting invoice for PEPPOL."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PrepareInvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from apps.accounting.models import Invoice
        
        try:
            invoice = Invoice.objects.get(
                id=serializer.validated_data['invoice_id'],
                company=request.user.company,
            )
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        peppol_invoice = PEPPOLService.prepare_invoice(invoice)
        
        return Response(
            PEPPOLInvoiceSerializer(peppol_invoice).data,
            status=status.HTTP_201_CREATED
        )


class SubmissionStatusView(APIView):
    """Get PEPPOL submission status for an invoice."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, invoice_id):
        from apps.accounting.models import Invoice
        
        try:
            invoice = Invoice.objects.get(
                id=invoice_id,
                company=request.user.company,
            )
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        status_info = PEPPOLService.get_submission_status(invoice)
        
        return Response(status_info)


class FullWorkflowView(APIView):
    """Run full PEPPOL workflow: prepare, validate, sign, submit."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PrepareInvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from apps.accounting.models import Invoice
        
        try:
            invoice = Invoice.objects.get(
                id=serializer.validated_data['invoice_id'],
                company=request.user.company,
            )
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            peppol_invoice = PEPPOLService.process_full_workflow(invoice)
            return Response(PEPPOLInvoiceSerializer(peppol_invoice).data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
