'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState, type ReactNode } from 'react';

interface ProvidersProps {
    children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
    const [queryClient] = useState(
        () =>
            new QueryClient({
                defaultOptions: {
                    queries: {
                        // Stale time of 1 minute
                        staleTime: 60 * 1000,
                        // Cache for 5 minutes
                        gcTime: 5 * 60 * 1000,
                        // Retry once on failure
                        retry: 1,
                        // Refetch on window focus
                        refetchOnWindowFocus: true,
                    },
                    mutations: {
                        // Retry once on failure
                        retry: 1,
                    },
                },
            })
    );

    return (
        <QueryClientProvider client={queryClient}>
            {children}
            <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
    );
}
