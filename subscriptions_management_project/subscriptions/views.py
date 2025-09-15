from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import Subscription, Category
from .forms import SubscriptionForm, PaymentForm
from .services import mark_period_paid, mark_period_unpaid
@login_required
def subscription_list(request):
    subscriptions = Subscription.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'subscriptions/subscription_list.html', {
        'subscriptions': subscriptions
    })

@login_required
def add_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()
            messages.success(request, 'Subscription added successfully!')
            return redirect('subscription_list')
    else:
        form = SubscriptionForm()
    return render(request, 'subscriptions/add_subscription.html', {'form': form})

@login_required
def subscription_detail(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    payments = subscription.payments.all()
    
    # Get billing periods using the new virtual payment system
    billing_periods = subscription.get_billing_periods()
    
    context = {
        'subscription': subscription,
        'payments': payments,
        'billing_periods': billing_periods
    }
    return render(request, 'subscriptions/subscription_detail.html', context)

def add_payment(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.subscription = subscription
            payment.save()
            messages.success(request, 'Payment recorded successfully!')
            return redirect('subscription_detail', pk=pk)
    else:
        form = PaymentForm()
    
    return render(request, 'subscriptions/add_payment.html', {
        'form': form, 'subscription': subscription
    })

@login_required
def edit_subscription(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=subscription)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subscription updated successfully!')
            return redirect('subscription_detail', pk=pk)
    else:
        form = SubscriptionForm(instance=subscription)
    return render(request, 'subscriptions/edit_subscription.html', {
        'form': form, 'subscription': subscription
    })

@login_required
def mark_payment_paid(request, pk, period_start):
    """Mark a specific billing period as paid"""
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Mark the payment as paid via service layer
        mark_period_paid(subscription, period_start)
        messages.success(request, f'Payment for period {period_start} marked as paid!')
        return redirect('subscription_detail', pk=pk)
    else:
        # Show confirmation page
        return render(request, 'subscriptions/mark_payment_paid.html', {
            'subscription': subscription,
            'period_start': period_start,
            'action': 'paid',
        })

@login_required
def mark_payment_unpaid(request, pk, period_start):
    """Mark a specific billing period as unpaid"""
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    if request.method == 'POST':
        # Mark the payment as unpaid via service layer
        mark_period_unpaid(subscription, period_start)
        messages.success(request, f'Payment for period {period_start} marked as unpaid!')
        return redirect('subscription_detail', pk=pk)
    else:
        return render(request, 'subscriptions/mark_payment_paid.html', {
            'subscription': subscription,
            'period_start': period_start,
            'action': 'unpaid',
        })

@login_required
def delete_subscription(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    if request.method == 'POST':
        subscription_name = subscription.name
        subscription.delete()
        messages.success(request, f'Subscription "{subscription_name}" deleted successfully!')
        return redirect('subscription_list')
    else:
        # This shouldn't happen with the modal, but just in case
        return redirect('subscription_list')