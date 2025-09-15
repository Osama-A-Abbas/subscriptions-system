from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from subscriptions.models import Subscription
from subscriptions.selectors import get_user_subscriptions, compute_dashboard_totals

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            messages.success(request, 'Account created successfully! Welcome to Subscription Manager.')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
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