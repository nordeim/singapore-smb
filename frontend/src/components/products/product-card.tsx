/**
 * Product Card Component
 * 
 * Card for displaying a product in grid layouts.
 */
'use client';

import * as React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { ShoppingCart } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useCart } from '@/lib/hooks/useCart';
import type { Product } from '@/types';

interface ProductCardProps {
    product: Product;
    priority?: boolean;
}

export function ProductCard({ product, priority = false }: ProductCardProps) {
    const { addItem, isUpdating } = useCart();
    const [isAdding, setIsAdding] = React.useState(false);

    const handleAddToCart = async (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();

        setIsAdding(true);
        try {
            await addItem({
                productId: product.id,
                quantity: 1,
            });
        } finally {
            setIsAdding(false);
        }
    };

    // Calculate GST-inclusive price
    const basePrice = parseFloat(product.basePrice);
    const gstRate = parseFloat(product.gstRate || '0');
    const priceWithGst = product.gstCode === 'SR'
        ? basePrice * (1 + gstRate / 100)
        : basePrice;

    return (
        <Link href={`/products/${product.slug}`}>
            <Card hoverable className="group overflow-hidden">
                {/* Image */}
                <div className="relative aspect-square overflow-hidden bg-gray-100">
                    {product.imageUrl ? (
                        <Image
                            src={product.imageUrl}
                            alt={product.name}
                            fill
                            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
                            className="object-cover transition-transform group-hover:scale-105"
                            priority={priority}
                        />
                    ) : (
                        <div className="flex h-full items-center justify-center">
                            <span className="text-4xl text-gray-300">📦</span>
                        </div>
                    )}

                    {/* Badges */}
                    <div className="absolute left-2 top-2 flex flex-col gap-1">
                        {product.compareAtPrice && parseFloat(product.compareAtPrice) > basePrice && (
                            <Badge variant="error" size="sm">
                                Sale
                            </Badge>
                        )}
                        {product.gstCode === 'ZR' && (
                            <Badge variant="success" size="sm">
                                GST-Free
                            </Badge>
                        )}
                    </div>

                    {/* Quick Add Button */}
                    <div className="absolute bottom-2 right-2 opacity-0 transition-opacity group-hover:opacity-100">
                        <Button
                            size="sm"
                            onClick={handleAddToCart}
                            loading={isAdding}
                            disabled={isUpdating}
                            className="shadow-lg"
                        >
                            <ShoppingCart className="h-4 w-4" />
                        </Button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-4">
                    {/* Category */}
                    {product.category && (
                        <p className="text-xs font-medium text-gray-500">
                            {product.category.name}
                        </p>
                    )}

                    {/* Title */}
                    <h3 className="mt-1 text-sm font-medium text-gray-900 line-clamp-2">
                        {product.name}
                    </h3>

                    {/* Price */}
                    <div className="mt-2 flex items-baseline gap-2">
                        <span className="text-lg font-semibold text-gray-900">
                            S${priceWithGst.toFixed(2)}
                        </span>
                        {product.compareAtPrice && parseFloat(product.compareAtPrice) > basePrice && (
                            <span className="text-sm text-gray-400 line-through">
                                S${parseFloat(product.compareAtPrice).toFixed(2)}
                            </span>
                        )}
                    </div>

                    {/* GST indicator */}
                    {product.gstCode === 'SR' && (
                        <p className="mt-1 text-xs text-gray-500">
                            Incl. {gstRate}% GST
                        </p>
                    )}
                </div>
            </Card>
        </Link>
    );
}

export default ProductCard;
