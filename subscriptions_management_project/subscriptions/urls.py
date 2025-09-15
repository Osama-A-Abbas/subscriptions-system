from django.urls import path
from . import views

urlpatterns = [
    path('', views.subscription_list, name='subscription_list'),
    path('add/', views.add_subscription, name='add_subscription'),
    path('<int:pk>/', views.subscription_detail, name='subscription_detail'),
    path('<int:pk>/edit/', views.edit_subscription, name='edit_subscription'),
    path('<int:pk>/delete/', views.delete_subscription, name='delete_subscription'),
    path('<int:pk>/payment/', views.add_payment, name='add_payment'),
    path('<int:pk>/mark-paid/<str:period_start>/', views.mark_payment_paid, name='mark_payment_paid'),
    path('<int:pk>/mark-unpaid/<str:period_start>/', views.mark_payment_unpaid, name='mark_payment_unpaid'),
]