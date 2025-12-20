# Phase 6: Frontend Foundation — Final Sub-Plan

> **Duration**: Weeks 16-18  
> **Dependencies**: Phases 1-5 Complete (370 backend tests passing)  
> **Goal**: Next.js 14 project structure, component library, API client, and authentication

---

## Validated Findings

### Frontend Dependencies (package.json confirmed)
| Package | Version | Purpose |
|---------|---------|---------|
| `next` | 14.2.35 | App Router framework |
| `@tanstack/react-query` | 5.90.12 | Server state management |
| `axios` | 1.13.2 | HTTP client |
| `react-hook-form` | 7.68.0 | Form handling |
| `zod` | 4.2.1 | Schema validation |
| `@radix-ui/*` | Various | Unstyled UI primitives |
| `lucide-react` | 0.556.0 | Icons |
| `tailwindcss` | 4.1.17 | CSS framework |
| `clsx` + `tailwind-merge` | - | Class composition |

### Backend API Endpoints (validated)
```
/api/v1/accounts/      → users/, companies/, roles/, auth/
/api/v1/commerce/      → categories/, products/, customers/, cart/, orders/
/api/v1/inventory/     → locations/, items/, movements/, reservations/
/api/v1/accounting/    → accounts/, journals/, invoices/, payments/, gst/
/api/v1/compliance/    → consents/, access-requests/, gst-returns/, audit/
/api/v1/payments/      → webhooks/stripe/, webhooks/hitpay/
/api/v1/integrations/  → shipping/rates/, shipping/create/
/api/v1/invoicenow/    → invoices/, submit/
```

---

## Files to Create (36 files)

### 1. Configuration (5 files)

| File | Description |
|------|-------------|
| `next.config.js` | API proxy, image domains, env exposure |
| `tailwind.config.js` | Theme colors, fonts, content paths |
| `postcss.config.js` | Tailwind PostCSS plugin |
| `tsconfig.json` | Strict mode, path aliases |
| `.env.local.example` | Environment template |

---

### 2. Core App Structure (6 files)

| File | Description |
|------|-------------|
| `src/app/layout.tsx` | Root layout with providers |
| `src/app/page.tsx` | Homepage with hero + featured products |
| `src/app/globals.css` | Tailwind imports, CSS variables |
| `src/app/loading.tsx` | Global loading spinner |
| `src/app/error.tsx` | Error boundary |
| `src/middleware.ts` | Auth route protection |

---

### 3. API Layer (4 files)

#### `src/lib/api/client.ts`
```typescript
// Features:
// - Axios instance with baseURL from env
// - Request interceptor for JWT header
// - Response interceptor for 401 → refresh
// - Token storage in localStorage (httpOnly cookie in Phase 7)

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
});
```

#### `src/lib/api/endpoints.ts`
```typescript
// Typed API functions for each domain:
export const ProductsApi = {
  getAll: (params) => apiClient.get<PaginatedResponse<Product>>('/commerce/products/', { params }),
  getBySlug: (slug) => apiClient.get<Product>(`/commerce/products/${slug}/`),
};

export const CartApi = {
  getCurrent: () => apiClient.get<Cart>('/commerce/cart/current/'),
  addItem: (data) => apiClient.post('/commerce/cart/add_item/', data),
  removeItem: (itemId) => apiClient.delete(`/commerce/cart/items/${itemId}/`),
};

export const AuthApi = {
  login: (credentials) => apiClient.post('/accounts/auth/login/', credentials),
  logout: () => apiClient.post('/accounts/auth/logout/'),
  me: () => apiClient.get('/accounts/users/me/'),
};
```

#### `src/lib/api/queries.ts`
```typescript
// React Query hooks:
export const useProducts = (params) => useQuery({
  queryKey: ['products', params],
  queryFn: () => ProductsApi.getAll(params),
});

export const useCart = () => useQuery({
  queryKey: ['cart'],
  queryFn: CartApi.getCurrent,
  staleTime: 1000 * 60, // 1 minute
});
```

