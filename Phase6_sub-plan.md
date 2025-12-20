# Phase 6: Frontend Foundation — Implementation Plan

> **Duration**: Weeks 16-18  
> **Dependencies**: Phases 1-5 (Backend Complete, 370 tests passing)  
> **Goal**: Set up Next.js 14 project structure, component library, API client, and authentication

---

## Executive Summary

Phase 6 establishes the **frontend foundation** for the Singapore SMB E-Commerce Platform using:
- **Next.js 14.2+** with App Router
- **React Query 5** for server state management
- **Tailwind CSS 4** + Radix UI for styling
- **TypeScript 5** for type safety
- **react-hook-form + Zod** for form handling

---

## User Review Required

> [!IMPORTANT]
> **Design System**: This plan uses Radix UI primitives (already in package.json). Confirm this is the desired approach vs. a complete component library like shadcn/ui.

> [!NOTE]
> **PWA**: Full PWA configuration (service worker, manifest) is deferred to Phase 8.

---

## Files to Create (35 files)

### Category 1: Configuration & Setup (6 files)

#### [NEW] `frontend/next.config.js`
**Description**: Next.js configuration for API rewrites, images, and environment.

**Features**:
- API proxy to backend (`/api/*` → `http://localhost:8000/api/*`)
- Image domains allowlist (CDN, placeholders)
- Environment variable exposure

**Interfaces**: N/A (build config)

**Checklist**:
- [ ] Configure `rewrites()` for API proxy in development
- [ ] Set `images.remotePatterns` for product images
- [ ] Add `env` section for public environment variables
- [ ] Configure `experimental.serverActions` if needed

---

#### [NEW] `frontend/tailwind.config.js`
**Description**: Tailwind CSS configuration with Singapore-appropriate theme.

**Features**:
- Custom color palette (primary, secondary, accent)
- Typography configuration
- Component-friendly spacing

**Interfaces**: N/A (build config)

**Checklist**:
- [ ] Define color palette with CSS variables
- [ ] Configure Inter font family
- [ ] Set content paths for purging
- [ ] Add custom animations for loading states

---

#### [NEW] `frontend/postcss.config.js`
**Description**: PostCSS configuration for Tailwind.

**Checklist**:
- [ ] Configure `@tailwindcss/postcss` plugin

---

#### [NEW] `frontend/tsconfig.json`
**Description**: TypeScript configuration.

**Checklist**:
- [ ] Set `"strict": true`
- [ ] Configure path aliases (`@/` → `src/`)
- [ ] Set target to ES2022

---

#### [NEW] `frontend/.env.local.example`
**Description**: Environment variable template.

**Checklist**:
- [ ] Add `NEXT_PUBLIC_API_URL`
- [ ] Add `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`

---

#### [NEW] `frontend/src/middleware.ts`
**Description**: Next.js middleware for auth protection.

**Features**:
- Protect `/account/*` routes
- Redirect unauthenticated users to login

**Interfaces**: Next.js middleware API

**Checklist**:
- [ ] Check for auth token in cookies
- [ ] Redirect to `/login` if missing on protected routes
- [ ] Allow public routes (`/`, `/products/*`, `/login`, `/register`)

---

### Category 2: Core App Structure (5 files)

#### [NEW] `frontend/src/app/layout.tsx`
**Description**: Root layout with providers and global structure.

**Features**:
- HTML metadata (title, description)
- Font loading (Inter from Google Fonts)
- Global providers (QueryClient, AuthProvider)

**Interfaces**:
- Wraps all pages with `<body>` and providers

**Checklist**:
- [ ] Set `<html lang="en">`
- [ ] Load Inter font via `next/font/google`
- [ ] Wrap children with `<QueryClientProvider>`
- [ ] Wrap with `<AuthProvider>`
- [ ] Include `<Header>` and `<Footer>`

---

#### [NEW] `frontend/src/app/page.tsx`
**Description**: Homepage with hero and featured products.

**Features**:
- Hero section with CTA
- Featured products grid (SSR fetch)
- Category navigation cards

**Interfaces**:
- Uses `ProductCard` and `ProductGrid` components
- Fetches from `/api/v1/commerce/products/?featured=true`

**Checklist**:
- [ ] Create responsive hero section
- [ ] Fetch featured products server-side
- [ ] Display 4-8 featured products
- [ ] Add category quick-links
- [ ] SEO metadata via `generateMetadata`

