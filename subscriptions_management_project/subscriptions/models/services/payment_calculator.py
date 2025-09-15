"""
Service for complex payment calculations and billing logic.

Handles advanced payment calculations, savings analysis, and
plan comparison logic.
"""

from typing import Optional, Dict, List
from decimal import Decimal


class PaymentCalculator:
    """Service for complex payment and billing calculations."""
    
    @staticmethod
    def calculate_monthly_equivalent_cost(subscription) -> float:
        """Calculate monthly equivalent cost for any subscription."""
        if subscription.billing_cycle == 'monthly':
            return float(subscription.monthly_cost or 0)
        else:
            return float(subscription.yearly_cost or 0) / 12
    
    @staticmethod
    def calculate_potential_savings(subscription) -> float:
        """Calculate potential savings if switching billing cycles."""
        if subscription.billing_cycle == 'monthly':
            # Calculate what yearly would cost
            monthly_cost = float(subscription.monthly_cost or 0)
            yearly_cost = float(subscription.yearly_cost or 0)
            if yearly_cost > 0:
                return (monthly_cost * 12) - yearly_cost
        else:
            # Calculate what monthly would cost
            monthly_cost = float(subscription.monthly_cost or 0)
            yearly_cost = float(subscription.yearly_cost or 0)
            if monthly_cost > 0:
                return yearly_cost - (monthly_cost * 12)
        return 0.0
    
    @staticmethod
    def calculate_simple_yearly_savings(
        monthly_cost: Optional[float], 
        yearly_cost: Optional[float], 
        months: Optional[int], 
        years: Optional[int]
    ) -> float:
        """Compute savings if switching from monthly to yearly based on duration."""
        if monthly_cost is None or yearly_cost is None:
            return 0.0
        
        total_months = months or (years * 12) if years else 0
        total_years = years or (months // 12) if months else 0
        
        if total_months == 0 or total_years == 0:
            return 0.0
        
        monthly_total = monthly_cost * total_months
        yearly_total = yearly_cost * total_years
        return max(0.0, monthly_total - yearly_total)
    
    @staticmethod
    def get_duration_months_total(months: Optional[int], years: Optional[int]) -> int:
        """Get total duration in months."""
        if months:
            return months
        if years:
            return years * 12
        return 0
    
    @staticmethod
    def get_duration_years_total(months: Optional[int], years: Optional[int]) -> int:
        """Get total duration in years."""
        if years:
            return years
        if months:
            return (months + 11) // 12  # Round up
        return 0
    
    @staticmethod
    def calculate_total_cost_over_duration(
        subscription, 
        duration_months: Optional[int] = None, 
        duration_years: Optional[int] = None
    ) -> Dict[str, float]:
        """Calculate total cost over duration for both billing types."""
        months = duration_months or subscription.duration_months
        years = duration_years or subscription.duration_years
        
        monthly_cost = float(subscription.monthly_cost or 0)
        yearly_cost = float(subscription.yearly_cost or 0)
        
        total_months = PaymentCalculator.get_duration_months_total(months, years)
        total_years = PaymentCalculator.get_duration_years_total(months, years)
        
        return {
            'monthly_total': monthly_cost * total_months,
            'yearly_total': yearly_cost * total_years,
            'savings': max(0.0, (monthly_cost * total_months) - (yearly_cost * total_years))
        }
