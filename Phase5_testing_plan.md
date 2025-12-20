# Phase 5: Testing & Configuration Plan

## User Preferences Applied

| Setting | Value |
|---------|-------|
| PEPPOL Access Point | Zetta Solution (zettapeppol.com) |
| Audit Log Retention | 7 years |
| Primary Payment Gateway | Stripe (HitPay as secondary) |

---

## Part 1: Code Updates Required

### 1.1 PEPPOL Access Point Configuration

#### [MODIFY] peppol_service.py

Update Access Point URL pattern to use Zetta Solution's InvoiceNow API.

```python
# Default AP configuration
ZETTA_AP_URL = 'https://zettapeppol.com/api/v1'
```

#### [NEW] services/zetta_client.py

Create dedicated Zetta Solution Access Point client with:
- Authentication handling
- Document submission
- Status polling
- Acknowledgment retrieval

---

### 1.2 Audit Log Retention Policy

#### [MODIFY] compliance/tasks.py

Update `enforce_data_retention` task to respect 7-year audit log retention:
- Add `AUDIT_LOG_RETENTION_YEARS = 7` setting
- Exclude audit logs from data anonymization
- Add separate audit log archival task

#### [MODIFY] config/settings/base.py

Add setting:
```python
# Audit log retention (years)
AUDIT_LOG_RETENTION_YEARS = 7
```

---

### 1.3 Payment Gateway Priority

#### [MODIFY] payment_orchestrator.py

Update gateway priority logic:
```python
# Gateway priority: Stripe first, HitPay fallback
DEFAULT_GATEWAY = 'stripe'
FALLBACK_GATEWAY = 'hitpay'
```

---

## Part 2: Test Execution Strategy

### 2.1 Unit Tests by App

| App | Test Files | Expected Tests |
|-----|-----------|----------------|
| Compliance | 5 files | 25+ tests |
| Payments | 3 files | 15+ tests |
| Integrations | 1 file | 8+ tests |
| InvoiceNow | 2 files | 10+ tests |
| **Total** | **11 files** | **58+ new tests** |

### 2.2 Test Categories

```
1. Model Tests
   - Field validation
   - Status transitions
   - Property calculations
   - Immutability constraints

2. Service Tests  
   - Business logic
   - Integration with models
   - Error handling
   - Edge cases

3. API Tests
   - Endpoint accessibility
   - Permission checks
   - Request/response validation
   - Action endpoints

4. Integration Tests
   - Cross-service workflows
   - Gateway interactions (mocked)
   - End-to-end submission flows
```

### 2.3 Mock Strategy

| Component | Mock Approach |
|-----------|---------------|
| Stripe API | Mock `stripe` module |
| HitPay API | Mock `httpx` responses |
| NinjaVan/SingPost | Mock `httpx` responses |
| PEPPOL AP | Mock Zetta client |
| GSTEngine | Mock service calls |

---

## Part 3: Verification Checklist

### 3.1 Migration Verification
- [ ] Create compliance schema
- [ ] Create GSTReturn table
- [ ] Create DataConsent table
- [ ] Create DataAccessRequest table
- [ ] Create AuditLog table
- [ ] Create PEPPOLInvoice table
- [ ] Create PEPPOLAcknowledgment table

### 3.2 Model Verification
- [ ] GSTReturn: F5 box calculations correct
- [ ] DataConsent: Immutability enforced
- [ ] DataAccessRequest: SLA tracking works
- [ ] AuditLog: Immutability enforced
- [ ] PEPPOLInvoice: Status transitions valid

### 3.3 Service Verification
- [ ] PDPAService: Consent records sync to Customer
- [ ] PDPAService: Data export includes all PII
- [ ] PDPAService: Anonymization preserves records
- [ ] AuditService: Signal-based logging works
- [ ] GSTReturnService: Box values calculate correctly
- [ ] PaymentOrchestrator: Gateway selection works
- [ ] ShippingService: Multi-carrier rates aggregate
- [ ] PEPPOLService: UBL generation valid
- [ ] PEPPOLService: Full workflow completes

### 3.4 API Verification
- [ ] All endpoints require authentication
- [ ] Company isolation enforced
- [ ] Action endpoints transition states
- [ ] Webhooks verify signatures

---

## Part 4: Implementation Steps

### Step 1: Apply Configuration Updates
1. Update `base.py` with retention setting
2. Update `payment_orchestrator.py` with gateway priority
3. Create Zetta AP client

### Step 2: Fix Any Import/Syntax Issues
1. Run `python manage.py check`
2. Fix any discovered issues

### Step 3: Run Migrations
```bash
cd backend
uv run python manage.py makemigrations --check
uv run python manage.py migrate
```

### Step 4: Execute Tests
```bash
# Run all tests
uv run pytest -v

# Run by app
uv run pytest apps/compliance/tests/ -v
uv run pytest apps/payments/tests/ -v
uv run pytest apps/integrations/tests/ -v
uv run pytest apps/invoicenow/tests/ -v
```

### Step 5: Validate Test Coverage
```bash
uv run pytest --cov=apps --cov-report=term-missing
```

---

## Part 5: Expected Outcomes

### Test Count Targets
| Phase | Tests |
|-------|-------|
| Phases 1-4 (existing) | 273 |
| Phase 5 (new) | 58+ |
| **Total Expected** | **331+** |

### Success Criteria
1. ✅ All migrations apply cleanly
2. ✅ All 331+ tests pass
3. ✅ No import errors
4. ✅ Admin pages load
5. ✅ API docs generate (drf-spectacular)
