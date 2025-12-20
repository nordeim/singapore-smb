/**
 * Login Form Component
 * 
 * Form with email/password fields, validation, and error handling.
 */
'use client';

import * as React from 'react';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { useAuth } from '@/lib/hooks/useAuth';

// Validation schema
const loginSchema = z.object({
    email: z
        .string()
        .min(1, 'Email is required')
        .email('Please enter a valid email address'),
    password: z
        .string()
        .min(1, 'Password is required')
        .min(8, 'Password must be at least 8 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

interface LoginFormProps {
    redirectTo?: string;
}

export function LoginForm({ redirectTo = '/account' }: LoginFormProps) {
    const { login, isLoading, error } = useAuth();
    const [serverError, setServerError] = React.useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginFormData) => {
        setServerError(null);
        try {
            await login(data, redirectTo);
        } catch (err) {
            setServerError(
                err instanceof Error
                    ? err.message
                    : 'Login failed. Please check your credentials.'
            );
        }
    };

    return (
        <Card className="w-full max-w-md mx-auto">
            <CardHeader className="text-center">
                <CardTitle className="text-2xl">Welcome Back</CardTitle>
                <CardDescription>
                    Sign in to your Singapore SMB account
                </CardDescription>
            </CardHeader>

            <form onSubmit={handleSubmit(onSubmit)}>
                <CardContent className="space-y-4">
                    {/* Server Error */}
                    {(serverError || error) && (
                        <div className="rounded-lg bg-error-50 p-3 text-sm text-error-700">
                            {serverError || error?.message}
                        </div>
                    )}

                    {/* Email */}
                    <Input
                        label="Email Address"
                        type="email"
                        autoComplete="email"
                        placeholder="you@example.com"
                        error={errors.email?.message}
                        {...register('email')}
                    />

                    {/* Password */}
                    <Input
                        label="Password"
                        type="password"
                        autoComplete="current-password"
                        placeholder="••••••••"
                        error={errors.password?.message}
                        {...register('password')}
                    />

                    {/* Forgot Password */}
                    <div className="flex justify-end">
                        <Link
                            href="/forgot-password"
                            className="text-sm text-primary-600 hover:text-primary-700"
                        >
                            Forgot password?
                        </Link>
                    </div>
                </CardContent>

                <CardFooter className="flex flex-col gap-4">
                    <Button
                        type="submit"
                        className="w-full"
                        loading={isSubmitting || isLoading}
                    >
                        Sign In
                    </Button>

                    <p className="text-center text-sm text-gray-600">
                        Don&apos;t have an account?{' '}
                        <Link
                            href="/register"
                            className="font-medium text-primary-600 hover:text-primary-700"
                        >
                            Create one
                        </Link>
                    </p>
                </CardFooter>
            </form>
        </Card>
    );
}

export default LoginForm;
