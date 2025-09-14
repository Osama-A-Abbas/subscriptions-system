from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Subscription, Category
from .forms import SubscriptionForm

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
    return render(request, 'subscriptions/subscription_detail.html', {
        'subscription': subscription
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