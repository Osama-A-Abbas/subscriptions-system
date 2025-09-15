"""
Subscription lifecycle management services.

This module handles subscription creation, updates, deletion, and
other lifecycle operations with proper validation and logging.
"""

from __future__ import annotations

from typing import Dict, Optional, Any
import logging

from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from ..models import Subscription, Category

User = get_user_model()
logger = logging.getLogger(__name__)


@transaction.atomic
def create_subscription(
    user: User,
    name: str,
    monthly_cost: Optional[float] = None,
    yearly_cost: Optional[float] = None,
    billing_cycle: str = 'monthly',
    start_date: Optional[str] = None,
    duration_months: Optional[int] = None,
    duration_years: Optional[int] = None,
    auto_renewal: bool = True,
    category: Optional[Category] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new subscription with validation and proper setup.
    
    Args:
        user: The user creating the subscription
        name: Name of the subscription
        monthly_cost: Monthly cost (required for monthly billing)
        yearly_cost: Yearly cost (required for yearly billing)
        billing_cycle: 'monthly' or 'yearly'
        start_date: Start date (defaults to today)
        duration_months: Duration in months (for monthly billing)
        duration_years: Duration in years (for yearly billing)
        auto_renewal: Whether to auto-renew
        category: Category for the subscription
        **kwargs: Additional subscription fields
        
    Returns:
        Dict with creation result and subscription details
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        # Validate required fields
        if not name.strip():
            raise ValidationError("Subscription name is required")
        
        if billing_cycle == 'monthly' and not monthly_cost:
            raise ValidationError("Monthly cost is required for monthly billing")
        
        if billing_cycle == 'yearly' and not yearly_cost:
            raise ValidationError("Yearly cost is required for yearly billing")
        
        if billing_cycle == 'monthly' and not duration_months:
            raise ValidationError("Duration in months is required for monthly billing")
        
        if billing_cycle == 'yearly' and not duration_years:
            raise ValidationError("Duration in years is required for yearly billing")
        
        # Set default category if none provided
        if not category:
            category, _ = Category.objects.get_or_create(
                name="Other",
                defaults={'description': 'Default category for uncategorized subscriptions'}
            )
        
        # Create the subscription
        subscription = Subscription.objects.create(
            user=user,
            name=name,
            monthly_cost=monthly_cost,
            yearly_cost=yearly_cost,
            billing_cycle=billing_cycle,
            start_date=start_date,
            duration_months=duration_months,
            duration_years=duration_years,
            auto_renewal=auto_renewal,
            category=category,
            **kwargs
        )
        
        logger.info(
            "Subscription created: id=%s, name=%s, user=%s, cycle=%s",
            subscription.id, subscription.name, user.id, billing_cycle
        )
        
        return {
            'success': True,
            'subscription': subscription,
            'message': f'Subscription "{subscription.name}" created successfully'
        }
        
    except Exception as e:
        logger.error(
            "Error creating subscription: user=%s, name=%s, error=%s",
            user.id, name, str(e)
        )
        raise


@transaction.atomic
def update_subscription(
    subscription: Subscription,
    **updates
) -> Dict[str, Any]:
    """
    Update an existing subscription with change tracking.
    
    Args:
        subscription: The subscription to update
        **updates: Fields to update
        
    Returns:
        Dict with update result and change details
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        # Track changes for logging
        changes = []
        original_data = {}
        
        for field, new_value in updates.items():
            if hasattr(subscription, field):
                old_value = getattr(subscription, field)
                original_data[field] = old_value
                
                if old_value != new_value:
                    changes.append(f"{field}: {old_value} → {new_value}")
                    setattr(subscription, field, new_value)
        
        if changes:
            subscription.save()
            
            logger.info(
                "Subscription updated: id=%s, changes=%s",
                subscription.id, '; '.join(changes)
            )
            
            return {
                'success': True,
                'subscription': subscription,
                'changes': changes,
                'original_data': original_data,
                'message': f'Subscription "{subscription.name}" updated successfully'
            }
        else:
            return {
                'success': True,
                'subscription': subscription,
                'changes': [],
                'message': 'No changes made to subscription'
            }
        
    except Exception as e:
        logger.error(
            "Error updating subscription: id=%s, error=%s",
            subscription.id, str(e)
        )
        raise


@transaction.atomic
def delete_subscription(subscription: Subscription) -> Dict[str, Any]:
    """
    Delete a subscription with proper cleanup.
    
    Args:
        subscription: The subscription to delete
        
    Returns:
        Dict with deletion result
        
    Raises:
        ValidationError: If deletion is not allowed
    """
    try:
        # Store subscription details for logging
        subscription_name = subscription.name
        subscription_id = subscription.id
        user_id = subscription.user.id
        
        # Delete the subscription (this will cascade to payments)
        subscription.delete()
        
        logger.info(
            "Subscription deleted: id=%s, name=%s, user=%s",
            subscription_id, subscription_name, user_id
        )
        
        return {
            'success': True,
            'subscription_name': subscription_name,
            'message': f'Subscription "{subscription_name}" deleted successfully'
        }
        
    except Exception as e:
        logger.error(
            "Error deleting subscription: id=%s, error=%s",
            subscription.id, str(e)
        )
        raise


def get_subscription_health(subscription: Subscription) -> Dict[str, Any]:
    """
    Get comprehensive health information for a subscription.
    
    Args:
        subscription: The subscription to analyze
        
    Returns:
        Dict with health information and recommendations
    """
    try:
        from .status_services import SubscriptionStatusService
        
        health_data = SubscriptionStatusService.determine_subscription_health(subscription)
        alerts = SubscriptionStatusService.get_subscription_alerts(subscription)
        
        # Add additional health metrics
        health_data.update({
            'total_cost': subscription.get_total_cost(),
            'remaining_payments': subscription.get_remaining_payments(),
            'days_until_end': subscription.get_ending_date(),
            'alerts': alerts,
            'recommendations': _get_health_recommendations(health_data)
        })
        
        return health_data
        
    except Exception as e:
        logger.error(
            "Error getting subscription health: id=%s, error=%s",
            subscription.id, str(e)
        )
        return {
            'health_score': 0,
            'health_level': 'unknown',
            'alerts': [{'type': 'error', 'message': 'Unable to determine health status'}],
            'recommendations': []
        }


def _get_health_recommendations(health_data: Dict[str, Any]) -> list:
    """Get recommendations based on health data."""
    recommendations = []
    
    if health_data.get('is_overdue'):
        recommendations.append("Consider paying overdue amounts to avoid service interruption")
    
    if health_data.get('is_renewing_soon'):
        recommendations.append("Prepare for upcoming renewal payment")
    
    if health_data.get('health_level') == 'critical':
        recommendations.append("Immediate attention required - review subscription status")
    
    if not health_data.get('is_active'):
        recommendations.append("Consider reactivating or canceling inactive subscription")
    
    return recommendations
