# AGENT.md - AI Coding Agent Briefing Document

> **Project**: Singapore SMB E-Commerce & Integrated Business Platform
> **Version**: 1.3
> **Last Updated**: December 20, 2025

---

## 🎯 Quick Start for AI Agents

### What Is This Project?

A **unified platform for Singapore SMBs** combining:
1. **E-commerce storefront** (Next.js 14 PWA)
2. **Real-time inventory management** (Multi-location)
3. **Automated accounting with GST compliance** (IRAS-ready)

### Core Technology Stack

```
Backend:   Django 6.0+ + DRF + Celery + Django Tasks
Frontend:  Next.js 14.2+ + React 18 + TypeScript
Database:  PostgreSQL 16+ + Redis 7.4+
Infra:     AWS ECS Fargate (Singapore region)
Python:    3.12+
```

---

## 📋 Essential Context

### Business Domain

| Concept | Description |
|---------|-------------|
| **GST** | Singapore's 9% Goods and Services Tax (like VAT) |
| **IRAS** | Inland Revenue Authority of Singapore (tax authority) |
| **PDPA** | Personal Data Protection Act (Singapore's privacy law) |
| **PayNow** | Singapore's instant payment system via UEN/mobile |
| **InvoiceNow** | Government e-invoicing standard (PEPPOL-based) |
| **UEN** | Unique Entity Number (Singapore business registration) |

### Target Users

- **SMB Owners**: 10-50 employees, S$500K-S$10M revenue
- **Industries**: Retail, F&B, Health & Beauty, B2B Wholesale
- **Key Pain Points**: Manual processes, GST errors, inventory sync issues

---

## 🏗️ Project Structure (Planned)

```
singapore-smb/
├── backend/                    # Django application
│   ├── apps/
│   │   ├── accounts/          # Authentication, users, RBAC
│   │   ├── companies/         # Company profiles, GST registration
│   │   ├── products/          # Product catalog, variants
│   │   ├── inventory/         # Multi-location stock management
│   │   ├── orders/            # Order processing, state machine
│   │   ├── payments/          # Payment gateway integrations
│   │   ├── accounting/        # Chart of accounts, journal entries
│   │   ├── gst/               # GST engine, F5 returns
│   │   ├── pdpa/              # Consent management, data access
│   │   └── integrations/      # Third-party API adapters
│   ├── config/                # Django settings
│   └── manage.py
├── frontend/                   # Next.js application
│   ├── app/                   # App Router pages
│   ├── components/            # React components
│   └── lib/                   # Utilities, API clients
├── docker/                     # Docker configurations
├── docs/                       # Documentation
└── tests/                      # Test suites
```

---

## ⚠️ Critical Rules

### 1. Financial Precision

```python
# ✅ ALWAYS use Decimal for money
from decimal import Decimal
price = Decimal('99.99')
gst = price * Decimal('0.09')

# ❌ NEVER use float for money
price = 99.99  # WRONG - causes rounding errors
```

### 2. GST Codes

```python
GST_CODES = {
    'SR': 'Standard Rated (9%)',      # Local sales
    'ZR': 'Zero Rated (0%)',          # Exports
    'ES': 'Exempt Supply',            # Financial services
    'OS': 'Out of Scope',             # Overseas services
}
```

### 3. Database Fields

```python
# All monetary fields:
models.DecimalField(max_digits=12, decimal_places=2)

# GST rate fields:
models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.09'))
```

### 4. Inventory Operations

```python
# Always use Redis locks for inventory updates
with redis_lock(f"inventory:{product_id}"):
    # Update inventory atomically
    pass
```

### 5. PDPA Compliance

```python
# Customer data MUST have consent fields
class Customer:
    consent_marketing = BooleanField(default=False)  # Explicit opt-in
    consent_analytics = BooleanField(default=True)   # Can opt-out
    data_retention_until = DateField()               # Auto-purge date
```

---

## 📐 Architecture Patterns

### Backend (Django)

| Pattern | Usage |
|---------|-------|
| **Service Layer** | Business logic in `services.py`, not views |
| **Repository Pattern** | Data access abstracted from business logic |
| **Factory Pattern** | Create complex objects (orders, invoices) |
| **State Machine** | Order status transitions |
| **Adapter Pattern** | Third-party integrations (payments, logistics) |

### Frontend (Next.js)

| Pattern | Usage |
|---------|-------|
| **App Router** | File-based routing with layouts |
| **Server Components** | Default for data fetching |
| **Client Components** | Interactive elements only |
| **React Query** | Server state management |
| **Zustand** | Client state management |

### API Design

```python
# RESTful endpoints with versioning
/api/v1/products/
/api/v1/orders/
/api/v1/inventory/
/api/v1/gst/f5-preparation/
```

### Django 6.0 Security (CSP)

```python
# Django 6.0 built-in Content Security Policy (CSP)
# Configure in settings (e.g. `backend/config/csp.py`) and enable middleware.

SECURE_CSP = {
    "default-src": ["'self'"],
    "script-src": ["'self'", "'nonce-{request.csp_nonce}'", "https://js.stripe.com"],
    "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
    "img-src": ["'self'", "https://*.cloudfront.net", "data:", "blob:"],
    "connect-src": ["'self'", "https://api.stripe.com", "https://api.hit-pay.com"],
    "frame-src": ["https://js.stripe.com", "https://paynow.sg"],
    "font-src": ["'self'", "https://fonts.gstatic.com"],
    "report-uri": "/api/v1/csp-report/",
}
```

---

## 🔧 Key Integrations

### Payment Gateways

| Gateway | Purpose | Priority |
|---------|---------|----------|
| Stripe | Cards, Apple Pay, Google Pay | Primary |
| HitPay | PayNow, GrabPay, ShopeePay | Local Priority |
| 2C2P | Backup / BNPL | Fallback |

### Logistics

| Provider | Services |
|----------|----------|
| Ninja Van | Standard, Same-day, COD |
| J&T Express | Express, Economy |
| SingPost | Registered, Speedpost |

### Marketplaces

| Platform | Sync Type |
|----------|-----------|
| Shopee | Real-time orders + inventory |
| Lazada | Real-time orders + inventory |
| Qoo10 | Batch sync (hourly) |

---

## 📊 Database Schema Essentials

### Core Models (Django)

```python
class Company(models.Model):
    """Tenant/business entity"""
    name = CharField(max_length=200)
    uen = CharField(max_length=10, unique=True)  # Singapore UEN
    gst_registered = BooleanField(default=False)
    gst_registration_number = CharField(max_length=15, null=True)

class Product(models.Model):
    """Product catalog"""
    company = ForeignKey(Company)
    sku = CharField(max_length=50, unique=True, db_index=True)
    name = CharField(max_length=200)
    base_price = DecimalField(max_digits=10, decimal_places=2)
    cost_price = DecimalField(max_digits=10, decimal_places=2)
    gst_code = CharField(max_length=2, default='SR')
    gst_rate = DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.09'))

class Order(models.Model):
    """Sales orders"""
    company = ForeignKey(Company)
    customer = ForeignKey(Customer)
    order_number = CharField(max_length=50, unique=True)
    status = CharField(max_length=20)  # pending, confirmed, shipped, delivered
    subtotal = DecimalField(max_digits=12, decimal_places=2)
    gst_amount = DecimalField(max_digits=12, decimal_places=2)
    total_amount = DecimalField(max_digits=12, decimal_places=2)
```

### Essential Indexes

```sql
CREATE INDEX idx_orders_company_status ON orders(company_id, status);
CREATE INDEX idx_inventory_location ON inventory_items(location_id, product_id);
CREATE INDEX idx_products_search ON products USING GIN(to_tsvector('english', name));
```

---

## 🧪 Testing Requirements

### Coverage Targets

| Layer | Target |
|-------|--------|
| Unit Tests | 85% |
| Integration Tests | 70% |
| E2E Tests | Critical paths |

### Critical Test Cases

1. **GST Calculation**: All GST codes, edge cases, rounding
2. **Inventory Reservation**: Concurrency, race conditions
3. **Order State Machine**: Valid/invalid transitions
4. **Payment Processing**: Success, failure, timeout scenarios
5. **PDPA Compliance**: Consent capture, data export, deletion

---

## 🚀 Implementation Phases

### Current Phase: Phase 4 (Accounting Domain)

### Phase 1 (Weeks 1-3): Foundation ✅ COMPLETE
- [x] Django project setup with Docker
- [x] Core models (Company, User, Role, RBAC)
- [x] Authentication (django-allauth + JWT)
- [x] Admin panel customization
- [x] 61 tests passing

### Phase 2 (Weeks 4-6): Commerce Domain ✅ COMPLETE
- [x] Category, Product, ProductVariant models
- [x] Customer with PDPA consent fields
- [x] Cart with guest support, expiry
- [x] Order with status state machine, GST reporting
- [x] 64 tests passing

### Phase 3 (Weeks 7-9): Inventory Domain ✅ COMPLETE
- [x] Location (warehouse/store/virtual)
- [x] InventoryItem with optimistic locking
- [x] Reservation with 30-min configurable expiry
- [x] Movement audit trail (immutable)
- [x] Redis distributed locking (15s timeout)
- [x] 57 tests passing

### Phase 4 (Weeks 10-12): Accounting Domain 🔲 In Progress
- [ ] Chart of Accounts (hierarchical)
- [ ] Journal Entries with balanced constraint
- [ ] Invoices and Payments
- [ ] GST Engine with F5 returns

### Phase 5 (Weeks 13-15): Compliance & Integrations
- [ ] PDPA consent framework
- [ ] PEPPOL/InvoiceNow
- [ ] Payment gateway integration (Stripe, HitPay)
- [ ] Logistics API (Ninja Van, SingPost)

### Phase 6-8 (Weeks 16-28): Frontend & Launch
- [ ] Next.js storefront
- [ ] Checkout flow with PayNow
- [ ] PWA implementation
- [ ] Production deployment

---

## 📚 Reference Documents

| Document | Purpose | Path |
|----------|---------|------|
| **Master PRD** | Full requirements | `gemini-_hybrid-PRD.md` |
| **Project Understanding** | Technical deep-dive | `PROJECT_UNDERSTANDING.md` |
| **nex-n1_PRD** | Original feature spec | `nex-n1_PRD.md` |
| **opus-revised-PRD-2** | Architecture spec | `opus-revised-PRD-2.md` |
| **qwen-revised-PRD** | Business ROI spec | `qwen-revised-PRD.md` |

---

## ✅ Pre-Commit Checklist

Before committing any code, verify:

- [ ] All monetary values use `Decimal`, not `float`
- [ ] GST calculations use correct rates and codes
- [ ] Customer data has PDPA consent fields
- [ ] Inventory operations use distributed locks
- [ ] API endpoints follow versioning (`/api/v1/`)
- [ ] Database migrations are included
- [ ] Tests cover new functionality
- [ ] Type hints are complete (Python/TypeScript)

---

## 🆘 Common Gotchas

### 1. GST Rate History (Complete)

```python
# Singapore GST rate history - use for historical tax calculations
from datetime import date
from decimal import Decimal

def get_gst_rate(transaction_date: date) -> Decimal:
    """
    Get historical GST rate for Singapore transactions.
    
    GST History:
    - April 1, 1994: GST introduced at 3%
    - January 1, 2003: Increased to 4%
    - January 1, 2004: Increased to 5%
    - July 1, 2007: Increased to 7%
    - January 1, 2023: Increased to 8%
    - January 1, 2024: Increased to 9% (current)
    """
    GST_RATES = [
        (date(2024, 1, 1), Decimal('0.09')),  # Current rate
        (date(2023, 1, 1), Decimal('0.08')),  # 2023
        (date(2007, 7, 1), Decimal('0.07')),  # 2007-2022
        (date(2004, 1, 1), Decimal('0.05')),  # 2004-2007
        (date(2003, 1, 1), Decimal('0.04')),  # 2003
        (date(1994, 4, 1), Decimal('0.03')),  # GST introduction
        (date.min, Decimal('0.00'))           # Before GST
    ]
    
    for effective_date, rate in GST_RATES:
        if transaction_date >= effective_date:
            return rate
    return Decimal('0.00')
```

### 2. Singapore Address Format

```
Block 123 Ang Mo Kio Avenue 3
#04-567
Singapore 560123
```

### 3. PayNow QR Contains

- Merchant UEN
- Transaction amount
- Reference number
- Expiry timestamp (typically 30 minutes)

### 4. Order Status Flow

```
pending → confirmed → processing → shipped → delivered
    ↓         ↓           ↓           ↓
cancelled  cancelled   cancelled   returned
```

---

## 📞 Key Contacts & Resources

### Singapore Government APIs
- **IRAS myTax Portal**: GST filing
- **ACRA BizFile+**: Business registration
- **GoBusiness**: Licensing portal

### Payment Provider Dashboards
- **Stripe Dashboard**: stripe.com/dashboard
- **HitPay Dashboard**: dashboard.hit-pay.com

### Logistics Tracking
- **Ninja Van**: ninjavan.co/en-sg/tracking
- **SingPost**: singpost.com/track-items

---

**Remember**: When in doubt, refer to `PROJECT_UNDERSTANDING.md` for detailed context, or the master PRD (`gemini-_hybrid-PRD.md`) for authoritative requirements.
