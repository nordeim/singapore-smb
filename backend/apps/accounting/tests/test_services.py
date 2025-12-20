"""
Tests for accounting services.
"""
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock

from django.db import transaction

from apps.accounting.services import LedgerService, InvoiceService, PaymentService
from apps.accounting.models import Account, JournalEntry, Invoice, Payment
from apps.accounting.tests.factories import (
    AccountFactory, AssetAccountFactory, LiabilityAccountFactory,
    RevenueAccountFactory,
    JournalEntryFactory,
    InvoiceFactory,
    PaymentFactory, CompletedPaymentFactory,
)
from apps.accounts.tests.factories import CompanyFactory


pytestmark = pytest.mark.django_db


class TestLedgerService:
    """Tests for LedgerService."""
    
    def test_create_journal_entry_balanced(self):
        """Test creating balanced journal entry."""
        company = CompanyFactory()
        debit_account = AssetAccountFactory(company=company, code='1100')
        credit_account = RevenueAccountFactory(company=company, code='4000')
        
        lines = [
            {
                'account_id': debit_account.id,
                'debit_amount': Decimal('100.00'),
                'credit_amount': Decimal('0.00'),
            },
            {
                'account_id': credit_account.id,
                'debit_amount': Decimal('0.00'),
                'credit_amount': Decimal('100.00'),
            },
        ]
        
        entry = LedgerService.create_journal_entry(
            company=company,
            entry_date=date.today(),
            lines=lines,
            description='Test entry',
        )
        
        assert entry.id is not None
        assert entry.status == 'draft'
        assert entry.total_debit == Decimal('100.00')
        assert entry.total_credit == Decimal('100.00')
        assert entry.lines.count() == 2
    
    def test_create_journal_entry_not_balanced(self):
        """Test creating unbalanced entry raises error."""
        company = CompanyFactory()
        account = AssetAccountFactory(company=company)
        
        lines = [
            {
                'account_id': account.id,
                'debit_amount': Decimal('100.00'),
                'credit_amount': Decimal('0.00'),
            },
        ]
        
        with pytest.raises(ValueError) as exc:
            LedgerService.create_journal_entry(
                company=company,
                entry_date=date.today(),
                lines=lines,
            )
        
        assert 'not balanced' in str(exc.value)
    
    def test_post_entry_updates_balances(self):
        """Test posting entry updates account balances."""
        company = CompanyFactory()
        debit_account = AssetAccountFactory(
            company=company, code='1100', current_balance=Decimal('0.00')
        )
        credit_account = RevenueAccountFactory(
            company=company, code='4000', current_balance=Decimal('0.00')
        )
        
        lines = [
            {
                'account_id': debit_account.id,
                'debit_amount': Decimal('100.00'),
                'credit_amount': Decimal('0.00'),
            },
            {
                'account_id': credit_account.id,
                'debit_amount': Decimal('0.00'),
                'credit_amount': Decimal('100.00'),
            },
        ]
        
        entry = LedgerService.create_journal_entry(
            company=company,
            entry_date=date.today(),
            lines=lines,
        )
        
        LedgerService.post_entry(entry)
        
        # Refresh from DB
        debit_account.refresh_from_db()
        credit_account.refresh_from_db()
        entry.refresh_from_db()
        
        assert entry.status == 'posted'
        assert debit_account.current_balance == Decimal('100.00')  # Debit increases asset
        assert credit_account.current_balance == Decimal('100.00')  # Credit increases revenue
    
    def test_void_entry_reverses_balances(self):
        """Test voiding entry reverses account balances."""
        company = CompanyFactory()
        debit_account = AssetAccountFactory(
            company=company, code='1100', current_balance=Decimal('100.00')
        )
        credit_account = RevenueAccountFactory(
            company=company, code='4000', current_balance=Decimal('100.00')
        )
        
        # Create and post entry
        lines = [
            {
                'account_id': debit_account.id,
                'debit_amount': Decimal('50.00'),
                'credit_amount': Decimal('0.00'),
            },
            {
                'account_id': credit_account.id,
                'debit_amount': Decimal('0.00'),
                'credit_amount': Decimal('50.00'),
            },
        ]
        
        entry = LedgerService.create_journal_entry(
            company=company,
            entry_date=date.today(),
            lines=lines,
        )
        LedgerService.post_entry(entry)
        
        # Verify balances after posting
        debit_account.refresh_from_db()
        credit_account.refresh_from_db()
        assert debit_account.current_balance == Decimal('150.00')
        assert credit_account.current_balance == Decimal('150.00')
        
        # Now void
        entry.refresh_from_db()
        LedgerService.void_entry(entry)
        
        debit_account.refresh_from_db()
        credit_account.refresh_from_db()
        entry.refresh_from_db()
        
        assert entry.status == 'voided'
        assert debit_account.current_balance == Decimal('100.00')  # Reversed
        assert credit_account.current_balance == Decimal('100.00')  # Reversed
    
    def test_get_trial_balance(self):
        """Test trial balance generation."""
        company = CompanyFactory()
        asset = AssetAccountFactory(
            company=company, code='1000', current_balance=Decimal('1000.00')
        )
        liability = LiabilityAccountFactory(
            company=company, code='2000', current_balance=Decimal('500.00')
        )
        revenue = RevenueAccountFactory(
            company=company, code='4000', current_balance=Decimal('500.00')
        )
        
        trial_balance = LedgerService.get_trial_balance(company)
        
        # Should have 3 accounts + 1 totals row
        assert len(trial_balance) == 4
        
        # Check totals row
        totals = trial_balance[-1]
        assert totals['account_name'] == 'TOTALS'
        assert totals['debit'] == Decimal('1000.00')
        assert totals['credit'] == Decimal('1000.00')  # 500 + 500


