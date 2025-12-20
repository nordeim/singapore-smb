# Phase 7: Frontend Features — Final Implementation Plan

> **Duration**: Weeks 19-22  
> **Dependencies**: Phase 6 (Frontend Foundation Complete — 37 files)  
> **Goal**: Complete e-commerce user journey: browsing, cart, checkout, account

---

## Validation Summary

| Source | Validation Points |
|--------|-------------------|
| **commerce/views.py** | ✅ CartViewSet: `current`, `add_item`, `update_item`, `remove_item`, `checkout` |
| **commerce/views.py** | ✅ OrderViewSet: `confirm`, `process`, `ship`, `deliver`, `cancel` |
| **payments/urls.py** | ✅ `create-intent`, `methods`, `status/<order_id>` endpoints |
| **schema.sql** | ✅ customer_addresses with SG postal_code (6 chars), unit_number |
| **AGENT.md** | ✅ Stripe CSP configuration, Server Components pattern |
| **Phase 6 endpoints.ts** | ✅ ProductsApi, CategoriesApi, CartApi, OrdersApi, AuthApi exist |

### Phase 6 Components Reusable:
- `cart/cart-item.tsx`, `cart/cart-summary.tsx` — reuse in cart page
- `products/product-card.tsx`, `product-grid.tsx` — reuse in listings
- `forms/login-form.tsx` — reuse in login page

---

## Files to Create (25 files)

### 1. API Layer Updates (2 files)

#### [MODIFY] `frontend/src/lib/api/endpoints.ts`
**Description**: Add PaymentsApi for Stripe integration.

**Changes**:
```typescript
export const PaymentsApi = {
  createIntent: (orderId: string) => apiClient.post('/payments/create-intent/', { order_id: orderId }),
  getStatus: (orderId: string) => apiClient.get(`/payments/status/${orderId}/`),
  getMethods: () => apiClient.get('/payments/methods/'),
};
```

**Checklist**:
- [ ] Add PaymentsApi with createIntent, getStatus, getMethods
- [ ] Add PaymentIntent type to types/index.ts

---

#### [MODIFY] `frontend/src/types/index.ts`
**Description**: Add payment-related types.

**Changes**:
```typescript
export interface PaymentIntent {
  id: string;
  clientSecret: string;
  amount: number;
  currency: string;
  status: 'pending' | 'succeeded' | 'failed';
}

export interface Address {
  id?: string;
  recipientName: string;
  phone: string;
  addressLine1: string;
  addressLine2?: string;
  postalCode: string;
  unitNumber?: string;
  isDefault?: boolean;
}
```

**Checklist**:
- [ ] Add PaymentIntent interface
- [ ] Add Address interface with Singapore fields

---

### 2. Product Pages (3 files)

#### [NEW] `frontend/src/app/products/page.tsx`
**Description**: Product listing with filters, search, pagination.

**Features**:
- Server Component for initial data (SEO)
- Client-side filtering via URL params
- Uses ProductGrid from Phase 6

**Interfaces**:
```typescript
// URL params: ?category=<slug>&search=<query>&page=<n>&sort=<field>
```

**Checklist**:
- [ ] Server-side data fetch with searchParams
- [ ] CategoryFilter sidebar component
- [ ] Search input with useDebounce
- [ ] Pagination component
- [ ] Sort dropdown (price, newest)
- [ ] Empty state for no results

---

#### [NEW] `frontend/src/app/products/[slug]/page.tsx`
**Description**: Product detail with variants and add-to-cart.

**Features**:
- generateMetadata for SEO
- Image gallery
- Variant selector
- Quantity controls

**Checklist**:
- [ ] Fetch product by slug (SSR)
- [ ] ImageGallery component
- [ ] VariantSelector component
- [ ] Quantity input with min/max
- [ ] Add to cart with toast feedback
- [ ] Related products (4 items)
- [ ] Breadcrumb navigation

---

#### [NEW] `frontend/src/app/products/loading.tsx`
**Description**: Loading skeleton for products page.

**Checklist**:
- [ ] Grid of SkeletonCard components

---

### 3. Cart Page (2 files)

#### [NEW] `frontend/src/app/cart/page.tsx`
**Description**: Shopping cart with items and summary.

**Features**:
- Reuses CartItem and CartSummary from Phase 6
- Protected route (middleware)

**Checklist**:
- [ ] Display cart items with CartItem component
- [ ] CartSummary with checkout CTA
- [ ] Empty cart state with "Continue Shopping" link
- [ ] Update URL: `/cart`

---

#### [NEW] `frontend/src/app/cart/layout.tsx`
**Description**: Cart section layout.

**Checklist**:
- [ ] Standard layout with header/footer

---

### 4. Checkout Flow (4 files)

