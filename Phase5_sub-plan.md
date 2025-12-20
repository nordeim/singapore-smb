# Phase 5: Compliance & Integrations — Final Implementation Plan

> **Version**: 2.0 (Validated)  
> **Created**: December 20, 2025  
> **Duration**: Weeks 13-15  
> **Dependencies**: Phase 4 (Accounting Domain)  
> **Status**: 🔲 Awaiting Approval

---

## Executive Summary

Phase 5 implements Singapore regulatory compliance and external integrations across 4 sub-domains:

| Sub-Domain | App | Key Deliverables | Files |
|-----------|-----|------------------|-------|
| **Compliance** | `apps/compliance/` | PDPA consent history, data access requests (30-day SLA), audit logging, GST F5 returns | 18 |
| **Payments** | `apps/payments/` | Gateway abstraction, Stripe + HitPay/PayNow adapters, webhooks | 16 |
| **Logistics** | `apps/integrations/` | NinjaVan + SingPost shipping adapters | 10 |
| **InvoiceNow** | `apps/invoicenow/` | PEPPOL BIS 3.0 UBL XML generation, Access Point submission | 16 |

**Total**: ~60 files, 80+ tests

---

## User Review Required

> [!IMPORTANT]
> **Decisions requiring approval before implementation:**

1. **PEPPOL Access Point**: Which Singapore Access Point provider? (e.g., Peppol.sg, InvoiceNow.sg)
2. **Audit Log Retention**: Indefinite vs. time-based purging policy?
3. **HitPay vs PayNow Direct**: HitPay provides PayNow QR - use HitPay or integrate PayNow directly via bank?
4. **Gateway Fallback Strategy**: Auto-fallback between gateways or manual selection?

> [!WARNING]
> **Existing Code Architecture Notes:**
> - Customer model (`commerce.models.Customer`) already has `consent_marketing`, `consent_analytics` boolean fields with timestamps
> - Invoice model (`accounting.models.Invoice`) already has `peppol_id`, `peppol_status`, `peppol_submitted_at` fields
> - Phase 5 EXTENDS these, not duplicates - compliance.DataConsent provides granular audit history

---

## 1. Compliance App

### 1.1 Directory Structure

```
backend/apps/compliance/
├── __init__.py
├── apps.py
├── admin.py
├── models/
│   ├── __init__.py
│   ├── gst_return.py        # GST F5 returns
│   ├── data_consent.py      # PDPA consent audit trail
│   ├── data_access_request.py  # PDPA access/deletion
│   └── audit_log.py         # Change audit trail
├── services/
│   ├── __init__.py
│   ├── pdpa_service.py      # Consent + data export
│   ├── audit_service.py     # Audit logging
│   └── gst_return_service.py # F5 preparation
├── serializers.py
├── views.py
├── urls.py
├── signals.py               # Auto audit logging
├── tasks.py
├── migrations/
│   ├── __init__.py
│   ├── 0001_create_schema.py
│   └── 0002_initial.py
└── tests/
    ├── __init__.py
    ├── factories.py
    ├── test_models.py
    ├── test_pdpa_service.py
    ├── test_audit_service.py
    ├── test_gst_return_service.py
    └── test_views.py
```

---

### 1.2 Models

#### [NEW] `models/gst_return.py`

| Field | Type | Purpose |
|-------|------|---------|
| `company` | FK | Multi-tenant owner |
| `period_start`, `period_end` | DATE | Filing period |
| `quarter`, `year` | INT | Q1-Q4, 2024+ |
| `box_1` - `box_8` | DECIMAL(12,2) | F5 form values |
| `status` | VARCHAR | draft → validated → submitted → accepted/rejected |
| `iras_reference` | VARCHAR | IRAS submission ID |
| `prepared_by`, `submitted_by` | FK(User) | Audit |

**Schema Reference**: `compliance.gst_returns` (lines 860-894)

**Checklist**:
- [ ] Create model matching schema
- [ ] Add `validate_boxes()` - Box 4 = 1+2+3, Box 8 = 6-7
- [ ] Add `can_submit()` - business rules validation
- [ ] Add status transition methods
- [ ] Add unique constraint: (company_id, year, quarter)

---

#### [NEW] `models/data_consent.py`

| Field | Type | Purpose |
|-------|------|---------|
| `customer` | FK | Links to commerce.Customer |
| `consent_type` | VARCHAR | 6 types (order_processing, marketing, etc.) |
| `is_granted` | BOOLEAN | Consent given/withdrawn |
| `source` | VARCHAR | Where consent was given (registration, checkout) |
| `ip_address` | INET | Recording context |
| `consent_timestamp` | TIMESTAMPTZ | When consent recorded |

