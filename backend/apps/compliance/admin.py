"""
Compliance Django admin configuration.
"""
from django.contrib import admin
from django.utils.html import format_html

from apps.compliance.models import GSTReturn, DataConsent, DataAccessRequest, AuditLog


@admin.register(GSTReturn)
class GSTReturnAdmin(admin.ModelAdmin):
    """Admin for GST F5 returns."""
    
    list_display = [
        'company', 'quarter', 'year', 'status_badge',
        'box_8', 'submission_date',
    ]
    list_filter = ['status', 'year', 'quarter']
    search_fields = ['company__name', 'iras_reference']
    readonly_fields = [
        'id', 'box_4', 'box_8', 'created_at', 'updated_at',
    ]
    fieldsets = [
        ('Period', {
            'fields': ('company', 'quarter', 'year', 'period_start', 'period_end')
        }),
        ('Supplies (Box 1-3)', {
            'fields': ('box_1', 'box_2', 'box_3', 'box_4')
        }),
        ('Tax (Box 5-8)', {
            'fields': ('box_5', 'box_6', 'box_7', 'box_8')
        }),
        ('Status', {
            'fields': ('status', 'submission_date', 'iras_reference')
        }),
        ('Audit', {
            'fields': ('prepared_by', 'submitted_by', 'created_at', 'updated_at')
        }),
    ]
    
    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'validated': '#17a2b8',
            'submitted': '#ffc107',
            'accepted': '#28a745',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="padding: 3px 8px; border-radius: 3px; '
            'background: {}; color: white;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(DataConsent)
class DataConsentAdmin(admin.ModelAdmin):
    """Read-only admin for consent records."""
    
    list_display = [
        'customer', 'consent_type', 'is_granted',
        'source', 'consent_timestamp',
    ]
    list_filter = ['consent_type', 'is_granted', 'source']
    search_fields = ['customer__email']
    readonly_fields = [
        'id', 'customer', 'consent_type', 'is_granted',
        'source', 'ip_address', 'user_agent',
        'consent_timestamp', 'created_at',
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DataAccessRequest)
class DataAccessRequestAdmin(admin.ModelAdmin):
    """Admin for PDPA data access requests."""
    
    list_display = [
        'customer', 'request_type', 'status', 'sla_badge',
        'due_date', 'completed_at',
    ]
    list_filter = ['status', 'request_type']
    search_fields = ['customer__email']
    readonly_fields = [
        'id', 'due_date', 'created_at', 'updated_at',
    ]
    fieldsets = [
        ('Request', {
            'fields': ('company', 'customer', 'request_type', 'status')
        }),
        ('Timeline', {
            'fields': ('requested_at', 'due_date', 'completed_at')
        }),
        ('Response', {
            'fields': ('response_notes', 'processed_by')
        }),
    ]
    
    def sla_badge(self, obj):
        colors = {
            'completed': '#28a745',
            'on_track': '#28a745',
            'at_risk': '#ffc107',
            'overdue': '#dc3545',
        }
        status = obj.sla_status
        color = colors.get(status, '#6c757d')
        label = f"{obj.days_until_due}d" if status != 'completed' else 'Done'
        return format_html(
            '<span style="padding: 3px 8px; border-radius: 3px; '
            'background: {}; color: white;">{}</span>',
            color, label
        )
    sla_badge.short_description = 'SLA'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Read-only admin for audit logs."""
    
    list_display = [
        'created_at', 'user', 'action',
        'resource_type', 'resource_id',
    ]
    list_filter = ['action', 'resource_type', 'created_at']
    search_fields = ['user__email', 'resource_type']
    readonly_fields = [
        'id', 'company', 'user', 'action',
        'resource_type', 'resource_id',
        'old_values', 'new_values',
        'ip_address', 'user_agent', 'created_at',
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
