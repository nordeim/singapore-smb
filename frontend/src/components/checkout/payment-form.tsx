/**
 * Payment Form Component
 * 
 * Payment method selection with Stripe and PayNow.
 */
'use client';

import { useState } from 'react';
import { CreditCard, QrCode } from 'lucide-react';
import { clsx } from 'clsx';
import { Button } from '@/components/ui/button';
import { PayNowQR } from './paynow-qr';

interface PaymentFormProps {
    paymentMethod: 'card' | 'paynow';
    onPaymentMethodChange: (method: 'card' | 'paynow') => void;
    onPaymentComplete: () => void;
    onBack: () => void;
}

export function PaymentForm({
    paymentMethod,
    onPaymentMethodChange,
    onPaymentComplete,
    onBack,
}: PaymentFormProps) {
    const [isProcessing, setIsProcessing] = useState(false);
    const [cardError, setCardError] = useState<string | null>(null);

    const handleCardSubmit = async () => {
        setIsProcessing(true);
        setCardError(null);

        try {
            // In a real implementation, this would use Stripe Elements
            // For now, we simulate a successful payment
            await new Promise((resolve) => setTimeout(resolve, 1500));
            onPaymentComplete();
        } catch (err) {
            setCardError(err instanceof Error ? err.message : 'Payment failed');
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Payment Method Selection */}
            <div className="grid gap-4 sm:grid-cols-2">
                <button
                    type="button"
                    onClick={() => onPaymentMethodChange('card')}
                    className={clsx(
                        'flex items-center gap-3 rounded-lg border-2 p-4 text-left transition-colors',
                        paymentMethod === 'card'
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200 hover:border-gray-300'
                    )}
                >
                    <CreditCard
                        className={clsx(
                            'h-6 w-6',
                            paymentMethod === 'card' ? 'text-primary-600' : 'text-gray-400'
                        )}
                    />
                    <div>
                        <p className="font-medium text-gray-900">Credit/Debit Card</p>
                        <p className="text-sm text-gray-500">Visa, Mastercard, AMEX</p>
                    </div>
                </button>

                <button
                    type="button"
                    onClick={() => onPaymentMethodChange('paynow')}
                    className={clsx(
                        'flex items-center gap-3 rounded-lg border-2 p-4 text-left transition-colors',
                        paymentMethod === 'paynow'
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200 hover:border-gray-300'
                    )}
                >
                    <QrCode
                        className={clsx(
                            'h-6 w-6',
                            paymentMethod === 'paynow' ? 'text-primary-600' : 'text-gray-400'
                        )}
                    />
                    <div>
                        <p className="font-medium text-gray-900">PayNow</p>
                        <p className="text-sm text-gray-500">Scan QR to pay</p>
                    </div>
                </button>
            </div>

            {/* Card Form */}
            {paymentMethod === 'card' && (
                <div className="space-y-4">
                    <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                        <p className="mb-4 text-sm text-gray-600">
                            Stripe Elements would be integrated here for PCI compliance.
                        </p>

                        {/* Placeholder for Stripe CardElement */}
                        <div className="space-y-4">
                            <div>
                                <label className="mb-1 block text-sm font-medium text-gray-700">
                                    Card Number
                                </label>
                                <input
                                    type="text"
                                    placeholder="4242 4242 4242 4242"
                                    className="h-10 w-full rounded-lg border border-gray-300 px-3 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="mb-1 block text-sm font-medium text-gray-700">
                                        Expiry
                                    </label>
                                    <input
                                        type="text"
                                        placeholder="MM/YY"
                                        className="h-10 w-full rounded-lg border border-gray-300 px-3 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                                    />
                                </div>
                                <div>
                                    <label className="mb-1 block text-sm font-medium text-gray-700">
                                        CVC
                                    </label>
                                    <input
                                        type="text"
                                        placeholder="123"
                                        className="h-10 w-full rounded-lg border border-gray-300 px-3 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {cardError && (
                        <p className="text-sm text-error-600">{cardError}</p>
                    )}
                </div>
            )}

            {/* PayNow QR */}
            {paymentMethod === 'paynow' && (
                <PayNowQR onPaymentComplete={onPaymentComplete} />
            )}

            {/* Actions */}
            <div className="flex gap-3">
                <Button type="button" variant="outline" onClick={onBack}>
                    Back
                </Button>
                {paymentMethod === 'card' && (
                    <Button
                        type="button"
                        onClick={handleCardSubmit}
                        loading={isProcessing}
                        className="flex-1"
                    >
                        Pay Now
                    </Button>
                )}
            </div>
        </div>
    );
}

export default PaymentForm;
