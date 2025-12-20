/**
 * Core TypeScript types for Singapore SMB Frontend
 * 
 * These types match the backend Django REST Framework serializers.
 */

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T> {
    status: 'success' | 'error';
    data: T;
    meta?: {
        pagination?: Pagination;
    };
}

export interface ApiError {
    status: 'error';
    error: {
        code: string;
        message: string;
        details?: Array<{ field: string; message: string }>;
    };
}

export interface Pagination {
    page: number;
    perPage: number;
    total: number;
    pages: number;
}

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

// ============================================================================
// Core Entity Types
// ============================================================================

export interface Company {
    id: string;
    name: string;
    legalName: string;
    uen: string;
    gstRegistered: boolean;
    gstRegistrationNumber: string | null;
}

export interface User {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    phone: string;
    isActive: boolean;
    company: Company;
}

// ============================================================================
// Commerce Types
// ============================================================================

export interface Category {
    id: string;
    name: string;
    slug: string;
    description: string | null;
    imageUrl: string | null;
    parentId: string | null;
    sortOrder: number;
    isActive: boolean;
}

export interface Product {
    id: string;
    sku: string;
    barcode: string | null;
    name: string;
    slug: string;
    description: string | null;
    shortDescription: string | null;
    basePrice: string; // Decimal as string for precision
    costPrice: string | null;
    compareAtPrice: string | null;
    gstCode: 'SR' | 'ZR' | 'ES' | 'OS';
    gstRate: string; // Decimal as string
    imageUrl: string | null;
    category: Category | null;
    variants: ProductVariant[];
    isActive: boolean;
    createdAt: string;
    updatedAt: string;
}

export interface ProductVariant {
    id: string;
    sku: string;
    name: string;
    options: Record<string, string>; // e.g., { color: 'Red', size: 'M' }
    price: string;
    costPrice: string | null;
    imageUrl: string | null;
    isActive: boolean;
}

export interface Customer {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    phone: string;
    customerType: 'retail' | 'wholesale' | 'vip';
    companyName: string | null;
    companyUen: string | null;
    consentMarketing: boolean;
    consentAnalytics: boolean;
}

// ============================================================================
// Cart Types
// ============================================================================

export interface Cart {
    id: string;
    items: CartItem[];
    itemCount: number;
    subtotal: string;
    gstAmount: string;
    total: string;
    expiresAt: string | null;
}

export interface CartItem {
    id: string;
    product: Product;
    variant: ProductVariant | null;
    quantity: number;
    unitPrice: string;
    gstAmount: string;
    lineTotal: string;
}

export interface AddToCartRequest {
    productId: string;
    variantId?: string;
    quantity: number;
}

// ============================================================================
// Order Types
// ============================================================================

export type OrderStatus =
    | 'pending'
    | 'confirmed'
    | 'processing'
    | 'shipped'
    | 'delivered'
    | 'cancelled'
    | 'returned';

export type PaymentStatus =
    | 'pending'
    | 'authorized'
    | 'captured'
    | 'failed'
    | 'refunded';

export interface Order {
    id: string;
    orderNumber: string;
    status: OrderStatus;
    paymentStatus: PaymentStatus;
    customer: Customer;
    items: OrderItem[];
    shippingAddress: Address;
    billingAddress: Address;
    subtotal: string;
    gstAmount: string;
    shippingAmount: string;
    totalAmount: string;
    notes: string | null;
    createdAt: string;
    updatedAt: string;
}

export interface OrderItem {
    id: string;
    product: Product;
    variant: ProductVariant | null;
    quantity: number;
    unitPrice: string;
    gstCode: string;
    gstAmount: string;
    lineTotal: string;
}

export interface Address {
    recipientName: string;
    phone: string;
    addressLine1: string;
    addressLine2: string | null;
    postalCode: string;
    unitNumber: string | null;
    isDefault: boolean;
}

// ============================================================================
// Auth Types
// ============================================================================

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface LoginResponse {
    access: string;
    refresh: string;
    user: User;
}

export interface RegisterData {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
    phone: string;
    companyName?: string;
    companyUen?: string;
}

// ============================================================================
// Filter/Query Types
// ============================================================================

export interface ProductFilters {
    search?: string;
    category?: string;
    minPrice?: number;
    maxPrice?: number;
    gstCode?: string;
    page?: number;
    pageSize?: number;
    ordering?: string;
}

export interface OrderFilters {
    status?: OrderStatus;
    paymentStatus?: PaymentStatus;
    dateFrom?: string;
    dateTo?: string;
    page?: number;
    pageSize?: number;
}
