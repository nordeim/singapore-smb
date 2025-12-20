# Comprehensive and Validated Project Understanding
## Singapore SMB E-Commerce & Integrated Business Platform

> **Reference Document for AI Agent Task Alignment**  
> **Created**: December 20, 2025  
> **Validated Against**: Codebase Phases 1-4 (273 tests passing)  
> **Location**: `/home/pete/.gemini/antigravity/brain/c7136b15-4639-49e0-8a4d-e8f1505f3976/COMPREHENSIVE_PROJECT_UNDERSTANDING.md`

---

## Executive Summary

The **Singapore SMB E-Commerce Platform** is a **modular monolith** designed to unify three critical business functions for Singapore Small and Medium Businesses (10-50 employees, S$500K-S$10M revenue):

| Pillar | Technology | Key Differentiator |
|--------|------------|-------------------|
| **E-commerce Storefront** | Next.js 14.2+ (PWA) | <2s mobile page load, PayNow integration |
| **Real-time Inventory** | Django + Redis locks | Multi-location sync, 99.5% accuracy target |
| **Automated Accounting** | GST Engine + Double-entry | Zero-error IRAS F5 filing, PEPPOL ready |

**Quantified Business Value**: S$390,000+ annual savings per SMB through system unification and automation.

---

## 1. WHAT We Are Building

### 1.1 Bounded Contexts (Domain-Driven Design)

```
┌───────────────────────────────────────────────────────────────────────┐
│                      BOUNDED CONTEXTS (4 Complete)                     │
├────────────────┬────────────────┬────────────────┬────────────────────┤
│   ACCOUNTS     │   COMMERCE     │   INVENTORY    │   ACCOUNTING       │
│   (Identity)   │   (Sales)      │   (Stock)      │   (Finance)        │
│   61 tests ✅  │   64 tests ✅  │   57 tests ✅  │   91 tests ✅      │
├────────────────┼────────────────┼────────────────┼────────────────────┤
│ • Company      │ • Categories   │ • Locations    │ • Chart of Accounts│
│ • User         │ • Products     │ • Stock Items  │ • Journal Entries  │
│ • Role/RBAC    │ • Variants     │ • Reservations │ • Invoices         │
│               │ • Customers    │ • Movements    │ • Payments         │
│               │ • Carts        │ (Redis locks)  │ • GST Engine       │
│               │ • Orders       │               │ • F5 Returns       │
├───────────────┴────────────────┴────────────────┴────────────────────┤
│   COMPLIANCE (Phase 5 - Not Started)     │   INTEGRATIONS (Phase 5)  │
├──────────────────────────────────────────┼───────────────────────────┤
│ • GST Returns (F5)                        │ • Stripe / HitPay         │
│ • PDPA Consents + Data Access Requests    │ • Ninja Van / SingPost    │
│ • Audit Logs                              │ • Shopee / Lazada / Qoo10 │
│ • PEPPOL/InvoiceNow                       │                           │
└──────────────────────────────────────────┴───────────────────────────┘
```

### 1.2 Core Entities by Domain

| Domain | Key Models | Notable Features |
|--------|-----------|------------------|
| **Accounts** | Company, User, Role, UserRole | UEN validation, RBAC permissions, MFA-ready |
| **Commerce** | Category, Product, ProductVariant, Customer, Cart, Order, OrderItem | GST codes (SR/ZR/ES/OS), PDPA consent, F5 reporting fields |
| **Inventory** | Location, InventoryItem, Reservation, Movement | Redis distributed locks, optimistic locking, immutable audit trail |
| **Accounting** | Account, JournalEntry, JournalLine, Invoice, Payment | Balanced entry constraint, historical GST rates, PEPPOL fields |

### 1.3 Singapore-Specific Compliance (Built-In)

