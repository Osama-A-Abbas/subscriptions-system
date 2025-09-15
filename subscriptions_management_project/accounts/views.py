from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import logging

from .forms import CustomUserCreationForm, UserProfileForm
from subscriptions.models import Subscription
from subscriptions.selectors import get_user_subscriptions, compute_dashboard_totals

logger = logging.getLogger(__name__)

def register(request):
    """
    Enhanced user registration with email field and better UX.
    
    Features:
    - Email field for user registration
    - Auto-login after successful registration
    - Bootstrap styling and error handling
    - Success messages and redirects
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)  # Auto-login after registration
                messages.success(
                    request, 
                    f'Account created successfully! Welcome to Subscription Manager, {user.username}!'
                )
                logger.info(f"New user registered: {user.username} ({user.email})")
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"Error during user registration: {e}")
                messages.error(request, 'An error occurred during registration. Please try again.')
        else:
            logger.warning(f"Registration form validation failed: {form.errors}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    """
    Enhanced user profile view with update functionality.
    
    Features:
    - Display user information
    - Handle profile updates via modal form
    - Success/error messages
    - Logging for security
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            form = UserProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Your profile has been updated successfully!')
                    logger.info(f"User profile updated: {request.user.username}")
                    return redirect('profile')
                except ValidationError as e:
                    messages.error(request, f'Validation error: {e}')
                    logger.warning(f"Profile update validation error for {request.user.username}: {e}")
                except Exception as e:
                    messages.error(request, 'An error occurred while updating your profile. Please try again.')
                    logger.error(f"Error updating profile for {request.user.username}: {e}")
            else:
                messages.error(request, 'Please correct the errors below.')
                logger.warning(f"Profile form validation failed for {request.user.username}: {form.errors}")
        else:
            messages.error(request, 'Invalid action.')
    
    return render(request, 'registration/profile.html', {'user': request.user})

@login_required
def dashboard(request):
    """Dashboard view using selectors (thin view).

    - Fetches active subscriptions via selector with eager loading
    - Computes totals via selector to keep logic out of the view
    """
    subscriptions_qs = get_user_subscriptions(request.user)
    total_monthly_cost, total_yearly_cost, total_count = compute_dashboard_totals(subscriptions_qs)

    context = {
        'subscriptions': list(subscriptions_qs),  # materialize for reuse in templates
        'total_monthly_cost': total_monthly_cost,
        'total_yearly_cost': total_yearly_cost,
        'total_subscriptions': total_count,
    }
    return render(request, 'dashboard.html', context)

def login_redirect(request):
    """Redirect to Django's built-in login view"""
    return redirect('login')

def logout_redirect(request):
    """Redirect to Django's built-in logout view"""
    return redirect('logout')