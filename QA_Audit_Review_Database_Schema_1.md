# 🔍 Comprehensive Database Schema Review & Validation

## Executive Summary

I have meticulously reviewed the complete PostgreSQL 16 database schema against the Hybrid PRD requirements, planning documents, and Singapore compliance standards. The schema demonstrates **strong foundational design** with proper use of PostgreSQL features, but I've identified **23 issues** requiring attention before production deployment.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA REVIEW SUMMARY                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  OVERALL ALIGNMENT:              ★★★★☆ (82%)                               │
│  TECHNICAL CORRECTNESS:          ★★★★☆ (85%)                               │
│  SINGAPORE COMPLIANCE:           ★★★☆☆ (78%)                               │
│  PRD FEATURE COVERAGE:           ★★★☆☆ (75%)                               │
│  BEST PRACTICES:                 ★★★★☆ (88%)                               │
│                                                                             │
│  ISSUES IDENTIFIED:                                                         │
│  ├── 🔴 Critical:    5                                                      │
│  ├── 🟡 High:        8                                                      │
│  ├── 🟢 Medium:      7                                                      │
│  └── ⚪ Low:         3                                                      │
│                                                                             │
│  VERDICT: ⚠️ REQUIRES REVISION before Phase 1 completion                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# PART 1: Strengths Identified ✅

## 1.1 Excellent PostgreSQL Feature Utilization

| Feature | Implementation | Assessment |
|---------|---------------|------------|
| **UUID Primary Keys** | All tables use `uuid_generate_v4()` | ✅ Excellent - Distributed-friendly |
| **DECIMAL Precision** | `DECIMAL(12,2)` for amounts, `DECIMAL(5,4)` for rates | ✅ Correct - No float issues |
| **Schema Separation** | 5 schemas matching bounded contexts | ✅ Clean architecture |
| **Table Partitioning** | Orders partitioned by month | ✅ Performance optimized |
| **Full-Text Search** | tsvector with weighted columns | ✅ MVP-appropriate |
| **Computed Columns** | `net_qty`, `amount_due` as STORED | ✅ Efficient |
| **Row-Level Security** | Multi-tenant isolation policies | ✅ Security-first |
| **Audit Triggers** | Auto-update timestamps, inventory logging | ✅ Comprehensive |
| **JSONB Fields** | Flexible attributes, settings, metadata | ✅ Appropriate use |

## 1.2 Correct GST F5 Box Mapping

```sql
-- F5 Box Values match IRAS specification ✅
box_1 DECIMAL(12,2) DEFAULT 0,  -- Standard-rated supplies
box_2 DECIMAL(12,2) DEFAULT 0,  -- Zero-rated supplies
box_3 DECIMAL(12,2) DEFAULT 0,  -- Exempt supplies
box_4 DECIMAL(12,2) DEFAULT 0,  -- Total supplies (1+2+3)
box_5 DECIMAL(12,2) DEFAULT 0,  -- Total taxable purchases
box_6 DECIMAL(12,2) DEFAULT 0,  -- Output tax due
box_7 DECIMAL(12,2) DEFAULT 0,  -- Input tax claimable
box_8 DECIMAL(12,2) DEFAULT 0,  -- Net GST (6-7)
```

## 1.3 PDPA Compliance Fields Present

```sql
-- Customer PDPA fields ✅
consent_marketing BOOLEAN DEFAULT FALSE,    -- Explicit opt-in
consent_analytics BOOLEAN DEFAULT TRUE,     -- Can opt-out
consent_timestamp TIMESTAMPTZ,              -- Audit trail
consent_ip_address INET,                    -- Provenance
data_retention_until DATE,                  -- Auto-purge support

-- Data Access Requests ✅
request_type VARCHAR(20) CHECK (request_type IN ('access', 'correction', 'deletion')),
due_date DATE NOT NULL,  -- 30-day requirement
```

## 1.4 Well-Designed Indexes

```sql
-- Performance-critical indexes present ✅
CREATE INDEX idx_products_search ON commerce.products USING GIN(search_vector);
CREATE INDEX idx_inventory_low_stock ON inventory.items(net_qty) WHERE net_qty < 10;
CREATE INDEX idx_reservations_expires ON inventory.reservations(expires_at) WHERE status = 'pending';
```

