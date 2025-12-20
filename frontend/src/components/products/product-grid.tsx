/**
 * Product Grid Component
 * 
 * Responsive grid layout for products with loading and empty states.
 */
import * as React from 'react';
import { ProductCard } from './product-card';
import { SkeletonCard } from '@/components/ui/skeleton';
import type { Product } from '@/types';

interface ProductGridProps {
    products: Product[];
    isLoading?: boolean;
    emptyMessage?: string;
    columns?: 2 | 3 | 4;
}

export function ProductGrid({
    products,
    isLoading = false,
    emptyMessage = 'No products found',
    columns = 4,
}: ProductGridProps) {
    const gridCols = {
        2: 'grid-cols-1 sm:grid-cols-2',
        3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
        4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
    };

    // Loading state
    if (isLoading) {
        return (
            <div className={`grid gap-6 ${gridCols[columns]}`}>
                {Array.from({ length: columns * 2 }).map((_, i) => (
                    <SkeletonCard key={i} />
                ))}
            </div>
        );
    }

    // Empty state
    if (products.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-16">
                <div className="text-6xl">📦</div>
                <h3 className="mt-4 text-lg font-medium text-gray-900">
                    {emptyMessage}
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                    Try adjusting your filters or search terms.
                </p>
            </div>
        );
    }

    return (
        <div className={`grid gap-6 ${gridCols[columns]}`}>
            {products.map((product, index) => (
                <ProductCard
                    key={product.id}
                    product={product}
                    priority={index < 4} // Prioritize first 4 images
                />
            ))}
        </div>
    );
}

export default ProductGrid;
