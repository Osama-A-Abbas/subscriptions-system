# subscriptions/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
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
    

# Subscription Model
class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    name = models.CharField(max_length=200)
    # cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    yearly_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES)
    start_date = models.DateField() # Subscription starting date
    renewal_date = models.DateField(null=True, blank=True) # Subscription 
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.user})"
    
    def calculate_next_renewal(self):
        """
        Returns the next renewal date after today based on start_date and billing_cycle.
        """
        today = timezone.now().date()
        current = self.start_date
        if self.billing_cycle == "monthly":
            delta = relativedelta(months=1)
        else:
            delta = relativedelta(years=1)

        # move forward until current > today
        while current <= today:
            current += delta
        return current

    def save(self, *args, **kwargs):
        """
        Override the default save method to automatically set renewal_date.
        
        If renewal_date is not provided or is None, it will be automatically calculated
        based on the subscription's start_date and billing_cycle using the 
        calculate_next_renewal() method.
        
        Args:
            *args: Variable length argument list passed to parent save method
            **kwargs: Arbitrary keyword arguments passed to parent save method
            
        Note:
            This ensures that every subscription has a valid renewal_date when saved,
            preventing the need for manual calculation in views or other parts of the code.
        """
        if not self.renewal_date:
            self.renewal_date = self.calculate_next_renewal()
        super().save(*args, **kwargs)
           
    def potential_savings(self):
        """
        Calculate potential savings by switching billing cycles.
        
        For monthly subscriptions: calculates savings if switching to yearly billing.
        For yearly subscriptions: calculates extra cost if switching to monthly billing.
        
        Returns:
            tuple or None: 
                - If potential savings exist: (billing_cycle, amount) where:
                    - billing_cycle (str): The alternative billing cycle ("yearly" or "monthly")
                    - amount (Decimal): The savings amount (positive) or extra cost (negative)
                - If no potential savings: None
                
        Examples:
            - Monthly $10 subscription with yearly $100 option returns ("yearly", 20.00)
            - Yearly $100 subscription with monthly $10 option returns ("monthly", 20.00)
        """
        if self.billing_cycle == "monthly" and self.yearly_cost and self.monthly_cost:
            yearly_equivalent = self.monthly_cost * 12
            saving = yearly_equivalent - self.yearly_cost
            if saving > 0:
                return ("yearly", saving)
        elif self.billing_cycle == "yearly" and self.monthly_cost and self.yearly_cost:
            monthly_equivalent = self.yearly_cost / 12
            extra = self.monthly_cost * 12 - self.yearly_cost
            if extra > 0:
                return ("monthly", extra)
        return None