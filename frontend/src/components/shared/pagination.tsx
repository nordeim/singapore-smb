/**
 * Pagination Component
 * 
 * Reusable pagination with URL-based navigation.
 */
import Link from 'next/link';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { clsx } from 'clsx';

interface PaginationProps {
    currentPage: number;
    totalPages: number;
    basePath: string;
    searchParams?: Record<string, string | undefined>;
}

export function Pagination({
    currentPage,
    totalPages,
    basePath,
    searchParams = {},
}: PaginationProps) {
    const buildUrl = (page: number) => {
        const params = new URLSearchParams();
        Object.entries(searchParams).forEach(([key, value]) => {
            if (value && key !== 'page') {
                params.set(key, value);
            }
        });
        params.set('page', page.toString());
        return `${basePath}?${params.toString()}`;
    };

    // Generate page numbers to display
    const getPageNumbers = () => {
        const pages: (number | 'ellipsis')[] = [];
        const showEllipsisStart = currentPage > 3;
        const showEllipsisEnd = currentPage < totalPages - 2;

        pages.push(1);

        if (showEllipsisStart) {
            pages.push('ellipsis');
        }

        for (
            let i = Math.max(2, currentPage - 1);
            i <= Math.min(totalPages - 1, currentPage + 1);
            i++
        ) {
            if (!pages.includes(i)) {
                pages.push(i);
            }
        }

        if (showEllipsisEnd) {
            pages.push('ellipsis');
        }

        if (totalPages > 1 && !pages.includes(totalPages)) {
            pages.push(totalPages);
        }

        return pages;
    };

    const pageNumbers = getPageNumbers();

    return (
        <nav className="flex items-center justify-center gap-1" aria-label="Pagination">
            {/* Previous */}
            {currentPage > 1 ? (
                <Link
                    href={buildUrl(currentPage - 1)}
                    className="flex h-10 items-center gap-1 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                    <ChevronLeft className="h-4 w-4" />
                    <span className="hidden sm:inline">Previous</span>
                </Link>
            ) : (
                <span className="flex h-10 items-center gap-1 rounded-lg border border-gray-200 bg-gray-50 px-3 text-sm font-medium text-gray-400">
                    <ChevronLeft className="h-4 w-4" />
                    <span className="hidden sm:inline">Previous</span>
                </span>
            )}

            {/* Page Numbers */}
            <div className="flex items-center gap-1">
                {pageNumbers.map((page, index) =>
                    page === 'ellipsis' ? (
                        <span
                            key={`ellipsis-${index}`}
                            className="flex h-10 w-10 items-center justify-center text-gray-500"
                        >
                            …
                        </span>
                    ) : (
                        <Link
                            key={page}
                            href={buildUrl(page)}
                            className={clsx(
                                'flex h-10 w-10 items-center justify-center rounded-lg text-sm font-medium transition-colors',
                                page === currentPage
                                    ? 'bg-primary-600 text-white'
                                    : 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                            )}
                        >
                            {page}
                        </Link>
                    )
                )}
            </div>

            {/* Next */}
            {currentPage < totalPages ? (
                <Link
                    href={buildUrl(currentPage + 1)}
                    className="flex h-10 items-center gap-1 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                    <span className="hidden sm:inline">Next</span>
                    <ChevronRight className="h-4 w-4" />
                </Link>
            ) : (
                <span className="flex h-10 items-center gap-1 rounded-lg border border-gray-200 bg-gray-50 px-3 text-sm font-medium text-gray-400">
                    <span className="hidden sm:inline">Next</span>
                    <ChevronRight className="h-4 w-4" />
                </span>
            )}
        </nav>
    );
}

export default Pagination;
