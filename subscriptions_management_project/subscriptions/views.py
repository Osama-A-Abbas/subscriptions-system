"""
Subscription views using Class-Based Views for better maintainability.

This module provides clean, consistent views with proper error handling,
logging, and separation of concerns.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
import logging

from .models import Subscription, Category, Payment
from .forms import SubscriptionForm, PaymentForm
from .services import mark_period_paid, mark_period_unpaid
from .selectors import get_user_subscriptions
from .mixins import UserOwnershipMixin, LoggingMixin, MessageMixin, TransactionMixin, ContextDataMixin

logger = logging.getLogger(__name__)


class SubscriptionListView(LoginRequiredMixin, LoggingMixin, MessageMixin, ContextDataMixin, ListView):
    """
    List view for user's subscriptions with enhanced functionality.
    
    Features:
    - Automatic user filtering
    - Eager loading for performance
    - Context data for template enhancements
    """
    model = Subscription
    template_name = 'subscriptions/subscription_list.html'
    context_object_name = 'subscriptions'
    paginate_by = 20
    
    def get_queryset(self):
        """Return user's subscriptions with optimized queries."""
        try:
            return get_user_subscriptions(self.request.user)
        except Exception as e:
            logger.error("Error fetching user subscriptions for user %s: %s", 
                        self.request.user.id, e)
            return Subscription.objects.none()
    
    def get_context_data(self, **kwargs):
        """Add additional context data for the template."""
        context = super().get_context_data(**kwargs)
        
        # Add summary statistics using the original queryset (not the paginated one)
        original_queryset = self.get_queryset()
        context['total_subscriptions'] = original_queryset.count()
        context['active_subscriptions'] = original_queryset.filter(is_active=True).count()
        context['renewing_soon'] = original_queryset.filter(
            renewal_date__lte=timezone.now().date() + timezone.timedelta(days=7)
        ).count()
        
        return context


class SubscriptionDetailView(LoginRequiredMixin, UserOwnershipMixin, LoggingMixin, MessageMixin, ContextDataMixin, DetailView):
    """
    Detail view for individual subscription with billing periods.
    
    Features:
    - User ownership validation
    - Billing periods generation
    - Payment status information
    """
    model = Subscription
    template_name = 'subscriptions/subscription_detail.html'
    context_object_name = 'subscription'
    
    def get_queryset(self):
        """Ensure user can only access their own subscriptions."""
        return Subscription.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Add billing periods and payment information to context."""
        context = super().get_context_data(**kwargs)
        subscription = context['subscription']
        
        try:
            # Get billing periods using the virtual payment system
            context['billing_periods'] = subscription.get_billing_periods()
            context['payments'] = subscription.payments.all()
            
            # Add payment status information
            context['payment_status'] = subscription.get_overall_payment_status()
            context['payment_progress'] = subscription.get_payment_progress_percentage()
            context['paid_count'] = subscription.get_paid_payments_count()
            context['total_payments'] = subscription.get_total_payments()
            
        except Exception as e:
            logger.error("Error generating billing periods for subscription %s: %s", 
                        subscription.id, e)
            context['billing_periods'] = []
            context['payments'] = []
            messages.error(self.request, 'Error loading billing information.')
        
        return context


class SubscriptionCreateView(LoginRequiredMixin, LoggingMixin, MessageMixin, ContextDataMixin, CreateView):
    """
    Create view for new subscriptions with enhanced validation.
    
    Features:
    - Automatic user assignment
    - Form validation with user feedback
    - Success message handling
    """
    model = Subscription
    form_class = SubscriptionForm
    template_name = 'subscriptions/add_subscription.html'
    success_url = reverse_lazy('subscription_list')
    
    def form_valid(self, form):
        """Handle successful form submission."""
        try:
            subscription = form.save(commit=False)
            subscription.user = self.request.user
            subscription.save()
            
            self.log_action('create', subscription.name)
            self.add_success_message(f'Subscription "{subscription.name}" added successfully!')
            
            return super().form_valid(form)
            
        except Exception as e:
            self.log_error(e)
            self.add_error_message('Error creating subscription. Please try again.')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        logger.warning("Subscription form validation failed for user %s: %s", 
                      self.request.user.id, form.errors)
        return super().form_invalid(form)


class SubscriptionUpdateView(LoginRequiredMixin, UserOwnershipMixin, LoggingMixin, MessageMixin, ContextDataMixin, UpdateView):
    """
    Update view for existing subscriptions with change tracking.
    
    Features:
    - User ownership validation
    - Change detection and logging
    - Success message handling
    """
    model = Subscription
    form_class = SubscriptionForm
    template_name = 'subscriptions/edit_subscription.html'
    
    def get_queryset(self):
        """Ensure user can only edit their own subscriptions."""
        return Subscription.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        """Redirect to subscription detail after successful update."""
        return reverse('subscription_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Handle successful form submission with change tracking."""
        try:
            # Track changes for logging
            original = Subscription.objects.get(pk=self.object.pk)
            changes = []
            
            for field in ['name', 'monthly_cost', 'yearly_cost', 'billing_cycle', 
                         'start_date', 'duration_months', 'duration_years']:
                old_value = getattr(original, field)
                new_value = form.cleaned_data.get(field)
                if old_value != new_value:
                    changes.append(f"{field}: {old_value} → {new_value}")
            
            subscription = form.save()
            
            if changes:
                logger.info("Subscription updated: %s by user %s. Changes: %s", 
                           subscription.name, self.request.user.id, '; '.join(changes))
            else:
                logger.info("Subscription form submitted without changes: %s by user %s", 
                           subscription.name, self.request.user.id)
            
            messages.success(self.request, f'Subscription "{subscription.name}" updated successfully!')
            return super().form_valid(form)
            
        except Exception as e:
            logger.error("Error updating subscription %s for user %s: %s", 
                        self.object.id, self.request.user.id, e)
            messages.error(self.request, 'Error updating subscription. Please try again.')
            return self.form_invalid(form)


