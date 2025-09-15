"""Utilities for plan comparison and savings calculations.

Kept decoupled from models to allow reuse in selectors, services,
management commands, and tests without importing models.
"""

from __future__ import annotations

from typing import Optional
import math


def months_from_duration(months: Optional[int], years: Optional[int]) -> Optional[int]:
    if months:
        return months
    if years:
        return years * 12
    return None


def years_from_duration(months: Optional[int], years: Optional[int]) -> Optional[int]:
    if years:
        return years
    if months:
        return math.ceil(months / 12)
    return None


def monthly_equivalent_of_yearly(yearly: float) -> float:
    return yearly / 12 if yearly else 0.0


def simple_yearly_savings(monthly_cost: Optional[float], yearly_cost: Optional[float], months: Optional[int], years: Optional[int]) -> float:
    """Compute savings if switching from monthly to yearly based on duration.

    Returns 0 if any required value is missing.
    """
    if monthly_cost is None or yearly_cost is None:
        return 0.0
    total_months = months_from_duration(months, years)
    total_years = years_from_duration(months, years)
    if total_months is None or total_years is None:
        return 0.0
    monthly_total = monthly_cost * total_months
    yearly_total = yearly_cost * total_years
    return max(0.0, monthly_total - yearly_total)


