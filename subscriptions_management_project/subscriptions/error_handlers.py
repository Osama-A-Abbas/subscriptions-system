"""
Error handling utilities and decorators for the subscription system.
"""

import logging
import traceback
from functools import wraps
from django.http import JsonResponse, HttpResponseServerError
from django.contrib import messages
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, DatabaseError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .exceptions import (
    SubscriptionError, PaymentError, ValidationError, 
    BusinessLogicError, DataIntegrityError, ExternalServiceError
)

logger = logging.getLogger(__name__)


def handle_errors(view_func):
    """
    Decorator to handle common errors in views.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except PaymentError as e:
            logger.error(f"Payment error in {view_func.__name__}: {e}")
            messages.error(request, f"Payment error: {e}")
            return HttpResponseServerError("Payment processing error")
        except ValidationError as e:
            logger.error(f"Validation error in {view_func.__name__}: {e}")
            messages.error(request, f"Validation error: {e}")
            return HttpResponseServerError("Validation error")
        except BusinessLogicError as e:
            logger.error(f"Business logic error in {view_func.__name__}: {e}")
            messages.error(request, f"Business logic error: {e}")
            return HttpResponseServerError("Business logic error")
        except DataIntegrityError as e:
            logger.error(f"Data integrity error in {view_func.__name__}: {e}")
            messages.error(request, "Data integrity error occurred")
            return HttpResponseServerError("Data integrity error")
        except ExternalServiceError as e:
            logger.error(f"External service error in {view_func.__name__}: {e}")
            messages.error(request, "External service temporarily unavailable")
            return HttpResponseServerError("Service unavailable")
        except DjangoValidationError as e:
            logger.error(f"Django validation error in {view_func.__name__}: {e}")
            messages.error(request, f"Validation error: {e}")
            return HttpResponseServerError("Validation error")
        except IntegrityError as e:
            logger.error(f"Database integrity error in {view_func.__name__}: {e}")
            messages.error(request, "Data integrity error occurred")
            return HttpResponseServerError("Data integrity error")
        except DatabaseError as e:
            logger.error(f"Database error in {view_func.__name__}: {e}")
            messages.error(request, "Database error occurred")
            return HttpResponseServerError("Database error")
        except Exception as e:
            logger.error(f"Unexpected error in {view_func.__name__}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            messages.error(request, "An unexpected error occurred")
            return HttpResponseServerError("Internal server error")
    
    return wrapper


def handle_service_errors(service_name):
    """
    Decorator to handle errors in service methods.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PaymentError as e:
                logger.error(f"Payment error in {service_name}.{func.__name__}: {e}")
                raise
            except ValidationError as e:
                logger.error(f"Validation error in {service_name}.{func.__name__}: {e}")
                raise
            except BusinessLogicError as e:
                logger.error(f"Business logic error in {service_name}.{func.__name__}: {e}")
                raise
            except DataIntegrityError as e:
                logger.error(f"Data integrity error in {service_name}.{func.__name__}: {e}")
                raise
            except ExternalServiceError as e:
                logger.error(f"External service error in {service_name}.{func.__name__}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {service_name}.{func.__name__}: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise SubscriptionError(f"Unexpected error in {service_name}: {e}")
        
        return wrapper
    return decorator


def handle_model_errors(model_name):
    """
    Decorator to handle errors in model methods.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"Validation error in {model_name}.{func.__name__}: {e}")
                raise
            except DataIntegrityError as e:
                logger.error(f"Data integrity error in {model_name}.{func.__name__}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {model_name}.{func.__name__}: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise SubscriptionError(f"Unexpected error in {model_name}: {e}")
        
        return wrapper
    return decorator


class ErrorHandlerMixin:
    """
    Mixin for class-based views to handle errors consistently.
    """
    
    def handle_error(self, request, error, context=None):
        """
        Handle errors consistently across views.
        """
        if isinstance(error, PaymentError):
            logger.error(f"Payment error: {error}")
            messages.error(request, f"Payment error: {error}")
        elif isinstance(error, ValidationError):
            logger.error(f"Validation error: {error}")
            messages.error(request, f"Validation error: {error}")
        elif isinstance(error, BusinessLogicError):
            logger.error(f"Business logic error: {error}")
            messages.error(request, f"Business logic error: {error}")
        elif isinstance(error, DataIntegrityError):
            logger.error(f"Data integrity error: {error}")
            messages.error(request, "Data integrity error occurred")
        elif isinstance(error, ExternalServiceError):
            logger.error(f"External service error: {error}")
            messages.error(request, "External service temporarily unavailable")
        else:
            logger.error(f"Unexpected error: {error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            messages.error(request, "An unexpected error occurred")
        
        # Log context if provided
        if context:
            logger.error(f"Error context: {context}")
    
    def get_error_response(self, request, error, template=None):
        """
        Get appropriate error response based on error type.
        """
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'error': str(error),
                'type': error.__class__.__name__
            }, status=500)
        
        if template:
            return self.render_to_response(template, {'error': error})
        
        return HttpResponseServerError("Internal server error")


def log_operation(operation_name):
    """
    Decorator to log operations for debugging and monitoring.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Starting operation: {operation_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Operation completed successfully: {operation_name}")
                return result
            except Exception as e:
                logger.error(f"Operation failed: {operation_name} - {e}")
                raise
        
        return wrapper
    return decorator
