/**
 * Register Page
 * 
 * Registration form with PDPA consent.
 */
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { useAuth } from '@/lib/hooks/useAuth';

const registerSchema = z.object({
    firstName: z.string().min(1, 'First name is required'),
    lastName: z.string().min(1, 'Last name is required'),
    email: z.string().min(1, 'Email is required').email('Invalid email address'),
    phone: z.string().regex(/^(\+65)?[689]\d{7}$/, 'Invalid Singapore phone number'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string(),
    consentMarketing: z.boolean().optional(),
    consentTerms: z.boolean().refine((val) => val === true, {
        message: 'You must accept the terms and conditions',
    }),
}).refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
    const router = useRouter();
    const { register: registerUser, isLoading } = useAuth();
    const [serverError, setServerError] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<RegisterFormData>({
        resolver: zodResolver(registerSchema),
        defaultValues: {
            consentMarketing: false,
            consentTerms: undefined,
        },
    });

    const onSubmit = async (data: RegisterFormData) => {
        setServerError(null);
        try {
            await registerUser({
                firstName: data.firstName,
                lastName: data.lastName,
                email: data.email,
                password: data.password,
                phone: data.phone,
            });
            router.push('/account');
        } catch (err) {
            setServerError(err instanceof Error ? err.message : 'Registration failed');
        }
    };

    return (
        <div className="flex min-h-[80vh] items-center justify-center px-4 py-8">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <CardTitle className="text-2xl">Create Account</CardTitle>
                    <CardDescription>
                        Join Singapore SMB to start shopping
                    </CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit(onSubmit)}>
                    <CardContent className="space-y-4">
                        {serverError && (
                            <div className="rounded-lg bg-error-50 p-3 text-sm text-error-700">
                                {serverError}
                            </div>
                        )}

                        {/* Name */}
                        <div className="grid gap-4 sm:grid-cols-2">
                            <Input
                                label="First Name"
                                placeholder="John"
                                error={errors.firstName?.message}
                                {...register('firstName')}
                            />
                            <Input
                                label="Last Name"
                                placeholder="Doe"
                                error={errors.lastName?.message}
                                {...register('lastName')}
                            />
                        </div>

                        {/* Email */}
                        <Input
                            label="Email Address"
                            type="email"
                            placeholder="you@example.com"
                            error={errors.email?.message}
                            {...register('email')}
                        />

                        {/* Phone */}
                        <Input
                            label="Phone Number"
                            type="tel"
                            placeholder="+65 9123 4567"
                            helpText="Singapore phone number"
                            error={errors.phone?.message}
                            {...register('phone')}
                        />

                        {/* Password */}
                        <Input
                            label="Password"
                            type="password"
                            placeholder="••••••••"
                            error={errors.password?.message}
                            {...register('password')}
                        />

                        <Input
                            label="Confirm Password"
                            type="password"
                            placeholder="••••••••"
                            error={errors.confirmPassword?.message}
                            {...register('confirmPassword')}
                        />

                        {/* Consent */}
                        <div className="space-y-3">
                            <label className="flex items-start gap-2">
                                <input
                                    type="checkbox"
                                    className="mt-1 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                                    {...register('consentMarketing')}
                                />
                                <span className="text-sm text-gray-600">
                                    I want to receive marketing emails and promotions
                                </span>
                            </label>

                            <label className="flex items-start gap-2">
                                <input
                                    type="checkbox"
                                    className="mt-1 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                                    {...register('consentTerms')}
                                />
                                <span className="text-sm text-gray-600">
                                    I agree to the{' '}
                                    <Link href="/terms" className="text-primary-600 hover:underline">
                                        Terms of Service
                                    </Link>{' '}
                                    and{' '}
                                    <Link href="/privacy" className="text-primary-600 hover:underline">
                                        Privacy Policy
                                    </Link>
                                </span>
                            </label>
                            {errors.consentTerms && (
                                <p className="text-sm text-error-600">{errors.consentTerms.message}</p>
                            )}
                        </div>
                    </CardContent>

                    <CardFooter className="flex flex-col gap-4">
                        <Button
                            type="submit"
                            className="w-full"
                            loading={isSubmitting || isLoading}
                        >
                            Create Account
                        </Button>

                        <p className="text-center text-sm text-gray-600">
                            Already have an account?{' '}
                            <Link
                                href="/login"
                                className="font-medium text-primary-600 hover:text-primary-700"
                            >
                                Sign in
                            </Link>
                        </p>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
