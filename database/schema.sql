-- ============================================================================
-- SINGAPORE SMB E-COMMERCE PLATFORM
-- Complete PostgreSQL 16 Database Schema
-- Version: 2.0
-- Date: December 18, 2025
-- ============================================================================

-- ============================================================================
-- EXTENSIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";       -- Encryption functions
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gist";     -- GiST index support

-- ============================================================================
-- SCHEMAS
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS commerce;
CREATE SCHEMA IF NOT EXISTS inventory;
CREATE SCHEMA IF NOT EXISTS accounting;
CREATE SCHEMA IF NOT EXISTS compliance;

-- ============================================================================
-- CORE SCHEMA - Shared entities
-- ============================================================================

-- Companies (Multi-tenant root)
CREATE TABLE core.companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    legal_name VARCHAR(200) NOT NULL,
    uen VARCHAR(10) UNIQUE NOT NULL,  -- Singapore Unique Entity Number
    
    -- GST Registration
    gst_registered BOOLEAN NOT NULL DEFAULT FALSE,
    gst_registration_number VARCHAR(15) NOT NULL,
    gst_registration_date DATE,
    
    -- Contact Information
    email VARCHAR(254) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    website VARCHAR(255) NOT NULL,
    
    -- Address
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255) NOT NULL,
    postal_code VARCHAR(6) NOT NULL,
    country VARCHAR(2) NOT NULL DEFAULT 'SG',
    
    -- Settings (JSONB for flexibility)
    settings JSONB NOT NULL DEFAULT '{}',
    
    -- Subscription
    plan_tier VARCHAR(20) NOT NULL DEFAULT 'lite' CHECK (plan_tier IN ('lite', 'standard', 'advanced')),
    
    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_companies_uen ON core.companies(uen);
CREATE INDEX idx_companies_gst ON core.companies(gst_registered) WHERE gst_registered = TRUE;
CREATE INDEX idx_companies_deleted_at ON core.companies(deleted_at);

-- Users
CREATE TABLE core.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES core.companies(id) ON DELETE CASCADE,
    
    -- Authentication
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Profile
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Security
    mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_secret VARCHAR(32) NOT NULL,
    last_login TIMESTAMPTZ,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ,
    
    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_users_company ON core.users(company_id);
CREATE INDEX idx_users_email ON core.users(email);
CREATE INDEX idx_users_deleted_at ON core.users(deleted_at);

-- Roles and Permissions (RBAC)
CREATE TABLE core.roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES core.companies(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    permissions JSONB NOT NULL DEFAULT '[]',
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_role_per_company UNIQUE(company_id, name)
);

CREATE INDEX idx_roles_company ON core.roles(company_id);

CREATE TABLE core.user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES core.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES core.roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID REFERENCES core.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_role UNIQUE(user_id, role_id)
);

CREATE INDEX idx_user_roles_user ON core.user_roles(user_id);
CREATE INDEX idx_user_roles_role ON core.user_roles(role_id);
CREATE INDEX idx_user_roles_assigned_by ON core.user_roles(assigned_by);

-- Sequences (Thread-safe numbering per company)
CREATE TABLE core.sequences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    sequence_type VARCHAR(50) NOT NULL,
    prefix VARCHAR(20),
    current_value BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, sequence_type)
);

-- ============================================================================
-- COMMERCE SCHEMA - E-commerce entities
-- ============================================================================

-- Categories
CREATE TABLE commerce.categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    parent_id UUID REFERENCES commerce.categories(id),
    
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    
    -- SEO
    meta_title VARCHAR(70),
    meta_description VARCHAR(160),
    
    -- Ordering
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(company_id, slug)
);

CREATE INDEX idx_categories_company ON commerce.categories(company_id);
CREATE INDEX idx_categories_parent ON commerce.categories(parent_id);

