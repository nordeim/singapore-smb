/**
 * Add to Cart Button Component
 * 
 * Client component for adding products to cart with quantity.
 */
'use client';

import { useState } from 'react';
import { Minus, Plus, ShoppingCart, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCart } from '@/lib/hooks/useCart';

interface AddToCartButtonProps {
    productId: string;
    productName: string;
    variantId?: string;
}

export function AddToCartButton({ productId, productName, variantId }: AddToCartButtonProps) {
    const { addItem, isUpdating } = useCart();
    const [quantity, setQuantity] = useState(1);
    const [isAdded, setIsAdded] = useState(false);

    const handleQuantityChange = (delta: number) => {
        setQuantity((prev) => Math.max(1, Math.min(99, prev + delta)));
    };

    const handleAddToCart = async () => {
        await addItem({
            productId,
            variantId,
            quantity,
        });

        // Show success state
        setIsAdded(true);
        setTimeout(() => setIsAdded(false), 2000);
    };

    return (
        <div className="space-y-4">
            {/* Quantity Selector */}
            <div className="flex items-center gap-4">
                <span className="text-sm font-medium text-gray-700">Quantity</span>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => handleQuantityChange(-1)}
                        disabled={quantity <= 1}
                        className="flex h-10 w-10 items-center justify-center rounded-lg border border-gray-300 text-gray-600 transition-colors hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        aria-label="Decrease quantity"
                    >
                        <Minus className="h-4 w-4" />
                    </button>
                    <input
                        type="number"
                        value={quantity}
                        onChange={(e) => setQuantity(Math.max(1, Math.min(99, parseInt(e.target.value) || 1)))}
                        className="h-10 w-16 rounded-lg border border-gray-300 text-center text-sm font-medium focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                        min="1"
                        max="99"
                    />
                    <button
                        onClick={() => handleQuantityChange(1)}
                        disabled={quantity >= 99}
                        className="flex h-10 w-10 items-center justify-center rounded-lg border border-gray-300 text-gray-600 transition-colors hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        aria-label="Increase quantity"
                    >
                        <Plus className="h-4 w-4" />
                    </button>
                </div>
            </div>

            {/* Add to Cart Button */}
            <Button
                onClick={handleAddToCart}
                loading={isUpdating}
                size="lg"
                className="w-full"
                variant={isAdded ? 'secondary' : 'primary'}
            >
                {isAdded ? (
                    <>
                        <Check className="h-5 w-5" />
                        Added to Cart
                    </>
                ) : (
                    <>
                        <ShoppingCart className="h-5 w-5" />
                        Add to Cart
                    </>
                )}
            </Button>
        </div>
    );
}

export default AddToCartButton;
