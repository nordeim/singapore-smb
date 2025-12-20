/**
 * Mobile Navigation Component
 * 
 * Slide-out drawer for mobile navigation.
 */
'use client';

import * as React from 'react';
import Link from 'next/link';
import * as Dialog from '@radix-ui/react-dialog';
import { X, ShoppingCart, User, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { User as UserType } from '@/types';

interface MobileNavProps {
    open: boolean;
    onClose: () => void;
    navigation: { name: string; href: string }[];
    isAuthenticated: boolean;
    user: UserType | null;
    onLogout: () => void;
}

export function MobileNav({
    open,
    onClose,
    navigation,
    isAuthenticated,
    user,
    onLogout,
}: MobileNavProps) {
    return (
        <Dialog.Root open={open} onOpenChange={onClose}>
            <Dialog.Portal>
                <Dialog.Overlay className="fixed inset-0 z-50 bg-black/50" />
                <Dialog.Content className="fixed inset-y-0 right-0 z-50 w-full max-w-xs bg-white shadow-xl">
                    {/* Header */}
                    <div className="flex h-16 items-center justify-between border-b border-gray-200 px-4">
                        <span className="text-lg font-semibold">Menu</span>
                        <Dialog.Close asChild>
                            <button
                                className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-600 hover:bg-gray-100"
                                aria-label="Close menu"
                            >
                                <X className="h-5 w-5" />
                            </button>
                        </Dialog.Close>
                    </div>

                    {/* User Section */}
                    {isAuthenticated && user ? (
                        <div className="border-b border-gray-200 p-4">
                            <div className="flex items-center gap-3">
                                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-100 text-primary-600">
                                    <User className="h-5 w-5" />
                                </div>
                                <div>
                                    <p className="font-medium text-gray-900">
                                        {user.firstName} {user.lastName}
                                    </p>
                                    <p className="text-sm text-gray-500">{user.email}</p>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="border-b border-gray-200 p-4 space-y-2">
                            <Link href="/login" onClick={onClose}>
                                <Button variant="outline" className="w-full">
                                    Sign In
                                </Button>
                            </Link>
                            <Link href="/register" onClick={onClose}>
                                <Button className="w-full">
                                    Register
                                </Button>
                            </Link>
                        </div>
                    )}

                    {/* Navigation Links */}
                    <nav className="p-4">
                        <ul className="space-y-1">
                            {navigation.map((item) => (
                                <li key={item.name}>
                                    <Link
                                        href={item.href}
                                        onClick={onClose}
                                        className="flex items-center justify-between rounded-lg px-3 py-2.5 text-gray-700 hover:bg-gray-100"
                                    >
                                        <span>{item.name}</span>
                                        <ChevronRight className="h-4 w-4 text-gray-400" />
                                    </Link>
                                </li>
                            ))}

                            {/* Cart Link */}
                            <li>
                                <Link
                                    href="/cart"
                                    onClick={onClose}
                                    className="flex items-center justify-between rounded-lg px-3 py-2.5 text-gray-700 hover:bg-gray-100"
                                >
                                    <span className="flex items-center gap-2">
                                        <ShoppingCart className="h-4 w-4" />
                                        Cart
                                    </span>
                                    <ChevronRight className="h-4 w-4 text-gray-400" />
                                </Link>
                            </li>
                        </ul>
                    </nav>

                    {/* Account Links (for authenticated users) */}
                    {isAuthenticated && (
                        <div className="border-t border-gray-200 p-4">
                            <ul className="space-y-1">
                                <li>
                                    <Link
                                        href="/account"
                                        onClick={onClose}
                                        className="flex items-center justify-between rounded-lg px-3 py-2.5 text-gray-700 hover:bg-gray-100"
                                    >
                                        <span>My Account</span>
                                        <ChevronRight className="h-4 w-4 text-gray-400" />
                                    </Link>
                                </li>
                                <li>
                                    <Link
                                        href="/account/orders"
                                        onClick={onClose}
                                        className="flex items-center justify-between rounded-lg px-3 py-2.5 text-gray-700 hover:bg-gray-100"
                                    >
                                        <span>Orders</span>
                                        <ChevronRight className="h-4 w-4 text-gray-400" />
                                    </Link>
                                </li>
                                <li>
                                    <button
                                        onClick={() => {
                                            onLogout();
                                            onClose();
                                        }}
                                        className="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-error-600 hover:bg-error-50"
                                    >
                                        <span>Sign Out</span>
                                    </button>
                                </li>
                            </ul>
                        </div>
                    )}
                </Dialog.Content>
            </Dialog.Portal>
        </Dialog.Root>
    );
}

export default MobileNav;
