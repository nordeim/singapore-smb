"""
Django Admin configuration for accounting app.
"""
from django.contrib import admin
from django.utils.html import format_html

from apps.accounting.models import Account, JournalEntry, JournalLine, Invoice, Payment


# =============================================================================
# INLINE ADMINS
# =============================================================================

class JournalLineInline(admin.TabularInline):
    """Inline for journal entry lines."""
    model = JournalLine
    extra = 0
    fields = ['account', 'debit_amount', 'credit_amount', 'gst_code', 'description']
    readonly_fields = ['created_at']
    
    def has_change_permission(self, request, obj=None):
        """Only allow changes for draft entries."""
        if obj and obj.status != 'draft':
            return False
        return super().has_change_permission(request, obj)


# =============================================================================
# MODEL ADMINS
# =============================================================================

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Admin for Chart of Accounts."""
    
    list_display = [
        'code', 'name', 'account_type', 'account_subtype',
        'balance_display', 'is_active', 'is_system',
    ]
    list_filter = ['account_type', 'is_active', 'is_system', 'company']
    search_fields = ['code', 'name']
    ordering = ['code']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('company', 'code', 'name', 'description', 'parent')
        }),
        ('Classification', {
            'fields': ('account_type', 'account_subtype', 'gst_code')
        }),
        ('Status', {
            'fields': ('is_active', 'is_system', 'current_balance')
        }),
    )
    
    readonly_fields = ['current_balance']
    
    def balance_display(self, obj):
        """Display balance with color coding."""
        balance = obj.current_balance
        if balance > 0:
            color = 'green'
        elif balance < 0:
            color = 'red'
        else:
            color = 'gray'
        return format_html(
            '<span style="color: {}">${:,.2f}</span>',
            color, balance
        )
    balance_display.short_description = 'Balance'
    balance_display.admin_order_field = 'current_balance'


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    """Admin for Journal Entries."""
    
    list_display = [
        'entry_number', 'entry_date', 'description',
        'status_display', 'total_debit', 'total_credit',
    ]
    list_filter = ['status', 'reference_type', 'company']
    search_fields = ['entry_number', 'description']
    date_hierarchy = 'entry_date'
    ordering = ['-entry_date', '-created_at']
    
    inlines = [JournalLineInline]
    
    fieldsets = (
        ('Entry Information', {
            'fields': ('company', 'entry_number', 'entry_date', 'description')
        }),
        ('Reference', {
            'fields': ('reference_type', 'reference_id')
        }),
        ('Status', {
            'fields': ('status', 'posted_at')
        }),
        ('Totals', {
            'fields': ('total_debit', 'total_credit')
        }),
        ('Audit', {
            'fields': ('created_by', 'approved_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['entry_number', 'total_debit', 'total_credit', 'posted_at']
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'draft': 'orange',
            'posted': 'green',
            'voided': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def has_change_permission(self, request, obj=None):
        """Only allow changes for draft entries."""
        if obj and obj.status != 'draft':
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Only allow deletion of draft entries."""
        if obj and obj.status != 'draft':
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin for Invoices."""
    
    list_display = [
        'invoice_number', 'customer', 'invoice_date', 'due_date',
        'status_display', 'total_amount', 'amount_due_display',
    ]
    list_filter = ['status', 'company']
    search_fields = ['invoice_number', 'customer__name']
    date_hierarchy = 'invoice_date'
    ordering = ['-invoice_date']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('company', 'invoice_number', 'customer', 'order_id')
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'gst_amount', 'total_amount', 'amount_paid')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('PEPPOL', {
            'fields': ('peppol_id', 'peppol_status', 'peppol_submitted_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes', 'terms'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['invoice_number', 'amount_paid']
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'draft': 'gray',
            'sent': 'blue',
            'paid': 'green',
            'overdue': 'red',
            'void': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def amount_due_display(self, obj):
        """Display amount due with color coding."""
        amount = obj.amount_due
        if amount > 0 and obj.is_overdue:
            color = 'red'
        elif amount > 0:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {}">${:,.2f}</span>',
            color, amount
        )
    amount_due_display.short_description = 'Amount Due'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payments."""
    
    list_display = [
        'payment_number', 'payment_date', 'amount',
        'payment_method', 'status_display', 'gateway',
    ]
    list_filter = ['status', 'payment_method', 'gateway', 'company']
    search_fields = ['payment_number', 'gateway_reference']
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('company', 'payment_number', 'payment_date', 'amount', 'currency')
        }),
        ('Method', {
            'fields': ('payment_method', 'gateway', 'gateway_reference')
        }),
        ('Status', {
            'fields': ('status', 'failed_reason')
        }),
        ('Reference', {
            'fields': ('reference_type', 'reference_id')
        }),
        ('Refund', {
            'fields': ('refund_amount', 'refunded_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['payment_number', 'status', 'refund_amount', 'refunded_at']
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'pending': 'orange',
            'completed': 'green',
            'failed': 'red',
            'refunded': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def has_change_permission(self, request, obj=None):
        """Only allow changes for pending payments."""
        if obj and obj.status != 'pending':
            return False
        return super().has_change_permission(request, obj)
