/**
 * Checkout Success Page
 * 
 * Order confirmation after successful checkout.
 */
import Link from 'next/link';
import { CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SuccessPageProps {
    searchParams: { order?: string };
}

export default function CheckoutSuccessPage({ searchParams }: SuccessPageProps) {
    const orderId = searchParams.order;

    return (
        <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6 lg:px-8">
            <div className="text-center">
                {/* Success Icon */}
                <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-success-100">
                    <CheckCircle className="h-12 w-12 text-success-600" />
                </div>

                {/* Message */}
                <h1 className="mt-6 text-3xl font-bold text-gray-900">
                    Order Confirmed!
                </h1>
                <p className="mt-4 text-lg text-gray-600">
                    Thank you for your order. We&apos;ve sent a confirmation to your email.
                </p>

                {/* Order Number */}
                {orderId && (
                    <div className="mt-8 rounded-lg bg-gray-50 p-4">
                        <p className="text-sm text-gray-500">Order Number</p>
                        <p className="text-lg font-semibold text-gray-900">{orderId}</p>
                    </div>
                )}

                {/* Info */}
                <div className="mt-8 space-y-4 text-left">
                    <div className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-4">
                        <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-primary-100 text-primary-600">
                            📧
                        </div>
                        <div>
                            <p className="font-medium text-gray-900">Confirmation Email</p>
                            <p className="text-sm text-gray-500">
                                You&apos;ll receive an email with your order details and tracking information.
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-4">
                        <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-primary-100 text-primary-600">
                            📦
                        </div>
                        <div>
                            <p className="font-medium text-gray-900">Shipping</p>
                            <p className="text-sm text-gray-500">
                                Your order will be processed and shipped within 1-3 business days.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
                    {orderId && (
                        <Link href={`/account/orders/${orderId}`}>
                            <Button variant="outline" size="lg" className="w-full sm:w-auto">
                                View Order
                            </Button>
                        </Link>
                    )}
                    <Link href="/products">
                        <Button size="lg" className="w-full sm:w-auto">
                            Continue Shopping
                        </Button>
                    </Link>
                </div>
            </div>
        </div>
    );
}

export const metadata = {
    title: 'Order Confirmed',
};
