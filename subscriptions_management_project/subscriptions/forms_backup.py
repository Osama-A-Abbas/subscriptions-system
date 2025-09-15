from django import forms
from django.db.models import Case, When, IntegerField
import logging
from .models import Subscription, Category, Payment

class SubscriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order categories alphabetically but always place "Other" at the end
        self.fields['category'].queryset = (
            Category.objects
            .annotate(
                is_other=Case(
                    When(name__iexact='other', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
            .order_by('is_other', 'name')
        )
        # Make category required and default to "Other" if present
        self.fields['category'].required = True
        self.fields['category'].empty_label = None
        other = Category.objects.filter(name__iexact='other').first()
        if other:
            # Only set initial if form is not bound and instance has no category
            if not self.is_bound and (not getattr(self.instance, 'category_id', None)):
                self.fields['category'].initial = other.pk
    class Meta:
        model = Subscription
        fields = [
            'name', 'monthly_cost', 'yearly_cost', 'billing_cycle', 
            'start_date', 'duration_months', 'duration_years', 'auto_renewal', 'category'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'monthly_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'yearly_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'billing_cycle': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'duration_months': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'duration_years': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'auto_renewal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'category': forms.Select(attrs={'class': 'form-select'})
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
    def clean(self):
        logger = logging.getLogger(__name__)
        cleaned_data = super().clean()
        monthly_cost = cleaned_data.get('monthly_cost')
        yearly_cost = cleaned_data.get('yearly_cost')
        billing_cycle = cleaned_data.get('billing_cycle')
        duration_months = cleaned_data.get('duration_months')
        duration_years = cleaned_data.get('duration_years')

        logger.debug("SubscriptionForm.clean: cycle=%s, duration_months=%s, duration_years=%s", billing_cycle, duration_months, duration_years)

        # Ensure at least one cost is provided
        if not monthly_cost and not yearly_cost:
            logger.debug("Validation error: no cost provided")
            raise forms.ValidationError('Please provide either monthly or yearly cost.')

        # Cost required per cycle
        if billing_cycle == 'monthly' and not monthly_cost:
            logger.debug("Validation error: monthly cycle without monthly_cost")
            raise forms.ValidationError('Monthly cost is required for monthly billing cycle.')
        if billing_cycle == 'yearly' and not yearly_cost:
            logger.debug("Validation error: yearly cycle without yearly_cost")
            raise forms.ValidationError('Yearly cost is required for yearly billing cycle.')

        # Normalize duration based on cycle (to avoid sticky opposite field when switching)
        if billing_cycle == 'monthly':
            if not duration_months:
                logger.debug("Validation error: monthly cycle missing duration_months")
                raise forms.ValidationError('Duration in months is required for monthly billing cycle.')
            if duration_years:
                logger.debug("Normalizing: clearing duration_years because cycle is monthly")
                cleaned_data['duration_years'] = None
        elif billing_cycle == 'yearly':
            if not duration_years:
                logger.debug("Validation error: yearly cycle missing duration_years")
                raise forms.ValidationError('Duration in years is required for yearly billing cycle.')
            if duration_months:
                logger.debug("Normalizing: clearing duration_months because cycle is yearly")
                cleaned_data['duration_months'] = None

        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Entertainment, Productivity, Cloud Services'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description for this category'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'name': 'Category Name',
            'description': 'Description',
            'parent': 'Parent Category (Optional)'
        }
        
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_date', 'billing_period_start', 'billing_period_end', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'billing_period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'billing_period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }