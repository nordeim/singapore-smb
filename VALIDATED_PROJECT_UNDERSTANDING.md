# Validated Project Understanding: Singapore SMB E-Commerce Platform

> **Document Type**: AI Agent Reference Document  
> **Created**: December 19, 2025  
> **Purpose**: Comprehensive validated understanding of WHAT, WHY, and HOW for AI coding agent task alignment  
> **Validation Status**: ✅ Phase 1 Codebase Validated

---

## Executive Summary

The **Singapore SMB E-Commerce Platform** is a unified business management solution for Singapore Small and Medium Businesses (10-50 employees, S$500K-S$10M revenue). It integrates three critical functions:

| Function | Technology | Key Feature |
|----------|-----------|-------------|
| **E-commerce Storefront** | Next.js 14.2+ PWA | <2s page load, PayNow QR integration |
| **Inventory Management** | Django + Redis locks | Multi-location, real-time sync, 99.5% accuracy |
| **Automated Accounting** | Django + GST Engine | Zero-error F5 filing, IRAS-ready, PEPPOL support |

**Quantified Value**: S$390,000+ annual savings per SMB through automation, compliance, and efficiency gains.

---

## 1. WHAT We Are Building

### 1.1 Bounded Contexts (Domain-Driven Design)

```
┌─────────────────────────────────────────────────────────────────┐
│                      BOUNDED CONTEXTS                            │
├───────────────┬───────────────┬────────────────┬────────────────┤
│   ACCOUNTS    │   COMMERCE    │   INVENTORY    │   ACCOUNTING   │
│   (Identity)  │   (Sales)     │   (Stock)      │   (Finance)    │
├───────────────┼───────────────┼────────────────┼────────────────┤
│ • Company     │ • Categories  │ • Locations    │ • CoA          │
│ • User        │ • Products    │ • Stock Items  │ • Journals     │
│ • Role/RBAC   │ • Variants    │ • Reservations │ • Invoices     │
│               │ • Customers   │ • Movements    │ • Payments     │
│               │ • Carts       │ • Transfers    │ • GST Engine   │
│               │ • Orders      │               │                │
├───────────────┴───────────────┴────────────────┼────────────────┤
│   COMPLIANCE                                    │ INTEGRATIONS   │
│   (Regulatory)                                  │ (External)     │
├─────────────────────────────────────────────────┼────────────────┤
│ • GST Returns (F5)                              │ • Stripe       │
│ • PDPA Consents                                 │ • HitPay       │
│ • Data Access Requests                          │ • Ninja Van    │
│ • Audit Logs                                    │ • SingPost     │
│ • PEPPOL/InvoiceNow                             │ • Shopee/Lazada│
└─────────────────────────────────────────────────┴────────────────┘
```

### 1.2 Core Entities (Validated Against Schema)