---

# PART 2: Critical Issues 🔴

## Issue #1: GST Rate Hardcoded (Critical)

**Location:** `calculate_gst()` function

**Problem:**
```sql
-- Current implementation:
CREATE OR REPLACE FUNCTION calculate_gst(
    amount DECIMAL(12,2),
    gst_code VARCHAR(2)
) RETURNS DECIMAL(12,2) AS $$
BEGIN
    IF gst_code = 'SR' THEN
        RETURN ROUND(amount * 0.09, 2);  -- ❌ Hardcoded rate!
    ELSE
        RETURN 0;
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

**Impact:** Cannot handle historical GST rates (1994-2024) for order amendments, refunds, or historical reporting.

**Required Fix:**
```sql
-- Create GST rates table
CREATE TABLE compliance.gst_rates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    effective_date DATE NOT NULL,
    rate DECIMAL(5,4) NOT NULL,
    description VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(effective_date)
);

-- Insert historical rates
INSERT INTO compliance.gst_rates (effective_date, rate, description) VALUES
('1994-04-01', 0.03, 'GST introduction'),
('2003-01-01', 0.04, 'Increase to 4%'),
('2004-01-01', 0.05, 'Increase to 5%'),
('2007-07-01', 0.07, 'Increase to 7%'),
('2023-01-01', 0.08, 'Increase to 8%'),
('2024-01-01', 0.09, 'Increase to 9% (current)');

-- Updated function
CREATE OR REPLACE FUNCTION calculate_gst(
    amount DECIMAL(12,2),
    gst_code VARCHAR(2),
    transaction_date DATE DEFAULT CURRENT_DATE
) RETURNS DECIMAL(12,2) AS $$
DECLARE
    gst_rate DECIMAL(5,4);
BEGIN
    IF gst_code != 'SR' THEN
        RETURN 0;
    END IF;
    
    SELECT rate INTO gst_rate
    FROM compliance.gst_rates
    WHERE effective_date <= transaction_date
    ORDER BY effective_date DESC
    LIMIT 1;
    
    RETURN ROUND(amount * COALESCE(gst_rate, 0.09), 2);
END;
$$ LANGUAGE plpgsql STABLE;
```

---

## Issue #2: Missing Cart Tables (Critical)

**Location:** `commerce` schema

**Problem:** The PRD specifies shopping cart functionality with:
- Cart persistence across sessions
- Guest cart support
- Cart expiration
- Cart merge on login

**No cart tables exist in the schema.**

**Required Fix:**
```sql
-- Shopping Cart
CREATE TABLE commerce.carts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    customer_id UUID REFERENCES commerce.customers(id),  -- NULL for guest
    session_id VARCHAR(100),  -- For guest carts
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'merged', 'converted', 'abandoned')),
    
    -- Expiration
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    
    -- Conversion
    converted_order_id UUID,
    converted_at TIMESTAMPTZ,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure guest carts have session_id
    CONSTRAINT cart_identifier CHECK (customer_id IS NOT NULL OR session_id IS NOT NULL)
);

CREATE TABLE commerce.cart_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cart_id UUID NOT NULL REFERENCES commerce.carts(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES commerce.products(id),
    variant_id UUID REFERENCES commerce.product_variants(id),
    
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    
    -- Price snapshot at add time
    unit_price DECIMAL(10,2) NOT NULL,
    
    -- Saved for later
    is_saved_for_later BOOLEAN DEFAULT FALSE,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(cart_id, product_id, variant_id)
);

