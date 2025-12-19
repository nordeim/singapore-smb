# Project Deep Understanding (Reference)

## Singapore SMB E-Commerce & Integrated Business Platform

**Scope**: Unified platform for Singapore SMBs:

- E-commerce storefront (Next.js 14 PWA)
- Real-time multi-location inventory
- Automated accounting with GST compliance (IRAS-ready)
- Compliance layer including PDPA + audit trail
- Integrations: payments, logistics, marketplaces, and future InvoiceNow/PEPPOL

**Docs reviewed**:

- `AGENT.md`
- `PROJECT_UNDERSTANDING.md`
- `Project Architecture Document.md` (PAD v2.x)
- `master_execution_plan.md`
- `database/schema.sql`

---

## Update Log

- **2025-12-19**: Synced this deep understanding reference with latest QA-audit-driven schema/design updates.
  - **GST**: Added historical GST rates table (`compliance.gst_rates`) and updated `calculate_gst(amount, gst_code, transaction_date)` to use historical lookup.
  - **Orders**: Replaced race-prone order numbering with concurrency-safe per-company sequences (`core.sequences`) used by `generate_order_number(company_id)`.
  - **Commerce**: Added cart persistence tables (`commerce.carts`, `commerce.cart_items`).
  - **Compliance / InvoiceNow readiness**: Added PEPPOL operational tables (`compliance.peppol_invoices`, `compliance.peppol_acknowledgments`).
  - **Accounting**: Replaced invalid default CoA seed with templates + initializer (`accounting.account_templates`, `initialize_company_accounts(company_id)`).
  - **PDPA**: Clarified consent model as a dedicated table (`compliance.data_consents`) with 6 consent types.
  - **Multi-tenancy**: Expanded RLS coverage and policies for newly added tables.

---

## 1) WHAT we are building

### 1.1 Product pillars

- **Commerce**
  - Product catalog (categories, products, variants)
  - Customers (B2C + B2B fields)
  - Carts + checkout
  - Orders with state machine and full lifecycle
- **Inventory**
  - Locations (warehouse/store/virtual)
  - Stock levels with reservations and movements
  - Concurrency-safe updates
- **Accounting**
  - Chart of accounts (Singapore-friendly)
  - Double-entry journal entries with balanced constraints
  - Invoices + payments
  - GST engine + F5 return preparation
- **Compliance**
  - PDPA consent tracking, data access requests
  - Audit logging of state changes
- **Integrations**
  - Payments: Stripe (primary), HitPay (PayNow etc.), 2C2P fallback
  - Logistics: Ninja Van, J&T, SingPost
  - Marketplaces: Shopee/Lazada real-time, Qoo10 batch
  - Future: InvoiceNow/PEPPOL BIS Billing 3.0 via Access Point Providers

### 1.2 Target users and typical roles

- SMB owners and staff (10–50 employees)
- Roles (RBAC): owner, admin, finance, warehouse, sales, customer

---

## 2) WHY this architecture

### 2.1 Business drivers

- Reduce tool fragmentation (replace 5–7 tools)
- Eliminate GST errors (target: 100% compliance, zero-error F5)
- Improve inventory accuracy (target: ~99.5%)
- Increase mobile checkout conversion (PWA, PayNow)

### 2.2 Architectural philosophy (PAD “re-imagined”)

- **Modular monolith MVP** → service extraction later
- **PostgreSQL-first** (JSONB + tsvector) to reduce infra complexity
- **Redis** as cache + distributed locks + Celery broker
- **Event-driven where needed** (Celery/tasks/webhooks/signals) without premature microservices

---

## 3) HOW the system is designed

## 3.1 Tech stack

- **Backend**: Django 6.0+ + DRF, Celery, Django Tasks
- **Frontend**: Next.js 14.2+ (App Router), React 18, TypeScript
- **DB**: PostgreSQL 16+
- **Cache/Queue/Locks**: Redis 7.4+
- **Infra (target)**: AWS ECS Fargate (SG region), CloudFront, S3; Nginx + WAF (MVP edge)

