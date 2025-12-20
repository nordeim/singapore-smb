/**
 * API Client with Axios
 * 
 * Features:
 * - Base URL configuration from environment
 * - JWT token handling via interceptors
 * - 401 response handling
 * - Error normalization
 */
import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import type { ApiError } from '@/types';

// Token storage key
const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 15000, // 15 seconds
});

// ============================================================================
// Token Management
// ============================================================================

export function getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
}

export function setAuthToken(token: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(TOKEN_KEY, token);
}

export function getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setRefreshToken(token: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

export function clearAuthTokens(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
}

// ============================================================================
// Request Interceptor - Add Authorization Header
// ============================================================================

apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = getAuthToken();
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// ============================================================================
// Response Interceptor - Handle 401 & Normalize Errors
// ============================================================================

let isRefreshing = false;
let failedQueue: Array<{
    resolve: (value?: unknown) => void;
    reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError<ApiError>) => {
        const originalRequest = error.config;

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && originalRequest) {
            // Check if this is already a retry
            if ((originalRequest as { _retry?: boolean })._retry) {
                // Refresh failed, clear tokens and redirect
                clearAuthTokens();
                if (typeof window !== 'undefined') {
                    window.location.href = '/login';
                }
                return Promise.reject(error);
            }

            // Try to refresh token
            if (!isRefreshing) {
                isRefreshing = true;
                (originalRequest as { _retry?: boolean })._retry = true;

                const refreshToken = getRefreshToken();
                if (!refreshToken) {
                    clearAuthTokens();
                    if (typeof window !== 'undefined') {
                        window.location.href = '/login';
                    }
                    return Promise.reject(error);
                }

                try {
                    const response = await axios.post(
                        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/accounts/auth/token/refresh/`,
                        { refresh: refreshToken }
                    );

                    const { access } = response.data;
                    setAuthToken(access);
                    processQueue(null, access);

                    // Retry original request
                    if (originalRequest.headers) {
                        originalRequest.headers.Authorization = `Bearer ${access}`;
                    }
                    return apiClient(originalRequest);
                } catch (refreshError) {
                    processQueue(refreshError as Error, null);
                    clearAuthTokens();
                    if (typeof window !== 'undefined') {
                        window.location.href = '/login';
                    }
                    return Promise.reject(refreshError);
                } finally {
                    isRefreshing = false;
                }
            }

            // Queue requests while refreshing
            return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject });
            }).then((token) => {
                if (originalRequest.headers) {
                    originalRequest.headers.Authorization = `Bearer ${token}`;
                }
                return apiClient(originalRequest);
            });
        }

        // Normalize error response
        const normalizedError: ApiError = {
            status: 'error',
            error: {
                code: error.response?.data?.error?.code || 'UNKNOWN_ERROR',
                message: error.response?.data?.error?.message || error.message || 'An unexpected error occurred',
                details: error.response?.data?.error?.details,
            },
        };

        return Promise.reject(normalizedError);
    }
);

export default apiClient;
