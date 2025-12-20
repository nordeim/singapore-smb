/**
 * Header Component
 * 
 * Site header with logo, navigation, search, cart, and user menu.
 */
'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ShoppingCart, User, Menu, Search, X } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/lib/hooks/useAuth';
import { useCart } from '@/lib/hooks/useCart';
import { useIsMobile } from '@/lib/hooks/useMediaQuery';
import { MobileNav } from './mobile-nav';

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

const navigation = [
    { name: 'Products', href: '/products' },
    { name: 'Categories', href: '/categories' },
];

export function Header() {
    const pathname = usePathname();
    const { user, isAuthenticated, logout, isLoading } = useAuth();
    const { totals } = useCart();
    const isMobile = useIsMobile();
    const [mobileNavOpen, setMobileNavOpen] = React.useState(false);
    const [searchOpen, setSearchOpen] = React.useState(false);

    return (
        <header className="sticky top-0 z-40 w-full border-b border-gray-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div className="flex h-16 items-center justify-between">
                    {/* Left: Logo & Nav */}
                    <div className="flex items-center gap-8">
                        {/* Logo */}
                        <Link href="/" className="flex items-center gap-2">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600 text-white font-bold">
                                S
                            </div>
                            <span className="hidden font-semibold text-gray-900 sm:block">
                                Singapore SMB
                            </span>
                        </Link>

                        {/* Desktop Navigation */}
                        {!isMobile && (
                            <nav className="hidden md:flex items-center gap-6">
                                {navigation.map((item) => (
                                    <Link
                                        key={item.name}
                                        href={item.href}
                                        className={cn(
                                            'text-sm font-medium transition-colors hover:text-primary-600',
                                            pathname === item.href
                                                ? 'text-primary-600'
                                                : 'text-gray-600'
                                        )}
                                    >
                                        {item.name}
                                    </Link>
                                ))}
                            </nav>
                        )}
                    </div>

                    {/* Center: Search (Desktop) */}
                    {!isMobile && (
                        <div className="hidden md:flex flex-1 items-center justify-center px-8">
                            <div className="w-full max-w-md relative">
                                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                                <input
                                    type="search"
                                    placeholder="Search products..."
                                    className="h-9 w-full rounded-lg border border-gray-300 bg-gray-50 pl-10 pr-4 text-sm placeholder:text-gray-400 focus:border-primary-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-primary-500"
                                />
                            </div>
                        </div>
                    )}

                    {/* Right: Actions */}
                    <div className="flex items-center gap-2">
                        {/* Mobile Search Toggle */}
                        {isMobile && (
                            <button
                                onClick={() => setSearchOpen(!searchOpen)}
                                className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-600 hover:bg-gray-100"
                                aria-label="Search"
                            >
                                {searchOpen ? (
                                    <X className="h-5 w-5" />
                                ) : (
                                    <Search className="h-5 w-5" />
                                )}
                            </button>
                        )}

                        {/* Cart */}
                        <Link
                            href="/cart"
                            className="relative flex h-9 w-9 items-center justify-center rounded-lg text-gray-600 hover:bg-gray-100"
                            aria-label="Shopping cart"
                        >
                            <ShoppingCart className="h-5 w-5" />
                            {totals.itemCount > 0 && (
                                <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary-600 text-xs font-medium text-white">
                                    {totals.itemCount > 99 ? '99+' : totals.itemCount}
                                </span>
                            )}
                        </Link>

                        {/* User Menu */}
                        {isAuthenticated ? (
                            <DropdownMenu.Root>
                                <DropdownMenu.Trigger asChild>
                                    <button
                                        className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-600 hover:bg-gray-100"
                                        aria-label="User menu"
                                    >
                                        <User className="h-5 w-5" />
                                    </button>
                                </DropdownMenu.Trigger>
                                <DropdownMenu.Portal>
                                    <DropdownMenu.Content
                                        className="z-50 min-w-[180px] rounded-lg border border-gray-200 bg-white p-1 shadow-lg"
                                        sideOffset={8}
                                        align="end"
                                    >
                                        <div className="px-3 py-2 border-b border-gray-100">
                                            <p className="text-sm font-medium text-gray-900">
                                                {user?.firstName} {user?.lastName}
                                            </p>
                                            <p className="text-xs text-gray-500">{user?.email}</p>
                                        </div>
                                        <DropdownMenu.Item asChild>
                                            <Link
                                                href="/account"
                                                className="flex w-full items-center rounded px-3 py-2 text-sm text-gray-700 outline-none hover:bg-gray-100"
                                            >
                                                My Account
                                            </Link>
                                        </DropdownMenu.Item>
                                        <DropdownMenu.Item asChild>
                                            <Link
                                                href="/account/orders"
                                                className="flex w-full items-center rounded px-3 py-2 text-sm text-gray-700 outline-none hover:bg-gray-100"
                                            >
                                                Orders
                                            </Link>
                                        </DropdownMenu.Item>
                                        <DropdownMenu.Separator className="my-1 h-px bg-gray-100" />
                                        <DropdownMenu.Item
                                            className="flex w-full cursor-pointer items-center rounded px-3 py-2 text-sm text-error-600 outline-none hover:bg-error-50"
                                            onClick={() => logout()}
                                        >
                                            Sign Out
                                        </DropdownMenu.Item>
                                    </DropdownMenu.Content>
                                </DropdownMenu.Portal>
                            </DropdownMenu.Root>
                        ) : (
                            <div className="hidden sm:flex items-center gap-2">
                                <Link href="/login">
                                    <Button variant="ghost" size="sm">
                                        Sign In
                                    </Button>
                                </Link>
                                <Link href="/register">
                                    <Button size="sm">
                                        Register
                                    </Button>
                                </Link>
                            </div>
                        )}

                        {/* Mobile Menu Toggle */}
                        {isMobile && (
                            <button
                                onClick={() => setMobileNavOpen(true)}
                                className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-600 hover:bg-gray-100 md:hidden"
                                aria-label="Open menu"
                            >
                                <Menu className="h-5 w-5" />
                            </button>
                        )}
                    </div>
                </div>

                {/* Mobile Search Bar */}
                {isMobile && searchOpen && (
                    <div className="pb-4">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                            <input
                                type="search"
                                placeholder="Search products..."
                                className="h-10 w-full rounded-lg border border-gray-300 bg-gray-50 pl-10 pr-4 text-sm placeholder:text-gray-400 focus:border-primary-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-primary-500"
                                autoFocus
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Mobile Navigation Drawer */}
            <MobileNav
                open={mobileNavOpen}
                onClose={() => setMobileNavOpen(false)}
                navigation={navigation}
                isAuthenticated={isAuthenticated}
                user={user}
                onLogout={logout}
            />
        </header>
    );
}

export default Header;
