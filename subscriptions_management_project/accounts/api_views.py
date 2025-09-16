"""
API views for real-time username validation and other AJAX operations.

This module provides API endpoints for client-side validation and
real-time feedback without page reloads.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def check_username_availability(request):
    """
    API endpoint to check username availability in real-time.
    
    POST /api/check-username/
    Body: {"username": "desired_username", "current_user_id": 123}
    
    Returns:
    {
        "available": true/false,
        "message": "Username is available" or error message
    }
    """
    try:
        # Parse JSON data
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        current_user_id = data.get('current_user_id')
        
        if not username:
            return JsonResponse({
                'available': False,
                'message': 'Username is required'
            })
        
        # Check if username is available
        query = User.objects.filter(username__iexact=username)
        
        # Exclude current user if editing profile
        if current_user_id:
            query = query.exclude(pk=current_user_id)
        
        existing_user = query.first()
        
        if existing_user:
            # Check if it's an exact match or case-insensitive match
            if existing_user.username.lower() == username.lower():
                return JsonResponse({
                    'available': False,
                    'message': 'This username is already taken'
                })
            else:
                return JsonResponse({
                    'available': False,
                    'message': f"A user with a similar username '{existing_user.username}' already exists"
                })
        
        # Username is available
        return JsonResponse({
            'available': True,
            'message': 'Username is available'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'available': False,
            'message': 'Invalid request data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error checking username availability: {e}")
        return JsonResponse({
            'available': False,
            'message': 'An error occurred while checking username availability'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def check_email_availability(request):
    """
    API endpoint to check email availability in real-time.
    
    POST /api/check-email/
    Body: {"email": "user@example.com", "current_user_id": 123}
    
    Returns:
    {
        "available": true/false,
        "message": "Email is available" or error message
    }
    """
    try:
        # Parse JSON data
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        current_user_id = data.get('current_user_id')
        
        if not email:
            return JsonResponse({
                'available': False,
                'message': 'Email is required'
            })
        
        # Check if email is available
        query = User.objects.filter(email__iexact=email)
        
        # Exclude current user if editing profile
        if current_user_id:
            query = query.exclude(pk=current_user_id)
        
        existing_user = query.first()
        
        if existing_user:
            return JsonResponse({
                'available': False,
                'message': 'This email address is already registered'
            })
        
        # Email is available
        return JsonResponse({
            'available': True,
            'message': 'Email is available'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'available': False,
            'message': 'Invalid request data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error checking email availability: {e}")
        return JsonResponse({
            'available': False,
            'message': 'An error occurred while checking email availability'
        }, status=500)
