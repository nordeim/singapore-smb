"""
Factory Boy factories for accounting tests.
"""
import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
from datetime import date, timedelta
import uuid

from apps.accounts.tests.factories import CompanyFactory, UserFactory
from apps.accounting.models import Account, JournalEntry, JournalLine, Invoice, Payment


class AccountFactory(DjangoModelFactory):
    """Factory for Account model."""
    
    class Meta:
        model = Account
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    code = factory.Sequence(lambda n: f'{1000 + n}')
    name = factory.Faker('company')
    description = factory.Faker('sentence')
    account_type = 'asset'
    account_subtype = 'current'
    is_active = True
    is_system = False
    current_balance = Decimal('0.00')


class AssetAccountFactory(AccountFactory):
    """Factory for Asset accounts."""
    account_type = 'asset'
    account_subtype = 'current'
    code = factory.Sequence(lambda n: f'{1000 + n}')


class LiabilityAccountFactory(AccountFactory):
    """Factory for Liability accounts."""
    account_type = 'liability'
    account_subtype = 'current_liability'
    code = factory.Sequence(lambda n: f'{2000 + n}')


class RevenueAccountFactory(AccountFactory):
    """Factory for Revenue accounts."""
    account_type = 'revenue'
    account_subtype = 'operating'
    code = factory.Sequence(lambda n: f'{4000 + n}')


class ExpenseAccountFactory(AccountFactory):
    """Factory for Expense accounts."""
    account_type = 'expense'
    account_subtype = 'operating_expense'
    code = factory.Sequence(lambda n: f'{6000 + n}')


class JournalEntryFactory(DjangoModelFactory):
    """Factory for JournalEntry model.
    
    Note: total_debit and total_credit are set to 0 by default
    to satisfy the balanced_entry DB constraint. When testing
    with actual lines, create the entry first, then add lines.
    """
    
    class Meta:
        model = JournalEntry
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    entry_number = factory.Sequence(lambda n: f'JE-2024-{n:05d}')
    entry_date = factory.LazyFunction(date.today)
    description = factory.Faker('sentence')
    reference_type = ''
    status = 'draft'
    # Must be balanced (equal) to satisfy DB constraint
    total_debit = Decimal('0.00')
    total_credit = Decimal('0.00')


class JournalLineFactory(DjangoModelFactory):
    """Factory for JournalLine model.
    
    Note: Does NOT auto-create a JournalEntry to avoid constraint issues.
    Pass journal_entry explicitly when using this factory.
    """
    
    class Meta:
        model = JournalLine
    
    id = factory.LazyFunction(uuid.uuid4)
    # No SubFactory - must pass journal_entry explicitly
    journal_entry = None
    account = factory.SubFactory(AccountFactory)
    debit_amount = Decimal('100.00')
    credit_amount = Decimal('0.00')
    gst_amount = Decimal('0.00')
    gst_code = ''
    description = ''


class InvoiceFactory(DjangoModelFactory):
    """Factory for Invoice model."""
    
    class Meta:
        model = Invoice
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    invoice_number = factory.Sequence(lambda n: f'INV-202412-{n:04d}')
    invoice_date = factory.LazyFunction(date.today)
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=30))
    status = 'draft'
    subtotal = Decimal('100.00')
    gst_amount = Decimal('9.00')
    total_amount = Decimal('109.00')
    amount_paid = Decimal('0.00')
    
    @factory.lazy_attribute
    def customer(self):
        """Create customer under same company."""
        from apps.commerce.tests.factories import CustomerFactory
        return CustomerFactory(company=self.company)


class PaidInvoiceFactory(InvoiceFactory):
    """Factory for paid invoices."""
    status = 'paid'
    amount_paid = Decimal('109.00')


class OverdueInvoiceFactory(InvoiceFactory):
    """Factory for overdue invoices."""
    status = 'overdue'
    due_date = factory.LazyFunction(lambda: date.today() - timedelta(days=7))


class PaymentFactory(DjangoModelFactory):
    """Factory for Payment model."""
    
    class Meta:
        model = Payment
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    payment_number = factory.Sequence(lambda n: f'PAY-2024-{n:05d}')
    payment_date = factory.LazyFunction(date.today)
    amount = Decimal('109.00')
    currency = 'SGD'
    payment_method = 'bank_transfer'
    gateway = ''
    status = 'pending'


class CompletedPaymentFactory(PaymentFactory):
    """Factory for completed payments."""
    status = 'completed'
