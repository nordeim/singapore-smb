/**
 * Cart Item Component
 * 
 * Single cart item row with quantity controls and remove button.
 */
'use client';

import * as React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Minus, Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCart } from '@/lib/hooks/useCart';
import type { CartItem as CartItemType } from '@/types';

interface CartItemProps {
    item: CartItemType;
}

export function CartItem({ item }: CartItemProps) {
    const { updateQuantity, removeItem, isUpdating } = useCart();
    const [isRemoving, setIsRemoving] = React.useState(false);

    const handleQuantityChange = async (delta: number) => {
        const newQuantity = item.quantity + delta;
        if (newQuantity >= 1) {
            await updateQuantity(item.id, newQuantity);
        }
    };

    const handleRemove = async () => {
        setIsRemoving(true);
        try {
            await removeItem(item.id);
        } finally {
            setIsRemoving(false);
        }
    };

    const lineTotal = parseFloat(item.lineTotal);

    return (
        <div className="flex gap-4 py-4 border-b border-gray-200 last:border-0">
            {/* Image */}
            <Link
                href={`/products/${item.product.slug}`}
                className="relative h-24 w-24 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100"
            >
                {item.product.imageUrl ? (
                    <Image
                        src={item.product.imageUrl}
                        alt={item.product.name}
                        fill
                        sizes="96px"
                        className="object-cover"
                    />
                ) : (
                    <div className="flex h-full items-center justify-center">
                        <span className="text-2xl text-gray-300">📦</span>
                    </div>
                )}
            </Link>

            {/* Details */}
            <div className="flex flex-1 flex-col justify-between">
                <div>
                    <Link
                        href={`/products/${item.product.slug}`}
                        className="text-sm font-medium text-gray-900 hover:text-primary-600"
                    >
                        {item.product.name}
                    </Link>

                    {/* Variant info */}
                    {item.variant && (
                        <p className="mt-1 text-xs text-gray-500">
                            {Object.entries(item.variant.options || {})
                                .map(([key, value]) => `${key}: ${value}`)
                                .join(', ')}
                        </p>
                    )}

                    {/* Unit price */}
                    <p className="mt-1 text-sm text-gray-600">
                        S${parseFloat(item.unitPrice).toFixed(2)} each
                    </p>
                </div>

                {/* Quantity & Actions */}
                <div className="mt-2 flex items-center justify-between">
                    {/* Quantity Controls */}
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => handleQuantityChange(-1)}
                            disabled={item.quantity <= 1 || isUpdating}
                            className="flex h-8 w-8 items-center justify-center rounded-lg border border-gray-300 text-gray-600 transition-colors hover:bg-gray-50 disabled:opacity-50"
                            aria-label="Decrease quantity"
                        >
                            <Minus className="h-4 w-4" />
                        </button>
                        <span className="w-8 text-center text-sm font-medium">
                            {item.quantity}
                        </span>
                        <button
                            onClick={() => handleQuantityChange(1)}
                            disabled={isUpdating}
                            className="flex h-8 w-8 items-center justify-center rounded-lg border border-gray-300 text-gray-600 transition-colors hover:bg-gray-50 disabled:opacity-50"
                            aria-label="Increase quantity"
                        >
                            <Plus className="h-4 w-4" />
                        </button>
                    </div>

                    {/* Line Total & Remove */}
                    <div className="flex items-center gap-4">
                        <span className="text-sm font-semibold text-gray-900">
                            S${lineTotal.toFixed(2)}
                        </span>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleRemove}
                            loading={isRemoving}
                            disabled={isUpdating}
                            className="text-gray-400 hover:text-error-600"
                            aria-label="Remove item"
                        >
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default CartItem;
