/**
 * useCart Hook
 * 
 * Shopping cart state and actions.
 * Provides convenient interface over React Query cart operations.
 */
'use client';

import { useMemo, useCallback } from 'react';
import { useCart as useCartQuery } from '@/lib/api/queries';
import { useAddToCart, useUpdateCartQuantity, useRemoveFromCart, useClearCart } from '@/lib/api/mutations';
import type { Cart, CartItem, AddToCartRequest } from '@/types';

export interface CartTotals {
    itemCount: number;
    subtotal: number;
    gstAmount: number;
    total: number;
}

export interface UseCartReturn {
    cart: Cart | null;
    items: CartItem[];
    totals: CartTotals;
    isLoading: boolean;
    isUpdating: boolean;
    error: Error | null;
    addItem: (data: AddToCartRequest) => Promise<void>;
    updateQuantity: (itemId: string, quantity: number) => Promise<void>;
    removeItem: (itemId: string) => Promise<void>;
    clearCart: () => Promise<void>;
}

const DEFAULT_TOTALS: CartTotals = {
    itemCount: 0,
    subtotal: 0,
    gstAmount: 0,
    total: 0,
};

export function useCart(): UseCartReturn {
    // Query
    const {
        data: cart,
        isLoading: isCartLoading,
        error: cartError,
    } = useCartQuery();

    // Mutations
    const addToCartMutation = useAddToCart();
    const updateQuantityMutation = useUpdateCartQuantity();
    const removeFromCartMutation = useRemoveFromCart();
    const clearCartMutation = useClearCart();

    // Derived state
    const items = useMemo(() => {
        return cart?.items ?? [];
    }, [cart]);

    const totals = useMemo((): CartTotals => {
        if (!cart) return DEFAULT_TOTALS;

        return {
            itemCount: cart.itemCount ?? items.reduce((sum, item) => sum + item.quantity, 0),
            subtotal: parseFloat(cart.subtotal || '0'),
            gstAmount: parseFloat(cart.gstAmount || '0'),
            total: parseFloat(cart.total || '0'),
        };
    }, [cart, items]);

    const isUpdating = useMemo(() => {
        return (
            addToCartMutation.isPending ||
            updateQuantityMutation.isPending ||
            removeFromCartMutation.isPending ||
            clearCartMutation.isPending
        );
    }, [
        addToCartMutation.isPending,
        updateQuantityMutation.isPending,
        removeFromCartMutation.isPending,
        clearCartMutation.isPending,
    ]);

    // Actions
    const addItem = useCallback(async (data: AddToCartRequest) => {
        await addToCartMutation.mutateAsync(data);
    }, [addToCartMutation]);

    const updateQuantity = useCallback(async (itemId: string, quantity: number) => {
        if (quantity < 1) {
            await removeFromCartMutation.mutateAsync(itemId);
        } else {
            await updateQuantityMutation.mutateAsync({ itemId, quantity });
        }
    }, [updateQuantityMutation, removeFromCartMutation]);

    const removeItem = useCallback(async (itemId: string) => {
        await removeFromCartMutation.mutateAsync(itemId);
    }, [removeFromCartMutation]);

    const clearCart = useCallback(async () => {
        await clearCartMutation.mutateAsync();
    }, [clearCartMutation]);

    return {
        cart: cart ?? null,
        items,
        totals,
        isLoading: isCartLoading,
        isUpdating,
        error: (cartError as Error) || addToCartMutation.error || updateQuantityMutation.error || removeFromCartMutation.error || null,
        addItem,
        updateQuantity,
        removeItem,
        clearCart,
    };
}

export default useCart;
