"""
DRF ViewSets for accounting domain.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsCompanyMember

from apps.accounting.models import Account, JournalEntry, Invoice, Payment
from apps.accounting.serializers import (
    AccountSerializer, AccountListSerializer, AccountTreeSerializer,
    JournalEntrySerializer, JournalEntryCreateSerializer,
    InvoiceSerializer, InvoiceListSerializer,
    PaymentSerializer, PaymentListSerializer,
    GSTF5Serializer, GSTF5PrepareRequestSerializer,
    TrialBalanceLineSerializer, AgingSummarySerializer,
)
from apps.accounting.services import LedgerService, InvoiceService, PaymentService
from apps.accounting.gst import GSTEngine


class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Chart of Accounts.
    
    Endpoints:
    - GET /accounts/ - List accounts
    - POST /accounts/ - Create account
    - GET /accounts/{id}/ - Retrieve account
    - PUT /accounts/{id}/ - Update account
    - DELETE /accounts/{id}/ - Delete account
    - GET /accounts/tree/ - Get hierarchical tree
    """
    
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['account_type', 'is_active', 'is_system']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name', 'account_type', 'current_balance']
    ordering = ['code']
    
    def get_queryset(self):
        """Filter to current company."""
        return Account.objects.filter(
            company=self.request.user.company
        ).select_related('parent')
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return AccountListSerializer
        if self.action == 'tree':
            return AccountTreeSerializer
        return AccountSerializer
    
    def perform_create(self, serializer):
        """Set company on create."""
        serializer.save(company=self.request.user.company)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get hierarchical account tree."""
        # Get root accounts (no parent)
        roots = self.get_queryset().filter(
            parent__isnull=True, is_active=True
        )
        serializer = AccountTreeSerializer(roots, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def balances(self, request):
        """Get account balances summary."""
        accounts = self.get_queryset().filter(is_active=True)
        
        summary = {
            'asset': sum(a.current_balance for a in accounts if a.account_type == 'asset'),
            'liability': sum(a.current_balance for a in accounts if a.account_type == 'liability'),
            'equity': sum(a.current_balance for a in accounts if a.account_type == 'equity'),
            'revenue': sum(a.current_balance for a in accounts if a.account_type == 'revenue'),
            'expense': sum(a.current_balance for a in accounts if a.account_type == 'expense'),
        }
        
        return Response(summary)


class JournalEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Journal Entries.
    
    Endpoints:
    - GET /journals/ - List entries
    - POST /journals/ - Create entry with lines
    - GET /journals/{id}/ - Retrieve entry
    - POST /journals/{id}/post/ - Post draft entry
    - POST /journals/{id}/void/ - Void posted entry
    """
    
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'reference_type']
    ordering_fields = ['entry_date', 'entry_number', 'created_at']
    ordering = ['-entry_date', '-created_at']
    http_method_names = ['get', 'post', 'head', 'options']  # No PUT/DELETE
    
    def get_queryset(self):
        """Filter to current company."""
        return JournalEntry.objects.filter(
            company=self.request.user.company
        ).prefetch_related('lines', 'lines__account')
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'create':
            return JournalEntryCreateSerializer
        return JournalEntrySerializer
    
    def create(self, request, *args, **kwargs):
        """Create journal entry with lines."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            entry = LedgerService.create_journal_entry(
                company=request.user.company,
                entry_date=serializer.validated_data['entry_date'],
                lines=serializer.validated_data['lines'],
                description=serializer.validated_data.get('description', ''),
                reference_type=serializer.validated_data.get('reference_type', ''),
                reference_id=serializer.validated_data.get('reference_id'),
                created_by=request.user,
            )
            
            return Response(
                JournalEntrySerializer(entry).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def post(self, request, pk=None):
        """Post a draft journal entry."""
        entry = self.get_object()
        
        try:
            LedgerService.post_entry(entry, approved_by=request.user)
            return Response(JournalEntrySerializer(entry).data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def void(self, request, pk=None):
        """Void a posted journal entry."""
        entry = self.get_object()
        
        try:
            LedgerService.void_entry(entry)
            return Response(JournalEntrySerializer(entry).data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Invoices.
    
    Endpoints:
    - GET /invoices/ - List invoices
    - POST /invoices/ - Create invoice
    - GET /invoices/{id}/ - Retrieve invoice
    - PUT /invoices/{id}/ - Update invoice
    - POST /invoices/{id}/send/ - Mark as sent
    - POST /invoices/{id}/void/ - Void invoice
    - GET /invoices/aging/ - Aging summary
    """
    
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'customer']
    search_fields = ['invoice_number']
    ordering_fields = ['invoice_date', 'due_date', 'total_amount']
    ordering = ['-invoice_date']
    
    def get_queryset(self):
        """Filter to current company."""
        return Invoice.objects.filter(
            company=self.request.user.company
        ).select_related('customer')
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer
    
    def perform_create(self, serializer):
        """Set company and generate number on create."""
        company = self.request.user.company
        invoice_number = Invoice.generate_invoice_number(company)
        serializer.save(company=company, invoice_number=invoice_number)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Mark invoice as sent."""
        invoice = self.get_object()
        InvoiceService.mark_sent(invoice)
        return Response(InvoiceSerializer(invoice).data)
    
    @action(detail=True, methods=['post'])
    def void(self, request, pk=None):
        """Void invoice."""
        invoice = self.get_object()
        
        try:
            InvoiceService.void(invoice)
            return Response(InvoiceSerializer(invoice).data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def aging(self, request):
        """Get accounts receivable aging summary."""
        company = request.user.company
        aging = InvoiceService.get_aging_summary(company)
        serializer = AgingSummarySerializer(aging)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Payments.
    
    Endpoints:
    - GET /payments/ - List payments
    - POST /payments/ - Record payment
    - GET /payments/{id}/ - Retrieve payment
    - POST /payments/{id}/complete/ - Complete payment
    - POST /payments/{id}/refund/ - Refund payment
    """
    
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'gateway']
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-payment_date']
    http_method_names = ['get', 'post', 'head', 'options']  # No PUT/DELETE
    
    def get_queryset(self):
        """Filter to current company."""
        return Payment.objects.filter(
            company=self.request.user.company
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return PaymentListSerializer
        return PaymentSerializer
    
    def perform_create(self, serializer):
        """Set company and generate number on create."""
        company = self.request.user.company
        payment_number = Payment.generate_payment_number(company)
        serializer.save(company=company, payment_number=payment_number)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a pending payment."""
        payment = self.get_object()
        
        try:
            PaymentService.complete_payment(payment)
            return Response(PaymentSerializer(payment).data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Refund a completed payment."""
        from decimal import Decimal
        
        payment = self.get_object()
        amount = request.data.get('amount')
        
        # Convert to Decimal if provided
        if amount is not None:
            amount = Decimal(str(amount))
        
        try:
            PaymentService.refund_payment(
                payment,
                amount=amount
            )
            return Response(PaymentSerializer(payment).data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class GSTF5ViewSet(viewsets.ViewSet):
    """
    ViewSet for GST F5 operations.
    
    Endpoints:
    - POST /gst/f5/prepare/ - Prepare F5 return data
    - POST /gst/f5/validate/ - Validate F5 return
    """
    
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    @action(detail=False, methods=['post'])
    def prepare(self, request):
        """Prepare GST F5 return data for a quarter."""
        serializer = GSTF5PrepareRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        company = request.user.company
        quarter = serializer.validated_data['quarter']
        year = serializer.validated_data['year']
        
        f5_return = GSTEngine.prepare_f5(company, quarter, year)
        
        return Response(f5_return.to_dict())
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Validate GST F5 return data."""
        serializer = GSTF5Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from apps.accounting.gst.engine import F5Return
        from datetime import date
        
        f5_return = F5Return(
            company_id=str(serializer.validated_data['company_id']),
            year=serializer.validated_data['year'],
            quarter=serializer.validated_data['quarter'],
            period_start=serializer.validated_data['period_start'],
            period_end=serializer.validated_data['period_end'],
            box_1=serializer.validated_data['box_1'],
            box_2=serializer.validated_data['box_2'],
            box_3=serializer.validated_data['box_3'],
            box_4=serializer.validated_data['box_4'],
            box_5=serializer.validated_data['box_5'],
            box_6=serializer.validated_data['box_6'],
            box_7=serializer.validated_data['box_7'],
            box_8=serializer.validated_data['box_8'],
        )
        
        is_valid, errors = GSTEngine.validate_f5(f5_return)
        
        return Response({
            'is_valid': is_valid,
            'errors': errors,
        })


class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet for accounting reports.
    
    Endpoints:
    - GET /reports/trial-balance/ - Trial balance
    """
    
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    @action(detail=False, methods=['get'], url_path='trial-balance')
    def trial_balance(self, request):
        """Generate trial balance report."""
        company = request.user.company
        as_of_date = request.query_params.get('as_of_date')
        
        if as_of_date:
            from datetime import datetime
            as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
        
        trial_balance = LedgerService.get_trial_balance(company, as_of_date)
        serializer = TrialBalanceLineSerializer(trial_balance, many=True)
        
        return Response(serializer.data)
