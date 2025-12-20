/**
 * Products Listing Page
 * 
 * Client Component with URL-based filtering.
 */
'use client';

import { Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { ProductGrid } from '@/components/products/product-grid';
import { CategoryFilter } from '@/components/products/category-filter';
import { ProductSearch } from '@/components/products/product-search';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { useProducts, useCategories } from '@/lib/api/queries';

export default function ProductsPage() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const page = parseInt(searchParams.get('page') || '1', 10);
    const category = searchParams.get('category') || undefined;
    const search = searchParams.get('search') || undefined;
    const sort = searchParams.get('sort') || '-created_at';
    const pageSize = 12;

    const { data: productsResponse, isLoading: productsLoading } = useProducts({
        category,
        search,
        page,
        pageSize,
        ordering: sort,
    });

    const { data: categories = [], isLoading: categoriesLoading } = useCategories();

    const products = productsResponse?.results || [];
    const totalPages = productsResponse ? Math.ceil(productsResponse.count / pageSize) : 0;

    const handlePageChange = (newPage: number) => {
        const params = new URLSearchParams(searchParams.toString());
        params.set('page', newPage.toString());
        router.push(`/products?${params.toString()}`);
    };

    return (
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            <div className="flex flex-col gap-8 lg:flex-row">
                {/* Sidebar */}
                <aside className="w-full lg:w-64 flex-shrink-0">
                    <div className="sticky top-20 space-y-6">
                        {/* Search */}
                        <div>
                            <h3 className="mb-3 text-sm font-semibold text-gray-900">Search</h3>
                            <ProductSearch defaultValue={search} />
                        </div>

                        {/* Categories */}
                        <div>
                            <h3 className="mb-3 text-sm font-semibold text-gray-900">Categories</h3>
                            {categoriesLoading ? (
                                <Skeleton className="h-40 w-full" />
                            ) : (
                                <CategoryFilter
                                    categories={categories}
                                    selectedCategory={category}
                                />
                            )}
                        </div>

                        {/* Sort */}
                        <div>
                            <h3 className="mb-3 text-sm font-semibold text-gray-900">Sort By</h3>
                            <SortSelect currentSort={sort} />
                        </div>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="flex-1">
                    {/* Header */}
                    <div className="mb-6 flex items-center justify-between">
                        <h1 className="text-2xl font-bold text-gray-900">
                            {category ? 'Category Results' : 'All Products'}
                        </h1>
                        <p className="text-sm text-gray-500">
                            {productsResponse?.count || 0} products
                        </p>
                    </div>

                    {/* Product Grid */}
                    <ProductGrid
                        products={products}
                        isLoading={productsLoading}
                        emptyMessage={
                            search
                                ? `No products found for "${search}"`
                                : 'No products available'
                        }
                    />

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="mt-8 flex justify-center gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handlePageChange(page - 1)}
                                disabled={page === 1}
                            >
                                Previous
                            </Button>
                            <span className="flex items-center px-4 text-sm text-gray-600">
                                Page {page} of {totalPages}
                            </span>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handlePageChange(page + 1)}
                                disabled={page === totalPages}
                            >
                                Next
                            </Button>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
}

function SortSelect({ currentSort }: { currentSort?: string }) {
    const router = useRouter();
    const searchParams = useSearchParams();

    const sortOptions = [
        { value: '-created_at', label: 'Newest' },
        { value: 'base_price', label: 'Price: Low to High' },
        { value: '-base_price', label: 'Price: High to Low' },
        { value: 'name', label: 'Name: A-Z' },
    ];

    const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const params = new URLSearchParams(searchParams.toString());
        params.set('sort', e.target.value);
        params.delete('page');
        router.push(`/products?${params.toString()}`);
    };

    return (
        <select
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            defaultValue={currentSort || '-created_at'}
            onChange={handleSortChange}
        >
            {sortOptions.map((option) => (
                <option key={option.value} value={option.value}>
                    {option.label}
                </option>
            ))}
        </select>
    );
}
