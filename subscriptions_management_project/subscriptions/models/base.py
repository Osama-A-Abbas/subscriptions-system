"""
Base models, constants, and shared functionality.

This module contains:
- Constants used across models
- Abstract base models
- Common mixins and utilities
"""

from django.db import models
from django.core.exceptions import ValidationError


# Constants
BILLING_CYCLE_CHOICES = [
    ("monthly", "Monthly"),
    ("yearly", "Yearly"),
]


class TimestampMixin(models.Model):
    """Mixin to add created_at and updated_at fields to any model."""
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class ValidationMixin:
    """Mixin to provide common validation patterns."""
    
    def clean(self):
        """Run validation and call super().clean()."""
        super().clean()
        self._run_custom_validation()
    
    def _run_custom_validation(self):
        """Override in subclasses to add custom validation logic."""
        pass
    
    def save(self, *args, **kwargs):
        """Override save to run validation before saving."""
        self.full_clean()
        super().save(*args, **kwargs)


class SelfReferencingMixin:
    """Mixin for models that can reference themselves (like categories)."""
    
    def _check_circular_reference(self, parent_field='parent'):
        """
        Check if setting the parent would create a circular reference.
        
        Args:
            parent_field: Name of the parent field to check
            
        Raises:
            ValidationError: If circular reference would be created
        """
        parent = getattr(self, parent_field)
        if not parent:
            return
            
        # If this is a new instance (no pk), we can't check circular refs yet
        if not self.pk:
            return
            
        # Check if the parent is a descendant of this category
        current = parent
        visited = {self.pk}  # Track visited items to prevent infinite loops
        
        while current:
            if current.pk in visited:
                raise ValidationError({
                    parent_field: f'Setting "{parent.name}" as parent would create a circular reference.'
                })
            
            if current.pk == self.pk:
                raise ValidationError({
                    parent_field: 'An item cannot be its own parent.'
                })
                
            visited.add(current.pk)
            current = getattr(current, parent_field, None)
