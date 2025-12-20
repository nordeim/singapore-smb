/**
 * Cart Page
 * 
 * Shopping cart with items, summary, and checkout CTA.
 */
'use client';

import Link from 'next/link';
import { ShoppingBag } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { CartItem } from '@/components/cart/cart-item';
import { CartSummary } from '@/components/cart/cart-summary';
import { useCart } from '@/lib/hooks/useCart';

export default function CartPage() {
    const { items, totals, isLoading } = useCart();

    if (isLoading) {
        return (
            <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                <h1 className="mb-8 text-2xl font-bold text-gray-900">Shopping Cart</h1>
                <div className="animate-pulse space-y-4">
                    {Array.from({ length: 3 }).map((_, i) => (
                        <div key={i} className="h-24 rounded-lg bg-gray-200" />
                    ))}
                </div>
            </div>
        );
    }

    // Empty cart state
    if (items.length === 0) {
        return (
            <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
                <div className="text-center">
                    <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-gray-100">
                        <ShoppingBag className="h-10 w-10 text-gray-400" />
                    </div>
                    <h1 className="mt-6 text-2xl font-bold text-gray-900">Your cart is empty</h1>
                    <p className="mt-2 text-gray-500">
                        Looks like you haven&apos;t added anything to your cart yet.
                    </p>
                    <Link href="/products" className="mt-6 inline-block">
                        <Button size="lg">Browse Products</Button>
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            <h1 className="mb-8 text-2xl font-bold text-gray-900">
                Shopping Cart ({totals.itemCount} {totals.itemCount === 1 ? 'item' : 'items'})
            </h1>

            <div className="grid gap-8 lg:grid-cols-3">
                {/* Cart Items */}
                <div className="lg:col-span-2">
                    <div className="rounded-xl border border-gray-200 bg-white p-6">
                        {items.map((item) => (
                            <CartItem key={item.id} item={item} />
                        ))}
                    </div>
                </div>

                {/* Cart Summary */}
                <div className="lg:col-span-1">
                    <CartSummary
                        subtotal={totals.subtotal}
                        gstAmount={totals.gstAmount}
                        total={totals.total}
                        itemCount={totals.itemCount}
                        isLoading={isLoading}
                    />
                </div>
            </div>
        </div>
    );
}
