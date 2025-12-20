/**
 * React Query Mutation Hooks
 * 
 * Mutations with cache invalidation and optimistic updates.
 */
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { CartApi, OrdersApi, AuthApi } from './endpoints';
import { queryKeys } from './queries';
import { setAuthToken, setRefreshToken, clearAuthTokens } from './client';
import type { Cart, Order, LoginCredentials, RegisterData, AddToCartRequest } from '@/types';

// ============================================================================
// Cart Mutations
// ============================================================================

/**
 * Add item to cart
 */
export function useAddToCart() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: AddToCartRequest) => CartApi.addItem(data),
        onSuccess: (newCart: Cart) => {
            // Update cart cache with new data
            queryClient.setQueryData(queryKeys.cart, newCart);
        },
        onError: () => {
            // Refetch cart on error to ensure consistency
            queryClient.invalidateQueries({ queryKey: queryKeys.cart });
        },
    });
}

/**
 * Update cart item quantity
 */
export function useUpdateCartQuantity() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ itemId, quantity }: { itemId: string; quantity: number }) =>
            CartApi.updateQuantity(itemId, quantity),
        onMutate: async ({ itemId, quantity }) => {
            // Cancel outgoing refetches
            await queryClient.cancelQueries({ queryKey: queryKeys.cart });

            // Snapshot previous value
            const previousCart = queryClient.getQueryData<Cart>(queryKeys.cart);

            // Optimistically update
            if (previousCart) {
                const newCart = {
                    ...previousCart,
                    items: previousCart.items.map((item) =>
                        item.id === itemId ? { ...item, quantity } : item
                    ),
                };
                queryClient.setQueryData(queryKeys.cart, newCart);
            }

            return { previousCart };
        },
        onError: (_err, _vars, context) => {
            // Rollback on error
            if (context?.previousCart) {
                queryClient.setQueryData(queryKeys.cart, context.previousCart);
            }
        },
        onSettled: () => {
            // Refetch to ensure consistency
            queryClient.invalidateQueries({ queryKey: queryKeys.cart });
        },
    });
}

/**
 * Remove item from cart
 */
export function useRemoveFromCart() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (itemId: string) => CartApi.removeItem(itemId),
        onMutate: async (itemId) => {
            await queryClient.cancelQueries({ queryKey: queryKeys.cart });

            const previousCart = queryClient.getQueryData<Cart>(queryKeys.cart);

            if (previousCart) {
                const newCart = {
                    ...previousCart,
                    items: previousCart.items.filter((item) => item.id !== itemId),
                };
                queryClient.setQueryData(queryKeys.cart, newCart);
            }

            return { previousCart };
        },
        onError: (_err, _vars, context) => {
            if (context?.previousCart) {
                queryClient.setQueryData(queryKeys.cart, context.previousCart);
            }
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.cart });
        },
    });
}

/**
 * Clear entire cart
 */
export function useClearCart() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: CartApi.clear,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.cart });
        },
    });
}

/**
 * Checkout cart to create order
 */
export function useCheckout() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: CartApi.checkout,
        onSuccess: (order: Order) => {
            // Clear cart cache
            queryClient.invalidateQueries({ queryKey: queryKeys.cart });
            // Add new order to cache
            queryClient.setQueryData(queryKeys.orderDetail(order.id), order);
            // Invalidate orders list
            queryClient.invalidateQueries({ queryKey: queryKeys.orders });
        },
    });
}

// ============================================================================
// Order Mutations
// ============================================================================

/**
 * Cancel an order
 */
export function useCancelOrder() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
            OrdersApi.cancel(id, reason),
        onSuccess: (updatedOrder: Order) => {
            // Update order in cache
            queryClient.setQueryData(queryKeys.orderDetail(updatedOrder.id), updatedOrder);
            // Invalidate orders list
            queryClient.invalidateQueries({ queryKey: queryKeys.orders });
        },
    });
}

// ============================================================================
// Auth Mutations
// ============================================================================

/**
 * Login mutation
 */
export function useLogin() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (credentials: LoginCredentials) => AuthApi.login(credentials),
        onSuccess: (data) => {
            // Store tokens
            setAuthToken(data.access);
            setRefreshToken(data.refresh);
            // Update user cache
            queryClient.setQueryData(queryKeys.user, data.user);
            // Invalidate cart (might merge guest cart)
            queryClient.invalidateQueries({ queryKey: queryKeys.cart });
        },
    });
}

/**
 * Logout mutation
 */
export function useLogout() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: AuthApi.logout,
        onSuccess: () => {
            // Clear tokens
            clearAuthTokens();
            // Clear all cached data
            queryClient.clear();
        },
        onError: () => {
            // Clear tokens anyway on error
            clearAuthTokens();
            queryClient.clear();
        },
    });
}

/**
 * Register mutation
 */
export function useRegister() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: RegisterData) => AuthApi.register(data),
        onSuccess: (data) => {
            // Store tokens
            setAuthToken(data.access);
            setRefreshToken(data.refresh);
            // Update user cache
            queryClient.setQueryData(queryKeys.user, data.user);
        },
    });
}