-- Products
CREATE TABLE commerce.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    category_id UUID REFERENCES commerce.categories(id),
    
    -- Identification
    sku VARCHAR(50) NOT NULL,
    barcode VARCHAR(50),
    
    -- Basic Info
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL,
    description TEXT,
    short_description VARCHAR(500),
    
    -- Pricing (DECIMAL precision critical)
    base_price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    compare_at_price DECIMAL(10,2),
    
    -- GST
    gst_code VARCHAR(2) DEFAULT 'SR' CHECK (gst_code IN ('SR', 'ZR', 'ES', 'OS')),
    gst_rate DECIMAL(5,4) DEFAULT 0.09,
    
    -- Physical
    weight_grams INTEGER,
    length_cm DECIMAL(6,2),
    width_cm DECIMAL(6,2),
    height_cm DECIMAL(6,2),
    
    -- Inventory
    track_inventory BOOLEAN DEFAULT TRUE,
    allow_backorder BOOLEAN DEFAULT FALSE,
    low_stock_threshold INTEGER DEFAULT 10,
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
    
    -- Media
    images JSONB DEFAULT '[]',
    
    -- SEO
    meta_title VARCHAR(70),
    meta_description VARCHAR(160),
    
    -- Custom Attributes
    attributes JSONB DEFAULT '{}',
    
    -- Search
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(description, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(sku, '')), 'A')
    ) STORED,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    
    UNIQUE(company_id, sku)
);

CREATE INDEX idx_products_company ON commerce.products(company_id);
CREATE INDEX idx_products_category ON commerce.products(category_id);
CREATE INDEX idx_products_status ON commerce.products(company_id, status);
CREATE INDEX idx_products_search ON commerce.products USING GIN(search_vector);
CREATE INDEX idx_products_sku ON commerce.products(sku);

-- Product Variants
CREATE TABLE commerce.product_variants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES commerce.products(id) ON DELETE CASCADE,
    
    sku VARCHAR(50) NOT NULL,
    barcode VARCHAR(50),
    name VARCHAR(200),
    
    -- Variant Attributes (e.g., {"size": "M", "color": "Blue"})
    options JSONB DEFAULT '{}',
    
    -- Pricing
    price_adjustment DECIMAL(10,2) DEFAULT 0,
    
    -- Physical
    weight_grams INTEGER,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_variants_product ON commerce.product_variants(product_id);
CREATE UNIQUE INDEX idx_variants_sku ON commerce.product_variants(sku);

-- Customers
CREATE TABLE commerce.customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    user_id UUID REFERENCES core.users(id),
    
    -- Profile
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    
    -- Customer Type
    customer_type VARCHAR(20) DEFAULT 'retail' CHECK (customer_type IN ('retail', 'wholesale', 'vip')),
    
    -- B2B Fields
    company_name VARCHAR(200),
    company_uen VARCHAR(10),
    credit_limit DECIMAL(12,2) DEFAULT 0,
    credit_used DECIMAL(12,2) DEFAULT 0,
    payment_terms INTEGER DEFAULT 0,  -- Days
    
    -- PDPA Compliance
    consent_marketing BOOLEAN DEFAULT FALSE,
    consent_analytics BOOLEAN DEFAULT TRUE,
    consent_timestamp TIMESTAMPTZ,
    consent_ip_address INET,
    data_retention_until DATE,
    
    -- Preferences
    preferred_language VARCHAR(5) DEFAULT 'en',
    preferred_currency VARCHAR(3) DEFAULT 'SGD',
    
    -- Tags
    tags JSONB DEFAULT '[]',
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    
    UNIQUE(company_id, email)
);

CREATE INDEX idx_customers_company ON commerce.customers(company_id);
CREATE INDEX idx_customers_email ON commerce.customers(email);
CREATE INDEX idx_customers_type ON commerce.customers(company_id, customer_type);

-- Customer Addresses
CREATE TABLE commerce.customer_addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES commerce.customers(id) ON DELETE CASCADE,
    
    -- Type
    address_type VARCHAR(20) DEFAULT 'shipping' CHECK (address_type IN ('shipping', 'billing')),
    is_default BOOLEAN DEFAULT FALSE,
    
    -- Address Fields
    recipient_name VARCHAR(200),
    phone VARCHAR(20),
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    postal_code VARCHAR(6) NOT NULL,
    country VARCHAR(2) DEFAULT 'SG',
    
    -- Singapore Specific
    building_name VARCHAR(200),
    unit_number VARCHAR(20),
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_addresses_customer ON commerce.customer_addresses(customer_id);

