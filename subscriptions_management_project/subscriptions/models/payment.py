"""
Payment model for tracking subscription billing periods.

Represents individual payment records for specific billing periods
within a subscription's lifecycle.
"""

from django.db import models
from django.conf import settings

from .managers import PaymentManager


class Payment(models.Model):
    """
    Payment model representing a billing period payment.
    
    Each payment record corresponds to a specific billing period
    (monthly or yearly) within a subscription's duration.
    """
    
    subscription = models.ForeignKey(
        'Subscription', 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(
        null=True, 
        blank=True, 
        help_text="Date when payment was made (null for unpaid periods)"
    )
    billing_period_start = models.DateField(
        help_text="Start of the billing period"
    )
    billing_period_end = models.DateField(
        help_text="End of the billing period"
    )
    is_paid = models.BooleanField(
        default=False,
        help_text="Whether this payment has been completed"
    )
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Custom manager
    objects = PaymentManager()
    
    class Meta:
        ordering = ['-billing_period_start']
        unique_together = ['subscription', 'billing_period_start']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
    
    def __str__(self):
        """String representation of the payment."""
        return f"{self.subscription.name} - {self.billing_period_start} to {self.billing_period_end}"
    
    @property
    def is_overdue(self):
        """Check if this payment is overdue (past due and unpaid)."""
        from django.utils import timezone
        return not self.is_paid and self.billing_period_end < timezone.now().date()
    
    @property
    def days_overdue(self):
        """Number of days this payment is overdue (0 if not overdue)."""
        if not self.is_overdue:
            return 0
        from django.utils import timezone
        return (timezone.now().date() - self.billing_period_end).days
