Awesome understanding! Please help me meticulously review and analyze the project documents below to have a deep understanding of the WHAT, WHY and HOW of the project and its codebase design and architecture.

# Singapore SMB E-Commerce Platform - Project Understanding

> **Document Purpose**: Comprehensive knowledge base for AI coding agents and developers working on this project.
> **Last Updated**: December 18, 2025
> **Status**: Foundation Phase - Pre-Implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Context](#2-business-context)
3. [Technical Architecture](#3-technical-architecture)
4. [Core Domain Models](#4-core-domain-models)
5. [Compliance Framework](#5-compliance-framework)
6. [Integration Landscape](#6-integration-landscape)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Key Design Decisions](#8-key-design-decisions)
9. [Critical Success Factors](#9-critical-success-factors)
10. [Reference Materials](#10-reference-materials)

---

## 1. Executive Summary

### 1.1 What We're Building

A **unified business platform** for Singapore Small and Medium Businesses (SMBs) that integrates three critical functions:

| Function | Description | Key Differentiator |
|----------|-------------|-------------------|
| **E-commerce Storefront** | Mobile-first PWA with 70% mobile traffic target | <2s page load, PayNow integration |
| **Inventory Management** | Multi-location real-time tracking | Redis locks for sync, 99.5% accuracy |
| **Automated Accounting** | Double-entry with GST compliance | Zero-error F5 filing, IRAS integration |

### 1.2 Why It Matters

**Quantified Value per SMB:**
- **S$390,000+** annual savings/revenue lift
- **60%** reduction in manual processes
- **100%** GST compliance (vs 3.2 errors/quarter average)
- **65%** checkout completion (vs 32% industry average)

### 1.3 Target Market

- **Business Size**: 10-50 employees, S$500K-S$10M revenue
- **Industries**: Retail (35%), F&B (25%), Health & Beauty (20%), B2B Wholesale (20%)
- **Geographic Focus**: Singapore (with future ASEAN expansion)

---

## 2. Business Context

### 2.1 Market Opportunity

- **Market Size**: US$4.5B (2024), projected US$5.0B by 2025
- **Mobile Commerce**: 70% of transactions via smartphones
- **Digital Wallet Adoption**: 39% of e-commerce payments
- **Government Support**: PSG grants up to S$30,000 for digital solutions

### 2.2 Primary Pain Points We Solve

| Problem | Current State | Our Solution | Annual Impact |
|---------|--------------|--------------|---------------|
| System Fragmentation | 5-7 different tools | Single unified platform | S$67,200 saved |
| GST Errors | 3.2 errors/quarter | Automated GST engine | S$60,000 penalty avoided |
| Inventory Inaccuracy | 23% discrepancy | Real-time multi-location sync | S$88,000 revenue saved |
| Manual Data Entry | 16 hours/week | 60% automation | S$38,400 labor saved |
| Checkout Abandonment | 68% abandonment | Mobile-optimized PWA | S$120,000 revenue lift |
| Compliance Penalties | Manual compliance | Automated PDPA/GST monitoring | S$16,400 risk avoided |
| **TOTAL** | - | - | **S$390,000** |

### 2.3 User Personas

#### Primary: Sarah Chen (SMB Owner)
- **Profile**: Fashion retailer, S$1.8M revenue, 12 employees
- **Pain Points**: Manual reconciliation (2hrs/day), GST filing (3 days/quarter)
- **Goals**: Unified dashboard, zero GST penalties, scale to S$5M
- **Platform Mode**: STANDARD (upgrade path to ADVANCED)

#### Secondary Personas
- **David Wong (Finance Manager)**: Needs automated journals, 1-day month-end close
- **Priya Sharma (Operations Manager)**: Needs <5 min inventory sync, barcode scanning
- **Emma Tan (End Customer)**: Mobile-first, <2s load time, cart persistence

---

## 3. Technical Architecture

### 3.1 Technology Stack

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| **Backend Framework** | Django | 6.0+ | Financial precision, built-in admin, ORM as source of truth, CSP support |
| **API Layer** | Django REST Framework | 3.16+ | JWT auth, serialization, versioning |
| **Frontend Framework** | Next.js | 14.2+ | App Router, SSR/SSG, PWA support |
| **Language** | Python / TypeScript | 3.12+ / 5.x | Type safety, Django 6.0 requires Python 3.12+ |
| **Database** | PostgreSQL | 16+ | ACID compliance, DECIMAL precision, JSONB |
| **Cache** | Redis | 7.4+ | Inventory locks, session management, Celery broker |
| **Queue** | Celery + Django Tasks | 5.5+ | Async order processing, marketplace sync (hybrid approach) |
| **Search** | PostgreSQL tsvector | - | Cost-effective for MVP (Elasticsearch for scale) |
| **Infrastructure** | AWS ECS Fargate | - | Cost-effective, managed containers |
| **CDN** | CloudFront | - | Global edge caching |

### 3.2 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────┬─────────────────┬─────────────────────────────────────────┤
│   Web PWA       │   Mobile PWA    │         Admin Dashboard                 │
│   (Next.js)     │   (Next.js)     │         (Django Admin)                  │
└────────┬────────┴────────┬────────┴──────────────────┬──────────────────────┘
         │                 │                           │
         ▼                 ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (AWS)                                    │
│                    Rate Limiting, Auth, CORS                                 │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                                    │
├─────────────────┬─────────────────┬─────────────────────────────────────────┤
│  Django 5.x     │  Celery Workers │         Django Channels                 │
│  (DRF APIs)     │  (Async Tasks)  │         (WebSockets)                    │
└────────┬────────┴────────┬────────┴──────────────────┬──────────────────────┘
         │                 │                           │
         ▼                 ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                         │
├─────────────────┬─────────────────┬─────────────────────────────────────────┤
│  PostgreSQL 15  │   Redis 7.x     │         S3 (Media)                      │
│  (Primary DB)   │   (Cache/Queue) │         (File Storage)                  │
└─────────────────┴─────────────────┴─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL INTEGRATIONS                                 │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────────────────┤
│ Stripe   │ HitPay   │ NinjaVan │ IRAS     │ Shopee   │ InvoiceNow           │
│ (Cards)  │ (PayNow) │ (Logis)  │ (GST)    │ (Mkt)    │ (PEPPOL)             │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────────────────┘
```

### 3.3 Key Architectural Patterns

1. **Repository Pattern**: Clean separation between data access and business logic
2. **Service Layer**: Business logic encapsulated in service classes
3. **Event-Driven**: Celery for async operations, webhooks for integrations
4. **CQRS (Light)**: Separate read models for reporting/analytics
5. **Distributed Locking**: Redis locks for inventory synchronization

---

## 4. Core Domain Models

### 4.1 Entity Relationship Overview

```
┌─────────┐       ┌─────────┐       ┌─────────────┐
│ Company │──────<│ Product │──────<│ InventoryItem│
└─────────┘       └─────────┘       └─────────────┘
     │                 │                   │
     │                 │                   │
     ▼                 ▼                   ▼
┌─────────┐       ┌─────────┐       ┌─────────────┐
│ Customer│──────<│  Order  │──────<│  OrderItem  │
└─────────┘       └─────────┘       └─────────────┘
     │                 │
     │                 │
     ▼                 ▼
┌─────────────┐   ┌─────────────┐
│ DataConsent │   │ JournalEntry│
└─────────────┘   └─────────────┘
```

### 4.2 Critical Model Fields

#### Financial Fields (DECIMAL Precision Required)

```python
# All monetary fields MUST use DECIMAL(12,2) or DECIMAL(10,2)
# NEVER use FLOAT for financial calculations

class Order(models.Model):
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
class Product(models.Model):
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.09)
```

#### GST Codes

```python
GST_CODES = [
    ('SR', 'Standard Rated (9%)'),
    ('ZR', 'Zero Rated (Exports)'),
    ('ES', 'Exempt Supply'),
    ('OS', 'Out of Scope'),
]
```

#### Inventory Net Quantity (Computed Field)

```python
class InventoryItem(models.Model):
    available_qty = models.IntegerField(default=0)
    reserved_qty = models.IntegerField(default=0)
    
    @property
    def net_qty(self):
        return self.available_qty - self.reserved_qty
```

### 4.3 Database Indexes (Performance Critical)

```sql
-- Essential indexes for operational performance
CREATE INDEX idx_orders_company_status ON orders(company_id, status);
CREATE INDEX idx_inventory_net_qty ON inventory_items(available_qty - reserved_qty);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_products_search ON products USING GIN(to_tsvector('english', name || ' ' || description));
CREATE INDEX idx_gst_f5_status ON gst_f5_returns(company_id, status);
```

---

## 5. Compliance Framework

### 5.1 GST Compliance (IRAS)

#### Current Rate: 9% (as of January 1, 2024)

#### GST Registration Threshold: S$1,000,000 rolling 12-month revenue

#### F5 Return Boxes

| Box | Description | Calculation |
|-----|-------------|-------------|
| Box 1 | Total value of standard-rated supplies | Sum of taxable sales |
| Box 2 | Total value of zero-rated supplies | Export sales |
| Box 3 | Total value of exempt supplies | Financial services, etc. |
| Box 4 | Total supplies (1+2+3) | Computed |
| Box 5 | Total taxable purchases | Purchases with GST |
| Box 6 | Output tax due | Box 1 × 9% |
| Box 7 | Input tax claimable | From supplier invoices |
| Box 8 | Net GST payable | Box 6 - Box 7 |

#### GST Engine Requirements

```python
class GSTEngine:
    """Core GST calculation and reporting engine"""
    
    def calculate_gst(self, amount: Decimal, gst_code: str) -> Decimal:
        """Calculate GST for a transaction"""
        if gst_code == 'SR':
            return amount * Decimal('0.09')
        return Decimal('0')
    
    def prepare_f5_return(self, company_id: int, period_start: date, period_end: date) -> dict:
        """Generate F5 return data for IRAS submission"""
        # Implementation details in accounting module
        pass
```

### 5.2 PDPA Compliance

#### Key Requirements

| Requirement | Implementation | Deadline |
|-------------|----------------|----------|
| Consent Management | Explicit opt-in for marketing | At registration |
| Data Access Request | Export customer data | 30 days |
| Data Deletion | Anonymize on request | 30 days |
| Breach Notification | Alert PDPC | 72 hours |
| Data Retention | Auto-purge per policy | 7 years (financial), 3 years (customer) |

#### Customer Consent Fields

```python
class Customer(models.Model):
    consent_marketing = models.BooleanField(default=False)
    consent_analytics = models.BooleanField(default=True)
    consent_timestamp = models.DateTimeField(null=True)
    data_retention_until = models.DateField(null=True)
```

### 5.3 InvoiceNow (PEPPOL)

- **Standard**: PEPPOL BIS Billing 3.0
- **Integration**: Via Singapore Access Point Providers (e.g., Peppol.sg)
- **Requirement**: B2G (Business-to-Government) transactions must use PEPPOL

#### PEPPOL BIS 3.0 Invoice Structure

```python
# Required PEPPOL legal_monetary_totals structure
peppol_invoice = {
    'legal_monetary_totals': {
        'line_extension_amount': Decimal('0.00'),      # Sum of line amounts
        'tax_exclusive_amount': Decimal('0.00'),       # Total before tax
        'tax_inclusive_amount': Decimal('0.00'),       # Total after tax
        'allowance_total_amount': Decimal('0.00'),     # Total discounts
        'charge_total_amount': Decimal('0.00'),        # Shipping charges
        'prepaid_amount': Decimal('0.00'),             # Amount already paid
        'payable_amount': Decimal('0.00'),             # Amount due
    },
    'tax_total': {
        'taxable_amount': Decimal('0.00'),
        'tax_amount': Decimal('0.00'),
        'percent': Decimal('9.00'),                    # Singapore GST rate
        'tax_category_code': 'S',                      # Standard rated
    }
}
```

### 5.4 Industry-Specific Licenses

| Industry | Authority | License Type |
|----------|-----------|--------------|
| F&B | SFA (Singapore Food Agency) | Food Shop License |
| Health & Beauty | HSA (Health Sciences Authority) | Product Registration |
| Alcohol | SPF (Singapore Police Force) | Liquor License |

---

## 6. Integration Landscape

### 6.1 Payment Gateways

| Gateway | Methods | Priority | Settlement |
|---------|---------|----------|------------|
| **Stripe** | Visa, MC, Amex, Apple Pay, Google Pay | Primary | T+2 |
| **HitPay** | PayNow QR, GrabPay, ShopeePay, Atome | Local Priority | T+1 |
| **2C2P** | Cards, wallets, BNPL | Backup | T+2 |

#### PayNow Integration (Critical)

```python
def generate_paynow_qr(amount: Decimal, reference: str) -> str:
    """Generate PayNow QR code for payment"""
    # UEN-based PayNow for business
    # Requires bank API integration for verification
    pass
```

### 6.2 Logistics Providers

| Provider | Services | API Version |
|----------|----------|-------------|
| **Ninja Van** | Standard, Same-day, COD | v2.1 |
| **J&T Express** | Express, Economy | v1.0 |
| **SingPost** | Registered, Speedpost | v2.0 |

### 6.3 Marketplaces

| Platform | Sync Type | Inventory Sync |
|----------|-----------|----------------|
| **Shopee** | Orders import, Inventory push | Real-time |
| **Lazada** | Orders import, Inventory push | Real-time |
| **Qoo10** | Orders import, Inventory push | Batch (hourly) |

### 6.4 Government APIs

| System | Purpose | Integration Status |
|--------|---------|-------------------|
| IRAS | GST F5 submission | Stubs (Phase 2) |
| SingPass | Customer authentication | Future |
| CorpPass | Business API access | Future |
| InvoiceNow | PEPPOL e-invoicing | Phase 5 |

---

## 7. Implementation Roadmap

### 7.1 Phase Overview (28 Weeks Total)

| Phase | Duration | Focus | Validation Gate |
|-------|----------|-------|-----------------|
| **Phase 1** | Weeks 1-6 | Foundation (Infra, Auth, Core Models) | MVP infrastructure stable |
| **Phase 2** | Weeks 7-10 | Compliance (GST Engine, PDPA) | Core compliance validated |
| **Phase 3** | Weeks 11-16 | E-Commerce Backend (Orders, Payments, Logistics) | Full order lifecycle |
| **Phase 4** | Weeks 17-22 | Next.js Frontend (Storefront, Checkout, PWA) | E2E customer journey |
| **Phase 5** | Weeks 23-28 | Integration & Launch (Marketplaces, Security, UAT) | Production launch |

### 7.2 Phase 1 Breakdown (Foundation)

#### Sprint 1-2: Infrastructure Setup
- [ ] AWS VPC, subnets, security groups
- [ ] Docker Compose for local development
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] PostgreSQL with replication config
- [ ] Redis cluster setup

#### Sprint 3-4: Core Models & Admin
- [ ] Company model with GST registration
- [ ] Product model with GST codes
- [ ] Customer model with PDPA fields
- [ ] Order model with financial precision
- [ ] Django Admin customization (Jazzmin)

#### Sprint 5-6: Authentication & API Foundation
- [ ] Django-allauth integration
- [ ] JWT token system (DRF SimpleJWT)
- [ ] RBAC permission system
- [ ] API versioning (`/api/v1/`)
- [ ] Swagger/OpenAPI documentation

---

## 8. Key Design Decisions

### 8.1 Why Django over Node.js?

| Factor | Django Advantage |
|--------|------------------|
| **Financial Precision** | Python Decimal vs JavaScript float issues |
| **Admin Panel** | Built-in, powerful, customizable |
| **ORM as Single Source of Truth** | Strong model layer |
| **AI/ML Integration** | Native Python ecosystem |
| **Proven Scale** | Instagram, Pinterest, Disqus |

### 8.2 Why Next.js over React SPA?

| Factor | Next.js Advantage |
|--------|-------------------|
| **SEO** | Server-side rendering for product pages |
| **Performance** | Static generation for catalog |
| **PWA** | Built-in service worker support |
| **Mobile** | App Router for modern mobile UX |

### 8.3 Why PostgreSQL over MySQL?

| Factor | PostgreSQL Advantage |
|--------|----------------------|
| **DECIMAL Precision** | Critical for financial data |
| **JSONB** | Flexible product attributes |
| **Full-text Search** | tsvector for MVP search |
| **Generated Columns** | Computed net_qty |
| **Partitioning** | Time-based order partitioning |

### 8.4 Inventory Reservation Strategy

```python
# Use Redis distributed locks for inventory operations
def reserve_inventory(product_id: int, qty: int, order_id: int) -> bool:
    lock_key = f"inventory_lock:{product_id}"
    with redis_client.lock(lock_key, timeout=10):
        inventory = InventoryItem.objects.select_for_update().get(product_id=product_id)
        if inventory.net_qty >= qty:
            inventory.reserved_qty += qty
            inventory.save()
            InventoryReservation.objects.create(
                product_id=product_id,
                quantity=qty,
                order_id=order_id,
                expires_at=timezone.now() + timedelta(minutes=30)
            )
            return True
        return False
```

---

## 9. Critical Success Factors

### 9.1 Technical KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time | <200ms (95th percentile) | Real-time |
| Page Load (Mobile) | <2.0s | Lighthouse |
| System Uptime | 99.9% | CloudWatch |
| GST Filing Accuracy | 100% | Quarterly audit |
| Inventory Accuracy | 99.5% | Daily cycle count |

### 9.2 Business KPIs

| Metric | Target | Timeline |
|--------|--------|----------|
| Monthly Recurring Revenue | S$50,000 | Month 6 |
| Active SMB Clients | 100 | Month 6 |
| Customer Churn Rate | <3% monthly | Ongoing |
| Order Processing Time | <8 hours | Day 1 launch |

### 9.3 Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Marketplace sync race conditions | High | High | Redis distributed locks, Celery queues |
| Django/Next.js auth mismatch | Medium | High | Strict JWT implementation, HttpOnly cookies |
| GST F5 validation errors | Medium | High | Comprehensive unit tests, manual review |
| PayNow QR failure | Low | Medium | HitPay fallback, error handling |

---

## 10. Reference Materials

### 10.1 Source PRD Documents

| Document | Focus | Location |
|----------|-------|----------|
| `nex-n1_PRD.md` | Feature requirements, payments | `/home/project/singapore-smb/` |
| `opus-revised-PRD-2.md` | Technical architecture, security | `/home/project/singapore-smb/` |
| `qwen-revised-PRD.md` | ROI analysis, business rules | `/home/project/singapore-smb/` |
| `gemini-_hybrid-PRD.md` | **Master PRD (use this)** | `/home/project/singapore-smb/` |

### 10.2 External References

- [IRAS GST Guidelines](https://www.iras.gov.sg/taxes/goods-services-tax-(gst))
- [Singapore PDPA](https://www.pdpc.gov.sg/overview-of-pdpa)
- [InvoiceNow / PEPPOL](https://www.imda.gov.sg/how-we-can-help/nationwide-e-invoicing-framework)
- [Django Documentation](https://docs.djangoproject.com/)
- [Next.js Documentation](https://nextjs.org/docs)

### 10.3 Singapore-Specific Resources

- **PayNow UEN Format**: 10-character UEN + optional suffix
- **Postal Code Format**: 6 digits (e.g., 018956)
- **GST Registration Number**: M + 8 digits + letter (e.g., M90012345A)
- **UEN Format**: 9/10 alphanumeric characters

---

# AGENT.md - AI Coding Agent Briefing Document

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

### Current Phase: Pre-Implementation (Foundation Planning)

### Phase 1 (Weeks 1-6): Foundation
- [ ] Django project setup with Docker
- [ ] Core models (Company, Product, Customer, Order)
- [ ] Authentication (django-allauth + JWT)
- [ ] Admin panel customization
- [ ] CI/CD pipeline

### Phase 2 (Weeks 7-10): Compliance Core
- [ ] GST Engine implementation
- [ ] F5 return preparation
- [ ] PDPA consent framework
- [ ] Audit trail system

### Phase 3 (Weeks 11-16): E-Commerce Backend
- [ ] Order management with state machine
- [ ] Inventory reservation system
- [ ] Payment gateway integration
- [ ] Logistics API integration

### Phase 4 (Weeks 17-22): Frontend
- [ ] Next.js storefront
- [ ] Checkout flow with PayNow
- [ ] PWA implementation
- [ ] Mobile optimization

### Phase 5 (Weeks 23-28): Launch
- [ ] Marketplace integrations
- [ ] Security audit
- [ ] Performance testing
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

# Singapore SMB E-Commerce Platform
## Project Architecture Document (PAD)
### Version 2.0 - Re-imagined Architecture

---

## Document Control

| Attribute | Details |
|-----------|---------|
| **Version** | 2.1 |
| **Date** | December 19, 2025 |
| **Status** | Final - Ready for Implementation |
| **Database** | PostgreSQL 16+ |
| **Backend** | Django 6.0+ |
| **Frontend** | Next.js 14.2+ |
| **Python** | 3.12+ |

---

## Table of Contents

1. [Architecture Vision](#1-architecture-vision)
2. [Architecture Principles](#2-architecture-principles)
3. [System Architecture](#3-system-architecture)
4. [Application Architecture](#4-application-architecture)
5. [Database Schema](#5-database-schema)
6. [API Architecture](#6-api-architecture)
7. [Security Architecture](#7-security-architecture)
8. [Integration Architecture](#8-integration-architecture)
9. [Performance Architecture](#9-performance-architecture)
10. [Deployment Architecture](#10-deployment-architecture)

---

## 1. Architecture Vision

### 1.1 Re-imagined Architecture Philosophy

After deep analysis of the original PAD and PRD documents, I've re-imagined the architecture with these key insights:

| Original Approach | Re-imagined Approach | Rationale |
|-------------------|---------------------|-----------|
| Microservices from Day 1 | **Modular Monolith** (MVP) → Microservices (Scale) | Reduce complexity, faster MVP, easier debugging |
| MongoDB for documents | **PostgreSQL JSONB** for all | Single database simplifies ops, ACID guaranteed |
| Elasticsearch for search | **PostgreSQL tsvector** (MVP) | Cost-effective, reduces infrastructure |
| Kong API Gateway | **Django + Nginx** (MVP) | Simpler ops, upgrade to Kong at scale |
| RabbitMQ | **Redis + Celery** | Already using Redis for cache, reduce components |

### 1.2 Key Architecture Decisions

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE EVOLUTION PATH                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   MVP (Month 1-6)          Scale (Month 7-12)      Enterprise   │
│   ─────────────────        ─────────────────       ──────────   │
│   Modular Monolith    →    Service Extraction  →  Microservices │
│   PostgreSQL only     →    + Redis Cluster     →  + Elasticsearch│
│   Django Admin        →    + Custom Admin      →  + React Admin │
│   ECS Fargate         →    + Auto-scaling      →  EKS Kubernetes│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Principles

### 2.1 Core Principles

| Principle | Implementation |
|-----------|---------------|
| **Domain-Driven Design** | Bounded contexts: Commerce, Inventory, Accounting, Compliance |
| **Clean Architecture** | Entities → Use Cases → Interfaces → Frameworks |
| **DECIMAL Precision** | All monetary fields use `DECIMAL(12,2)` or `DECIMAL(10,2)` |
| **Event-Driven** | Domain events via Django signals + Celery + Django Tasks |
| **API-First** | OpenAPI 3.0 specification, versioned endpoints |
| **Security by Design** | OWASP Top 10, PDPA, PCI DSS tokenization, CSP headers |

### 2.2 Bounded Contexts

```
┌─────────────────────────────────────────────────────────────────┐
│                      BOUNDED CONTEXTS                            │
├───────────────┬───────────────┬────────────────┬────────────────┤
│   COMMERCE    │   INVENTORY   │   ACCOUNTING   │   COMPLIANCE   │
├───────────────┼───────────────┼────────────────┼────────────────┤
│ • Products    │ • Locations   │ • Chart of Acc │ • GST Engine   │
│ • Orders      │ • Stock Levels│ • Journals     │ • PDPA Manager │
│ • Customers   │ • Movements   │ • Invoices     │ • Audit Logs   │
│ • Cart        │ • Reservations│ • Payments     │ • Consent      │
│ • Promotions  │ • Transfers   │ • Bank Recon   │ • Data Retention│
└───────────────┴───────────────┴────────────────┴────────────────┘
```

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
                                    ┌─────────────────┐
                                    │   CloudFront    │
                                    │      CDN        │
                                    └────────┬────────┘
                                             │
┌─────────────┐    ┌─────────────┐    ┌──────┴───────┐
│  Next.js    │    │   Mobile    │    │    Nginx     │
│  Frontend   │───▶│    PWA      │───▶│   + WAF      │
│  (Vercel)   │    │             │    │              │
└─────────────┘    └─────────────┘    └──────┬───────┘
                                             │
                        ┌────────────────────┼────────────────────┐
                        │                    │                    │
                        ▼                    ▼                    ▼
              ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
              │  Django App     │  │  Django Admin   │  │  Celery Workers │
              │  (DRF APIs)     │  │  (Jazzmin)      │  │  (Background)   │
              └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
                       │                    │                    │
                       └────────────────────┼────────────────────┘
                                            │
              ┌─────────────────────────────┼─────────────────────────────┐
              │                             │                             │
              ▼                             ▼                             ▼
    ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
    │  PostgreSQL 16  │          │   Redis 7.x     │          │   AWS S3        │
    │  (RDS Multi-AZ) │          │  (ElastiCache)  │          │  (Media/Files)  │
    └─────────────────┘          └─────────────────┘          └─────────────────┘
```

### 3.2 Django Application Structure

```
backend/                        # Existing folder (pyproject.toml, .python-version)
├── config/                     # Django configuration
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py            # Shared settings
│   │   ├── development.py     # Dev settings
│   │   ├── staging.py         # Staging settings
│   │   └── production.py      # Production settings
│   ├── urls.py                # Root URL configuration
│   ├── celery.py              # Celery app configuration
│   ├── asgi.py                # ASGI entry point
│   └── wsgi.py                # WSGI entry point
│
├── apps/
│   ├── accounts/              # Authentication, Users, RBAC
│   │   ├── models.py          # User, Company, Role
│   │   ├── serializers.py     # DRF serializers
│   │   ├── views.py           # ViewSets
│   │   ├── urls.py            # URL routing
│   │   ├── services.py        # Business logic
│   │   ├── admin.py           # Django admin
│   │   └── tests/             # Unit tests
│   │
│   ├── commerce/              # E-commerce domain
│   │   ├── models/
│   │   │   ├── product.py     # Product, ProductVariant, Category
│   │   │   ├── order.py       # Order, OrderItem, OrderStatus
│   │   │   ├── customer.py    # Customer, Address, Cart
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── product_service.py
│   │   │   ├── order_service.py
│   │   │   └── cart_service.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tasks.py           # Celery tasks
│   │   └── tests/
│   │
│   ├── inventory/             # Inventory domain
│   │   ├── models.py          # Location, InventoryItem, Movement
│   │   ├── services.py        # ReservationService, TransferService
│   │   ├── locks.py           # Redis distributed locks
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tasks.py
│   │   └── tests/
│   │
│   ├── accounting/            # Accounting domain
│   │   ├── models.py          # Account, JournalEntry, Invoice
│   │   ├── services.py        # LedgerService, ReconciliationService
│   │   ├── gst/               # GST engine
│   │   │   ├── engine.py      # GSTCalculator, F5Preparer
│   │   │   └── rates.py       # Historical GST rates
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tasks.py
│   │   └── tests/
│   │
│   ├── payments/              # Payment processing
│   │   ├── gateways/          # Stripe, HitPay adapters
│   │   │   ├── base.py
│   │   │   ├── stripe_adapter.py
│   │   │   └── hitpay_adapter.py
│   │   ├── services.py        # PaymentOrchestrator
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── compliance/            # Regulatory compliance
│   │   ├── models.py          # GSTReturn, DataConsent, AuditLog
│   │   ├── pdpa.py            # PDPA service
│   │   ├── audit.py           # Audit logging
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   └── integrations/          # Third-party integrations
│       └── logistics/         # NinjaVan, SingPost
│           ├── ninjavan.py
│           └── singpost.py
│
├── core/                      # Shared infrastructure
│   ├── models.py              # BaseModel with audit fields
│   ├── exceptions.py          # Custom exceptions
│   ├── permissions.py         # RBAC permissions
│   └── middleware.py          # Security, logging middleware
│
├── manage.py
├── pyproject.toml             # ✅ Existing - Django 6.0+, DRF, Celery
├── .python-version            # ✅ Existing - Python 3.12
├── uv.lock                    # ✅ Existing - Dependency lock
└── README.md                  # ✅ Existing

frontend/                       # Existing folder (package.json)
├── src/
│   ├── app/                   # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx           # Homepage
│   │   ├── products/
│   │   ├── cart/
│   │   ├── checkout/
│   │   ├── account/
│   │   ├── login/
│   │   └── register/
│   ├── components/
│   │   ├── ui/                # Base components
│   │   ├── layout/            # Header, Footer
│   │   ├── products/          # Product cards, grid
│   │   └── checkout/          # Address, payment forms
│   ├── lib/
│   │   ├── api/               # API client, endpoints
│   │   └── hooks/             # useAuth, useCart
│   └── types/                 # TypeScript types
├── package.json               # ✅ Existing - Next.js 14, React Query
└── next.config.js
```

---

## 4. Application Architecture

### 4.1 Service Layer Pattern

```python
# Core service pattern used throughout the application
class BaseService:
    """Base service with transaction management and logging"""
    
    def __init__(self, user=None, company=None):
        self.user = user
        self.company = company
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @transaction.atomic
    def execute(self, *args, **kwargs):
        """Execute with automatic transaction management"""
        try:
            result = self._execute(*args, **kwargs)
            self._publish_events()
            return result
        except Exception as e:
            self.logger.error(f"Service error: {e}")
            raise
    
    def _execute(self, *args, **kwargs):
        raise NotImplementedError
    
    def _publish_events(self):
        """Publish domain events via Celery"""
        for event in self._pending_events:
            publish_event.delay(event)
```

### 4.2 Order Processing Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Create  │───▶│  Reserve │───▶│  Process │───▶│  Create  │───▶│   Send   │
│  Order   │    │ Inventory│    │  Payment │    │  Invoice │    │  Notify  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
 OrderCreated   StockReserved   PaymentDone    InvoiceCreated  NotifySent
   (Event)        (Event)        (Event)         (Event)        (Event)
```

---

## 5. Database Schema

### 5.1 PostgreSQL 16 Complete Schema

See **Section 5.2** for the complete SQL schema file.

### 5.2 Schema Design Principles

1. **UUID Primary Keys**: All tables use UUID for distributed-friendly IDs
2. **DECIMAL for Money**: `DECIMAL(12,2)` for amounts, `DECIMAL(5,4)` for rates
3. **Audit Fields**: `created_at`, `updated_at`, `created_by`, `updated_by` on all tables
4. **Soft Deletes**: `deleted_at` for recoverable deletions
5. **JSONB for Flexibility**: Metadata, settings, custom attributes
6. **Computed Columns**: `net_qty` = `available_qty - reserved_qty`
7. **Table Partitioning**: Orders partitioned by month for performance
8. **Row-Level Security**: Multi-tenant data isolation

---

*Continued in next section: Complete PostgreSQL 16 Schema*

The complete database schema is available at: [`database/schema.sql`](database/schema.sql)

---

## 6. API Architecture

### 6.1 RESTful API Design

```
Base URL: /api/v1/

Authentication: Bearer JWT Token
Content-Type: application/json

┌──────────────────────────────────────────────────────────────────┐
│                        API ENDPOINTS                              │
├──────────────────────────────────────────────────────────────────┤
│ COMMERCE                                                          │
│ ├── GET    /products/              List products (paginated)     │
│ ├── POST   /products/              Create product                │
│ ├── GET    /products/{id}/         Get product details           │
│ ├── PATCH  /products/{id}/         Update product                │
│ ├── DELETE /products/{id}/         Soft delete product           │
│ ├── POST   /orders/                Create order                  │
│ ├── GET    /orders/                List orders                   │
│ ├── GET    /orders/{id}/           Get order details             │
│ └── PATCH  /orders/{id}/status/    Update order status           │
│                                                                   │
│ INVENTORY                                                         │
│ ├── GET    /inventory/             List inventory levels         │
│ ├── POST   /inventory/adjust/      Adjust stock                 │
│ ├── GET    /inventory/movements/   Stock movement history        │
│ └── POST   /inventory/transfer/    Transfer between locations    │
│                                                                   │
│ ACCOUNTING                                                        │
│ ├── GET    /accounting/accounts/   Chart of accounts             │
│ ├── POST   /accounting/journals/   Create journal entry          │
│ ├── GET    /accounting/invoices/   List invoices                 │
│ └── GET    /accounting/reports/    Generate reports              │
│                                                                   │
│ COMPLIANCE                                                        │
│ ├── GET    /gst/f5-preparation/    Prepare F5 return            │
│ ├── POST   /gst/f5-submit/         Submit F5 return             │
│ ├── POST   /pdpa/access-request/   Data access request          │
│ └── PATCH  /customers/{id}/consent/ Update consent              │
└──────────────────────────────────────────────────────────────────┘
```

### 6.2 API Response Format

```python
# Success Response
{
    "status": "success",
    "data": { ... },
    "meta": {
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 150,
            "pages": 8
        }
    }
}

# Error Response
{
    "status": "error",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": [
            {"field": "email", "message": "Invalid email format"}
        ]
    }
}
```

---

## 7. Security Architecture

### 7.1 Defense in Depth

```
┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Layer 1: PERIMETER                                             │
│   ├── CloudFlare DDoS Protection                                 │
│   ├── Web Application Firewall (WAF)                             │
│   └── Rate Limiting (100 req/min)                                │
│                                                                  │
│   Layer 2: NETWORK                                               │
│   ├── AWS VPC Isolation                                          │
│   ├── Security Groups (least privilege)                          │
│   └── Private Subnets for Databases                              │
│                                                                  │
│   Layer 3: APPLICATION                                           │
│   ├── JWT Authentication (15-min access tokens)                  │
│   ├── RBAC Authorization                                         │
│   ├── CSRF Protection                                            │
│   ├── XSS Prevention (Content-Security-Policy)                   │
│   └── SQL Injection Prevention (Django ORM)                      │
│                                                                  │
│   Layer 4: DATA                                                  │
│   ├── AES-256 Encryption at Rest                                 │
│   ├── TLS 1.3 in Transit                                         │
│   ├── Payment Tokenization (Stripe/HitPay)                       │
│   └── PII Masking in Logs                                        │
│                                                                  │
│   Layer 5: MONITORING                                            │
│   ├── Audit Logging (all state changes)                          │
│   ├── Anomaly Detection                                          │
│   └── SIEM Integration                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 RBAC Permissions

| Role | Permissions |
|------|-------------|
| **owner** | Full access to all resources |
| **admin** | Manage products, orders, customers, inventory, users |
| **finance** | View orders, manage accounting, file GST |
| **warehouse** | Manage inventory, process orders |
| **sales** | View products, create orders, manage customers |
| **customer** | View own orders, manage own profile |

---

## 8. Integration Architecture

### 8.1 Payment Gateway Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                   PAYMENT ORCHESTRATOR                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐                   │
│   │ Stripe  │     │ HitPay  │     │  2C2P   │                   │
│   │(Primary)│     │ (Local) │     │(Backup) │                   │
│   └────┬────┘     └────┬────┘     └────┬────┘                   │
│        │               │               │                         │
│        └───────────────┼───────────────┘                         │
│                        ▼                                         │
│              ┌─────────────────┐                                 │
│              │ PaymentService  │                                 │
│              │ • create_intent │                                 │
│              │ • capture       │                                 │
│              │ • refund        │                                 │
│              └─────────────────┘                                 │
│                                                                  │
│   Features:                                                      │
│   ├── Automatic fallback on gateway failure                      │
│   ├── PayNow QR code generation                                  │
│   ├── Webhook handling for async payments                        │
│   └── PCI DSS compliance via tokenization                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Logistics Integration

| Provider | Services | Integration |
|----------|----------|-------------|
| **Ninja Van** | Standard, Same-day, COD | REST API v2.1 |
| **J&T Express** | Express, Economy | REST API |
| **SingPost** | Registered, Speedpost | REST API v2.0 |

### 8.3 InvoiceNow (PEPPOL) Integration

| Component | Description | Django 6.0 Feature |
|-----------|-------------|-------------------|
| Access Point Provider | Integration via certified AP (Peppol.sg) | Background Tasks for async processing |
| Document Format | PEPPOL BIS Billing 3.0 UBL | Template Partials for XML generation |
| Signing | XML digital signature | CSP headers for secure delivery |
| Acknowledgments | Webhook processing | Tasks framework for retry logic |

```
backend/apps/invoicenow/
├── __init__.py
├── apps.py
├── models.py           # PEPPOLInvoice, InvoiceSubmission
├── peppol.py           # BIS 3.0 invoice generation
├── xml_signer.py       # XMLDSig signing
├── access_point.py     # AP provider client
├── tasks.py            # Django Tasks for async submission
├── serializers.py
├── views.py
├── urls.py
└── tests/
```

### 8.4 Django 6.0 Content Security Policy (CSP)

Django 6.0 introduced built-in CSP support for enhanced security:

```python
# config/settings/base.py
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

MIDDLEWARE = [
    ...
    'django.middleware.security.ContentSecurityPolicyMiddleware',
    ...
]
```

### 8.5 Hybrid Background Processing (Celery + Django Tasks)

| Use Case | Approach | Rationale |
|----------|----------|-----------|
| GST filing notifications | Django Tasks | Simple async, built-in |
| PDPA consent emails | Django Tasks | Low volume, simple |
| PEPPOL acknowledgments | Django Tasks | Event-driven, lightweight |
| Marketplace inventory sync | Celery | High volume, complex |
| Bulk order processing | Celery | CPU-intensive, distributed |
| Large data imports | Celery | Long-running, needs monitoring |

```python
# Django 6.0 Tasks example
from django.tasks import task

@task
def send_gst_filing_notification(company_id: int, filing_id: str):
    """Send GST filing confirmation via Django Tasks"""
    company = Company.objects.get(id=company_id)
    send_mail(
        subject=f"GST Filing {filing_id} Submitted",
        message=f"Your GST F5 return has been submitted successfully.",
        from_email="gst@company.sg",
        recipient_list=[company.email],
    )
```

---

## 9. Performance Architecture

### 9.1 Performance Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| **Page Load (Mobile)** | < 2.0s | CDN, image optimization, code splitting |
| **API Response** | < 200ms (p95) | Database indexing, Redis caching |
| **Database Query** | < 100ms | Query optimization, read replicas |
| **Order Processing** | < 2 min | Async with Celery |
| **Search Results** | < 500ms | PostgreSQL tsvector |

### 9.2 Caching Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                     CACHING LAYERS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   L1: CDN (CloudFront)                                           │
│   ├── Static assets: 1 year                                      │
│   ├── Product images: 24 hours                                   │
│   └── API responses: No cache (dynamic)                          │
│                                                                  │
│   L2: Redis Application Cache                                    │
│   ├── Session data: 30 minutes                                   │
│   ├── Product catalog: 1 hour                                    │
│   ├── Inventory levels: 30 seconds                               │
│   ├── Cart data: 7 days                                          │
│   └── Rate limiting: 1 minute windows                            │
│                                                                  │
│   L3: Database Query Cache                                       │
│   ├── Prepared statements: Connection lifetime                   │
│   └── Materialized views: Refresh on schedule                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Deployment Architecture

### 10.1 AWS Infrastructure

```
┌─────────────────────────────────────────────────────────────────┐
│                     AWS SINGAPORE (ap-southeast-1)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                        VPC                               │   │
│   │  ┌─────────────────┐  ┌─────────────────┐               │   │
│   │  │  Public Subnet  │  │  Public Subnet  │               │   │
│   │  │      (AZ-1)     │  │      (AZ-2)     │               │   │
│   │  │  ┌───────────┐  │  │  ┌───────────┐  │               │   │
│   │  │  │    ALB    │  │  │  │    ALB    │  │               │   │
│   │  │  └───────────┘  │  │  └───────────┘  │               │   │
│   │  └─────────────────┘  └─────────────────┘               │   │
│   │                                                          │   │
│   │  ┌─────────────────┐  ┌─────────────────┐               │   │
│   │  │ Private Subnet  │  │ Private Subnet  │               │   │
│   │  │      (AZ-1)     │  │      (AZ-2)     │               │   │
│   │  │  ┌───────────┐  │  │  ┌───────────┐  │               │   │
│   │  │  │ECS Fargate│  │  │  │ECS Fargate│  │               │   │
│   │  │  │ (Django)  │  │  │  │ (Celery)  │  │               │   │
│   │  │  └───────────┘  │  │  └───────────┘  │               │   │
│   │  └─────────────────┘  └─────────────────┘               │   │
│   │                                                          │   │
│   │  ┌─────────────────┐  ┌─────────────────┐               │   │
│   │  │Isolated Subnet  │  │Isolated Subnet  │               │   │
│   │  │      (AZ-1)     │  │      (AZ-2)     │               │   │
│   │  │  ┌───────────┐  │  │  ┌───────────┐  │               │   │
│   │  │  │RDS Postgres│  │  │  │   Redis   │  │               │   │
│   │  │  │ (Primary) │  │  │  │(Cluster)  │  │               │   │
│   │  │  └───────────┘  │  │  └───────────┘  │               │   │
│   │  └─────────────────┘  └─────────────────┘               │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 CI/CD Pipeline

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   Push   │───▶│  GitHub  │───▶│  Build   │───▶│  Deploy  │
│  to Git  │    │ Actions  │    │  & Test  │    │  to ECS  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                     │
                     ▼
              ┌──────────────┐
              │ Quality Gates│
              │ • Unit Tests │
              │ • Lint Check │
              │ • Security   │
              │ • Coverage   │
              └──────────────┘
```

---

## Appendix A: Key Technology Versions

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Runtime (Django 6.0 requirement) |
| Django | 6.0+ | Web framework with CSP, Background Tasks |
| DRF | 3.16+ | REST API |
| PostgreSQL | 16+ | Primary database |
| Redis | 7.4+ | Cache & queue |
| Celery | 5.5+ | Heavy async tasks |
| Next.js | 14.2+ | Frontend |
| TypeScript | 5.x | Type safety |
| Docker | 24+ | Containerization |

---

# Master Execution Plan
## Singapore SMB E-Commerce Platform

> **Version**: 1.0
> **Created**: December 18, 2025
> **Estimated Duration**: 24-28 weeks
> **Status**: Ready for Implementation

---

## Executive Summary

This document outlines the comprehensive implementation plan for the Singapore SMB E-Commerce Platform. The plan is organized into **8 logical phases** that can be executed independently, with clear dependencies between phases.

### Project Foundation (Already Exists)

| Component | File | Status |
|-----------|------|--------|
| Backend Dependencies | `backend/pyproject.toml` | ✅ Django 6.0+, DRF, Celery, Redis |
| Backend Python | `backend/.python-version` | ✅ Python 3.12+ |
| Frontend Dependencies | `frontend/package.json` | ✅ Next.js 14, React Query, Tailwind |
| Database Schema | `database/schema.sql` | ✅ PostgreSQL 16 Complete Schema |

---

## Phase Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           IMPLEMENTATION PHASES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Phase 1: Foundation (Weeks 1-3)                                            │
│  └── Django project setup, core models, authentication, admin               │
│                                                                              │
│  Phase 2: Commerce Domain (Weeks 4-6)                                       │
│  └── Products, Categories, Customers, Orders, Cart                          │
│                                                                              │
│  Phase 3: Inventory Domain (Weeks 7-9)                                      │
│  └── Locations, Stock levels, Movements, Reservations                       │
│                                                                              │
│  Phase 4: Accounting Domain (Weeks 10-12)                                   │
│  └── Chart of Accounts, Journals, Invoices, GST Engine                      │
│                                                                              │
│  Phase 5: Compliance & Integrations (Weeks 13-15)                           │
│  └── PDPA, Audit logs, Payment gateways, Logistics                          │
│                                                                              │
│  Phase 6: Frontend Foundation (Weeks 16-18)                                 │
│  └── Next.js setup, components, layouts, API client                         │
│                                                                              │
│  Phase 7: Frontend Features (Weeks 19-22)                                   │
│  └── Storefront, Cart, Checkout, User dashboard                             │
│                                                                              │
│  Phase 8: Testing & Deployment (Weeks 23-28)                                │
│  └── E2E tests, Performance, Security audit, Production deploy              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation

**Duration**: Weeks 1-3
**Dependencies**: None
**Goal**: Establish Django project structure, core models, authentication, and admin interface

### Files to Create

---

#### 1.1 `backend/config/__init__.py`

**Description**: Django project configuration package initializer.

**Features**:
- Celery app initialization
- Package exports

**Interfaces**: None

**Checklist**:
- [ ] Create empty `__init__.py`
- [ ] Import Celery app
- [ ] Export `celery_app` for external use

---

#### 1.2 `backend/config/settings/base.py`

**Description**: Base Django settings shared across all environments.

**Features**:
- Installed apps configuration
- Middleware stack
- Database configuration (PostgreSQL)
- Redis cache configuration
- Celery configuration
- REST Framework settings
- Authentication settings (django-allauth, JWT)
- Static and media file settings
- Logging configuration

**Interfaces**:
- Environment variables via `django-environ`
- `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`

**Checklist**:
- [ ] Configure `INSTALLED_APPS` with all project apps
- [ ] Set up PostgreSQL database with DECIMAL precision
- [ ] Configure Redis for cache and Celery broker
- [ ] Set up REST Framework with JWT authentication
- [ ] Configure django-allauth for authentication
- [ ] Set up logging with rotating file handlers
- [ ] Configure CORS headers for frontend

---

#### 1.3 `backend/config/settings/development.py`

**Description**: Development-specific Django settings.

**Features**:
- Debug mode enabled
- Local database settings
- Django Debug Toolbar
- Relaxed CORS for local development

**Interfaces**: Inherits from `base.py`

**Checklist**:
- [ ] Enable `DEBUG=True`
- [ ] Configure local PostgreSQL connection
- [ ] Add Django Debug Toolbar to installed apps
- [ ] Set `CORS_ALLOW_ALL_ORIGINS=True`

---

#### 1.4 `backend/config/settings/production.py`

**Description**: Production-specific Django settings.

**Features**:
- Debug mode disabled
- Secure cookie settings
- HTTPS enforcement
- Sentry error tracking
- Production database via RDS

**Interfaces**: Inherits from `base.py`

**Checklist**:
- [ ] Disable `DEBUG`
- [ ] Enable `SECURE_SSL_REDIRECT`
- [ ] Configure `CSRF_COOKIE_SECURE` and `SESSION_COOKIE_SECURE`
- [ ] Initialize Sentry SDK
- [ ] Configure production database URL

---

#### 1.5 `backend/config/urls.py`

**Description**: Root URL configuration.

**Features**:
- API versioning (`/api/v1/`)
- Admin URL
- API documentation (drf-spectacular)
- Health check endpoint

**Interfaces**:
- `GET /api/v1/` - API root
- `GET /api/docs/` - Swagger UI
- `GET /health/` - Health check

**Checklist**:
- [ ] Include admin URLs
- [ ] Include API v1 URLs with namespace
- [ ] Add drf-spectacular schema and UI views
- [ ] Add health check endpoint

---

#### 1.6 `backend/config/celery.py`

**Description**: Celery application configuration.

**Features**:
- Celery app initialization
- Task autodiscovery
- Beat scheduler configuration
- Task routing

**Interfaces**:
- Redis broker connection
- Task queues: `default`, `commerce`, `inventory`, `accounting`

**Checklist**:
- [ ] Create Celery app with Django settings
- [ ] Configure task autodiscovery
- [ ] Set up task routing to queues
- [ ] Configure beat schedule for periodic tasks

---

#### 1.7 `backend/config/asgi.py`

**Description**: ASGI application entry point.

**Features**:
- ASGI application for async support
- WebSocket support preparation

**Interfaces**: ASGI interface

**Checklist**:
- [ ] Configure Django ASGI application
- [ ] Set `DJANGO_SETTINGS_MODULE`

---

#### 1.8 `backend/config/wsgi.py`

**Description**: WSGI application entry point.

**Features**:
- WSGI application for Gunicorn

**Interfaces**: WSGI interface

**Checklist**:
- [ ] Configure Django WSGI application
- [ ] Set `DJANGO_SETTINGS_MODULE`

---

#### 1.9 `backend/manage.py`

**Description**: Django management script.

**Features**:
- Django CLI entry point

**Interfaces**: Command line

**Checklist**:
- [ ] Create standard Django manage.py
- [ ] Set default settings module

---

#### 1.10 `backend/core/__init__.py`

**Description**: Core application package.

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 1.11 `backend/core/models.py`

**Description**: Base models with audit fields.

**Features**:
- `BaseModel` with `created_at`, `updated_at`
- `AuditableModel` with `created_by`, `updated_by`
- `SoftDeleteModel` with `deleted_at`

**Interfaces**:
- Abstract base classes for inheritance

**Checklist**:
- [ ] Create `BaseModel` with timestamp fields
- [ ] Create `AuditableModel` with user tracking
- [ ] Create `SoftDeleteModel` with soft delete logic
- [ ] Add custom manager for soft delete filtering

---

#### 1.12 `backend/core/exceptions.py`

**Description**: Custom exception classes.

**Features**:
- `BusinessLogicError` base exception
- `ValidationError` for business rule violations
- `InsufficientStockError` for inventory
- `PaymentError` for payment failures

**Interfaces**:
- Exception classes with error codes

**Checklist**:
- [ ] Create base `BusinessLogicError` class
- [ ] Create domain-specific exceptions
- [ ] Add error codes for API responses

---

#### 1.13 `backend/core/permissions.py`

**Description**: Custom DRF permissions.

**Features**:
- `IsCompanyMember` - Tenant isolation
- `HasRole` - Role-based access
- `IsOwnerOrAdmin` - Object-level permission

**Interfaces**:
- DRF permission classes

**Checklist**:
- [ ] Create `IsCompanyMember` permission
- [ ] Create `HasRole` parameterized permission
- [ ] Create `IsOwnerOrAdmin` object permission

---

#### 1.14 `backend/core/middleware.py`

**Description**: Custom middleware.

**Features**:
- `TenantMiddleware` - Set current company context
- `AuditMiddleware` - Track request user
- `SecurityHeadersMiddleware` - Add security headers

**Interfaces**:
- Django middleware interface

**Checklist**:
- [ ] Create `TenantMiddleware` to extract company from request
- [ ] Create `AuditMiddleware` to set current user in thread local
- [ ] Add security headers (CSP, X-Frame-Options, etc.)

---

#### 1.15 `backend/apps/__init__.py`

**Description**: Applications package.

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 1.16 `backend/apps/accounts/__init__.py`

**Description**: Accounts app package.

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 1.17 `backend/apps/accounts/apps.py`

**Description**: Accounts app configuration.

**Checklist**:
- [ ] Create `AccountsConfig` class
- [ ] Set app name and verbose name

---

#### 1.18 `backend/apps/accounts/models.py`

**Description**: User and authentication models.

**Features**:
- Custom `User` model extending `AbstractUser`
- `Company` model for multi-tenancy
- `Role` and `Permission` models for RBAC
- `UserRole` junction model

**Interfaces**:
- User authentication via django-allauth
- Company-scoped permissions

**Checklist**:
- [ ] Create custom `User` model with company FK
- [ ] Create `Company` model with UEN, GST fields
- [ ] Create `Role` model with JSON permissions
- [ ] Create `UserRole` M2M through model
- [ ] Add user profile fields (phone, MFA settings)
- [ ] Add indexes for email and company lookups

---

#### 1.19 `backend/apps/accounts/serializers.py`

**Description**: DRF serializers for accounts.

**Features**:
- `UserSerializer` - User CRUD
- `UserCreateSerializer` - Registration
- `CompanySerializer` - Company CRUD
- `RoleSerializer` - Role management
- `LoginSerializer` - Authentication
- `TokenSerializer` - JWT response

**Interfaces**:
- REST API request/response serialization

**Checklist**:
- [ ] Create `UserSerializer` with nested company
- [ ] Create `UserCreateSerializer` with password validation
- [ ] Create `CompanySerializer` with UEN validation
- [ ] Create `LoginSerializer` for authentication
- [ ] Add password strength validation

---

#### 1.20 `backend/apps/accounts/views.py`

**Description**: DRF views for accounts.

**Features**:
- `UserViewSet` - User CRUD operations
- `CompanyViewSet` - Company management
- `RoleViewSet` - Role management
- `AuthViewSet` - Login, logout, token refresh
- `ProfileView` - Current user profile

**Interfaces**:
- REST API endpoints

**Checklist**:
- [ ] Create `UserViewSet` with company filtering
- [ ] Create `CompanyViewSet` with owner permission
- [ ] Create `AuthViewSet` with login/logout actions
- [ ] Add JWT token generation on login
- [ ] Add MFA verification endpoint

---

#### 1.21 `backend/apps/accounts/urls.py`

**Description**: URL routing for accounts API.

**Features**:
- Router registration for ViewSets
- Custom action URLs

**Interfaces**:
- `/api/v1/accounts/users/`
- `/api/v1/accounts/companies/`
- `/api/v1/accounts/auth/login/`
- `/api/v1/accounts/auth/token/refresh/`

**Checklist**:
- [ ] Register ViewSets with router
- [ ] Add auth endpoints
- [ ] Include in main URLs

---

#### 1.22 `backend/apps/accounts/admin.py`

**Description**: Django admin configuration.

**Features**:
- Custom `UserAdmin` with company filter
- `CompanyAdmin` with inline users
- `RoleAdmin` with permission editor

**Interfaces**:
- Django Admin interface

**Checklist**:
- [ ] Create custom `UserAdmin`
- [ ] Create `CompanyAdmin` with search/filter
- [ ] Create `RoleAdmin` with JSON editor

---

#### 1.23 `backend/apps/accounts/services.py`

**Description**: Business logic for accounts.

**Features**:
- `AuthService` - Authentication logic
- `UserService` - User management
- `CompanyService` - Company operations

**Interfaces**:
- Service class methods

**Checklist**:
- [ ] Create `AuthService.authenticate()` method
- [ ] Create `AuthService.generate_tokens()` for JWT
- [ ] Create `UserService.create_user()` with role assignment
- [ ] Create `CompanyService.create_company()` with setup

---

#### 1.24 `backend/apps/accounts/tests/__init__.py`

**Description**: Tests package for accounts.

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 1.25 `backend/apps/accounts/tests/test_models.py`

**Description**: Unit tests for account models.

**Features**:
- User model tests
- Company model tests
- Role/permission tests

**Checklist**:
- [ ] Test user creation with company
- [ ] Test company UEN validation
- [ ] Test role permission checks
- [ ] Test user-role assignment

---

#### 1.26 `backend/apps/accounts/tests/test_views.py`

**Description**: API tests for accounts.

**Features**:
- Authentication endpoint tests
- User CRUD tests
- Permission tests

**Checklist**:
- [ ] Test login with valid credentials
- [ ] Test login with invalid credentials
- [ ] Test token refresh
- [ ] Test user list with company filter
- [ ] Test role-based access control

---

### Phase 1 Verification Plan

**Database Migration Strategy**:
```bash
cd backend
# Verify migrations are correct before applying
uv run python manage.py makemigrations --check --dry-run

# Create initial migrations
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate

# Verify with showmigrations
uv run python manage.py showmigrations
```

**Unit Tests**:
```bash
cd backend
uv run pytest apps/accounts/tests/ -v
```

**Manual Verification**:
1. Start Django development server: `uv run python manage.py runserver`
2. Access admin at `http://localhost:8000/admin/`
3. Create a company and user via admin
4. Test login API via Swagger at `http://localhost:8000/api/docs/`

---

## Phase 2: Commerce Domain

**Duration**: Weeks 4-6
**Dependencies**: Phase 1 (accounts, core)
**Goal**: Implement product catalog, customers, orders, and cart functionality

### Files to Create

---

#### 2.1 `backend/apps/commerce/__init__.py`

**Description**: Commerce app package.

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 2.2 `backend/apps/commerce/apps.py`

**Description**: Commerce app configuration.

**Checklist**:
- [ ] Create `CommerceConfig` class

---

#### 2.3 `backend/apps/commerce/models/product.py`

**Description**: Product and category models.

**Features**:
- `Category` model with hierarchy
- `Product` model with GST codes, DECIMAL pricing
- `ProductVariant` model with options
- Full-text search vector

**Interfaces**:
- Product API endpoints

**Checklist**:
- [ ] Create `Category` with parent FK (self-referential)
- [ ] Create `Product` with `DECIMAL(10,2)` price fields
- [ ] Create `ProductVariant` with options JSONB
- [ ] Add GST code field with choices (SR, ZR, ES, OS)
- [ ] Add `search_vector` tsvector field
- [ ] Create indexes for SKU, category, search

---

#### 2.4 `backend/apps/commerce/models/customer.py`

**Description**: Customer and address models.

**Features**:
- `Customer` model with PDPA consent fields
- `CustomerAddress` model with Singapore format
- Customer types (retail, wholesale, VIP)

**Interfaces**:
- Customer API endpoints

**Checklist**:
- [ ] Create `Customer` with email, phone, consent fields
- [ ] Create `CustomerAddress` with postal_code, unit_number
- [ ] Add `customer_type` choices
- [ ] Add B2B fields (company_uen, credit_limit)
- [ ] Add PDPA consent fields with timestamps

---

#### 2.5 `backend/apps/commerce/models/order.py`

**Description**: Order and order item models.

**Features**:
- `Order` model with DECIMAL amounts
- `OrderItem` model with line totals
- Order status state machine
- GST amount tracking

**Interfaces**:
- Order API endpoints

**Checklist**:
- [ ] Create `Order` with status, payment_status fields
- [ ] Create `OrderItem` with quantity, unit_price, gst_amount
- [ ] Add `DECIMAL(12,2)` for all monetary fields
- [ ] Add shipping and billing address JSONB
- [ ] Calculate line totals with GST
- [ ] Add order number generation

---

#### 2.6 `backend/apps/commerce/models/cart.py`

**Description**: Shopping cart models.

**Features**:
- `Cart` model linked to customer/session
- `CartItem` model with product reference
- Cart expiration handling

**Interfaces**:
- Cart API endpoints

**Checklist**:
- [ ] Create `Cart` with customer FK (nullable for guest)
- [ ] Create `CartItem` with product, variant, quantity
- [ ] Add session-based cart for guests
- [ ] Add `expires_at` for cart cleanup
- [ ] Add cart merge on login

---

#### 2.7 `backend/apps/commerce/models/__init__.py`

**Description**: Models package exports.

**Checklist**:
- [ ] Export all commerce models

---

#### 2.8 `backend/apps/commerce/serializers.py`

**Description**: DRF serializers for commerce.

**Features**:
- Product serializers with variants
- Customer serializers with addresses
- Order serializers with items
- Cart serializers

**Interfaces**:
- REST API serialization

**Checklist**:
- [ ] Create `ProductSerializer` with category nested
- [ ] Create `ProductVariantSerializer`
- [ ] Create `CustomerSerializer` with consent validation
- [ ] Create `OrderSerializer` with read-only totals
- [ ] Create `CartSerializer` with item list

---

#### 2.9 `backend/apps/commerce/views.py`

**Description**: DRF views for commerce.

**Features**:
- `ProductViewSet` with search, filter
- `CategoryViewSet` with tree structure
- `CustomerViewSet` with company filter
- `OrderViewSet` with status actions
- `CartViewSet` with add/remove/checkout

**Interfaces**:
- REST API endpoints

**Checklist**:
- [ ] Create `ProductViewSet` with search filter
- [ ] Create `CategoryViewSet` with nested representation
- [ ] Create `CustomerViewSet` with PDPA data export
- [ ] Create `OrderViewSet` with status transitions
- [ ] Create `CartViewSet` with checkout action

---

#### 2.10 `backend/apps/commerce/urls.py`

**Description**: URL routing for commerce API.

**Interfaces**:
- `/api/v1/commerce/products/`
- `/api/v1/commerce/categories/`
- `/api/v1/commerce/customers/`
- `/api/v1/commerce/orders/`
- `/api/v1/commerce/cart/`

**Checklist**:
- [ ] Register all ViewSets
- [ ] Add custom action routes

---

#### 2.11 `backend/apps/commerce/admin.py`

**Description**: Django admin for commerce.

**Features**:
- Product admin with variant inline
- Order admin with items inline
- Customer admin with address inline

**Checklist**:
- [ ] Create `ProductAdmin` with variant inline
- [ ] Create `OrderAdmin` with read-only totals
- [ ] Create `CustomerAdmin` with address inline

---

#### 2.12 `backend/apps/commerce/services/__init__.py`

**Description**: Commerce services package.

**Checklist**:
- [ ] Export all services

---

#### 2.13 `backend/apps/commerce/services/product_service.py`

**Description**: Product business logic.

**Features**:
- Product creation with variants
- Price calculation with GST
- Product search

**Checklist**:
- [ ] Create `ProductService.create_product()`
- [ ] Create `ProductService.update_price()` with GST calc
- [ ] Create `ProductService.search()` using tsvector

---

#### 2.14 `backend/apps/commerce/services/order_service.py`

**Description**: Order business logic.

**Features**:
- Order creation from cart
- Order status transitions
- Order total calculation

**Interfaces**:
- Emits domain events for inventory, accounting

**Checklist**:
- [ ] Create `OrderService.create_from_cart()`
- [ ] Create `OrderService.confirm()` - reserve inventory
- [ ] Create `OrderService.ship()` - update fulfillment
- [ ] Create `OrderService.cancel()` - release inventory
- [ ] Emit events for downstream processing

---

#### 2.15 `backend/apps/commerce/services/cart_service.py`

**Description**: Cart business logic.

**Features**:
- Add/remove items
- Calculate totals with GST
- Checkout validation
- Cart merge on login

**Checklist**:
- [ ] Create `CartService.add_item()`
- [ ] Create `CartService.remove_item()`
- [ ] Create `CartService.calculate_totals()`
- [ ] Create `CartService.checkout()` - create order
- [ ] Create `CartService.merge_guest_cart()`

---

#### 2.16 `backend/apps/commerce/tasks.py`

**Description**: Celery tasks for commerce.

**Features**:
- Order confirmation email
- Cart cleanup (expired carts)
- Order status sync

**Checklist**:
- [ ] Create `send_order_confirmation` task
- [ ] Create `cleanup_expired_carts` periodic task
- [ ] Create `sync_order_status` for marketplace orders

---

#### 2.17 `backend/apps/commerce/tests/__init__.py`

**Description**: Tests package.

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 2.18 `backend/apps/commerce/tests/test_models.py`

**Description**: Model unit tests.

**Checklist**:
- [ ] Test product creation with GST
- [ ] Test order total calculation
- [ ] Test cart item quantity updates

---

#### 2.19 `backend/apps/commerce/tests/test_services.py`

**Description**: Service unit tests.

**Checklist**:
- [ ] Test `OrderService.create_from_cart()`
- [ ] Test order status transitions
- [ ] Test cart checkout flow

---

#### 2.20 `backend/apps/commerce/tests/test_views.py`

**Description**: API integration tests.

**Checklist**:
- [ ] Test product search endpoint
- [ ] Test order creation
- [ ] Test cart operations

---

### Phase 2 Verification Plan

**Unit Tests**:
```bash
cd backend
uv run pytest apps/commerce/tests/ -v
```

**Manual Verification**:
1. Create products via admin
2. Test product search via API
3. Add items to cart, checkout
4. Verify order creation and GST calculation

---

## Phase 3: Inventory Domain

**Duration**: Weeks 7-9
**Dependencies**: Phase 2 (commerce)
**Goal**: Implement inventory tracking, reservations, and stock movements

### Files to Create

---

#### 3.1 `backend/apps/inventory/__init__.py`

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 3.2 `backend/apps/inventory/apps.py`

**Checklist**:
- [ ] Create `InventoryConfig` class

---

#### 3.3 `backend/apps/inventory/models.py`

**Description**: Inventory models.

**Features**:
- `Location` model (warehouse, store)
- `InventoryItem` with computed `net_qty`
- `InventoryReservation` with expiration
- `InventoryMovement` for audit trail

**Interfaces**:
- Real-time stock levels

**Checklist**:
- [ ] Create `Location` with type choices
- [ ] Create `InventoryItem` with available_qty, reserved_qty
- [ ] Add computed `net_qty` property
- [ ] Create `InventoryReservation` with expires_at
- [ ] Create `InventoryMovement` with movement_type choices
- [ ] Add version field for optimistic locking

---

#### 3.4 `backend/apps/inventory/serializers.py`

**Description**: Inventory serializers.

**Checklist**:
- [ ] Create `LocationSerializer`
- [ ] Create `InventoryItemSerializer` with net_qty
- [ ] Create `InventoryMovementSerializer`

---

#### 3.5 `backend/apps/inventory/views.py`

**Description**: Inventory API views.

**Interfaces**:
- `/api/v1/inventory/locations/`
- `/api/v1/inventory/items/`
- `/api/v1/inventory/movements/`
- `/api/v1/inventory/adjust/`
- `/api/v1/inventory/transfer/`

**Checklist**:
- [ ] Create `LocationViewSet`
- [ ] Create `InventoryItemViewSet` with low stock filter
- [ ] Create `InventoryMovementViewSet` (read-only)
- [ ] Add `adjust_stock` action
- [ ] Add `transfer_stock` action

---

#### 3.6 `backend/apps/inventory/urls.py`

**Checklist**:
- [ ] Register ViewSets
- [ ] Add custom action routes

---

#### 3.7 `backend/apps/inventory/admin.py`

**Checklist**:
- [ ] Create `LocationAdmin`
- [ ] Create `InventoryItemAdmin` with filters
- [ ] Create `InventoryMovementAdmin` (read-only)

---

#### 3.8 `backend/apps/inventory/services.py`

**Description**: Inventory business logic.

**Features**:
- Stock reservation with Redis locks
- Stock adjustment with movement logging
- Transfer between locations
- Low stock alerts

**Checklist**:
- [ ] Create `InventoryService.reserve_stock()` with Redis lock
- [ ] Create `InventoryService.release_reservation()`
- [ ] Create `InventoryService.adjust_stock()`
- [ ] Create `InventoryService.transfer_stock()`
- [ ] Create `InventoryService.check_low_stock()`

---

#### 3.9 `backend/apps/inventory/locks.py`

**Description**: Redis distributed locking.

**Features**:
- Distributed lock for inventory operations
- Lock timeout and retry logic

**Checklist**:
- [ ] Create `InventoryLock` context manager
- [ ] Implement lock acquisition with timeout
- [ ] Implement lock release
- [ ] Add retry logic for lock contention

---

#### 3.10 `backend/apps/inventory/tasks.py`

**Description**: Celery tasks.

**Features**:
- Periodic reservation cleanup
- Low stock notifications
- Inventory sync with marketplaces

**Checklist**:
- [ ] Create `cleanup_expired_reservations` periodic task
- [ ] Create `send_low_stock_alerts` periodic task
- [ ] Create `sync_marketplace_inventory` task

---

#### 3.11 `backend/apps/inventory/tests/__init__.py`

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 3.12 `backend/apps/inventory/tests/test_services.py`

**Checklist**:
- [ ] Test stock reservation with concurrent requests
- [ ] Test reservation expiration
- [ ] Test stock transfer between locations
- [ ] Test low stock detection

---

### Phase 3 Verification Plan

**Unit Tests**:
```bash
cd backend
uv run pytest apps/inventory/tests/ -v
```

**Concurrency Test**:
```python
# Test concurrent reservations don't oversell
# Create script to simulate 10 concurrent reservations for 5 available items
```

---

## Phase 4: Accounting Domain

**Duration**: Weeks 10-12
**Dependencies**: Phase 2 (commerce)
**Goal**: Implement chart of accounts, journal entries, invoices, and GST engine

### Files to Create

---

#### 4.1 `backend/apps/accounting/__init__.py`

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 4.2 `backend/apps/accounting/apps.py`

**Checklist**:
- [ ] Create `AccountingConfig` class

---

#### 4.3 `backend/apps/accounting/models.py`

**Description**: Accounting models.

**Features**:
- `Account` (Chart of Accounts)
- `JournalEntry` with balanced validation
- `JournalLine` with debit/credit
- `Invoice` with PEPPOL fields
- `Payment` with gateway reference

**Checklist**:
- [ ] Create `Account` with type, subtype
- [ ] Create `JournalEntry` with balanced constraint
- [ ] Create `JournalLine` with one-side-only constraint
- [ ] Create `Invoice` with computed amount_due
- [ ] Create `Payment` with gateway reference

---

#### 4.4 `backend/apps/accounting/gst/__init__.py`

**Checklist**:
- [ ] Export GST engine classes

---

#### 4.5 `backend/apps/accounting/gst/engine.py`

**Description**: GST calculation engine.

**Features**:
- GST rate lookup (historical)
- GST calculation for transactions
- F5 return preparation
- Box calculations

**Interfaces**:
- `GSTEngine.calculate(amount, gst_code, date)`
- `GSTEngine.prepare_f5(company_id, quarter, year)`

**Checklist**:
- [ ] Create `GSTEngine.calculate()` with rate lookup
- [ ] Create `GSTEngine.get_rate()` for historical rates
- [ ] Create `GSTEngine.prepare_f5()` with all box calculations
- [ ] Create `GSTEngine.validate_f5()` for data integrity

---

#### 4.6 `backend/apps/accounting/gst/rates.py`

**Description**: Historical GST rates.

**Features**:
- GST rate table by date range
- Current rate: 9% (from Jan 1, 2024)

**Checklist**:
- [ ] Define GST rate history
- [ ] Create `get_gst_rate(date)` function

---

#### 4.7 `backend/apps/accounting/serializers.py`

**Checklist**:
- [ ] Create `AccountSerializer`
- [ ] Create `JournalEntrySerializer` with lines
- [ ] Create `InvoiceSerializer`
- [ ] Create `PaymentSerializer`
- [ ] Create `GSTF5Serializer`

---

#### 4.8 `backend/apps/accounting/views.py`

**Interfaces**:
- `/api/v1/accounting/accounts/`
- `/api/v1/accounting/journals/`
- `/api/v1/accounting/invoices/`
- `/api/v1/accounting/payments/`
- `/api/v1/accounting/gst/f5-preparation/`

**Checklist**:
- [ ] Create `AccountViewSet`
- [ ] Create `JournalEntryViewSet`
- [ ] Create `InvoiceViewSet` with PDF generation
- [ ] Create `PaymentViewSet`
- [ ] Create `GSTF5View` for F5 preparation

---

#### 4.9 `backend/apps/accounting/urls.py`

**Checklist**:
- [ ] Register ViewSets
- [ ] Add GST endpoints

---

#### 4.10 `backend/apps/accounting/admin.py`

**Checklist**:
- [ ] Create `AccountAdmin`
- [ ] Create `JournalEntryAdmin` with lines inline
- [ ] Create `InvoiceAdmin`

---

#### 4.11 `backend/apps/accounting/services.py`

**Description**: Accounting business logic.

**Features**:
- Journal entry creation with validation
- Invoice generation from orders
- Payment recording
- Month-end close

**Checklist**:
- [ ] Create `LedgerService.create_journal_entry()`
- [ ] Create `LedgerService.post_entry()`
- [ ] Create `InvoiceService.create_from_order()`
- [ ] Create `InvoiceService.generate_pdf()`
- [ ] Create `PaymentService.record_payment()`

---

#### 4.12 `backend/apps/accounting/tasks.py`

**Checklist**:
- [ ] Create `generate_daily_revenue_report` periodic task
- [ ] Create `prepare_gst_filing_reminder` periodic task
- [ ] Create `generate_invoice_pdf` async task

---

#### 4.13 `backend/apps/accounting/tests/__init__.py`

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 4.14 `backend/apps/accounting/tests/test_gst_engine.py`

**Checklist**:
- [ ] Test GST calculation for SR, ZR, ES, OS codes
- [ ] Test historical rate lookup
- [ ] Test F5 box calculations
- [ ] Test F5 validation

---

### Phase 4 Verification Plan

**Unit Tests**:
```bash
cd backend
uv run pytest apps/accounting/tests/ -v
```

**GST Calculation Verification**:
1. Create test orders with different GST codes
2. Verify GST amounts match expected calculations
3. Generate F5 preparation and verify box totals

---

## Phase 5: Compliance & Integrations

**Duration**: Weeks 13-15
**Dependencies**: Phase 4 (accounting)
**Goal**: Implement PDPA compliance, audit logging, payment gateways, and logistics

### Files to Create

---

#### 5.1 `backend/apps/compliance/__init__.py`

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 5.2 `backend/apps/compliance/apps.py`

**Checklist**:
- [ ] Create `ComplianceConfig` class

---

#### 5.3 `backend/apps/compliance/models.py`

**Description**: Compliance models.

**Features**:
- `GSTReturn` for F5 filings
- `DataConsent` for PDPA
- `DataAccessRequest` for PDPA
- `AuditLog` for all changes

**Checklist**:
- [ ] Create `GSTReturn` with box values
- [ ] Create `DataConsent` with type, status
- [ ] Create `DataAccessRequest` with 30-day due date
- [ ] Create `AuditLog` with old/new values

---

#### 5.4 `backend/apps/compliance/pdpa.py`

**Description**: PDPA compliance service.

**Features**:
- Consent management
- Data export
- Data anonymization
- Breach notification

**Checklist**:
- [ ] Create `PDPAService.record_consent()`
- [ ] Create `PDPAService.export_customer_data()`
- [ ] Create `PDPAService.anonymize_customer()`
- [ ] Create `PDPAService.process_access_request()`

---

#### 5.5 `backend/apps/compliance/audit.py`

**Description**: Audit logging service.

**Features**:
- Automatic audit log creation
- User and IP tracking
- Old/new value diff

**Checklist**:
- [ ] Create `AuditService.log_change()`
- [ ] Create audit signal handlers
- [ ] Create `AuditService.get_history()`

---

#### 5.6 `backend/apps/compliance/serializers.py`

**Checklist**:
- [ ] Create `GSTReturnSerializer`
- [ ] Create `DataAccessRequestSerializer`
- [ ] Create `AuditLogSerializer`

---

#### 5.7 `backend/apps/compliance/views.py`

**Interfaces**:
- `/api/v1/compliance/gst-returns/`
- `/api/v1/compliance/data-access-requests/`
- `/api/v1/compliance/audit-logs/`

**Checklist**:
- [ ] Create `GSTReturnViewSet`
- [ ] Create `DataAccessRequestViewSet`
- [ ] Create `AuditLogViewSet` (read-only)

---

#### 5.8 `backend/apps/compliance/urls.py`

**Checklist**:
- [ ] Register ViewSets

---

#### 5.9 `backend/apps/payments/__init__.py`

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 5.10 `backend/apps/payments/apps.py`

**Checklist**:
- [ ] Create `PaymentsConfig` class

---

#### 5.11 `backend/apps/payments/gateways/__init__.py`

**Checklist**:
- [ ] Export gateway adapters

---

#### 5.12 `backend/apps/payments/gateways/base.py`

**Description**: Base payment gateway adapter.

**Features**:
- Abstract interface for payment gateways
- Common error handling

**Checklist**:
- [ ] Create `PaymentGatewayAdapter` abstract class
- [ ] Define `create_payment_intent()` method
- [ ] Define `capture_payment()` method
- [ ] Define `refund_payment()` method

---

#### 5.13 `backend/apps/payments/gateways/stripe_adapter.py`

**Description**: Stripe payment gateway.

**Checklist**:
- [ ] Implement Stripe payment intent creation
- [ ] Implement Stripe webhook handling
- [ ] Implement refund processing

---

#### 5.14 `backend/apps/payments/gateways/hitpay_adapter.py`

**Description**: HitPay payment gateway (PayNow, GrabPay).

**Checklist**:
- [ ] Implement HitPay payment request creation
- [ ] Implement PayNow QR code generation
- [ ] Implement webhook handling

---

#### 5.15 `backend/apps/payments/services.py`

**Description**: Payment orchestrator.

**Features**:
- Gateway selection
- Fallback handling
- Payment recording

**Checklist**:
- [ ] Create `PaymentOrchestrator.process_payment()`
- [ ] Implement gateway fallback logic
- [ ] Record payment attempt and result

---

#### 5.16 `backend/apps/payments/views.py`

**Interfaces**:
- `POST /api/v1/payments/create-intent/`
- `POST /api/v1/payments/webhooks/stripe/`
- `POST /api/v1/payments/webhooks/hitpay/`

**Checklist**:
- [ ] Create payment intent endpoint
- [ ] Create Stripe webhook endpoint
- [ ] Create HitPay webhook endpoint

---

#### 5.17 `backend/apps/payments/urls.py`

**Checklist**:
- [ ] Add payment endpoints

---

#### 5.18 `backend/apps/integrations/__init__.py`

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 5.19 `backend/apps/integrations/logistics/__init__.py`

**Checklist**:
- [ ] Export logistics adapters

---

#### 5.20 `backend/apps/integrations/logistics/ninjavan.py`

**Description**: Ninja Van logistics adapter.

**Checklist**:
- [ ] Implement shipping rate quote
- [ ] Implement shipment creation
- [ ] Implement tracking lookup
- [ ] Implement webhook handling

---

#### 5.21 `backend/apps/integrations/logistics/singpost.py`

**Description**: SingPost logistics adapter.

**Checklist**:
- [ ] Implement shipping rate quote
- [ ] Implement shipment creation
- [ ] Implement tracking lookup

---

#### 5.22 `backend/apps/invoicenow/__init__.py`

**Description**: InvoiceNow/PEPPOL integration package.

**Checklist**:
- [ ] Create empty `__init__.py`

---

#### 5.23 `backend/apps/invoicenow/apps.py`

**Description**: InvoiceNow app configuration.

**Checklist**:
- [ ] Create `InvoiceNowConfig` class

---

#### 5.24 `backend/apps/invoicenow/models.py`

**Description**: PEPPOL invoice and submission models.

**Features**:
- `PEPPOLInvoice` with BIS 3.0 fields
- `InvoiceSubmission` tracking
- `InvoiceAcknowledgment` for responses

**Checklist**:
- [ ] Create `PEPPOLInvoice` with legal_monetary_totals JSONB
- [ ] Create `InvoiceSubmission` with status tracking
- [ ] Create `InvoiceAcknowledgment` for webhook responses
- [ ] Add indexes for status and submission date

---

#### 5.25 `backend/apps/invoicenow/peppol.py`

**Description**: PEPPOL BIS Billing 3.0 invoice generation.

**Features**:
- UBL 2.1 XML generation
- Schema validation
- legal_monetary_totals generation
- tax_total with Singapore GST

**Checklist**:
- [ ] Create `PEPPOLInvoiceGenerator` class
- [ ] Implement `generate_ubl_xml()` with all required elements
- [ ] Implement `validate_schema()` against PEPPOL schema
- [ ] Add legal_monetary_totals generation
- [ ] Add tax_total generation with GST codes

---

#### 5.26 `backend/apps/invoicenow/xml_signer.py`

**Description**: XML digital signature for PEPPOL documents.

**Features**:
- XMLDSig signing
- Certificate management
- Signature validation

**Checklist**:
- [ ] Create `XMLSigner` class
- [ ] Implement `sign_document()` with enveloped signature
- [ ] Implement certificate loading from settings
- [ ] Add signature validation method

---

#### 5.27 `backend/apps/invoicenow/access_point.py`

**Description**: Access Point Provider integration.

**Features**:
- Singapore AP client (e.g., Peppol.sg)
- Document submission
- Status polling

**Checklist**:
- [ ] Create `AccessPointClient` class
- [ ] Implement `submit_invoice()` method
- [ ] Implement `check_status()` method
- [ ] Add retry logic with exponential backoff

---

#### 5.28 `backend/apps/invoicenow/tasks.py`

**Description**: Django Tasks for PEPPOL async operations.

**Features**:
- Async invoice submission
- Acknowledgment processing
- Retry handling

**Checklist**:
- [ ] Create `submit_peppol_invoice` task
- [ ] Create `process_peppol_acknowledgment` task
- [ ] Create `retry_failed_submissions` periodic task

---

#### 5.29 `backend/apps/invoicenow/serializers.py`

**Description**: DRF serializers for PEPPOL invoices.

**Checklist**:
- [ ] Create `PEPPOLInvoiceSerializer`
- [ ] Create `InvoiceSubmissionSerializer`

---

#### 5.30 `backend/apps/invoicenow/views.py`

**Description**: API views for PEPPOL operations.

**Interfaces**:
- `/api/v1/invoicenow/invoices/`
- `/api/v1/invoicenow/submit/`
- `/api/v1/invoicenow/status/`

**Checklist**:
- [ ] Create `PEPPOLInvoiceViewSet`
- [ ] Add `submit_invoice` action
- [ ] Add `check_status` action

---

#### 5.31 `backend/apps/invoicenow/urls.py`

**Checklist**:
- [ ] Register ViewSets with router

---

### Phase 5 Verification Plan

**Unit Tests**:
```bash
cd backend
uv run pytest apps/compliance/tests/ apps/payments/tests/ -v
```

**Integration Tests**:
1. Test Stripe payment flow with test API keys
2. Test HitPay payment flow with sandbox
3. Test Ninja Van shipment creation with sandbox

---

## Phase 6: Frontend Foundation

**Duration**: Weeks 16-18
**Dependencies**: Phase 1-5 (backend complete)
**Goal**: Set up Next.js project structure, components, and API client

### Files to Create

---

#### 6.1 `frontend/src/app/layout.tsx`

**Description**: Root layout component.

**Features**:
- HTML structure
- Font loading
- Global providers

**Checklist**:
- [ ] Set up HTML with lang="en"
- [ ] Configure fonts (Inter)
- [ ] Wrap with providers (QueryClient, Auth)

---

#### 6.2 `frontend/src/app/page.tsx`

**Description**: Homepage.

**Features**:
- Featured products
- Hero section
- Category navigation

**Checklist**:
- [ ] Create hero section
- [ ] Display featured products
- [ ] Add category quick links

---

#### 6.3 `frontend/src/app/globals.css`

**Description**: Global styles.

**Checklist**:
- [ ] Import Tailwind directives
- [ ] Define CSS variables for theme
- [ ] Add custom utility classes

---

#### 6.4 `frontend/src/lib/api/client.ts`

**Description**: API client with axios.

**Features**:
- Base URL configuration
- JWT token handling
- Error interceptors
- Token refresh

**Checklist**:
- [ ] Create axios instance
- [ ] Add request interceptor for JWT
- [ ] Add response interceptor for 401 refresh
- [ ] Export typed API methods

---

#### 6.5 `frontend/src/lib/api/endpoints.ts`

**Description**: API endpoint definitions.

**Features**:
- Typed API functions
- Request/response types

**Checklist**:
- [ ] Create product API functions
- [ ] Create cart API functions
- [ ] Create order API functions
- [ ] Create auth API functions

---

#### 6.6 `frontend/src/lib/hooks/useAuth.ts`

**Description**: Authentication hook.

**Features**:
- Login/logout
- Token management
- User state

**Checklist**:
- [ ] Create `useAuth` hook
- [ ] Implement login mutation
- [ ] Implement logout
- [ ] Manage JWT in httpOnly cookie or localStorage

---

#### 6.7 `frontend/src/lib/hooks/useCart.ts`

**Description**: Cart management hook.

**Features**:
- Add/remove items
- Cart state
- Persist across sessions

**Checklist**:
- [ ] Create `useCart` hook with React Query
- [ ] Implement add item mutation
- [ ] Implement remove item mutation
- [ ] Implement quantity update

---

#### 6.8 `frontend/src/components/ui/button.tsx`

**Description**: Button component.

**Checklist**:
- [ ] Create Button with variants (primary, secondary, ghost)
- [ ] Add loading state
- [ ] Add disabled state

---

#### 6.9 `frontend/src/components/ui/input.tsx`

**Description**: Input component.

**Checklist**:
- [ ] Create Input with label
- [ ] Add error state
- [ ] Add help text

---

#### 6.10 `frontend/src/components/ui/card.tsx`

**Description**: Card component.

**Checklist**:
- [ ] Create Card container
- [ ] Create CardHeader, CardContent, CardFooter

---

#### 6.11 `frontend/src/components/layout/header.tsx`

**Description**: Site header.

**Features**:
- Logo
- Navigation
- Cart icon with count
- User menu

**Checklist**:
- [ ] Create responsive header
- [ ] Add cart badge with item count
- [ ] Add user dropdown menu
- [ ] Add mobile menu

---

#### 6.12 `frontend/src/components/layout/footer.tsx`

**Description**: Site footer.

**Checklist**:
- [ ] Create footer with links
- [ ] Add social icons
- [ ] Add copyright

---

#### 6.13 `frontend/src/components/products/product-card.tsx`

**Description**: Product card for grid display.

**Features**:
- Image with fallback
- Title, price, GST-inclusive
- Add to cart button

**Checklist**:
- [ ] Create responsive product card
- [ ] Show GST-inclusive price
- [ ] Add to cart with quantity selector

---

#### 6.14 `frontend/src/components/products/product-grid.tsx`

**Description**: Product grid layout.

**Checklist**:
- [ ] Create responsive grid
- [ ] Add loading skeleton
- [ ] Add empty state

---

#### 6.15 `frontend/src/types/index.ts`

**Description**: TypeScript type definitions.

**Checklist**:
- [ ] Define Product type
- [ ] Define Order type
- [ ] Define Cart type
- [ ] Define User type

---

#### 6.16 `frontend/next.config.js`

**Description**: Next.js configuration.

**Checklist**:
- [ ] Configure image domains
- [ ] Set up environment variables
- [ ] Configure PWA settings

---

#### 6.17 `frontend/tailwind.config.js`

**Description**: Tailwind configuration.

**Checklist**:
- [ ] Define color palette
- [ ] Configure fonts
- [ ] Add custom breakpoints

---

### Phase 6 Verification Plan

**Build Check**:
```bash
cd frontend
npm run build
npm run lint
npm run type-check
```

**Visual Verification**:
1. Start dev server: `npm run dev`
2. Verify homepage renders
3. Verify component styling
4. Test responsive layouts

---

## Phase 7: Frontend Features

**Duration**: Weeks 19-22
**Dependencies**: Phase 6 (frontend foundation)
**Goal**: Implement storefront, cart, checkout, and user dashboard

### Files to Create

---

#### 7.1 `frontend/src/app/products/page.tsx`

**Description**: Product listing page.

**Features**:
- Product grid
- Category filter
- Search
- Pagination

**Checklist**:
- [ ] Fetch products with React Query
- [ ] Implement category filter
- [ ] Implement search
- [ ] Add pagination

---

#### 7.2 `frontend/src/app/products/[slug]/page.tsx`

**Description**: Product detail page.

**Features**:
- Product images
- Variant selection
- Add to cart
- Related products

**Checklist**:
- [ ] Fetch product by slug
- [ ] Display image gallery
- [ ] Implement variant selector
- [ ] Add to cart with quantity

---

#### 7.3 `frontend/src/app/cart/page.tsx`

**Description**: Shopping cart page.

**Features**:
- Cart items list
- Quantity update
- Remove items
- Cart summary with GST

**Checklist**:
- [ ] Display cart items
- [ ] Update quantity
- [ ] Remove items
- [ ] Show subtotal, GST, total

---

#### 7.4 `frontend/src/app/checkout/page.tsx`

**Description**: Checkout page.

**Features**:
- Shipping address form
- Payment method selection
- Order summary
- Place order

**Checklist**:
- [ ] Create address form with validation
- [ ] Integrate Stripe Elements
- [ ] Integrate PayNow QR
- [ ] Submit order

---

#### 7.5 `frontend/src/app/checkout/success/page.tsx`

**Description**: Order success page.

**Checklist**:
- [ ] Display order confirmation
- [ ] Show order number
- [ ] Provide tracking info link

---

#### 7.6 `frontend/src/app/account/page.tsx`

**Description**: User account dashboard.

**Checklist**:
- [ ] Display user profile
- [ ] Show recent orders
- [ ] Link to order history

---

#### 7.7 `frontend/src/app/account/orders/page.tsx`

**Description**: Order history page.

**Checklist**:
- [ ] List all orders
- [ ] Show order status
- [ ] Link to order details

---

#### 7.8 `frontend/src/app/account/orders/[id]/page.tsx`

**Description**: Order detail page.

**Checklist**:
- [ ] Display order details
- [ ] Show order items
- [ ] Show tracking info
- [ ] Download invoice

---

#### 7.9 `frontend/src/app/login/page.tsx`

**Description**: Login page.

**Checklist**:
- [ ] Create login form
- [ ] Handle authentication
- [ ] Redirect on success

---

#### 7.10 `frontend/src/app/register/page.tsx`

**Description**: Registration page.

**Checklist**:
- [ ] Create registration form
- [ ] PDPA consent checkbox
- [ ] Handle registration

---

#### 7.11 `frontend/src/components/checkout/address-form.tsx`

**Description**: Shipping address form.

**Checklist**:
- [ ] Create form with react-hook-form
- [ ] Singapore postal code validation
- [ ] Unit number field

---

#### 7.12 `frontend/src/components/checkout/payment-form.tsx`

**Description**: Payment method form.

**Features**:
- Stripe card input
- PayNow QR option

**Checklist**:
- [ ] Integrate Stripe Elements
- [ ] Show PayNow QR code
- [ ] Handle payment method selection

---

#### 7.13 `frontend/src/components/checkout/order-summary.tsx`

**Description**: Order summary component.

**Checklist**:
- [ ] Display line items
- [ ] Show subtotal, shipping, GST, total
- [ ] Format currency as SGD

---

### Phase 7 Verification Plan

**E2E Tests**:
```bash
cd frontend
npm run test:e2e
```

**Manual Verification**:
1. Browse products, add to cart
2. Complete checkout with test card
3. Verify order in user dashboard
4. Test PayNow QR generation

---

## Phase 8: Testing & Deployment

**Duration**: Weeks 23-28
**Dependencies**: All previous phases
**Goal**: Comprehensive testing, security audit, and production deployment

### Files to Create

---

#### 8.1 `backend/tests/conftest.py`

**Description**: Pytest configuration.

**Checklist**:
- [ ] Create test database fixtures
- [ ] Create user and company fixtures
- [ ] Create API client fixture

---

#### 8.2 `backend/tests/e2e/test_order_flow.py`

**Description**: End-to-end order flow test.

**Checklist**:
- [ ] Test complete order flow
- [ ] Verify inventory reservation
- [ ] Verify invoice generation
- [ ] Verify GST calculation

---

#### 8.3 `frontend/cypress/e2e/checkout.cy.ts`

**Description**: Cypress E2E test for checkout.

**Checklist**:
- [ ] Test add to cart
- [ ] Test checkout form submission
- [ ] Test payment completion
- [ ] Test order confirmation

---

#### 8.4 `docker/docker-compose.yml`

**Description**: Docker Compose for local development.

**Checklist**:
- [ ] Django service
- [ ] Celery worker service
- [ ] PostgreSQL service
- [ ] Redis service
- [ ] Next.js service

---

#### 8.5 `docker/Dockerfile.backend`

**Description**: Backend Dockerfile.

**Checklist**:
- [ ] Python 3.12 base image
- [ ] Install dependencies with uv
- [ ] Configure Gunicorn

---

#### 8.6 `docker/Dockerfile.frontend`

**Description**: Frontend Dockerfile.

**Checklist**:
- [ ] Node 20 base image
- [ ] Build Next.js app
- [ ] Configure production server

---

#### 8.7 `.github/workflows/ci.yml`

**Description**: CI pipeline.

**Checklist**:
- [ ] Run backend tests
- [ ] Run frontend tests
- [ ] Run linting
- [ ] Build Docker images

---

#### 8.8 `.github/workflows/deploy.yml`

**Description**: CD pipeline.

**Checklist**:
- [ ] Deploy to staging on PR merge
- [ ] Deploy to production on release
- [ ] Run database migrations

---

#### 8.9 `docs/runbook.md`

**Description**: Operations runbook.

**Checklist**:
- [ ] Document deployment process
- [ ] Document rollback procedure
- [ ] Document monitoring alerts

---

### Phase 8 Verification Plan

**Full Test Suite**:
```bash
# Backend
cd backend
uv run pytest --cov=apps --cov-report=html

# Frontend
cd frontend
npm run test
npm run test:e2e
```

**Security Audit**:
1. Run OWASP ZAP scan
2. Run Snyk dependency scan
3. Perform manual penetration testing

**Performance Testing**:
1. Run k6 load tests
2. Verify <200ms API response (p95)
3. Verify <2s page load on mobile

---

## Summary

| Phase | Duration | Files | Key Deliverables |
|-------|----------|-------|------------------|
| **1. Foundation** | 3 weeks | 26 files | Django setup, auth, admin |
| **2. Commerce** | 3 weeks | 20 files | Products, orders, cart |
| **3. Inventory** | 3 weeks | 12 files | Stock tracking, reservations |
| **4. Accounting** | 3 weeks | 14 files | Ledger, invoices, GST |
| **5. Compliance** | 3 weeks | 21 files | PDPA, payments, logistics |
| **6. Frontend Foundation** | 3 weeks | 17 files | Next.js setup, components |
| **7. Frontend Features** | 4 weeks | 13 files | Storefront, checkout |
| **8. Testing & Deploy** | 6 weeks | 9 files | E2E tests, CI/CD, production |

**Total**: ~132 files across 28 weeks