| Requirement | Implementation | Database Support |
|------------|----------------|-----------------|
| **GST (9% from 2024)** | Historical rate lookup via `get_gst_rate(transaction_date)` | `compliance.gst_rates` table |
| **GST F5 Returns** | Boxes 1-8 calculation from order data | `compliance.gst_returns`, order fields `gst_box_1_amount`, `gst_box_6_amount` |
| **PDPA Consent** | 6 consent types tracked | `compliance.data_consents` (Phase 5) |
| **PEPPOL/InvoiceNow** | BIS Billing 3.0 ready | Invoice `peppol_id`, `peppol_status` fields |
| **UEN Format** | 10-character validation | `core.companies.uen` (unique) |
| **Postal Code** | 6-digit Singapore format | Address fields validation |

---

## 2. WHY This Architecture

### 2.1 Business Drivers & ROI

| Pain Point | Current State | Platform Solution | Annual Impact |
|-----------|--------------|-------------------|---------------|
| System Fragmentation | 5-7 different tools | Single unified platform | S$67,200 saved |
| GST Errors | 3.2 errors/quarter | Automated GST engine | S$60,000 penalties avoided |
| Inventory Inaccuracy | 23% discrepancy | Real-time multi-location sync | S$88,000 revenue saved |
| Checkout Abandonment | 68% rate | Mobile-optimized PWA | S$120,000 revenue lift |
| **TOTAL** | — | — | **S$390,000** |

### 2.2 Architectural Philosophy

| Principle | Implementation | Rationale |
|-----------|---------------|-----------|
| **Modular Monolith MVP** | 4 Django apps under `apps/` | Faster development, easier debugging → extract to microservices at scale |
| **PostgreSQL-First** | DECIMAL precision, JSONB, tsvector, RLS | Single DB simplifies ops, ACID guaranteed |
| **Redis for Locks/Cache** | 15-second inventory locks, session cache | Prevents race conditions, improves read performance |
| **Multi-Tenancy via Company** | `company_id` FK on all domain tables | Row-Level Security policies enforce isolation |
| **Django 6.0 Features** | CSP support, background tasks ready | Modern Python 3.12+, latest Django patterns |

### 2.3 Key Technology Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Backend | Django 6.0 | Node.js/Express | Python Decimal for financial precision, built-in admin/ORM |
| API Layer | DRF + JWT | GraphQL | Simpler caching, versioned REST endpoints |
| Frontend | Next.js 14.2 | React SPA | SSR for SEO, App Router, PWA support |
| Database | PostgreSQL 16 | MySQL | DECIMAL precision, generated columns, partitioning |
| Queue | Celery + Django Tasks | RabbitMQ | Already using Redis, hybrid async approach |

---

## 3. HOW The System Is Designed

### 3.1 Technology Stack (Validated)

| Layer | Technology | Version | Validated |
|-------|------------|---------|-----------|
| **Runtime** | Python | 3.12+ | ✅ `.python-version` |
| **Web Framework** | Django | 6.0+ | ✅ `pyproject.toml` |
| **API Framework** | Django REST Framework | 3.16+ | ✅ `base.py` |
| **Authentication** | django-allauth + SimpleJWT | Latest | ✅ Token blacklist enabled |
| **Database** | PostgreSQL | 16+ | ✅ `database/schema.sql` |
| **Cache/Locks** | Redis | 7.4+ | ✅ `locks.py`, Celery config |
| **Task Queue** | Celery | 5.5+ | ✅ `config/celery.py` |
| **Frontend** | Next.js | 14.2+ | ✅ `frontend/package.json` |

### 3.2 Project Structure (Validated)

