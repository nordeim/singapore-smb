/**
 * useMediaQuery Hook
 * 
 * SSR-safe hook for detecting responsive breakpoints.
 * Matches Tailwind CSS breakpoints by default.
 */
'use client';

import { useState, useEffect, useCallback } from 'react';

// Tailwind CSS breakpoints
export const breakpoints = {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
} as const;

type Breakpoint = keyof typeof breakpoints;

/**
 * Check if a media query matches
 * 
 * @param query - Media query string
 * @returns Boolean indicating if query matches
 * 
 * @example
 * ```tsx
 * const isMobile = useMediaQuery('(max-width: 767px)');
 * const isDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
 * ```
 */
export function useMediaQuery(query: string): boolean {
    // Default to false for SSR
    const [matches, setMatches] = useState(false);

    useEffect(() => {
        // Only run on client
        if (typeof window === 'undefined') return;

        const mediaQuery = window.matchMedia(query);

        // Set initial value
        setMatches(mediaQuery.matches);

        // Create event listener
        const handler = (event: MediaQueryListEvent) => {
            setMatches(event.matches);
        };

        // Add listener
        mediaQuery.addEventListener('change', handler);

        // Clean up
        return () => {
            mediaQuery.removeEventListener('change', handler);
        };
    }, [query]);

    return matches;
}

/**
 * Check if viewport is at or above a breakpoint
 * 
 * @param breakpoint - Tailwind breakpoint name
 * @returns Boolean indicating if viewport matches
 * 
 * @example
 * ```tsx
 * const isDesktop = useBreakpoint('lg'); // >= 1024px
 * const isTablet = useBreakpoint('md');  // >= 768px
 * ```
 */
export function useBreakpoint(breakpoint: Breakpoint): boolean {
    const query = `(min-width: ${breakpoints[breakpoint]})`;
    return useMediaQuery(query);
}

/**
 * Get current breakpoint name
 * 
 * @returns Current breakpoint name or 'xs' for mobile
 * 
 * @example
 * ```tsx
 * const currentBreakpoint = useCurrentBreakpoint();
 * // Returns 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'
 * ```
 */
export function useCurrentBreakpoint(): Breakpoint | 'xs' {
    const isSm = useBreakpoint('sm');
    const isMd = useBreakpoint('md');
    const isLg = useBreakpoint('lg');
    const isXl = useBreakpoint('xl');
    const is2xl = useBreakpoint('2xl');

    if (is2xl) return '2xl';
    if (isXl) return 'xl';
    if (isLg) return 'lg';
    if (isMd) return 'md';
    if (isSm) return 'sm';
    return 'xs';
}

/**
 * Check if on mobile (below md breakpoint)
 */
export function useIsMobile(): boolean {
    return !useBreakpoint('md');
}

/**
 * Check if on desktop (at or above lg breakpoint)
 */
export function useIsDesktop(): boolean {
    return useBreakpoint('lg');
}

export default useMediaQuery;
