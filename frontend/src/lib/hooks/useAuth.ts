/**
 * useAuth Hook
 * 
 * Authentication state and actions.
 * Uses React Query for user state management.
 */
'use client';

import { useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import { useUser, queryKeys } from '@/lib/api/queries';
import { useLogin, useLogout, useRegister } from '@/lib/api/mutations';
import { getAuthToken, clearAuthTokens } from '@/lib/api/client';
import type { LoginCredentials, RegisterData, User } from '@/types';

export interface UseAuthReturn {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: Error | null;
    login: (credentials: LoginCredentials, redirectTo?: string) => Promise<void>;
    logout: () => Promise<void>;
    register: (data: RegisterData, redirectTo?: string) => Promise<void>;
}

export function useAuth(): UseAuthReturn {
    const router = useRouter();
    const queryClient = useQueryClient();

    // Get user from cache/API
    const {
        data: user,
        isLoading: isUserLoading,
        error: userError,
    } = useUser({
        enabled: typeof window !== 'undefined' && !!getAuthToken(),
        retry: false,
    });

    // Mutations
    const loginMutation = useLogin();
    const logoutMutation = useLogout();
    const registerMutation = useRegister();

    // Derived state
    const isAuthenticated = useMemo(() => {
        return !!user && !!getAuthToken();
    }, [user]);

    const isLoading = useMemo(() => {
        return isUserLoading || loginMutation.isPending || logoutMutation.isPending || registerMutation.isPending;
    }, [isUserLoading, loginMutation.isPending, logoutMutation.isPending, registerMutation.isPending]);

    // Login action
    const login = useCallback(async (credentials: LoginCredentials, redirectTo: string = '/account') => {
        await loginMutation.mutateAsync(credentials);
        router.push(redirectTo);
    }, [loginMutation, router]);

    // Logout action
    const logout = useCallback(async () => {
        try {
            await logoutMutation.mutateAsync();
        } catch {
            // Clear anyway even if API call fails
            clearAuthTokens();
            queryClient.clear();
        }
        router.push('/');
    }, [logoutMutation, queryClient, router]);

    // Register action
    const register = useCallback(async (data: RegisterData, redirectTo: string = '/account') => {
        await registerMutation.mutateAsync(data);
        router.push(redirectTo);
    }, [registerMutation, router]);

    return {
        user: user ?? null,
        isAuthenticated,
        isLoading,
        error: (userError as Error) || loginMutation.error || logoutMutation.error || registerMutation.error || null,
        login,
        logout,
        register,
    };
}

export default useAuth;
