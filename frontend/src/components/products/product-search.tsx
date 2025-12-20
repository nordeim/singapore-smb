/**
 * Product Search Component
 * 
 * Search input with debounced URL navigation.
 */
'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { Search } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useDebounce } from '@/lib/hooks/useDebounce';

interface ProductSearchProps {
    defaultValue?: string;
}

export function ProductSearch({ defaultValue = '' }: ProductSearchProps) {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [query, setQuery] = useState(defaultValue);
    const debouncedQuery = useDebounce(query, 300);

    useEffect(() => {
        const params = new URLSearchParams(searchParams.toString());

        if (debouncedQuery) {
            params.set('search', debouncedQuery);
        } else {
            params.delete('search');
        }
        params.delete('page'); // Reset pagination

        router.push(`/products?${params.toString()}`);
    }, [debouncedQuery, router, searchParams]);

    return (
        <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search products..."
                className="h-10 w-full rounded-lg border border-gray-300 bg-white pl-10 pr-4 text-sm placeholder:text-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
        </div>
    );
}

export default ProductSearch;
