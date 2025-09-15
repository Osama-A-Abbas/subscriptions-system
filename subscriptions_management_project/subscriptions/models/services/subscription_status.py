"""
Service for subscription status determination and lifecycle management.

Handles complex status calculations and subscription lifecycle logic.
"""

from typing import Dict, List
from django.utils import timezone


class SubscriptionStatusService:
    """Service for subscription status and lifecycle management."""
    
    @staticmethod
    def determine_subscription_health(subscription) -> Dict[str, any]:
        """Determine overall health and status of a subscription."""
        today = timezone.now().date()
        
        # Basic status
        is_active = subscription.is_active
        days_until_renewal = subscription.days_until_renewal()
        payment_status = subscription.get_overall_payment_status()
        
        # Health indicators
        is_overdue = days_until_renewal is not None and days_until_renewal < 0
        is_renewing_soon = subscription.is_renewing_within(7)
        has_payment_issues = payment_status in ['unpaid', 'progressing']
        
        # Overall health score (0-100)
        health_score = 100
        if not is_active:
            health_score -= 50
        if is_overdue:
            health_score -= 30
        if has_payment_issues:
            health_score -= 20
        if is_renewing_soon:
            health_score -= 10
        
        return {
            'is_active': is_active,
            'is_overdue': is_overdue,
            'is_renewing_soon': is_renewing_soon,
            'has_payment_issues': has_payment_issues,
            'payment_status': payment_status,
            'days_until_renewal': days_until_renewal,
            'health_score': max(0, health_score),
            'health_level': SubscriptionStatusService._get_health_level(health_score)
        }
    
    @staticmethod
    def _get_health_level(score: int) -> str:
        """Convert health score to descriptive level."""
        if score >= 90:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 50:
            return 'fair'
        elif score >= 30:
            return 'poor'
        else:
            return 'critical'
    
    @staticmethod
    def get_subscription_alerts(subscription) -> List[Dict[str, str]]:
        """Get list of alerts/warnings for a subscription."""
        alerts = []
        health = SubscriptionStatusService.determine_subscription_health(subscription)
        
        if not subscription.is_active:
            alerts.append({
                'type': 'error',
                'message': 'Subscription is inactive'
            })
        
        if health['is_overdue']:
            alerts.append({
                'type': 'error', 
                'message': f'Payment is {abs(health["days_until_renewal"])} days overdue'
            })
        
        if health['is_renewing_soon']:
            alerts.append({
                'type': 'warning',
                'message': f'Renews in {health["days_until_renewal"]} days'
            })
        
        if health['has_payment_issues']:
            alerts.append({
                'type': 'warning',
                'message': f'Payment status: {health["payment_status"]}'
            })
        
        if not subscription.auto_renewal:
            alerts.append({
                'type': 'info',
                'message': 'Auto-renewal is disabled'
            })
        
        return alerts
    
    @staticmethod
    def should_send_reminder(subscription) -> bool:
        """Determine if a reminder should be sent for this subscription."""
        health = SubscriptionStatusService.determine_subscription_health(subscription)
        
        # Send reminders for:
        # 1. Renewals within 3 days
        # 2. Overdue payments
        # 3. Critical health status
        
        return (
            health['is_renewing_soon'] or 
            health['is_overdue'] or 
            health['health_level'] == 'critical'
        )
