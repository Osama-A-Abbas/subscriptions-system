"""
Payment-related services for subscription management.

This module handles all payment operations including marking payments
as paid/unpaid, payment validation, and payment record management.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, Optional
import logging

from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import Subscription

logger = logging.getLogger(__name__)


@transaction.atomic
def mark_period_paid(subscription: Subscription, period_start: date, payment_date: Optional[date] = None) -> Dict[str, any]:
    """
    Mark a specific billing period as paid.
    
    Args:
        subscription: The subscription instance
        period_start: Start date of the billing period
        payment_date: Optional payment date (defaults to today)
        
    Returns:
        Dict with operation result and payment details
        
    Raises:
        ValidationError: If the period is invalid or already paid
    """
    try:
        # Validate the subscription and period
        if not subscription.is_active:
            raise ValidationError("Cannot mark payment for inactive subscription")
        
        # Mark the payment as paid via model method
        payment = subscription.mark_payment_paid(period_start, payment_date)
        
        logger.info(
            "Payment marked as paid: subscription=%s, period=%s, amount=%s",
            subscription.id, period_start, payment.amount
        )
        
        return {
            'success': True,
            'payment': payment,
            'message': f'Payment for period {period_start} marked as paid'
        }
        
    except Exception as e:
        logger.error(
            "Error marking payment as paid: subscription=%s, period=%s, error=%s",
            subscription.id, period_start, str(e)
        )
        raise


@transaction.atomic
def mark_period_unpaid(subscription: Subscription, period_start: date) -> Dict[str, any]:
    """
    Mark a specific billing period as unpaid.
    
    Args:
        subscription: The subscription instance
        period_start: Start date of the billing period
        
    Returns:
        Dict with operation result and payment details
        
    Raises:
        ValidationError: If the period is invalid
    """
    try:
        # Validate the subscription
        if not subscription.is_active:
            raise ValidationError("Cannot modify payment for inactive subscription")
        
        # Mark the payment as unpaid via model method
        payment = subscription.mark_payment_unpaid(period_start)
        
        logger.info(
            "Payment marked as unpaid: subscription=%s, period=%s",
            subscription.id, period_start
        )
        
        return {
            'success': True,
            'payment': payment,
            'message': f'Payment for period {period_start} marked as unpaid'
        }
        
    except Exception as e:
        logger.error(
            "Error marking payment as unpaid: subscription=%s, period=%s, error=%s",
            subscription.id, period_start, str(e)
        )
        raise


@transaction.atomic
def reset_payments_after_schedule_change(subscription: Subscription) -> Dict[str, int]:
    """
    Reset all payments when the subscription schedule changes.
    
    This implements Option A from our decisions: delete all payment rows
    and let the UI render fresh state without pre-creating future placeholders.
    
    Args:
        subscription: The subscription instance
        
    Returns:
        Dict with count of deleted payment records
        
    Raises:
        ValidationError: If the subscription is invalid
    """
    try:
        # Validate the subscription
        if not subscription.pk:
            raise ValidationError("Cannot reset payments for unsaved subscription")
        
        # Reset payments via model method
        result = subscription.reset_payments_for_new_schedule()
        
        logger.info(
            "Payments reset after schedule change: subscription=%s, deleted=%s",
            subscription.id, result.get('deleted', 0)
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Error resetting payments: subscription=%s, error=%s",
            subscription.id, str(e)
        )
        raise


def validate_payment_period(subscription: Subscription, period_start: date) -> bool:
    """
    Validate that a payment period is valid for the subscription.
    
    Args:
        subscription: The subscription instance
        period_start: Start date of the billing period
        
    Returns:
        True if the period is valid, False otherwise
    """
    try:
        # Check if the period is within the subscription's intended periods
        intended_periods = subscription._generate_intended_periods()
        period_starts = {start for start, _ in intended_periods}
        
        return period_start in period_starts
        
    except Exception as e:
        logger.error(
            "Error validating payment period: subscription=%s, period=%s, error=%s",
            subscription.id, period_start, str(e)
        )
        return False


def get_payment_summary(subscription: Subscription) -> Dict[str, any]:
    """
    Get a summary of payment information for a subscription.
    
    Args:
        subscription: The subscription instance
        
    Returns:
        Dict with payment summary information
    """
    try:
        total_payments = subscription.get_total_payments() or 0
        paid_count = subscription.get_paid_payments_count()
        progress_percentage = subscription.get_payment_progress_percentage()
        overall_status = subscription.get_overall_payment_status()
        
        return {
            'total_payments': total_payments,
            'paid_count': paid_count,
            'unpaid_count': total_payments - paid_count,
            'progress_percentage': progress_percentage,
            'overall_status': overall_status,
            'is_completed': overall_status == 'completed',
            'is_progressing': overall_status == 'progressing',
            'is_unpaid': overall_status == 'unpaid'
        }
        
    except Exception as e:
        logger.error(
            "Error getting payment summary: subscription=%s, error=%s",
            subscription.id, str(e)
        )
        return {
            'total_payments': 0,
            'paid_count': 0,
            'unpaid_count': 0,
            'progress_percentage': 0,
            'overall_status': 'unknown',
            'is_completed': False,
            'is_progressing': False,
            'is_unpaid': True
        }