#### `src/lib/api/mutations.ts`
```typescript
// Mutations with cache invalidation:
export const useAddToCart = () => useMutation({
  mutationFn: CartApi.addItem,
  onSuccess: () => queryClient.invalidateQueries(['cart']),
});
```

---

### 4. Custom Hooks (4 files)

| File | Description |
|------|-------------|
| `src/lib/hooks/useAuth.ts` | `{ user, isAuthenticated, login, logout }` |
| `src/lib/hooks/useCart.ts` | `{ items, addItem, removeItem, totals }` |
| `src/lib/hooks/useDebounce.ts` | Debounce for search input |
| `src/lib/hooks/useMediaQuery.ts` | Responsive breakpoint detection |

---

### 5. UI Components (8 files)

| File | Variants | Features |
|------|----------|----------|
| `components/ui/button.tsx` | primary, secondary, outline, ghost | Loading state, disabled |
| `components/ui/input.tsx` | default, error | Label, error message, help text |
| `components/ui/card.tsx` | - | Header, Content, Footer subcomponents |
| `components/ui/badge.tsx` | default, success, warning, error | - |
| `components/ui/skeleton.tsx` | - | Animated loading placeholders |
| `components/ui/spinner.tsx` | sm, md, lg | SVG animation |
| `components/ui/toast.tsx` | success, error, info | Uses Radix Toast |
| `components/ui/index.ts` | - | Barrel export |

---

### 6. Layout Components (3 files)

#### `components/layout/header.tsx`
```typescript
// Features:
// - Logo → homepage link
// - Nav: Products, Categories
// - Search input (debounced)
// - Cart icon with item count badge
// - User dropdown (Login/Profile)
```

#### `components/layout/footer.tsx`
```typescript
// Sections:
// - Quick Links: About, Contact, Terms
// - Social: Facebook, Instagram, LinkedIn
// - Copyright © 2025
```

#### `components/layout/mobile-nav.tsx`
```typescript
// Uses Radix Dialog as drawer
// Full navigation + cart + user actions
```

---

### 7. Feature Components (5 files)

| File | Props | Features |
|------|-------|----------|
| `components/products/product-card.tsx` | `product: Product` | Image, title, price (GST-inclusive), add-to-cart |
| `components/products/product-grid.tsx` | `products[], isLoading` | Responsive grid, skeletons, empty state |
| `components/cart/cart-item.tsx` | `item: CartItem` | Thumbnail, qty controls, remove, line total |
| `components/cart/cart-summary.tsx` | `subtotal, gstAmount, total` | Formatted SGD, checkout CTA |
| `components/forms/login-form.tsx` | - | Email/password, Zod validation, error display |

---

### 8. Types (1 file)

#### `src/types/index.ts`
```typescript
// Core types matching backend serializers:

export interface Product {
  id: string;
  sku: string;
  name: string;
  slug: string;
  description: string;
  basePrice: string; // Decimal as string
  gstCode: 'SR' | 'ZR' | 'ES' | 'OS';
  gstRate: string;
  imageUrl: string;
  category: Category | null;
  variants: ProductVariant[];
  isActive: boolean;
}

export interface CartItem {
  id: string;
  product: Product;
  variant: ProductVariant | null;
  quantity: number;
  unitPrice: string;
  lineTotal: string;
}

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  company: { id: string; name: string; uen: string };
}

export interface ApiResponse<T> {
  status: 'success' | 'error';
  data: T;
  meta?: { pagination: Pagination };
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

---

## Verification Checklist

### Build Verification
```bash
cd frontend
npm install
npm run build      # ✅ No errors
npm run lint       # ✅ No warnings
npm run type-check # ✅ No TS errors
```

### Visual Verification
1. `npm run dev` → Homepage renders
2. Header with logo, nav, cart badge
3. Featured products grid
4. Footer with links
5. Responsive on mobile

### API Integration
1. Products load from backend
2. Login flow works
3. Add-to-cart updates badge

---

## Success Criteria

| Criteria | Target |
|----------|--------|
| Build passes | ✅ |
| TypeScript strict | ✅ |
| Homepage renders | ✅ |
| Auth flow works | ✅ |
| Cart updates work | ✅ |
| Mobile responsive | ✅ |