-- Shopping Carts
CREATE TABLE commerce.carts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    customer_id UUID REFERENCES commerce.customers(id),
    session_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'merged', 'converted', 'abandoned')),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    converted_order_id UUID,
    converted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    CONSTRAINT cart_identifier CHECK (customer_id IS NOT NULL OR session_id IS NOT NULL)
);

CREATE TABLE commerce.cart_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cart_id UUID NOT NULL REFERENCES commerce.carts(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES commerce.products(id),
    variant_id UUID REFERENCES commerce.product_variants(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    is_saved_for_later BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cart_id, product_id, variant_id)
);

CREATE INDEX idx_carts_company ON commerce.carts(company_id);
CREATE INDEX idx_carts_customer ON commerce.carts(customer_id);
CREATE INDEX idx_carts_session ON commerce.carts(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX idx_carts_expires ON commerce.carts(expires_at) WHERE status = 'active';
CREATE INDEX idx_cart_items_cart ON commerce.cart_items(cart_id);

-- Orders (Partitioned by month)
CREATE TABLE commerce.orders (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    customer_id UUID REFERENCES commerce.customers(id),
    
    -- Order Identification
    order_number VARCHAR(50) NOT NULL,
    
    -- Status
    status VARCHAR(30) DEFAULT 'pending' CHECK (status IN (
        'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'
    )),
    payment_status VARCHAR(30) DEFAULT 'pending' CHECK (payment_status IN (
        'pending', 'authorized', 'paid', 'partially_refunded', 'refunded', 'failed'
    )),
    fulfillment_status VARCHAR(30) DEFAULT 'unfulfilled' CHECK (fulfillment_status IN (
        'unfulfilled', 'partially_fulfilled', 'fulfilled', 'returned'
    )),
    
    -- Pricing (DECIMAL precision critical)
    subtotal DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    shipping_amount DECIMAL(12,2) DEFAULT 0,
    gst_amount DECIMAL(12,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    
    -- GST Reporting
    gst_box_1_amount DECIMAL(12,2),  -- Standard-rated supplies
    gst_box_6_amount DECIMAL(12,2),  -- Output tax
    
    -- Currency
    currency VARCHAR(3) DEFAULT 'SGD',
    
    -- Payment
    payment_method VARCHAR(50),
    payment_reference VARCHAR(100),
    
    -- Shipping
    shipping_method VARCHAR(50),
    shipping_address JSONB,
    billing_address JSONB,
    
    -- Tracking
    tracking_number VARCHAR(100),
    carrier VARCHAR(50),
    
    -- Dates
    order_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMPTZ,
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    
    -- Notes
    customer_notes TEXT,
    internal_notes TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES core.users(id),
    
    PRIMARY KEY (id, order_date)
) PARTITION BY RANGE (order_date);

-- Create monthly partitions (example for 2025)
CREATE TABLE commerce.orders_2025_01 PARTITION OF commerce.orders
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE commerce.orders_2025_02 PARTITION OF commerce.orders
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE commerce.orders_2025_03 PARTITION OF commerce.orders
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE commerce.orders_2025_04 PARTITION OF commerce.orders
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
CREATE TABLE commerce.orders_2025_05 PARTITION OF commerce.orders
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
CREATE TABLE commerce.orders_2025_06 PARTITION OF commerce.orders
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
CREATE TABLE commerce.orders_2025_07 PARTITION OF commerce.orders
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
CREATE TABLE commerce.orders_2025_08 PARTITION OF commerce.orders
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
CREATE TABLE commerce.orders_2025_09 PARTITION OF commerce.orders
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
CREATE TABLE commerce.orders_2025_10 PARTITION OF commerce.orders
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
CREATE TABLE commerce.orders_2025_11 PARTITION OF commerce.orders
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
CREATE TABLE commerce.orders_2025_12 PARTITION OF commerce.orders
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE INDEX idx_orders_company_status ON commerce.orders(company_id, status);
CREATE INDEX idx_orders_customer ON commerce.orders(customer_id);
CREATE INDEX idx_orders_number ON commerce.orders(order_number);
CREATE INDEX idx_orders_date ON commerce.orders(order_date);

-- Order Items
CREATE TABLE commerce.order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL,
    order_date TIMESTAMPTZ NOT NULL,
    product_id UUID REFERENCES commerce.products(id),
    variant_id UUID REFERENCES commerce.product_variants(id),
    
    -- Product Snapshot
    sku VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    
    -- Quantity
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    
    -- Pricing (DECIMAL precision)
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    gst_rate DECIMAL(5,4) NOT NULL,
    gst_amount DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,
    
    -- GST Code
    gst_code VARCHAR(2) NOT NULL,
    
    -- Fulfillment
    fulfilled_quantity INTEGER DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (order_id, order_date) REFERENCES commerce.orders(id, order_date)
);

CREATE INDEX idx_order_items_order ON commerce.order_items(order_id);
CREATE INDEX idx_order_items_product ON commerce.order_items(product_id);

-- ============================================================================
-- INVENTORY SCHEMA
-- ============================================================================

-- Locations (Warehouses, Stores)
CREATE TABLE inventory.locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    location_type VARCHAR(20) DEFAULT 'warehouse' CHECK (location_type IN ('warehouse', 'store', 'virtual')),
    
    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    postal_code VARCHAR(6),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    
    -- Settings
    settings JSONB DEFAULT '{}',
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(company_id, code)
);

