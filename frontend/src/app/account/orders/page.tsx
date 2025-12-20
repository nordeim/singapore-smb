/**
 * Orders List Page
 * 
 * Paginated order history.
 */
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { useOrders } from '@/lib/api/queries';

export default function OrdersPage() {
    const [page, setPage] = useState(1);
    const pageSize = 10;

    const { data: ordersResponse, isLoading } = useOrders({ page, pageSize });
    const orders = ordersResponse?.results || [];
    const totalPages = ordersResponse ? Math.ceil(ordersResponse.count / pageSize) : 0;

    if (isLoading) {
        return (
            <div className="space-y-6">
                <Skeleton className="h-8 w-48" />
                <Skeleton className="h-64" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">Order History</h1>

            {orders.length === 0 ? (
                <div className="py-16 text-center">
                    <p className="text-gray-500">No orders found</p>
                </div>
            ) : (
                <>
                    <Card>
                        <CardContent className="divide-y divide-gray-200 p-0">
                            {orders.map((order) => (
                                <Link
                                    key={order.id}
                                    href={`/account/orders/${order.id}`}
                                    className="flex items-center justify-between p-4 hover:bg-gray-50"
                                >
                                    <div className="space-y-1">
                                        <div className="flex items-center gap-3">
                                            <span className="font-medium text-gray-900">
                                                #{order.orderNumber}
                                            </span>
                                            <StatusBadge status={order.status} />
                                        </div>
                                        <p className="text-sm text-gray-500">
                                            {new Date(order.createdAt).toLocaleDateString('en-SG', {
                                                year: 'numeric',
                                                month: 'long',
                                                day: 'numeric',
                                            })}
                                        </p>
                                        <p className="text-sm text-gray-500">
                                            {order.items.length} item{order.items.length !== 1 && 's'}
                                        </p>
                                    </div>

                                    <div className="flex items-center gap-4">
                                        <span className="text-lg font-semibold text-gray-900">
                                            S${parseFloat(order.totalAmount).toFixed(2)}
                                        </span>
                                        <ChevronRight className="h-5 w-5 text-gray-400" />
                                    </div>
                                </Link>
                            ))}
                        </CardContent>
                    </Card>

                    {totalPages > 1 && (
                        <div className="flex justify-center gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setPage((p) => Math.max(1, p - 1))}
                                disabled={page === 1}
                            >
                                Previous
                            </Button>
                            <span className="flex items-center px-4 text-sm text-gray-600">
                                Page {page} of {totalPages}
                            </span>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                                disabled={page === totalPages}
                            >
                                Next
                            </Button>
                        </div>
                    )}
                </>
            )}
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