**Schema Reference**: `compliance.data_consents` (lines 941-968)

**Architecture Note**: This table provides an **immutable audit history** of consent changes. The `commerce.Customer.consent_marketing` boolean field is the **current state**. When consent changes, a new `DataConsent` record is created and `Customer` field is updated.

**Checklist**:
- [ ] Create model matching schema
- [ ] Override `save()` to prevent updates (immutable)
- [ ] Add `record_consent()` class method that updates both tables
- [ ] Add index on customer_id

---

#### [NEW] `models/data_access_request.py`

| Field | Type | Purpose |
|-------|------|---------|
| `company`, `customer` | FK | Multi-tenant, requester |
| `request_type` | VARCHAR | access, correction, deletion |
| `status` | VARCHAR | pending → processing → completed/rejected |
| `requested_at` | TIMESTAMPTZ | When submitted |
| `due_date` | DATE | Auto-calculated: requested_at + 30 days |
| `completed_at` | TIMESTAMPTZ | When resolved |
| `response_notes` | TEXT | Resolution notes |
| `processed_by` | FK(User) | Who handled it |

**Schema Reference**: `compliance.data_access_requests` (lines 973-996)

**Checklist**:
- [ ] Create model with auto-calculated `due_date`
- [ ] Add `is_overdue` property
- [ ] Add `complete()`, `reject()` methods
- [ ] Add SLA tracking utilities

---

#### [NEW] `models/audit_log.py`

| Field | Type | Purpose |
|-------|------|---------|
| `company`, `user` | FK | Context |
| `action` | VARCHAR | CREATE, UPDATE, DELETE |
| `resource_type` | VARCHAR | Model name |
| `resource_id` | UUID | Object ID |
| `old_values`, `new_values` | JSONB | State diff |
| `ip_address` | INET | Request context |
| `created_at` | TIMESTAMPTZ | Timestamp |

**Schema Reference**: `compliance.audit_logs` (lines 1002-1027)

**Checklist**:
- [ ] Create immutable model (no update/delete)
- [ ] Add `create_for_model()` class method
- [ ] Add serialization helpers for JSONB

---

### 1.3 Services

#### [NEW] `services/pdpa_service.py`

```python
class PDPAService:
    @staticmethod
    def record_consent(customer, consent_type, is_granted, source, ip_address, user_agent) -> DataConsent
    
    @staticmethod
    def export_customer_data(customer) -> dict  # Full PII export for PDPA request
    
    @staticmethod
    def anonymize_customer(customer) -> None  # Replace PII with tokens
    
    @staticmethod
    def process_access_request(request_id, action, notes, user) -> DataAccessRequest
    
    @staticmethod
    def get_consent_summary(customer) -> dict  # Current state by type
```

**Integration**: Updates `commerce.Customer` consent fields when consent changes.

**Checklist**:
- [ ] Implement all methods following service patterns
- [ ] Use `transaction.atomic()` for consent recording
- [ ] Include Orders, Addresses in data export
- [ ] Add PII replacement for anonymization

---

#### [NEW] `services/audit_service.py`

```python
class AuditService:
    @staticmethod
    def log_change(action, resource_type, resource_id, old_values, new_values, user, ip) -> AuditLog
    
    @staticmethod
    def get_history(resource_type, resource_id) -> QuerySet
    
    @staticmethod
    def get_user_activity(user_id, since_date) -> QuerySet
```

**Checklist**:
- [ ] Implement change logging
- [ ] Add automatic diff calculation
- [ ] Add query methods with ordering

---

#### [NEW] `services/gst_return_service.py`

```python
class GSTReturnService:
    @staticmethod
    def prepare_return(company_id, quarter, year) -> GSTReturn
    
    @staticmethod
    def validate_return(return_id) -> tuple[bool, list[str]]
    
    @staticmethod
    def submit_return(return_id, submitted_by) -> GSTReturn
```

**Integration**: Uses `apps.accounting.gst.GSTEngine.prepare_f5()` for box calculations.

**Checklist**:
- [ ] Integrate with existing GSTEngine
- [ ] Add box validation logic
- [ ] Add status transition enforcement

---

### 1.4 Signals

#### [NEW] `signals.py`

Auto-audit logging for configured models via Django signals.

