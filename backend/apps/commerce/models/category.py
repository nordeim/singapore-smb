"""
Category model for product categorization.

Implements hierarchical categories with self-referential parent FK.
"""
from django.db import models

from core.models import SoftDeleteModel


class Category(SoftDeleteModel):
    """
    Product category with hierarchical structure.
    
    Supports nested categories via self-referential parent FK.
    Company-scoped for multi-tenant isolation.
    
    Attributes:
        company: Company that owns this category
        parent: Parent category (null for top-level)
        name: Category display name
        slug: URL-friendly identifier (unique per company)
        description: Optional detailed description
        image_url: Optional category image
        sort_order: Display ordering within parent
        is_active: Whether category is visible
    """
    
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='categories',
        help_text="Company that owns this category"
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        help_text="Parent category (null for top-level)"
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Category display name"
    )
    
    slug = models.SlugField(
        max_length=100,
        help_text="URL-friendly identifier"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Optional detailed description"
    )
    
    image_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Optional category image URL"
    )
    
    # SEO fields
    meta_title = models.CharField(
        max_length=70,
        blank=True,
        help_text="SEO title (max 70 chars)"
    )
    
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO meta description (max 160 chars)"
    )
    
    # Ordering and status
    sort_order = models.IntegerField(
        default=0,
        help_text="Display order within parent category"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether category is visible to customers"
    )
    
    class Meta:
        db_table = '"commerce"."categories"'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']
        unique_together = [('company', 'slug')]
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_ancestors(self):
        """
        Get all ancestor categories from parent to root.
        
        Returns:
            List of Category objects from immediate parent to root
        """
        ancestors = []
        current = self.parent
        while current is not None:
            ancestors.append(current)
            current = current.parent
        return ancestors
    
    def get_descendants(self):
        """
        Get all descendant categories (children, grandchildren, etc).
        
        Returns:
            QuerySet of all descendant Category objects
        """
        descendants = list(self.children.all())
        for child in self.children.all():
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_breadcrumb_path(self):
        """
        Get category path for breadcrumb navigation.
        
        Returns:
            List of categories from root to self
        """
        path = self.get_ancestors()
        path.reverse()
        path.append(self)
        return path
    
    @property
    def depth(self) -> int:
        """
        Get depth level of this category in the hierarchy.
        
        Returns:
            0 for top-level, 1 for first-level child, etc.
        """
        return len(self.get_ancestors())
    
    @property
    def is_leaf(self) -> bool:
        """Check if this category has no children."""
        return not self.children.exists()
