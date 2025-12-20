"""
Compliance serializers.

Provides DRF serializers for:
- GSTReturn
- DataConsent (create-only)
- DataAccessRequest
- AuditLog (read-only)
"""
from rest_framework import serializers
from decimal import Decimal

from apps.compliance.models import GSTReturn, DataConsent, DataAccessRequest, AuditLog


class GSTReturnSerializer(serializers.ModelSerializer):
    """Full serializer for GST returns."""
    
    is_valid_boxes = serializers.SerializerMethodField()
    can_submit = serializers.SerializerMethodField()
    
    class Meta:
        model = GSTReturn
        fields = [
            'id', 'company', 'period_start', 'period_end',
            'quarter', 'year',
            'box_1', 'box_2', 'box_3', 'box_4',
            'box_5', 'box_6', 'box_7', 'box_8',
            'status', 'submission_date', 'iras_reference',
            'prepared_by', 'submitted_by',
            'created_at', 'updated_at',
            'is_valid_boxes', 'can_submit',
        ]
        read_only_fields = [
            'id', 'company', 'box_4', 'box_8',
            'status', 'submission_date', 'iras_reference',
            'prepared_by', 'submitted_by',
            'created_at', 'updated_at',
        ]
    
    def get_is_valid_boxes(self, obj) -> bool:
        is_valid, _ = obj.validate_boxes()
        return is_valid
    
    def get_can_submit(self, obj) -> bool:
        return obj.can_submit()


class GSTReturnListSerializer(serializers.ModelSerializer):
    """Summary serializer for GST return lists."""
    
    net_gst = serializers.DecimalField(source='box_8', max_digits=12, decimal_places=2)
    
    class Meta:
        model = GSTReturn
        fields = [
            'id', 'quarter', 'year', 'status',
            'net_gst', 'submission_date',
        ]


class GSTReturnCreateSerializer(serializers.Serializer):
    """Serializer for creating/preparing a GST return."""
    
    quarter = serializers.IntegerField(min_value=1, max_value=4)
    year = serializers.IntegerField(min_value=2020)


class GSTReturnValidateSerializer(serializers.Serializer):
    """Response serializer for validation results."""
    
    is_valid = serializers.BooleanField()
    errors = serializers.ListField(child=serializers.CharField())


class DataConsentSerializer(serializers.ModelSerializer):
    """Serializer for data consent records (read-only after create)."""
    
    class Meta:
        model = DataConsent
        fields = [
            'id', 'customer', 'consent_type', 'is_granted',
            'source', 'consent_timestamp', 'created_at',
        ]
        read_only_fields = ['id', 'consent_timestamp', 'created_at']


class DataConsentCreateSerializer(serializers.Serializer):
    """Serializer for recording consent."""
    
    consent_type = serializers.ChoiceField(choices=[
        'order_processing', 'marketing', 'analytics',
        'third_party', 'profiling', 'legal_compliance',
    ])
    is_granted = serializers.BooleanField()
    source = serializers.CharField(max_length=50, required=False, default='')


class ConsentSummarySerializer(serializers.Serializer):
    """Serializer for consent summary response."""
    
    marketing = serializers.DictField()
    analytics = serializers.DictField()
    order_processing = serializers.DictField()
    third_party = serializers.DictField()
    profiling = serializers.DictField()
    legal_compliance = serializers.DictField()


class DataAccessRequestSerializer(serializers.ModelSerializer):
    """Full serializer for data access requests."""
    
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)
    sla_status = serializers.CharField(read_only=True)
    
    class Meta:
        model = DataAccessRequest
        fields = [
            'id', 'company', 'customer', 'request_type',
            'status', 'requested_at', 'due_date', 'completed_at',
            'response_notes', 'processed_by',
            'created_at', 'updated_at',
            'is_overdue', 'days_until_due', 'sla_status',
        ]
        read_only_fields = [
            'id', 'company', 'due_date', 'completed_at',
            'status', 'processed_by', 'created_at', 'updated_at',
        ]


class DataAccessRequestCreateSerializer(serializers.Serializer):
    """Serializer for creating data access requests."""
    
    customer_id = serializers.UUIDField()
    request_type = serializers.ChoiceField(
        choices=['access', 'correction', 'deletion']
    )


class DataAccessRequestActionSerializer(serializers.Serializer):
    """Serializer for completing/rejecting data access requests."""
    
    action = serializers.ChoiceField(choices=['complete', 'reject'])
    notes = serializers.CharField(required=False, default='')


class CustomerDataExportSerializer(serializers.Serializer):
    """Serializer for PDPA data export response."""
    
    customer = serializers.DictField()
    consent = serializers.DictField()
    addresses = serializers.ListField()
    orders = serializers.ListField()


class AuditLogSerializer(serializers.ModelSerializer):
    """Read-only serializer for audit logs."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    change_summary = serializers.CharField(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'company', 'user', 'user_email',
            'action', 'resource_type', 'resource_id',
            'old_values', 'new_values', 'change_summary',
            'ip_address', 'created_at',
        ]
        read_only_fields = fields