```python
AUDIT_MODELS = [
    'accounts.Company',
    'accounts.User', 
    'commerce.Order',
    'accounting.Invoice',
    'accounting.Payment',
]
```

**Checklist**:
- [ ] Create `post_save` handler for tracked models
- [ ] Create `post_delete` handler
- [ ] Calculate old/new value diff on updates
- [ ] Get IP from thread-local or request

---

### 1.5 Views & URLs

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/v1/compliance/gst-returns/` | GET, POST | List/create GST returns |
| `/api/v1/compliance/gst-returns/{id}/` | GET | Return detail |
| `/api/v1/compliance/gst-returns/{id}/validate/` | POST | Validate boxes |
| `/api/v1/compliance/gst-returns/{id}/submit/` | POST | Submit to IRAS |
| `/api/v1/compliance/data-requests/` | GET, POST | PDPA requests |
| `/api/v1/compliance/data-requests/{id}/complete/` | POST | Mark complete |
| `/api/v1/compliance/audit-logs/` | GET | Read-only, filterable |
| `/api/v1/compliance/consent/` | POST | Record consent |
| `/api/v1/compliance/consent/status/` | GET | Current consent state |

**Permissions**: Finance role for GST, Admin for audit logs.

---

### 1.6 Admin

#### [NEW] `admin.py`

**Checklist**:
- [ ] `GSTReturnAdmin` with status colors, readonly boxes for submitted
- [ ] `DataAccessRequestAdmin` with SLA indicators
- [ ] `AuditLogAdmin` read-only with filters
- [ ] `DataConsentAdmin` read-only

---

## 2. Payments App

### 2.1 Directory Structure

```
backend/apps/payments/
├── __init__.py
├── apps.py
├── exceptions.py
├── gateways/
│   ├── __init__.py
│   ├── base.py              # Abstract adapter
│   ├── stripe_adapter.py
│   └── hitpay_adapter.py
├── services/
│   ├── __init__.py
│   └── payment_orchestrator.py
├── serializers.py
├── views.py
├── urls.py
├── webhooks.py
├── tasks.py
└── tests/
    ├── __init__.py
    ├── factories.py
    ├── test_gateways.py
    ├── test_orchestrator.py
    └── test_webhooks.py
```

**Note**: No new models - uses existing `accounting.Payment`.

---

### 2.2 Gateway Abstraction

#### [NEW] `gateways/base.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class PaymentIntent:
    id: str
    client_secret: str
    amount: Decimal
    currency: str
    status: str
    gateway: str
    metadata: dict

@dataclass
class PaymentResult:
    success: bool
    payment_id: str
    gateway_reference: str
    error_message: Optional[str] = None

class PaymentGatewayAdapter(ABC):
    name: str
    
    @abstractmethod
    def create_payment_intent(self, amount: Decimal, currency: str, order_id, metadata: dict) -> PaymentIntent:
        pass
    
    @abstractmethod
    def capture_payment(self, payment_intent_id: str) -> PaymentResult:
        pass
    
    @abstractmethod
    def refund_payment(self, payment_id: str, amount: Decimal, reason: str) -> PaymentResult:
        pass
    
    @abstractmethod
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        pass
```

---

#### [NEW] `gateways/stripe_adapter.py`

**Features**: Card payments, Apple Pay, Google Pay, webhook verification.

**Checklist**:
- [ ] Implement `StripeAdapter(PaymentGatewayAdapter)`
- [ ] `create_payment_intent()` with idempotency key
- [ ] `capture_payment()` for manual capture
- [ ] `refund_payment()` with partial support
- [ ] `verify_webhook()` with Stripe signature

---

#### [NEW] `gateways/hitpay_adapter.py`

**Features**: PayNow QR, GrabPay, ShopeePay.

**Checklist**:
- [ ] Implement `HitPayAdapter(PaymentGatewayAdapter)`
- [ ] `create_payment_intent()` → payment request
- [ ] Add `generate_paynow_qr()` helper
- [ ] HMAC webhook verification

---

### 2.3 Orchestrator Service

#### [NEW] `services/payment_orchestrator.py`

```python
class PaymentOrchestrator:
    @staticmethod
    def process_payment(order_id, payment_method, amount, gateway=None) -> PaymentResult
    
    @staticmethod
    def get_available_methods(order) -> list[str]
    
    @staticmethod
    def handle_payment_success(payment_id) -> None  # Update order, trigger invoice
    
    @staticmethod
    def handle_payment_failure(payment_id, reason) -> None
