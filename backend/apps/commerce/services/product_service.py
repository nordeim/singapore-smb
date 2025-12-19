"""
Product service for business logic.

Handles:
- Product creation with variants
- Price calculation with GST
- Full-text search
"""
from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from apps.commerce.models import Product, ProductVariant, Category


class ProductService:
    """Service class for product business logic."""
    
    @staticmethod
    @transaction.atomic
    def create_product(
        company,
        data: dict,
        variants: list[dict] | None = None
    ) -> Product:
        """
        Create a product with optional variants.
        
        Args:
            company: Company instance
            data: Product data dict
            variants: Optional list of variant data dicts
            
        Returns:
            Created Product instance
        """
        # Set company
        data['company'] = company
        
        # Handle category by ID
        category_id = data.pop('category_id', None)
        if category_id:
            data['category'] = Category.objects.get(id=category_id, company=company)
        
        # Create product
        product = Product.objects.create(**data)
        
        # Create variants if provided
        if variants:
            for variant_data in variants:
                variant_data['product'] = product
                ProductVariant.objects.create(**variant_data)
        
        return product
    
    @staticmethod
    @transaction.atomic
    def update_product(product: Product, data: dict) -> Product:
        """
        Update a product.
        
        Args:
            product: Product instance
            data: Update data dict
            
        Returns:
            Updated Product instance
        """
        # Handle category by ID
        category_id = data.pop('category_id', None)
        if category_id:
            data['category'] = Category.objects.get(
                id=category_id, company=product.company
            )
        
        for key, value in data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        product.save()
        return product
    
    @staticmethod
    def calculate_price_with_gst(
        product: Product,
        quantity: int = 1,
        variant: ProductVariant | None = None
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Calculate price breakdown with GST.
        
        Args:
            product: Product instance
            quantity: Number of items
            variant: Optional variant for price adjustment
            
        Returns:
            Tuple of (subtotal, gst_amount, total)
        """
        # Get unit price
        if variant:
            unit_price = variant.effective_price
        else:
            unit_price = product.base_price
        
        subtotal = unit_price * quantity
        
        # Calculate GST based on code
        if product.gst_code == 'SR':
            gst_amount = round(subtotal * product.gst_rate, 2)
        else:
            gst_amount = Decimal('0.00')
        
        total = subtotal + gst_amount
        return subtotal, gst_amount, total
    
    @staticmethod
    def search(
        company,
        query: str,
        category_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ):
        """
        Search products using full-text search.
        
        Args:
            company: Company instance
            query: Search query string
            category_id: Optional category filter
            status: Optional status filter
            limit: Maximum results to return
            
        Returns:
            QuerySet of matching products
        """
        # Base queryset
        qs = Product.objects.filter(company=company)
        
        # Apply filters
        if category_id:
            qs = qs.filter(category_id=category_id)
        
        if status:
            qs = qs.filter(status=status)
        else:
            qs = qs.exclude(status='archived')
        
        if query:
            # Use PostgreSQL full-text search
            search_vector = SearchVector('name', weight='A') + \
                           SearchVector('description', weight='B') + \
                           SearchVector('sku', weight='A')
            search_query = SearchQuery(query)
            
            qs = qs.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank')
        else:
            qs = qs.order_by('-created_at')
        
        return qs[:limit]
    
    @staticmethod
    @transaction.atomic
    def bulk_update_prices(
        product_ids: list[str],
        price_adjustment: Decimal | None = None,
        price_multiplier: Decimal | None = None
    ) -> int:
        """
        Bulk update product prices.
        
        Args:
            product_ids: List of product IDs
            price_adjustment: Fixed amount to add (can be negative)
            price_multiplier: Multiplier for prices (e.g., 1.1 for 10% increase)
            
        Returns:
            Number of products updated
        """
        products = Product.objects.filter(id__in=product_ids)
        updated = 0
        
        for product in products:
            if price_adjustment is not None:
                product.base_price = max(Decimal('0'), product.base_price + price_adjustment)
            elif price_multiplier is not None:
                product.base_price = round(product.base_price * price_multiplier, 2)
            product.save(update_fields=['base_price', 'updated_at'])
            updated += 1
        
        return updated
