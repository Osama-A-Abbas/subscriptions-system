from django import forms
from .models import Subscription, Category, Payment

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = [
            'name', 'monthly_cost', 'yearly_cost', 'billing_cycle', 
            'start_date', 'ending_date', 'auto_renewal', 'category'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'monthly_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'yearly_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'billing_cycle': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ending_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'auto_renewal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'category': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'name': 'Subscription Name',
            'monthly_cost': 'Monthly Cost ($)',
            'yearly_cost': 'Yearly Cost ($)',
            'billing_cycle': 'Billing Cycle',
            'start_date': 'Start Date',
            'ending_date': 'End Date (Optional)',
            'auto_renewal': 'Auto Renewal',
            'category': 'Category'
        }
    def clean(self):
        cleaned_data = super().clean()
        monthly_cost = cleaned_data.get('monthly_cost')
        yearly_cost = cleaned_data.get('yearly_cost')
        billing_cycle = cleaned_data.get('billing_cycle')

        # Ensure at least one cost is provided
        if not monthly_cost and not yearly_cost:
            raise forms.ValidationError('Please provide either monthly or yearly cost.')

        # If billing cycle is monthly, require monthly cost
        if billing_cycle == 'monthly' and not monthly_cost:
            raise forms.ValidationError('Monthly cost is required for monthly billing cycle.')

        # If billing cycle is yearly, require yearly cost
        if billing_cycle == 'yearly' and not yearly_cost:
            raise forms.ValidationError('Yearly cost is required for yearly billing cycle.')

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