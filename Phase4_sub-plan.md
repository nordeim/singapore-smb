# Phase 4: Accounting Domain Implementation Plan

## Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | Weeks 10-12 |
| **Dependencies** | Phase 2 (Commerce), Phase 3 (Inventory) |
| **Goal** | Chart of Accounts, Journal Entries, Invoices, Payments, GST Engine |

---

## Proposed Changes

### Accounting App Structure

#### [NEW] [__init__.py](file:///home/project/singapore-smb/backend/apps/accounting/__init__.py)
Empty package initializer.

#### [NEW] [apps.py](file:///home/project/singapore-smb/backend/apps/accounting/apps.py)
- [ ] Create `AccountingConfig` with name and verbose_name

---

### Models

#### [NEW] [models/account.py](file:///home/project/singapore-smb/backend/apps/accounting/models/account.py)

**Schema Reference**: `accounting.accounts`

| Field | Type | Constraints |
|-------|------|-------------|
| `company_id` | FK → companies | NOT NULL |
| `parent_id` | FK → accounts | Self-referential (hierarchy) |
| `code` | VARCHAR(20) | UNIQUE(company, code) |
| `name` | VARCHAR(100) | NOT NULL |
| `description` | TEXT | Optional |
| `account_type` | VARCHAR(20) | asset, liability, equity, revenue, expense |
| `account_subtype` | VARCHAR(50) | Optional |
| `gst_code` | VARCHAR(2) | SR, ZR, ES, OS |
| `is_active` | BOOLEAN | Default TRUE |
| `is_system` | BOOLEAN | Default FALSE (protected accounts) |
| `current_balance` | DECIMAL(15,2) | Default 0 |

**Checklist**:
- [ ] Create `Account` model inheriting from `AuditableModel`
- [ ] Add `ACCOUNT_TYPE_CHOICES` = asset, liability, equity, revenue, expense
- [ ] Add `parent` FK for hierarchical chart of accounts
- [ ] Add `code` field (unique per company)
- [ ] Add `account_type` and `account_subtype`
- [ ] Add `gst_code` for GST mapping
- [ ] Add `is_active`, `is_system` flags
- [ ] Add `current_balance` DecimalField(15,2)
- [ ] Define `db_table = '"accounting"."accounts"'`
- [ ] Add `__str__` returning code - name
- [ ] Add `get_ancestors()` method
- [ ] Add `get_descendants()` method
- [ ] Add `is_debit_normal` property (asset/expense = True)

---

#### [NEW] [models/journal_entry.py](file:///home/project/singapore-smb/backend/apps/accounting/models/journal_entry.py)

**Schema Reference**: `accounting.journal_entries`

| Field | Type | Constraints |
|-------|------|-------------|
| `company_id` | FK | NOT NULL |
| `entry_number` | VARCHAR(50) | UNIQUE(company, entry_number) |
| `entry_date` | DATE | NOT NULL |
| `description` | TEXT | Optional |
| `reference_type` | VARCHAR(50) | order, invoice, payment, manual |
| `reference_id` | UUID | Optional |
| `status` | VARCHAR(20) | draft, posted, voided |
| `posted_at` | TIMESTAMPTZ | Optional |
| `total_debit` | DECIMAL(15,2) | NOT NULL |
| `total_credit` | DECIMAL(15,2) | NOT NULL |
| `created_by` | FK → users | Optional |
| `approved_by` | FK → users | Optional |

**Constraint**: `balanced_entry CHECK (total_debit = total_credit)`

**Checklist**:
- [ ] Create `JournalEntry` model inheriting from `AuditableModel`
- [ ] Add `ENTRY_STATUS_CHOICES` = draft, posted, voided
- [ ] Add `REFERENCE_TYPE_CHOICES` = order, invoice, payment, manual
- [ ] Add `entry_number` with auto-generation
- [ ] Add `total_debit`, `total_credit` with precision
- [ ] Add DB-level `balanced_entry` constraint via Meta
- [ ] Add `status` with transitions
- [ ] Add `created_by`, `approved_by` FKs
- [ ] Define `db_table = '"accounting"."journal_entries"'`
- [ ] Add `post()` method with validation
- [ ] Add `void()` method
- [ ] Add `is_balanced` property

---

#### [NEW] [models/journal_line.py](file:///home/project/singapore-smb/backend/apps/accounting/models/journal_line.py)

