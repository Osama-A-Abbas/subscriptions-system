"""
Custom exceptions for the subscription management system.
"""


class SubscriptionError(Exception):
    """Base exception for subscription-related errors."""
    pass


class PaymentError(SubscriptionError):
    """Exception raised for payment-related errors."""
    pass


class ValidationError(SubscriptionError):
    """Exception raised for validation errors."""
    pass


class BusinessLogicError(SubscriptionError):
    """Exception raised for business logic violations."""
    pass


class DataIntegrityError(SubscriptionError):
    """Exception raised for data integrity issues."""
    pass


class ExternalServiceError(SubscriptionError):
    """Exception raised for external service failures."""
    pass
