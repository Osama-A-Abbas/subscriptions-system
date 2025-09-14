from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from subscriptions.models import Subscription

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
    # Get user's subscriptions
    subscriptions = Subscription.objects.filter(user=request.user, is_active=True)
    
    # Calculate total monthly cost
    total_monthly = sum(sub.monthly_cost or 0 for sub in subscriptions if sub.billing_cycle == 'monthly')
    total_yearly = sum(sub.yearly_cost or 0 for sub in subscriptions if sub.billing_cycle == 'yearly')
    
    # Convert yearly to monthly equivalent for total
    yearly_monthly_equivalent = total_yearly / 12 if total_yearly > 0 else 0
    total_monthly_cost = total_monthly + yearly_monthly_equivalent
    
    # Calculate yearly cost (monthly * 12)
    total_yearly_cost = total_monthly_cost * 12
    
    context = {
        'subscriptions': subscriptions,
        'total_monthly_cost': total_monthly_cost,
        'total_yearly_cost': total_yearly_cost,
        'total_subscriptions': subscriptions.count(),
    }
    return render(request, 'dashboard.html', context)

def login_redirect(request):
    """Redirect to Django's built-in login view"""
    return redirect('login')

def logout_redirect(request):
    """Redirect to Django's built-in logout view"""
    return redirect('logout')