```
backend/                          # 98 Python files
├── config/                       # Django configuration
│   ├── __init__.py               # Celery app export
│   ├── settings/
│   │   ├── base.py               # Core settings, DRF, allauth, JWT
│   │   ├── development.py        # Debug, local DB
│   │   └── production.py         # Secure cookies, Sentry
│   ├── celery.py                 # Task queues, beat schedule (conditional)
│   └── urls.py                   # API versioning, Swagger
│
├── core/                         # Shared infrastructure
│   ├── models.py                 # BaseModel, AuditableModel, SoftDeleteModel
│   ├── exceptions.py             # BusinessLogicError, InsufficientStockError
│   ├── permissions.py            # IsCompanyMember, HasRole, IsOwnerOrAdmin
│   └── middleware.py             # TenantMiddleware, AuditMiddleware
│
└── apps/                         # Domain applications
    ├── accounts/                 # 19 files, 61 tests ✅
    │   ├── models.py             # Company, User, Role, UserRole
    │   ├── services.py           # AuthService, UserService, CompanyService
    │   ├── views.py              # ViewSets, Login/Logout
    │   └── tests/                # Model, view, service tests
    │
    ├── commerce/                 # 25 files, 64 tests ✅
    │   ├── models/               # Category, Product, Variant, Customer, Cart, Order
    │   ├── services/             # ProductService, CartService, OrderService
    │   ├── views.py              # 5 ViewSets with status transitions
    │   └── tests/                # GST, order state machine tests
    │
    ├── inventory/                # 24 files, 57 tests ✅
    │   ├── models/               # Location, InventoryItem, Reservation, Movement
    │   ├── locks.py              # Redis InventoryLock, MultiItemLock
    │   ├── services/             # InventoryService (reserve, release, transfer)
    │   └── tests/                # Concurrency, locking tests
    │
    └── accounting/               # 29 files, 91 tests ✅
        ├── models/               # Account, JournalEntry, JournalLine, Invoice, Payment
        ├── gst/                  # rates.py, engine.py (F5 preparation)
        ├── services/             # LedgerService, InvoiceService, PaymentService
        └── tests/                # Balanced entry, GST calculation tests
```

### 3.3 Abstract Model Hierarchy

```python
BaseModel              # UUID pk, created_at, updated_at
    └── AuditableModel     # + created_by, updated_by
    └── SoftDeleteModel    # + deleted_at, soft delete manager
        └── CompanyOwnedModel  # + company FK (multi-tenant)
```

### 3.4 RBAC System (Validated)

| Role | Permissions | Scope |
|------|-------------|-------|
| `owner` | All permissions | Company-wide |
| `admin` | User management, settings | Company-wide |
| `finance` | Accounting, GST filing | Accounting domain |
| `warehouse` | Inventory management | Inventory domain |
| `sales` | Orders, customers | Commerce domain |

**Permission Classes**:
- `IsCompanyMember` — Multi-tenant isolation
- `HasRole` / `HasAnyRole` — Role-based access
- `IsOwnerOrAdmin` — Object-level permission
- `IsFinanceUser` — Finance-sensitive operations

---

## 4. Implementation Status

### 4.1 Phase Completion Summary

| Phase | Focus | Duration | Status | Tests |
|-------|-------|----------|--------|-------|
| **Phase 1** | Foundation | Weeks 1-3 | ✅ **COMPLETE** | 61 |
| **Phase 2** | Commerce Domain | Weeks 4-6 | ✅ **COMPLETE** | 64 |
| **Phase 3** | Inventory Domain | Weeks 7-9 | ✅ **COMPLETE** | 57 |
| **Phase 4** | Accounting Domain | Weeks 10-12 | ✅ **COMPLETE** | 91 |
| Phase 5 | Compliance & Integrations | Weeks 13-15 | 🔲 Not started | - |
| Phase 6 | Frontend Foundation | Weeks 16-18 | 🔲 Not started | - |
| Phase 7 | Frontend Features | Weeks 19-22 | 🔲 Not started | - |
| Phase 8 | Testing & Deployment | Weeks 23-28 | 🔲 Not started | - |

**Total Tests Passing**: 273

### 4.2 Phase 1-4 Key Deliverables

#### Phase 1: Foundation
- Django project structure with split settings (dev/prod)
- Core models (Company, User, Role, UserRole)
- JWT authentication with token blacklist
- Custom middleware (Tenant, Audit, Security)
- Docker Compose for local Postgres/Redis
- Seed command for baseline data

#### Phase 2: Commerce Domain
- Category hierarchy with slug-based routing
- Products with GST codes (SR/ZR/ES/OS)
- Customer model with PDPA consent fields
- Order status state machine (pending → confirmed → shipped → delivered)
- F5 reporting fields on orders

#### Phase 3: Inventory Domain
- Location model (warehouse/store/virtual)
- Redis distributed locking (15s timeout, 3 retries)
- Reservation system (30-min configurable expiry)
- Immutable movement audit trail
- Optimistic locking via version field

