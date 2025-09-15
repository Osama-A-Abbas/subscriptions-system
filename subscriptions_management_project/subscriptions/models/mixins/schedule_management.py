"""
Mixin for billing schedule and period management.

Provides methods for generating billing periods, managing payment records,
and handling schedule changes.
"""

from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class ScheduleManagementMixin:
    """Mixin providing schedule and billing period management methods."""
    
    def get_billing_periods(self):
        """Generate billing periods and create payment records as needed."""
        import logging
        logger = logging.getLogger(__name__)
        
        periods = []
        current_date = self.start_date
        today = timezone.now().date()
        
        total_payments = self.get_total_payments()
        if not total_payments:
            logger.debug(f"No total payments for subscription {self.pk}")
            return periods
        
        logger.debug(f"Generating {total_payments} billing periods for subscription {self.pk}, start_date: {current_date}, today: {today}")
        
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
            is_current_period = self._is_current_period(current_date, period_end)
            is_past_due_period = self._is_past_due(current_date, period_end)
            
            should_create_record = (
                (is_current_period or is_past_due_period) and 
                not payment
            )
            
            if should_create_record:
                payment = self._create_payment_record(
                    period_start=current_date,
                    period_end=period_end,
                    period_number=period_num
                )
                logger.debug(f"Created payment record for period {period_num}: {current_date} to {period_end}")
            
            is_current = self._is_current_period(current_date, period_end)
            is_past_due = self._is_past_due(current_date, period_end)
            
            if is_current:
                logger.debug(f"Period {period_num} is CURRENT: {current_date} to {period_end}")
            elif is_past_due:
                logger.debug(f"Period {period_num} is PAST DUE: {current_date} to {period_end}")
            
            periods.append({
                'period_number': period_num,
                'start': current_date,
                'end': period_end,
                'amount': self.get_current_cost(),
                'is_paid': payment.is_paid if payment else False,
                'payment': payment,
                'is_current': is_current,
                'is_past_due': is_past_due
            })
            
            current_date = next_period_start
        
        return periods
    
    def refresh_billing_periods(self):
        """Force refresh billing periods by clearing any cached data and regenerating."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Refreshing billing periods for subscription {self.pk}")
        
        # Clear any existing payment records that might be stale
        # This ensures we start fresh
        self.payments.all().delete()
        
        # Regenerate billing periods
        periods = self.get_billing_periods()
        
        logger.info(f"Refreshed billing periods for subscription {self.pk}: {len(periods)} periods generated")
        
        return periods
    
    def _create_payment_record(self, period_start, period_end, period_number):
        """Create a payment record for a specific period."""
        from ..payment import Payment
        return Payment.objects.create(
            subscription=self,
            billing_period_start=period_start,
            billing_period_end=period_end,
            amount=self.get_current_cost(),
            payment_date=None,  # Will be set when user marks as paid
            is_paid=False
        )
    
    def _is_current_period(self, period_start, period_end):
        """Check if this period is currently active."""
        today = timezone.now().date()
        # A period is current if today falls within its date range
        # Include both start and end dates (end date is the last day of the period)
        is_current = period_start <= today <= period_end
        
        # Debug logging for troubleshooting
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Checking if period {period_start} to {period_end} is current (today: {today}): {is_current}")
        
        return is_current
    
    def _is_past_due(self, period_start, period_end):
        """Check if this period is past due."""
        today = timezone.now().date()
        return period_end < today

    def _generate_intended_periods(self):
        """Return a list of tuples (start_date, end_date) for intended periods."""
        periods = []
        total = self.get_total_payments() or 0
        if total <= 0:
            return periods
        current_start = self.start_date
        for _ in range(total):
            if self.billing_cycle == 'monthly':
                end = current_start + relativedelta(months=1) - timedelta(days=1)
                next_start = current_start + relativedelta(months=1)
            else:
                end = current_start + relativedelta(years=1) - timedelta(days=1)
                next_start = current_start + relativedelta(years=1)
            periods.append((current_start, end))
            current_start = next_start
        return periods

    def reconcile_payments(self):
        """Reconcile stored Payment rows with the current schedule.

        - Keep all paid payments (even if out of schedule) as history.
        - Delete unpaid payments that are no longer part of the intended schedule.
        - Ensure placeholders exist for current/past-due intended periods.

        Returns a dict with counts of changes for optional display.
        """
        intended = self._generate_intended_periods()
        intended_starts = {start for start, _ in intended}
        today = timezone.now().date()

        existing = list(self.payments.all())
        deleted = 0
        created = 0

        # Delete unpaid records that do not belong to intended schedule
        for p in existing:
            if not p.is_paid and p.billing_period_start not in intended_starts:
                p.delete()
                deleted += 1

        # Refresh existing after deletions
        existing_by_start = {p.billing_period_start: p for p in self.payments.all()}

        # Create placeholders for current/past-due intended periods if missing
        for start, end in intended:
            if start not in existing_by_start:
                is_current = self._is_current_period(start, end)
                is_past_due = end < today
                if is_current or is_past_due:
                    from ..payment import Payment
                    Payment.objects.create(
                        subscription=self,
                        billing_period_start=start,
                        billing_period_end=end,
                        amount=self.get_current_cost(),
                        payment_date=None,
                        is_paid=False,
                    )
                    created += 1

        return {"deleted_unpaid": deleted, "created_placeholders": created}

    def reset_payments_for_new_schedule(self):
        """Delete all payments for this subscription (no placeholders created).

        Returns dict with count of deleted rows.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        qs = self.payments.all()
        deleted = qs.count()
        qs.delete()
        
        logger.info(f"Reset payments for subscription {self.pk}: deleted {deleted} payment records")
        return {"deleted": deleted}
