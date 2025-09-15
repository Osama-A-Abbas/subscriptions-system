"""
Mixin for cost and duration calculations.

Provides methods for calculating costs, durations, and financial metrics
for subscription models.
"""

from dateutil.relativedelta import relativedelta


class CostCalculationsMixin:
    """Mixin providing cost and duration calculation methods."""
    
    def get_current_cost(self):
        """Get current cost based on billing cycle."""
        if self.billing_cycle == 'monthly':
            return self.monthly_cost or 0
        else:
            return self.yearly_cost or 0
    
    def get_ending_date(self):
        """Calculate ending date based on duration."""
        if self.billing_cycle == 'monthly' and self.duration_months:
            return self.start_date + relativedelta(months=self.duration_months)
        elif self.billing_cycle == 'yearly' and self.duration_years:
            return self.start_date + relativedelta(years=self.duration_years)
        return None
    
    def get_total_payments(self):
        """Get total number of payments for the entire duration."""
        if self.billing_cycle == 'monthly' and self.duration_months:
            return self.duration_months
        elif self.billing_cycle == 'yearly' and self.duration_years:
            return self.duration_years
        return None
    
    def get_total_cost(self):
        """Calculate total cost for the entire duration."""
        total_payments = self.get_total_payments()
        if total_payments:
            return self.get_current_cost() * total_payments
        return None
    
    def get_remaining_payments(self):
        """Get remaining number of payments."""
        if not self.get_ending_date():
            return None
            
        from django.utils import timezone
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
