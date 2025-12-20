"""InvoiceNow serializers."""
from rest_framework import serializers

from apps.invoicenow.models import PEPPOLInvoice, PEPPOLAcknowledgment


class PEPPOLInvoiceSerializer(serializers.ModelSerializer):
    """PEPPOL invoice serializer."""
    
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PEPPOLInvoice
        fields = [
            'id', 'invoice', 'invoice_number', 'customer_name',
            'peppol_id', 'sender_endpoint', 'receiver_endpoint',
            'status', 'access_point_provider', 'submission_reference',
            'submitted_at', 'validation_errors',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'peppol_id', 'status', 'submitted_at',
            'validation_errors', 'created_at', 'updated_at',
        ]
    
    def get_customer_name(self, obj):
        customer = obj.invoice.customer
        return customer.company_name or f"{customer.first_name} {customer.last_name}"


class PEPPOLInvoiceListSerializer(serializers.ModelSerializer):
    """Summary serializer for listings."""
    
    invoice_number = serializers.CharField(source='invoice.invoice_number')
    amount = serializers.DecimalField(
        source='invoice.total_amount',
        max_digits=12,
        decimal_places=2
    )
    
    class Meta:
        model = PEPPOLInvoice
        fields = [
            'id', 'peppol_id', 'invoice_number', 'amount',
            'status', 'submitted_at',
        ]


class PEPPOLAcknowledgmentSerializer(serializers.ModelSerializer):
    """Acknowledgment serializer."""
    
    class Meta:
        model = PEPPOLAcknowledgment
        fields = [
            'id', 'peppol_invoice', 'acknowledgment_type',
            'message_id', 'response_code', 'response_description',
            'received_at',
        ]


class PrepareInvoiceSerializer(serializers.Serializer):
    """Serializer for prepare request."""
    
    invoice_id = serializers.UUIDField()


class SubmissionStatusSerializer(serializers.Serializer):
    """Serializer for submission status response."""
    
    exists = serializers.BooleanField()
    status = serializers.CharField(allow_null=True)
    peppol_id = serializers.CharField(allow_null=True)
    submitted_at = serializers.CharField(allow_null=True)
    acknowledgments = serializers.ListField(required=False)
