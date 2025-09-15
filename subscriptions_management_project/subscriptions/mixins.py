"""
View mixins for common subscription functionality.

These mixins provide reusable functionality that can be composed
into views for consistent behavior across the application.
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)


class UserOwnershipMixin:
    """
    Mixin to ensure users can only access their own subscriptions.
    
    Provides automatic filtering of querysets to only include
    objects owned by the current user.
    """
    
    def get_queryset(self):
        """Filter queryset to only include user's own subscriptions."""
        if hasattr(self, 'model') and hasattr(self.model, 'user'):
            return self.model.objects.filter(user=self.request.user)
        return super().get_queryset()


class LoggingMixin:
    """
    Mixin to provide consistent logging across views.
    
    Automatically logs view actions with user context and
    error handling for debugging and monitoring.
    """
    
    def log_action(self, action, object_name=None, **kwargs):
        """Log a view action with context."""
        log_data = {
            'action': action,
            'user_id': self.request.user.id,
            'view_name': self.__class__.__name__,
        }
        
        if object_name:
            log_data['object'] = object_name
        
        log_data.update(kwargs)
        
        logger.info("View action: %s", log_data)
    
    def log_error(self, error, **kwargs):
        """Log an error with context."""
        log_data = {
            'error': str(error),
            'user_id': self.request.user.id,
            'view_name': self.__class__.__name__,
        }
        log_data.update(kwargs)
        
        logger.error("View error: %s", log_data)


class MessageMixin:
    """
    Mixin to provide consistent user messaging.
    
    Provides methods for displaying success, error, and info
    messages to users with consistent formatting.
    """
    
    def add_success_message(self, message):
        """Add a success message."""
        messages.success(self.request, message)
    
    def add_error_message(self, message):
        """Add an error message."""
        messages.error(self.request, message)
    
    def add_warning_message(self, message):
        """Add a warning message."""
        messages.warning(self.request, message)
    
    def add_info_message(self, message):
        """Add an info message."""
        messages.info(self.request, message)


class TransactionMixin:
    """
    Mixin to provide database transaction safety.
    
    Wraps view operations in database transactions to ensure
    data consistency and proper rollback on errors.
    """
    
    def execute_with_transaction(self, operation, *args, **kwargs):
        """Execute an operation within a database transaction."""
        from django.db import transaction
        
        try:
            with transaction.atomic():
                return operation(*args, **kwargs)
        except Exception as e:
            logger.error("Transaction failed in %s: %s", 
                        self.__class__.__name__, e)
            raise


class ContextDataMixin:
    """
    Mixin to provide common context data for templates.
    
    Adds frequently used context variables to all views
    that use this mixin.
    """
    
    def get_context_data(self, **kwargs):
        """Add common context data."""
        context = super().get_context_data(**kwargs)
        
        # Add user context
        context['user'] = self.request.user
        
        # Add current timestamp for templates
        from django.utils import timezone
        context['current_time'] = timezone.now()
        
        return context
