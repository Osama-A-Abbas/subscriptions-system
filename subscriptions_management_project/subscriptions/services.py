"""Write-side domain services for subscriptions.

Services encapsulate business operations that mutate state. They are
explicitly called from views or signals and are easy to unit test.
"""

from __future__ import annotations

from datetime import date
from typing import Dict

from django.db import transaction

from .models import Subscription


@transaction.atomic
def mark_period_paid(subscription: Subscription, period_start: date) -> None:
    """Mark a specific billing period as paid.

    Delegates to the model method to keep domain rules in one place.
    Wrapped in an atomic transaction for safety.
    """
    subscription.mark_payment_paid(period_start)


@transaction.atomic
def mark_period_unpaid(subscription: Subscription, period_start: date) -> None:
    """Mark a specific billing period as unpaid (clears payment date)."""
    subscription.mark_payment_unpaid(period_start)


@transaction.atomic
def reset_payments_after_schedule_change(subscription: Subscription) -> Dict[str, int]:
    """Reset all payments when the schedule changes.

    This is Option A from our decisions: delete all rows and let the UI
    render fresh state without pre-creating future placeholders.
    """
    return subscription.reset_payments_for_new_schedule()


