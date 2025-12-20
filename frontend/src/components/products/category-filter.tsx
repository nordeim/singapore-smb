/**
 * Category Filter Component
 * 
 * Sidebar filter for product categories.
 */
'use client';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { clsx } from 'clsx';
import type { Category } from '@/types';

interface CategoryFilterProps {
    categories: Category[];
    selectedCategory?: string;
}

export function CategoryFilter({ categories, selectedCategory }: CategoryFilterProps) {
    const searchParams = useSearchParams();

    const buildUrl = (categorySlug?: string) => {
        const params = new URLSearchParams(searchParams.toString());
        if (categorySlug) {
            params.set('category', categorySlug);
        } else {
            params.delete('category');
        }
        params.delete('page'); // Reset pagination
        return `/products?${params.toString()}`;
    };

    return (
        <nav className="space-y-1">
            {/* All Products */}
            <Link
                href={buildUrl()}
                className={clsx(
                    'block rounded-lg px-3 py-2 text-sm transition-colors',
                    !selectedCategory
                        ? 'bg-primary-50 font-medium text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100'
                )}
            >
                All Products
            </Link>

            {/* Category List */}
            {categories.map((category) => (
                <CategoryItem
                    key={category.id}
                    category={category}
                    selectedCategory={selectedCategory}
                    buildUrl={buildUrl}
                />
            ))}
        </nav>
    );
}

interface CategoryItemProps {
    category: Category;
    selectedCategory?: string;
    buildUrl: (slug?: string) => string;
    depth?: number;
}

function CategoryItem({ category, selectedCategory, buildUrl, depth = 0 }: CategoryItemProps) {
    const isSelected = selectedCategory === category.slug;

    return (
        <div>
            <Link
                href={buildUrl(category.slug)}
                className={clsx(
                    'block rounded-lg px-3 py-2 text-sm transition-colors',
                    isSelected
                        ? 'bg-primary-50 font-medium text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100',
                    depth > 0 && 'ml-4'
                )}
            >
                {category.name}
            </Link>
        </div>
    );
}

export default CategoryFilter;
