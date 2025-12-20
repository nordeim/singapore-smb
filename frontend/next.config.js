/** @type {import('next').NextConfig} */
const nextConfig = {
    // API Proxy for development
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: `${process.env.BACKEND_URL || 'http://localhost:8000'}/api/:path*`,
            },
        ];
    },

    // Image optimization
    images: {
        remotePatterns: [
            {
                protocol: 'https',
                hostname: '*.cloudfront.net',
                pathname: '/**',
            },
            {
                protocol: 'https',
                hostname: 'images.unsplash.com',
                pathname: '/**',
            },
            {
                protocol: 'https',
                hostname: 'placehold.co',
                pathname: '/**',
            },
        ],
    },

    // Environment variables exposed to client
    env: {
        NEXT_PUBLIC_APP_NAME: 'Singapore SMB',
        NEXT_PUBLIC_APP_VERSION: '0.1.0',
    },

    // Strict mode for React
    reactStrictMode: true,

    // Experimental features
    experimental: {
        // Enable server actions for forms
        serverActions: {
            allowedOrigins: ['localhost:3000'],
        },
    },
};

module.exports = nextConfig;