class SubscriptionDeleteView(LoginRequiredMixin, UserOwnershipMixin, LoggingMixin, MessageMixin, ContextDataMixin, DeleteView):
    """
    Delete view for subscriptions with confirmation.
    
    Features:
    - User ownership validation
    - Confirmation handling
    - Success message with subscription name
    """
    model = Subscription
    template_name = 'subscriptions/delete_subscription.html'
    success_url = reverse_lazy('subscription_list')
    
    def get_queryset(self):
        """Ensure user can only delete their own subscriptions."""
        return Subscription.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """Handle deletion with logging and user feedback."""
        try:
            subscription = self.get_object()
            subscription_name = subscription.name
            
            logger.info("Subscription deleted: %s by user %s", 
                       subscription_name, request.user.id)
            
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f'Subscription "{subscription_name}" deleted successfully!')
            
            return response
            
        except Exception as e:
            logger.error("Error deleting subscription for user %s: %s", 
                        request.user.id, e)
            messages.error(request, 'Error deleting subscription. Please try again.')
            return redirect('subscription_list')


class PaymentActionView(LoginRequiredMixin, View):
    """
    Base view for payment actions (paid/unpaid) with confirmation.
    
    Features:
    - User ownership validation
    - Confirmation handling
    - Atomic transaction processing
    """
    template_name = 'subscriptions/mark_payment_paid.html'
    
    def get_subscription(self):
        """Get subscription with user ownership validation."""
        subscription = get_object_or_404(
            Subscription, 
            pk=self.kwargs['pk'], 
            user=self.request.user
        )
        return subscription
    
    def get_period_start(self):
        """Get the billing period start date from URL."""
        return self.kwargs['period_start']
    
    def get(self, request, *args, **kwargs):
        """Handle GET request - show confirmation page."""
        context = {
            'subscription': self.get_subscription(),
            'period_start': self.get_period_start(),
        }
        return render(request, self.template_name, context)


class MarkPaymentPaidView(PaymentActionView):
    """View for marking a payment period as paid."""
    
    def get(self, request, *args, **kwargs):
        """Handle GET request - show confirmation page."""
        context = {
            'subscription': self.get_subscription(),
            'period_start': self.get_period_start(),
            'action': 'paid',
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        """Handle payment marking with transaction safety."""
        try:
            subscription = self.get_subscription()
            period_start = self.get_period_start()
            
            with transaction.atomic():
                mark_period_paid(subscription, period_start)
            
            logger.info("Payment marked as paid: subscription %s, period %s by user %s", 
                       subscription.id, period_start, request.user.id)
            
            messages.success(request, f'Payment for period {period_start} marked as paid!')
            return redirect('subscription_detail', pk=subscription.pk)
            
        except Exception as e:
            logger.error("Error marking payment as paid for subscription %s, period %s: %s", 
                        subscription.id, period_start, e)
            messages.error(request, 'Error marking payment as paid. Please try again.')
            return redirect('subscription_detail', pk=subscription.pk)


class MarkPaymentUnpaidView(PaymentActionView):
    """View for marking a payment period as unpaid."""
    
    def get(self, request, *args, **kwargs):
        """Handle GET request - show confirmation page."""
        context = {
            'subscription': self.get_subscription(),
            'period_start': self.get_period_start(),
            'action': 'unpaid',
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        """Handle payment unmarking with transaction safety."""
        try:
            subscription = self.get_subscription()
            period_start = self.get_period_start()
            
            with transaction.atomic():
                mark_period_unpaid(subscription, period_start)
            
            logger.info("Payment marked as unpaid: subscription %s, period %s by user %s", 
                       subscription.id, period_start, request.user.id)
            
            messages.success(request, f'Payment for period {period_start} marked as unpaid!')
            return redirect('subscription_detail', pk=subscription.pk)
            
        except Exception as e:
            logger.error("Error marking payment as unpaid for subscription %s, period %s: %s", 
                        subscription.id, period_start, e)
            messages.error(request, 'Error marking payment as unpaid. Please try again.')
            return redirect('subscription_detail', pk=subscription.pk)


class AddPaymentView(LoginRequiredMixin, CreateView):
    """
    View for manually adding payment records.
    
    Features:
    - User ownership validation
    - Automatic subscription assignment
    - Form validation
    """
    model = Payment
    form_class = PaymentForm
    template_name = 'subscriptions/add_payment.html'
    
    def get_subscription(self):
        """Get subscription with user ownership validation."""
        return get_object_or_404(
            Subscription, 
            pk=self.kwargs['pk'], 
            user=self.request.user
        )
    
    def get_context_data(self, **kwargs):
        """Add subscription to context."""
        context = super().get_context_data(**kwargs)
        context['subscription'] = self.get_subscription()
        return context
    
    def get_success_url(self):
        """Redirect to subscription detail after successful payment creation."""
        return reverse('subscription_detail', kwargs={'pk': self.kwargs['pk']})
    
    def form_valid(self, form):
        """Handle successful form submission."""
        try:
            payment = form.save(commit=False)
            payment.subscription = self.get_subscription()
            payment.save()
            
            logger.info("Payment added: subscription %s, amount %s by user %s", 
                       payment.subscription.id, payment.amount, self.request.user.id)
            
            messages.success(self.request, 'Payment recorded successfully!')
            return super().form_valid(form)
            
        except Exception as e:
            logger.error("Error adding payment for subscription %s: %s", 
                        self.kwargs['pk'], e)
            messages.error(self.request, 'Error recording payment. Please try again.')
            return self.form_invalid(form)