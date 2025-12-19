# Phase 2: Commerce Domain Walkthrough

## Summary
Implemented the complete Commerce Domain for the Singapore SMB E-Commerce Platform, delivering product catalog, customer management, shopping cart, and order processing with full GST compliance.

## Files Created (25 total)

### App Structure
| File | Purpose |
|------|---------|
| [apps.py](file:///home/project/singapore-smb/backend/apps/commerce/apps.py) | Django app configuration |
| [__init__.py](file:///home/project/singapore-smb/backend/apps/commerce/__init__.py) | Package initializer |

### Models (9 models)
| Model | Key Features |
|-------|--------------|
| [Category](file:///home/project/singapore-smb/backend/apps/commerce/models/category.py#11-157) | Hierarchical (parent FK), SEO fields, company-scoped slug |
| [Product](file:///home/project/singapore-smb/backend/apps/commerce/models/product.py#35-296) | DECIMAL pricing, GST codes (SR/ZR/ES/OS), JSONB images/attributes |
| [ProductVariant](file:///home/project/singapore-smb/backend/apps/commerce/models/product.py#298-406) | Price adjustment, options JSONB |
| [Customer](file:///home/project/singapore-smb/backend/apps/commerce/models/customer.py#29-216) | PDPA consent fields, B2B (credit_limit, payment_terms, UEN) |
| [CustomerAddress](file:///home/project/singapore-smb/backend/apps/commerce/models/customer.py#218-364) | Singapore format (6-digit postal, unit_number) |
| [Cart](file:///home/project/singapore-smb/backend/apps/commerce/models/cart.py#32-187) | Guest/customer, 7-day expiry, status tracking |
| [CartItem](file:///home/project/singapore-smb/backend/apps/commerce/models/cart.py#189-301) | Price snapshot, quantity constraints |
| [Order](file:///home/project/singapore-smb/backend/apps/commerce/models/order.py#60-434) | Status state machine, GST F5 reporting (box_1, box_6) |
| [OrderItem](file:///home/project/singapore-smb/backend/apps/commerce/models/order.py#436-594) | Product snapshot, fulfillment tracking |

### Services (3 services)
| Service | Responsibilities |
|---------|-----------------|
| [ProductService](file:///home/project/singapore-smb/backend/apps/commerce/services/product_service.py#18-198) | Create, search (PostgreSQL FTS), GST calculation |
| [CartService](file:///home/project/singapore-smb/backend/apps/commerce/services/cart_service.py#23-334) | Add items, guest merge, checkout to order |
| [OrderService](file:///home/project/singapore-smb/backend/apps/commerce/services/order_service.py#19-282) | Status transitions, cancel, refund, GST reporting |

### API Layer
| File | Contents |
|------|----------|
| [serializers.py](file:///home/project/singapore-smb/backend/apps/commerce/serializers.py) | 14 serializers with GST/postal validation |
| [views.py](file:///home/project/singapore-smb/backend/apps/commerce/views.py) | 5 ViewSets with custom actions |
| [urls.py](file:///home/project/singapore-smb/backend/apps/commerce/urls.py) | Router with all endpoints |
| [admin.py](file:///home/project/singapore-smb/backend/apps/commerce/admin.py) | Full admin with inlines |

---

## Key Design Decisions

### 1. DECIMAL Financial Precision
All monetary fields use `DecimalField(max_digits=12, decimal_places=2)` matching PostgreSQL `DECIMAL(12,2)`.

### 2. GST Compliance
- GST codes: SR (Standard Rated), ZR (Zero Rated), ES (Exempt), OS (Out of Scope)
- GST rate: Configurable via `GST_DEFAULT_RATE` env variable
- F5 Reporting: `gst_box_1_amount` and `gst_box_6_amount` on orders

### 3. Order Status State Machine
```
pending → confirmed → processing → shipped → delivered
    ↓          ↓           ↓
  cancelled  cancelled  cancelled
```

### 4. Django 6.0 Compatibility
- `CheckConstraint` uses `condition=` instead of `check=`
- PostgreSQL schema creation via migration

---

## Verification Results

```
============================= 64 passed in 27.11s ==============================
```

| Test Category | Count | Status |
|---------------|-------|--------|
| Model tests | 30 | ✅ PASSED |
| Service tests | 17 | ✅ PASSED |
| View tests | 17 | ✅ PASSED |
| **Total** | **64** | ✅ **ALL PASSED** |

### Verified Features
- Category hierarchy and ancestor traversal
- Product GST calculation (SR, ZR codes)
- Customer credit limit and B2B detection
- Cart expiry and guest cart merge
- Order status transitions with validation
- Company isolation (multi-tenancy)

---

## API Endpoints

| Endpoint | Methods | Custom Actions |
|----------|---------|----------------|
| `/api/v1/commerce/categories/` | CRUD | [tree/](file:///home/project/singapore-smb/backend/apps/commerce/views.py#53-59) |
| `/api/v1/commerce/products/` | CRUD | [search/](file:///home/project/singapore-smb/backend/apps/commerce/services/product_service.py#119-167) |
| `/api/v1/commerce/customers/` | CRUD | [addresses/](file:///home/project/singapore-smb/backend/apps/commerce/views.py#123-129), [pdpa_export/](file:///home/project/singapore-smb/backend/apps/commerce/views.py#139-149) |
| `/api/v1/commerce/cart/` | - | [current/](file:///home/project/singapore-smb/backend/apps/commerce/views.py#181-187), [add_item/](file:///home/project/singapore-smb/backend/apps/commerce/views.py#188-214), [checkout/](file:///home/project/singapore-smb/backend/apps/commerce/views.py#239-273) |
| `/api/v1/commerce/orders/` | CRUD | [confirm/](file:///home/project/singapore-smb/backend/apps/commerce/services/order_service.py#53-70), [process/](file:///home/project/singapore-smb/backend/apps/commerce/views.py#305-314), [ship/](file:///home/project/singapore-smb/backend/apps/commerce/models/order.py#334-356), [deliver/](file:///home/project/singapore-smb/backend/apps/commerce/services/order_service.py#112-128), [cancel/](file:///home/project/singapore-smb/backend/apps/commerce/models/order.py#370-387) |

---

## Next Steps
Phase 3: Inventory Domain implementation (locations, items, reservations, movements).
