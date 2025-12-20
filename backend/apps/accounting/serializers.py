"""
DRF serializers for accounting domain.
"""
from decimal import Decimal
from rest_framework import serializers

from apps.accounting.models import (
    Account, JournalEntry, JournalLine, Invoice, Payment,
    ACCOUNT_TYPE_CHOICES, ENTRY_STATUS_CHOICES,
    INVOICE_STATUS_CHOICES, PAYMENT_STATUS_CHOICES,
)


# =============================================================================
# ACCOUNT SERIALIZERS
# =============================================================================

class AccountSerializer(serializers.ModelSerializer):
    """Full serializer for Account CRUD."""
    
    is_debit_normal = serializers.BooleanField(read_only=True)
    full_code = serializers.CharField(read_only=True)
    
    class Meta:
        model = Account
        fields = [
            'id', 'code', 'name', 'description',
            'account_type', 'account_subtype', 'gst_code',
            'parent', 'is_active', 'is_system',
            'current_balance', 'is_debit_normal', 'full_code',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'current_balance', 'created_at', 'updated_at']


class AccountListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for account lists."""
    
    class Meta:
        model = Account
        fields = ['id', 'code', 'name', 'account_type', 'current_balance', 'is_active']


class AccountTreeSerializer(serializers.ModelSerializer):
    """Serializer for hierarchical account tree."""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'code', 'name', 'account_type',
            'current_balance', 'is_active', 'children',
        ]
    
    def get_children(self, obj):
        """Get nested children."""
        children = obj.children.filter(is_active=True)
        return AccountTreeSerializer(children, many=True).data


# =============================================================================
# JOURNAL ENTRY SERIALIZERS
# =============================================================================

class JournalLineSerializer(serializers.ModelSerializer):
    """Serializer for journal entry lines."""
    
    account_code = serializers.CharField(source='account.code', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    is_debit = serializers.BooleanField(read_only=True)
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = JournalLine
        fields = [
            'id', 'account', 'account_code', 'account_name',
            'debit_amount', 'credit_amount',
            'is_debit', 'amount',
            'gst_amount', 'gst_code', 'description',
        ]
        read_only_fields = ['id']


class JournalEntrySerializer(serializers.ModelSerializer):
    """Full serializer for JournalEntry with lines."""
    
    lines = JournalLineSerializer(many=True, read_only=True)
    is_balanced = serializers.BooleanField(read_only=True)
    can_edit = serializers.BooleanField(read_only=True)
    created_by_email = serializers.CharField(
        source='created_by.email', read_only=True
    )
    
    class Meta:
        model = JournalEntry
        fields = [
            'id', 'entry_number', 'entry_date', 'description',
            'reference_type', 'reference_id',
            'status', 'posted_at',
            'total_debit', 'total_credit', 'is_balanced',
            'can_edit', 'created_by', 'created_by_email',
            'approved_by', 'lines',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'entry_number', 'status', 'posted_at',
            'total_debit', 'total_credit',
            'created_at', 'updated_at',
        ]


class JournalLineCreateSerializer(serializers.Serializer):
    """Serializer for creating journal lines."""
    
    account_id = serializers.UUIDField()
    debit_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00')
    )
    credit_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00')
    )
    description = serializers.CharField(required=False, default='')
    gst_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, default=Decimal('0.00')
    )
    gst_code = serializers.CharField(required=False, default='')


class JournalEntryCreateSerializer(serializers.Serializer):
    """Serializer for creating journal entries with lines."""
    
    entry_date = serializers.DateField()
    description = serializers.CharField(required=False, default='')
    reference_type = serializers.CharField(required=False, default='')
    reference_id = serializers.UUIDField(required=False, allow_null=True)
    lines = JournalLineCreateSerializer(many=True)
    
    def validate_lines(self, value):
        """Validate that lines are balanced."""
        if not value:
            raise serializers.ValidationError("At least one line is required")
        
        total_debit = sum(
            Decimal(str(line.get('debit_amount', 0)))
            for line in value
        )
        total_credit = sum(
            Decimal(str(line.get('credit_amount', 0)))
            for line in value
        )
        
        if total_debit != total_credit:
            raise serializers.ValidationError(
                f"Entry is not balanced: debit={total_debit}, credit={total_credit}"
            )
        
        return value


# =============================================================================
# INVOICE SERIALIZERS
# =============================================================================

class InvoiceSerializer(serializers.ModelSerializer):
    """Full serializer for Invoice."""
    
    amount_due = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    customer_name = serializers.CharField(
        source='customer.name', read_only=True
    )
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_date', 'due_date',
            'customer', 'customer_name', 'order_id',
            'status', 'subtotal', 'gst_amount', 'total_amount',
            'amount_paid', 'amount_due', 'is_paid', 'is_overdue',
            'peppol_id', 'peppol_status', 'peppol_submitted_at',
            'notes', 'terms',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'invoice_number', 'amount_paid',
            'peppol_id', 'peppol_status', 'peppol_submitted_at',
            'created_at', 'updated_at',
        ]


class InvoiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for invoice lists."""
    
    amount_due = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    customer_name = serializers.CharField(
        source='customer.name', read_only=True
    )
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_date', 'due_date',
            'customer_name', 'status', 'total_amount', 'amount_due',
        ]


