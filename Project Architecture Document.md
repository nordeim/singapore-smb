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

## Update Log

- **2025-12-19**: Synced PAD with QA-audit-driven schema/design updates.
  - **GST**: Historical rates (`compliance.gst_rates`) and historical lookup in `calculate_gst(amount, gst_code, transaction_date)`.
  - **Orders**: Concurrency-safe order numbering via per-company sequences (`core.sequences`) used by `generate_order_number(company_id)`.
  - **Commerce**: Cart persistence (`commerce.carts`, `commerce.cart_items`).
  - **InvoiceNow readiness**: PEPPOL operational tables (`compliance.peppol_invoices`, `compliance.peppol_acknowledgments`).
  - **Accounting**: CoA seeding via templates + initializer (`accounting.account_templates`, `initialize_company_accounts(company_id)`).
  - **Multi-tenancy**: Expanded RLS coverage/policies for the newly introduced tables.

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
    │  PostgreSQL 16  │          │   Redis 7.4+    │          │   AWS S3        │
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

### 3.3 Implementation Status (December 2025)

| Phase | Focus | Status | Tests |
|-------|-------|--------|-------|
| Phase 1 | Foundation (accounts, core) | ✅ Complete | 61 |
| Phase 2 | Commerce Domain | ✅ Complete | 64 |
| Phase 3 | Inventory Domain | ✅ Complete | 57 |
| Phase 4 | Accounting Domain | ✅ Complete | 91 |
| Phase 5 | Compliance & Integrations | ✅ Complete | 97 |
| **Total** | **Backend Implementation** | **✅** | **370** |

**Phase 5 Key Components:**
- **Compliance App**: GST F5 returns, PDPA consent (6 types), audit logging (7-year retention)
- **Payments App**: Stripe (primary) + HitPay (fallback) with webhooks
- **Integrations App**: NinjaVan + SingPost logistics
- **InvoiceNow App**: PEPPOL BIS 3.0 via Zetta Solution AP

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

### 5.3 QA-Audit-Driven Critical Schema Updates (Implemented)

- **GST historical correctness**: `compliance.gst_rates` is the source-of-truth for effective-date GST rates; GST calculation uses `transaction_date` for backdated transactions.
- **Order numbering safety**: `core.sequences` prevents race conditions during order-number generation under concurrent order creation.
- **Cart persistence**: `commerce.carts` and `commerce.cart_items` support session carts, customer carts, merge, and conversion to orders.
- **InvoiceNow readiness**: `compliance.peppol_invoices` and `compliance.peppol_acknowledgments` model the PEPPOL submission + ack lifecycle.
- **CoA initialization**: `accounting.account_templates` and `initialize_company_accounts(company_id)` ensure per-company accounts without violating `NOT NULL` constraints.
- **Multi-tenancy isolation**: RLS policies are extended to new tables (including join-based policies where `company_id` is indirect).

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

**Document Version**: 2.0
**Created**: December 18, 2025
**Author**: AI Coding Agent (Meticulous Approach Framework)