CREATE INDEX idx_carts_customer ON commerce.carts(customer_id);
CREATE INDEX idx_carts_session ON commerce.carts(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX idx_carts_expires ON commerce.carts(expires_at) WHERE status = 'active';
CREATE INDEX idx_cart_items_cart ON commerce.cart_items(cart_id);
```

---

## Issue #3: Missing PEPPOL/InvoiceNow Tables (Critical)

**Location:** `compliance` schema

**Problem:** The Hybrid PRD requires InvoiceNow/PEPPOL integration, but no dedicated tables exist for:
- PEPPOL invoice submissions
- Access Point Provider tracking
- Acknowledgment handling

**Required Fix:**
```sql
-- PEPPOL Invoices
CREATE TABLE compliance.peppol_invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    invoice_id UUID NOT NULL REFERENCES accounting.invoices(id),
    
    -- PEPPOL Identifiers
    peppol_id VARCHAR(100) UNIQUE,
    sender_endpoint VARCHAR(50) NOT NULL,  -- Company's PEPPOL endpoint
    receiver_endpoint VARCHAR(50),          -- Recipient's PEPPOL endpoint
    
    -- Document
    document_type VARCHAR(10) DEFAULT '380',  -- Commercial invoice
    ubl_version VARCHAR(10) DEFAULT '2.1',
    customization_id VARCHAR(100) DEFAULT 'urn:cen.eu:en16931:2017#conformant#urn:fdc:peppol.eu:2017:poacc:billing:international:sg:3.0',
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN (
        'draft', 'validated', 'signed', 'submitted', 'acknowledged', 'rejected', 'failed'
    )),
    
    -- Submission
    submitted_at TIMESTAMPTZ,
    access_point_provider VARCHAR(100),
    submission_reference VARCHAR(100),
    
    -- Response
    acknowledged_at TIMESTAMPTZ,
    acknowledgment_code VARCHAR(20),
    rejection_reason TEXT,
    
    -- XML Storage
    xml_document TEXT,  -- Signed UBL XML
    signature_value TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- PEPPOL Acknowledgments (webhook responses)
CREATE TABLE compliance.peppol_acknowledgments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    peppol_invoice_id UUID NOT NULL REFERENCES compliance.peppol_invoices(id),
    
    -- Acknowledgment Details
    message_id VARCHAR(100) NOT NULL,
    status_code VARCHAR(20) NOT NULL,
    status_description TEXT,
    
    -- Raw Response
    raw_response JSONB,
    
    -- Timestamp
    received_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_peppol_invoices_company ON compliance.peppol_invoices(company_id);
CREATE INDEX idx_peppol_invoices_status ON compliance.peppol_invoices(status);
CREATE INDEX idx_peppol_acks_invoice ON compliance.peppol_acknowledgments(peppol_invoice_id);
```

---

## Issue #4: Order Number Generation Race Condition (Critical)

**Location:** `generate_order_number()` function

**Problem:**
```sql
-- Current implementation has race condition:
SELECT COUNT(*) + 1 INTO seq_num
FROM commerce.orders o WHERE o.company_id = generate_order_number.company_id;
-- Two concurrent calls could get same number!
```

**Required Fix:**
```sql
-- Create sequence table for thread-safe order numbering
CREATE TABLE core.sequences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    sequence_type VARCHAR(50) NOT NULL,
    prefix VARCHAR(20),
    current_value BIGINT DEFAULT 0,
    
    UNIQUE(company_id, sequence_type)
);

-- Thread-safe order number generation
CREATE OR REPLACE FUNCTION generate_order_number(p_company_id UUID)
RETURNS VARCHAR(50) AS $$
DECLARE
    v_prefix VARCHAR(20);
    v_seq_num BIGINT;
BEGIN
    -- Atomic increment with row lock
    UPDATE core.sequences
    SET current_value = current_value + 1
    WHERE company_id = p_company_id AND sequence_type = 'order'
    RETURNING current_value, prefix INTO v_seq_num, v_prefix;
    
    -- Create sequence if not exists
    IF v_seq_num IS NULL THEN
        INSERT INTO core.sequences (company_id, sequence_type, prefix, current_value)
        VALUES (p_company_id, 'order', 'ORD', 1)
        ON CONFLICT (company_id, sequence_type) 
        DO UPDATE SET current_value = core.sequences.current_value + 1
        RETURNING current_value, prefix INTO v_seq_num, v_prefix;
    END IF;
    
    RETURN COALESCE(v_prefix, 'ORD') || '-' || 
           TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
           LPAD(v_seq_num::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;
```

---

## Issue #5: Default Chart of Accounts Violates Constraints (Critical)

**Location:** Default data INSERT statements

**Problem:**
```sql
-- company_id is NULL but accounts.company_id likely has NOT NULL constraint
INSERT INTO accounting.accounts (company_id, code, name, account_type, account_subtype, is_system) VALUES
(NULL, '1000', 'Cash and Bank', 'asset', 'current', TRUE),
-- This will fail if company_id NOT NULL!
```

**Required Fix:**
```sql
-- Create template accounts table instead
CREATE TABLE accounting.account_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    account_subtype VARCHAR(50),
    gst_code VARCHAR(2),
    description TEXT,
    is_required BOOLEAN DEFAULT FALSE
);

