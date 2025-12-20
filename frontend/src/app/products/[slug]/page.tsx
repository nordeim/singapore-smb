/**
 * Product Detail Page
 * 
 * Client component for product details with add-to-cart.
 */
'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';
import { ImageGallery } from '@/components/products/image-gallery';
import { VariantSelector } from '@/components/products/variant-selector';
import { AddToCartButton } from '@/components/products/add-to-cart-button';
import { ProductGrid } from '@/components/products/product-grid';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useProduct, useProducts } from '@/lib/api/queries';

export default function ProductPage() {
    const params = useParams();
    const slug = params.slug as string;
    const { data: product, isLoading } = useProduct(slug);

    // Get related products
    const { data: relatedResponse } = useProducts(
        product?.category ? { category: product.category.slug, pageSize: 4 } : undefined
    );
    const relatedProducts = (relatedResponse?.results || [])
        .filter((p) => p.id !== product?.id)
        .slice(0, 4);

    if (isLoading) {
        return (
            <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                <div className="grid gap-8 lg:grid-cols-2">
                    <Skeleton className="aspect-square w-full rounded-xl" />
                    <div className="space-y-4">
                        <Skeleton className="h-8 w-3/4" />
                        <Skeleton className="h-12 w-1/3" />
                        <Skeleton className="h-24 w-full" />
                        <Skeleton className="h-12 w-full" />
                    </div>
                </div>
            </div>
        );
    }

    if (!product) {
        return (
            <div className="mx-auto max-w-7xl px-4 py-16 text-center">
                <h1 className="text-2xl font-bold text-gray-900">Product Not Found</h1>
                <p className="mt-2 text-gray-500">The product you're looking for doesn't exist.</p>
                <Link href="/products" className="mt-4 inline-block text-primary-600 hover:underline">
                    Back to Products
                </Link>
            </div>
        );
    }

    // Calculate GST-inclusive price
    const basePrice = parseFloat(product.basePrice);
    const gstRate = parseFloat(product.gstRate || '0');
    const priceWithGst = product.gstCode === 'SR'
        ? basePrice * (1 + gstRate / 100)
        : basePrice;

    return (
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            {/* Breadcrumb */}
            <nav className="mb-6 flex items-center gap-2 text-sm text-gray-500">
                <Link href="/products" className="hover:text-primary-600">
                    Products
                </Link>
                <ChevronRight className="h-4 w-4" />
                {product.category && (
                    <>
                        <Link
                            href={`/products?category=${product.category.slug}`}
                            className="hover:text-primary-600"
                        >
                            {product.category.name}
                        </Link>
                        <ChevronRight className="h-4 w-4" />
                    </>
                )}
                <span className="text-gray-900">{product.name}</span>
            </nav>

            {/* Product Detail */}
            <div className="grid gap-8 lg:grid-cols-2">
                {/* Image Gallery */}
                <ImageGallery
                    images={product.imageUrl ? [product.imageUrl] : []}
                    productName={product.name}
                />

                {/* Product Info */}
                <div className="flex flex-col">
                    {/* Title & Badges */}
                    <div className="mb-4">
                        <div className="flex flex-wrap gap-2 mb-2">
                            {product.gstCode === 'ZR' && (
                                <Badge variant="success">GST-Free</Badge>
                            )}
                            {product.compareAtPrice && parseFloat(product.compareAtPrice) > basePrice && (
                                <Badge variant="error">Sale</Badge>
                            )}
                        </div>
                        <h1 className="text-3xl font-bold text-gray-900">{product.name}</h1>
                        <p className="mt-1 text-sm text-gray-500">SKU: {product.sku}</p>
                    </div>

                    {/* Price */}
                    <div className="mb-6">
                        <div className="flex items-baseline gap-3">
                            <span className="text-3xl font-bold text-gray-900">
                                S${priceWithGst.toFixed(2)}
                            </span>
                            {product.compareAtPrice && parseFloat(product.compareAtPrice) > basePrice && (
                                <span className="text-lg text-gray-400 line-through">
                                    S${parseFloat(product.compareAtPrice).toFixed(2)}
                                </span>
                            )}
                        </div>
                        {product.gstCode === 'SR' && (
                            <p className="mt-1 text-sm text-gray-500">
                                Includes {gstRate}% GST
                            </p>
                        )}
                    </div>

                    {/* Description */}
                    {product.description && (
                        <div className="mb-6">
                            <h2 className="mb-2 text-sm font-semibold text-gray-900">Description</h2>
                            <p className="text-gray-600">{product.description}</p>
                        </div>
                    )}

                    {/* Variant Selector */}
                    {product.variants && product.variants.length > 0 && (
                        <div className="mb-6">
                            <VariantSelector variants={product.variants} />
                        </div>
                    )}

                    {/* Add to Cart */}
                    <AddToCartButton productId={product.id} productName={product.name} />
                </div>
            </div>

            {/* Related Products */}
            {relatedProducts.length > 0 && (
                <div className="mt-16">
                    <h2 className="mb-6 text-2xl font-bold text-gray-900">Related Products</h2>
                    <ProductGrid products={relatedProducts} columns={4} />
                </div>
            )}
        </div>
    );
}
