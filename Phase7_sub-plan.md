# Phase 7: Frontend Features — Implementation Plan

> **Duration**: Weeks 19-22  
> **Dependencies**: Phase 6 (Frontend Foundation Complete)  
> **Goal**: Implement storefront, cart, checkout, and user dashboard

---

## Executive Summary

Phase 7 delivers the **complete e-commerce user journey**:
1. Product browsing with filters/search
2. Cart management
3. Checkout with Stripe + PayNow
4. User account dashboard

---

## Validated Against

| Document | Validation Points |
|----------|-------------------|
| **schema.sql** | Orders, cart_items, customer_addresses structure |
| **AGENT.md** | Server Components, React Query, Stripe CSP integration |
| **Project Architecture** | GST calculations, PDPA consent requirements |

---

## Files to Create (22 files)

### Category 1: Product Pages (3 files)

#### [NEW] `frontend/src/app/products/page.tsx`
**Description**: Product listing page with filters and search.

**Features**:
- Product grid with pagination
- Category filter sidebar
- Search with debounce
- Sort options (price, newest)
- URL query params for sharing

**Interfaces**:
- Uses `useProducts()` query with filters
- Server Component with client filter controls

**Checklist**:
- [ ] Fetch products server-side for SEO
- [ ] Implement CategoryFilter component
- [ ] Add search input with debounce
- [ ] URL-based filtering (`?category=X&search=Y`)
- [ ] Pagination with page numbers
- [ ] Sort dropdown (price asc/desc, newest)

---

#### [NEW] `frontend/src/app/products/[slug]/page.tsx`
**Description**: Product detail page with variants.

**Features**:
- Image gallery with thumbnails
- Variant selection (color, size)
- Dynamic pricing based on variant
- Add to cart with quantity
- Related products section

**Interfaces**:
- Server Component for initial data
- Uses `useAddToCart()` mutation

**Checklist**:
- [ ] Fetch product by slug (SSR)
- [ ] Image gallery with lightbox
- [ ] Variant selector with stock check
- [ ] Quantity input with +/- buttons
- [ ] Add to cart button with feedback
- [ ] Related products grid (4 items)
- [ ] SEO metadata via `generateMetadata`

---

#### [NEW] `frontend/src/app/categories/[slug]/page.tsx`
**Description**: Category-specific product listing.

**Checklist**:
- [ ] Fetch category by slug
- [ ] Display category banner/description
- [ ] Filter products by category
- [ ] Breadcrumb navigation

---

### Category 2: Cart & Checkout Pages (5 files)

#### [NEW] `frontend/src/app/cart/page.tsx`
**Description**: Shopping cart page.

**Features**:
- Cart items list
- Quantity update
- Remove items
- Cart summary with GST breakdown
- Checkout CTA

**Interfaces**:
- Uses `useCart()` hook
- CartItem and CartSummary components

**Checklist**:
- [ ] Display cart items with images
- [ ] Quantity controls (+/-)
- [ ] Remove item button
- [ ] Live subtotal, GST (9%), total
- [ ] Empty cart state
- [ ] Continue shopping link
- [ ] Proceed to checkout button

---

#### [NEW] `frontend/src/app/checkout/page.tsx`
**Description**: Multi-step checkout flow.

**Features**:
- Shipping address form
- Payment method selection
- Order review
- Place order

**Interfaces**:
- Protected route (requires auth)
- Uses AddressForm, PaymentForm, OrderSummary components

**Checklist**:
- [ ] Redirect if cart empty
- [ ] Step indicator (Address → Payment → Review)
- [ ] Address form with validation
- [ ] Payment method selection (Stripe/PayNow)
- [ ] Order summary sidebar
- [ ] Place order with loading state
- [ ] Error handling for payment failures

---

#### [NEW] `frontend/src/app/checkout/success/page.tsx`
**Description**: Order confirmation page.

**Checklist**:
- [ ] Display order number
- [ ] Show order details summary
- [ ] Email confirmation message
- [ ] Continue shopping button
- [ ] View order link

---

#### [NEW] `frontend/src/app/checkout/layout.tsx`
**Description**: Checkout-specific layout (minimal header).

**Checklist**:
- [ ] Simplified header (logo only)
- [ ] Hide footer for focus
- [ ] Cart lock indication

---

#### [NEW] `frontend/src/app/cart/loading.tsx`
**Description**: Cart page loading state.

**Checklist**:
- [ ] Skeleton for cart items

---

### Category 3: Account Pages (5 files)

#### [NEW] `frontend/src/app/account/page.tsx`
**Description**: User account dashboard.

**Features**:
- Welcome message
- Recent orders (3)
- Quick links

**Checklist**:
- [ ] Display user name/email
- [ ] Recent orders list
- [ ] Links to orders, settings
- [ ] Logout button

---

#### [NEW] `frontend/src/app/account/orders/page.tsx`
**Description**: Order history page.

**Checklist**:
- [ ] List all orders with pagination
- [ ] Order status badges
- [ ] Order date and total
- [ ] Link to order detail

---

#### [NEW] `frontend/src/app/account/orders/[id]/page.tsx`
**Description**: Single order detail page.

