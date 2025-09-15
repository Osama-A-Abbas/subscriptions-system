"""
Financial calculation and plan comparison services.

This module handles complex financial calculations, savings analysis,
and plan comparison logic for subscriptions.
"""

from __future__ import annotations

from typing import Optional, Dict, List, Any
from decimal import Decimal
import math


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
    
    @staticmethod
    def calculate_break_even_point(monthly_cost: float, yearly_cost: float) -> float:
        """Calculate the break-even point in months for yearly vs monthly billing."""
        if monthly_cost <= 0 or yearly_cost <= 0:
            return 0.0
        
        # Break-even when: monthly_cost * months = yearly_cost
        return yearly_cost / monthly_cost
    
    @staticmethod
    def calculate_roi_for_yearly_switch(
        monthly_cost: float, 
        yearly_cost: float, 
        months_remaining: int
    ) -> Dict[str, float]:
        """Calculate ROI for switching to yearly billing."""
        if monthly_cost <= 0 or yearly_cost <= 0 or months_remaining <= 0:
            return {'roi_percentage': 0.0, 'savings': 0.0, 'break_even_months': 0.0}
        
        monthly_total = monthly_cost * months_remaining
        yearly_total = yearly_cost
        savings = monthly_total - yearly_total
        
        # ROI as percentage of yearly cost
        roi_percentage = (savings / yearly_total) * 100 if yearly_total > 0 else 0.0
        break_even = PaymentCalculator.calculate_break_even_point(monthly_cost, yearly_cost)
        
        return {
            'roi_percentage': roi_percentage,
            'savings': savings,
            'break_even_months': break_even,
            'is_worthwhile': savings > 0 and months_remaining >= break_even
        }


class PlanComparisonService:
    """Service for comparing subscription plans and identifying optimization opportunities."""
    
    @staticmethod
    def find_high_cost_subscriptions(subscriptions: List[Any], threshold: float = 50.0) -> List[Dict[str, Any]]:
        """Find subscriptions with high monthly equivalent costs."""
        high_cost_subs = []
        
        for subscription in subscriptions:
            monthly_equiv = PaymentCalculator.calculate_monthly_equivalent_cost(subscription)
            
            if monthly_equiv >= threshold:
                high_cost_subs.append({
                    'subscription': subscription,
                    'monthly_equivalent': monthly_equiv,
                    'current_cycle': subscription.billing_cycle,
                    'potential_savings': PaymentCalculator.calculate_potential_savings(subscription)
                })
        
        # Sort by monthly equivalent cost (highest first)
        return sorted(high_cost_subs, key=lambda x: x['monthly_equivalent'], reverse=True)
    
    @staticmethod
    def find_savings_opportunities(subscriptions: List[Any]) -> List[Dict[str, Any]]:
        """Find subscriptions with potential savings opportunities."""
        opportunities = []
        
        for subscription in subscriptions:
            potential_savings = PaymentCalculator.calculate_potential_savings(subscription)
            
            if potential_savings > 0:
                opportunities.append({
                    'subscription': subscription,
                    'potential_savings': potential_savings,
                    'current_cycle': subscription.billing_cycle,
                    'recommended_cycle': 'yearly' if subscription.billing_cycle == 'monthly' else 'monthly',
                    'monthly_equivalent': PaymentCalculator.calculate_monthly_equivalent_cost(subscription)
                })
        
        # Sort by potential savings (highest first)
        return sorted(opportunities, key=lambda x: x['potential_savings'], reverse=True)
    
    @staticmethod
    def calculate_portfolio_optimization(subscriptions: List[Any]) -> Dict[str, Any]:
        """Calculate overall portfolio optimization recommendations."""
        total_monthly_cost = 0.0
        total_yearly_cost = 0.0
        total_potential_savings = 0.0
        
        monthly_subs = []
        yearly_subs = []
        
        for subscription in subscriptions:
            monthly_equiv = PaymentCalculator.calculate_monthly_equivalent_cost(subscription)
            potential_savings = PaymentCalculator.calculate_potential_savings(subscription)
            
            total_monthly_cost += monthly_equiv
            total_potential_savings += potential_savings
            
            if subscription.billing_cycle == 'monthly':
                monthly_subs.append(subscription)
            else:
                yearly_subs.append(subscription)
        
        # Calculate yearly equivalent
        total_yearly_cost = total_monthly_cost * 12
        
        return {
            'total_monthly_cost': total_monthly_cost,
            'total_yearly_cost': total_yearly_cost,
            'total_potential_savings': total_potential_savings,
            'monthly_subscriptions_count': len(monthly_subs),
            'yearly_subscriptions_count': len(yearly_subs),
            'optimization_percentage': (total_potential_savings / total_monthly_cost) * 100 if total_monthly_cost > 0 else 0.0,
            'recommendations': PlanComparisonService._generate_portfolio_recommendations(
                total_potential_savings, len(monthly_subs), len(yearly_subs)
            )
        }
    
    @staticmethod
    def _generate_portfolio_recommendations(
        total_savings: float, 
        monthly_count: int, 
        yearly_count: int
    ) -> List[str]:
        """Generate portfolio optimization recommendations."""
        recommendations = []
        
        if total_savings > 100:
            recommendations.append(f"Potential savings of ${total_savings:.2f} available through billing cycle optimization")
        
        if monthly_count > yearly_count * 2:
            recommendations.append("Consider switching more subscriptions to yearly billing for better rates")
        
        if yearly_count > monthly_count * 2:
            recommendations.append("Some yearly subscriptions might benefit from monthly billing for flexibility")
        
        if total_savings < 10:
            recommendations.append("Current billing cycles appear well-optimized")
        
        return recommendations
