/**
 * API Endpoint Functions
 * 
 * Typed API functions for each domain.
 * All functions return Promise with typed responses.
 */
import { apiClient } from './client';
import type {
    Product,
    Category,
    Cart,
    Order,
    User,
    PaginatedResponse,
    ProductFilters,
    OrderFilters,
    LoginCredentials,
    LoginResponse,
    RegisterData,
    AddToCartRequest,
} from '@/types';

// ============================================================================
// Products API
// ============================================================================

export const ProductsApi = {
    /**
     * Get paginated list of products with optional filters
     */
    getAll: async (filters?: ProductFilters): Promise<PaginatedResponse<Product>> => {
        const response = await apiClient.get<PaginatedResponse<Product>>('/commerce/products/', {
            params: filters,
        });
        return response.data;
    },

    /**
     * Get single product by slug
     */
    getBySlug: async (slug: string): Promise<Product> => {
        const response = await apiClient.get<Product>(`/commerce/products/${slug}/`);
        return response.data;
    },

    /**
     * Get featured products for homepage
     */
    getFeatured: async (limit: number = 8): Promise<Product[]> => {
        const response = await apiClient.get<PaginatedResponse<Product>>('/commerce/products/', {
            params: { is_featured: true, page_size: limit },
        });
        return response.data.results;
    },

    /**
     * Search products by query
     */
    search: async (query: string): Promise<Product[]> => {
        const response = await apiClient.get<PaginatedResponse<Product>>('/commerce/products/', {
            params: { search: query },
        });
        return response.data.results;
    },
};

// ============================================================================
// Categories API
// ============================================================================

export const CategoriesApi = {
    /**
     * Get all categories
     */
    getAll: async (): Promise<Category[]> => {
        const response = await apiClient.get<PaginatedResponse<Category>>('/commerce/categories/');
        return response.data.results;
    },

    /**
     * Get category tree structure
     */
    getTree: async (): Promise<Category[]> => {
        const response = await apiClient.get<Category[]>('/commerce/categories/tree/');
        return response.data;
    },

    /**
     * Get single category by slug
     */
    getBySlug: async (slug: string): Promise<Category> => {
        const response = await apiClient.get<Category>(`/commerce/categories/${slug}/`);
        return response.data;
    },
};

// ============================================================================
// Cart API
// ============================================================================

export const CartApi = {
    /**
     * Get current user's cart
     */
    getCurrent: async (): Promise<Cart> => {
        const response = await apiClient.get<Cart>('/commerce/cart/current/');
        return response.data;
    },

    /**
     * Add item to cart
     */
    addItem: async (data: AddToCartRequest): Promise<Cart> => {
        const response = await apiClient.post<Cart>('/commerce/cart/add_item/', {
            product_id: data.productId,
            variant_id: data.variantId,
            quantity: data.quantity,
        });
        return response.data;
    },

    /**
     * Update cart item quantity
     */
    updateQuantity: async (itemId: string, quantity: number): Promise<Cart> => {
        const response = await apiClient.patch<Cart>(`/commerce/cart/items/${itemId}/`, {
            quantity,
        });
        return response.data;
    },

    /**
     * Remove item from cart
     */
    removeItem: async (itemId: string): Promise<void> => {
        await apiClient.delete(`/commerce/cart/items/${itemId}/`);
    },

    /**
     * Clear entire cart
     */
    clear: async (): Promise<void> => {
        await apiClient.delete('/commerce/cart/clear/');
    },

    /**
     * Checkout cart to create order
     */
    checkout: async (data: {
        shippingAddressId: string;
        billingAddressId?: string;
        paymentMethod: string;
        notes?: string;
    }): Promise<Order> => {
        const response = await apiClient.post<Order>('/commerce/cart/checkout/', {
            shipping_address_id: data.shippingAddressId,
            billing_address_id: data.billingAddressId,
            payment_method: data.paymentMethod,
            notes: data.notes,
        });
        return response.data;
    },
};

// ============================================================================
// Orders API
// ============================================================================

export const OrdersApi = {
    /**
     * Get user's orders with optional filters
     */
    getAll: async (filters?: OrderFilters): Promise<PaginatedResponse<Order>> => {
        const response = await apiClient.get<PaginatedResponse<Order>>('/commerce/orders/', {
            params: filters,
        });
        return response.data;
    },

    /**
     * Get single order by ID
     */
    getById: async (id: string): Promise<Order> => {
        const response = await apiClient.get<Order>(`/commerce/orders/${id}/`);
        return response.data;
    },

    /**
     * Cancel an order
     */
    cancel: async (id: string, reason?: string): Promise<Order> => {
        const response = await apiClient.post<Order>(`/commerce/orders/${id}/cancel/`, {
            reason,
        });
        return response.data;
    },
};

// ============================================================================
// Auth API
// ============================================================================

export const AuthApi = {
    /**
     * Login with email and password
     */
    login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
        const response = await apiClient.post<LoginResponse>('/accounts/auth/login/', credentials);
        return response.data;
    },

    /**
     * Logout (blacklist token)
     */
    logout: async (): Promise<void> => {
        await apiClient.post('/accounts/auth/logout/');
    },

    /**
     * Register new user
     */
    register: async (data: RegisterData): Promise<LoginResponse> => {
        const response = await apiClient.post<LoginResponse>('/accounts/users/', {
            email: data.email,
            password: data.password,
            first_name: data.firstName,
            last_name: data.lastName,
            phone: data.phone,
            company_name: data.companyName,
            company_uen: data.companyUen,
        });
        return response.data;
    },

    /**
     * Get current user profile
     */
    me: async (): Promise<User> => {
        const response = await apiClient.get<User>('/accounts/users/me/');
        return response.data;
    },

    /**
     * Refresh access token
     */
    refreshToken: async (refreshToken: string): Promise<{ access: string }> => {
        const response = await apiClient.post<{ access: string }>('/accounts/auth/token/refresh/', {
            refresh: refreshToken,
        });
        return response.data;
    },
};
