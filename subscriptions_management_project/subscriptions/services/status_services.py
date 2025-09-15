"""
Subscription status and health determination services.

This module handles status calculations, health monitoring, and
alert generation for subscriptions.
"""

from __future__ import annotations

from typing import Dict, List, Any
from django.utils import timezone


class SubscriptionStatusService:
    """Service for subscription status and lifecycle management."""
    
    @staticmethod
    def determine_subscription_health(subscription) -> Dict[str, Any]:
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
    
    @staticmethod
    def get_subscription_summary(subscription) -> Dict[str, Any]:
        """Get a comprehensive summary of subscription status and metrics."""
        health = SubscriptionStatusService.determine_subscription_health(subscription)
        alerts = SubscriptionStatusService.get_subscription_alerts(subscription)
        
        # Add financial metrics
        total_cost = subscription.get_total_cost()
        remaining_payments = subscription.get_remaining_payments()
        payment_progress = subscription.get_payment_progress_percentage()
        
        # Add lifecycle metrics
        ending_date = subscription.get_ending_date()
        days_until_end = None
        if ending_date:
            days_until_end = (ending_date - timezone.now().date()).days
        
        return {
            'subscription': subscription,
            'health': health,
            'alerts': alerts,
            'financial': {
                'total_cost': total_cost,
                'remaining_payments': remaining_payments,
                'payment_progress': payment_progress,
                'current_cost': subscription.get_current_cost()
            },
            'lifecycle': {
                'ending_date': ending_date,
                'days_until_end': days_until_end,
                'is_ending_soon': days_until_end is not None and days_until_end <= 30,
                'auto_renewal': subscription.auto_renewal
            },
            'recommendations': SubscriptionStatusService._generate_recommendations(
                health, alerts, remaining_payments, days_until_end
            )
        }
    
    @staticmethod
    def _generate_recommendations(
        health: Dict[str, Any], 
        alerts: List[Dict[str, str]], 
        remaining_payments: int, 
        days_until_end: int
    ) -> List[str]:
        """Generate actionable recommendations based on subscription status."""
        recommendations = []
        
        if health['is_overdue']:
            recommendations.append("Pay overdue amount immediately to avoid service interruption")
        
        if health['is_renewing_soon']:
            recommendations.append("Prepare payment for upcoming renewal")
        
        if health['health_level'] == 'critical':
            recommendations.append("Review subscription status and consider cancellation if no longer needed")
        
        if remaining_payments == 0 and days_until_end is not None and days_until_end <= 7:
            recommendations.append("Subscription ending soon - consider renewal or cancellation")
        
        if len(alerts) > 3:
            recommendations.append("Multiple issues detected - review subscription settings")
        
        if health['health_score'] >= 90:
            recommendations.append("Subscription is in excellent health - no action needed")
        
        return recommendations


def get_subscription_alerts(subscription) -> List[Dict[str, str]]:
    """Convenience function to get subscription alerts."""
    return SubscriptionStatusService.get_subscription_alerts(subscription)


def should_send_reminder(subscription) -> bool:
    """Convenience function to check if reminder should be sent."""
    return SubscriptionStatusService.should_send_reminder(subscription)