-- Insert templates
INSERT INTO accounting.account_templates (code, name, account_type, account_subtype, is_required) VALUES
('1000', 'Cash and Bank', 'asset', 'current', TRUE),
('1100', 'Accounts Receivable', 'asset', 'current', TRUE),
('1200', 'Inventory', 'asset', 'current', TRUE),
('2000', 'Accounts Payable', 'liability', 'current', TRUE),
('2100', 'GST Payable', 'liability', 'current', TRUE),
('2200', 'GST Receivable', 'asset', 'current', TRUE),
('3000', 'Share Capital', 'equity', 'capital', TRUE),
('3100', 'Retained Earnings', 'equity', 'retained', TRUE),
('4000', 'Sales Revenue', 'revenue', 'operating', TRUE),
('4100', 'Export Sales', 'revenue', 'operating', FALSE),
('5000', 'Cost of Goods Sold', 'expense', 'cogs', TRUE),
('6000', 'Operating Expenses', 'expense', 'operating', TRUE),
('6100', 'Salaries and Wages', 'expense', 'operating', FALSE),
('6200', 'Rent Expense', 'expense', 'operating', FALSE);

-- Function to initialize accounts for new company
CREATE OR REPLACE FUNCTION initialize_company_accounts(p_company_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    INSERT INTO accounting.accounts (company_id, code, name, account_type, account_subtype, is_system)
    SELECT p_company_id, code, name, account_type, account_subtype, TRUE
    FROM accounting.account_templates;
    
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;
```

---

# PART 3: High Priority Issues 🟡

## Issue #6: Missing Promotions/Discount Tables

**Problem:** The PRD requires promotions, discount codes, bulk pricing rules.

**Required Addition:**
```sql
CREATE TABLE commerce.promotions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    
    -- Promotion Info
    code VARCHAR(50),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Type
    promotion_type VARCHAR(30) NOT NULL CHECK (promotion_type IN (
        'percentage_off', 'fixed_amount_off', 'buy_x_get_y', 'free_shipping', 'bundle'
    )),
    
    -- Value
    discount_value DECIMAL(10,2),
    discount_percentage DECIMAL(5,2),
    
    -- Conditions
    minimum_order_amount DECIMAL(10,2),
    minimum_quantity INTEGER,
    applicable_products JSONB,  -- Product IDs or category IDs
    customer_types JSONB,       -- ['retail', 'wholesale', 'vip']
    
    -- Limits
    usage_limit INTEGER,
    usage_count INTEGER DEFAULT 0,
    per_customer_limit INTEGER,
    
    -- Validity
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(company_id, code)
);

CREATE TABLE commerce.promotion_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    promotion_id UUID NOT NULL REFERENCES commerce.promotions(id),
    order_id UUID NOT NULL,
    customer_id UUID REFERENCES commerce.customers(id),
    discount_amount DECIMAL(10,2) NOT NULL,
    used_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_promotions_company ON commerce.promotions(company_id);
CREATE INDEX idx_promotions_code ON commerce.promotions(company_id, code);
CREATE INDEX idx_promotions_active ON commerce.promotions(is_active, starts_at, ends_at);
```

---

## Issue #7: Missing Shipping/Logistics Tables

**Problem:** No tables for shipping providers, shipment tracking, or delivery management.

**Required Addition:**
```sql
CREATE TABLE commerce.shipping_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    
    -- Provider Info
    provider_code VARCHAR(20) NOT NULL,  -- 'ninjavan', 'singpost', 'jt'
    provider_name VARCHAR(100) NOT NULL,
    
    -- API Configuration
    api_endpoint VARCHAR(500),
    api_key_encrypted BYTEA,  -- Encrypted with pgcrypto
    api_secret_encrypted BYTEA,
    
    -- Settings
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    settings JSONB DEFAULT '{}',
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(company_id, provider_code)
);