| Entity | Schema Table | Key Fields |
|--------|--------------|------------|
| [Company](file:///home/project/singapore-smb/backend/apps/accounts/models.py#41-162) | `core.companies` | `uen` (unique), [gst_registered](file:///home/project/singapore-smb/backend/apps/accounts/models.py#149-153), `gst_registration_number`, `settings` (JSONB) |
| [User](file:///home/project/singapore-smb/backend/apps/accounts/models.py#199-346) | `core.users` | `email` (unique), `company_id`, `mfa_enabled`, `failed_login_attempts`, `locked_until` |
| [Role](file:///home/project/singapore-smb/backend/apps/accounts/models.py#352-432) | `core.roles` | `company_id`, [name](file:///home/project/singapore-smb/backend/apps/accounts/models.py#314-319), [permissions](file:///home/project/singapore-smb/backend/apps/accounts/views.py#64-69) (JSONB), `is_system` |
| `Product` | `commerce.products` | `sku`, `base_price`, `cost_price`, `gst_code`, `gst_rate`, `search_vector` (tsvector) |
| [Order](file:///home/project/singapore-smb/backend/core/exceptions.py#68-76) | `commerce.orders` (partitioned) | `order_number`, `status`, `payment_status`, `fulfillment_status`, GST box amounts |
| `InventoryItem` | `inventory.items` | `available_qty`, `reserved_qty`, `net_qty` (computed stored), [version](file:///home/project/singapore-smb/backend/.python-version) (optimistic lock) |
| [Account](file:///home/project/singapore-smb/backend/core/exceptions.py#117-121) | `accounting.accounts` | `code`, `account_type`, `current_balance` |
| `JournalEntry` | `accounting.journal_entries` | `total_debit`, `total_credit` with `balanced_entry` constraint |
| `GSTReturn` | `compliance.gst_returns` | Boxes 1-8 for F5 filing, `status`, `iras_reference` |

### 1.3 Singapore-Specific Compliance

| Requirement | Implementation | Database Support |
|------------|----------------|-----------------|
| **GST (9% from 2024-01-01)** | Historical rates lookup, `calculate_gst(amount, gst_code, transaction_date)` function | `compliance.gst_rates` table |
| **GST F5 Returns** | Quarterly filing with Boxes 1-8 | `compliance.gst_returns` |
| **PDPA Consent** | 6 consent types, explicit opt-in for marketing | `compliance.data_consents` |
| **Data Access Requests** | 30-day SLA, access/correction/deletion | `compliance.data_access_requests` |
| **PEPPOL/InvoiceNow** | BIS Billing 3.0 UBL, Access Point integration | `compliance.peppol_invoices`, `compliance.peppol_acknowledgments` |
| **UEN Format** | 10-character Singapore business registration | `core.companies.uen` (unique constraint) |

---

## 2. WHY This Architecture

### 2.1 Business Drivers

| Problem | Current State | Our Solution | Annual Impact |
|---------|--------------|--------------|---------------|
| System Fragmentation | 5-7 different tools | Single unified platform | S$67,200 saved |
| GST Errors | 3.2 errors/quarter | Automated GST engine | S$60,000 penalty avoided |
| Inventory Inaccuracy | 23% discrepancy | Real-time multi-location sync | S$88,000 revenue saved |
| Checkout Abandonment | 68% abandonment | Mobile-optimized PWA | S$120,000 revenue lift |
| **TOTAL** | - | - | **S$390,000** |

### 2.2 Architectural Philosophy

| Approach | Rationale |
|----------|-----------|
| **Modular Monolith MVP** | Reduce complexity, faster MVP, easier debugging → extract to microservices at scale |
| **PostgreSQL-First** | DECIMAL precision for finance, JSONB flexibility, tsvector search, table partitioning |
| **Redis for Cache + Locks** | Inventory concurrency, session management, Celery broker |
| **Django 6.0** | Built-in admin, ORM as source of truth, CSP support, Python 3.12+ ecosystem |
| **Multi-Tenant with RLS** | Company-based isolation, `SET app.current_company_id` for Row-Level Security |

### 2.3 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend Framework | Django 6.0 over Node.js | Financial precision (Python Decimal), built-in admin, AI/ML ecosystem |
| Frontend Framework | Next.js 14.2 over React SPA | SSR for SEO, App Router, PWA support |
| Database | PostgreSQL 16 over MySQL | DECIMAL precision, JSONB, generated columns, partitioning, RLS |
| API Design | DRF + JWT over GraphQL | Simpler caching, versioned REST endpoints |
| Background Tasks | Celery + Django Tasks | Celery for heavy/distributed, Django Tasks for lightweight async |

---

## 3. HOW The System Is Designed

### 3.1 Technology Stack (Validated)

| Layer | Technology | Version | Status |
|-------|------------|---------|--------|
| **Backend Framework** | Django | 6.0+ | ✅ Configured in [pyproject.toml](file:///home/project/singapore-smb/backend/pyproject.toml) |
| **API Layer** | Django REST Framework | 3.16+ | ✅ Configured in [base.py](file:///home/project/singapore-smb/backend/config/settings/base.py) |
| **Authentication** | django-allauth + SimpleJWT | Latest | ✅ Configured, token blacklist enabled |
| **Database** | PostgreSQL | 16+ | ✅ Schema defined in [database/schema.sql](file:///home/project/singapore-smb/database/schema.sql) |
| **Cache/Queue** | Redis | 7.4+ | ✅ Celery broker configured |
| **Frontend** | Next.js | 14.2+ | ✅ Scaffold in `frontend/` |
| **Python** | Python | 3.12+ | ✅ [.python-version](file:///home/project/singapore-smb/backend/.python-version) confirmed |

### 3.2 Project Structure (Implemented)

```
backend/
├── config/                           # Django configuration
│   ├── __init__.py                   # ✅ Celery app export
│   ├── settings/
│   │   ├── base.py                   # ✅ Core settings, DRF, allauth, JWT
│   │   ├── development.py            # ✅ Debug, local DB
│   │   └── production.py             # ✅ Secure cookies, Sentry
│   ├── celery.py                     # ✅ Task queues, beat schedule
│   ├── urls.py                       # ✅ API versioning, Swagger
│   ├── asgi.py                       # ✅ ASGI entry
│   └── wsgi.py                       # ✅ WSGI entry
│
├── core/                             # Shared infrastructure
│   ├── models.py                     # ✅ BaseModel, AuditableModel, SoftDeleteModel, CompanyOwnedModel
│   ├── exceptions.py                 # ✅ BusinessLogicError, InsufficientStockError, PaymentError, etc.
│   ├── permissions.py                # ✅ IsCompanyMember, HasRole, IsOwnerOrAdmin, IsFinanceUser
│   └── middleware.py                 # ✅ TenantMiddleware, AuditMiddleware, SecurityHeadersMiddleware
│
├── apps/
│   └── accounts/                     # ✅ Authentication, Users, RBAC
│       ├── models.py                 # ✅ Company, User, Role, UserRole
│       ├── serializers.py            # ✅ UserSerializer, CompanySerializer, LoginSerializer
│       ├── views.py                  # ✅ CompanyViewSet, UserViewSet, RoleViewSet, LoginView, LogoutView
│       ├── services.py               # ✅ AuthService, UserService, CompanyService
│       ├── admin.py                  # ✅ CompanyAdmin, UserAdmin, RoleAdmin
│       ├── urls.py                   # ✅ Router registration
│       └── tests/                    # ✅ Test package
│
└── manage.py                         # ✅ Django CLI
```

### 3.3 Core Abstract Models (Validated)

```python
# core/models.py - Inheritance hierarchy
BaseModel              # UUID pk, created_at, updated_at
    └── AuditableModel     # + created_by, updated_by
    └── SoftDeleteModel    # + deleted_at, soft delete methods
        └── CompanyOwnedModel  # + company FK (multi-tenant)
```

### 3.4 RBAC System (Validated)

| Role | Permissions | System Role |
|------|-------------|-------------|
| `owner` | All permissions | `is_system=True` |
| `admin` | User management, settings | `is_system=True` |
| `finance` | Accounting, GST filing | `is_system=True` |
| `warehouse` | Inventory management | `is_system=True` |
| `sales` | Orders, customers | `is_system=True` |

**Permission Classes Implemented**:
- [IsCompanyMember](file:///home/project/singapore-smb/backend/core/permissions.py#12-54) - Multi-tenant isolation
- [HasRole](file:///home/project/singapore-smb/backend/core/permissions.py#56-84) / [HasAnyRole](file:///home/project/singapore-smb/backend/core/permissions.py#86-107) - Role-based access
- [IsOwnerOrAdmin](file:///home/project/singapore-smb/backend/core/permissions.py#109-143) - Object-level permission
- [IsAdminUser](file:///home/project/singapore-smb/backend/core/permissions.py#145-166) - Admin-only actions
- [IsFinanceUser](file:///home/project/singapore-smb/backend/core/permissions.py#168-191) - Finance-sensitive operations

### 3.5 Middleware Stack (Validated)

| Middleware | Purpose |
|------------|---------|
| [TenantMiddleware](file:///home/project/singapore-smb/backend/core/middleware.py#33-72) | Extract company from JWT/user, set thread-local context |
| [AuditMiddleware](file:///home/project/singapore-smb/backend/core/middleware.py#74-94) | Store current user for `created_by`/`updated_by` |
| [SecurityHeadersMiddleware](file:///home/project/singapore-smb/backend/core/middleware.py#96-129) | X-Frame-Options, X-XSS-Protection, CSP |
| [RequestLoggingMiddleware](file:///home/project/singapore-smb/backend/core/middleware.py#131-174) | API request logging with duration |
| [MaintenanceModeMiddleware](file:///home/project/singapore-smb/backend/core/middleware.py#190-223) | 503 response when maintenance enabled |

### 3.6 GST Engine Design

```python
# Historical GST rate lookup (database-driven)
calculate_gst(amount, gst_code, transaction_date)
    → Queries compliance.gst_rates for effective_date <= transaction_date
    → Returns ROUND(amount * rate, 2) for SR, else 0

# GST Codes
SR = 'Standard Rated (9%)'  # Local sales
ZR = 'Zero Rated (0%)'      # Exports
ES = 'Exempt Supply'        # Financial services
OS = 'Out of Scope'         # Overseas services
```

### 3.7 Order Numbering (Concurrency-Safe)

```sql
-- core.sequences table + generate_order_number(company_id) function
-- Uses UPDATE ... RETURNING with UPSERT for race-condition safety
-- Format: {PREFIX}-{YYYYMMDD}-{PADDED_SEQUENCE}
-- Example: ORD-20251219-000001
```

---

## 4. Implementation Status

### 4.1 Phase Overview

| Phase | Focus | Duration | Status |
|-------|-------|----------|--------|
| **Phase 1** | Foundation | Weeks 1-3 | ✅ **COMPLETE** |
| Phase 2 | Commerce Domain | Weeks 4-6 | 🔲 Not started |
| Phase 3 | Inventory Domain | Weeks 7-9 | 🔲 Not started |
| Phase 4 | Accounting Domain | Weeks 10-12 | 🔲 Not started |
| Phase 5 | Compliance & Integrations | Weeks 13-15 | 🔲 Not started |
| Phase 6 | Frontend Foundation | Weeks 16-18 | 🔲 Not started |
| Phase 7 | Frontend Features | Weeks 19-22 | 🔲 Not started |
| Phase 8 | Testing & Deployment | Weeks 23-28 | 🔲 Not started |

### 4.2 Phase 1 Completion Checklist

| Component | Files | Status |
|-----------|-------|--------|
| Django project structure | `config/`, [manage.py](file:///home/project/singapore-smb/backend/manage.py) | ✅ |
| Settings (base, dev, prod) | `config/settings/*.py` | ✅ |
| Celery configuration | [config/celery.py](file:///home/project/singapore-smb/backend/config/celery.py) | ✅ |
| Core models | [core/models.py](file:///home/project/singapore-smb/backend/core/models.py) | ✅ |
| Custom exceptions | [core/exceptions.py](file:///home/project/singapore-smb/backend/core/exceptions.py) | ✅ |
| Custom permissions | [core/permissions.py](file:///home/project/singapore-smb/backend/core/permissions.py) | ✅ |
| Custom middleware | [core/middleware.py](file:///home/project/singapore-smb/backend/core/middleware.py) | ✅ |
| Accounts app models | [apps/accounts/models.py](file:///home/project/singapore-smb/backend/apps/accounts/models.py) | ✅ |
| Accounts app serializers | [apps/accounts/serializers.py](file:///home/project/singapore-smb/backend/apps/accounts/serializers.py) | ✅ |
| Accounts app views | [apps/accounts/views.py](file:///home/project/singapore-smb/backend/apps/accounts/views.py) | ✅ |
| Accounts app services | [apps/accounts/services.py](file:///home/project/singapore-smb/backend/apps/accounts/services.py) | ✅ |
| Accounts app admin | [apps/accounts/admin.py](file:///home/project/singapore-smb/backend/apps/accounts/admin.py) | ✅ |
| Accounts app URLs | [apps/accounts/urls.py](file:///home/project/singapore-smb/backend/apps/accounts/urls.py) | ✅ |
| Accounts app tests | `apps/accounts/tests/` | ✅ |
| Environment files | [.env.example](file:///home/project/singapore-smb/backend/.env.example) | ✅ |

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

### 5.3 Inventory Safety

```python
# Always use Redis locks for inventory updates
with redis_lock(f"inventory:{product_id}"):
    # Check and update atomically
    pass

# Reservations expire and are cleaned up
# Net quantity: available_qty - reserved_qty
# Constraint: reserved_qty <= available_qty
```

### 5.4 Multi-Tenancy Isolation

```python
# Company is the tenant boundary
# All queries must filter by company_id
# RLS policies enforce isolation at database level
# TenantMiddleware sets app.current_company_id
```

---

## 6. API Endpoints (Phase 1)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/accounts/companies/` | GET, POST | List/create companies |
| `/api/v1/accounts/companies/{id}/` | GET, PUT, PATCH, DELETE | Company CRUD |
| `/api/v1/accounts/users/` | GET, POST | List/create users |
| `/api/v1/accounts/users/me/` | GET | Current user profile |
| `/api/v1/accounts/users/{id}/assign-role/` | POST | Assign role to user |
| `/api/v1/accounts/roles/` | GET, POST | List/create roles |
| `/api/v1/accounts/auth/login/` | POST | User login, returns JWT |
| `/api/v1/accounts/auth/logout/` | POST | User logout, blacklist token |
| `/api/v1/accounts/auth/token/refresh/` | POST | Refresh access token |
| `/api/docs/` | GET | Swagger UI (drf-spectacular) |
| `/health/` | GET | Health check endpoint |

---

## 7. Database Schema Highlights

### 7.1 PostgreSQL Extensions

```sql
uuid-ossp     -- UUID generation
pgcrypto      -- Encryption functions
pg_trgm       -- Fuzzy text search
btree_gist    -- GiST index support
```

### 7.2 Schemas (Namespaces)

```
core        -- Companies, users, roles, sequences
commerce    -- Products, customers, orders, carts
inventory   -- Locations, items, reservations, movements
accounting  -- Accounts, journals, invoices, payments
compliance  -- GST returns, consents, audit logs, PEPPOL
```

### 7.3 Key Tables with Constraints

| Table | Key Constraints |
|-------|-----------------|
| `accounting.journal_entries` | `balanced_entry CHECK (total_debit = total_credit)` |
| `accounting.journal_lines` | `one_side_only CHECK (debit XOR credit)` |
| `inventory.items` | `valid_reserved CHECK (reserved_qty <= available_qty)` |
| `commerce.cart_items` | `quantity > 0` |
| `commerce.orders` | Partitioned by `order_date` (monthly) |

### 7.4 Computed/Generated Columns

| Table | Column | Expression |
|-------|--------|------------|
| `inventory.items` | `net_qty` | `available_qty - reserved_qty` (STORED) |
| `commerce.products` | `search_vector` | tsvector from name, description, sku (STORED) |
| `accounting.invoices` | `amount_due` | `total_amount - amount_paid` (STORED) |

---

## 8. Next Phase: Commerce Domain (Phase 2)

### 8.1 Files to Create

| File | Purpose |
|------|---------|
| `apps/commerce/__init__.py` | App package |
| `apps/commerce/apps.py` | App configuration |
| `apps/commerce/models/product.py` | Product, ProductVariant, Category |
| `apps/commerce/models/customer.py` | Customer, CustomerAddress |
| `apps/commerce/models/order.py` | Order, OrderItem |
| `apps/commerce/models/cart.py` | Cart, CartItem |
| `apps/commerce/serializers.py` | DRF serializers |
| `apps/commerce/views.py` | ViewSets |
| `apps/commerce/services/*.py` | Business logic |
| `apps/commerce/admin.py` | Django admin |
| `apps/commerce/tasks.py` | Celery tasks |
| `apps/commerce/tests/` | Test suite |

### 8.2 Key Considerations

1. **Product GST codes** must default to 'SR' with rate 0.09
2. **Order totals** calculated with DECIMAL precision
3. **Cart expiration** after 7 days (guest carts)
4. **Cart merge** on customer login
5. **Order state machine** with valid transitions
6. **Order numbering** via `generate_order_number(company_id)`

---

## 9. Reference Quick Links

| Document | Purpose | Location |
|----------|---------|----------|
| AGENT.md | Quick start for AI agents | [/home/project/singapore-smb/AGENT.md](file:///home/project/singapore-smb/AGENT.md) |
| Project Architecture Document | Technical architecture | [/home/project/singapore-smb/Project Architecture Document.md](file:///home/project/singapore-smb/Project%20Architecture%20Document.md) |
| PROJECT_UNDERSTANDING.md | Business context | [/home/project/singapore-smb/PROJECT_UNDERSTANDING.md](file:///home/project/singapore-smb/PROJECT_UNDERSTANDING.md) |
| PROJECT_DEEP_UNDERSTANDING.md | Technical deep-dive | [/home/project/singapore-smb/PROJECT_DEEP_UNDERSTANDING.md](file:///home/project/singapore-smb/PROJECT_DEEP_UNDERSTANDING.md) |
| master_execution_plan.md | Implementation phases | [/home/project/singapore-smb/master_execution_plan.md](file:///home/project/singapore-smb/master_execution_plan.md) |
| database/schema.sql | Complete PostgreSQL schema | [/home/project/singapore-smb/database/schema.sql](file:///home/project/singapore-smb/database/schema.sql) |

---

## 10. Quality Assurance Checklist

Before any commit:

- [ ] All monetary values use `Decimal`, not `float`
- [ ] GST calculations use correct rates and codes
- [ ] Customer data has PDPA consent fields
- [ ] Inventory operations use distributed locks
- [ ] API endpoints follow versioning (`/api/v1/`)
- [ ] Database migrations are included
- [ ] Tests cover new functionality
- [ ] Type hints are complete (Python/TypeScript)
- [ ] Company filtering for multi-tenant isolation
- [ ] Audit fields populated for tracked models

---

**Document saved to**: [/home/pete/.gemini/antigravity/brain/c68464d0-90e3-4d82-b89e-60dfdae6a4d3/VALIDATED_PROJECT_UNDERSTANDING.md](file:///home/pete/.gemini/antigravity/brain/c68464d0-90e3-4d82-b89e-60dfdae6a4d3/VALIDATED_PROJECT_UNDERSTANDING.md)

This document serves as the authoritative reference for AI coding agent alignment with the Singapore SMB E-Commerce Platform project.
