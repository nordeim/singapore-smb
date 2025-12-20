import { SkeletonCard } from '@/components/ui/skeleton';

export default function ProductsLoading() {
    return (
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            <div className="flex flex-col gap-8 lg:flex-row">
                {/* Sidebar Skeleton */}
                <aside className="w-full lg:w-64 flex-shrink-0">
                    <div className="space-y-6">
                        <div className="h-10 w-full rounded-lg bg-gray-200 animate-pulse" />
                        <div className="h-40 w-full rounded-lg bg-gray-200 animate-pulse" />
                    </div>
                </aside>

                {/* Grid Skeleton */}
                <main className="flex-1">
                    <div className="mb-6 h-8 w-48 bg-gray-200 animate-pulse rounded" />
                    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {Array.from({ length: 6 }).map((_, i) => (
                            <SkeletonCard key={i} />
                        ))}
                    </div>
                </main>
            </div>
        </div>
    );
}
