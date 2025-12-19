# Phase 3: Inventory Domain Implementation Plan

## Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | Weeks 7-9 |
| **Dependencies** | Phase 2 (Commerce Domain) |
| **Goal** | Inventory tracking, reservations with Redis locks, stock movements |

---

## Proposed Changes

### Inventory App Structure

#### [NEW] [__init__.py](file:///home/project/singapore-smb/backend/apps/inventory/__init__.py)
Empty package initializer.

#### [NEW] [apps.py](file:///home/project/singapore-smb/backend/apps/inventory/apps.py)
- [ ] Create `InventoryConfig` with name and verbose_name

---

### Models

#### [NEW] [models/location.py](file:///home/project/singapore-smb/backend/apps/inventory/models/location.py)

**Schema Reference**: `inventory.locations`

| Field | Type | Constraints |
|-------|------|-------------|
| `company_id` | FK → companies | NOT NULL |
| [code](file:///home/project/singapore-smb/backend/apps/commerce/serializers.py#169-176) | VARCHAR(20) | UNIQUE(company, code) |
| [name](file:///home/project/singapore-smb/backend/apps/accounts/models.py#314-319) | VARCHAR(100) | NOT NULL |
| `location_type` | VARCHAR(20) | `warehouse`, [store](file:///home/project/singapore-smb/backend/core/models.py#140-145), `virtual` |
| `address_line1/2` | VARCHAR(255) | Optional |
| [postal_code](file:///home/project/singapore-smb/backend/apps/commerce/serializers.py#200-207) | VARCHAR(6) | SG format |
| `is_active` | BOOLEAN | Default TRUE |
| `is_default` | BOOLEAN | Default FALSE |
| [settings](file:///home/project/singapore-smb/backend/apps/accounts/tests/test_models.py#64-71) | JSONB | Default {} |

**Checklist**:
- [ ] Create `Location` model inheriting from [SoftDeleteModel](file:///home/project/singapore-smb/backend/core/models.py#93-145)
- [ ] Add `LOCATION_TYPE_CHOICES` = warehouse, store, virtual
- [ ] Add company FK with `related_name='locations'`
- [ ] Add [code](file:///home/project/singapore-smb/backend/apps/commerce/serializers.py#169-176) field (unique per company)
- [ ] Add address fields (Singapore format)
- [ ] Add `is_active` and `is_default` flags
- [ ] Add [settings](file:///home/project/singapore-smb/backend/apps/accounts/tests/test_models.py#64-71) JSONField
- [ ] Define `db_table = '"inventory"."locations"'`
- [ ] Add [__str__](file:///home/project/singapore-smb/backend/apps/commerce/models/product.py#377-381) returning code - name

---

#### [NEW] [models/item.py](file:///home/project/singapore-smb/backend/apps/inventory/models/item.py)

**Schema Reference**: `inventory.items`

| Field | Type | Constraints |
|-------|------|-------------|
| `company_id` | FK | NOT NULL |
| `product_id` | FK → products | NOT NULL |
| `variant_id` | FK → variants | Optional |
| `location_id` | FK → locations | NOT NULL |
| `available_qty` | INTEGER | >= 0 |
| `reserved_qty` | INTEGER | >= 0, <= available_qty |
| `net_qty` | INTEGER | **GENERATED** (available - reserved) |
| `reorder_point` | INTEGER | Optional |
| `reorder_quantity` | INTEGER | Optional |
| `unit_cost` | DECIMAL(10,2) | Optional |
| `last_counted_at` | TIMESTAMPTZ | Optional |
| `last_movement_at` | TIMESTAMPTZ | Optional |
| [version](file:///home/project/singapore-smb/backend/.python-version) | INTEGER | Optimistic locking |

**Checklist**:
- [ ] Create `InventoryItem` model
- [ ] Add company, product, variant, location FKs
- [ ] Add `available_qty` with min=0 constraint
- [ ] Add `reserved_qty` with min=0 constraint
- [ ] Add `net_qty` as **property** (DB-generated, read-only in Django)
- [ ] Add `reorder_point` and `reorder_quantity`
- [ ] Add `unit_cost` DecimalField(10,2)
- [ ] Add `last_counted_at`, `last_movement_at` timestamps
- [ ] Add [version](file:///home/project/singapore-smb/backend/.python-version) for optimistic locking
- [ ] UNIQUE constraint: (product, variant, location)
- [ ] CheckConstraint: `reserved_qty <= available_qty`
- [ ] Define `db_table = '"inventory"."items"'`
- [ ] Add `is_low_stock` property checking against product.low_stock_threshold

---

#### [NEW] [models/reservation.py](file:///home/project/singapore-smb/backend/apps/inventory/models/reservation.py)

**Schema Reference**: `inventory.reservations`

| Field | Type | Constraints |
|-------|------|-------------|
| `inventory_item_id` | FK → items | NOT NULL |
| `order_id` | UUID | NOT NULL |
| [quantity](file:///home/project/singapore-smb/backend/apps/commerce/models/cart.py#287-301) | INTEGER | > 0 |
| [status](file:///home/project/singapore-smb/backend/apps/commerce/tests/test_models.py#278-286) | VARCHAR(20) | pending, confirmed, released, expired |
| `expires_at` | TIMESTAMPTZ | NOT NULL |
| `confirmed_at` | TIMESTAMPTZ | Optional |
| `released_at` | TIMESTAMPTZ | Optional |

**Checklist**:
- [ ] Create `InventoryReservation` model
- [ ] Add `inventory_item` FK with `related_name='reservations'`
- [ ] Add `order_id` UUIDField (FK created later when linking)
- [ ] Add [quantity](file:///home/project/singapore-smb/backend/apps/commerce/models/cart.py#287-301) PositiveIntegerField
- [ ] Add `RESERVATION_STATUS_CHOICES` = pending, confirmed, released, expired
- [ ] Add `expires_at` DateTimeField
- [ ] Add `confirmed_at`, `released_at` optional timestamps
- [ ] CheckConstraint: quantity > 0
- [ ] Define `db_table = '"inventory"."reservations"'`
- [ ] Add [is_expired](file:///home/project/singapore-smb/backend/apps/commerce/models/cart.py#121-125) property

---

#### [NEW] [models/movement.py](file:///home/project/singapore-smb/backend/apps/inventory/models/movement.py)

**Schema Reference**: `inventory.movements`

| Field | Type | Constraints |
|-------|------|-------------|
| `company_id` | FK | NOT NULL |
| `inventory_item_id` | FK → items | NOT NULL |
| `movement_type` | VARCHAR(30) | 8 types |
| [quantity](file:///home/project/singapore-smb/backend/apps/commerce/models/cart.py#287-301) | INTEGER | +/- for in/out |
| `quantity_before` | INTEGER | NOT NULL |
| `quantity_after` | INTEGER | NOT NULL |
| `reference_type` | VARCHAR(50) | Optional |
| `reference_id` | UUID | Optional |
| `notes` | TEXT | Optional |
| `created_by` | FK → users | Optional |

**Movement Types**:
- `purchase` - Stock received from supplier
- [sale](file:///home/project/singapore-smb/backend/apps/commerce/models/product.py#247-253) - Stock sold to customer
- [adjustment](file:///home/project/singapore-smb/backend/apps/commerce/tests/test_models.py#162-170) - Manual correction
- `transfer_in` - Received from another location
- `transfer_out` - Sent to another location
- [return](file:///home/project/singapore-smb/backend/apps/commerce/tests/test_views.py#214-221) - Customer return
- `damage` - Damaged/written off
- [count](file:///home/project/singapore-smb/backend/apps/commerce/models/cart.py#131-135) - Inventory count adjustment

**Checklist**:
- [ ] Create `InventoryMovement` model (NOT inheriting SoftDelete - audit log)
- [ ] Add company, inventory_item FKs
- [ ] Add `MOVEMENT_TYPE_CHOICES` (8 types)
- [ ] Add [quantity](file:///home/project/singapore-smb/backend/apps/commerce/models/cart.py#287-301) IntegerField (can be negative)
- [ ] Add `quantity_before`, `quantity_after` IntegerFields
- [ ] Add `reference_type`, `reference_id` for linking to orders/transfers
- [ ] Add `notes` TextField
- [ ] Add `created_by` FK to User
- [ ] Define `db_table = '"inventory"."movements"'`
- [ ] Make model read-only (no save() override, create via service)

---

#### [NEW] [models/__init__.py](file:///home/project/singapore-smb/backend/apps/inventory/models/__init__.py)
- [ ] Export Location, InventoryItem, InventoryReservation, InventoryMovement
- [ ] Export all choice constants

---

### Redis Locking

#### [NEW] [locks.py](file:///home/project/singapore-smb/backend/apps/inventory/locks.py)

**Purpose**: Distributed locking for inventory operations using Redis.

**Checklist**:
- [ ] Create `InventoryLock` class as context manager
- [ ] Use Django Redis cache backend
- [ ] Implement `acquire()` with configurable timeout (default: 10s)
- [ ] Implement `release()` with owner verification
- [ ] Add retry logic with exponential backoff
- [ ] Add `LockAcquisitionError` exception
- [ ] Add `LockTimeoutError` exception
- [ ] Lock key format: `inventory:lock:{item_id}`

---

### Services

#### [NEW] [services/__init__.py](file:///home/project/singapore-smb/backend/apps/inventory/services/__init__.py)
- [ ] Export InventoryService

#### [NEW] [services/inventory_service.py](file:///home/project/singapore-smb/backend/apps/inventory/services/inventory_service.py)

**Methods**:

| Method | Purpose | Uses Lock |
|--------|---------|-----------|
| `reserve_stock()` | Create reservation, decrement available | ✅ Redis lock |
| `confirm_reservation()` | Confirm pending reservation | ✅ |
| `release_reservation()` | Release and restore available | ✅ |
| `adjust_stock()` | Manual adjustment with movement log | ✅ |
| `transfer_stock()` | Transfer between locations | ✅ (both items) |
| `receive_stock()` | Add stock from purchase | ✅ |
| `record_sale()` | Decrement for sale | ✅ |
| `check_low_stock()` | Query items below threshold | ❌ |
| `get_stock_levels()` | Summary by product across locations | ❌ |

**Checklist**:
- [ ] Implement `reserve_stock(item_id, quantity, order_id, expires_minutes=15)`
  - [ ] Acquire Redis lock
  - [ ] Check available_qty - reserved_qty >= quantity
  - [ ] Update reserved_qty with optimistic lock (version check)
  - [ ] Create InventoryReservation with expires_at
  - [ ] Create InventoryMovement with type='sale'
  - [ ] Return reservation
- [ ] Implement `confirm_reservation(reservation_id)`
  - [ ] Acquire lock, update status to 'confirmed'
- [ ] Implement `release_reservation(reservation_id)`
  - [ ] Acquire lock, restore reserved_qty, update status
  - [ ] Create movement with type='return'
- [ ] Implement `adjust_stock(item_id, quantity_delta, notes, user)`
  - [ ] Acquire lock, update available_qty
  - [ ] Create movement with type='adjustment'
- [ ] Implement `transfer_stock(from_item_id, to_item_id, quantity, user)`
  - [ ] Acquire locks on both items
  - [ ] Decrement source, increment destination
  - [ ] Create transfer_out and transfer_in movements
- [ ] Implement `check_low_stock(company_id)` returning list of items
- [ ] Implement `get_stock_levels(product_id)` aggregated across locations

---

### API Layer

#### [NEW] [serializers.py](file:///home/project/singapore-smb/backend/apps/inventory/serializers.py)

**Checklist**:
- [ ] `LocationSerializer` - full CRUD
- [ ] `LocationListSerializer` - lightweight for lists
- [ ] `InventoryItemSerializer` - with computed net_qty, is_low_stock
- [ ] `InventoryItemDetailSerializer` - with location, product info
- [ ] `InventoryReservationSerializer` - read-only for admin
- [ ] `InventoryMovementSerializer` - read-only audit log
- [ ] `StockAdjustmentSerializer` - for adjust action (quantity, notes)
- [ ] `StockTransferSerializer` - for transfer action (from, to, quantity)
- [ ] `StockLevelSerializer` - aggregated view per product

---

#### [NEW] [views.py](file:///home/project/singapore-smb/backend/apps/inventory/views.py)

**Endpoints**:

| Endpoint | Methods | Custom Actions |
|----------|---------|----------------|
| `/locations/` | CRUD | - |
| `/items/` | List, Retrieve | [adjust/](file:///home/project/singapore-smb/backend/apps/commerce/tests/test_models.py#162-170), `low_stock/` |
| `/movements/` | List, Retrieve | - (read-only) |
| `/reservations/` | List | [cleanup/](file:///home/project/singapore-smb/backend/apps/commerce/services/cart_service.py#312-334) (admin) |

**Checklist**:
- [ ] `LocationViewSet` - standard CRUD with company filter
- [ ] `InventoryItemViewSet`
  - [ ] List with `location`, [product](file:///home/project/singapore-smb/backend/apps/commerce/services/product_service.py#58-84) filters
  - [ ] `@action adjust` - POST with quantity and notes
  - [ ] `@action low_stock` - GET items below threshold
  - [ ] `@action transfer` - POST to transfer between locations
- [ ] `InventoryMovementViewSet` - read-only, filterable by item/date
- [ ] `InventoryReservationViewSet` - read-only for admin

---

#### [NEW] [urls.py](file:///home/project/singapore-smb/backend/apps/inventory/urls.py)
- [ ] Register ViewSets with router
- [ ] app_name = 'inventory'

---

#### [MODIFY] [config/urls.py](file:///home/project/singapore-smb/backend/config/urls.py)
- [ ] Add [path('inventory/', include('apps.inventory.urls', namespace='inventory'))](file:///home/project/singapore-smb/backend/apps/commerce/models/category.py#131-142)

---

#### [MODIFY] [config/settings/base.py](file:///home/project/singapore-smb/backend/config/settings/base.py)
- [ ] Add `'apps.inventory'` to LOCAL_APPS

---

### Admin

#### [NEW] [admin.py](file:///home/project/singapore-smb/backend/apps/inventory/admin.py)

**Checklist**:
- [ ] `LocationAdmin` with list_display, search, filters
- [ ] `InventoryItemAdmin`
  - [ ] Inline for reservations
  - [ ] Display net_qty, is_low_stock with colored indicator
  - [ ] Filter by location, product type
- [ ] `InventoryMovementAdmin` (read-only)
  - [ ] Display quantity with +/- coloring
  - [ ] Filter by movement_type, date range
- [ ] `InventoryReservationAdmin` - status filter, expires_at display

---

### Celery Tasks

#### [NEW] [tasks.py](file:///home/project/singapore-smb/backend/apps/inventory/tasks.py)

**Checklist**:
- [ ] `cleanup_expired_reservations` - periodic task
  - [ ] Find reservations where expires_at < now AND status='pending'
  - [ ] Release each via InventoryService.release_reservation()
  - [ ] Return count of cleaned reservations
- [ ] `send_low_stock_alerts` - periodic task
  - [ ] Check items below reorder_point
  - [ ] Create notification (future: email/webhook)
- [ ] `sync_marketplace_inventory` - placeholder for Phase 5

---

### Tests

#### [NEW] [tests/__init__.py](file:///home/project/singapore-smb/backend/apps/inventory/tests/__init__.py)
Empty package.

#### [NEW] [tests/factories.py](file:///home/project/singapore-smb/backend/apps/inventory/tests/factories.py)
- [ ] `LocationFactory`
- [ ] `InventoryItemFactory`
- [ ] `InventoryReservationFactory`
- [ ] `InventoryMovementFactory`

#### [NEW] [tests/test_models.py](file:///home/project/singapore-smb/backend/apps/inventory/tests/test_models.py)
- [ ] Test Location CRUD and uniqueness
- [ ] Test InventoryItem net_qty property
- [ ] Test reserved_qty <= available_qty constraint
- [ ] Test optimistic locking with version
- [ ] Test Reservation status transitions
- [ ] Test Movement creation and audit

#### [NEW] [tests/test_services.py](file:///home/project/singapore-smb/backend/apps/inventory/tests/test_services.py)
- [ ] Test reserve_stock success
- [ ] Test reserve_stock insufficient stock
- [ ] Test reserve_stock concurrent (Redis lock)
- [ ] Test release_reservation restores qty
- [ ] Test adjust_stock with movement logging
- [ ] Test transfer_stock between locations
- [ ] Test check_low_stock returns correct items

#### [NEW] [tests/test_views.py](file:///home/project/singapore-smb/backend/apps/inventory/tests/test_views.py)
- [ ] Test Location CRUD
- [ ] Test InventoryItem list with filters
- [ ] Test adjust action
- [ ] Test low_stock action
- [ ] Test company isolation

#### [NEW] [tests/test_locks.py](file:///home/project/singapore-smb/backend/apps/inventory/tests/test_locks.py)
- [ ] Test lock acquisition and release
- [ ] Test lock timeout
- [ ] Test lock contention/retry

---

### Migrations

#### [NEW] [migrations/0001_create_schema.py](file:///home/project/singapore-smb/backend/apps/inventory/migrations/0001_create_schema.py)
- [ ] `CREATE SCHEMA IF NOT EXISTS inventory;`

#### [AUTO] [migrations/0002_models.py](file:///home/project/singapore-smb/backend/apps/inventory/migrations/0002_models.py)
- [ ] Auto-generated via `makemigrations`

---

## Summary

| Category | Files | New | Modified |
|----------|-------|-----|----------|
| App Structure | 2 | 2 | 0 |
| Models | 5 | 5 | 0 |
| Services | 2 | 2 | 0 |
| Locks | 1 | 1 | 0 |
| API Layer | 3 | 3 | 0 |
| Admin | 1 | 1 | 0 |
| Tasks | 1 | 1 | 0 |
| Tests | 5 | 5 | 0 |
| Migrations | 2 | 2 | 0 |
| Config | 2 | 0 | 2 |
| **Total** | **24** | **22** | **2** |

---

## Verification Plan

### Automated Tests
```bash
cd backend
uv run pytest apps/inventory/tests/ -v
```

### Concurrency Test
```python
# Test: 10 concurrent reservations for 5 available items
# Expected: Only 5 succeed, 5 raise InsufficientStockError
```

### Manual Verification
1. Create location via admin
2. Create inventory item linked to product
3. Test stock adjustment via API
4. Test reservation/release cycle
5. Verify movement audit trail

---

## Key Design Decisions

### 1. net_qty as Property (Not DB Field)
Django cannot write to PostgreSQL `GENERATED ALWAYS AS` columns. The `net_qty` is computed in the database but read as a property in Django.

### 2. Redis Locking Strategy
- Lock key: `inventory:lock:{item_id}`
- Timeout: 10 seconds default
- Retry: 3 attempts with 100ms backoff
- Owner: Random UUID to prevent accidental release

### 3. Optimistic Locking
The [version](file:///home/project/singapore-smb/backend/.python-version) field increments on every update. Service methods check version before update to detect concurrent modifications.

### 4. Movement Immutability
`InventoryMovement` records are append-only audit logs. No update or delete operations allowed.

---

# Phase 3: Inventory Domain Implementation

## Planning Phase
- [x] Review master_execution_plan.md Phase 3 section
- [x] Review VALIDATED_PROJECT_UNDERSTANDING.md for context
- [x] Review database/schema.sql for inventory tables
- [x] Create comprehensive implementation_plan.md
- [x] **User approval received**

## Execution Phase (Completed)

### App Structure
- [x] Create [apps/inventory/__init__.py](file:///home/project/singapore-smb/backend/apps/inventory/__init__.py)
- [x] Create [apps/inventory/apps.py](file:///home/project/singapore-smb/backend/apps/inventory/apps.py)
- [x] Add to INSTALLED_APPS
- [x] Add to main URLs

### Models (4)
- [x] [models/location.py](file:///home/project/singapore-smb/backend/apps/inventory/models/location.py) - Location with type choices
- [x] [models/item.py](file:///home/project/singapore-smb/backend/apps/inventory/models/item.py) - InventoryItem with net_qty, version
- [x] [models/reservation.py](file:///home/project/singapore-smb/backend/apps/inventory/models/reservation.py) - InventoryReservation with expiry
- [x] [models/movement.py](file:///home/project/singapore-smb/backend/apps/inventory/models/movement.py) - InventoryMovement audit log
- [x] [models/__init__.py](file:///home/project/singapore-smb/backend/apps/commerce/models/__init__.py) - Exports

### Services & Locks
- [x] [locks.py](file:///home/project/singapore-smb/backend/apps/inventory/locks.py) - Redis distributed locking (15s timeout)
- [x] [services/inventory_service.py](file:///home/project/singapore-smb/backend/apps/inventory/services/inventory_service.py) - All business logic

### API Layer
- [x] [serializers.py](file:///home/project/singapore-smb/backend/apps/commerce/serializers.py) - 10 serializers
- [x] [views.py](file:///home/project/singapore-smb/backend/apps/accounts/views.py) - 4 ViewSets with custom actions
- [x] [urls.py](file:///home/project/singapore-smb/backend/config/urls.py) - Router configuration
- [x] [admin.py](file:///home/project/singapore-smb/backend/apps/accounts/admin.py) - Admin for all models

### Tasks
- [x] [tasks.py](file:///home/project/singapore-smb/backend/apps/commerce/tasks.py) - Reservation cleanup, low stock alerts

### Tests
- [x] [tests/factories.py](file:///home/project/singapore-smb/backend/apps/accounts/tests/factories.py) - 6 factories
- [x] [tests/test_models.py](file:///home/project/singapore-smb/backend/apps/commerce/tests/test_models.py) - 17 tests
- [x] [tests/test_services.py](file:///home/project/singapore-smb/backend/apps/accounts/tests/test_services.py) - 17 tests
- [x] [tests/test_views.py](file:///home/project/singapore-smb/backend/apps/commerce/tests/test_views.py) - 12 tests
- [x] [tests/test_locks.py](file:///home/project/singapore-smb/backend/apps/inventory/tests/test_locks.py) - 11 tests

## Verification (Complete)
- [x] Django check passes (0 issues)
- [x] Migrations created (0001_create_schema.py, 0002_initial.py)
- [x] **57/57 tests PASSED**
