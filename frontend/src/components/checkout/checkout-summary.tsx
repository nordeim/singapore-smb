/**
 * Checkout Summary Component
 * 
 * Order summary for the checkout sidebar.
 */
import Image from 'next/image';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import type { CartItem } from '@/types';

interface CheckoutSummaryProps {
    items: CartItem[];
    totals: {
        subtotal: number;
        gstAmount: number;
        total: number;
        itemCount: number;
    };
}

export function CheckoutSummary({ items, totals }: CheckoutSummaryProps) {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Order Summary</CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Items */}
                <div className="max-h-64 space-y-3 overflow-y-auto">
                    {items.map((item) => (
                        <div key={item.id} className="flex gap-3">
                            {/* Image */}
                            <div className="relative h-16 w-16 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100">
                                {item.product.imageUrl ? (
                                    <Image
                                        src={item.product.imageUrl}
                                        alt={item.product.name}
                                        fill
                                        sizes="64px"
                                        className="object-cover"
                                    />
                                ) : (
                                    <div className="flex h-full items-center justify-center text-gray-400">
                                        📦
                                    </div>
                                )}
                            </div>

                            {/* Details */}
                            <div className="flex-1 min-w-0">
                                <p className="truncate text-sm font-medium text-gray-900">
                                    {item.product.name}
                                </p>
                                {item.variant && (
                                    <p className="text-xs text-gray-500">
                                        {Object.values(item.variant.options).join(', ')}
                                    </p>
                                )}
                                <p className="text-xs text-gray-500">Qty: {item.quantity}</p>
                            </div>

                            {/* Price */}
                            <p className="text-sm font-medium text-gray-900">
                                S${parseFloat(item.lineTotal).toFixed(2)}
                            </p>
                        </div>
                    ))}
                </div>

                <div className="border-t border-gray-200 pt-4 space-y-2">
                    {/* Subtotal */}
                    <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Subtotal</span>
                        <span className="font-medium">S${totals.subtotal.toFixed(2)}</span>
                    </div>

                    {/* Shipping */}
                    <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Shipping</span>
                        <span className="text-success-600">Calculated at next step</span>
                    </div>

                    {/* GST */}
                    <div className="flex justify-between text-sm">
                        <span className="text-gray-600">GST (9%)</span>
                        <span className="font-medium">S${totals.gstAmount.toFixed(2)}</span>
                    </div>
                </div>

                {/* Total */}
                <div className="border-t border-gray-200 pt-4">
                    <div className="flex justify-between">
                        <span className="text-lg font-semibold text-gray-900">Total</span>
                        <span className="text-xl font-bold text-gray-900">
                            S${totals.total.toFixed(2)}
                        </span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

export default CheckoutSummary;
