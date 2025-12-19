# Phase 2: Commerce Domain - Implementation Plan

> **Version**: 1.0  
> **Created**: December 19, 2025  
> **Duration**: Weeks 4-6  
> **Dependencies**: Phase 1 (accounts, core) ✅ Complete  
> **Status**: 🔵 Pending User Approval

---

## 1. Executive Summary

Phase 2 implements the **Commerce Domain** — the core e-commerce functionality including product catalog, customers, shopping carts, and orders. This phase establishes the foundation for inventory management (Phase 3) and accounting (Phase 4).

### Scope

| Entity | Schema Table | Key Features |
|--------|--------------|--------------|
| Category | `commerce.categories` | Hierarchical (self-referential), SEO fields |
| Product | `commerce.products` | DECIMAL pricing, GST codes, tsvector search |
| ProductVariant | `commerce.product_variants` | Options JSONB, price adjustment |
| Customer | `commerce.customers` | PDPA consent, B2B fields, customer types |
| CustomerAddress | `commerce.customer_addresses` | Singapore format, unit_number |
| Cart | `commerce.carts` | Guest/customer, 7-day expiry, merge on login |
| CartItem | `commerce.cart_items` | Quantity constraints, saved-for-later |
| Order | `commerce.orders` | **Partitioned by month**, GST reporting fields |
| OrderItem | `commerce.order_items` | Line totals, GST, fulfilled_quantity |

---

## 2. User Review Required

> [!IMPORTANT]
> **Order Partitioning Strategy**: The schema uses PostgreSQL range partitioning by `order_date`. Django does not natively support partitioned tables. We have two options:
> 1. **Managed Partitions**: Create partitions via raw SQL in migrations (recommended for production)
> 2. **Single Table MVP**: Ignore partitioning in Django ORM, handle at DB level
>
> **Recommendation**: Option 1 — use raw SQL for partition creation in initial migration.

> [!WARNING]
> **tsvector Search**: Django does not auto-populate PostgreSQL `GENERATED ALWAYS AS` columns. The `search_vector` field will be:
> - Read-only in Django (populated by PostgreSQL trigger/generated column)
> - Used via `SearchVector` and `SearchQuery` from `django.contrib.postgres.search`

---

## 3. Proposed Changes

### 3.1 App Structure

#### [NEW] `backend/apps/commerce/__init__.py`

Empty package initializer.

