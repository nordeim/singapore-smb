"""
Ledger Service for journal entry operations.

Provides:
- Journal entry creation with balance validation
- Posting entries (updates account balances)
- Voiding entries (reverses balances)
- Auto-generation of entries from orders
- Trial balance reporting
"""
from decimal import Decimal
from datetime import date
from typing import List, Dict, Any, Optional, Tuple
import logging

from django.db import transaction
from django.db.models import Sum, Q

from apps.accounting.models import Account, JournalEntry, JournalLine


logger = logging.getLogger(__name__)


class LedgerService:
    """
    Service for managing journal entries and account ledgers.
    """
    
    @staticmethod
    def create_journal_entry(
        company,
        entry_date: date,
        lines: List[Dict[str, Any]],
        description: str = '',
        reference_type: str = '',
        reference_id=None,
        created_by=None,
    ) -> JournalEntry:
        """
        Create a new journal entry with lines.
        
        Args:
            company: Company instance
            entry_date: Date of the entry
            lines: List of line dicts with keys:
                - account_id: UUID of account
                - debit_amount: Decimal (or 0)
                - credit_amount: Decimal (or 0)
                - description: Optional line description
                - gst_amount: Optional GST amount
                - gst_code: Optional GST code
            description: Entry description
            reference_type: Type of source document
            reference_id: UUID of source document
            created_by: User creating the entry
            
        Returns:
            Created JournalEntry
            
        Raises:
            ValueError: If entry is not balanced
        """
        # Calculate totals
        total_debit = sum(
            Decimal(str(line.get('debit_amount', 0)))
            for line in lines
        )
        total_credit = sum(
            Decimal(str(line.get('credit_amount', 0)))
            for line in lines
        )
        
        # Validate balance
        if total_debit != total_credit:
            raise ValueError(
                f"Entry is not balanced: debit={total_debit}, credit={total_credit}"
            )
        
        if total_debit == 0:
            raise ValueError("Entry must have at least one non-zero line")
        
        with transaction.atomic():
            # Generate entry number
            entry_number = JournalEntry.generate_entry_number(company)
            
            # Create entry
            entry = JournalEntry.objects.create(
                company=company,
                entry_number=entry_number,
                entry_date=entry_date,
                description=description,
                reference_type=reference_type,
                reference_id=reference_id,
                total_debit=total_debit,
                total_credit=total_credit,
                created_by=created_by,
            )
            
            # Create lines
            for line_data in lines:
                JournalLine.objects.create(
                    journal_entry=entry,
                    account_id=line_data['account_id'],
                    debit_amount=Decimal(str(line_data.get('debit_amount', 0))),
                    credit_amount=Decimal(str(line_data.get('credit_amount', 0))),
                    description=line_data.get('description', ''),
                    gst_amount=Decimal(str(line_data.get('gst_amount', 0))),
                    gst_code=line_data.get('gst_code', ''),
                )
            
            logger.info(f"Created journal entry {entry.entry_number}")
            
            return entry
    
    @staticmethod
    def post_entry(entry: JournalEntry, approved_by=None) -> None:
        """
        Post a draft journal entry.
        
        This updates all affected account balances.
        
        Args:
            entry: JournalEntry to post
            approved_by: User approving the entry
        """
        with transaction.atomic():
            entry.refresh_from_db()
            entry.post(approved_by=approved_by)
            logger.info(f"Posted journal entry {entry.entry_number}")
    
    @staticmethod
    def void_entry(entry: JournalEntry) -> None:
        """
        Void a posted journal entry.
        
        This reverses all affected account balances.
        
        Args:
            entry: JournalEntry to void
        """
        with transaction.atomic():
            entry.refresh_from_db()
            entry.void()
            logger.info(f"Voided journal entry {entry.entry_number}")
    
    @staticmethod
    def create_from_order(order, created_by=None) -> JournalEntry:
        """
        Create journal entry from a completed order.
        
        Standard double-entry for sales:
        - DR Accounts Receivable: Total amount
        - CR Sales Revenue: Subtotal
        - CR GST Payable: GST amount
        
        Args:
            order: Order instance
            created_by: User creating the entry
            
        Returns:
            Created JournalEntry
        """
        # Get required accounts
        company = order.company
        
        # Find accounts by code (assumes standard chart of accounts)
        try:
            ar_account = Account.objects.get(company=company, code='1100')
            revenue_account = Account.objects.get(company=company, code='4000')
            gst_payable_account = Account.objects.get(company=company, code='2100')
        except Account.DoesNotExist as e:
            raise ValueError(
                f"Required account not found. Please initialize chart of accounts: {e}"
            )
        
        # Calculate amounts
        subtotal = order.subtotal
        gst_amount = order.gst_amount
        total = order.total_amount
        
        # Build lines
        lines = [
            {
                'account_id': ar_account.id,
                'debit_amount': total,
                'credit_amount': Decimal('0.00'),
                'description': f"Order {order.order_number}",
            },
            {
                'account_id': revenue_account.id,
                'debit_amount': Decimal('0.00'),
                'credit_amount': subtotal,
                'description': f"Sales - Order {order.order_number}",
                'gst_code': 'SR',
            },
        ]
        
        # Only add GST line if there's GST
        if gst_amount > 0:
            lines.append({
                'account_id': gst_payable_account.id,
                'debit_amount': Decimal('0.00'),
                'credit_amount': gst_amount,
                'description': f"GST - Order {order.order_number}",
                'gst_amount': gst_amount,
                'gst_code': 'SR',
            })
        
        return LedgerService.create_journal_entry(
            company=company,
            entry_date=order.created_at.date(),
            lines=lines,
            description=f"Revenue from Order {order.order_number}",
            reference_type='order',
            reference_id=order.id,
            created_by=created_by,
        )
    
    @staticmethod
    def get_account_balance(account: Account, as_of_date: Optional[date] = None) -> Decimal:
        """
        Get account balance as of a specific date.
        
        Args:
            account: Account to check
            as_of_date: Date to calculate balance as of (default: current)
            
        Returns:
            Account balance as Decimal
        """
        if as_of_date is None:
            return account.current_balance
        
        # Calculate from posted entries up to date
        lines = JournalLine.objects.filter(
            account=account,
            journal_entry__status='posted',
            journal_entry__entry_date__lte=as_of_date,
        )
        
        totals = lines.aggregate(
            total_debit=Sum('debit_amount'),
            total_credit=Sum('credit_amount'),
        )
        
        total_debit = totals['total_debit'] or Decimal('0.00')
        total_credit = totals['total_credit'] or Decimal('0.00')
        
        # Calculate balance based on normal balance
        if account.is_debit_normal:
            return total_debit - total_credit
        else:
            return total_credit - total_debit
    
    @staticmethod
    def get_trial_balance(
        company,
        as_of_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate trial balance report.
        
        Args:
            company: Company to report on
            as_of_date: Date for balance calculation
            
        Returns:
            List of account balances with debit/credit columns
        """
        accounts = Account.objects.filter(
            company=company,
            is_active=True,
        ).order_by('code')
        
        trial_balance = []
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        for account in accounts:
            balance = LedgerService.get_account_balance(account, as_of_date)
            
            if balance == 0:
                continue
            
            if balance > 0:
                if account.is_debit_normal:
                    debit = balance
                    credit = Decimal('0.00')
                else:
                    debit = Decimal('0.00')
                    credit = balance
            else:
                if account.is_debit_normal:
                    debit = Decimal('0.00')
                    credit = abs(balance)
                else:
                    debit = abs(balance)
                    credit = Decimal('0.00')
            
            trial_balance.append({
                'account_id': str(account.id),
                'account_code': account.code,
                'account_name': account.name,
                'account_type': account.account_type,
                'debit': debit,
                'credit': credit,
            })
            
            total_debit += debit
            total_credit += credit
        
        # Add totals row
        trial_balance.append({
            'account_id': None,
            'account_code': '',
            'account_name': 'TOTALS',
            'account_type': '',
            'debit': total_debit,
            'credit': total_credit,
        })
        
        return trial_balance
