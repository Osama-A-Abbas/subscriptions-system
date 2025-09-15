"""
Form utilities and helper functions.

This module provides utility functions for form handling, validation,
and common form operations.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class FormFieldFactory:
    """Factory class for creating common form fields with consistent styling."""
    
    @staticmethod
    def create_text_input(placeholder=None, max_length=None, **attrs):
        """Create a styled text input field."""
        default_attrs = {'class': 'form-control'}
        if placeholder:
            default_attrs['placeholder'] = placeholder
        if max_length:
            default_attrs['maxlength'] = max_length
        
        default_attrs.update(attrs)
        return forms.TextInput(attrs=default_attrs)
    
    @staticmethod
    def create_number_input(step='0.01', min_value=None, max_value=None, **attrs):
        """Create a styled number input field."""
        default_attrs = {'class': 'form-control', 'step': step}
        if min_value is not None:
            default_attrs['min'] = min_value
        if max_value is not None:
            default_attrs['max'] = max_value
        
        default_attrs.update(attrs)
        return forms.NumberInput(attrs=default_attrs)
    
    @staticmethod
    def create_date_input(**attrs):
        """Create a styled date input field."""
        default_attrs = {'class': 'form-control', 'type': 'date'}
        default_attrs.update(attrs)
        return forms.DateInput(attrs=default_attrs)
    
    @staticmethod
    def create_select(choices=None, **attrs):
        """Create a styled select field."""
        default_attrs = {'class': 'form-select'}
        default_attrs.update(attrs)
        # Only pass choices if they are provided
        if choices is not None:
            return forms.Select(choices=choices, attrs=default_attrs)
        else:
            return forms.Select(attrs=default_attrs)
    
    @staticmethod
    def create_textarea(rows=3, placeholder=None, **attrs):
        """Create a styled textarea field."""
        default_attrs = {'class': 'form-control', 'rows': rows}
        if placeholder:
            default_attrs['placeholder'] = placeholder
        
        default_attrs.update(attrs)
        return forms.Textarea(attrs=default_attrs)
    
    @staticmethod
    def create_checkbox(**attrs):
        """Create a styled checkbox field."""
        default_attrs = {'class': 'form-check-input'}
        default_attrs.update(attrs)
        return forms.CheckboxInput(attrs=default_attrs)


class FormValidator:
    """Utility class for common form validation operations."""
    
    @staticmethod
    def validate_date_range(start_date, end_date, field_name='date'):
        """Validate that start_date is before end_date."""
        if start_date and end_date and start_date >= end_date:
            raise ValidationError(f'{field_name.title()} start date must be before end date.')
    
    @staticmethod
    def validate_future_date(date_value, field_name='date', allow_today=True):
        """Validate that date is in the future."""
        if date_value:
            today = timezone.now().date()
            if allow_today and date_value < today:
                raise ValidationError(f'{field_name.title()} cannot be in the past.')
            elif not allow_today and date_value <= today:
                raise ValidationError(f'{field_name.title()} must be in the future.')
    
    @staticmethod
    def validate_past_date(date_value, field_name='date', allow_today=True):
        """Validate that date is in the past."""
        if date_value:
            today = timezone.now().date()
            if allow_today and date_value > today:
                raise ValidationError(f'{field_name.title()} cannot be in the future.')
            elif not allow_today and date_value >= today:
                raise ValidationError(f'{field_name.title()} must be in the past.')
    
    @staticmethod
    def validate_positive_number(value, field_name='number'):
        """Validate that number is positive."""
        if value is not None and value <= 0:
            raise ValidationError(f'{field_name.title()} must be greater than 0.')
    
    @staticmethod
    def validate_decimal_precision(value, max_digits=10, decimal_places=2):
        """Validate decimal precision."""
        if value is not None:
            # Convert to string to check precision
            str_value = str(value)
            if '.' in str_value:
                integer_part, decimal_part = str_value.split('.')
                if len(integer_part) > max_digits - decimal_places:
                    raise ValidationError(f'Number has too many digits before decimal point.')
                if len(decimal_part) > decimal_places:
                    raise ValidationError(f'Number has too many decimal places (max {decimal_places}).')


class FormHelper:
    """Helper class for common form operations."""
    
    @staticmethod
    def get_billing_cycle_choices():
        """Get billing cycle choices for forms."""
        return [
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ]
    
    @staticmethod
    def get_duration_choices(max_months=120, max_years=10):
        """Get duration choices for forms."""
        month_choices = [(i, f'{i} month{"s" if i != 1 else ""}') for i in range(1, max_months + 1)]
        year_choices = [(i, f'{i} year{"s" if i != 1 else ""}') for i in range(1, max_years + 1)]
        
        return {
            'months': month_choices,
            'years': year_choices
        }
    
    @staticmethod
    def get_default_start_date():
        """Get default start date (today)."""
        return timezone.now().date()
    
    @staticmethod
    def get_date_range_choices(days_back=365, days_forward=365):
        """Get date range choices for forms."""
        today = timezone.now().date()
        start_date = today - timedelta(days=days_back)
        end_date = today + timedelta(days=days_forward)
        
        return {
            'start_date': start_date,
            'end_date': end_date
        }
    
    @staticmethod
    def format_currency(value, currency='$'):
        """Format value as currency."""
        if value is None:
            return f'{currency}0.00'
        
        try:
            decimal_value = Decimal(str(value))
            return f'{currency}{decimal_value:.2f}'
        except (ValueError, TypeError):
            return f'{currency}0.00'
    
    @staticmethod
    def parse_currency(value):
        """Parse currency string to decimal."""
        if not value:
            return None
        
        # Remove currency symbols and whitespace
        cleaned = str(value).replace('$', '').replace(',', '').strip()
        
        try:
            return Decimal(cleaned)
        except (ValueError, TypeError):
            return None


class FormErrorHandler:
    """Utility class for handling form errors consistently."""
    
    @staticmethod
    def add_field_error(form, field_name, message):
        """Add an error to a specific field."""
        if field_name not in form.errors:
            form.errors[field_name] = []
        form.errors[field_name].append(message)
    
    @staticmethod
    def add_non_field_error(form, message):
        """Add a non-field error to the form."""
        if not hasattr(form, '_errors') or '__all__' not in form._errors:
            form._errors['__all__'] = []
        form._errors['__all__'].append(message)
    
    @staticmethod
    def get_error_summary(form):
        """Get a summary of all form errors."""
        errors = []
        
        # Field errors
        for field_name, field_errors in form.errors.items():
            if field_name != '__all__':
                field_label = form.fields[field_name].label or field_name
                for error in field_errors:
                    errors.append(f'{field_label}: {error}')
        
        # Non-field errors
        if '__all__' in form.errors:
            errors.extend(form.errors['__all__'])
        
        return errors
    
    @staticmethod
    def log_form_errors(form, context=None):
        """Log form errors for debugging."""
        error_summary = FormErrorHandler.get_error_summary(form)
        if error_summary:
            logger.warning(
                "Form validation errors: form=%s, errors=%s, context=%s",
                form.__class__.__name__, error_summary, context
            )