CREATE INDEX idx_locations_company ON inventory.locations(company_id);

-- Inventory Items
CREATE TABLE inventory.items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    product_id UUID NOT NULL REFERENCES commerce.products(id),
    variant_id UUID REFERENCES commerce.product_variants(id),
    location_id UUID NOT NULL REFERENCES inventory.locations(id),
    
    -- Quantities
    available_qty INTEGER NOT NULL DEFAULT 0 CHECK (available_qty >= 0),
    reserved_qty INTEGER NOT NULL DEFAULT 0 CHECK (reserved_qty >= 0),
    
    -- Computed net quantity
    net_qty INTEGER GENERATED ALWAYS AS (available_qty - reserved_qty) STORED,
    
    -- Reorder
    reorder_point INTEGER,
    reorder_quantity INTEGER,
    
    -- Costing
    unit_cost DECIMAL(10,2),
    
    -- Tracking
    last_counted_at TIMESTAMPTZ,
    last_movement_at TIMESTAMPTZ,
    
    -- Optimistic Locking
    version INTEGER DEFAULT 1,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(product_id, variant_id, location_id),
    
    CONSTRAINT valid_reserved CHECK (reserved_qty <= available_qty)
);

CREATE INDEX idx_inventory_company ON inventory.items(company_id);
CREATE INDEX idx_inventory_product ON inventory.items(product_id);
CREATE INDEX idx_inventory_location ON inventory.items(location_id);
CREATE INDEX idx_inventory_low_stock ON inventory.items(net_qty) WHERE net_qty < 10;

-- Inventory Reservations
CREATE TABLE inventory.reservations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inventory_item_id UUID NOT NULL REFERENCES inventory.items(id),
    order_id UUID NOT NULL,
    
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'released', 'expired')),
    
    expires_at TIMESTAMPTZ NOT NULL,
    confirmed_at TIMESTAMPTZ,
    released_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reservations_item ON inventory.reservations(inventory_item_id);
CREATE INDEX idx_reservations_order ON inventory.reservations(order_id);
CREATE INDEX idx_reservations_expires ON inventory.reservations(expires_at) WHERE status = 'pending';

-- Inventory Movements
CREATE TABLE inventory.movements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    inventory_item_id UUID NOT NULL REFERENCES inventory.items(id),
    
    -- Movement Type
    movement_type VARCHAR(30) NOT NULL CHECK (movement_type IN (
        'purchase', 'sale', 'adjustment', 'transfer_in', 'transfer_out', 'return', 'damage', 'count'
    )),
    
    -- Quantity
    quantity INTEGER NOT NULL,  -- Positive for in, negative for out
    quantity_before INTEGER NOT NULL,
    quantity_after INTEGER NOT NULL,
    
    -- Reference
    reference_type VARCHAR(50),
    reference_id UUID,
    
    -- Details
    notes TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES core.users(id)
);

