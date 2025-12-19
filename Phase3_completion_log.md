# Phase 3: Inventory Domain Walkthrough

## Summary
Implemented the complete Inventory Domain for the Singapore SMB E-Commerce Platform, delivering stock tracking, reservations with Redis distributed locking, and full movement audit trail.

## Files Created (24 total)

### App Structure
| File | Purpose |
|------|---------|
| [apps.py](file:///home/project/singapore-smb/backend/apps/inventory/apps.py) | Django app configuration |
| [__init__.py](file:///home/project/singapore-smb/backend/apps/inventory/__init__.py) | Package initializer |

### Models (4 models)
| Model | Key Features |
|-------|--------------|
| [Location](file:///home/project/singapore-smb/backend/apps/inventory/models/location.py#22-131) | Types (warehouse/store/virtual), Singapore address, unique code per company |
| [InventoryItem](file:///home/project/singapore-smb/backend/apps/inventory/models/item.py#18-195) | available_qty, reserved_qty, net_qty property, version for optimistic lock |
| [InventoryReservation](file:///home/project/singapore-smb/backend/apps/inventory/models/reservation.py#35-180) | 30-min configurable expiry, status lifecycle (pending→confirmed/released/expired) |
| [InventoryMovement](file:///home/project/singapore-smb/backend/apps/inventory/models/movement.py#26-185) | Immutable audit log, 8 movement types, before/after tracking |

### Redis Locking
| File | Purpose |
|------|---------|
| [locks.py](file:///home/project/singapore-smb/backend/apps/inventory/locks.py) | InventoryLock (15s timeout), MultiItemLock for transfers |

### Services
| File | Methods |
|------|---------|
| [inventory_service.py](file:///home/project/singapore-smb/backend/apps/inventory/services/inventory_service.py) | reserve_stock, release_reservation, adjust_stock, transfer_stock, receive_stock, check_low_stock, cleanup_expired_reservations |

### API Layer
| File | Contents |
|------|----------|
| [serializers.py](file:///home/project/singapore-smb/backend/apps/inventory/serializers.py) | 10 serializers with action serializers |
| [views.py](file:///home/project/singapore-smb/backend/apps/inventory/views.py) | 4 ViewSets with custom actions |
| [urls.py](file:///home/project/singapore-smb/backend/apps/inventory/urls.py) | Router with all endpoints |
| [admin.py](file:///home/project/singapore-smb/backend/apps/inventory/admin.py) | Admin with color-coded indicators |

---

## Key Design Decisions

### 1. Redis Distributed Locking
- **Timeout**: 15 seconds (user configured)
- **Retry**: 3 attempts with exponential backoff (100ms base)
- **Owner verification**: Prevents accidental release of other's locks
- **MultiItemLock**: Acquires locks in sorted order to prevent deadlocks

### 2. Reservation Expiry
- **Default**: 30 minutes (configurable via `INVENTORY_RESERVATION_EXPIRY_MINUTES`)
- **Cleanup**: Periodic Celery task expires pending reservations past expiry

### 3. Optimistic Locking
The [version](file:///home/project/singapore-smb/backend/.python-version) field increments on every update. Service methods check version to detect concurrent modifications.

### 4. Movement Immutability
[InventoryMovement](file:///home/project/singapore-smb/backend/apps/inventory/models/movement.py#26-185) records are append-only. [save()](file:///home/project/singapore-smb/backend/apps/inventory/models/reservation.py#122-128) raises error on updates to existing records.

---

## Verification Results

```
============================= 57 passed in 27.39s ==============================
```

| Test Category | Count | Status |
|---------------|-------|--------|
| Model tests | 17 | ✅ PASSED |
| Service tests | 17 | ✅ PASSED |
| View tests | 12 | ✅ PASSED |
| Lock tests | 11 | ✅ PASSED |
| **Total** | **57** | ✅ **ALL PASSED** |

---

## API Endpoints

| Endpoint | Methods | Custom Actions |
|----------|---------|----------------|
| `/api/v1/inventory/locations/` | CRUD | - |
| `/api/v1/inventory/items/` | CRUD | [adjust/](file:///home/project/singapore-smb/backend/apps/inventory/views.py#77-97), [transfer/](file:///home/project/singapore-smb/backend/apps/inventory/views.py#98-138), [receive/](file:///home/project/singapore-smb/backend/apps/inventory/views.py#139-157), [low_stock/](file:///home/project/singapore-smb/backend/apps/inventory/views.py#158-164), [stock_levels/](file:///home/project/singapore-smb/backend/apps/inventory/views.py#165-176) |
| `/api/v1/inventory/movements/` | List, Retrieve | - (read-only) |
| `/api/v1/inventory/reservations/` | List | [cleanup/](file:///home/project/singapore-smb/backend/apps/inventory/views.py#211-218) |

---

## Next Steps
Phase 4: Accounting Domain implementation (Chart of Accounts, Journal Entries, Invoices, GST Engine).
