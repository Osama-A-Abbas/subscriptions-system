"""
Custom middleware for error handling and logging.
"""

import logging
import traceback
from django.http import HttpResponseServerError
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)


class ErrorLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all errors and provide consistent error responses.
    """
    
    def process_exception(self, request, exception):
        """
        Log exceptions and provide consistent error responses.
        """
        # Log the exception
        logger.error(f"Unhandled exception in {request.path}: {exception}")
        logger.error(f"Request method: {request.method}")
        logger.error(f"Request user: {getattr(request, 'user', 'Anonymous')}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Log request details in debug mode
        if settings.DEBUG:
            logger.debug(f"Request data: {request.POST}")
            logger.debug(f"Request GET: {request.GET}")
            logger.debug(f"Request headers: {dict(request.headers)}")
        
        # Return appropriate error response
        if request.path.startswith('/api/'):
            # API endpoints return JSON
            return HttpResponseServerError(
                '{"error": "Internal server error"}',
                content_type='application/json'
            )
        else:
            # Web pages return HTML error page
            return HttpResponseServerError(
                '<html><body><h1>Internal Server Error</h1><p>An error occurred while processing your request.</p></body></html>'
            )


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests for monitoring and debugging.
    """
    
    def process_request(self, request):
        """
        Log incoming requests.
        """
        logger.info(f"Request: {request.method} {request.path}")
        logger.info(f"User: {getattr(request, 'user', 'Anonymous')}")
        logger.info(f"IP: {self.get_client_ip(request)}")
    
    def process_response(self, request, response):
        """
        Log outgoing responses.
        """
        logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
        return response
    
    def get_client_ip(self, request):
        """
        Get the client IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