CREATE INDEX idx_movements_company ON inventory.movements(company_id);
CREATE INDEX idx_movements_item ON inventory.movements(inventory_item_id);
CREATE INDEX idx_movements_date ON inventory.movements(created_at);

-- ============================================================================
-- ACCOUNTING SCHEMA
-- ============================================================================

-- Chart of Accounts
CREATE TABLE accounting.accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    parent_id UUID REFERENCES accounting.accounts(id),
    
    -- Account Info
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Classification
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN (
        'asset', 'liability', 'equity', 'revenue', 'expense'
    )),
    account_subtype VARCHAR(50),
    
    -- GST Mapping
    gst_code VARCHAR(2),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE,
    
    -- Balance
    current_balance DECIMAL(15,2) DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(company_id, code)
);

CREATE INDEX idx_accounts_company ON accounting.accounts(company_id);
CREATE INDEX idx_accounts_type ON accounting.accounts(account_type);

-- Journal Entries
CREATE TABLE accounting.journal_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    
    -- Entry Info
    entry_number VARCHAR(50) NOT NULL,
    entry_date DATE NOT NULL,
    description TEXT,
    
    -- Reference
    reference_type VARCHAR(50),  -- 'order', 'invoice', 'payment', 'manual'
    reference_id UUID,
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'posted', 'voided')),
    posted_at TIMESTAMPTZ,
    
    -- Totals (for validation)
    total_debit DECIMAL(15,2) NOT NULL,
    total_credit DECIMAL(15,2) NOT NULL,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES core.users(id),
    approved_by UUID REFERENCES core.users(id),
    
    UNIQUE(company_id, entry_number),
    CONSTRAINT balanced_entry CHECK (total_debit = total_credit)
);

CREATE INDEX idx_journals_company ON accounting.journal_entries(company_id);
CREATE INDEX idx_journals_date ON accounting.journal_entries(entry_date);
CREATE INDEX idx_journals_reference ON accounting.journal_entries(reference_type, reference_id);

-- Journal Entry Lines
CREATE TABLE accounting.journal_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journal_entry_id UUID NOT NULL REFERENCES accounting.journal_entries(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounting.accounts(id),
    
    -- Amounts
    debit_amount DECIMAL(12,2) DEFAULT 0 CHECK (debit_amount >= 0),
    credit_amount DECIMAL(12,2) DEFAULT 0 CHECK (credit_amount >= 0),
    
    -- GST
    gst_amount DECIMAL(10,2) DEFAULT 0,
    gst_code VARCHAR(2),
    
    -- Description
    description TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT one_side_only CHECK (
        (debit_amount > 0 AND credit_amount = 0) OR
        (credit_amount > 0 AND debit_amount = 0)
    )
);

CREATE INDEX idx_journal_lines_entry ON accounting.journal_lines(journal_entry_id);
CREATE INDEX idx_journal_lines_account ON accounting.journal_lines(account_id);

-- Invoices
CREATE TABLE accounting.invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    customer_id UUID REFERENCES commerce.customers(id),
    order_id UUID,
    
    -- Invoice Info
    invoice_number VARCHAR(50) NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'paid', 'overdue', 'void')),
    
    -- Amounts
    subtotal DECIMAL(12,2) NOT NULL,
    gst_amount DECIMAL(12,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    amount_paid DECIMAL(12,2) DEFAULT 0,
    amount_due DECIMAL(12,2) GENERATED ALWAYS AS (total_amount - amount_paid) STORED,
    
    -- PEPPOL/InvoiceNow
    peppol_id VARCHAR(100),
    peppol_status VARCHAR(20),
    peppol_submitted_at TIMESTAMPTZ,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(company_id, invoice_number)
);