class TestInvoiceService:
    """Tests for InvoiceService."""
    
    def test_apply_payment(self):
        """Test applying payment to invoice."""
        invoice = InvoiceFactory(
            total_amount=Decimal('100.00'),
            amount_paid=Decimal('0.00'),
            status='sent'
        )
        
        InvoiceService.apply_payment(invoice, Decimal('50.00'))
        
        invoice.refresh_from_db()
        assert invoice.amount_paid == Decimal('50.00')
        assert invoice.amount_due == Decimal('50.00')
    
    def test_apply_payment_exceeds_due(self):
        """Test applying payment exceeding amount due raises error."""
        invoice = InvoiceFactory(
            total_amount=Decimal('100.00'),
            amount_paid=Decimal('0.00'),
        )
        
        with pytest.raises(ValueError) as exc:
            InvoiceService.apply_payment(invoice, Decimal('150.00'))
        
        assert 'exceeds' in str(exc.value)
    
    def test_mark_sent(self):
        """Test marking invoice as sent."""
        invoice = InvoiceFactory(status='draft')
        
        InvoiceService.mark_sent(invoice)
        
        invoice.refresh_from_db()
        assert invoice.status == 'sent'
    
    def test_check_overdue_invoices(self):
        """Test checking and updating overdue invoices."""
        company = CompanyFactory()
        
        from datetime import timedelta
        
        # Create sent invoice that's overdue
        overdue_invoice = InvoiceFactory(
            company=company,
            status='sent',
            due_date=date.today() - timedelta(days=7),  # 7 days ago
        )
        
        count = InvoiceService.check_overdue_invoices(company)
        
        overdue_invoice.refresh_from_db()
        assert overdue_invoice.status == 'overdue'
        assert count == 1
    
    def test_get_aging_summary(self):
        """Test aging summary generation."""
        company = CompanyFactory()
        
        from datetime import timedelta
        
        # Create invoices in different age buckets
        InvoiceFactory(
            company=company,
            status='sent',
            due_date=date.today() + timedelta(days=7),  # Current
            total_amount=Decimal('100.00'),
            amount_paid=Decimal('0.00'),
        )
        InvoiceFactory(
            company=company,
            status='sent',
            due_date=date.today() - timedelta(days=15),  # 1-30 days
            total_amount=Decimal('200.00'),
            amount_paid=Decimal('0.00'),
        )
        
        aging = InvoiceService.get_aging_summary(company)
        
        assert aging['current'] == Decimal('100.00')
        assert aging['1_30'] == Decimal('200.00')
        assert aging['total'] == Decimal('300.00')


class TestPaymentService:
    """Tests for PaymentService."""
    
    def test_record_payment(self):
        """Test recording a payment."""
        company = CompanyFactory()
        
        payment = PaymentService.record_payment(
            company=company,
            amount=Decimal('100.00'),
            payment_method='bank_transfer',
        )
        
        assert payment.id is not None
        assert payment.status == 'pending'
        assert payment.amount == Decimal('100.00')
    
    def test_complete_payment(self):
        """Test completing a payment."""
        payment = PaymentFactory(status='pending')
        
        PaymentService.complete_payment(payment)
        
        payment.refresh_from_db()
        assert payment.status == 'completed'
    
    def test_complete_payment_applies_to_invoice(self):
        """Test completing payment applies to linked invoice."""
        invoice = InvoiceFactory(
            total_amount=Decimal('100.00'),
            amount_paid=Decimal('0.00'),
            status='sent',
        )
        
        payment = PaymentFactory(
            company=invoice.company,
            amount=Decimal('100.00'),
            reference_type='invoice',
            reference_id=invoice.id,
            status='pending',
        )
        
        PaymentService.complete_payment(payment)
        
        invoice.refresh_from_db()
        payment.refresh_from_db()
        
        assert payment.status == 'completed'
        assert invoice.amount_paid == Decimal('100.00')
        assert invoice.status == 'paid'
    
    def test_fail_payment(self):
        """Test failing a payment."""
        payment = PaymentFactory(status='pending')
        
        PaymentService.fail_payment(payment, 'Card declined')
        
        payment.refresh_from_db()
        assert payment.status == 'failed'
        assert payment.failed_reason == 'Card declined'
    
    def test_refund_payment(self):
        """Test refunding a payment."""
        payment = CompletedPaymentFactory(amount=Decimal('100.00'))
        
        PaymentService.refund_payment(payment, Decimal('50.00'))
        
        payment.refresh_from_db()
        assert payment.refund_amount == Decimal('50.00')
        assert payment.status == 'completed'  # Partial refund
    
    def test_record_and_complete_payment(self):
        """Test convenience method for immediate payments."""
        company = CompanyFactory()
        
        payment = PaymentService.record_and_complete_payment(
            company=company,
            amount=Decimal('50.00'),
            payment_method='cash',
        )
        
        assert payment.status == 'completed'
        assert payment.completed_at is not None