#### [NEW] `frontend/src/app/checkout/page.tsx`
**Description**: Multi-step checkout: Address → Payment → Review.

**Features**:
- Step indicator
- Address form
- Payment method selection
- Order summary

**Checklist**:
- [ ] Redirect if cart empty
- [ ] Step navigation (Address, Payment, Review)
- [ ] AddressForm component
- [ ] PaymentForm component
- [ ] OrderSummary sidebar
- [ ] Place order button with loading
- [ ] Error handling

---

#### [NEW] `frontend/src/app/checkout/success/page.tsx`
**Description**: Order confirmation after successful checkout.

**Checklist**:
- [ ] Display order number
- [ ] Order summary
- [ ] Email confirmation notice
- [ ] "View Order" and "Continue Shopping" buttons

---

#### [NEW] `frontend/src/app/checkout/layout.tsx`
**Description**: Minimal checkout layout (logo only, no footer).

**Checklist**:
- [ ] Logo header only
- [ ] No footer
- [ ] Cart item count indicator

---

#### [NEW] `frontend/src/app/checkout/loading.tsx`
**Description**: Checkout loading state.

---

### 5. Account Pages (5 files)

#### [NEW] `frontend/src/app/account/page.tsx`
**Description**: Account dashboard with recent orders.

**Checklist**:
- [ ] Welcome message with user name
- [ ] Recent orders (3 items)
- [ ] Quick links: Orders, Settings
- [ ] Logout button

---

#### [NEW] `frontend/src/app/account/orders/page.tsx`
**Description**: Order history with pagination.

**Checklist**:
- [ ] Order list with status badges
- [ ] Pagination
- [ ] Link to order detail

---

#### [NEW] `frontend/src/app/account/orders/[id]/page.tsx`
**Description**: Single order detail.

**Checklist**:
- [ ] Order items with images
- [ ] Order totals (subtotal, GST, shipping, total)
- [ ] Shipping address
- [ ] Tracking info (if shipped)
- [ ] Download invoice link

---

#### [NEW] `frontend/src/app/account/layout.tsx`
**Description**: Account sidebar layout.

**Checklist**:
- [ ] Sidebar navigation (Dashboard, Orders, Settings)
- [ ] Active link highlighting

---

#### [NEW] `frontend/src/app/account/loading.tsx`
**Description**: Account loading skeleton.

---

### 6. Auth Pages (2 files)

#### [NEW] `frontend/src/app/login/page.tsx`
**Description**: Login page using LoginForm from Phase 6.

**Checklist**:
- [ ] Centered card layout
- [ ] Use LoginForm component
- [ ] Handle redirect query param

---

#### [NEW] `frontend/src/app/register/page.tsx`
**Description**: Registration with PDPA consent.

**Checklist**:
- [ ] Name, email, password, phone fields
- [ ] PDPA marketing consent checkbox
- [ ] Terms acceptance checkbox
- [ ] Registration success redirect

---

### 7. Checkout Components (4 files)

#### [NEW] `frontend/src/components/checkout/address-form.tsx`
**Description**: Shipping address with Singapore validation.

**Validation (Zod)**:
```typescript
const addressSchema = z.object({
  recipientName: z.string().min(1, 'Name is required'),
  phone: z.string().regex(/^\+?65\d{8}$/, 'Invalid SG phone'),
  addressLine1: z.string().min(1, 'Address is required'),
  addressLine2: z.string().optional(),
  postalCode: z.string().regex(/^\d{6}$/, 'Must be 6 digits'),
  unitNumber: z.string().optional(),
});
```

**Checklist**:
- [ ] Form fields with react-hook-form
- [ ] Zod validation schema
- [ ] Singapore postal code validation (6 digits)
- [ ] Save as default checkbox

---

#### [NEW] `frontend/src/components/checkout/payment-form.tsx`
**Description**: Stripe Elements + PayNow tabs.

**Features**:
- Card payment via Stripe
- PayNow QR alternative

**Checklist**:
- [ ] Stripe CardElement
- [ ] PayNow tab with QR
- [ ] Payment method toggle
- [ ] Loading state during processing
- [ ] Error display

---

#### [NEW] `frontend/src/components/checkout/paynow-qr.tsx`
**Description**: PayNow QR code with countdown.

**Checklist**:
- [ ] QR code generation (qrcode.react)
- [ ] Payment reference display
- [ ] 15-minute countdown timer
- [ ] Polling for payment confirmation

---

#### [NEW] `frontend/src/components/checkout/checkout-summary.tsx`
**Description**: Order summary for checkout sidebar.

**Checklist**:
- [ ] Line items with thumbnails
- [ ] Subtotal, shipping, GST, total
- [ ] SGD formatting

---

### 8. Shared Components (3 files)

#### [NEW] `frontend/src/components/products/image-gallery.tsx`
**Description**: Product image gallery with thumbnails.