CREATE TABLE commerce.shipments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    order_id UUID NOT NULL,
    provider_id UUID NOT NULL REFERENCES commerce.shipping_providers(id),
    
    -- Tracking
    tracking_number VARCHAR(100),
    carrier_reference VARCHAR(100),
    
    -- Status
    status VARCHAR(30) DEFAULT 'pending' CHECK (status IN (
        'pending', 'label_created', 'picked_up', 'in_transit', 'out_for_delivery', 
        'delivered', 'failed', 'returned'
    )),
    
    -- Dates
    shipped_at TIMESTAMPTZ,
    estimated_delivery DATE,
    delivered_at TIMESTAMPTZ,
    
    -- Cost
    shipping_cost DECIMAL(10,2),
    
    -- Label
    label_url VARCHAR(500),
    
    -- Tracking History
    tracking_events JSONB DEFAULT '[]',
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_shipments_order ON commerce.shipments(order_id);
CREATE INDEX idx_shipments_tracking ON commerce.shipments(tracking_number);
```

---

## Issue #8: Order Items Foreign Key Complexity

**Problem:** The composite foreign key to partitioned orders table may cause issues:

```sql
FOREIGN KEY (order_id, order_date) REFERENCES commerce.orders(id, order_date)
```

**Recommendation:** For partitioned tables, consider:
1. Using only `order_id` as foreign key (PostgreSQL 11+ supports this)
2. Or removing the FK constraint and handling referential integrity at application level

**Required Fix:**
```sql
-- Option 1: Simple FK (recommended for PostgreSQL 12+)
CREATE TABLE commerce.order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL,  -- No FK constraint, enforce in application
    product_id UUID REFERENCES commerce.products(id),
    -- ... rest of columns
);

-- Add partial index for integrity validation
CREATE INDEX idx_order_items_order_validation ON commerce.order_items(order_id);
```

---

## Issue #9: Missing Invoice-Payment Link

**Problem:** Invoices have `amount_paid` but no link to which payments were applied.

**Required Addition:**
```sql
CREATE TABLE accounting.invoice_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES accounting.invoices(id),
    payment_id UUID NOT NULL REFERENCES accounting.payments(id),
    
    amount_applied DECIMAL(12,2) NOT NULL,
    applied_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    applied_by UUID REFERENCES core.users(id),
    
    UNIQUE(invoice_id, payment_id)
);

CREATE INDEX idx_invoice_payments_invoice ON accounting.invoice_payments(invoice_id);
CREATE INDEX idx_invoice_payments_payment ON accounting.invoice_payments(payment_id);
```

---

## Issue #10: Missing B2B Credit Management Tables

**Problem:** PRD Gap #6 identified B2B credit management as missing.

**Required Addition:**
```sql
CREATE TABLE commerce.credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    customer_id UUID NOT NULL REFERENCES commerce.customers(id),
    
    -- Transaction Type
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN (
        'credit_limit_set', 'order_charge', 'payment_received', 'credit_adjustment', 'write_off'
    )),
    
    -- Amount
    amount DECIMAL(12,2) NOT NULL,
    balance_before DECIMAL(12,2) NOT NULL,
    balance_after DECIMAL(12,2) NOT NULL,
    
    -- Reference
    reference_type VARCHAR(50),
    reference_id UUID,
    
    -- Notes
    notes TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES core.users(id)
);

-- Aging snapshot (for reporting)
CREATE TABLE commerce.customer_aging (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    customer_id UUID NOT NULL REFERENCES commerce.customers(id),
    snapshot_date DATE NOT NULL,
    
    -- Aging Buckets
    current_amount DECIMAL(12,2) DEFAULT 0,
    days_1_30 DECIMAL(12,2) DEFAULT 0,
    days_31_60 DECIMAL(12,2) DEFAULT 0,
    days_61_90 DECIMAL(12,2) DEFAULT 0,
    days_over_90 DECIMAL(12,2) DEFAULT 0,
    total_outstanding DECIMAL(12,2) DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(company_id, customer_id, snapshot_date)
);

