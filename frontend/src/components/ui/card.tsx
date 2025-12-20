/**
 * Card Component
 * 
 * Card container with header, content, and footer subcomponents.
 */
import * as React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

// Card Root
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    hoverable?: boolean;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
    ({ className, hoverable = false, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    'rounded-xl border border-gray-200 bg-white shadow-card',
                    hoverable && 'transition-shadow hover:shadow-card-hover',
                    className
                )}
                {...props}
            />
        );
    }
);
Card.displayName = 'Card';

// Card Header
export const CardHeader = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => {
    return (
        <div
            ref={ref}
            className={cn('flex flex-col space-y-1.5 p-6', className)}
            {...props}
        />
    );
});
CardHeader.displayName = 'CardHeader';

// Card Title
export const CardTitle = React.forwardRef<
    HTMLHeadingElement,
    React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => {
    return (
        <h3
            ref={ref}
            className={cn('text-lg font-semibold leading-none tracking-tight', className)}
            {...props}
        />
    );
});
CardTitle.displayName = 'CardTitle';

// Card Description
export const CardDescription = React.forwardRef<
    HTMLParagraphElement,
    React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => {
    return (
        <p
            ref={ref}
            className={cn('text-sm text-gray-500', className)}
            {...props}
        />
    );
});
CardDescription.displayName = 'CardDescription';

// Card Content
export const CardContent = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => {
    return (
        <div
            ref={ref}
            className={cn('p-6 pt-0', className)}
            {...props}
        />
    );
});
CardContent.displayName = 'CardContent';

// Card Footer
export const CardFooter = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => {
    return (
        <div
            ref={ref}
            className={cn('flex items-center p-6 pt-0', className)}
            {...props}
        />
    );
});
CardFooter.displayName = 'CardFooter';

export default Card;