CREATE INDEX idx_invoices_company ON accounting.invoices(company_id);
CREATE INDEX idx_invoices_customer ON accounting.invoices(customer_id);
CREATE INDEX idx_invoices_status ON accounting.invoices(status);

-- Payments
CREATE TABLE accounting.payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    
    -- Payment Info
    payment_number VARCHAR(50) NOT NULL,
    payment_date DATE NOT NULL,
    
    -- Amount
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'SGD',
    
    -- Payment Method
    payment_method VARCHAR(50) NOT NULL,
    gateway VARCHAR(50),
    gateway_reference VARCHAR(100),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    
    -- Reference
    reference_type VARCHAR(50),  -- 'order', 'invoice'
    reference_id UUID,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(company_id, payment_number)
);

CREATE INDEX idx_payments_company ON accounting.payments(company_id);
CREATE INDEX idx_payments_reference ON accounting.payments(reference_type, reference_id);

-- ==========================================================================
-- COMPLIANCE SCHEMA
-- ==========================================================================

-- GST Rates (Historical)
CREATE TABLE compliance.gst_rates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    effective_date DATE NOT NULL,
    rate DECIMAL(5,4) NOT NULL,
    description VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(effective_date)
);

INSERT INTO compliance.gst_rates (effective_date, rate, description) VALUES
('1994-04-01', 0.03, 'GST introduction'),
('2003-01-01', 0.04, 'Increase to 4%'),
('2004-01-01', 0.05, 'Increase to 5%'),
('2007-07-01', 0.07, 'Increase to 7%'),
('2023-01-01', 0.08, 'Increase to 8%'),
('2024-01-01', 0.09, 'Increase to 9% (current)');

-- GST F5 Returns
CREATE TABLE compliance.gst_returns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    
    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    year INTEGER NOT NULL,
    
    -- F5 Box Values (DECIMAL precision)
    box_1 DECIMAL(12,2) DEFAULT 0,  -- Standard-rated supplies
    box_2 DECIMAL(12,2) DEFAULT 0,  -- Zero-rated supplies
    box_3 DECIMAL(12,2) DEFAULT 0,  -- Exempt supplies
    box_4 DECIMAL(12,2) DEFAULT 0,  -- Total supplies (1+2+3)
    box_5 DECIMAL(12,2) DEFAULT 0,  -- Total taxable purchases
    box_6 DECIMAL(12,2) DEFAULT 0,  -- Output tax due
    box_7 DECIMAL(12,2) DEFAULT 0,  -- Input tax claimable
    box_8 DECIMAL(12,2) DEFAULT 0,  -- Net GST (6-7)
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'validated', 'submitted', 'accepted', 'rejected')),
    
    -- Submission
    submission_date DATE,
    iras_reference VARCHAR(100),
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    prepared_by UUID REFERENCES core.users(id),
    submitted_by UUID REFERENCES core.users(id),
    
    UNIQUE(company_id, year, quarter)
);

CREATE INDEX idx_gst_returns_company ON compliance.gst_returns(company_id);
CREATE INDEX idx_gst_returns_status ON compliance.gst_returns(status);

-- PEPPOL Invoices
CREATE TABLE compliance.peppol_invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    invoice_id UUID NOT NULL REFERENCES accounting.invoices(id),
    peppol_id VARCHAR(100) UNIQUE,
    sender_endpoint VARCHAR(50) NOT NULL,
    receiver_endpoint VARCHAR(50),
    document_type VARCHAR(10) DEFAULT '380',
    ubl_version VARCHAR(10) DEFAULT '2.1',
    customization_id VARCHAR(100) DEFAULT 'urn:cen.eu:en16931:2017#conformant#urn:fdc:peppol.eu:2017:poacc:billing:international:sg:3.0',
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN (
        'draft', 'validated', 'signed', 'submitted', 'acknowledged', 'rejected', 'failed'
    )),
    submitted_at TIMESTAMPTZ,
    access_point_provider VARCHAR(100),
    submission_reference VARCHAR(100),
    acknowledged_at TIMESTAMPTZ,
    acknowledgment_code VARCHAR(20),
    rejection_reason TEXT,
    xml_document TEXT,
    signature_value TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);