**Schema Reference**: `accounting.journal_lines`

| Field | Type | Constraints |
|-------|------|-------------|
| `journal_entry_id` | FK → journal_entries | ON DELETE CASCADE |
| `account_id` | FK → accounts | NOT NULL |
| `debit_amount` | DECIMAL(12,2) | >= 0, default 0 |
| `credit_amount` | DECIMAL(12,2) | >= 0, default 0 |
| `gst_amount` | DECIMAL(10,2) | Default 0 |
| `gst_code` | VARCHAR(2) | Optional |
| `description` | TEXT | Optional |

**Constraint**: `one_side_only CHECK ((debit > 0 AND credit = 0) OR (credit > 0 AND debit = 0))`

**Checklist**:
- [ ] Create `JournalLine` model
- [ ] Add `debit_amount`, `credit_amount` with min=0
- [ ] Add `one_side_only` constraint via Meta
- [ ] Add `gst_amount`, `gst_code`
- [ ] Add `account` FK with `related_name='journal_lines'`
- [ ] Define `db_table = '"accounting"."journal_lines"'`
- [ ] Add `is_debit` property
- [ ] Add `amount` property (returns non-zero)

---

#### [NEW] [models/invoice.py](file:///home/project/singapore-smb/backend/apps/accounting/models/invoice.py)

**Schema Reference**: `accounting.invoices`

| Field | Type | Constraints |
|-------|------|-------------|
| `company_id` | FK | NOT NULL |
| `customer_id` | FK → customers | Optional |
| `order_id` | UUID | Optional |
| `invoice_number` | VARCHAR(50) | UNIQUE(company, invoice_number) |
| `invoice_date` | DATE | NOT NULL |
| `due_date` | DATE | NOT NULL |
| `status` | VARCHAR(20) | draft, sent, paid, overdue, void |
| `subtotal` | DECIMAL(12,2) | NOT NULL |
| `gst_amount` | DECIMAL(12,2) | NOT NULL |
| `total_amount` | DECIMAL(12,2) | NOT NULL |
| `amount_paid` | DECIMAL(12,2) | Default 0 |
| `amount_due` | DECIMAL(12,2) | **GENERATED** (total - paid) |
| `peppol_id` | VARCHAR(100) | Optional |
| `peppol_status` | VARCHAR(20) | Optional |
| `peppol_submitted_at` | TIMESTAMPTZ | Optional |

**Checklist**:
- [ ] Create `Invoice` model inheriting from `AuditableModel`
- [ ] Add `INVOICE_STATUS_CHOICES` = draft, sent, paid, overdue, void
- [ ] Add `customer` FK (optional for cash sales)
- [ ] Add `order_id` for order reference
- [ ] Add monetary fields with DECIMAL precision
- [ ] Add `amount_due` as **property** (GENERATED column)
- [ ] Add PEPPOL/InvoiceNow fields
- [ ] Define `db_table = '"accounting"."invoices"'`
- [ ] Add `mark_paid()` method
- [ ] Add `is_overdue` property
- [ ] Add `apply_payment(amount)` method

---

#### [NEW] [models/payment.py](file:///home/project/singapore-smb/backend/apps/accounting/models/payment.py)

**Schema Reference**: `accounting.payments`

| Field | Type | Constraints |
|-------|------|-------------|
| `company_id` | FK | NOT NULL |
| `payment_number` | VARCHAR(50) | UNIQUE(company) |
| `payment_date` | DATE | NOT NULL |
| `amount` | DECIMAL(12,2) | NOT NULL |
| `currency` | VARCHAR(3) | Default SGD |
| `payment_method` | VARCHAR(50) | NOT NULL |
| `gateway` | VARCHAR(50) | Optional (stripe, hitpay, paynow) |
| `gateway_reference` | VARCHAR(100) | Optional |
| `status` | VARCHAR(20) | pending, completed, failed, refunded |
| `reference_type` | VARCHAR(50) | order, invoice |
| `reference_id` | UUID | Optional |
| `metadata` | JSONB | Default {} |

**Checklist**:
- [ ] Create `Payment` model inheriting from `AuditableModel`
- [ ] Add `PAYMENT_STATUS_CHOICES` = pending, completed, failed, refunded
- [ ] Add `PAYMENT_METHOD_CHOICES` = cash, bank, card, paynow, etc.
- [ ] Add gateway fields for Stripe/HitPay integration
- [ ] Add `metadata` JSONField for provider response
- [ ] Define `db_table = '"accounting"."payments"'`
- [ ] Add `complete()`, `fail()`, `refund()` methods

