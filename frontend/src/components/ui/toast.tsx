/**
 * Toast Component
 * 
 * Toast notifications using Radix Toast primitives.
 */
'use client';

import * as React from 'react';
import * as ToastPrimitive from '@radix-ui/react-toast';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { X } from 'lucide-react';

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

// Toast Provider
export const ToastProvider = ToastPrimitive.Provider;

// Toast Viewport
export const ToastViewport = React.forwardRef<
    React.ElementRef<typeof ToastPrimitive.Viewport>,
    React.ComponentPropsWithoutRef<typeof ToastPrimitive.Viewport>
>(({ className, ...props }, ref) => (
    <ToastPrimitive.Viewport
        ref={ref}
        className={cn(
            'fixed top-0 z-50 flex max-h-screen w-full flex-col-reverse gap-2 p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:max-w-md',
            className
        )}
        {...props}
    />
));
ToastViewport.displayName = 'ToastViewport';

// Toast variants
const toastVariants = {
    default: 'bg-white border-gray-200',
    success: 'bg-success-50 border-success-200',
    error: 'bg-error-50 border-error-200',
    warning: 'bg-warning-50 border-warning-200',
    info: 'bg-primary-50 border-primary-200',
};

export interface ToastProps
    extends React.ComponentPropsWithoutRef<typeof ToastPrimitive.Root> {
    variant?: keyof typeof toastVariants;
}

// Toast Root
export const Toast = React.forwardRef<
    React.ElementRef<typeof ToastPrimitive.Root>,
    ToastProps
>(({ className, variant = 'default', ...props }, ref) => (
    <ToastPrimitive.Root
        ref={ref}
        className={cn(
            'group pointer-events-auto relative flex w-full items-center justify-between gap-4 overflow-hidden rounded-lg border p-4 shadow-lg transition-all',
            'data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none',
            'data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full',
            toastVariants[variant],
            className
        )}
        {...props}
    />
));
Toast.displayName = 'Toast';

// Toast Title
export const ToastTitle = React.forwardRef<
    React.ElementRef<typeof ToastPrimitive.Title>,
    React.ComponentPropsWithoutRef<typeof ToastPrimitive.Title>
>(({ className, ...props }, ref) => (
    <ToastPrimitive.Title
        ref={ref}
        className={cn('text-sm font-semibold', className)}
        {...props}
    />
));
ToastTitle.displayName = 'ToastTitle';

// Toast Description
export const ToastDescription = React.forwardRef<
    React.ElementRef<typeof ToastPrimitive.Description>,
    React.ComponentPropsWithoutRef<typeof ToastPrimitive.Description>
>(({ className, ...props }, ref) => (
    <ToastPrimitive.Description
        ref={ref}
        className={cn('text-sm opacity-90', className)}
        {...props}
    />
));
ToastDescription.displayName = 'ToastDescription';

// Toast Close Button
export const ToastClose = React.forwardRef<
    React.ElementRef<typeof ToastPrimitive.Close>,
    React.ComponentPropsWithoutRef<typeof ToastPrimitive.Close>
>(({ className, ...props }, ref) => (
    <ToastPrimitive.Close
        ref={ref}
        className={cn(
            'absolute right-2 top-2 rounded-md p-1 text-gray-500 opacity-0 transition-opacity hover:text-gray-900 focus:opacity-100 focus:outline-none focus:ring-2 group-hover:opacity-100',
            className
        )}
        toast-close=""
        {...props}
    >
        <X className="h-4 w-4" />
    </ToastPrimitive.Close>
));
ToastClose.displayName = 'ToastClose';

// Toast Action
export const ToastAction = React.forwardRef<
    React.ElementRef<typeof ToastPrimitive.Action>,
    React.ComponentPropsWithoutRef<typeof ToastPrimitive.Action>
>(({ className, ...props }, ref) => (
    <ToastPrimitive.Action
        ref={ref}
        className={cn(
            'inline-flex h-8 shrink-0 items-center justify-center rounded-md border bg-transparent px-3 text-sm font-medium ring-offset-white transition-colors hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
            className
        )}
        {...props}
    />
));
ToastAction.displayName = 'ToastAction';

// ============================================================================
// Toast Hook
// ============================================================================

type ToastType = {
    id: string;
    title?: string;
    description?: string;
    variant?: keyof typeof toastVariants;
    duration?: number;
};

interface ToastContextValue {
    toasts: ToastType[];
    addToast: (toast: Omit<ToastType, 'id'>) => void;
    removeToast: (id: string) => void;
}

const ToastContext = React.createContext<ToastContextValue | undefined>(undefined);

export function ToastContextProvider({ children }: { children: React.ReactNode }) {
    const [toasts, setToasts] = React.useState<ToastType[]>([]);

    const addToast = React.useCallback((toast: Omit<ToastType, 'id'>) => {
        const id = Math.random().toString(36).substring(2, 9);
        setToasts((prev) => [...prev, { ...toast, id }]);
    }, []);

    const removeToast = React.useCallback((id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);

    return (
        <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
            <ToastProvider>
                {children}
                {toasts.map((toast) => (
                    <Toast
                        key={toast.id}
                        variant={toast.variant}
                        duration={toast.duration || 5000}
                        onOpenChange={(open) => {
                            if (!open) removeToast(toast.id);
                        }}
                    >
                        <div className="flex flex-col gap-1">
                            {toast.title && <ToastTitle>{toast.title}</ToastTitle>}
                            {toast.description && (
                                <ToastDescription>{toast.description}</ToastDescription>
                            )}
                        </div>
                        <ToastClose />
                    </Toast>
                ))}
                <ToastViewport />
            </ToastProvider>
        </ToastContext.Provider>
    );
}

export function useToast() {
    const context = React.useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within a ToastContextProvider');
    }
    return context;
}

export default Toast;