---

#### [NEW] `frontend/src/app/globals.css`
**Description**: Global styles and Tailwind imports.

**Checklist**:
- [ ] Import `@tailwind base`, `components`, `utilities`
- [ ] Define CSS variables for colors
- [ ] Add focus-visible styles for accessibility
- [ ] Add smooth scrolling

---

#### [NEW] `frontend/src/app/loading.tsx`
**Description**: Global loading state.

**Checklist**:
- [ ] Create loading spinner component
- [ ] Center vertically and horizontally

---

#### [NEW] `frontend/src/app/error.tsx`
**Description**: Global error boundary.

**Checklist**:
- [ ] Display error message
- [ ] Add "Try Again" button with `reset()`

---

### Category 3: API Layer (4 files)

#### [NEW] `frontend/src/lib/api/client.ts`
**Description**: Axios instance with JWT handling.

**Features**:
- Base URL from environment
- Request interceptor for Authorization header
- Response interceptor for 401 → token refresh

**Interfaces**:
- Exports `apiClient` axios instance
- Exports `setAuthToken(token)` and `clearAuthToken()`

**Checklist**:
- [ ] Create axios instance with `baseURL`
- [ ] Add request interceptor to attach Bearer token
- [ ] Add response interceptor for 401 handling
- [ ] Implement silent token refresh
- [ ] Handle network errors gracefully

---

#### [NEW] `frontend/src/lib/api/endpoints.ts`
**Description**: Typed API endpoint functions.

**Features**:
- Products: `getProducts()`, `getProductBySlug()`
- Cart: `getCurrentCart()`, `addToCart()`, `removeFromCart()`
- Auth: `login()`, `logout()`, `register()`
- Orders: `createOrder()`, `getOrders()`

**Interfaces**:
- All functions return typed `Promise<ApiResponse<T>>`

**Checklist**:
- [ ] Create `ProductsApi` namespace
- [ ] Create `CartApi` namespace
- [ ] Create `AuthApi` namespace
- [ ] Create `OrdersApi` namespace
- [ ] Add pagination support for list endpoints

---

#### [NEW] `frontend/src/lib/api/queries.ts`
**Description**: React Query hooks for data fetching.

**Features**:
- `useProducts()` with filters
- `useProduct(slug)` for detail
- `useCart()` for current cart
- `useUser()` for current user

**Interfaces**:
- Returns React Query `UseQueryResult`

**Checklist**:
- [ ] Create `useProducts` query with staleTime
- [ ] Create `useProduct` query with slug key
- [ ] Create `useCart` query with refetch on window focus
- [ ] Create `useUser` query with retry: false

---

#### [NEW] `frontend/src/lib/api/mutations.ts`
**Description**: React Query mutation hooks.

**Features**:
- `useAddToCart()` with optimistic update
- `useRemoveFromCart()`
- `useLogin()` with redirect
- `useCreateOrder()`

**Interfaces**:
- Returns React Query `UseMutationResult`

**Checklist**:
- [ ] Create `useAddToCart` with cache invalidation
- [ ] Create `useRemoveFromCart` with optimistic UI
- [ ] Create `useLogin` with token storage
- [ ] Create `useLogout` with cache clear

---

### Category 4: Custom Hooks (4 files)

#### [NEW] `frontend/src/lib/hooks/useAuth.ts`
**Description**: Authentication state and actions.

**Features**:
- Current user state
- Login/logout functions
- Token management
- Auth status check

**Interfaces**:
- Returns `{ user, isAuthenticated, login, logout, isLoading }`

**Checklist**:
- [ ] Use React Query for user state
- [ ] Store token in httpOnly cookie (preferred) or localStorage
- [ ] Implement `login(email, password)` mutation
- [ ] Implement `logout()` with token blacklist API call
- [ ] Redirect after login/logout

---

#### [NEW] `frontend/src/lib/hooks/useCart.ts`
**Description**: Shopping cart state and actions.

**Features**:
- Cart items with quantities
- Add/remove/update functions
- Cart totals (subtotal, GST, total)

**Interfaces**:
- Returns `{ items, addItem, removeItem, updateQuantity, totals, isLoading }`

**Checklist**:
- [ ] Fetch cart from API
- [ ] Optimistic updates for better UX
- [ ] Calculate GST (9%) on frontend for display
- [ ] Sync guest cart on login

---

