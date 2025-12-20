import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function HomePage() {
    return (
        <div className="flex flex-col">
            {/* Hero Section */}
            <section className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
                <div className="mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
                    <div className="text-center">
                        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
                            Singapore SMB Platform
                        </h1>
                        <p className="mx-auto mt-6 max-w-2xl text-xl text-primary-100">
                            Unified e-commerce, inventory, and accounting for Singapore small and medium businesses.
                            GST-compliant, IRAS-ready.
                        </p>
                        <div className="mt-10 flex items-center justify-center gap-4">
                            <Link href="/products">
                                <Button size="lg" variant="secondary">
                                    Browse Products
                                </Button>
                            </Link>
                            <Link href="/register">
                                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-primary-700">
                                    Get Started
                                </Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-20">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="text-center">
                        <h2 className="text-3xl font-bold tracking-tight text-gray-900">
                            Everything You Need to Run Your Business
                        </h2>
                        <p className="mt-4 text-lg text-gray-600">
                            One platform for e-commerce, inventory, and accounting
                        </p>
                    </div>

                    <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
                        {/* E-commerce */}
                        <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-card transition-shadow hover:shadow-card-hover">
                            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-100 text-primary-600">
                                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                                </svg>
                            </div>
                            <h3 className="mt-6 text-xl font-semibold text-gray-900">E-commerce</h3>
                            <p className="mt-2 text-gray-600">
                                PWA storefront with PayNow, Stripe, and HitPay. Mobile-first design.
                            </p>
                        </div>

                        {/* Inventory */}
                        <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-card transition-shadow hover:shadow-card-hover">
                            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-success-100 text-success-600">
                                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                                </svg>
                            </div>
                            <h3 className="mt-6 text-xl font-semibold text-gray-900">Inventory</h3>
                            <p className="mt-2 text-gray-600">
                                Multi-location stock tracking with real-time sync. 99.5% accuracy target.
                            </p>
                        </div>

                        {/* Accounting */}
                        <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-card transition-shadow hover:shadow-card-hover">
                            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-warning-100 text-warning-600">
                                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                </svg>
                            </div>
                            <h3 className="mt-6 text-xl font-semibold text-gray-900">Accounting</h3>
                            <p className="mt-2 text-gray-600">
                                GST-compliant. Auto F5 returns. PEPPOL/InvoiceNow ready for IRAS.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="bg-gray-50 py-16">
                <div className="mx-auto max-w-7xl px-4 text-center sm:px-6 lg:px-8">
                    <h2 className="text-2xl font-bold text-gray-900">
                        Ready to streamline your business?
                    </h2>
                    <p className="mt-4 text-gray-600">
                        Join Singapore SMBs saving S$390,000+ annually
                    </p>
                    <Link href="/register" className="mt-8 inline-block">
                        <Button size="lg">
                            Start Free Trial
                        </Button>
                    </Link>
                </div>
            </section>
        </div>
    );
}
