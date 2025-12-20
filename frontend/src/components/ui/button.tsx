/**
 * Button Component
 * 
 * Primary button component with variants, sizes, and loading state.
 */
import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Spinner } from './spinner';

// Utility function for merging classes
function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
    size?: 'sm' | 'md' | 'lg';
    loading?: boolean;
    asChild?: boolean;
}

const variantStyles = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus-visible:ring-primary-500',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-500',
    outline: 'border border-gray-300 bg-transparent text-gray-700 hover:bg-gray-50 focus-visible:ring-gray-500',
    ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-500',
    destructive: 'bg-error-600 text-white hover:bg-error-700 focus-visible:ring-error-500',
};

const sizeStyles = {
    sm: 'h-8 px-3 text-sm',
    md: 'h-10 px-4 text-base',
    lg: 'h-12 px-6 text-lg',
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    (
        {
            className,
            variant = 'primary',
            size = 'md',
            loading = false,
            disabled,
            asChild = false,
            children,
            ...props
        },
        ref
    ) => {
        const Comp = asChild ? Slot : 'button';

        return (
            <Comp
                ref={ref}
                className={cn(
                    // Base styles
                    'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors',
                    // Focus styles
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
                    // Disabled styles
                    'disabled:pointer-events-none disabled:opacity-50',
                    // Variant styles
                    variantStyles[variant],
                    // Size styles
                    sizeStyles[size],
                    className
                )}
                disabled={disabled || loading}
                {...props}
            >
                {loading && <Spinner size="sm" />}
                {children}
            </Comp>
        );
    }
);

Button.displayName = 'Button';

export default Button;