---

#### [NEW] [models/__init__.py](file:///home/project/singapore-smb/backend/apps/accounting/models/__init__.py)
- [ ] Export Account, JournalEntry, JournalLine, Invoice, Payment
- [ ] Export all choice constants

---

### GST Engine

#### [NEW] [gst/__init__.py](file:///home/project/singapore-smb/backend/apps/accounting/gst/__init__.py)
- [ ] Export GSTEngine, get_gst_rate

#### [NEW] [gst/rates.py](file:///home/project/singapore-smb/backend/apps/accounting/gst/rates.py)

**Purpose**: Historical GST rate lookup.

**GST History (Singapore)**:
- 1994-04-01: 3%
- 2003-01-01: 4%
- 2004-01-01: 5%
- 2007-07-01: 7%
- 2023-01-01: 8%
- 2024-01-01: 9% (current)

**Checklist**:
- [ ] Define `GST_RATES` list with (effective_date, rate) tuples
- [ ] Create `get_gst_rate(transaction_date)` function
- [ ] Add `get_current_rate()` shortcut
- [ ] Support env override via `GST_DEFAULT_RATE`

#### [NEW] [gst/engine.py](file:///home/project/singapore-smb/backend/apps/accounting/gst/engine.py)

**Purpose**: GST calculation and F5 return preparation.

**Methods**:

| Method | Purpose |
|--------|---------|
| `calculate(amount, gst_code, date)` | Calculate GST for transaction |
| `get_rate(gst_code, date)` | Get applicable rate |
| `prepare_f5(company, quarter, year)` | Generate F5 return data |
| `validate_f5(f5_return)` | Validate F5 data integrity |

**F5 Return Boxes**:
- Box 1: Standard-rated supplies (SR)
- Box 2: Zero-rated supplies (ZR)
- Box 3: Exempt supplies (ES)
- Box 4: Total supplies (1+2+3)
- Box 5: Total taxable purchases
- Box 6: Output tax due (Box 1 × rate)
- Box 7: Input tax claimable
- Box 8: Net GST payable (6-7)

**Checklist**:
- [ ] Create `GSTEngine` class
- [ ] Implement `calculate(amount, gst_code, date)` returning (net, gst, gross)
- [ ] Implement `get_rate(gst_code, date)` with historical lookup
- [ ] Implement `prepare_f5(company_id, quarter, year)`
  - [ ] Query orders by quarter with GST codes
  - [ ] Sum by GST code for boxes 1-3
  - [ ] Calculate boxes 4-8
- [ ] Implement `validate_f5(f5_return)` checking totals
- [ ] Handle rounding (ROUND_HALF_UP)

---

### Services

#### [NEW] [services/__init__.py](file:///home/project/singapore-smb/backend/apps/accounting/services/__init__.py)
- [ ] Export LedgerService, InvoiceService, PaymentService

#### [NEW] [services/ledger_service.py](file:///home/project/singapore-smb/backend/apps/accounting/services/ledger_service.py)

**Methods**:

| Method | Purpose |
|--------|---------|
| `create_journal_entry()` | Create with lines, validate balance |
| `post_entry()` | Post draft entry, update account balances |
| `void_entry()` | Void posted entry, reverse balances |
| `create_from_order()` | Auto-create journal from order |
| `get_account_balance()` | Get balance for account |
| `get_trial_balance()` | Generate trial balance report |

**Checklist**:
- [ ] Implement `create_journal_entry(company, date, lines[], description)`
  - [ ] Validate debit == credit
  - [ ] Create entry and lines
- [ ] Implement `post_entry(entry_id)`
  - [ ] Update account current_balance
  - [ ] Set status = posted, posted_at = now
- [ ] Implement `void_entry(entry_id)`
  - [ ] Reverse account balance updates
  - [ ] Set status = voided
- [ ] Implement `create_from_order(order)` for automatic entries
- [ ] Implement `get_trial_balance(company, as_of_date)`

#### [NEW] [services/invoice_service.py](file:///home/project/singapore-smb/backend/apps/accounting/services/invoice_service.py)

**Methods**:

