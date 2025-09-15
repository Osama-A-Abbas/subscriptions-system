"""
Consolidated services for the subscriptions app.

This module provides a clean, organized service layer that separates
business logic from views and models for better maintainability.

Services are organized by domain:
- payment_services: Payment-related operations
- subscription_services: Subscription lifecycle management  
- calculation_services: Financial calculations and comparisons
- status_services: Status determination and health checks
"""

from .payment_services import (
    mark_period_paid,
    mark_period_unpaid,
    reset_payments_after_schedule_change,
)

from .subscription_services import (
    create_subscription,
    update_subscription,
    delete_subscription,
    get_subscription_health,
)

from .calculation_services import (
    PaymentCalculator,
    PlanComparisonService,
)

from .status_services import (
    SubscriptionStatusService,
    get_subscription_alerts,
    should_send_reminder,
)

__all__ = [
    # Payment services
    'mark_period_paid',
    'mark_period_unpaid', 
    'reset_payments_after_schedule_change',
    
    # Subscription services
    'create_subscription',
    'update_subscription',
    'delete_subscription',
    'get_subscription_health',
    
    # Calculation services
    'PaymentCalculator',
    'PlanComparisonService',
    
    # Status services
    'SubscriptionStatusService',
    'get_subscription_alerts',
    'should_send_reminder',
]