```

**Checklist**:
- [ ] Gateway selection by payment method
- [ ] Optional fallback on failure
- [ ] Create `accounting.Payment` record
- [ ] Integration with `OrderService` and `InvoiceService`

---

### 2.4 Webhooks

#### [NEW] `webhooks.py`

| Endpoint | Exempt | Purpose |
|----------|--------|---------|
| `/api/v1/payments/webhooks/stripe/` | CSRF | Stripe events |
| `/api/v1/payments/webhooks/hitpay/` | CSRF | HitPay events |

**Features**: Signature verification, idempotent processing.

**Checklist**:
- [ ] `StripeWebhookView` handling `payment_intent.succeeded/failed`
- [ ] `HitPayWebhookView` handling `payment.completed/failed`
- [ ] Idempotency via payment reference check

---

### 2.5 Views

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/payments/create-intent/` | POST | Create payment intent for frontend |
| `/api/v1/payments/methods/` | GET | Available payment methods |
| `/api/v1/payments/status/{order_id}/` | GET | Payment status check |

---

## 3. Integrations App

### 3.1 Directory Structure

```
backend/apps/integrations/
├── __init__.py
├── apps.py
├── logistics/
│   ├── __init__.py
│   ├── base.py
│   ├── ninjavan.py
│   └── singpost.py
├── services/
│   ├── __init__.py
│   └── shipping_service.py
├── serializers.py
├── views.py
├── urls.py
├── tasks.py
└── tests/
    ├── __init__.py
    ├── test_ninjavan.py
    └── test_singpost.py
```

---

### 3.2 Logistics Adapters

#### [NEW] `logistics/base.py`

```python
@dataclass
class ShippingRate:
    provider: str
    service_type: str
    price: Decimal
    currency: str = 'SGD'
    estimated_days: int = 3

@dataclass  
class Shipment:
    id: str
    tracking_number: str
    label_url: str
    status: str

class LogisticsAdapter(ABC):
    name: str
    
    @abstractmethod
    def get_rates(self, origin, destination, weight_grams, dimensions) -> list[ShippingRate]
    
    @abstractmethod
    def create_shipment(self, order_id, rate_id, pickup_details) -> Shipment
    
    @abstractmethod
    def get_tracking(self, tracking_number) -> dict
```

---

#### [NEW] `logistics/ninjavan.py`

**Checklist**:
- [ ] Implement `NinjaVanAdapter`
- [ ] Rate quotes with service types
- [ ] Shipment creation with label
- [ ] Tracking API integration

---

#### [NEW] `logistics/singpost.py`

**Checklist**:
- [ ] Implement `SingPostAdapter`
- [ ] Registered/Speedpost rates
- [ ] Shipment creation
- [ ] Tracking integration

---

### 3.3 Shipping Service

```python
class ShippingService:
    @staticmethod
    def get_rates(order) -> list[ShippingRate]  # Aggregate all carriers
    
    @staticmethod
    def create_shipment(order, rate_id) -> Shipment
    
    @staticmethod
    def update_fulfillment_status(tracking_number, status) -> None
```

---

## 4. InvoiceNow App

### 4.1 Directory Structure

```
backend/apps/invoicenow/
├── __init__.py
├── apps.py
├── admin.py
├── models/
│   ├── __init__.py
│   ├── peppol_invoice.py
│   └── peppol_acknowledgment.py
├── services/
│   ├── __init__.py
│   ├── peppol_service.py
│   └── ubl_generator.py
├── xml_signer.py
├── access_point.py
├── serializers.py
├── views.py
├── urls.py
├── tasks.py
└── tests/
    ├── __init__.py
    ├── factories.py
    ├── test_ubl_generator.py
    ├── test_peppol_service.py
    └── test_views.py
```

---

### 4.2 Models

#### [NEW] `models/peppol_invoice.py`

**Schema Reference**: `compliance.peppol_invoices` (lines 900-924)

**Note**: Extends existing `accounting.Invoice.peppol_*` fields with full submission tracking.

| Field | Type | Purpose |
|-------|------|---------|
| `invoice` | FK(Invoice) | Link to accounting invoice |
| `peppol_id` | VARCHAR | PEPPOL document ID |
| `sender_endpoint`, `receiver_endpoint` | VARCHAR | PEPPOL participants |
| `status` | VARCHAR | draft → validated → signed → submitted → acknowledged/rejected |
| `xml_document` | TEXT | Generated UBL XML |
| `signature_value` | TEXT | XMLDSig signature |
| `access_point_provider` | VARCHAR | AP used |
| `submission_reference` | VARCHAR | AP submission ID |