| Method | Purpose |
|--------|---------|
| `create_from_order()` | Generate invoice from order |
| `apply_payment()` | Apply payment to invoice |
| `mark_sent()` | Mark invoice as sent |
| `check_overdue()` | Update overdue status |
| `generate_invoice_number()` | Auto-generate number |

**Checklist**:
- [ ] Implement `create_from_order(order)` with GST calculation
- [ ] Implement `apply_payment(invoice, amount)`
- [ ] Implement `mark_sent(invoice)` updating status
- [ ] Implement `check_overdue(company)` batch update
- [ ] Implement `generate_invoice_number(company)` with format INV-YYYYMM-NNNN

#### [NEW] [services/payment_service.py](file:///home/project/singapore-smb/backend/apps/accounting/services/payment_service.py)

**Methods**:

| Method | Purpose |
|--------|---------|
| `record_payment()` | Create payment record |
| `complete_payment()` | Mark payment completed |
| `fail_payment()` | Mark payment failed |
| `refund_payment()` | Process refund |
| `reconcile_gateway()` | Reconcile with gateway |

**Checklist**:
- [ ] Implement `record_payment(invoice/order, amount, method, gateway_ref)`
- [ ] Implement `complete_payment(payment_id)` updating invoice
- [ ] Implement `fail_payment(payment_id, reason)`
- [ ] Implement `refund_payment(payment_id, amount)`
- [ ] Create journal entries for payments

---

### API Layer

#### [NEW] [serializers.py](file:///home/project/singapore-smb/backend/apps/accounting/serializers.py)

**Checklist**:
- [ ] `AccountSerializer` - full CRUD with hierarchy
- [ ] `AccountListSerializer` - lightweight for lists
- [ ] `AccountTreeSerializer` - with children nested
- [ ] `JournalEntrySerializer` - with lines nested
- [ ] `JournalLineSerializer` - for line items
- [ ] `JournalEntryCreateSerializer` - for creating with lines
- [ ] `InvoiceSerializer` - with computed amount_due
- [ ] `InvoiceListSerializer` - lightweight
- [ ] `PaymentSerializer` - full CRUD
- [ ] `GSTF5Serializer` - for F5 return data
- [ ] `TrialBalanceSerializer` - for balance report

---

#### [NEW] [views.py](file:///home/project/singapore-smb/backend/apps/accounting/views.py)

**Endpoints**:

| Endpoint | Methods | Custom Actions |
|----------|---------|----------------|
| `/accounts/` | CRUD | `tree/`, `balances/` |
| `/journals/` | List, Create, Retrieve | `post/`, `void/` |
| `/invoices/` | CRUD | `send/`, `pdf/` |
| `/payments/` | List, Create, Retrieve | `complete/`, `refund/` |
| `/gst/f5/` | - | `prepare/`, `validate/`, `submit/` |
| `/reports/trial-balance/` | GET | - |

**Checklist**:
- [ ] `AccountViewSet` - CRUD with company filter
  - [ ] `@action tree` - nested tree structure
  - [ ] `@action balances` - account balances
- [ ] `JournalEntryViewSet`
  - [ ] Create with lines (nested)
  - [ ] `@action post` - post draft entry
  - [ ] `@action void` - void posted entry
- [ ] `InvoiceViewSet`
  - [ ] `@action send` - mark sent
  - [ ] `@action pdf` - generate PDF (placeholder)
- [ ] `PaymentViewSet`
  - [ ] `@action complete` - mark completed
  - [ ] `@action refund` - process refund
- [ ] `GSTF5ViewSet` or custom views for GST operations
  - [ ] `prepare/` - prepare F5 return
  - [ ] `validate/` - validate F5 data

---

#### [NEW] [urls.py](file:///home/project/singapore-smb/backend/apps/accounting/urls.py)
- [ ] Register ViewSets with router
- [ ] Add GST-specific routes
- [ ] app_name = 'accounting'

---

#### [MODIFY] [config/urls.py](file:///home/project/singapore-smb/backend/config/urls.py)
- [ ] Add `path('accounting/', include('apps.accounting.urls', namespace='accounting'))`

---

#### [MODIFY] [config/settings/base.py](file:///home/project/singapore-smb/backend/config/settings/base.py)
- [ ] Add `'apps.accounting'` to LOCAL_APPS

---

### Admin

#### [NEW] [admin.py](file:///home/project/singapore-smb/backend/apps/accounting/admin.py)

