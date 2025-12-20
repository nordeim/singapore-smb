import { Spinner } from '@/components/ui/spinner';

export default function CheckoutLoading() {
    return (
        <div className="flex min-h-[60vh] items-center justify-center">
            <div className="text-center">
                <Spinner size="lg" />
                <p className="mt-4 text-gray-600">Loading checkout...</p>
            </div>
        </div>
    );
}