**Checklist**:
- [ ] Create model matching schema
- [ ] Link to accounting.Invoice via FK
- [ ] Add status transition methods
- [ ] Sync status back to Invoice.peppol_status

---

#### [NEW] `models/peppol_acknowledgment.py`

**Schema Reference**: `compliance.peppol_acknowledgments` (lines 926-934)

**Checklist**:
- [ ] Create model for AP responses
- [ ] Store raw JSONB response
- [ ] Link to PEPPOLInvoice

---

### 4.3 Services

#### [NEW] `services/ubl_generator.py`

```python
class UBLGenerator:
    @staticmethod
    def generate(invoice, seller_company, buyer_customer) -> str  # UBL 2.1 XML
    
    @staticmethod
    def validate_schema(xml: str) -> tuple[bool, list[str]]
```

**PEPPOL BIS Billing 3.0 Requirements**:
- CustomizationID for Singapore profile
- ProfileID: `urn:fdc:peppol.eu:2017:poacc:billing:01:1.0`
- InvoiceTypeCode: 380
- AccountingSupplierParty with UEN
- AccountingCustomerParty
- InvoiceLine with item details
- TaxTotal with Singapore GST codes
- LegalMonetaryTotal (7 fields)

**Checklist**:
- [ ] Generate complete UBL XML structure
- [ ] Map GST codes (SR→S, ZR→Z, ES→E, OS→O)
- [ ] Include all monetary totals
- [ ] Add schema validation (lxml)

---

#### [NEW] `services/peppol_service.py`

```python
class PEPPOLService:
    @staticmethod
    def prepare_invoice(invoice_id) -> PEPPOLInvoice  # Generate UBL
    
    @staticmethod
    def validate_invoice(peppol_id) -> tuple[bool, list[str]]
    
    @staticmethod
    def sign_invoice(peppol_id) -> PEPPOLInvoice
    
    @staticmethod
    def submit_invoice(peppol_id) -> PEPPOLInvoice
    
    @staticmethod
    def process_acknowledgment(peppol_id, ack_data) -> PEPPOLAcknowledgment
```

---

### 4.4 XML Signing

#### [NEW] `xml_signer.py`

Uses `signxml` library for XMLDSig.

**Checklist**:
- [ ] Implement enveloped signature
- [ ] Load certificate from path/env
- [ ] Add verification method

---

### 4.5 Access Point Client

#### [NEW] `access_point.py`

```python
class AccessPointClient:
    def submit(self, signed_xml: str, receiver_endpoint: str) -> SubmissionResult
    def check_status(self, submission_reference: str) -> StatusResult
```

**Checklist**:
- [ ] HTTP client with retry
- [ ] Configure from settings
- [ ] Handle AP-specific responses

---

### 4.6 Views

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/invoicenow/invoices/` | GET | List PEPPOL invoices |
| `/api/v1/invoicenow/invoices/{id}/prepare/` | POST | Generate UBL |
| `/api/v1/invoicenow/invoices/{id}/validate/` | POST | Validate XML |
| `/api/v1/invoicenow/invoices/{id}/submit/` | POST | Submit to AP |
| `/api/v1/invoicenow/invoices/{id}/download/` | GET | Download XML |

---

## 5. Configuration Changes

### 5.1 Settings

#### [MODIFY] `config/settings/base.py`

```python
LOCAL_APPS = [
    # ... existing ...
    'apps.compliance',
    'apps.payments',
    'apps.integrations',
    'apps.invoicenow',
]

# Payment Gateways
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')
HITPAY_API_KEY = env('HITPAY_API_KEY', default='')
HITPAY_SALT = env('HITPAY_SALT', default='')

# Logistics
NINJAVAN_API_KEY = env('NINJAVAN_API_KEY', default='')
SINGPOST_API_KEY = env('SINGPOST_API_KEY', default='')

# PEPPOL
PEPPOL_AP_URL = env('PEPPOL_AP_URL', default='')
PEPPOL_AP_KEY = env('PEPPOL_AP_KEY', default='')
PEPPOL_SENDER_ID = env('PEPPOL_SENDER_ID', default='')
PEPPOL_CERT_PATH = env('PEPPOL_CERT_PATH', default='')

