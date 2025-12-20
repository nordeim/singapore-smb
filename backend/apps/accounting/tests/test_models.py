"""
Tests for accounting models.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta

from django.db import IntegrityError

from apps.accounting.models import Account, JournalEntry, JournalLine, Invoice, Payment
from apps.accounting.tests.factories import (
    AccountFactory, AssetAccountFactory, LiabilityAccountFactory,
    RevenueAccountFactory, ExpenseAccountFactory,
    JournalEntryFactory, JournalLineFactory,
    InvoiceFactory, OverdueInvoiceFactory,
    PaymentFactory, CompletedPaymentFactory,
)


pytestmark = pytest.mark.django_db


class TestAccountModel:
    """Tests for Account model."""
    
    def test_create_account(self):
        """Test account creation."""
        account = AccountFactory()
        assert account.id is not None
        assert account.code is not None
        assert account.current_balance == Decimal('0.00')
    
    def test_account_str(self):
        """Test __str__ representation."""
        account = AccountFactory(code='1000', name='Cash')
        assert str(account) == '1000 - Cash'
    
    def test_is_debit_normal_asset(self):
        """Test debit-normal for asset accounts."""
        account = AssetAccountFactory()
        assert account.is_debit_normal is True
    
    def test_is_debit_normal_liability(self):
        """Test credit-normal for liability accounts."""
        account = LiabilityAccountFactory()
        assert account.is_debit_normal is False
    
    def test_is_debit_normal_revenue(self):
        """Test credit-normal for revenue accounts."""
        account = RevenueAccountFactory()
        assert account.is_debit_normal is False
    
    def test_is_debit_normal_expense(self):
        """Test debit-normal for expense accounts."""
        account = ExpenseAccountFactory()
        assert account.is_debit_normal is True
    
    def test_update_balance_debit_normal_debit(self):
        """Test balance update for debit-normal account with debit."""
        account = AssetAccountFactory(current_balance=Decimal('100.00'))
        account.update_balance(Decimal('50.00'), is_debit=True)
        assert account.current_balance == Decimal('150.00')
    
    def test_update_balance_debit_normal_credit(self):
        """Test balance update for debit-normal account with credit."""
        account = AssetAccountFactory(current_balance=Decimal('100.00'))
        account.update_balance(Decimal('30.00'), is_debit=False)
        assert account.current_balance == Decimal('70.00')
    
    def test_update_balance_credit_normal_credit(self):
        """Test balance update for credit-normal account with credit."""
        account = LiabilityAccountFactory(current_balance=Decimal('100.00'))
        account.update_balance(Decimal('50.00'), is_debit=False)
        assert account.current_balance == Decimal('150.00')
    
    def test_update_balance_credit_normal_debit(self):
        """Test balance update for credit-normal account with debit."""
        account = LiabilityAccountFactory(current_balance=Decimal('100.00'))
        account.update_balance(Decimal('30.00'), is_debit=True)
        assert account.current_balance == Decimal('70.00')
    
    def test_unique_code_per_company(self):
        """Test unique constraint on code per company."""
        account1 = AccountFactory(code='1000')
        
        with pytest.raises(IntegrityError):
            AccountFactory(company=account1.company, code='1000')


class TestJournalEntryModel:
    """Tests for JournalEntry model."""
    
    def test_create_entry(self):
        """Test journal entry creation."""
        entry = JournalEntryFactory()
        assert entry.id is not None
        assert entry.status == 'draft'
    
    def test_is_balanced(self):
        """Test is_balanced property."""
        entry = JournalEntryFactory(
            total_debit=Decimal('100.00'),
            total_credit=Decimal('100.00')
        )
        assert entry.is_balanced is True
    
    def test_is_not_balanced(self):
        """Test is_balanced property when not balanced.
        
        Note: We use build() to test the property without hitting DB constraint.
        In practice, unbalanced entries cannot be saved to DB.
        """
        entry = JournalEntryFactory.build(
            total_debit=Decimal('100.00'),
            total_credit=Decimal('90.00')
        )
        assert entry.is_balanced is False
    
    def test_can_edit_draft(self):
        """Test can_edit for draft entries."""
        entry = JournalEntryFactory(status='draft')
        assert entry.can_edit is True
    
    def test_can_edit_posted(self):
        """Test can_edit for posted entries."""
        entry = JournalEntryFactory(status='posted')
        assert entry.can_edit is False
    
    def test_generate_entry_number(self):
        """Test entry number generation."""
        entry = JournalEntryFactory()
        number = JournalEntry.generate_entry_number(entry.company)
        assert number.startswith('JE-')


class TestJournalLineModel:
    """Tests for JournalLine model."""
    
    def test_create_debit_line(self):
        """Test debit line creation."""
        # Create a balanced entry first
        entry = JournalEntryFactory()
        account = AccountFactory(company=entry.company)
        
        line = JournalLine.objects.create(
            journal_entry=entry,
            account=account,
            debit_amount=Decimal('100.00'),
            credit_amount=Decimal('0.00'),
        )
        assert line.is_debit is True
        assert line.is_credit is False
        assert line.amount == Decimal('100.00')
    
    def test_create_credit_line(self):
        """Test credit line creation."""
        # Create a balanced entry first
        entry = JournalEntryFactory()
        account = AccountFactory(company=entry.company)
        
        line = JournalLine.objects.create(
            journal_entry=entry,
            account=account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('50.00'),
        )
        assert line.is_debit is False
        assert line.is_credit is True
        assert line.amount == Decimal('50.00')
    
    def test_signed_amount_debit(self):
        """Test signed_amount for debit line."""
        entry = JournalEntryFactory()
        account = AccountFactory(company=entry.company)
        
        line = JournalLine.objects.create(
            journal_entry=entry,
            account=account,
            debit_amount=Decimal('100.00'),
            credit_amount=Decimal('0.00'),
        )
        assert line.signed_amount == Decimal('100.00')
    
    def test_signed_amount_credit(self):
        """Test signed_amount for credit line."""
        entry = JournalEntryFactory()
        account = AccountFactory(company=entry.company)
        
        line = JournalLine.objects.create(
            journal_entry=entry,
            account=account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('50.00'),
        )
        assert line.signed_amount == Decimal('-50.00')


class TestInvoiceModel:
    """Tests for Invoice model."""
    
    def test_create_invoice(self):
        """Test invoice creation."""
        invoice = InvoiceFactory()
        assert invoice.id is not None
        assert invoice.status == 'draft'
    
    def test_amount_due_property(self):
        """Test amount_due calculation."""
        invoice = InvoiceFactory(
            total_amount=Decimal('109.00'),
            amount_paid=Decimal('50.00')
        )
        assert invoice.amount_due == Decimal('59.00')
    
    def test_is_paid_not_paid(self):
        """Test is_paid when not fully paid."""
        invoice = InvoiceFactory(
            total_amount=Decimal('100.00'),
            amount_paid=Decimal('50.00')
        )
        assert invoice.is_paid is False
    
    def test_is_paid_fully_paid(self):
        """Test is_paid when fully paid."""
        invoice = InvoiceFactory(
            total_amount=Decimal('100.00'),
            amount_paid=Decimal('100.00')
        )
        assert invoice.is_paid is True
    
    def test_is_overdue_true(self):
        """Test is_overdue when past due date."""
        invoice = OverdueInvoiceFactory()
        invoice.status = 'sent'  # Overdue only applies to sent
        assert invoice.is_overdue is True
    
    def test_is_overdue_false_not_due(self):
        """Test is_overdue when not yet due."""
        invoice = InvoiceFactory(
            status='sent',
            due_date=date.today() + timedelta(days=7)
        )
        assert invoice.is_overdue is False
    
    def test_apply_payment(self):
        """Test applying payment to invoice."""
        invoice = InvoiceFactory(
            total_amount=Decimal('100.00'),
            amount_paid=Decimal('0.00'),
            status='sent'
        )
        invoice.apply_payment(Decimal('50.00'))
        assert invoice.amount_paid == Decimal('50.00')
        assert invoice.status == 'sent'  # Still sent, not fully paid
    
    def test_apply_payment_full(self):
        """Test applying full payment marks as paid."""
        invoice = InvoiceFactory(
            total_amount=Decimal('100.00'),
            amount_paid=Decimal('0.00'),
            status='sent'
        )
        invoice.apply_payment(Decimal('100.00'))
        assert invoice.amount_paid == Decimal('100.00')
        assert invoice.status == 'paid'
    
    def test_mark_sent(self):
        """Test marking invoice as sent."""
        invoice = InvoiceFactory(status='draft')
        invoice.mark_sent()
        assert invoice.status == 'sent'


class TestPaymentModel:
    """Tests for Payment model."""
    
    def test_create_payment(self):
        """Test payment creation."""
        payment = PaymentFactory()
        assert payment.id is not None
        assert payment.status == 'pending'
    
    def test_complete_payment(self):
        """Test completing a payment."""
        payment = PaymentFactory(status='pending')
        payment.complete()
        assert payment.status == 'completed'
        assert payment.completed_at is not None
    
    def test_complete_non_pending_raises(self):
        """Test completing non-pending payment raises error."""
        payment = CompletedPaymentFactory()
        with pytest.raises(ValueError):
            payment.complete()
    
    def test_fail_payment(self):
        """Test failing a payment."""
        payment = PaymentFactory(status='pending')
        payment.fail('Card declined')
        assert payment.status == 'failed'
        assert payment.failed_reason == 'Card declined'
    
    def test_refund_payment(self):
        """Test refunding a payment."""
        payment = CompletedPaymentFactory(amount=Decimal('100.00'))
        payment.refund(Decimal('50.00'))
        assert payment.refund_amount == Decimal('50.00')
        assert payment.status == 'completed'  # Still completed, partial refund
    
    def test_refund_full_payment(self):
        """Test full refund marks as refunded."""
        payment = CompletedPaymentFactory(amount=Decimal('100.00'))
        payment.refund()  # Full refund
        assert payment.refund_amount == Decimal('100.00')
        assert payment.status == 'refunded'
    
    def test_net_amount(self):
        """Test net_amount calculation."""
        payment = CompletedPaymentFactory(
            amount=Decimal('100.00'),
            refund_amount=Decimal('30.00')
        )
        assert payment.net_amount == Decimal('70.00')