# =============================================================================
# PAYMENT SERIALIZERS
# =============================================================================

class PaymentSerializer(serializers.ModelSerializer):
    """Full serializer for Payment."""
    
    net_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    is_completed = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_number', 'payment_date',
            'amount', 'currency', 'payment_method',
            'gateway', 'gateway_reference', 'status',
            'reference_type', 'reference_id',
            'refund_amount', 'net_amount', 'is_completed',
            'failed_reason', 'metadata',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'payment_number', 'status',
            'refund_amount', 'refunded_at', 'completed_at',
            'created_at', 'updated_at',
        ]


class PaymentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for payment lists."""
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_number', 'payment_date',
            'amount', 'payment_method', 'status',
        ]


# =============================================================================
# GST F5 SERIALIZERS
# =============================================================================

class GSTF5Serializer(serializers.Serializer):
    """Serializer for GST F5 return data."""
    
    company_id = serializers.UUIDField()
    year = serializers.IntegerField()
    quarter = serializers.IntegerField(min_value=1, max_value=4)
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    
    # F5 Box values
    box_1 = serializers.DecimalField(max_digits=12, decimal_places=2)
    box_2 = serializers.DecimalField(max_digits=12, decimal_places=2)
    box_3 = serializers.DecimalField(max_digits=12, decimal_places=2)
    box_4 = serializers.DecimalField(max_digits=12, decimal_places=2)
    box_5 = serializers.DecimalField(max_digits=12, decimal_places=2)
    box_6 = serializers.DecimalField(max_digits=12, decimal_places=2)
    box_7 = serializers.DecimalField(max_digits=12, decimal_places=2)
    box_8 = serializers.DecimalField(max_digits=12, decimal_places=2)


class GSTF5PrepareRequestSerializer(serializers.Serializer):
    """Serializer for F5 preparation request."""
    
    quarter = serializers.IntegerField(min_value=1, max_value=4)
    year = serializers.IntegerField()


# =============================================================================
# REPORT SERIALIZERS
# =============================================================================

class TrialBalanceLineSerializer(serializers.Serializer):
    """Serializer for trial balance line item."""
    
    account_id = serializers.UUIDField(allow_null=True)
    account_code = serializers.CharField()
    account_name = serializers.CharField()
    account_type = serializers.CharField()
    debit = serializers.DecimalField(max_digits=15, decimal_places=2)
    credit = serializers.DecimalField(max_digits=15, decimal_places=2)


class AgingSummarySerializer(serializers.Serializer):
    """Serializer for accounts receivable aging."""
    
    current = serializers.DecimalField(max_digits=15, decimal_places=2)
    days_1_30 = serializers.DecimalField(
        max_digits=15, decimal_places=2, source='1_30'
    )
    days_31_60 = serializers.DecimalField(
        max_digits=15, decimal_places=2, source='31_60'
    )
    days_61_90 = serializers.DecimalField(
        max_digits=15, decimal_places=2, source='61_90'
    )
    days_90_plus = serializers.DecimalField(
        max_digits=15, decimal_places=2, source='90_plus'
    )
    total = serializers.DecimalField(max_digits=15, decimal_places=2)
