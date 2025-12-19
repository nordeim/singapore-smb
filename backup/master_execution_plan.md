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

---

**Document Version**: 1.0
**Created**: December 18, 2025
**Author**: AI Coding Agent (Meticulous Approach Framework)