**Checklist**:
- [ ] `AccountAdmin` with hierarchy display
  - [ ] list_display: code, name, type, balance
  - [ ] Filter by type, is_active
- [ ] `JournalEntryAdmin`
  - [ ] Inline for JournalLines
  - [ ] Read-only for posted entries
  - [ ] Filter by status, date
- [ ] `InvoiceAdmin`
  - [ ] Display status with colors
  - [ ] Filter by status, overdue
- [ ] `PaymentAdmin`
  - [ ] Display gateway info
  - [ ] Filter by status, method

---

### Celery Tasks

#### [NEW] [tasks.py](file:///home/project/singapore-smb/backend/apps/accounting/tasks.py)

**Checklist**:
- [ ] `check_overdue_invoices` - periodic task
  - [ ] Find invoices where due_date < today AND status = 'sent'
  - [ ] Update status to 'overdue'
- [ ] `prepare_gst_filing_reminder` - periodic task
  - [ ] Send reminder 7 days before quarter end
- [ ] `generate_invoice_pdf` - async task
  - [ ] Generate PDF from invoice data (placeholder)
- [ ] `generate_daily_revenue_report` - periodic task
  - [ ] Aggregate daily revenue by category

---

### Tests

#### [NEW] [tests/__init__.py](file:///home/project/singapore-smb/backend/apps/accounting/tests/__init__.py)
Empty package.

#### [NEW] [tests/factories.py](file:///home/project/singapore-smb/backend/apps/accounting/tests/factories.py)
- [ ] `AccountFactory`
- [ ] `JournalEntryFactory`
- [ ] `JournalLineFactory`
- [ ] `InvoiceFactory`
- [ ] `PaymentFactory`

#### [NEW] [tests/test_models.py](file:///home/project/singapore-smb/backend/apps/accounting/tests/test_models.py)
- [ ] Test Account CRUD and hierarchy
- [ ] Test JournalEntry balanced constraint
- [ ] Test JournalLine one_side_only constraint
- [ ] Test Invoice amount_due property
- [ ] Test Payment status transitions

#### [NEW] [tests/test_gst_engine.py](file:///home/project/singapore-smb/backend/apps/accounting/tests/test_gst_engine.py)
- [ ] Test GST calculation for SR (9%)
- [ ] Test GST calculation for ZR (0%)
- [ ] Test GST calculation for ES, OS (0%)
- [ ] Test historical rate lookup
- [ ] Test F5 box calculations
- [ ] Test F5 validation

#### [NEW] [tests/test_services.py](file:///home/project/singapore-smb/backend/apps/accounting/tests/test_services.py)
- [ ] Test LedgerService.create_journal_entry
- [ ] Test LedgerService.post_entry updates balances
- [ ] Test LedgerService.void_entry reverses
- [ ] Test InvoiceService.create_from_order
- [ ] Test PaymentService.record_payment

#### [NEW] [tests/test_views.py](file:///home/project/singapore-smb/backend/apps/accounting/tests/test_views.py)
- [ ] Test Account CRUD
- [ ] Test JournalEntry create with lines
- [ ] Test JournalEntry post action
- [ ] Test Invoice CRUD and status transitions
- [ ] Test Payment CRUD and complete action

---

### Migrations

#### [NEW] [migrations/0001_create_schema.py](file:///home/project/singapore-smb/backend/apps/accounting/migrations/0001_create_schema.py)
- [ ] `CREATE SCHEMA IF NOT EXISTS accounting;`

#### [AUTO] [migrations/0002_models.py](file:///home/project/singapore-smb/backend/apps/accounting/migrations/0002_models.py)
- [ ] Auto-generated via `makemigrations`

---

## Summary

| Category | Files | New | Modified |
|----------|-------|-----|----------|
| App Structure | 2 | 2 | 0 |
| Models | 6 | 6 | 0 |
| GST Engine | 3 | 3 | 0 |
| Services | 4 | 4 | 0 |
| API Layer | 3 | 3 | 0 |
| Admin | 1 | 1 | 0 |
| Tasks | 1 | 1 | 0 |
| Tests | 6 | 6 | 0 |
| Migrations | 2 | 2 | 0 |
| Config | 2 | 0 | 2 |
| **Total** | **30** | **28** | **2** |

---

## Verification Plan

### Automated Tests
```bash
cd backend
uv run pytest apps/accounting/tests/ -v
```