#### Phase 4: Accounting Domain
- Chart of Accounts (hierarchical, 5 types)
- Double-entry journal with DB-level balance constraint
- Historical GST rates (1994-2024)
- F5 return preparation and validation
- Invoice lifecycle with PEPPOL fields

---

## 5. Non-Negotiable Invariants

### 5.1 Financial Precision

```python
# ✅ ALWAYS use Decimal for money
from decimal import Decimal
price = Decimal('99.99')
gst = price * Decimal('0.09')

# ❌ NEVER use float for money
price = 99.99  # WRONG - causes rounding errors
```

### 5.2 Database Field Standards

```python
# Monetary fields
models.DecimalField(max_digits=12, decimal_places=2)

# GST rate fields
models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.09'))

# Primary keys
models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```

### 5.3 Inventory Concurrency Safety

```python
# Always use Redis locks for inventory updates
with InventoryLock(item_id, timeout=15):
    # Check and update atomically
    pass

# Reservation rules:
# - Default expiry: 30 minutes
# - Constraint: reserved_qty <= available_qty
# - Net quantity: available_qty - reserved_qty
```

### 5.4 Multi-Tenancy Isolation

- Company is the tenant boundary
- All domain tables have `company_id` FK
- TenantMiddleware sets `app.current_company_id`
- RLS policies enforce isolation at DB level
- API views filter by `request.user.company`

### 5.5 GST Compliance Rules

```python
# GST Codes (rate from compliance.gst_rates table)
SR = 'Standard Rated'   # 9% from 2024-01-01
ZR = 'Zero Rated'       # 0% (exports)
ES = 'Exempt Supply'    # Financial services
OS = 'Out of Scope'     # Overseas services

# Historical rate lookup required for backdated transactions
rate = get_gst_rate(transaction_date)  # Not hardcoded!
```

---

## 6. Data Model Highlights

### 6.1 PostgreSQL Extensions

```sql
uuid-ossp     -- UUID generation
pgcrypto      -- Encryption functions
pg_trgm       -- Fuzzy text search
btree_gist    -- GiST index support
```

### 6.2 Database Schemas

```
core        -- Companies, users, roles, sequences
commerce    -- Products, customers, orders, carts
inventory   -- Locations, items, reservations, movements
accounting  -- Accounts, journals, invoices, payments
compliance  -- GST returns, consents, audit logs (Phase 5)
```

### 6.3 Critical Constraints

| Table | Constraint | Purpose |
|-------|-----------|---------|
| `accounting.journal_entries` | `total_debit = total_credit` | Double-entry enforcement |
| `accounting.journal_lines` | `(debit > 0 AND credit = 0) OR (credit > 0 AND debit = 0)` | One-side-only |
| `inventory.items` | `reserved_qty <= available_qty` | Prevent oversell |
| `commerce.cart_items` | `quantity > 0` | Valid cart items |
| `commerce.orders` | Partitioned by `order_date` (monthly) | Performance |

### 6.4 Generated/Computed Columns

| Table | Column | Expression |
|-------|--------|-----------|
| `inventory.items` | `net_qty` | `available_qty - reserved_qty` (STORED) |
| `commerce.products` | `search_vector` | tsvector from name, description, sku |
| `accounting.invoices` | `amount_due` | `total_amount - amount_paid` |

---

## 7. API Endpoints Summary

### 7.1 Accounts API (`/api/v1/accounts/`)

| Endpoint | Methods | Custom Actions |
|----------|---------|----------------|
| `/companies/` | CRUD | - |
| `/users/` | CRUD | `me/`, `assign-role/` |
| `/roles/` | CRUD | - |
| `/auth/login/` | POST | JWT generation |
| `/auth/logout/` | POST | Token blacklist |
| `/auth/token/refresh/` | POST | Token refresh |

### 7.2 Commerce API (`/api/v1/commerce/`)

| Endpoint | Methods | Custom Actions |
|----------|---------|----------------|
| `/categories/` | CRUD | `tree/` |
| `/products/` | CRUD | `search/` |
| `/customers/` | CRUD | `addresses/`, `pdpa_export/` |
| `/cart/` | - | `current/`, `add_item/`, `checkout/` |
| `/orders/` | CRUD | `confirm/`, `ship/`, `deliver/`, `cancel/` |

