from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import Subscription, Category
from .forms import SubscriptionForm, PaymentForm
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
    
    # Generate billing periods for the last 12 months
    billing_periods = []
    today = timezone.now().date()
    current_date = subscription.start_date
    
    for i in range(12):
        if subscription.billing_cycle == 'monthly':
            period_end = current_date + relativedelta(months=1)
        else:
            period_end = current_date + relativedelta(years=1)
        
        # Check if there's a payment for this period
        payment = subscription.payments.filter(
            billing_period_start=current_date,
            billing_period_end=period_end
        ).first()
        
        billing_periods.append({
            'start': current_date,
            'end': period_end,
            'payment': payment,
            'is_paid': payment.is_paid if payment else False,
            'is_current': current_date <= today < period_end,
            'is_past_due': period_end < today and not (payment and payment.is_paid)
        })
        
        current_date = period_end
    
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
def delete_subscription(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    if request.method == 'POST':
        subscription.delete()
        messages.success(request, 'Subscription deleted successfully!')
        return redirect('subscription_list')
    return render(request, 'subscriptions/delete_subscription.html', {
        'subscription': subscription
    })