# Audit
AUDIT_MODELS = [
    'accounts.Company',
    'accounts.User',
    'commerce.Order',
    'accounting.Invoice',
    'accounting.Payment',
]
```

---

### 5.2 URLs

#### [MODIFY] `config/urls.py`

```python
path('api/v1/', include([
    # ... existing ...
    path('compliance/', include('apps.compliance.urls')),
    path('payments/', include('apps.payments.urls')),
    path('integrations/', include('apps.integrations.urls')),
    path('invoicenow/', include('apps.invoicenow.urls')),
])),
```

---

### 5.3 Dependencies

#### [MODIFY] `pyproject.toml`

```toml
[project.dependencies]
stripe = "^10.0"      # Stripe API
signxml = "^3.0"      # XMLDSig
lxml = "^5.0"         # XML parsing
httpx = "^0.27"       # Async HTTP
```

---

## 6. Verification Plan

### 6.1 Automated Tests

**Test Command**:
```bash
cd backend
uv run python -m pytest apps/compliance/tests/ apps/payments/tests/ apps/integrations/tests/ apps/invoicenow/tests/ -v
```

**Test Counts by File**:

| App | File | Est. Tests |
|-----|------|------------|
| compliance | test_models.py | 12 |
| compliance | test_pdpa_service.py | 10 |
| compliance | test_audit_service.py | 6 |
| compliance | test_gst_return_service.py | 6 |
| compliance | test_views.py | 8 |
| payments | test_gateways.py | 10 |
| payments | test_orchestrator.py | 6 |
| payments | test_webhooks.py | 4 |
| integrations | test_ninjavan.py | 4 |
| integrations | test_singpost.py | 3 |
| invoicenow | test_ubl_generator.py | 8 |
| invoicenow | test_peppol_service.py | 6 |
| invoicenow | test_views.py | 4 |
| **Total** | | **~87** |

**Factory Pattern** (following `apps.accounting.tests.factories`):
```python
class GSTReturnFactory(DjangoModelFactory):
    class Meta:
        model = GSTReturn
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    quarter = 1
    year = 2024
    # ... etc
```

---

### 6.2 Integration Tests (Sandbox)

> [!NOTE]
> Requires sandbox API keys in `.env`

```bash
# Run integration tests with marker
uv run python -m pytest -m "integration" -v
```

**Scenarios**:
1. Stripe: Create intent → mock webhook → verify payment recorded
2. HitPay: Create request → mock callback
3. UBL: Generate XML → validate against PEPPOL schema

---

### 6.3 Manual Verification

**For User to Verify**:

1. **GST Return Flow**:
   - Create via admin or API
   - Run prepare_return() and check boxes
   - Validate and submit (mock IRAS)

2. **PDPA Consent**:
   - Record consent via API
   - Verify Customer.consent_* updated
   - Check DataConsent audit record created

3. **PEPPOL UBL**:
   - Generate UBL for existing invoice
   - Download XML and manually inspect structure
   - Validate against online PEPPOL validator

---

## 7. Implementation Order

| Week | Day | Task | Deliverables |
|------|-----|------|--------------|
| 13 | 1-2 | Compliance models | 4 models, migrations |
| 13 | 3-4 | Compliance services | PDPA, Audit, GST services |
| 13 | 5 | Compliance views/tests | ViewSets, 35+ tests |
| 14 | 1-2 | Payments gateways | Base, Stripe, HitPay |
| 14 | 3-4 | Payments orchestrator | Service, webhooks |
| 14 | 5 | Payments tests | 20+ tests |
| 15 | 1-2 | InvoiceNow models | PEPPOLInvoice, Acknowledgment |
| 15 | 3-4 | InvoiceNow UBL/services | Generator, PEPPOLService |
| 15 | 5 | Integration tests | E2E flows, 15+ tests |

---

## 8. Success Criteria

- [ ] 85+ tests passing for Phase 5
- [ ] GST F5 box calculations match manual verification
- [ ] Consent recording updates both Customer and DataConsent
- [ ] Audit logs capture configured model changes
- [ ] Stripe payment intent creates successfully (sandbox)
- [ ] UBL XML validates against PEPPOL BIS 3.0 schema
- [ ] All 4 apps registered and accessible via API

---

## 9. Open Questions for User

1. **PEPPOL Access Point**: Which provider to integrate? (peppol.sg, invoicenow.sg, other)
2. **Audit Retention**: Keep forever or implement purging (e.g., 7 years)?
3. **Payment Priority**: Which gateway as primary? (Stripe vs HitPay)
4. **Logistics Priority**: NinjaVan first or both simultaneously?

---

**Document Status**: ✅ Validated against codebase  
**Awaiting**: User approval to proceed to EXECUTION
