"""
Custom managers and querysets for subscription models.

This module contains custom managers that provide convenient methods
for common queries and business logic operations.
"""

from django.db import models
from django.utils import timezone
from django.db.models import Q, Count, Case, When, IntegerField


class SubscriptionQuerySet(models.QuerySet):
    """Custom queryset for Subscription model with business logic methods."""
    
    def active(self):
        """Return only active subscriptions."""
        return self.filter(is_active=True)
    
    def for_user(self, user):
        """Return subscriptions for a specific user."""
        return self.filter(user=user)
    
    def renewing_soon(self, days=7):
        """Return subscriptions renewing within specified days."""
        today = timezone.now().date()
        future_date = today + timezone.timedelta(days=days)
        return self.filter(
            renewal_date__lte=future_date,
            renewal_date__gte=today,
            is_active=True
        )
    
    def overdue(self):
        """Return subscriptions with overdue payments."""
        today = timezone.now().date()
        return self.filter(
            renewal_date__lt=today,
            is_active=True
        )
    
    def with_payment_status(self):
        """Annotate queryset with payment status information."""
        return self.annotate(
            total_payments=Count('payments'),
            paid_payments=Count(
                'payments',
                filter=Q(payments__is_paid=True)
            )
        )
    
    def monthly_billing(self):
        """Return subscriptions with monthly billing cycle."""
        return self.filter(billing_cycle='monthly')
    
    def yearly_billing(self):
        """Return subscriptions with yearly billing cycle."""
        return self.filter(billing_cycle='yearly')
    
    def by_category(self, category):
        """Return subscriptions in a specific category."""
        return self.filter(category=category)
    
    def with_auto_renewal(self):
        """Return subscriptions with auto-renewal enabled."""
        return self.filter(auto_renewal=True)
    
    def without_auto_renewal(self):
        """Return subscriptions with auto-renewal disabled."""
        return self.filter(auto_renewal=False)


class SubscriptionManager(models.Manager):
    """Custom manager for Subscription model."""
    
    def get_queryset(self):
        """Return custom queryset with business logic methods."""
        return SubscriptionQuerySet(self.model, using=self._db)
    
    def active(self):
        """Return only active subscriptions."""
        return self.get_queryset().active()
    
    def for_user(self, user):
        """Return subscriptions for a specific user."""
        return self.get_queryset().for_user(user)
    
    def renewing_soon(self, days=7):
        """Return subscriptions renewing within specified days."""
        return self.get_queryset().renewing_soon(days)
    
    def overdue(self):
        """Return subscriptions with overdue payments."""
        return self.get_queryset().overdue()
    
    def with_payment_status(self):
        """Annotate queryset with payment status information."""
        return self.get_queryset().with_payment_status()
    
    def monthly_billing(self):
        """Return subscriptions with monthly billing cycle."""
        return self.get_queryset().monthly_billing()
    
    def yearly_billing(self):
        """Return subscriptions with yearly billing cycle."""
        return self.get_queryset().yearly_billing()
    
    def by_category(self, category):
        """Return subscriptions in a specific category."""
        return self.get_queryset().by_category(category)
    
    def with_auto_renewal(self):
        """Return subscriptions with auto-renewal enabled."""
        return self.get_queryset().with_auto_renewal()
    
    def without_auto_renewal(self):
        """Return subscriptions with auto-renewal disabled."""
        return self.get_queryset().without_auto_renewal()


class CategoryQuerySet(models.QuerySet):
    """Custom queryset for Category model."""
    
    def parent_categories(self):
        """Return only parent categories (no parent)."""
        return self.filter(parent__isnull=True)
    
    def subcategories(self):
        """Return only subcategories (have a parent)."""
        return self.filter(parent__isnull=False)
    
    def with_subcategory_count(self):
        """Annotate with count of subcategories."""
        return self.annotate(
            subcategory_count=Count('subcategories')
        )
    
    def with_subscription_count(self):
        """Annotate with count of subscriptions."""
        return self.annotate(
            subscription_count=Count('subscriptions')
        )


class CategoryManager(models.Manager):
    """Custom manager for Category model."""
    
    def get_queryset(self):
        """Return custom queryset with business logic methods."""
        return CategoryQuerySet(self.model, using=self._db)
    
    def parent_categories(self):
        """Return only parent categories (no parent)."""
        return self.get_queryset().parent_categories()
    
    def subcategories(self):
        """Return only subcategories (have a parent)."""
        return self.get_queryset().subcategories()
    
    def with_subcategory_count(self):
        """Annotate with count of subcategories."""
        return self.get_queryset().with_subcategory_count()
    
    def with_subscription_count(self):
        """Annotate with count of subscriptions."""
        return self.get_queryset().with_subscription_count()


class PaymentQuerySet(models.QuerySet):
    """Custom queryset for Payment model."""
    
    def paid(self):
        """Return only paid payments."""
        return self.filter(is_paid=True)
    
    def unpaid(self):
        """Return only unpaid payments."""
        return self.filter(is_paid=False)
    
    def overdue(self):
        """Return overdue payments (past due and unpaid)."""
        today = timezone.now().date()
        return self.filter(
            billing_period_end__lt=today,
            is_paid=False
        )
    
    def current_period(self):
        """Return payments for current billing period."""
        today = timezone.now().date()
        return self.filter(
            billing_period_start__lte=today,
            billing_period_end__gte=today
        )
    
    def for_subscription(self, subscription):
        """Return payments for a specific subscription."""
        return self.filter(subscription=subscription)
    
    def by_date_range(self, start_date, end_date):
        """Return payments within a date range."""
        return self.filter(
            billing_period_start__gte=start_date,
            billing_period_end__lte=end_date
        )


class PaymentManager(models.Manager):
    """Custom manager for Payment model."""
    
    def get_queryset(self):
        """Return custom queryset with business logic methods."""
        return PaymentQuerySet(self.model, using=self._db)
    
    def paid(self):
        """Return only paid payments."""
        return self.get_queryset().paid()
    
    def unpaid(self):
        """Return only unpaid payments."""
        return self.get_queryset().unpaid()
    
    def overdue(self):
        """Return overdue payments (past due and unpaid)."""
        return self.get_queryset().overdue()
    
    def current_period(self):
        """Return payments for current billing period."""
        return self.get_queryset().current_period()
    
    def for_subscription(self, subscription):
        """Return payments for a specific subscription."""
        return self.get_queryset().for_subscription(subscription)
    
    def by_date_range(self, start_date, end_date):
        """Return payments within a date range."""
        return self.get_queryset().by_date_range(start_date, end_date)