---

## 4) Key architectural patterns & rules of engagement

### 4.1 Patterns

- **Service Layer**: business logic lives in services; views are thin orchestration
- **Repository-ish separation**: keep data access isolated where it clarifies logic
- **Domain events**: signals/tasks/celery for async and integration workflows
- **Light CQRS**: read-optimized views/materializations for reporting and performance
- **Distributed locking**: Redis locks around inventory-critical sections

### 4.2 Non-negotiable invariants

- **Financial precision**:
  - Never use floats for money
  - Monetary fields use DECIMAL/`Decimal` (`DECIMAL(12,2)` typical)
- **GST correctness**:
  - Codes: SR (standard rated), ZR (zero rated), ES (exempt), OS (out of scope)
  - Current rate: 9% from 2024-01-01
  - Historical lookup required for backdated transactions (rates stored in `compliance.gst_rates`; `calculate_gst(amount, gst_code, transaction_date)` uses effective-date lookup)
- **Inventory correctness**:
  - Must be concurrency-safe (Redis locks + DB transactional integrity)
  - Prevent oversell; reservations expire and are cleaned up
- **PDPA compliance**:
  - Explicit opt-in for marketing
  - Data access/deletion workflows with timelines
  - Data retention policy (not fully implemented yet, but modeled/required)
- **Multi-tenant isolation**:
  - Company is the tenant boundary
  - Row-level security (RLS) policies exist in schema; app must set `app.current_company_id`
- **Auditability**:
  - Audit logs / movements capture state changes with context

---

## 5) Bounded contexts / modules (DDD)

- **Accounts (Identity/Tenancy/RBAC)**
  - Company, users, roles, permissions
- **Commerce**
  - Categories, products, variants, customers, cart, orders
- **Inventory**
  - Locations, items, reservations, movements
- **Accounting**
  - Accounts (CoA), journal entries/lines, invoices, payments
- **Compliance**
  - GST returns, consents, access requests, audit logs
- **Integrations**
  - Gateways/adapters for payment/logistics/marketplaces

---

## 6) Core flows (end-to-end)

### 6.1 Order lifecycle (conceptual)

1. **Create order** (from cart / API)
2. **Reserve inventory**

   - lock by product/inventory item
   - update reserved_qty
   - create reservation (expires ~30 mins typical)
3. **Process payment**

   - gateway orchestration, webhooks for async confirmations
4. **Create invoice**

   - accounting entries + invoice record (and later PEPPOL optional)
5. **Notify + fulfill**

   - logistics label creation, tracking updates
6. **State transitions**

   - pending → confirmed → processing → shipped → delivered
   - cancellations/refunds/returns branch as allowed by state machine

### 6.2 Inventory computation

- `net_qty = available_qty - reserved_qty`
- Reservation ensures `reserved_qty <= available_qty` (constraint exists in SQL schema)

### 6.3 GST reporting (F5)

- `compliance.gst_returns` stores quarterly results:
  - Boxes 1–8 (taxable supplies, purchases, output tax, input tax, net)
- Orders store some GST reporting fields (e.g. box 1 & box 6 amounts)

---

## 7) Data model (database/schema.sql highlights)

### 7.1 Schemas (namespaces)

- `core`, `commerce`, `inventory`, `accounting`, `compliance`

### 7.2 Tenant root

- `core.companies`
  - UEN unique
  - GST registration fields
  - `settings` JSONB (e.g. order prefix)
- `core.users` + RBAC tables `core.roles`, `core.user_roles`
- `core.sequences`
  - Per-company, concurrency-safe sequencing for document numbers (e.g. orders)

### 7.3 Commerce

- `commerce.categories` (hierarchy via parent_id)
- `commerce.products`
  - DECIMAL pricing
  - `gst_code`, `gst_rate` (note: compliance-grade GST calculation must use `compliance.gst_rates` historical lookup)
  - `search_vector` generated tsvector with GIN index
  - `attributes` JSONB, `images` JSONB
