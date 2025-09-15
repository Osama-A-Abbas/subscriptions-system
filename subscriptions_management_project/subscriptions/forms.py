"""
Enhanced forms for subscription management with improved validation and UX.

This module provides clean, well-organized forms with comprehensive validation,
better user experience, and consistent styling.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging

from .models import Subscription, Category, Payment
from .form_mixins import (
    BootstrapFormMixin,
    CategoryOrderingMixin,
    CostValidationMixin,
    DurationValidationMixin,
    LoggingMixin,
    FieldHelpTextMixin,
    ConditionalFieldMixin
)
from .form_utils import FormFieldFactory, FormValidator, FormHelper, FormErrorHandler

logger = logging.getLogger(__name__)


class SubscriptionForm(
    BootstrapFormMixin,
    CategoryOrderingMixin,
    CostValidationMixin,
    DurationValidationMixin,
    LoggingMixin,
    FieldHelpTextMixin,
    forms.ModelForm
):
    """
    Enhanced subscription form with comprehensive validation and better UX.
    
    Features:
    - Automatic Bootstrap styling
    - Smart category ordering and default selection
    - Cost and duration validation
    - Comprehensive error handling
    """
    
    class Meta:
        model = Subscription
        fields = [
            'name', 'monthly_cost', 'yearly_cost', 'billing_cycle', 
            'start_date', 'duration_months', 'duration_years', 'auto_renewal', 'category'
        ]
        widgets = {
            'name': FormFieldFactory.create_text_input(
                placeholder='e.g., Netflix, Spotify, Adobe Creative Cloud',
                max_length=200
            ),
            'monthly_cost': FormFieldFactory.create_number_input(
                step='0.01',
                min_value=0,
                placeholder='0.00'
            ),
            'yearly_cost': FormFieldFactory.create_number_input(
                step='0.01',
                min_value=0,
                placeholder='0.00'
            ),
            'billing_cycle': FormFieldFactory.create_select(
                choices=FormHelper.get_billing_cycle_choices()
            ),
            'start_date': FormFieldFactory.create_date_input(),
            'duration_months': FormFieldFactory.create_number_input(
                min_value=1,
                max_value=120,
                placeholder='1'
            ),
            'duration_years': FormFieldFactory.create_number_input(
                min_value=1,
                max_value=10,
                placeholder='1'
            ),
            'auto_renewal': FormFieldFactory.create_checkbox(),
            'category': FormFieldFactory.create_select()
        }
        labels = {
            'name': 'Subscription Name',
            'monthly_cost': 'Monthly Cost ($)',
            'yearly_cost': 'Yearly Cost ($)',
            'billing_cycle': 'Billing Cycle',
            'start_date': 'Start Date',
            'duration_months': 'Duration (Months)',
            'duration_years': 'Duration (Years)',
            'auto_renewal': 'Auto Renewal',
            'category': 'Category'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Setup category field
        self.setup_category_field()
        
        # Add help texts
        self.add_help_texts({
            'name': 'Enter a descriptive name for your subscription',
            'monthly_cost': 'Cost per month (required for monthly billing)',
            'yearly_cost': 'Cost per year (required for yearly billing)',
            'billing_cycle': 'Choose how often you are billed',
            'start_date': 'When did/will this subscription start?',
            'duration_months': 'How many months will this subscription last?',
            'duration_years': 'How many years will this subscription last?',
            'auto_renewal': 'Automatically renew when the subscription expires',
            'category': 'Organize your subscriptions by category'
        })
        
        # Set default start date if not provided
        if not self.instance.pk and not self.data.get('start_date'):
            self.fields['start_date'].initial = FormHelper.get_default_start_date()
    
    def clean_name(self):
        """Validate subscription name."""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError('Subscription name must be at least 2 characters long.')
            if len(name) > 200:
                raise ValidationError('Subscription name cannot exceed 200 characters.')
        return name
    
    def clean_start_date(self):
        """Validate start date."""
        start_date = self.cleaned_data.get('start_date')
        if start_date:
            # Allow both past and future dates for better UX
            # Users may want to add existing subscriptions or plan future ones
            pass  # No date restrictions
        return start_date
    
    def clean_monthly_cost(self):
        """Validate monthly cost."""
        monthly_cost = self.cleaned_data.get('monthly_cost')
        if monthly_cost is not None:
            FormValidator.validate_positive_number(monthly_cost, 'Monthly cost')
            FormValidator.validate_decimal_precision(monthly_cost)
        return monthly_cost
    
    def clean_yearly_cost(self):
        """Validate yearly cost."""
        yearly_cost = self.cleaned_data.get('yearly_cost')
        if yearly_cost is not None:
            FormValidator.validate_positive_number(yearly_cost, 'Yearly cost')
            FormValidator.validate_decimal_precision(yearly_cost)
        return yearly_cost
    
    def clean(self):
        """Comprehensive form validation."""
        cleaned_data = super().clean()
        
        # Debug logging
        logger.debug("SubscriptionForm.clean: billing_cycle=%s, duration_months=%s, duration_years=%s", 
                    cleaned_data.get('billing_cycle'), 
                    cleaned_data.get('duration_months'), 
                    cleaned_data.get('duration_years'))
        
        try:
            # Validate costs
            self.validate_costs(cleaned_data)
            
            # Validate duration
            self.validate_duration(cleaned_data)
            
            # Additional business logic validation
            self._validate_business_rules(cleaned_data)
            
            self.log_validation_success()
            
        except ValidationError as e:
            self.log_validation_error('form', str(e))
            FormErrorHandler.add_non_field_error(self, str(e))
            raise
        
        return cleaned_data
    
    def _validate_business_rules(self, cleaned_data):
        """Validate business rules and constraints."""
        billing_cycle = cleaned_data.get('billing_cycle')
        monthly_cost = cleaned_data.get('monthly_cost')
        yearly_cost = cleaned_data.get('yearly_cost')
        
        # Check for unusual cost ratios
        if monthly_cost and yearly_cost:
            monthly_equiv = yearly_cost / 12
            ratio = monthly_cost / monthly_equiv if monthly_equiv > 0 else 0
            
            if ratio > 2.0:  # Monthly is 100% more expensive than yearly equivalent
                logger.warning(
                    "Very unusual cost ratio: monthly=%s, yearly=%s, ratio=%s",
                    monthly_cost, yearly_cost, ratio
                )
                # Don't raise error, just log warning


class CategoryForm(
    BootstrapFormMixin,
    LoggingMixin,
    FieldHelpTextMixin,
    forms.ModelForm
):
    """
    Enhanced category form with validation and better UX.
    
    Features:
    - Automatic Bootstrap styling
    - Parent category validation
    - Circular reference prevention
    - Helpful placeholder text
    """
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']
        widgets = {
            'name': FormFieldFactory.create_text_input(
                placeholder='e.g., Entertainment, Productivity, Cloud Services',
                max_length=150
            ),
            'description': FormFieldFactory.create_textarea(
                rows=3,
                placeholder='Optional description for this category'
            ),
            'parent': FormFieldFactory.create_select()
        }
        labels = {
            'name': 'Category Name',
            'description': 'Description',
            'parent': 'Parent Category (Optional)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help texts
        self.add_help_texts({
            'name': 'Enter a clear, descriptive name for the category',
            'description': 'Optional description to help organize your subscriptions',
            'parent': 'Select a parent category to create a subcategory'
        })
        
        # Filter parent choices to prevent self-reference
        if self.instance.pk:
            self.fields['parent'].queryset = Category.objects.exclude(pk=self.instance.pk)
        else:
            self.fields['parent'].queryset = Category.objects.all()
    
    def clean_name(self):
        """Validate category name."""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError('Category name must be at least 2 characters long.')
            if len(name) > 150:
                raise ValidationError('Category name cannot exceed 150 characters.')
            
            # Check for duplicate names (case-insensitive)
            existing = Category.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('A category with this name already exists.')
        
        return name
    
    def clean(self):
        """Validate category relationships."""
        cleaned_data = super().clean()
        
        try:
            parent = cleaned_data.get('parent')
            
            if parent:
                # Check for circular references
                self._check_circular_reference(parent)
            
            self.log_validation_success()
            
        except ValidationError as e:
            self.log_validation_error('form', str(e))
            raise
        
        return cleaned_data
    
    def _check_circular_reference(self, parent):
        """Check for circular reference in parent-child relationship."""
        if self.instance.pk:
            # Check if parent is a descendant of this category
            current = parent
            visited = {self.instance.pk}
            
            while current:
                if current.pk in visited:
                    raise ValidationError('This would create a circular reference.')
                visited.add(current.pk)
                current = current.parent


class PaymentForm(
    BootstrapFormMixin,
    LoggingMixin,
    FieldHelpTextMixin,
    forms.ModelForm
):
    """
    Enhanced payment form with validation and better UX.
    
    Features:
    - Automatic Bootstrap styling
    - Date range validation
    - Amount validation
    - Helpful placeholder text
    """
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_date', 'billing_period_start', 'billing_period_end', 'notes']
        widgets = {
            'amount': FormFieldFactory.create_number_input(
                step='0.01',
                min_value=0,
                placeholder='0.00'
            ),
            'payment_date': FormFieldFactory.create_date_input(),
            'billing_period_start': FormFieldFactory.create_date_input(),
            'billing_period_end': FormFieldFactory.create_date_input(),
            'notes': FormFieldFactory.create_textarea(
                rows=3,
                placeholder='Optional notes about this payment'
            )
        }
        labels = {
            'amount': 'Payment Amount ($)',
            'payment_date': 'Payment Date',
            'billing_period_start': 'Billing Period Start',
            'billing_period_end': 'Billing Period End',
            'notes': 'Notes'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help texts
        self.add_help_texts({
            'amount': 'Enter the payment amount',
            'payment_date': 'When was this payment made?',
            'billing_period_start': 'Start date of the billing period',
            'billing_period_end': 'End date of the billing period',
            'notes': 'Optional notes about this payment'
        })
        
        # Set default payment date to today
        if not self.instance.pk and not self.data.get('payment_date'):
            self.fields['payment_date'].initial = timezone.now().date()
    
    def clean_amount(self):
        """Validate payment amount."""
        amount = self.cleaned_data.get('amount')
        if amount is not None:
            FormValidator.validate_positive_number(amount, 'Payment amount')
            FormValidator.validate_decimal_precision(amount)
        return amount
    
    def clean_payment_date(self):
        """Validate payment date."""
        payment_date = self.cleaned_data.get('payment_date')
        if payment_date:
            FormValidator.validate_past_date(payment_date, 'Payment date', allow_today=True)
        return payment_date
    
    def clean(self):
        """Validate payment date ranges."""
        cleaned_data = super().clean()
        
        try:
            start_date = cleaned_data.get('billing_period_start')
            end_date = cleaned_data.get('billing_period_end')
            
            if start_date and end_date:
                FormValidator.validate_date_range(start_date, end_date, 'Billing period')
            
            self.log_validation_success()
            
        except ValidationError as e:
            self.log_validation_error('form', str(e))
            raise
        
        return cleaned_data


class SubscriptionSearchForm(BootstrapFormMixin, forms.Form):
    """
    Form for searching and filtering subscriptions.
    
    Features:
    - Search by name
    - Filter by category
    - Filter by billing cycle
    - Filter by status
    """
    
    name = forms.CharField(
        required=False,
        widget=FormFieldFactory.create_text_input(
            placeholder='Search by subscription name...'
        ),
        label='Search'
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=FormFieldFactory.create_select(),
        label='Category'
    )
    
    billing_cycle = forms.ChoiceField(
        choices=[('', 'All Cycles')] + FormHelper.get_billing_cycle_choices(),
        required=False,
        widget=FormFieldFactory.create_select(),
        label='Billing Cycle'
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('renewing_soon', 'Renewing Soon'),
            ('overdue', 'Overdue')
        ],
        required=False,
        widget=FormFieldFactory.create_select(),
        label='Status'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Order categories alphabetically
        self.fields['category'].queryset = Category.objects.order_by('name')