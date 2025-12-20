/**
 * Cart Summary Component
 * 
 * Cart totals with subtotal, GST, and total.
 */
import * as React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

interface CartSummaryProps {
    subtotal: number;
    gstAmount: number;
    total: number;
    itemCount: number;
    isLoading?: boolean;
}

export function CartSummary({
    subtotal,
    gstAmount,
    total,
    itemCount,
    isLoading = false,
}: CartSummaryProps) {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Order Summary</CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Subtotal */}
                <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">
                        Subtotal ({itemCount} {itemCount === 1 ? 'item' : 'items'})
                    </span>
                    <span className="font-medium text-gray-900">
                        S${subtotal.toFixed(2)}
                    </span>
                </div>

                {/* GST */}
                <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">GST (9%)</span>
                    <span className="font-medium text-gray-900">
                        S${gstAmount.toFixed(2)}
                    </span>
                </div>

                {/* Shipping */}
                <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Shipping</span>
                    <span className="font-medium text-success-600">
                        Calculated at checkout
                    </span>
                </div>

                {/* Divider */}
                <div className="border-t border-gray-200" />

                {/* Total */}
                <div className="flex items-center justify-between">
                    <span className="text-lg font-semibold text-gray-900">Total</span>
                    <span className="text-xl font-bold text-gray-900">
                        S${total.toFixed(2)}
                    </span>
                </div>

                {/* GST Note */}
                <p className="text-xs text-gray-500">
                    All prices include GST where applicable
                </p>
            </CardContent>

            <CardFooter className="flex flex-col gap-3">
                <Link href="/checkout" className="w-full">
                    <Button
                        className="w-full"
                        size="lg"
                        disabled={itemCount === 0 || isLoading}
                    >
                        Proceed to Checkout
                    </Button>
                </Link>
                <Link href="/products" className="w-full">
                    <Button variant="outline" className="w-full">
                        Continue Shopping
                    </Button>
                </Link>
            </CardFooter>
        </Card>
    );
}

export default CartSummary;