**Checklist**:
- [ ] Create empty [__init__.py](file:///home/project/singapore-smb/backend/core/__init__.py)

---

#### [NEW] `backend/apps/commerce/apps.py`

App configuration.

**Checklist**:
- [ ] Create `CommerceConfig` with `name = 'apps.commerce'`
- [ ] Set `verbose_name = 'Commerce'`
- [ ] Add `default_auto_field = 'django.db.models.UUIDField'`

---

### 3.2 Models

#### [NEW] `backend/apps/commerce/models/__init__.py`

**Checklist**:
- [ ] Export all model classes (Category, Product, ProductVariant, Customer, CustomerAddress, Cart, CartItem, Order, OrderItem)

---

#### [NEW] `backend/apps/commerce/models/category.py`

**Features**:
- Self-referential `parent` FK for hierarchy
- Company-scoped (`company_id`)
- SEO fields (`meta_title`, `meta_description`)
- Unique [(company_id, slug)](file:///home/project/singapore-smb/backend/apps/accounts/views.py#127-132) constraint

**Interfaces**:
- Inherits from `core.models.SoftDeleteModel` + [CompanyOwnedModel](file:///home/project/singapore-smb/backend/core/models.py#147-163)

**Checklist**:
- [ ] [id](file:///home/project/singapore-smb/backend/core/middleware.py#74-94) UUID primary key
- [ ] [company](file:///home/project/singapore-smb/backend/apps/accounts/services.py#340-388) FK to `accounts.Company` (CASCADE)
- [ ] `parent` FK to self (SET_NULL, null=True)
- [ ] [name](file:///home/project/singapore-smb/backend/apps/accounts/models.py#314-319) CharField(100)
- [ ] `slug` SlugField(100) with `unique_together = [('company', 'slug')]`
- [ ] `description` TextField(blank=True)
- [ ] `image_url` URLField(blank=True)
- [ ] `meta_title` CharField(70, blank=True)
- [ ] `meta_description` CharField(160, blank=True)
- [ ] `sort_order` IntegerField(default=0)
- [ ] `is_active` BooleanField(default=True)
- [ ] Add `get_ancestors()` and `get_descendants()` methods
- [ ] Set `db_table = '"commerce"."categories"'`

---

#### [NEW] `backend/apps/commerce/models/product.py`

**Features**:
- DECIMAL pricing fields (base_price, cost_price, compare_at_price)
- GST code with choices (SR, ZR, ES, OS)
- PostgreSQL tsvector search (read-only, DB-generated)
- JSONB for images and custom attributes

**Interfaces**:
- Inherits from [SoftDeleteModel](file:///home/project/singapore-smb/backend/core/models.py#93-145) + [CompanyOwnedModel](file:///home/project/singapore-smb/backend/core/models.py#147-163)

**Checklist**:
- [ ] [id](file:///home/project/singapore-smb/backend/core/middleware.py#74-94) UUID primary key
- [ ] [company](file:///home/project/singapore-smb/backend/apps/accounts/services.py#340-388) FK (CASCADE)
- [ ] `category` FK to Category (SET_NULL, null=True)
- [ ] `sku` CharField(50) with `unique_together = [('company', 'sku')]`
- [ ] `barcode` CharField(50, blank=True)
- [ ] [name](file:///home/project/singapore-smb/backend/apps/accounts/models.py#314-319) CharField(200)
- [ ] `slug` SlugField(200)
- [ ] `description` TextField(blank=True)
- [ ] `short_description` CharField(500, blank=True)
- [ ] `base_price` DecimalField(max_digits=10, decimal_places=2)
- [ ] `cost_price` DecimalField(max_digits=10, decimal_places=2, null=True)
- [ ] `compare_at_price` DecimalField(max_digits=10, decimal_places=2, null=True)
- [ ] `gst_code` CharField(2) with choices, default='SR'
- [ ] `gst_rate` DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.09'))
- [ ] `weight_grams` PositiveIntegerField(null=True)
- [ ] `length_cm`, `width_cm`, `height_cm` DecimalField(6,2, null=True)
- [ ] `track_inventory` BooleanField(default=True)
- [ ] `allow_backorder` BooleanField(default=False)
- [ ] `low_stock_threshold` PositiveIntegerField(default=10)
- [ ] `status` CharField(20) choices: draft, active, archived
- [ ] `images` JSONField(default=list)
- [ ] `meta_title` CharField(70, blank=True)
- [ ] `meta_description` CharField(160, blank=True)
- [ ] `attributes` JSONField(default=dict)
- [ ] Add `@property effective_price` (base_price or compare_at_price)
- [ ] Add `calculate_gst(quantity=1)` method
- [ ] Set `db_table = '"commerce"."products"'`
- [ ] Add GIN index for search (migration with raw SQL)

---

#### [NEW] `backend/apps/commerce/models/product.py` (ProductVariant class)

**Features**:
- Options as JSONB (e.g., `{"size": "M", "color": "Blue"}`)
- Price adjustment (added to base_price)

**Checklist**:
- [ ] [id](file:///home/project/singapore-smb/backend/core/middleware.py#74-94) UUID primary key
- [ ] `product` FK (CASCADE)
- [ ] `sku` CharField(50, unique=True)
- [ ] `barcode` CharField(50, blank=True)
- [ ] [name](file:///home/project/singapore-smb/backend/apps/accounts/models.py#314-319) CharField(200, blank=True)
- [ ] `options` JSONField(default=dict)
- [ ] `price_adjustment` DecimalField(10,2, default=0)
- [ ] `weight_grams` PositiveIntegerField(null=True)
- [ ] `is_active` BooleanField(default=True)
- [ ] Add `@property effective_price` (product.base_price + price_adjustment)
- [ ] Set `db_table = '"commerce"."product_variants"'`

---

#### [NEW] `backend/apps/commerce/models/customer.py`

**Features**:
- Customer types: retail, wholesale, VIP
- B2B fields: company_uen, credit_limit, payment_terms
- PDPA consent fields with timestamps

**Interfaces**:
- Inherits from [SoftDeleteModel](file:///home/project/singapore-smb/backend/core/models.py#93-145) + [CompanyOwnedModel](file:///home/project/singapore-smb/backend/core/models.py#147-163)

**Checklist**:
- [ ] [id](file:///home/project/singapore-smb/backend/core/middleware.py#74-94) UUID primary key
- [ ] [company](file:///home/project/singapore-smb/backend/apps/accounts/services.py#340-388) FK (CASCADE)
- [ ] [user](file:///home/project/singapore-smb/backend/apps/accounts/views.py#70-77) FK to User (SET_NULL, null=True) — optional link to platform user
- [ ] [email](file:///home/project/singapore-smb/backend/apps/accounts/tests/test_models.py#123-129) EmailField with `unique_together = [('company', 'email')]`
- [ ] `phone` CharField(20, blank=True)
- [ ] `first_name` CharField(100)
- [ ] `last_name` CharField(100)
- [ ] `customer_type` CharField(20) choices: retail, wholesale, vip
- [ ] `company_name` CharField(200, blank=True) — B2B
- [ ] `company_uen` CharField(10, blank=True) — B2B
- [ ] `credit_limit` DecimalField(12,2, default=0)
- [ ] `credit_used` DecimalField(12,2, default=0)
- [ ] `payment_terms` PositiveIntegerField(default=0)
- [ ] `consent_marketing` BooleanField(default=False)
- [ ] `consent_analytics` BooleanField(default=True)
- [ ] `consent_timestamp` DateTimeField(null=True)
- [ ] `consent_ip_address` GenericIPAddressField(null=True)
- [ ] `data_retention_until` DateField(null=True)
- [ ] `preferred_language` CharField(5, default='en')
- [ ] `preferred_currency` CharField(3, default='SGD')
- [ ] `tags` JSONField(default=list)
- [ ] Add `@property full_name`
- [ ] Add `@property available_credit` (credit_limit - credit_used)
- [ ] Set `db_table = '"commerce"."customers"'`

---

#### [NEW] `backend/apps/commerce/models/customer.py` (CustomerAddress class)

**Checklist**:
- [ ] [id](file:///home/project/singapore-smb/backend/core/middleware.py#74-94) UUID primary key
- [ ] `customer` FK (CASCADE)
- [ ] `address_type` CharField(20) choices: shipping, billing
- [ ] `is_default` BooleanField(default=False)
- [ ] `recipient_name` CharField(200)
- [ ] `phone` CharField(20, blank=True)
- [ ] `address_line1` CharField(255)
- [ ] `address_line2` CharField(255, blank=True)
- [ ] `postal_code` CharField(6) — Singapore 6-digit
- [ ] `country` CharField(2, default='SG')
- [ ] `building_name` CharField(200, blank=True)
- [ ] `unit_number` CharField(20, blank=True)
- [ ] Add `get_formatted_address()` method
- [ ] Set `db_table = '"commerce"."customer_addresses"'`

---

#### [NEW] `backend/apps/commerce/models/cart.py`

**Features**:
- Guest carts via `session_id`
- 7-day default expiry
- Cart statuses: active, merged, converted, abandoned
- Constraint: `customer_id IS NOT NULL OR session_id IS NOT NULL`

**Checklist**:
- [ ] [id](file:///home/project/singapore-smb/backend/core/middleware.py#74-94) UUID primary key
- [ ] [company](file:///home/project/singapore-smb/backend/apps/accounts/services.py#340-388) FK (CASCADE)
- [ ] `customer` FK to Customer (SET_NULL, null=True)
- [ ] `session_id` CharField(100, blank=True, null=True)
- [ ] `status` CharField(20) choices, default='active'
- [ ] `expires_at` DateTimeField (default: now + 7 days)
- [ ] `converted_order_id` UUIDField(null=True)
- [ ] `converted_at` DateTimeField(null=True)
- [ ] Add constraint for guest/customer check
- [ ] Add `@property is_expired`
- [ ] Add `@property item_count`
- [ ] Add `calculate_totals()` method
- [ ] Set `db_table = '"commerce"."carts"'`

---

#### [NEW] `backend/apps/commerce/models/cart.py` (CartItem class)

**Checklist**:
- [ ] [id](file:///home/project/singapore-smb/backend/core/middleware.py#74-94) UUID primary key
- [ ] `cart` FK (CASCADE)
- [ ] `product` FK to Product (PROTECT)
- [ ] `variant` FK to ProductVariant (SET_NULL, null=True)
- [ ] `quantity` PositiveIntegerField with `MIN_VALUE=1` validator
- [ ] `unit_price` DecimalField(10,2) — snapshot at add time
- [ ] `is_saved_for_later` BooleanField(default=False)
- [ ] Add `unique_together = [('cart', 'product', 'variant')]`
- [ ] Add `@property line_total` (quantity * unit_price)
- [ ] Set `db_table = '"commerce"."cart_items"'`

---

#### [NEW] `backend/apps/commerce/models/order.py`

**Features**:
- Order status state machine: pending → confirmed → processing → shipped → delivered
- Payment status tracking
- GST reporting fields (box_1, box_6)
- JSONB for shipping/billing addresses
- **Note**: Table is partitioned in PostgreSQL, manage via raw SQL

**Checklist**:
- [ ] [id](file:///home/project/singapore-smb/backend/core/middleware.py#74-94) UUID primary key
- [ ] [company](file:///home/project/singapore-smb/backend/apps/accounts/services.py#340-388) FK (CASCADE)
- [ ] `customer` FK to Customer (SET_NULL, null=True)
- [ ] `order_number` CharField(50) — generated via `generate_order_number()`
- [ ] `status` CharField(30) with transitions
- [ ] `payment_status` CharField(30)
- [ ] `fulfillment_status` CharField(30)
- [ ] `subtotal` DecimalField(12,2)
- [ ] `discount_amount` DecimalField(12,2, default=0)
- [ ] `shipping_amount` DecimalField(12,2, default=0)
- [ ] `gst_amount` DecimalField(12,2)
- [ ] `total_amount` DecimalField(12,2)
- [ ] `gst_box_1_amount` DecimalField(12,2, null=True)
- [ ] `gst_box_6_amount` DecimalField(12,2, null=True)
- [ ] `currency` CharField(3, default='SGD')
- [ ] `payment_method` CharField(50, blank=True)
- [ ] `payment_reference` CharField(100, blank=True)
- [ ] `shipping_method` CharField(50, blank=True)
- [ ] `shipping_address` JSONField(null=True)
- [ ] `billing_address` JSONField(null=True)
- [ ] `tracking_number` CharField(100, blank=True)
- [ ] `carrier` CharField(50, blank=True)
- [ ] `order_date` DateTimeField(default=now)
- [ ] `paid_at`, `shipped_at`, `delivered_at`, `cancelled_at` DateTimeField(null=True)
- [ ] `customer_notes` TextField(blank=True)
- [ ] `internal_notes` TextField(blank=True)
- [ ] `metadata` JSONField(default=dict)
- [ ] `created_by` FK to User (SET_NULL)
- [ ] Add status transition methods: `confirm()`, `ship()`, `deliver()`, `cancel()`
- [ ] Add `calculate_totals()` method
- [ ] Set `db_table = '"commerce"."orders"'`

---

#### [NEW] `backend/apps/commerce/models/order.py` (OrderItem class)

**Checklist**:
- [ ] [id](file:///home/project/singapore-smb/backend/core/middleware.py#74-94) UUID primary key
- [ ] `order` FK (CASCADE)
- [ ] `order_date` DateTimeField — for partitioning FK
- [ ] `product` FK to Product (PROTECT)
- [ ] `variant` FK to ProductVariant (SET_NULL)
- [ ] `sku` CharField(50) — snapshot
- [ ] [name](file:///home/project/singapore-smb/backend/apps/accounts/models.py#314-319) CharField(200) — snapshot
- [ ] `quantity` PositiveIntegerField
- [ ] `unit_price` DecimalField(10,2)
- [ ] `discount_amount` DecimalField(10,2, default=0)
- [ ] `gst_rate` DecimalField(5,4)
- [ ] `gst_amount` DecimalField(10,2)
- [ ] `gst_code` CharField(2)
- [ ] `line_total` DecimalField(10,2)
- [ ] `fulfilled_quantity` PositiveIntegerField(default=0)
- [ ] Add `@property is_fulfilled` (fulfilled_quantity >= quantity)
- [ ] Set `db_table = '"commerce"."order_items"'`

---

### 3.3 Serializers

#### [NEW] `backend/apps/commerce/serializers.py`

**Checklist**:
- [ ] `CategorySerializer` with nested parent (read_only)
- [ ] `CategoryTreeSerializer` with recursive children
- [ ] `ProductVariantSerializer` with effective_price
- [ ] `ProductListSerializer` (summary for lists)
- [ ] `ProductDetailSerializer` with variants, category nested
- [ ] `ProductCreateUpdateSerializer` with GST code validation
- [ ] `CustomerSerializer` with PDPA consent validation
- [ ] `CustomerAddressSerializer` with Singapore postal code validation (6 digits)
- [ ] `CartItemSerializer` with line_total
- [ ] `CartSerializer` with items nested, totals
- [ ] `OrderItemSerializer` with line calculations
- [ ] `OrderListSerializer` (summary)
- [ ] `OrderDetailSerializer` with items, addresses
- [ ] `OrderCreateSerializer` (from cart)
- [ ] All monetary fields use `DecimalField` serialization

---

### 3.4 Services

#### [NEW] `backend/apps/commerce/services/__init__.py`

**Checklist**:
- [ ] Export ProductService, OrderService, CartService

---

#### [NEW] `backend/apps/commerce/services/product_service.py`

**Features**:
- Product creation with variants
- Price calculation with GST
- Full-text search

**Checklist**:
- [ ] `create_product(company, data, variants=None)` — atomic creation
- [ ] `update_product(product, data)` — with variant sync
- [ ] `calculate_price_with_gst(product, quantity=1)` — returns subtotal, gst, total
- [ ] `search(company, query, filters=None)` — using SearchVector/SearchQuery
- [ ] `bulk_update_prices(product_ids, price_data)` — admin bulk action

---

#### [NEW] `backend/apps/commerce/services/cart_service.py`

**Features**:
- Add/remove items with stock check (Phase 3 integration point)
- Calculate totals with GST
- Guest cart merge on login
- Checkout to order

**Checklist**:
- [ ] `get_or_create_cart(company, customer=None, session_id=None)`
- [ ] `add_item(cart, product, variant=None, quantity=1)` — price snapshot
- [ ] `update_item_quantity(cart_item, quantity)` — with validation
- [ ] `remove_item(cart_item)`
- [ ] `calculate_totals(cart)` — returns subtotal, gst_amount, total
- [ ] `merge_guest_cart(guest_session_id, customer)` — on login
- [ ] `checkout(cart, shipping_address, billing_address, payment_method)` — create order
- [ ] `cleanup_expired_carts(company=None)` — soft delete expired

---

#### [NEW] `backend/apps/commerce/services/order_service.py`

**Features**:
- Order creation from cart
- Status transitions with validation
- GST calculation for F5 reporting
- Order number generation

**Checklist**:
- [ ] `create_from_cart(cart, shipping_address, billing_address)` — atomic
- [ ] `confirm(order)` — pending → confirmed, emit events
- [ ] [process(order)](file:///home/project/singapore-smb/backend/core/middleware.py#82-86) — confirmed → processing
- [ ] `ship(order, tracking_number, carrier)` — processing → shipped
- [ ] `deliver(order)` — shipped → delivered
- [ ] `cancel(order, reason)` — various → cancelled
- [ ] `refund(order, items=None)` — full/partial refund
- [ ] `calculate_gst_totals(order)` — populate box_1, box_6
- [ ] `generate_order_number(company)` — use core.sequences

---

### 3.5 Views

#### [NEW] `backend/apps/commerce/views.py`

**Checklist**:
- [ ] `CategoryViewSet` — CRUD, tree endpoint
- [ ] `ProductViewSet` — CRUD, search action, filter by category/status
- [ ] `CustomerViewSet` — CRUD, PDPA export action, address inline
- [ ] `CartViewSet` — get_or_create, add_item, remove_item, checkout actions
- [ ] `OrderViewSet` — CRUD, status transition actions, company-filtered
- [ ] All ViewSets use `IsAuthenticated` + [IsCompanyMember](file:///home/project/singapore-smb/backend/core/permissions.py#12-54) permissions
- [ ] Add pagination (default 20 items)
- [ ] Add filtering via django-filter

---

### 3.6 URLs

#### [NEW] `backend/apps/commerce/urls.py`

**Interfaces**:
```
GET/POST    /api/v1/commerce/categories/
GET/PUT/DEL /api/v1/commerce/categories/{id}/
GET         /api/v1/commerce/categories/tree/

GET/POST    /api/v1/commerce/products/
GET/PUT/DEL /api/v1/commerce/products/{id}/
GET         /api/v1/commerce/products/search/?q=...

GET/POST    /api/v1/commerce/customers/
GET/PUT/DEL /api/v1/commerce/customers/{id}/
GET         /api/v1/commerce/customers/{id}/addresses/

GET/POST    /api/v1/commerce/cart/
POST        /api/v1/commerce/cart/add_item/
POST        /api/v1/commerce/cart/remove_item/
POST        /api/v1/commerce/cart/checkout/

GET/POST    /api/v1/commerce/orders/
GET/PUT     /api/v1/commerce/orders/{id}/
POST        /api/v1/commerce/orders/{id}/confirm/
POST        /api/v1/commerce/orders/{id}/ship/
POST        /api/v1/commerce/orders/{id}/cancel/
```

**Checklist**:
- [ ] Register all ViewSets with DRF router
- [ ] Include in main [config/urls.py](file:///home/project/singapore-smb/backend/config/urls.py)

---

### 3.7 Admin

#### [NEW] `backend/apps/commerce/admin.py`

**Checklist**:
- [ ] `CategoryAdmin` — tree display, filters by company
- [ ] `ProductAdmin` — with ProductVariantInline, filters by status/category
- [ ] `CustomerAdmin` — with CustomerAddressInline, search by email/name
- [ ] `OrderAdmin` — with OrderItemInline, read-only totals, status filter
- [ ] `CartAdmin` — with CartItemInline, filter by status

---

### 3.8 Tasks

#### [NEW] `backend/apps/commerce/tasks.py`

**Checklist**:
- [ ] `send_order_confirmation(order_id)` — email to customer
- [ ] `cleanup_expired_carts()` — periodic, mark abandoned carts
- [ ] `sync_marketplace_orders(company_id)` — future integration point

---

### 3.9 Tests

#### [NEW] `backend/apps/commerce/tests/__init__.py`

Empty package.

---

#### [NEW] `backend/apps/commerce/tests/factories.py`

**Checklist**:
- [ ] `CategoryFactory`
- [ ] `ProductFactory` (with GST code defaults)
- [ ] `ProductVariantFactory`
- [ ] `CustomerFactory` (with PDPA defaults)
- [ ] `CustomerAddressFactory`
- [ ] `CartFactory` (with session_id for guest)
- [ ] `CartItemFactory`
- [ ] `OrderFactory`
- [ ] `OrderItemFactory`

---

#### [NEW] `backend/apps/commerce/tests/test_models.py`

**Checklist**:
- [ ] Test Category hierarchy (parent/child)
- [ ] Test Product GST calculation
- [ ] Test Product SKU uniqueness per company
- [ ] Test Customer email uniqueness per company
- [ ] Test Cart expiry logic
- [ ] Test Order status transitions (valid/invalid)
- [ ] Test OrderItem line_total calculation

---

#### [NEW] `backend/apps/commerce/tests/test_services.py`

**Checklist**:
- [ ] Test `CartService.add_item()` price snapshot
- [ ] Test `CartService.checkout()` creates order
- [ ] Test `CartService.merge_guest_cart()`
- [ ] Test `OrderService.create_from_cart()` totals
- [ ] Test `OrderService.confirm()` transition
- [ ] Test invalid status transitions raise error
- [ ] Test GST calculation accuracy (DECIMAL precision)

---

#### [NEW] `backend/apps/commerce/tests/test_views.py`

**Checklist**:
- [ ] Test product search endpoint
- [ ] Test category tree endpoint
- [ ] Test cart add/remove flow
- [ ] Test checkout creates order
- [ ] Test order status actions
- [ ] Test company isolation (cannot see other company's data)

---

### 3.10 Configuration Updates

#### [MODIFY] [backend/config/settings/base.py](file:///home/project/singapore-smb/backend/config/settings/base.py)

**Changes**:
- Add `'apps.commerce'` to `LOCAL_APPS`

---

#### [MODIFY] [backend/config/urls.py](file:///home/project/singapore-smb/backend/config/urls.py)

**Changes**:
- Include commerce URLs: `path('api/v1/commerce/', include('apps.commerce.urls'))`

---

#### [MODIFY] [backend/config/celery.py](file:///home/project/singapore-smb/backend/config/celery.py)

**Changes**:
- Celery beat schedule already conditional (Phase 1 remediation)
- Commerce tasks will be auto-discovered when app is created

---

## 4. Verification Plan

### 4.1 Automated Tests

**Commands**:
```bash
cd backend

# Run commerce tests only
uv run pytest apps/commerce/tests/ -v --tb=short

# Run with coverage
uv run pytest apps/commerce/tests/ -v --cov=apps.commerce --cov-report=term-missing

# Run all tests to ensure no regression
uv run pytest -q
```

**Expected Results**:
- All commerce tests pass
- Coverage > 80% for models and services
- No regressions in accounts tests (61 existing tests)

---

### 4.2 Manual Verification

**Step 1: Database Migration**
```bash
cd backend
source ../.env.docker  # or set -a && source ../.env.docker && set +a
uv run python manage.py makemigrations commerce
uv run python manage.py migrate
uv run python manage.py showmigrations commerce
```
✓ Migrations apply without error

**Step 2: Admin Interface**
1. Start server: `uv run python manage.py runserver`
2. Open: `http://localhost:8000/admin/`
3. Login with superuser
4. Navigate to Commerce section
5. Create a Category
6. Create a Product with GST code SR
7. Create a Customer with consent fields
8. Create an Order
✓ All models visible and editable in admin

**Step 3: API Endpoints (Swagger)**
1. Open: `http://localhost:8000/api/docs/`
2. Authenticate via login endpoint
3. Test endpoints:
   - `GET /api/v1/commerce/products/` — returns empty list
   - `POST /api/v1/commerce/products/` — create product
   - `GET /api/v1/commerce/products/search/?q=test` — search works
   - `GET /api/v1/commerce/cart/` — returns empty cart
   - `POST /api/v1/commerce/cart/add_item/` — adds item
✓ All endpoints respond correctly

**Step 4: GST Calculation Verification**
```python
# Django shell test
cd backend
uv run python manage.py shell

from decimal import Decimal
from apps.commerce.models import Product
from apps.commerce.services import ProductService

# Create test product
product = Product.objects.first()  # or create one
subtotal, gst, total = ProductService.calculate_price_with_gst(product, quantity=2)
print(f"Subtotal: {subtotal}, GST: {gst}, Total: {total}")
# Expected: GST = subtotal * 0.09 (rounded to 2 decimal places)
```
✓ GST calculation uses DECIMAL precision

---

## 5. File Summary

| Type | Count | Files |
|------|-------|-------|
| New Files | 23 | App config, models, serializers, services, views, admin, tasks, tests |
| Modified Files | 2 | [base.py](file:///home/project/singapore-smb/backend/config/settings/base.py), [urls.py](file:///home/project/singapore-smb/backend/config/urls.py) |
| **Total** | **25** | |

---

## 6. Dependencies

| Dependency | Reason | Status |
|------------|--------|--------|
| Phase 1 Accounts | Company model, User model, permissions | ✅ Complete |
| Phase 1 Core | BaseModel, SoftDeleteModel, CompanyOwnedModel | ✅ Complete |
| django-filter | API filtering | ✅ In pyproject.toml |
| django.contrib.postgres | SearchVector, SearchQuery for tsvector | ✅ Built-in |

---

## 7. Out of Scope (Future Phases)

- **Inventory reservation** on cart add (Phase 3)
- **Payment processing** on checkout (Phase 5)
- **Accounting entries** on order confirm (Phase 4)
- **PDPA data export** endpoint (Phase 5)
- **Marketplace sync** (Phase 5)

---

**Approval Required**: Please review and approve this plan before I proceed with execution.