#### [NEW] `frontend/src/lib/hooks/useDebounce.ts`
**Description**: Debounce hook for search input.

**Checklist**:
- [ ] Implement generic debounce with configurable delay

---

#### [NEW] `frontend/src/lib/hooks/useMediaQuery.ts`
**Description**: Responsive breakpoint hook.

**Checklist**:
- [ ] Implement SSR-safe media query hook
- [ ] Support Tailwind breakpoints (sm, md, lg, xl)

---

### Category 5: UI Components (8 files)

#### [NEW] `frontend/src/components/ui/button.tsx`
**Description**: Button component with variants.

**Features**:
- Variants: `primary`, `secondary`, `outline`, `ghost`, `destructive`
- Sizes: `sm`, `md`, `lg`
- Loading state with spinner
- Disabled state

**Interfaces**:
- Props: `variant`, `size`, `loading`, `disabled`, `children`

**Checklist**:
- [ ] Create with Radix Slot for polymorphism
- [ ] Style with Tailwind + cva (class-variance-authority)
- [ ] Add loading spinner
- [ ] Add focus ring for accessibility

---

#### [NEW] `frontend/src/components/ui/input.tsx`
**Description**: Input component with validation states.

**Features**:
- Label integration
- Error state with message
- Help text

**Interfaces**:
- Props: `label`, `error`, `helpText`, standard input props

**Checklist**:
- [ ] Forward ref for react-hook-form
- [ ] Style error state with red border
- [ ] Display error message below input

---

#### [NEW] `frontend/src/components/ui/card.tsx`
**Description**: Card container component.

**Checklist**:
- [ ] Create `Card`, `CardHeader`, `CardTitle`, `CardContent`, `CardFooter`
- [ ] Style with shadow and border

---

#### [NEW] `frontend/src/components/ui/badge.tsx`
**Description**: Badge/tag component.

**Checklist**:
- [ ] Create with variants: `default`, `success`, `warning`, `error`

---

#### [NEW] `frontend/src/components/ui/skeleton.tsx`
**Description**: Loading skeleton component.

**Checklist**:
- [ ] Create animated pulse skeleton
- [ ] Create preset shapes: `SkeletonCard`, `SkeletonText`

---

#### [NEW] `frontend/src/components/ui/spinner.tsx`
**Description**: Loading spinner component.

**Checklist**:
- [ ] Create SVG spinner with animation
- [ ] Size variants

---

#### [NEW] `frontend/src/components/ui/toast.tsx`
**Description**: Toast notification component.

**Features**:
- Success, error, info variants
- Auto-dismiss with configurable duration

**Checklist**:
- [ ] Use Radix Toast primitive
- [ ] Create `ToastProvider` and `useToast` hook

---

#### [NEW] `frontend/src/components/ui/index.ts`
**Description**: Barrel export for UI components.

**Checklist**:
- [ ] Export all UI components

---

### Category 6: Layout Components (3 files)

#### [NEW] `frontend/src/components/layout/header.tsx`
**Description**: Site header with navigation.

**Features**:
- Logo with link to homepage
- Navigation links (Products, Categories)
- Search input
- Cart icon with badge
- User menu (login/profile)

**Interfaces**:
- Uses `useCart` for item count
- Uses `useAuth` for user state

**Checklist**:
- [ ] Create responsive header with mobile menu
- [ ] Display cart item count badge
- [ ] Show user dropdown when authenticated
- [ ] Show login/register when not authenticated
- [ ] Sticky header on scroll

---

#### [NEW] `frontend/src/components/layout/footer.tsx`
**Description**: Site footer.

**Features**:
- Quick links (About, Contact, Terms)
- Social media links
- Copyright

**Checklist**:
- [ ] Create multi-column footer layout
- [ ] Add link sections
- [ ] Add copyright with current year

---

#### [NEW] `frontend/src/components/layout/mobile-nav.tsx`
**Description**: Mobile navigation drawer.

**Checklist**:
- [ ] Use Radix Dialog for drawer
- [ ] Include all navigation items
- [ ] Include cart and user actions

---

### Category 7: Feature Components (5 files)

#### [NEW] `frontend/src/components/products/product-card.tsx`
**Description**: Product card for grid display.

**Features**:
- Product image with fallback
- Title, price (GST-inclusive)
- Quick add-to-cart button

**Interfaces**:
- Props: `product: Product`
- Emits: `onAddToCart`

