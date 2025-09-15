"""
Category model for organizing subscriptions.

Categories can have subcategories through self-referencing relationships.
Includes validation to prevent circular references.
"""

from django.db import models
from django.core.exceptions import ValidationError

from .base import ValidationMixin, SelfReferencingMixin
from .managers import CategoryManager


class Category(ValidationMixin, SelfReferencingMixin, models.Model):
    """
    Category model for organizing subscriptions.
    
    Supports hierarchical structure through self-referencing parent field.
    Includes validation to prevent circular references and self-referencing.
    """
    
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    
    # Self-referencing relationship for subcategories
    # If parent = null, then it is a parent category
    # If parent = some_category_id, then it is a subcategory
    parent = models.ForeignKey(
        "self", 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name="subcategories"
    )
    
    # Custom manager
    objects = CategoryManager()
    
    def __str__(self):
        """String representation of the category."""
        return self.name
    
    def _run_custom_validation(self):
        """
        Validate category data to prevent invalid parent relationships.
        
        Raises:
            ValidationError: If validation fails
        """
        # Prevent self-referencing
        if self.parent == self:
            raise ValidationError({
                'parent': 'A category cannot be its own parent.'
            })
        
        # Prevent circular references
        if self.parent:
            self._check_circular_reference('parent')
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']
