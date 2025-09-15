"""
Mixin for payment tracking and management.

Provides methods for managing individual payment records and
payment status tracking.
"""

from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class PaymentManagementMixin:
    """Mixin providing payment management methods."""
    
    def mark_payment_paid(self, period_start, payment_date=None):
        """Mark a specific period as paid."""
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
            
            from ..payment import Payment
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
    
    def mark_payment_unpaid(self, period_start):
        """Mark a specific period as unpaid (clears payment_date)."""
        payment = self.payments.filter(
            billing_period_start=period_start
        ).first()
        if payment:
            payment.is_paid = False
            payment.payment_date = None
            payment.save()
            return payment
        # If no record exists yet, create an unpaid placeholder for consistency
        if self.billing_cycle == 'monthly':
            period_end = period_start + relativedelta(months=1) - timedelta(days=1)
        else:
            period_end = period_start + relativedelta(years=1) - timedelta(days=1)
        
        from ..payment import Payment
        return Payment.objects.create(
            subscription=self,
            billing_period_start=period_start,
            billing_period_end=period_end,
            amount=self.get_current_cost(),
            payment_date=None,
            is_paid=False
        )
    
    def get_paid_payments_count(self):
        """Get count of paid payments within the current schedule."""
        intended_starts = {start for start, _ in self._generate_intended_periods()}
        return self.payments.filter(is_paid=True, billing_period_start__in=intended_starts).count()

    def get_payment_progress_percentage(self):
        """Calculate payment progress as a percentage."""
        total_required = self.get_total_payments() or 0
        if total_required == 0:
            return 0
        paid_count = self.get_paid_payments_count()
        return int((paid_count / total_required) * 100)
