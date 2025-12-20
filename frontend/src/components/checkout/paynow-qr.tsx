/**
 * PayNow QR Component
 * 
 * QR code display for PayNow payment.
 */
'use client';

import { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { CheckCircle, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface PayNowQRProps {
    onPaymentComplete: () => void;
}

export function PayNowQR({ onPaymentComplete }: PayNowQRProps) {
    const [timeLeft, setTimeLeft] = useState(15 * 60); // 15 minutes
    const [status, setStatus] = useState<'pending' | 'checking' | 'complete'>('pending');

    // Countdown timer
    useEffect(() => {
        const timer = setInterval(() => {
            setTimeLeft((prev) => {
                if (prev <= 0) {
                    clearInterval(timer);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    // Format time as MM:SS
    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    // Simulate payment verification (in production, this would poll the backend)
    const handleCheckPayment = async () => {
        setStatus('checking');

        // Simulate checking payment status
        await new Promise((resolve) => setTimeout(resolve, 2000));

        // In production, this would check with the backend
        // For demo, we'll simulate success
        setStatus('complete');
        setTimeout(onPaymentComplete, 1000);
    };

    // Demo QR data (in production, this would come from the backend)
    const qrData = '00020201021126360009SG.PAYNOW010120210289012345S0302010406123456520400005303702540510.005802SG5902NA6009Singapore6105123456304ABCD';

    if (status === 'complete') {
        return (
            <div className="text-center py-8">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-success-100">
                    <CheckCircle className="h-8 w-8 text-success-600" />
                </div>
                <p className="mt-4 text-lg font-medium text-gray-900">Payment Received!</p>
                <p className="text-gray-500">Redirecting...</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* QR Code */}
            <div className="flex flex-col items-center">
                <div className="rounded-xl bg-white p-4 shadow-sm">
                    <QRCodeSVG
                        value={qrData}
                        size={200}
                        level="M"
                        includeMargin
                    />
                </div>

                {/* Timer */}
                <div className="mt-4 flex items-center gap-2 text-sm text-gray-600">
                    <Clock className="h-4 w-4" />
                    <span>
                        Expires in <span className="font-medium">{formatTime(timeLeft)}</span>
                    </span>
                </div>
            </div>

            {/* Instructions */}
            <div className="rounded-lg bg-primary-50 p-4 text-sm">
                <p className="font-medium text-primary-900">How to pay with PayNow:</p>
                <ol className="mt-2 list-inside list-decimal space-y-1 text-primary-800">
                    <li>Open your banking app</li>
                    <li>Scan the QR code above</li>
                    <li>Confirm the payment amount</li>
                    <li>Click "I've Paid" below</li>
                </ol>
            </div>

            {/* Reference */}
            <div className="text-center text-sm text-gray-500">
                Payment Reference: <span className="font-mono font-medium">SGP-123456</span>
            </div>

            {/* Verify Button */}
            <Button
                onClick={handleCheckPayment}
                loading={status === 'checking'}
                variant="outline"
                className="w-full"
            >
                I've Paid - Verify Payment
            </Button>
        </div>
    );
}

export default PayNowQR;
