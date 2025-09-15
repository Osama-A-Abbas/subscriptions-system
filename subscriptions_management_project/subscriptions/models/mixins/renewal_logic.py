"""
Mixin for renewal and status logic.

Provides methods for calculating renewal dates, checking renewal status,
and determining subscription lifecycle states.
"""

from django.utils import timezone
from dateutil.relativedelta import relativedelta


class RenewalLogicMixin:
    """Mixin providing renewal and status logic methods."""
    
    def calculate_next_renewal(self):
        """Calculate next renewal date from current renewal date."""
        if self.billing_cycle == "monthly":
            delta = relativedelta(months=1)
        else:
            delta = relativedelta(years=1)
        
        return self.renewal_date + delta
    
    def days_until_renewal(self):
        """Return number of days until next renewal, or None if unknown."""
        if not self.renewal_date or not self.is_active:
            return None
        today = timezone.now().date()
        return (self.renewal_date - today).days
    
    def is_renewing_within(self, days: int = 7) -> bool:
        """Whether the subscription renews within given days from today."""
        remaining_days = self.days_until_renewal()
        if remaining_days is None:
            return False
        # Do not flag if already past due
        if remaining_days < 0:
            return False
        return remaining_days <= days
    
    def get_payment_status(self):
        """Get current payment status."""
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

    def get_overall_payment_status(self):
        """Aggregate subscription payment status across all required periods.

        Returns one of: 'unpaid', 'progressing', 'completed'.
        """
        total_required = self.get_total_payments() or 0
        intended_starts = {start for start, _ in self._generate_intended_periods()}
        paid_count = self.payments.filter(is_paid=True, billing_period_start__in=intended_starts).count()

        if total_required == 0:
            # No duration configured; fallback to current-period logic
            return "paid" if self.get_payment_status() == "paid" else "unpaid"

        if paid_count <= 0:
            return "unpaid"
        if paid_count >= total_required:
            return "completed"
        return "progressing"
    
    def should_auto_renew(self):
        """Check if subscription should auto-renew (only if paid)."""
        if not self.auto_renewal or not self.is_active or self.get_ending_date():
            return False
        
        # Only auto-renew if current period is paid
        return self.get_payment_status() == "paid"