**Checklist**:
- [ ] Display product image with aspect ratio
- [ ] Show price with "incl. GST" label
- [ ] Add hover effect
- [ ] Quick add-to-cart button

---

#### [NEW] `frontend/src/components/products/product-grid.tsx`
**Description**: Responsive product grid.

**Features**:
- Responsive columns (1 → 2 → 3 → 4)
- Loading skeletons
- Empty state

**Interfaces**:
- Props: `products: Product[]`, `isLoading: boolean`

**Checklist**:
- [ ] Create CSS Grid with responsive columns
- [ ] Show skeletons when loading
- [ ] Show "No products found" when empty

---

#### [NEW] `frontend/src/components/cart/cart-item.tsx`
**Description**: Cart item row component.

**Features**:
- Product thumbnail
- Name and variant
- Quantity controls
- Remove button
- Line total

**Interfaces**:
- Props: `item: CartItem`

**Checklist**:
- [ ] Display product info
- [ ] Quantity +/- buttons
- [ ] Remove button with confirmation
- [ ] Show line total

---

#### [NEW] `frontend/src/components/cart/cart-summary.tsx`
**Description**: Cart totals summary.

**Features**:
- Subtotal
- GST amount (9%)
- Total

**Interfaces**:
- Props: `subtotal`, `gstAmount`, `total`

**Checklist**:
- [ ] Display formatted currency (SGD)
- [ ] Show GST breakdown
- [ ] Checkout button

---

#### [NEW] `frontend/src/components/forms/login-form.tsx`
**Description**: Login form component.

**Features**:
- Email and password fields
- Form validation with Zod
- Submit with loading state
- Error display

**Interfaces**:
- Uses `react-hook-form` with Zod resolver

**Checklist**:
- [ ] Create form with email/password
- [ ] Validate with Zod schema
- [ ] Show server errors
- [ ] Loading state on submit
- [ ] Link to register page

---

### Category 8: Types (1 file)

#### [NEW] `frontend/src/types/index.ts`
**Description**: Shared TypeScript type definitions.

**Interfaces**:
```typescript
interface Product {
  id: string;
  sku: string;
  name: string;
  slug: string;
  description: string;
  basePrice: number;
  gstCode: 'SR' | 'ZR' | 'ES' | 'OS';
  gstRate: number;
  imageUrl: string;
  category: Category;
  variants: ProductVariant[];
}

interface CartItem {
  id: string;
  product: Product;
  variant?: ProductVariant;
  quantity: number;
  unitPrice: number;
  lineTotal: number;
}

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  company: Company;
}
```

**Checklist**:
- [ ] Define `Product` type matching backend serializer
- [ ] Define `ProductVariant` type
- [ ] Define `Category` type
- [ ] Define `CartItem` type
- [ ] Define `Order` type
- [ ] Define `User` type
- [ ] Define `ApiResponse<T>` wrapper type
- [ ] Define `PaginatedResponse<T>` type

---

## Verification Plan

### Build Verification
```bash
cd frontend
npm install
npm run build
npm run lint
npm run type-check
```

### Visual Verification
1. Start dev server: `npm run dev`
2. Verify homepage renders with header/footer
3. Test responsive breakpoints
4. Verify all UI components render correctly

### API Integration Test
1. Ensure backend is running
2. Test product fetch on homepage
3. Test login flow
4. Test add-to-cart

---

## File Summary

| Category | Files | Purpose |
|----------|-------|---------|
| Config/Setup | 6 | Next.js, Tailwind, TypeScript, Middleware |
| Core Pages | 5 | Layout, Homepage, Loading, Error |
| API Layer | 4 | Client, Endpoints, Queries, Mutations |
| Hooks | 4 | Auth, Cart, Debounce, MediaQuery |
| UI Components | 8 | Button, Input, Card, Badge, Skeleton, etc. |
| Layout | 3 | Header, Footer, Mobile Nav |
| Features | 5 | Product Card/Grid, Cart Item/Summary, Login |
| Types | 1 | TypeScript definitions |
| **Total** | **36** | |

---

## Success Criteria

1. ✅ `npm run build` completes without errors
2. ✅ `npm run type-check` passes
3. ✅ Homepage displays with header, hero, footer
4. ✅ All UI components render correctly
5. ✅ API client connects to backend
6. ✅ Auth flow (login/logout) works
7. ✅ Cart add/remove works
