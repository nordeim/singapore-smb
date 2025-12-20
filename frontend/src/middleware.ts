import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Routes that require authentication
const protectedRoutes = [
    '/account',
    '/account/orders',
    '/account/settings',
    '/checkout',
];

// Routes that are only for unauthenticated users
const authRoutes = [
    '/login',
    '/register',
];

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // Get token from cookies
    const token = request.cookies.get('auth_token')?.value;

    // Check if trying to access protected route without auth
    const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));
    if (isProtectedRoute && !token) {
        const loginUrl = new URL('/login', request.url);
        loginUrl.searchParams.set('redirect', pathname);
        return NextResponse.redirect(loginUrl);
    }

    // Check if authenticated user trying to access auth routes
    const isAuthRoute = authRoutes.some(route => pathname.startsWith(route));
    if (isAuthRoute && token) {
        return NextResponse.redirect(new URL('/account', request.url));
    }

    return NextResponse.next();
}

export const config = {
    // Run middleware on these paths
    matcher: [
        '/account/:path*',
        '/checkout/:path*',
        '/login',
        '/register',
    ],
};
