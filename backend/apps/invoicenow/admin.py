"""InvoiceNow admin."""
from django.contrib import admin
from django.utils.html import format_html

from apps.invoicenow.models import PEPPOLInvoice, PEPPOLAcknowledgment


@admin.register(PEPPOLInvoice)
class PEPPOLInvoiceAdmin(admin.ModelAdmin):
    """Admin for PEPPOL invoices."""
    
    list_display = [
        'peppol_id', 'invoice', 'status_badge',
        'submitted_at', 'created_at',
    ]
    list_filter = ['status', 'access_point_provider']
    search_fields = ['peppol_id', 'invoice__invoice_number']
    readonly_fields = [
        'id', 'peppol_id', 'xml_document', 'signature_value',
        'signature_timestamp', 'submitted_at', 'created_at', 'updated_at',
    ]
    fieldsets = [
        ('Invoice', {
            'fields': ('invoice', 'peppol_id', 'status')
        }),
        ('Endpoints', {
            'fields': ('sender_endpoint', 'receiver_endpoint')
        }),
        ('Submission', {
            'fields': ('access_point_provider', 'submission_reference', 'submitted_at')
        }),
        ('Validation', {
            'fields': ('validation_errors',)
        }),
        ('Document', {
            'fields': ('xml_document',),
            'classes': ('collapse',)
        }),
        ('Signature', {
            'fields': ('signature_value', 'signature_timestamp'),
            'classes': ('collapse',)
        }),
    ]
    
    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'validated': '#17a2b8',
            'signed': '#007bff',
            'submitted': '#ffc107',
            'acknowledged': '#28a745',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="padding: 3px 8px; border-radius: 3px; '
            'background: {}; color: white;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(PEPPOLAcknowledgment)
class PEPPOLAcknowledgmentAdmin(admin.ModelAdmin):
    """Admin for PEPPOL acknowledgments."""
    
    list_display = [
        'peppol_invoice', 'acknowledgment_type',
        'response_code', 'received_at',
    ]
    list_filter = ['acknowledgment_type', 'response_code']
    readonly_fields = [
        'id', 'peppol_invoice', 'acknowledgment_type',
        'message_id', 'response_code', 'response_description',
        'response_payload', 'received_at',
    ]
