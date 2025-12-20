import { Spinner } from '@/components/ui/spinner';

export default function Loading() {
    return (
        <div className="flex min-h-[60vh] items-center justify-center">
            <div className="text-center">
                <Spinner size="lg" />
                <p className="mt-4 text-gray-600">Loading...</p>
            </div>
        </div>
    );
}
