"""
Form mixins for common functionality and validation patterns.

These mixins provide reusable form behavior that can be composed
into forms for consistent validation and user experience.
"""

from django import forms
from django.db.models import Case, When, IntegerField
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class BootstrapFormMixin:
    """Mixin to add Bootstrap CSS classes to form fields."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_bootstrap_classes()
    
    def _add_bootstrap_classes(self):
        """Add Bootstrap CSS classes to form fields."""
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.EmailInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'date'})


class CategoryOrderingMixin:
    """Mixin to handle category field ordering and default selection."""
    
    def setup_category_field(self, field_name='category', default_category='Other'):
        """
        Setup category field with proper ordering and default selection.
        
        Args:
            field_name: Name of the category field
            default_category: Name of the default category to select
        """
        from .models import Category
        
        if field_name not in self.fields:
            return
        
        # Order categories alphabetically but always place default at the end
        self.fields[field_name].queryset = (
            Category.objects
            .annotate(
                is_default=Case(
                    When(name__iexact=default_category, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
            .order_by('is_default', 'name')
        )
        
        # Make category required and remove empty label
        self.fields[field_name].required = True
        self.fields[field_name].empty_label = None
        
        # Set default category if form is not bound and no instance category
        default_cat = Category.objects.filter(name__iexact=default_category).first()
        if default_cat:
            if not self.is_bound and (not getattr(self.instance, f'{field_name}_id', None)):
                self.fields[field_name].initial = default_cat.pk


class CostValidationMixin:
    """Mixin to handle cost validation for subscription forms."""
    
    def validate_costs(self, cleaned_data):
        """
        Validate cost fields based on billing cycle.
        
        Args:
            cleaned_data: The cleaned form data
            
        Raises:
            ValidationError: If cost validation fails
        """
        monthly_cost = cleaned_data.get('monthly_cost')
        yearly_cost = cleaned_data.get('yearly_cost')
        billing_cycle = cleaned_data.get('billing_cycle')
        
        # Ensure at least one cost is provided
        if not monthly_cost and not yearly_cost:
            raise ValidationError('Please provide either monthly or yearly cost.')
        
        # Cost required per cycle
        if billing_cycle == 'monthly' and not monthly_cost:
            raise ValidationError('Monthly cost is required for monthly billing cycle.')
        
        if billing_cycle == 'yearly' and not yearly_cost:
            raise ValidationError('Yearly cost is required for yearly billing cycle.')
        
        # Validate cost values
        if monthly_cost is not None and monthly_cost < 0:
            raise ValidationError('Monthly cost cannot be negative.')
        
        if yearly_cost is not None and yearly_cost < 0:
            raise ValidationError('Yearly cost cannot be negative.')
        
        # Warn about unusual cost ratios
        if monthly_cost and yearly_cost:
            monthly_equiv = yearly_cost / 12
            ratio = monthly_cost / monthly_equiv if monthly_equiv > 0 else 0
            
            if ratio > 1.5:  # Monthly is 50% more expensive than yearly equivalent
                logger.warning(
                    "Unusual cost ratio detected: monthly=%s, yearly=%s, ratio=%s",
                    monthly_cost, yearly_cost, ratio
                )


class DurationValidationMixin:
    """Mixin to handle duration validation for subscription forms."""
    
    def validate_duration(self, cleaned_data):
        """
        Validate duration fields based on billing cycle.
        
        Args:
            cleaned_data: The cleaned form data
            
        Raises:
            ValidationError: If duration validation fails
        """
        billing_cycle = cleaned_data.get('billing_cycle')
        duration_months = cleaned_data.get('duration_months')
        duration_years = cleaned_data.get('duration_years')
        
        # Only validate if billing cycle is set
        if not billing_cycle:
            return
        
        # Normalize duration based on cycle
        if billing_cycle == 'monthly':
            if not duration_months:
                raise ValidationError('Duration in months is required for monthly billing cycle.')
            if duration_months <= 0:
                raise ValidationError('Duration in months must be greater than 0.')
            if duration_months > 120:  # 10 years max
                raise ValidationError('Duration in months cannot exceed 120 (10 years).')
            # Clear yearly duration for monthly billing
            cleaned_data['duration_years'] = None
            
        elif billing_cycle == 'yearly':
            if not duration_years:
                raise ValidationError('Duration in years is required for yearly billing cycle.')
            if duration_years <= 0:
                raise ValidationError('Duration in years must be greater than 0.')
            if duration_years > 10:  # 10 years max
                raise ValidationError('Duration in years cannot exceed 10.')
            # Clear monthly duration for yearly billing
            cleaned_data['duration_months'] = None


class LoggingMixin:
    """Mixin to provide consistent logging for form validation."""
    
    def log_validation_error(self, field, error_message, **context):
        """Log form validation errors with context."""
        logger.warning(
            "Form validation error: field=%s, error=%s, form=%s, context=%s",
            field, error_message, self.__class__.__name__, context
        )
    
    def log_validation_success(self, **context):
        """Log successful form validation."""
        logger.debug(
            "Form validation successful: form=%s, context=%s",
            self.__class__.__name__, context
        )


class FieldHelpTextMixin:
    """Mixin to provide consistent help text for form fields."""
    
    def add_help_texts(self, help_texts):
        """
        Add help texts to form fields.
        
        Args:
            help_texts: Dict mapping field names to help text strings
        """
        for field_name, help_text in help_texts.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = help_text


class ConditionalFieldMixin:
    """Mixin to handle conditional field visibility and validation."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_conditional_fields()
    
    def _setup_conditional_fields(self):
        """Setup conditional field behavior. Override in subclasses."""
        pass
    
    def get_conditional_fields(self):
        """Return dict of conditional field configurations."""
        return getattr(self, 'conditional_fields', {})
    
    def clean_conditional_fields(self, cleaned_data):
        """Clean conditional fields based on their visibility rules."""
        conditional_config = self.get_conditional_fields()
        
        for field_name, config in conditional_config.items():
            if field_name not in self.fields:
                continue
            
            # Check if field should be visible based on other field values
            depends_on = config.get('depends_on')
            condition = config.get('condition')
            
            if depends_on and condition:
                dependent_value = cleaned_data.get(depends_on)
                if not condition(dependent_value):
                    # Field is not visible, clear its value but don't remove from cleaned_data
                    # This prevents the form from getting "frozen"
                    if field_name in self.errors:
                        del self.errors[field_name]
                    # Don't clear the value in cleaned_data to avoid form freezing
        
        return cleaned_data
