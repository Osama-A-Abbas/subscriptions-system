"""
URL patterns for subscription views using Class-Based Views.

This module provides clean, consistent URL patterns that work with
the refactored Class-Based Views for better maintainability.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Subscription CRUD operations
    path('', views.SubscriptionListView.as_view(), name='subscription_list'),
    path('add/', views.SubscriptionCreateView.as_view(), name='add_subscription'),
    path('<int:pk>/', views.SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('<int:pk>/edit/', views.SubscriptionUpdateView.as_view(), name='edit_subscription'),
    path('<int:pk>/delete/', views.SubscriptionDeleteView.as_view(), name='delete_subscription'),
    
    # Payment operations
    path('<int:pk>/payment/', views.AddPaymentView.as_view(), name='add_payment'),
    path('<int:pk>/mark-paid/<str:period_start>/', views.MarkPaymentPaidView.as_view(), name='mark_payment_paid'),
    path('<int:pk>/mark-unpaid/<str:period_start>/', views.MarkPaymentUnpaidView.as_view(), name='mark_payment_unpaid'),
]