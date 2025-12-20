/**
 * Order Detail Page
 * 
 * Single order view with items and tracking.
 */
'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { ArrowLeft, FileText, Truck } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { useOrder } from '@/lib/api/queries';
import type { OrderItem } from '@/types';

export default function OrderDetailPage() {
    const params = useParams();
    const orderId = params.id as string;
    const { data: order, isLoading } = useOrder(orderId);

    if (isLoading) {
        return (
            <div className="space-y-6">
                <Skeleton className="h-10 w-64" />
                <div className="grid gap-6 lg:grid-cols-3">
                    <div className="lg:col-span-2 space-y-6">
                        <Skeleton className="h-64" />
                        <Skeleton className="h-32" />
                    </div>
                    <Skeleton className="h-48" />
                </div>
            </div>
        );
    }

    if (!order) {
        return <div className="text-center py-8">Order not found</div>;
    }

    const statusVariants: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
        delivered: 'success',
        shipped: 'success',
        processing: 'warning',
        confirmed: 'warning',
        pending: 'default',
        cancelled: 'error',
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Link href="/account/orders">
                    <Button variant="ghost" size="sm">
                        <ArrowLeft className="h-4 w-4" />
                        Back
                    </Button>
                </Link>
                <div className="flex-1">
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl font-bold text-gray-900">
                            Order #{order.orderNumber}
                        </h1>
                        <Badge variant={statusVariants[order.status] || 'default'}>
                            {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                        </Badge>
                    </div>
                    <p className="text-sm text-gray-500">
                        Placed on {new Date(order.createdAt).toLocaleDateString('en-SG', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                        })}
                    </p>
                </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Order Items */}
                <div className="lg:col-span-2 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Order Items</CardTitle>
                        </CardHeader>
                        <CardContent className="divide-y divide-gray-200">
                            {order.items.map((item: OrderItem) => (
                                <div key={item.id} className="flex gap-4 py-4 first:pt-0 last:pb-0">
                                    {/* Image */}
                                    <div className="relative h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100">
                                        {item.product.imageUrl ? (
                                            <Image
                                                src={item.product.imageUrl}
                                                alt={item.product.name}
                                                fill
                                                sizes="80px"
                                                className="object-cover"
                                            />
                                        ) : (
                                            <div className="flex h-full items-center justify-center text-gray-400">
                                                📦
                                            </div>
                                        )}
                                    </div>

                                    {/* Details */}
                                    <div className="flex-1">
                                        <Link
                                            href={`/products/${item.product.slug}`}
                                            className="font-medium text-gray-900 hover:text-primary-600"
                                        >
                                            {item.product.name}
                                        </Link>
                                        {item.variant && (
                                            <p className="text-sm text-gray-500">
                                                {Object.values(item.variant.options).join(', ')}
                                            </p>
                                        )}
                                        <p className="text-sm text-gray-500">
                                            S${parseFloat(item.unitPrice).toFixed(2)} × {item.quantity}
                                        </p>
                                    </div>

                                    {/* Line Total */}
                                    <div className="text-right">
                                        <p className="font-medium text-gray-900">
                                            S${parseFloat(item.lineTotal).toFixed(2)}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>

                    {/* Shipping Address */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Shipping Address</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-sm text-gray-600">
                                <p className="font-medium text-gray-900">
                                    {order.shippingAddress.recipientName}
                                </p>
                                <p>{order.shippingAddress.addressLine1}</p>
                                {order.shippingAddress.addressLine2 && (
                                    <p>{order.shippingAddress.addressLine2}</p>
                                )}
                                {order.shippingAddress.unitNumber && (
                                    <p>Unit: {order.shippingAddress.unitNumber}</p>
                                )}
                                <p>Singapore {order.shippingAddress.postalCode}</p>
                                <p>{order.shippingAddress.phone}</p>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Order Summary Sidebar */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Order Summary</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Subtotal</span>
                                <span>S${parseFloat(order.subtotal).toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Shipping</span>
                                <span>S${parseFloat(order.shippingAmount).toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">GST (9%)</span>
                                <span>S${parseFloat(order.gstAmount).toFixed(2)}</span>
                            </div>
                            <div className="border-t border-gray-200 pt-3">
                                <div className="flex justify-between font-semibold">
                                    <span>Total</span>
                                    <span>S${parseFloat(order.totalAmount).toFixed(2)}</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Actions */}
                    <Card>
                        <CardContent className="space-y-3 p-4">
                            <Button variant="outline" className="w-full">
                                <FileText className="h-4 w-4" />
                                Download Invoice
                            </Button>
                            {order.status === 'shipped' && (
                                <Button variant="outline" className="w-full">
                                    <Truck className="h-4 w-4" />
                                    Track Order
                                </Button>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
