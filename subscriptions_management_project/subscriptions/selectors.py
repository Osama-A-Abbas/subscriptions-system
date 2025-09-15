"""Read-only query helpers (selectors) for the subscriptions domain.

Selectors encapsulate queries and simple reporting calculations, keeping
views thin and making query reuse easy and testable.
"""

from __future__ import annotations

from typing import Iterable, Tuple

from django.db.models import QuerySet
from django.contrib.auth import get_user_model

from .models import Subscription


def get_user_subscriptions(user) -> QuerySet[Subscription]:
    """Return active subscriptions for a user with sensible eager loading.

    - Uses select_related for `category` to avoid N+1 in table views.
    - Ordered by `-created_at` so recent items appear first.
    """
    return (
        Subscription.objects.select_related("category")
        .filter(user=user, is_active=True)
        .order_by("-created_at")
    )


def compute_dashboard_totals(subscriptions: Iterable[Subscription]) -> Tuple[float, float, int]:
    """Compute (total_monthly_cost, total_yearly_cost, count) for dashboard.

    - Monthly total includes yearly plans normalized to monthly (yearly/12).
    - Yearly total is the monthly-equivalent total * 12.
    """
    total_monthly_direct = 0.0
    total_yearly_direct = 0.0

    for sub in subscriptions:
        if sub.billing_cycle == "monthly":
            total_monthly_direct += float(sub.monthly_cost or 0)
        else:
            total_yearly_direct += float(sub.yearly_cost or 0)

    monthly_equiv_from_yearly = total_yearly_direct / 12 if total_yearly_direct > 0 else 0.0
    total_monthly_cost = total_monthly_direct + monthly_equiv_from_yearly
    total_yearly_cost = total_monthly_cost * 12

    return total_monthly_cost, total_yearly_cost, len(list(subscriptions))