**Checklist**:
- [ ] Order items with images
- [ ] Order totals (subtotal, GST, shipping, total)
- [ ] Shipping address
- [ ] Tracking info (if shipped)
- [ ] Download invoice button

---

#### [NEW] `frontend/src/app/account/settings/page.tsx`
**Description**: Account settings page.

**Checklist**:
- [ ] Edit profile form
- [ ] Change password
- [ ] PDPA consent management

---

#### [NEW] `frontend/src/app/account/layout.tsx`
**Description**: Account section layout with sidebar.

**Checklist**:
- [ ] Sidebar navigation
- [ ] Active link highlighting

---

### Category 4: Auth Pages (2 files)

#### [NEW] `frontend/src/app/login/page.tsx`
**Description**: Login page using LoginForm component.

**Checklist**:
- [ ] Centered card layout
- [ ] Use LoginForm from Phase 6
- [ ] Handle redirect query param

---

#### [NEW] `frontend/src/app/register/page.tsx`
**Description**: Registration page.

**Features**:
- Registration form
- PDPA consent checkboxes
- Email verification notice

**Checklist**:
- [ ] Name, email, password fields
- [ ] Phone number field
- [ ] PDPA marketing consent checkbox
- [ ] Terms acceptance checkbox
- [ ] Registration success redirect

---

### Category 5: Checkout Components (4 files)

#### [NEW] `frontend/src/components/checkout/address-form.tsx`
**Description**: Shipping address form with Singapore validation.

**Features**:
- Singapore postal code validation (6 digits)
- Unit number field
- Address autocomplete ready

**Interfaces**:
- Props: `onSubmit`, `defaultValues`
- Uses react-hook-form + Zod

**Checklist**:
- [ ] Recipient name field
- [ ] Phone number field
- [ ] Address line 1 (required)
- [ ] Address line 2 (optional)
- [ ] Postal code (6 digits, SG validation)
- [ ] Unit number field
- [ ] Save as default checkbox

---

#### [NEW] `frontend/src/components/checkout/payment-form.tsx`
**Description**: Payment method selection with Stripe Elements.

**Features**:
- Stripe card input
- PayNow QR option
- Payment method tabs

**Interfaces**:
- Uses `@stripe/react-stripe-js`
- Props: `clientSecret`, `onPaymentComplete`

**Checklist**:
- [ ] Load Stripe.js with publishable key
- [ ] CardElement for card payments
- [ ] PayNow tab with QR code
- [ ] Payment method toggle
- [ ] Loading state during processing
- [ ] Error display for failures

---

#### [NEW] `frontend/src/components/checkout/order-summary.tsx`
**Description**: Checkout order summary panel.

**Checklist**:
- [ ] Line items with thumbnails
- [ ] Subtotal
- [ ] Shipping cost
- [ ] GST amount (9%)
- [ ] Total
- [ ] SGD currency formatting

---

#### [NEW] `frontend/src/components/checkout/paynow-qr.tsx`
**Description**: PayNow QR code generator.

**Features**:
- QR code display
- Payment reference
- Expiry countdown

**Checklist**:
- [ ] Generate QR from payment intent
- [ ] Display payment reference
- [ ] Countdown timer (15 min)
- [ ] Polling for payment status

---

### Category 6: Shared Components (3 files)

#### [NEW] `frontend/src/components/products/image-gallery.tsx`
**Description**: Product image gallery with thumbnails.

**Checklist**:
- [ ] Main image display
- [ ] Thumbnail navigation
- [ ] Lightbox on click
- [ ] Swipe support on mobile

---

#### [NEW] `frontend/src/components/products/variant-selector.tsx`
**Description**: Product variant selection UI.

**Checklist**:
- [ ] Option buttons (color, size)
- [ ] Selected state styling
- [ ] Stock availability check
- [ ] Price update on selection

---

#### [NEW] `frontend/src/components/shared/pagination.tsx`
**Description**: Reusable pagination component.

**Checklist**:
- [ ] Page numbers
- [ ] Prev/Next buttons
- [ ] Current page indicator
- [ ] Total pages display

---

## Dependencies to Install

```bash
npm install @stripe/stripe-js @stripe/react-stripe-js qrcode.react
```

---

## Verification Plan

### Build Verification
```bash
cd frontend
npm run build
npm run lint
npm run type-check
```

### E2E Tests
1. Browse products, filter by category
2. Add to cart, update quantity
3. Complete checkout with Stripe test card
4. View order in account dashboard

### PayNow Test
1. Generate PayNow QR
2. Verify polling for payment status

---

## File Summary

| Category | Files | Key Features |
|----------|-------|--------------|
| Product Pages | 3 | Listing, Detail, Category |
| Cart & Checkout | 5 | Cart, Checkout flow, Success |
| Account | 5 | Dashboard, Orders, Settings |
| Auth | 2 | Login, Register |
| Checkout Components | 4 | Address, Payment, PayNow QR |
| Shared | 3 | Gallery, Variants, Pagination |
| **Total** | **22** | |

---

## Success Criteria

1. ✅ Product browsing with filters works
2. ✅ Cart add/remove/update works
3. ✅ Stripe checkout completes
4. ✅ PayNow QR generates
5. ✅ Order appears in account
6. ✅ All pages render correctly
7. ✅ Mobile responsive
