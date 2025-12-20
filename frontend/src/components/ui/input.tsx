/**
 * Input Component
 * 
 * Form input with label, error state, and help text.
 */
import * as React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import * as LabelPrimitive from '@radix-ui/react-label';

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    helpText?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ className, label, error, helpText, id, type = 'text', ...props }, ref) => {
        const inputId = id || React.useId();
        const errorId = `${inputId}-error`;
        const helpId = `${inputId}-help`;

        return (
            <div className="w-full">
                {label && (
                    <LabelPrimitive.Root
                        htmlFor={inputId}
                        className="mb-1.5 block text-sm font-medium text-gray-700"
                    >
                        {label}
                    </LabelPrimitive.Root>
                )}
                <input
                    ref={ref}
                    id={inputId}
                    type={type}
                    className={cn(
                        // Base styles
                        'flex h-10 w-full rounded-lg border bg-white px-3 py-2 text-base',
                        // Placeholder
                        'placeholder:text-gray-400',
                        // Focus styles
                        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2',
                        // Disabled styles
                        'disabled:cursor-not-allowed disabled:bg-gray-50 disabled:opacity-50',
                        // Error styles
                        error
                            ? 'border-error-500 focus-visible:ring-error-500'
                            : 'border-gray-300',
                        className
                    )}
                    aria-invalid={!!error}
                    aria-describedby={
                        error ? errorId : helpText ? helpId : undefined
                    }
                    {...props}
                />
                {error && (
                    <p id={errorId} className="mt-1.5 text-sm text-error-600">
                        {error}
                    </p>
                )}
                {helpText && !error && (
                    <p id={helpId} className="mt-1.5 text-sm text-gray-500">
                        {helpText}
                    </p>
                )}
            </div>
        );
    }
);

Input.displayName = 'Input';

export default Input;
