/**
 * Login Page
 * 
 * Uses LoginForm from Phase 6.
 */
import { LoginForm } from '@/components/forms/login-form';

interface LoginPageProps {
    searchParams: { redirect?: string };
}

export default function LoginPage({ searchParams }: LoginPageProps) {
    return (
        <div className="flex min-h-[80vh] items-center justify-center px-4">
            <LoginForm redirectTo={searchParams.redirect || '/account'} />
        </div>
    );
}

export const metadata = {
    title: 'Sign In',
};
