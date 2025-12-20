/**
 * Checkout Page
 * 
 * Multi-step checkout flow: Address → Payment → Review.
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Check } from 'lucide-react';
import { clsx } from 'clsx';
import { Button } from '@/components/ui/button';
import { AddressForm } from '@/components/checkout/address-form';
import { PaymentForm } from '@/components/checkout/payment-form';
import { CheckoutSummary } from '@/components/checkout/checkout-summary';
import { useCart } from '@/lib/hooks/useCart';
import { useCheckout } from '@/lib/api/mutations';
import type { AddressFormData } from '@/types';

type CheckoutStep = 'address' | 'payment' | 'review';

const steps: { id: CheckoutStep; name: string }[] = [
    { id: 'address', name: 'Shipping' },
    { id: 'payment', name: 'Payment' },
    { id: 'review', name: 'Review' },
];

export default function CheckoutPage() {
    const router = useRouter();
    const { cart, items, totals, isLoading } = useCart();
    const checkoutMutation = useCheckout();

    const [currentStep, setCurrentStep] = useState<CheckoutStep>('address');
    const [shippingAddress, setShippingAddress] = useState<AddressFormData | null>(null);
    const [paymentMethod, setPaymentMethod] = useState<'card' | 'paynow'>('card');
    const [paymentComplete, setPaymentComplete] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Redirect if cart is empty
    if (!isLoading && items.length === 0) {
        router.push('/cart');
        return null;
    }

    const handleAddressSubmit = (data: AddressFormData) => {
        setShippingAddress(data);
        setCurrentStep('payment');
    };

    const handlePaymentComplete = () => {
        setPaymentComplete(true);
        setCurrentStep('review');
    };

    const handlePlaceOrder = async () => {
        if (!shippingAddress || !cart) return;

        setError(null);
        try {
            const order = await checkoutMutation.mutateAsync({
                shippingAddressId: cart.id, // Using cart.id as placeholder since we create inline address
                paymentMethod,
                notes: '',
            });

            router.push(`/checkout/success?order=${order.id}`);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to place order');
        }
    };

    const getCurrentStepIndex = () => steps.findIndex((s) => s.id === currentStep);

    return (
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            {/* Step Indicator */}
            <nav className="mb-8">
                <ol className="flex items-center justify-center gap-4">
                    {steps.map((step, index) => {
                        const isComplete = index < getCurrentStepIndex();
                        const isCurrent = step.id === currentStep;

                        return (
                            <li key={step.id} className="flex items-center gap-2">
                                <div
                                    className={clsx(
                                        'flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium',
                                        isComplete
                                            ? 'bg-primary-600 text-white'
                                            : isCurrent
                                                ? 'border-2 border-primary-600 text-primary-600'
                                                : 'border-2 border-gray-300 text-gray-400'
                                    )}
                                >
                                    {isComplete ? <Check className="h-4 w-4" /> : index + 1}
                                </div>
                                <span
                                    className={clsx(
                                        'hidden text-sm font-medium sm:inline',
                                        isCurrent ? 'text-primary-600' : 'text-gray-500'
                                    )}
                                >
                                    {step.name}
                                </span>
                                {index < steps.length - 1 && (
                                    <div className="ml-2 h-0.5 w-8 bg-gray-200 sm:w-16" />
                                )}
                            </li>
                        );
                    })}
                </ol>
            </nav>

            <div className="grid gap-8 lg:grid-cols-3">
                {/* Main Content */}
                <div className="lg:col-span-2">
                    {error && (
                        <div className="mb-4 rounded-lg bg-error-50 p-4 text-sm text-error-700">
                            {error}
                        </div>
                    )}

                    {/* Address Step */}
                    {currentStep === 'address' && (
                        <div className="rounded-xl border border-gray-200 bg-white p-6">
                            <h2 className="mb-6 text-lg font-semibold text-gray-900">
                                Shipping Address
                            </h2>
                            <AddressForm
                                onSubmit={handleAddressSubmit}
                                defaultValues={shippingAddress || undefined}
                            />
                        </div>
                    )}

                    {/* Payment Step */}
                    {currentStep === 'payment' && (
                        <div className="rounded-xl border border-gray-200 bg-white p-6">
                            <h2 className="mb-6 text-lg font-semibold text-gray-900">
                                Payment Method
                            </h2>
                            <PaymentForm
                                paymentMethod={paymentMethod}
                                onPaymentMethodChange={setPaymentMethod}
                                onPaymentComplete={handlePaymentComplete}
                                onBack={() => setCurrentStep('address')}
                            />
                        </div>
                    )}

                    {/* Review Step */}
                    {currentStep === 'review' && (
                        <div className="space-y-6">
                            <div className="rounded-xl border border-gray-200 bg-white p-6">
                                <h2 className="mb-4 text-lg font-semibold text-gray-900">
                                    Shipping Address
                                </h2>
                                {shippingAddress && (
                                    <div className="text-sm text-gray-600">
                                        <p className="font-medium text-gray-900">
                                            {shippingAddress.recipientName}
                                        </p>
                                        <p>{shippingAddress.addressLine1}</p>
                                        {shippingAddress.addressLine2 && (
                                            <p>{shippingAddress.addressLine2}</p>
                                        )}
                                        {shippingAddress.unitNumber && (
                                            <p>Unit: {shippingAddress.unitNumber}</p>
                                        )}
                                        <p>Singapore {shippingAddress.postalCode}</p>
                                        <p>{shippingAddress.phone}</p>
                                    </div>
                                )}
                            </div>

                            <div className="rounded-xl border border-gray-200 bg-white p-6">
                                <h2 className="mb-4 text-lg font-semibold text-gray-900">
                                    Payment Method
                                </h2>
                                <p className="text-sm text-gray-600">
                                    {paymentMethod === 'card' ? 'Credit/Debit Card' : 'PayNow'}
                                </p>
                            </div>

                            <Button
                                onClick={handlePlaceOrder}
                                loading={checkoutMutation.isPending}
                                size="lg"
                                className="w-full"
                            >
                                Place Order
                            </Button>
                        </div>
                    )}
                </div>

                {/* Order Summary Sidebar */}
                <div className="lg:col-span-1">
                    <CheckoutSummary items={items} totals={totals} />
                </div>
            </div>
        </div>
    );
}
