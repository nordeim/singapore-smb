/**
 * Account Layout
 * 
 * Sidebar layout for account section.
 */
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { User, Package, Settings, LogOut } from 'lucide-react';
import { clsx } from 'clsx';
import { useAuth } from '@/lib/hooks/useAuth';

const navigation = [
    { name: 'Dashboard', href: '/account', icon: User },
    { name: 'Orders', href: '/account/orders', icon: Package },
    { name: 'Settings', href: '/account/settings', icon: Settings },
];

export default function AccountLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();
    const { logout } = useAuth();

    return (
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            <div className="flex flex-col gap-8 lg:flex-row">
                {/* Sidebar */}
                <aside className="w-full lg:w-64 flex-shrink-0">
                    <nav className="space-y-1 rounded-xl border border-gray-200 bg-white p-2">
                        {navigation.map((item) => {
                            const isActive =
                                item.href === '/account'
                                    ? pathname === '/account'
                                    : pathname.startsWith(item.href);

                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={clsx(
                                        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                                        isActive
                                            ? 'bg-primary-50 text-primary-700'
                                            : 'text-gray-600 hover:bg-gray-50'
                                    )}
                                >
                                    <item.icon className="h-5 w-5" />
                                    {item.name}
                                </Link>
                            );
                        })}

                        <hr className="my-2 border-gray-200" />

                        <button
                            onClick={() => logout()}
                            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-error-600 transition-colors hover:bg-error-50"
                        >
                            <LogOut className="h-5 w-5" />
                            Sign Out
                        </button>
                    </nav>
                </aside>

                {/* Main Content */}
                <main className="flex-1">{children}</main>
            </div>
        </div>
    );
}