CREATE TABLE compliance.peppol_acknowledgments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    peppol_invoice_id UUID NOT NULL REFERENCES compliance.peppol_invoices(id) ON DELETE CASCADE,
    message_id VARCHAR(100) NOT NULL,
    status_code VARCHAR(20) NOT NULL,
    status_description TEXT,
    raw_response JSONB,
    received_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_peppol_invoices_company ON compliance.peppol_invoices(company_id);
CREATE INDEX idx_peppol_invoices_status ON compliance.peppol_invoices(status);
CREATE INDEX idx_peppol_acks_invoice ON compliance.peppol_acknowledgments(peppol_invoice_id);

-- PDPA Data Consents
CREATE TABLE compliance.data_consents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES commerce.customers(id),
    
    -- Consent Type
    consent_type VARCHAR(50) NOT NULL CHECK (consent_type IN (
        'order_processing',
        'marketing',
        'analytics',
        'third_party',
        'profiling',
        'legal_compliance'
    )),
    
    -- Status
    is_granted BOOLEAN NOT NULL,
    
    -- Context
    source VARCHAR(50),  -- 'registration', 'checkout', 'settings'
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp
    consent_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_consents_customer ON compliance.data_consents(customer_id);

-- Data Access Requests (PDPA)
CREATE TABLE compliance.data_access_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES core.companies(id),
    customer_id UUID NOT NULL REFERENCES commerce.customers(id),
    
    -- Request Type
    request_type VARCHAR(20) NOT NULL CHECK (request_type IN ('access', 'correction', 'deletion')),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'rejected')),
    
    -- Timeline (30-day requirement)
    requested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date DATE NOT NULL,
    completed_at TIMESTAMPTZ,
    
    -- Response
    response_notes TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    processed_by UUID REFERENCES core.users(id)
);

CREATE INDEX idx_data_requests_company ON compliance.data_access_requests(company_id);
CREATE INDEX idx_data_requests_status ON compliance.data_access_requests(status);