### 7.3 Inventory API (`/api/v1/inventory/`)

| Endpoint | Methods | Custom Actions |
|----------|---------|----------------|
| `/locations/` | CRUD | - |
| `/items/` | CRUD | `adjust/`, `transfer/`, `receive/`, `low_stock/` |
| `/movements/` | Read-only | - |
| `/reservations/` | List | `cleanup/` |

### 7.4 Accounting API (`/api/v1/accounting/`)

| Endpoint | Methods | Custom Actions |
|----------|---------|----------------|
| `/accounts/` | CRUD | `tree/`, `balances/` |
| `/journals/` | List/Create | `post/`, `void/` |
| `/invoices/` | CRUD | `send/`, `void/`, `aging/` |
| `/payments/` | List/Create | `complete/`, `refund/` |
| `/gst/f5/` | - | `prepare/`, `validate/` |
| `/reports/` | - | `trial-balance/` |

---

## 8. Upcoming Phases (5-8)

### Phase 5: Compliance & Integrations (Weeks 13-15)
- PDPA consent framework (`compliance.data_consents`)
- Data access/deletion request handling
- PEPPOL/InvoiceNow submission via Access Points
- Payment gateway integration (Stripe, HitPay)
- Logistics API (Ninja Van, SingPost)

### Phase 6: Frontend Foundation (Weeks 16-18)
- Next.js 14.2 App Router setup
- Component library with Tailwind
- API client with React Query
- Authentication flow with JWT

### Phase 7: Frontend Features (Weeks 19-22)
- Storefront with SSR product pages
- Shopping cart with PayNow QR
- Checkout flow with multiple payment methods
- Customer dashboard

### Phase 8: Testing & Deployment (Weeks 23-28)
- E2E tests with Playwright
- Performance optimization
- Security audit
- AWS ECS Fargate deployment

---

## 9. Quick Reference

### 9.1 Running the Project Locally

```bash
# Start database containers
docker compose --env-file .env.docker up -d postgres redis

# Install dependencies
cd backend && uv sync

# Load environment and run migrations
set -a && source ../.env.docker && set +a
uv run python manage.py migrate
uv run python manage.py seed

# Run tests
uv run python -m pytest -q

# Start development server
uv run python manage.py runserver
```

### 9.2 Key Configuration Files

| File | Purpose |
|------|---------|
| `backend/pyproject.toml` | Python dependencies (Django 6.0+) |
| `backend/.python-version` | Python version (3.12+) |
| `backend/config/settings/base.py` | Core Django settings |
| `database/schema.sql` | Complete PostgreSQL schema |
| `.env.docker` | Local development environment |
| `docker-compose.yml` | Postgres/Redis containers |

### 9.3 Source Documentation

| Document | Purpose |
|----------|---------|
| `AGENT.md` | Quick start for AI agents |
| `Project Architecture Document.md` | Technical architecture (PAD v2.1) |
| `PROJECT_UNDERSTANDING.md` | Business context |
| `PROJECT_DEEP_UNDERSTANDING.md` | Technical deep-dive |
| `master_execution_plan.md` | Implementation phases |
| `VALIDATED_PROJECT_UNDERSTANDING.md` | Phases 1-3 validation |
| `Phase*_completion_log.md` | Phase-specific walkthroughs |

---

## 10. Quality Assurance Checklist

Before any commit:

- [ ] All monetary values use `Decimal`, not `float`
- [ ] GST calculations use historical rate lookup when backdated
- [ ] Customer data has PDPA consent fields where applicable
- [ ] Inventory operations use Redis distributed locks
- [ ] API endpoints follow versioning (`/api/v1/`)
- [ ] Database migrations are included
- [ ] Tests cover new functionality (target: 85% unit, 70% integration)
- [ ] Type hints are complete (Python)
- [ ] Company filtering enforced for multi-tenant isolation
- [ ] Audit fields populated for tracked models

---

**Document validated against codebase on December 20, 2025**  
**Total tests passing: 273 (61 + 64 + 57 + 91)**
