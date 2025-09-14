# subscriptions/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from decimal import Decimal

# Used in Subscription Model to determine the billing cycle choices
BILLING_CYCLE_CHOICES = [
    ("monthly", "Monthly"),
    ("yearly", "Yearly"),
]

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    
    # Used self-relation to enable easy controllable subcategories
    # If  parent = null, then it is a parent category, but if it has an id;
    # parent = some_category_id then it is a subcategory
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="subcategories")

    def __str__(self):
        return self.name
    
    def clean(self):
        """
        Validate category data to prevent invalid parent relationships.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()
        
        # Prevent self-referencing
        if self.parent == self:
            raise ValidationError({
                'parent': 'A category cannot be its own parent.'
            })
        
        # Prevent circular references
        if self.parent:
            self._check_circular_reference()
    
    def _check_circular_reference(self):
        """
        Check if setting this parent would create a circular reference.
        
        Raises:
            ValidationError: If circular reference would be created
        """
        if not self.parent:
            return
            
        # If this is a new instance (no pk), we can't check circular refs yet
        if not self.pk:
            return
            
        # Check if the parent is a descendant of this category
        current = self.parent
        visited = {self.pk}  # Track visited categories to prevent infinite loops
        
        while current:
            if current.pk in visited:
                raise ValidationError({
                    'parent': f'Setting "{self.parent.name}" as parent would create a circular reference.'
                })
            
            if current.pk == self.pk:
                raise ValidationError({
                    'parent': 'A category cannot be its own parent.'
                })
                
            visited.add(current.pk)
            current = current.parent
    
    def save(self, *args, **kwargs):
        """
        Override save to run validation before saving.
        """
        self.full_clean()
        super().save(*args, **kwargs)
    



###############
class Subscription(models.Model):
    # Basic Info
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    name = models.CharField(max_length=200)
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    yearly_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES)
    
    # Lifecycle Dates
    start_date = models.DateField()
    renewal_date = models.DateField(null=True, blank=True)
    
    # Duration (replaces ending_date)
    duration_months = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in months (for monthly billing)")
    duration_years = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in years (for yearly billing)")
    
    # Status & Settings
    is_active = models.BooleanField(default=True)
    auto_renewal = models.BooleanField(default=True)  # Default enabled
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_current_cost(self):
        """Get current cost based on billing cycle"""
        if self.billing_cycle == 'monthly':
            return self.monthly_cost or 0
        else:
            return self.yearly_cost or 0
    
    def get_ending_date(self):
        """Calculate ending date based on duration"""
        if self.billing_cycle == 'monthly' and self.duration_months:
            return self.start_date + relativedelta(months=self.duration_months)
        elif self.billing_cycle == 'yearly' and self.duration_years:
            return self.start_date + relativedelta(years=self.duration_years)
        return None
    
    def get_total_payments(self):
        """Get total number of payments for the entire duration"""
        if self.billing_cycle == 'monthly' and self.duration_months:
            return self.duration_months
        elif self.billing_cycle == 'yearly' and self.duration_years:
            return self.duration_years
        return None
    
    def get_total_cost(self):
        """Calculate total cost for the entire duration"""
        total_payments = self.get_total_payments()
        if total_payments:
            return self.get_current_cost() * total_payments
        return None
    
    def get_remaining_payments(self):
        """Get remaining number of payments"""
        if not self.get_ending_date():
            return None
            
        today = timezone.now().date()
        if today >= self.get_ending_date():
            return 0
            
        # Calculate how many payments have passed
        if self.billing_cycle == 'monthly':
            months_passed = (today.year - self.start_date.year) * 12 + (today.month - self.start_date.month)
            if today.day >= self.start_date.day:
                months_passed += 1
        else:  # yearly
            years_passed = today.year - self.start_date.year
            if today.month > self.start_date.month or (today.month == self.start_date.month and today.day >= self.start_date.day):
                years_passed += 1
        
        total_payments = self.get_total_payments()
        if total_payments:
            if self.billing_cycle == 'monthly':
                return max(0, total_payments - months_passed)
            else:
                return max(0, total_payments - years_passed)
        return None
    
    def calculate_next_renewal(self):
        """Calculate next renewal date from current renewal date"""
        if self.billing_cycle == "monthly":
            delta = relativedelta(months=1)
        else:
            delta = relativedelta(years=1)
        
        return self.renewal_date + delta
    
    def get_payment_status(self):
        """Get current payment status"""
        today = timezone.now().date()
        
        # Check if subscription has ended
        ending_date = self.get_ending_date()
        if ending_date and ending_date <= today:
            self.is_active = False
            self.save()
            return "ended"
        
        # Check if renewal date has passed
        if self.renewal_date <= today:
            # Calculate the start of current billing period
            if self.billing_cycle == 'monthly':
                current_period_start = self.renewal_date - relativedelta(months=1)
            else:
                current_period_start = self.renewal_date - relativedelta(years=1)
            
            # Check if there's a payment for this period
            has_payment = self.payments.filter(
                billing_period_start=current_period_start,
                is_paid=True
            ).exists()
            
            if not has_payment:
                return "unpaid"
            else:
                return "paid"
        
        return "paid"
    
    def should_auto_renew(self):
        """Check if subscription should auto-renew (only if paid)"""
        if not self.auto_renewal or not self.is_active or self.get_ending_date():
            return False
        
        # Only auto-renew if current period is paid
        return self.get_payment_status() == "paid"
    
    def save(self, *args, **kwargs):
        """Override save to set initial renewal date"""
        if not self.renewal_date:
            if self.billing_cycle == "monthly":
                delta = relativedelta(months=1)
            else:
                delta = relativedelta(years=1)
            self.renewal_date = self.start_date + delta
        super().save(*args, **kwargs)
        
        
        
class Payment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    billing_period_start = models.DateField()  # Start of the billing period
    billing_period_end = models.DateField()    # End of the billing period
    is_paid = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-billing_period_start']
        unique_together = ['subscription', 'billing_period_start']  # One payment per period
    
    def __str__(self):
        return f"{self.subscription.name} - {self.billing_period_start} to {self.billing_period_end}"