- `commerce.product_variants` (unique variant SKU)
- `commerce.customers`
  - Customer profile, B2B attributes, and audit fields
  - PDPA consent is tracked in `compliance.data_consents` (multiple consent types over time)
  - B2B fields like `company_uen`, credit limits
- `commerce.carts`, `commerce.cart_items`
  - Cart persistence for anonymous sessions and logged-in customers
  - Supports cart merge/convert flows; cart items are unique per `(cart_id, product_id, variant_id)`
- `commerce.orders` (partitioned by `order_date`)
  - separate statuses: order/payment/fulfillment
  - monetary totals
  - addresses as JSONB
  - `commerce.order_items` references partitioned orders via `(order_id, order_date)` FK

### 7.4 Inventory

- `inventory.locations`
- `inventory.items`
  - computed stored `net_qty`
  - optimistic `version`
  - constraint `reserved_qty <= available_qty`
- `inventory.reservations` with expiry & status
- `inventory.movements` for audit trail
- Trigger: `log_inventory_change` writes a movement on available_qty change

### 7.5 Accounting

- `accounting.accounts` (CoA)
- `accounting.account_templates`
  - Seed templates used to initialize company-specific accounts (avoids invalid `NULL company_id` inserts)
- `initialize_company_accounts(company_id)`
  - Helper function to populate `accounting.accounts` per company
- `accounting.journal_entries` with `balanced_entry` constraint
- `accounting.journal_lines` with `one_side_only` constraint
- `accounting.invoices` with computed `amount_due`
- `accounting.payments`

### 7.6 Compliance

- `compliance.gst_returns` for F5 lifecycle
- `compliance.gst_rates` for historical GST rates (effective-date lookup)
- `compliance.data_consents`
  - Consent type is normalized with 6 purposes: `marketing`, `analytics`, `third_party`, `profiling`, `order_processing`, `legal_compliance`
- `compliance.data_access_requests` with due_date SLA
- `compliance.audit_logs`
- `compliance.peppol_invoices`, `compliance.peppol_acknowledgments`
  - Operational storage for InvoiceNow/PEPPOL submission lifecycle and acknowledgments

### 7.7 RLS

- RLS enabled for key tables and policies based on:
  - `current_setting('app.current_company_id')::UUID`
  - Newly added tables are also covered, including carts, sequences, and PEPPOL operational tables

---

## 8) Performance and reliability targets (from docs)

- **API**: <200ms p95
- **Mobile**: <2.0s page load
- **Inventory accuracy**: 99.5%
- **Uptime**: 99.9%
- **Search**: Postgres tsvector for MVP (upgrade later)

---

## 9) Security posture (high-level)

- Defense-in-depth (WAF/rate limiting → app auth/RBAC → encryption/tokenization → monitoring/audit)
- JWT auth (short-lived access tokens suggested)
- CSP headers (Django 6 supports CSP)
- PII masking in logs
- Payment PCI scope minimized via tokenization (Stripe/HitPay)

---

## 10) Implementation roadmap (macro)

- Phase 1: Foundation (infra, settings, core models, auth/RBAC, admin)
- Phase 2: Commerce domain
- Phase 3: Inventory domain
- Phase 4: Accounting + GST engine
- Phase 5: Compliance & integrations
- Phase 6–7: Frontend foundation + features
- Phase 8: Testing + deployment hardening

---

## 11) Practical dev guardrails

- Treat `database/schema.sql` as a design source of truth (UUIDs, computed columns, constraints, RLS).
- Use a single consistent rounding strategy for GST and totals (2 dp for amounts).
- Ensure all domain write operations are:
  - transactional (DB)
  - concurrency-safe (inventory)
  - auditable (movements/audit logs)
- Keep domain modules decoupled via services/events, not cross-import spaghetti.
