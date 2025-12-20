/**
 * React Query Hooks for Data Fetching
 * 
 * Query hooks with proper caching and stale time configuration.
 */
import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { ProductsApi, CategoriesApi, CartApi, OrdersApi, AuthApi } from './endpoints';
import type { Product, Category, Cart, Order, User, PaginatedResponse, ProductFilters, OrderFilters } from '@/types';

// ============================================================================
// Query Keys
// ============================================================================

export const queryKeys = {
    // Products
    products: ['products'] as const,
    productsList: (filters?: ProductFilters) => [...queryKeys.products, 'list', filters] as const,
    productDetail: (slug: string) => [...queryKeys.products, 'detail', slug] as const,
    productsFeatured: ['products', 'featured'] as const,

    // Categories
    categories: ['categories'] as const,
    categoriesTree: ['categories', 'tree'] as const,
    categoryDetail: (slug: string) => ['categories', 'detail', slug] as const,

    // Cart
    cart: ['cart'] as const,

    // Orders
    orders: ['orders'] as const,
    ordersList: (filters?: OrderFilters) => [...queryKeys.orders, 'list', filters] as const,
    orderDetail: (id: string) => [...queryKeys.orders, 'detail', id] as const,

    // User
    user: ['user'] as const,
};

// ============================================================================
// Product Queries
// ============================================================================

/**
 * Fetch paginated products with optional filters
 */
export function useProducts(
    filters?: ProductFilters,
    options?: Omit<UseQueryOptions<PaginatedResponse<Product>>, 'queryKey' | 'queryFn'>
) {
    return useQuery({
        queryKey: queryKeys.productsList(filters),
        queryFn: () => ProductsApi.getAll(filters),
        staleTime: 2 * 60 * 1000, // 2 minutes
        ...options,
    });
}

/**
 * Fetch single product by slug
 */
export function useProduct(
    slug: string,
    options?: Omit<UseQueryOptions<Product>, 'queryKey' | 'queryFn'>
) {
    return useQuery({
        queryKey: queryKeys.productDetail(slug),
        queryFn: () => ProductsApi.getBySlug(slug),
        staleTime: 5 * 60 * 1000, // 5 minutes
        enabled: !!slug,
        ...options,
    });
}

/**
 * Fetch featured products for homepage
 */
export function useFeaturedProducts(
    limit: number = 8,
    options?: Omit<UseQueryOptions<Product[]>, 'queryKey' | 'queryFn'>
) {
    return useQuery({
        queryKey: queryKeys.productsFeatured,
        queryFn: () => ProductsApi.getFeatured(limit),
        staleTime: 5 * 60 * 1000, // 5 minutes
        ...options,
    });
}

// ============================================================================
// Category Queries
// ============================================================================

/**
 * Fetch all categories
 */
export function useCategories(
    options?: Omit<UseQueryOptions<Category[]>, 'queryKey' | 'queryFn'>
) {
    return useQuery({
        queryKey: queryKeys.categories,
        queryFn: CategoriesApi.getAll,
        staleTime: 10 * 60 * 1000, // 10 minutes (categories change rarely)
        ...options,
    });
}

/**
 * Fetch category tree structure
 */
export function useCategoryTree(
    options?: Omit<UseQueryOptions<Category[]>, 'queryKey' | 'queryFn'>
) {
    return useQuery({
        queryKey: queryKeys.categoriesTree,
        queryFn: CategoriesApi.getTree,
        staleTime: 10 * 60 * 1000, // 10 minutes
        ...options,
    });
}

// ============================================================================
// Cart Queries
// ============================================================================

/**
 * Fetch current user's cart
 */
export function useCart(
    options?: Omit<UseQueryOptions<Cart>, 'queryKey' | 'queryFn'>
) {
    return useQuery({
        queryKey: queryKeys.cart,
        queryFn: CartApi.getCurrent,
        staleTime: 30 * 1000, // 30 seconds (cart changes frequently)
        refetchOnWindowFocus: true,
        ...options,
    });
}

// ============================================================================
// Order Queries
// ============================================================================

/**
 * Fetch user's orders with optional filters
 */
export function useOrders(
    filters?: OrderFilters,
    options?: Omit<UseQueryOptions<PaginatedResponse<Order>>, 'queryKey' | 'queryFn'>
) {
    return useQuery({
        queryKey: queryKeys.ordersList(filters),
        queryFn: () => OrdersApi.getAll(filters),
        staleTime: 60 * 1000, // 1 minute
        ...options,
    });
}

/**
 * Fetch single order by ID
 */
export function useOrder(
    id: string,
    options?: Omit<UseQueryOptions<Order>, 'queryKey' | 'queryFn'>
) {
    return useQuery({
        queryKey: queryKeys.orderDetail(id),
        queryFn: () => OrdersApi.getById(id),
        staleTime: 60 * 1000, // 1 minute
        enabled: !!id,
        ...options,
    });
}

// ============================================================================
// User Queries
// ============================================================================

/**
 * Fetch current user profile
 */
export function useUser(
    options?: Omit<UseQueryOptions<User>, 'queryKey' | 'queryFn'>
) {
    return useQuery({
        queryKey: queryKeys.user,
        queryFn: AuthApi.me,
        staleTime: 5 * 60 * 1000, // 5 minutes
        retry: false, // Don't retry on 401
        ...options,
    });
}
