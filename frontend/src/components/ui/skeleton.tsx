/**
 * Skeleton Component
 * 
 * Loading placeholder with pulse animation.
 */
import * as React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

// Base Skeleton
export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> { }

export const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
    ({ className, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    'animate-pulse rounded-lg bg-gray-200',
                    className
                )}
                {...props}
            />
        );
    }
);
Skeleton.displayName = 'Skeleton';

// Skeleton Text Line
export const SkeletonText = React.forwardRef<
    HTMLDivElement,
    SkeletonProps & { lines?: number }
>(({ className, lines = 1, ...props }, ref) => {
    return (
        <div ref={ref} className={cn('space-y-2', className)} {...props}>
            {Array.from({ length: lines }).map((_, i) => (
                <Skeleton
                    key={i}
                    className={cn(
                        'h-4',
                        // Make last line shorter
                        i === lines - 1 && lines > 1 && 'w-3/4'
                    )}
                />
            ))}
        </div>
    );
});
SkeletonText.displayName = 'SkeletonText';

// Skeleton Card (for product cards, etc.)
export const SkeletonCard = React.forwardRef<HTMLDivElement, SkeletonProps>(
    ({ className, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn('space-y-4 rounded-xl border border-gray-200 p-4', className)}
                {...props}
            >
                {/* Image placeholder */}
                <Skeleton className="aspect-square w-full rounded-lg" />
                {/* Title */}
                <Skeleton className="h-5 w-3/4" />
                {/* Price */}
                <Skeleton className="h-4 w-1/3" />
                {/* Button */}
                <Skeleton className="h-10 w-full rounded-lg" />
            </div>
        );
    }
);
SkeletonCard.displayName = 'SkeletonCard';

// Skeleton Avatar
export const SkeletonAvatar = React.forwardRef<
    HTMLDivElement,
    SkeletonProps & { size?: 'sm' | 'md' | 'lg' }
>(({ className, size = 'md', ...props }, ref) => {
    const sizeClasses = {
        sm: 'h-8 w-8',
        md: 'h-10 w-10',
        lg: 'h-12 w-12',
    };

    return (
        <Skeleton
            ref={ref}
            className={cn('rounded-full', sizeClasses[size], className)}
            {...props}
        />
    );
});
SkeletonAvatar.displayName = 'SkeletonAvatar';

export default Skeleton;
