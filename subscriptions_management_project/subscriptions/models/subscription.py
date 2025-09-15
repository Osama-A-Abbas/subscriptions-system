"""
Simplified Subscription model using mixins for clean separation of concerns.

This model focuses on data fields and basic functionality, with complex
business logic delegated to mixins and services.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import logging

from .base import BILLING_CYCLE_CHOICES, TimestampMixin, ValidationMixin
from .managers import SubscriptionManager
from .mixins import (
    CostCalculationsMixin,
    PaymentManagementMixin,
    RenewalLogicMixin,
    ScheduleManagementMixin
)

logger = logging.getLogger(__name__)


class Subscription(
    ValidationMixin,
    TimestampMixin,
    CostCalculationsMixin,
    PaymentManagementMixin,
    RenewalLogicMixin,
    ScheduleManagementMixin,
    models.Model
):
    """
    Subscription model representing a user's subscription service.
    
    This model uses mixins to separate concerns:
    - CostCalculationsMixin: Cost and duration calculations
    - PaymentManagementMixin: Payment tracking and management
    - RenewalLogicMixin: Renewal dates and status logic
    - ScheduleManagementMixin: Billing periods and schedule management
    """
    
    # Basic Information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="subscriptions"
    )
    name = models.CharField(max_length=200)
    monthly_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    yearly_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    billing_cycle = models.CharField(
        max_length=10, 
        choices=BILLING_CYCLE_CHOICES
    )
    
    # Lifecycle Dates
    start_date = models.DateField()
    renewal_date = models.DateField(null=True, blank=True)
    
    # Duration (replaces ending_date)
    duration_months = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Duration in months (for monthly billing)"
    )
    duration_years = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Duration in years (for yearly billing)"
    )
    
    # Status & Settings
    is_active = models.BooleanField(default=True)
    auto_renewal = models.BooleanField(
        default=True,
        help_text="Whether subscription auto-renews"
    )
    category = models.ForeignKey(
        'Category', 
        on_delete=models.PROTECT
    )
    
    # Custom manager
    objects = SubscriptionManager()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
    
    def __str__(self):
        """String representation of the subscription."""
        return f"{self.name} ({self.user.username})"
    
    # Model Lifecycle
    def save(self, *args, **kwargs):
        """Override save to keep renewal_date in sync with start_date and billing_cycle.

        Behaviors:
        - On create: if no renewal_date provided, set to start_date + 1 period.
        - On update: if start_date or billing_cycle changed, reset renewal_date relative to start_date.
        """
        should_reset_renewal = False
        schedule_changed = False

        if self.pk:
            try:
                original = Subscription.objects.get(pk=self.pk)
                if (original.start_date != self.start_date or
                    original.billing_cycle != self.billing_cycle or
                    original.duration_months != self.duration_months or
                    original.duration_years != self.duration_years):
                    schedule_changed = True
                if original.start_date != self.start_date or original.billing_cycle != self.billing_cycle:
                    should_reset_renewal = True
            except Subscription.DoesNotExist:
                # If somehow not found, treat as create
                should_reset_renewal = not bool(self.renewal_date)
                schedule_changed = True
        else:
            # New instance
            should_reset_renewal = not bool(self.renewal_date)
            # On create we will reconcile after saving to create current/past due placeholders
            schedule_changed = True

        if should_reset_renewal:
            if self.billing_cycle == "monthly":
                delta = relativedelta(months=1)
            else:
                delta = relativedelta(years=1)
            self.renewal_date = self.start_date + delta

        super().save(*args, **kwargs)

        # If the schedule changed, reset payments entirely (Option A)
        if schedule_changed:
            try:
                result = self.reset_payments_for_new_schedule()
                logger.info(
                    "Subscription %s schedule changed; reset payments: deleted=%s",
                    self.pk, result.get("deleted", 0)
                )
            except Exception as exc:
                logger.exception("Failed to reset payments for subscription %s: %s", self.pk, exc)
    
    def _run_custom_validation(self):
        """Validate subscription data."""
        # Ensure category is set (fallback to "Other" if needed)
        if not self.category_id:
            from .category import Category
            other_category, _ = Category.objects.get_or_create(
                name="Other",
                defaults={'description': 'Default category for uncategorized subscriptions'}
            )
            self.category = other_category