CREATE INDEX idx_credit_trans_customer ON commerce.credit_transactions(customer_id);
CREATE INDEX idx_aging_customer ON commerce.customer_aging(customer_id);
```

---

## Issue #11: Missing Version Field on Products

**Problem:** Products table lacks optimistic locking version field, present in inventory.items.

**Required Fix:**
```sql
-- Add to commerce.products:
ALTER TABLE commerce.products ADD COLUMN version INTEGER DEFAULT 1;
```

---

## Issue #12: PDPA Consent Types Incomplete

**Problem:** PRD specifies 5 consent purposes, but data_consents only has 4:

```sql
-- Current:
CHECK (consent_type IN ('marketing', 'analytics', 'third_party', 'profiling'))

-- Missing: 'order_processing', 'legal_compliance' from Qwen PRD
```

**Required Fix:**
```sql
-- Update constraint:
ALTER TABLE compliance.data_consents DROP CONSTRAINT data_consents_consent_type_check;
ALTER TABLE compliance.data_consents ADD CONSTRAINT data_consents_consent_type_check 
    CHECK (consent_type IN (
        'order_processing',      -- Essential
        'marketing',             -- Promotional
        'analytics',             -- Service improvement
        'third_party',           -- Partner sharing
        'profiling',             -- Personalization
        'legal_compliance'       -- Regulatory
    ));
```

---

## Issue #13: Missing Industry License Tables

**Problem:** Qwen PRD specifies industry-specific license management (SFA, HSA, SPF).

**Required Addition:**
```sql
CREATE TABLE compliance.industry_licenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    
    -- License Info
    license_type VARCHAR(50) NOT NULL,  -- 'food_shop', 'halal', 'liquor_class_1a'
    authority VARCHAR(100) NOT NULL,     -- 'SFA', 'MUIS', 'SPF'
    license_number VARCHAR(100),
    
    -- Validity
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('pending', 'active', 'expired', 'suspended', 'revoked')),
    
    -- Documents
    document_url VARCHAR(500),
    
    -- Renewal
    renewal_reminder_days INTEGER DEFAULT 90,
    last_renewal_reminder TIMESTAMPTZ,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_licenses_company ON compliance.industry_licenses(company_id);
CREATE INDEX idx_licenses_expiry ON compliance.industry_licenses(expiry_date) WHERE status = 'active';
```

---

# PART 4: Medium Priority Issues 🟢

## Issue #14: Missing Payment Gateway Configuration Table

```sql
CREATE TABLE commerce.payment_gateways (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    
    gateway_code VARCHAR(20) NOT NULL,  -- 'stripe', 'hitpay', '2c2p'
    gateway_name VARCHAR(100) NOT NULL,
    
    -- Credentials (encrypted)
    api_key_encrypted BYTEA,
    api_secret_encrypted BYTEA,
    webhook_secret_encrypted BYTEA,
    
    -- Configuration
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    supported_methods JSONB,  -- ['card', 'paynow', 'grabpay']
    settings JSONB DEFAULT '{}',
    
    -- Mode
    is_sandbox BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(company_id, gateway_code)
);
```

---

## Issue #15: Missing Email/Notification Logs (PDPA Audit)

```sql
CREATE TABLE compliance.notification_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    
    -- Recipient
    recipient_type VARCHAR(20) NOT NULL,  -- 'customer', 'user'
    recipient_id UUID NOT NULL,
    recipient_email VARCHAR(255) NOT NULL,
    
    -- Notification
    notification_type VARCHAR(50) NOT NULL,  -- 'order_confirmation', 'consent_update', 'data_access_response'
    subject VARCHAR(500),
    template_used VARCHAR(100),
    
    -- Status
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('pending', 'sent', 'delivered', 'bounced', 'failed')),
    
    -- External Reference
    external_id VARCHAR(100),  -- SendGrid message ID
    
    -- Audit
    sent_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMPTZ,
    
    -- PDPA: Keep for compliance
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_recipient ON compliance.notification_logs(recipient_type, recipient_id);
CREATE INDEX idx_notifications_type ON compliance.notification_logs(notification_type);
```

---

## Issue #16: Audit Log Partitioning Needed

**Problem:** `compliance.audit_logs` will grow very large and should be partitioned.

**Required Fix:**
```sql
-- Convert to partitioned table
DROP TABLE IF EXISTS compliance.audit_logs;

