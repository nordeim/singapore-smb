# Phase 4: Accounting Domain - Implementation Walkthrough

## Overview

Phase 4 of the Singapore SMB platform has been successfully implemented, adding a comprehensive **Accounting Domain** with double-entry bookkeeping, Singapore GST compliance, and invoice/payment management.

---

## What Was Implemented

### 1. Models (5 files)

| Model | Purpose | Key Features |
|-------|---------|--------------|
| [Account](file:///home/project/singapore-smb/backend/apps/accounting/models/account.py) | Chart of Accounts | Hierarchical structure, 5 account types, debit/credit normal balance detection |
| [JournalEntry](file:///home/project/singapore-smb/backend/apps/accounting/models/journal_entry.py) | Double-entry records | Balanced constraint (DB-level), post/void workflow, auto-numbering |
| [JournalLine](file:///home/project/singapore-smb/backend/apps/accounting/models/journal_line.py) | Individual debits/credits | One-side-only constraint, GST tracking per line |
| [Invoice](file:///home/project/singapore-smb/backend/apps/accounting/models/invoice.py) | Accounts Receivable | PEPPOL fields, payment application, overdue detection |
| [Payment](file:///home/project/singapore-smb/backend/apps/accounting/models/payment.py) | Payment tracking | Multiple methods, gateway integration fields, refund support |

### 2. GST Engine (3 files)

| File | Purpose |
|------|---------|
| [rates.py](file:///home/project/singapore-smb/backend/apps/accounting/gst/rates.py) | Historical Singapore GST rates (1994-2024) |
| [engine.py](file:///home/project/singapore-smb/backend/apps/accounting/gst/engine.py) | GST calculation, F5 return preparation and validation |

**Key capabilities:**
- Historical rate lookup for any transaction date
- SR (Standard Rated), ZR (Zero Rated), ES (Exempt), OS (Out of Scope) codes
- GST-inclusive/exclusive calculations with proper rounding
- F5 return boxes 1-8 calculation from orders

### 3. Services (3 files)

| Service | Key Methods |
|---------|-------------|
| [LedgerService](file:///home/project/singapore-smb/backend/apps/accounting/services/ledger_service.py) | `create_journal_entry()`, `post_entry()`, `void_entry()`, `get_trial_balance()` |
| [InvoiceService](file:///home/project/singapore-smb/backend/apps/accounting/services/invoice_service.py) | `create_from_order()`, `apply_payment()`, `check_overdue_invoices()`, `get_aging_summary()` |
| [PaymentService](file:///home/project/singapore-smb/backend/apps/accounting/services/payment_service.py) | `record_payment()`, `complete_payment()`, `refund_payment()` |

### 4. API Endpoints

| ViewSet | Endpoints | Custom Actions |
|---------|-----------|----------------|
| AccountViewSet | CRUD `/accounts/` | `tree/`, `balances/` |
| JournalEntryViewSet | List/Create `/journals/` | `post/`, `void/` |
| InvoiceViewSet | CRUD `/invoices/` | `send/`, `void/`, `aging/` |
| PaymentViewSet | List/Create `/payments/` | `complete/`, `refund/` |
| GSTF5ViewSet | `/gst/f5/` | `prepare/`, `validate/` |
| ReportViewSet | `/reports/` | `trial-balance/` |

### 5. Celery Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| `check_overdue_invoices` | Daily | Mark past-due invoices as overdue |
| `prepare_gst_filing_reminder` | Weekly | Send reminders near quarter-end |
| `generate_daily_revenue_report` | On-demand | Aggregate daily revenue |
| `generate_invoice_pdf` | On-demand | PDF generation (placeholder) |
| `sync_account_balances` | On-demand | Recalculate balances from entries |

---

## Key Design Decisions

### Double-Entry Enforcement
```python
# DB-level constraint ensures total_debit == total_credit
models.CheckConstraint(
    condition=models.Q(total_debit=models.F('total_credit')),
    name='balanced_entry',
)
```

### Historical GST Rate Lookup
```python
GST_RATES = [
    (date(2024, 1, 1), Decimal('0.09')),  # 9% from 2024
    (date(2023, 1, 1), Decimal('0.08')),  # 8% from 2023
    (date(2007, 7, 1), Decimal('0.07')),  # 7% from 2007
    # ... back to 1994
]
```

### Account Balance Updates
- Balances only update when entries are **posted**, not on creation
- Voiding reverses the balance changes
- Service layer controls the lifecycle

---

## Test Results

```
============================= 91 passed in 32.37s ==============================
```

| Test File | Tests | Coverage |
|-----------|-------|----------|
| test_models.py | 32 | Account balance, journal constraints, invoice/payment lifecycle |
| test_gst_engine.py | 20 | Rate lookup, calculations, F5 validation |
| test_services.py | 17 | Ledger, invoice, payment operations |
| test_views.py | 15 | API endpoints and actions |

**Full suite:** 273 tests pass with no regressions.

---

## Files Created

```
backend/apps/accounting/
├── __init__.py
├── apps.py
├── admin.py
├── serializers.py
├── views.py
├── urls.py
├── tasks.py
├── models/
│   ├── __init__.py
│   ├── account.py
│   ├── journal_entry.py
│   ├── journal_line.py
│   ├── invoice.py
│   └── payment.py
├── gst/
│   ├── __init__.py
│   ├── rates.py
│   └── engine.py
├── services/
│   ├── __init__.py
│   ├── ledger_service.py
│   ├── invoice_service.py
│   └── payment_service.py
├── migrations/
│   ├── __init__.py
│   ├── 0001_create_schema.py
│   └── 0002_initial.py
└── tests/
    ├── __init__.py
    ├── factories.py
    ├── test_models.py
    ├── test_gst_engine.py
    ├── test_services.py
    └── test_views.py
```

---

## Configuration Changes

### settings/base.py
```diff
 LOCAL_APPS = [
     'core',
     'apps.accounts',
     'apps.commerce',
     'apps.inventory',
+    'apps.accounting',
 ]
```

### config/urls.py
```diff
 path('api/v1/', include([
     path('accounts/', include('apps.accounts.urls')),
     path('commerce/', include('apps.commerce.urls')),
     path('inventory/', include('apps.inventory.urls')),
+    path('accounting/', include('apps.accounting.urls')),
 ])),
```

---

## Outstanding Items for Future Phases

1. **Invoice PDF Generation** - Placeholder in `tasks.py`, needs templating implementation
2. **Payment Gateway Integration** - Model fields ready, actual API calls needed
3. **Chart of Accounts Templates** - `initialize_company_accounts()` function for new companies
4. **PEPPOL Integration** - Fields present, submission logic for Phase 5
