import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';

const inter = Inter({
    subsets: ['latin'],
    display: 'swap',
    variable: '--font-inter',
});

export const metadata: Metadata = {
    title: {
        template: '%s | Singapore SMB',
        default: 'Singapore SMB - E-Commerce Platform',
    },
    description: 'Unified e-commerce, inventory, and accounting platform for Singapore small and medium businesses.',
    keywords: ['e-commerce', 'Singapore', 'SMB', 'inventory', 'accounting', 'GST'],
    authors: [{ name: 'Singapore SMB Team' }],
    openGraph: {
        type: 'website',
        locale: 'en_SG',
        siteName: 'Singapore SMB',
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className={inter.variable}>
            <body className="antialiased">
                <Providers>
                    <div className="flex min-h-screen flex-col">
                        <Header />
                        <main className="flex-1">
                            {children}
                        </main>
                        <Footer />
                    </div>
                </Providers>
            </body>
        </html>
    );
}