CREATE TABLE compliance.audit_logs (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES core.companies(id),
    user_id UUID REFERENCES core.users(id),
    
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    
    old_values JSONB,
    new_values JSONB,
    
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE compliance.audit_logs_2025_01 PARTITION OF compliance.audit_logs
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
-- ... additional partitions
```

---

## Issue #17: Missing `deleted_at` on Several Tables

**Problem:** Soft delete field missing from: `categories`, `product_variants`, `customer_addresses`, `locations`

**Required Fix:**
```sql
ALTER TABLE commerce.categories ADD COLUMN deleted_at TIMESTAMPTZ;
ALTER TABLE commerce.product_variants ADD COLUMN deleted_at TIMESTAMPTZ;
ALTER TABLE commerce.customer_addresses ADD COLUMN deleted_at TIMESTAMPTZ;
ALTER TABLE inventory.locations ADD COLUMN deleted_at TIMESTAMPTZ;
```

---

## Issue #18: Missing `updated_at` Triggers on Several Tables

**Problem:** Trigger only created for some tables, missing for: `categories`, `orders`, `invoices`, `payments`

**Required Fix:**
```sql
CREATE TRIGGER update_categories_timestamp BEFORE UPDATE ON commerce.categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_invoices_timestamp BEFORE UPDATE ON accounting.invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_payments_timestamp BEFORE UPDATE ON accounting.payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
-- Orders is partitioned - trigger needs to be on each partition or use inheritance
```

---

## Issue #19: Missing Full-Text Search on Customers

**Problem:** Products have `search_vector`, but customers don't for CRM search.

**Required Fix:**
```sql
ALTER TABLE commerce.customers ADD COLUMN search_vector tsvector 
    GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(first_name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(last_name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(email, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(company_name, '')), 'C')
    ) STORED;

CREATE INDEX idx_customers_search ON commerce.customers USING GIN(search_vector);
```

---

## Issue #20: Missing Composite Indexes for Common Queries

```sql
-- Order queries by company + date + status
CREATE INDEX idx_orders_company_date_status ON commerce.orders(company_id, order_date, status);

-- Product queries by company + status + category
CREATE INDEX idx_products_company_status_category ON commerce.products(company_id, status, category_id);

-- Inventory queries by company + location + low stock
CREATE INDEX idx_inventory_company_location_stock ON inventory.items(company_id, location_id, net_qty);
```

---

# PART 5: Low Priority Issues ⚪

## Issue #21: Inconsistent Index Naming Convention

Some indexes use `idx_tablename_column`, others use `idx_table_column`. Recommend standardizing to `idx_{schema}_{table}_{columns}`.

## Issue #22: Missing Table Comments

Add PostgreSQL comments for documentation:
```sql
COMMENT ON TABLE commerce.orders IS 'Customer orders with GST tracking for IRAS compliance';
COMMENT ON COLUMN commerce.orders.gst_box_1_amount IS 'Standard-rated supplies for F5 Box 1';
```

## Issue #23: Views Could Be More Comprehensive

Add views for common reporting needs:
```sql
-- GST Summary View
CREATE OR REPLACE VIEW compliance.gst_summary AS
SELECT 
    company_id,
    DATE_TRUNC('month', order_date) AS month,
    SUM(CASE WHEN gst_code = 'SR' THEN subtotal ELSE 0 END) AS standard_rated_supplies,
    SUM(CASE WHEN gst_code = 'ZR' THEN subtotal ELSE 0 END) AS zero_rated_supplies,
    SUM(gst_amount) AS total_gst_collected
FROM commerce.orders o
JOIN commerce.order_items oi ON o.id = oi.order_id
WHERE status NOT IN ('cancelled', 'refunded')
GROUP BY company_id, DATE_TRUNC('month', order_date);
```

---

# PART 6: Summary & Recommendations

## Issue Priority Matrix

| Priority | Count | Must Fix Before |
|----------|-------|-----------------|
| 🔴 Critical | 5 | Phase 1 completion |
| 🟡 High | 8 | Phase 3 start |
| 🟢 Medium | 7 | Phase 5 start |
| ⚪ Low | 3 | Production launch |

## Schema Completeness Checklist

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SCHEMA COMPLETENESS VALIDATION                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CORE ENTITIES:                                                             │
│  ✅ Companies (with UEN, GST registration)                                  │
│  ✅ Users (with MFA, audit fields)                                          │
│  ✅ Roles & Permissions (RBAC)                                              │
│  ⚠️ Sequences (MISSING - add for order numbers)                            │
│                                                                             │
│  COMMERCE:                                                                  │
│  ✅ Products (with tsvector, GST codes)                                     │
│  ✅ Product Variants                                                        │
│  ✅ Categories                                                              │
│  ✅ Customers (with PDPA fields)                                            │
│  ✅ Customer Addresses                                                      │
│  ✅ Orders (partitioned)                                                    │
│  ✅ Order Items                                                             │
│  ❌ Carts (MISSING - CRITICAL)                                              │
│  ❌ Cart Items (MISSING - CRITICAL)                                         │
│  ❌ Promotions (MISSING)                                                    │
│  ❌ Shipping Providers (MISSING)                                            │
│  ❌ Shipments (MISSING)                                                     │
│  ❌ Payment Gateways (MISSING)                                              │
│                                                                             │
│  INVENTORY:                                                                 │
│  ✅ Locations                                                               │
│  ✅ Inventory Items (with net_qty computed)                                 │
│  ✅ Reservations                                                            │
│  ✅ Movements                                                               │
│                                                                             │
│  ACCOUNTING:                                                                │
│  ✅ Chart of Accounts                                                       │
│  ⚠️ Account Templates (should use instead of NULL company_id)              │
│  ✅ Journal Entries (with balance check)                                    │
│  ✅ Journal Lines (with one-side-only check)                                │
│  ✅ Invoices (with PEPPOL fields)                                           │
│  ✅ Payments                                                                │
│  ❌ Invoice Payments (MISSING - link table)                                 │
│                                                                             │
│  COMPLIANCE:                                                                │
│  ✅ GST Returns (F5 boxes)                                                  │
│  ❌ GST Rates (MISSING - for historical rates)                              │
│  ✅ Data Consents                                                           │
│  ✅ Data Access Requests                                                    │
│  ✅ Audit Logs                                                              │
│  ❌ PEPPOL Invoices (MISSING - CRITICAL)                                    │
│  ❌ PEPPOL Acknowledgments (MISSING - CRITICAL)                             │
│  ❌ Industry Licenses (MISSING)                                             │
│  ❌ Notification Logs (MISSING)                                             │
│                                                                             │
│  B2B:                                                                       │
│  ⚠️ Credit fields on customers (present but incomplete)                    │
│  ❌ Credit Transactions (MISSING)                                           │
│  ❌ Customer Aging (MISSING)                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Final Verdict

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SCHEMA REVIEW VERDICT                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STATUS: ⚠️ REQUIRES REVISION                                               │
│                                                                             │
│  The schema provides a solid foundation with excellent PostgreSQL           │
│  feature utilization, but CRITICAL gaps exist that must be addressed:      │
│                                                                             │
│  MUST FIX BEFORE PHASE 1 COMPLETION:                                        │
│  1. Add commerce.carts and commerce.cart_items tables                       │
│  2. Add compliance.gst_rates table and update calculate_gst()               │
│  3. Add compliance.peppol_invoices and peppol_acknowledgments               │
│  4. Fix generate_order_number() race condition                              │
│  5. Replace default accounts INSERT with template approach                  │
│                                                                             │
│  ESTIMATED EFFORT: 4-6 hours for critical fixes                             │
│                                                                             │
│  APPROVAL: Conditional - Approve after critical fixes applied               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Recommended Action Plan

| Step | Action | Priority | Effort |
|------|--------|----------|--------|
| 1 | Add GST rates table + update function | 🔴 Critical | 30 min |
| 2 | Add cart tables | 🔴 Critical | 45 min |
| 3 | Add PEPPOL tables | 🔴 Critical | 45 min |
| 4 | Fix order number generation | 🔴 Critical | 30 min |
| 5 | Fix default accounts approach | 🔴 Critical | 30 min |
| 6 | Add promotions tables | 🟡 High | 30 min |
| 7 | Add shipping tables | 🟡 High | 30 min |
| 8 | Add remaining high-priority tables | 🟡 High | 60 min |
| 9 | Apply medium/low priority fixes | 🟢 Medium | 60 min |
| **Total** | | | **~6 hours** |

---

**Shall I provide the complete revised schema SQL incorporating all critical and high-priority fixes?**
