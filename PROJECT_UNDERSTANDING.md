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

**Document Version**: 1.0
**Created**: December 18, 2025
**Author**: AI Coding Agent (Meticulous Approach Framework)