-- Audit Log
CREATE TABLE compliance.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES core.companies(id),
    user_id UUID REFERENCES core.users(id),
    
    -- Action
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    
    -- Details
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_company ON compliance.audit_logs(company_id);
CREATE INDEX idx_audit_user ON compliance.audit_logs(user_id);
CREATE INDEX idx_audit_resource ON compliance.audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_date ON compliance.audit_logs(created_at);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_companies_timestamp BEFORE UPDATE ON core.companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_users_timestamp BEFORE UPDATE ON core.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_products_timestamp BEFORE UPDATE ON commerce.products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_customers_timestamp BEFORE UPDATE ON commerce.customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_inventory_timestamp BEFORE UPDATE ON inventory.items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_sequences_timestamp BEFORE UPDATE ON core.sequences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_carts_timestamp BEFORE UPDATE ON commerce.carts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_cart_items_timestamp BEFORE UPDATE ON commerce.cart_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_peppol_invoices_timestamp BEFORE UPDATE ON compliance.peppol_invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Inventory movement audit trigger
CREATE OR REPLACE FUNCTION log_inventory_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.available_qty != NEW.available_qty THEN
        INSERT INTO inventory.movements (
            company_id, inventory_item_id, movement_type,
            quantity, quantity_before, quantity_after, notes
        ) VALUES (
            NEW.company_id, NEW.id, 'adjustment',
            NEW.available_qty - OLD.available_qty,
            OLD.available_qty, NEW.available_qty,
            'Automatic audit log'
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_inventory_changes AFTER UPDATE ON inventory.items
    FOR EACH ROW EXECUTE FUNCTION log_inventory_change();

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Calculate GST amount
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

-- Generate order number
CREATE OR REPLACE FUNCTION generate_order_number(p_company_id UUID)
RETURNS VARCHAR(50) AS $$
DECLARE
    v_prefix VARCHAR(20);
    v_seq_num BIGINT;
BEGIN
    UPDATE core.sequences
    SET current_value = current_value + 1
    WHERE company_id = p_company_id AND sequence_type = 'order'
    RETURNING current_value, prefix INTO v_seq_num, v_prefix;

    IF v_seq_num IS NULL THEN
        INSERT INTO core.sequences (company_id, sequence_type, prefix, current_value)
        VALUES (p_company_id, 'order', 'ORD', 1)
        ON CONFLICT (company_id, sequence_type)
        DO UPDATE SET current_value = core.sequences.current_value + 1
        RETURNING current_value, prefix INTO v_seq_num, v_prefix;
    END IF;

    RETURN COALESCE(v_prefix, 'ORD') || '-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || LPAD(v_seq_num::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;

-- ==========================================================================
-- DEFAULT DATA
-- ==========================================================================

-- Default Chart of Accounts (Singapore) - Templates
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

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Inventory Summary View
CREATE OR REPLACE VIEW inventory.summary AS
SELECT 
    i.company_id,
    p.id AS product_id,
    p.sku,
    p.name,
    l.id AS location_id,
    l.name AS location_name,
    i.available_qty,
    i.reserved_qty,
    i.net_qty,
    i.reorder_point,
    CASE WHEN i.net_qty <= COALESCE(i.reorder_point, 10) THEN TRUE ELSE FALSE END AS needs_reorder
FROM inventory.items i
JOIN commerce.products p ON i.product_id = p.id
JOIN inventory.locations l ON i.location_id = l.id
WHERE p.deleted_at IS NULL;

-- Daily Sales Summary View
CREATE OR REPLACE VIEW accounting.daily_sales AS
SELECT 
    company_id,
    DATE(order_date) AS sale_date,
    COUNT(*) AS order_count,
    SUM(subtotal) AS subtotal,
    SUM(gst_amount) AS gst_amount,
    SUM(total_amount) AS total_amount,
    AVG(total_amount) AS avg_order_value
FROM commerce.orders
WHERE status NOT IN ('cancelled', 'refunded')
GROUP BY company_id, DATE(order_date);

-- ============================================================================
-- ROW-LEVEL SECURITY (Multi-tenant isolation)
-- ============================================================================

-- Enable RLS on key tables
ALTER TABLE commerce.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE commerce.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE commerce.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory.items ENABLE ROW LEVEL SECURITY;

ALTER TABLE core.sequences ENABLE ROW LEVEL SECURITY;
ALTER TABLE commerce.carts ENABLE ROW LEVEL SECURITY;
ALTER TABLE commerce.cart_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance.gst_returns ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance.peppol_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance.peppol_acknowledgments ENABLE ROW LEVEL SECURITY;

-- Create policies (companies can only see their own data)
CREATE POLICY company_isolation_products ON commerce.products
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY company_isolation_orders ON commerce.orders
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY company_isolation_customers ON commerce.customers
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY company_isolation_inventory ON inventory.items
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY company_isolation_sequences ON core.sequences
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY company_isolation_carts ON commerce.carts
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY company_isolation_cart_items ON commerce.cart_items
    USING (
        EXISTS (
            SELECT 1
            FROM commerce.carts c
            WHERE c.id = cart_id
              AND c.company_id = current_setting('app.current_company_id')::UUID
        )
    );

CREATE POLICY company_isolation_gst_returns ON compliance.gst_returns
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY company_isolation_peppol_invoices ON compliance.peppol_invoices
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY company_isolation_peppol_acknowledgments ON compliance.peppol_acknowledgments
    USING (
        EXISTS (
            SELECT 1
            FROM compliance.peppol_invoices pi
            WHERE pi.id = peppol_invoice_id
              AND pi.company_id = current_setting('app.current_company_id')::UUID
        )
    );

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Application role
CREATE ROLE app_user;
GRANT USAGE ON SCHEMA core, commerce, inventory, accounting, compliance TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA core, commerce, inventory, accounting, compliance TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA core, commerce, inventory, accounting, compliance TO app_user;

-- Read-only role for reporting
CREATE ROLE readonly_user;
GRANT USAGE ON SCHEMA core, commerce, inventory, accounting, compliance TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA core, commerce, inventory, accounting, compliance TO readonly_user;
