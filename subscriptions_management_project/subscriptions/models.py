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
    
    def get_billing_periods(self):
        """Generate billing periods and create payment records as needed"""
        from datetime import timedelta
        
        periods = []
        current_date = self.start_date
        today = timezone.now().date()
        
        total_payments = self.get_total_payments()
        if not total_payments:
            return periods
        
        for period_num in range(1, total_payments + 1):
            if self.billing_cycle == 'monthly':
                period_end = current_date + relativedelta(months=1) - timedelta(days=1)
                next_period_start = current_date + relativedelta(months=1)
            else:  # yearly
                period_end = current_date + relativedelta(years=1) - timedelta(days=1)
                next_period_start = current_date + relativedelta(years=1)
            
            # Check if payment record exists
            payment = self.payments.filter(
                billing_period_start=current_date
            ).first()
            
            # Create payment record if:
            # 1. Period is current or past due AND no payment record exists
            # 2. User manually marks as paid
            should_create_record = (
                (period_end >= today or current_date <= today) and 
                not payment
            )
            
            if should_create_record:
                payment = self._create_payment_record(
                    period_start=current_date,
                    period_end=period_end,
                    period_number=period_num
                )
            
            periods.append({
                'period_number': period_num,
                'start': current_date,
                'end': period_end,
                'amount': self.get_current_cost(),
                'is_paid': payment.is_paid if payment else False,
                'payment': payment,
                'is_current': self._is_current_period(current_date, period_end),
                'is_past_due': self._is_past_due(current_date, period_end)
            })
            
            current_date = next_period_start
        
        return periods
    
    def _create_payment_record(self, period_start, period_end, period_number):
        """Create a payment record for a specific period"""
        return Payment.objects.create(
            subscription=self,
            billing_period_start=period_start,
            billing_period_end=period_end,
            amount=self.get_current_cost(),
            payment_date=None,  # Will be set when user marks as paid
            is_paid=False
        )
    
    def _is_current_period(self, period_start, period_end):
        """Check if this period is currently active"""
        today = timezone.now().date()
        return period_start <= today <= period_end
    
    def _is_past_due(self, period_start, period_end):
        """Check if this period is past due"""
        today = timezone.now().date()
        return period_end < today
    
    def mark_payment_paid(self, period_start, payment_date=None):
        """Mark a specific period as paid"""
        if not payment_date:
            payment_date = timezone.now().date()
        
        # Get or create payment record
        payment = self.payments.filter(
            billing_period_start=period_start
        ).first()
        
        if not payment:
            # Create payment record if it doesn't exist
            if self.billing_cycle == 'monthly':
                period_end = period_start + relativedelta(months=1) - timedelta(days=1)
            else:
                period_end = period_start + relativedelta(years=1) - timedelta(days=1)
            
            payment = Payment.objects.create(
                subscription=self,
                billing_period_start=period_start,
                billing_period_end=period_end,
                amount=self.get_current_cost(),
                payment_date=payment_date,
                is_paid=True
            )
        else:
            # Update existing payment record
            payment.payment_date = payment_date
            payment.is_paid = True
            payment.save()
        
        return payment
    
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
    payment_date = models.DateField(null=True, blank=True)  # Allow null for unpaid periods
    billing_period_start = models.DateField()  # Start of the billing period
    billing_period_end = models.DateField()    # End of the billing period
    is_paid = models.BooleanField(default=False)  # Default to False for unpaid periods
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-billing_period_start']
        unique_together = ['subscription', 'billing_period_start']  # One payment per period
    
    def __str__(self):
        return f"{self.subscription.name} - {self.billing_period_start} to {self.billing_period_end}"