**Checklist**:
- [ ] Main image display
- [ ] Thumbnail navigation
- [ ] Click to enlarge (lightbox)

---

#### [NEW] `frontend/src/components/products/variant-selector.tsx`
**Description**: Option selector (color, size).

**Checklist**:
- [ ] Button group per option
- [ ] Selected state styling
- [ ] Disabled if out of stock
- [ ] Price update on selection

---

#### [NEW] `frontend/src/components/shared/pagination.tsx`
**Description**: Reusable pagination.

**Checklist**:
- [ ] Page numbers with ellipsis
- [ ] Prev/Next arrows
- [ ] Current page indicator

---

## Dependencies to Install

```bash
npm install @stripe/stripe-js @stripe/react-stripe-js qrcode.react
```

---

## File Summary

| Category | Files | Description |
|----------|-------|-------------|
| API Updates | 2 | PaymentsApi, types |
| Product Pages | 3 | Listing, Detail, Loading |
| Cart | 2 | Page, Layout |
| Checkout | 4 | Page, Success, Layout, Loading |
| Account | 5 | Dashboard, Orders, Order Detail, Layout, Loading |
| Auth | 2 | Login, Register |
| Checkout Components | 4 | Address, Payment, PayNow QR, Summary |
| Shared | 3 | Gallery, Variants, Pagination |
| **Total** | **25** | |

---

## Verification Plan

```bash
# Build checks
cd frontend
npm install @stripe/stripe-js @stripe/react-stripe-js qrcode.react
npm run type-check
npm run build
```

### Manual Tests:
1. Browse `/products` → filter, search, paginate
2. View `/products/[slug]` → select variant, add to cart
3. View `/cart` → update quantity, remove item
4. Complete `/checkout` → address, Stripe test card
5. View `/checkout/success` → order confirmation
6. View `/account/orders/[id]` → order detail

---

## Success Criteria

| Criteria | Validation |
|----------|------------|
| Product listing works | Filter, search, pagination |
| Cart operations work | Add, update, remove |
| Stripe checkout works | Test card 4242... succeeds |
| PayNow QR displays | QR renders, polls status |
| Account pages work | Orders listed, details shown |
| Build passes | No TS errors, no build errors |
| Mobile responsive | All pages work on mobile |

---

# Phase 7: Frontend Features — Task Tracker

## Status: ⏳ PENDING APPROVAL

---

## 1. API Layer Updates (2 files)
- [ ] `frontend/src/lib/api/endpoints.ts` — Add PaymentsApi
- [ ] `frontend/src/types/index.ts` — Add PaymentIntent, Address types

## 2. Product Pages (3 files)
- [ ] `frontend/src/app/products/page.tsx`
- [ ] `frontend/src/app/products/[slug]/page.tsx`
- [ ] `frontend/src/app/products/loading.tsx`

## 3. Cart (2 files)
- [ ] `frontend/src/app/cart/page.tsx`
- [ ] `frontend/src/app/cart/layout.tsx`

## 4. Checkout Flow (4 files)
- [ ] `frontend/src/app/checkout/page.tsx`
- [ ] `frontend/src/app/checkout/success/page.tsx`
- [ ] `frontend/src/app/checkout/layout.tsx`
- [ ] `frontend/src/app/checkout/loading.tsx`

## 5. Account Pages (5 files)
- [ ] `frontend/src/app/account/page.tsx`
- [ ] `frontend/src/app/account/orders/page.tsx`
- [ ] `frontend/src/app/account/orders/[id]/page.tsx`
- [ ] `frontend/src/app/account/layout.tsx`
- [ ] `frontend/src/app/account/loading.tsx`

## 6. Auth Pages (2 files)
- [ ] `frontend/src/app/login/page.tsx`
- [ ] `frontend/src/app/register/page.tsx`

## 7. Checkout Components (4 files)
- [ ] `frontend/src/components/checkout/address-form.tsx`
- [ ] `frontend/src/components/checkout/payment-form.tsx`
- [ ] `frontend/src/components/checkout/paynow-qr.tsx`
- [ ] `frontend/src/components/checkout/checkout-summary.tsx`

## 8. Shared Components (3 files)
- [ ] `frontend/src/components/products/image-gallery.tsx`
- [ ] `frontend/src/components/products/variant-selector.tsx`
- [ ] `frontend/src/components/shared/pagination.tsx`

---

## New Dependencies
- [ ] `@stripe/stripe-js`
- [ ] `@stripe/react-stripe-js`
- [ ] `qrcode.react`

---

## Verification
- [ ] `npm run type-check` passes
- [ ] `npm run build` passes
- [ ] Product listing works
- [ ] Cart operations work
- [ ] Stripe checkout works
- [ ] Account pages work