### GST Calculation Verification
```python
# Test cases:
# 1. SR at 9%: $100.00 → GST $9.00 → Total $109.00
# 2. ZR at 0%: $100.00 → GST $0.00 → Total $100.00
# 3. Historical: $100.00 on 2022-06-01 → 7% = $7.00
```

### F5 Return Verification
1. Create test orders with different GST codes
2. Run `GSTEngine.prepare_f5(company, Q1, 2024)`
3. Verify Box 1-8 totals match expected

### Manual Verification
1. Create account via admin
2. Create journal entry with lines
3. Post entry and verify account balance updates
4. Create invoice from order
5. Apply payment and verify amount_due

---

## Key Design Decisions

### 1. Journal Entry Balance Validation
Enforced at both Django model level (pre-save validation) and database level (CHECK constraint) for data integrity.

### 2. amount_due as Property
PostgreSQL `GENERATED ALWAYS AS` column is read-only in Django. Exposed as computed property.

### 3. GST Rate Lookup
Historical rates stored in memory (from schema seed data). Environment-configurable current rate as fallback.

### 4. Account Balance Updates
Account `current_balance` is updated when journal entries are POSTED (not created). Void reverses these updates.

### 5. Double-Entry Accounting
Every transaction creates balanced journal entries (debits = credits). Order → automates: DR Receivables, CR Revenue, CR GST Payable.

---

# Phase 4: Accounting Domain Implementation

## Task Status: ✅ COMPLETE

---

## Planning
- [x] Review master_execution_plan.md Phase 4 scope
- [x] Review database/schema.sql for accounting tables
- [x] Create comprehensive implementation_plan.md
- [x] Get user approval for implementation plan

---

## Execution

### App Structure
- [x] Create `backend/apps/accounting/__init__.py`
- [x] Create `backend/apps/accounting/apps.py`

### Models (5/5)
- [x] Create `models/account.py` - Chart of Accounts with hierarchy
- [x] Create `models/journal_entry.py` - Double-entry with balanced constraint
- [x] Create `models/journal_line.py` - Individual debit/credit lines
- [x] Create `models/invoice.py` - AR with PEPPOL fields
- [x] Create `models/payment.py` - Payment tracking with refunds
- [x] Create `models/__init__.py` - Exports

### GST Engine (3/3)
- [x] Create `gst/__init__.py` - Package exports
- [x] Create `gst/rates.py` - Historical Singapore GST rates
- [x] Create `gst/engine.py` - GSTEngine with F5 preparation

### Services (3/3)
- [x] Create `services/__init__.py` - Package exports
- [x] Create `services/ledger_service.py` - Journal entry management
- [x] Create `services/invoice_service.py` - Invoice lifecycle
- [x] Create `services/payment_service.py` - Payment processing

### API Layer
- [x] Create `serializers.py` - 13 serializers
- [x] Create `views.py` - 6 ViewSets with custom actions
- [x] Create `urls.py` - Router configuration
- [x] Create `admin.py` - Django Admin with color-coded statuses

### Celery Tasks
- [x] Create `tasks.py` - 5 background tasks

### Tests (4/4 files)
- [x] Create `tests/__init__.py`
- [x] Create `tests/factories.py` - 10 factories
- [x] Create `tests/test_models.py` - 32 tests
- [x] Create `tests/test_gst_engine.py` - 20 tests
- [x] Create `tests/test_services.py` - 17 tests
- [x] Create `tests/test_views.py` - 15 tests

### Migrations
- [x] Create `migrations/__init__.py`
- [x] Create `migrations/0001_create_schema.py`
- [x] Generate `migrations/0002_initial.py` (auto-generated)

### Configuration
- [x] Add `apps.accounting` to `LOCAL_APPS` in settings
- [x] Add accounting URLs to main URL configuration

---

## Verification
- [x] Django check passes (0 issues)
- [x] All 91 accounting tests pass
- [x] All 273 total tests pass (no regressions)

---

## Summary

Phase 4 Accounting Domain is fully implemented with:

| Component | Count | Status |
|-----------|-------|--------|
| Models | 5 | ✅ |
| GST Engine Files | 3 | ✅ |
| Services | 3 | ✅ |
| Serializers | 13 | ✅ |
| ViewSets | 6 | ✅ |
| Celery Tasks | 5 | ✅ |
| Test Files | 5 | ✅ |
| Tests | 91 | ✅ |
| Migrations | 2 | ✅ |
