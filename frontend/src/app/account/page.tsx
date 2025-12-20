/**
 * Account Dashboard Page
 * 
 * User account overview with recent orders.
 */
'use client';

import Link from 'next/link';
import { Package, Settings, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { useUser, useOrders } from '@/lib/api/queries';

export default function AccountPage() {
    const { data: user, isLoading: userLoading } = useUser();
    const { data: ordersResponse, isLoading: ordersLoading } = useOrders({ pageSize: 3 });
    const recentOrders = ordersResponse?.results || [];

    if (userLoading) {
        return (
            <div className="space-y-8">
                <div className="space-y-2">
                    <Skeleton className="h-8 w-48" />
                    <Skeleton className="h-4 w-32" />
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                    <Skeleton className="h-24" />
                    <Skeleton className="h-24" />
                </div>
                <Skeleton className="h-64" />
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Welcome */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900">
                    Welcome back, {user?.firstName || 'User'}!
                </h1>
                <p className="mt-1 text-gray-600">{user?.email}</p>
            </div>

            {/* Quick Links */}
            <div className="grid gap-4 sm:grid-cols-2">
                <Link href="/account/orders">
                    <Card className="h-full transition-shadow hover:shadow-md">
                        <CardContent className="flex items-center gap-4 p-6">
                            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary-100">
                                <Package className="h-6 w-6 text-primary-600" />
                            </div>
                            <div className="flex-1">
                                <h3 className="font-medium text-gray-900">Orders</h3>
                                <p className="text-sm text-gray-500">View order history</p>
                            </div>
                            <ChevronRight className="h-5 w-5 text-gray-400" />
                        </CardContent>
                    </Card>
                </Link>

                <Link href="/account/settings">
                    <Card className="h-full transition-shadow hover:shadow-md">
                        <CardContent className="flex items-center gap-4 p-6">
                            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
                                <Settings className="h-6 w-6 text-gray-600" />
                            </div>
                            <div className="flex-1">
                                <h3 className="font-medium text-gray-900">Settings</h3>
                                <p className="text-sm text-gray-500">Manage your account</p>
                            </div>
                            <ChevronRight className="h-5 w-5 text-gray-400" />
                        </CardContent>
                    </Card>
                </Link>
            </div>

            {/* Recent Orders */}
            <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle>Recent Orders</CardTitle>
                    <Link href="/account/orders">
                        <Button variant="ghost" size="sm">
                            View All
                        </Button>
                    </Link>
                </CardHeader>
                <CardContent>
                    {ordersLoading ? (
                        <div className="space-y-4">
                            <Skeleton className="h-16" />
                            <Skeleton className="h-16" />
                        </div>
                    ) : recentOrders.length === 0 ? (
                        <div className="py-8 text-center text-gray-500">
                            <Package className="mx-auto h-12 w-12 text-gray-400" />
                            <p className="mt-2">No orders yet</p>
                            <Link href="/products" className="mt-4 inline-block">
                                <Button variant="outline" size="sm">
                                    Start Shopping
                                </Button>
                            </Link>
                        </div>
                    ) : (
                        <div className="divide-y divide-gray-200">
                            {recentOrders.map((order) => (
                                <Link
                                    key={order.id}
                                    href={`/account/orders/${order.id}`}
                                    className="flex items-center justify-between py-4 hover:bg-gray-50 -mx-6 px-6"
                                >
                                    <div>
                                        <p className="font-medium text-gray-900">
                                            Order #{order.orderNumber}
                                        </p>
                                        <p className="text-sm text-gray-500">
                                            {new Date(order.createdAt).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <StatusBadge status={order.status} />
                                        <span className="font-medium text-gray-900">
                                            S${parseFloat(order.totalAmount).toFixed(2)}
                                        </span>
                                        <ChevronRight className="h-5 w-5 text-gray-400" />
                                    </div>
                                </Link>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}

function StatusBadge({ status }: { status: string }) {
    const variants: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
        delivered: 'success',
        shipped: 'success',
        processing: 'warning',
        confirmed: 'warning',
        pending: 'default',
        cancelled: 'error',
    };

    return (
        <Badge variant={variants[status] || 'default'} size="sm">
            {status.charAt(0).toUpperCase() + status.slice(1)}
        </Badge>
    );
}
