from django.urls import path
from . import views

urlpatterns = [
    path('', views.subscription_list, name='subscription_list'),
    path('add/', views.add_subscription, name='add_subscription'),
    path('<int:pk>/', views.subscription_detail, name='subscription_detail'),
    path('<int:pk>/edit/', views.edit_subscription, name='edit_subscription'),
    path('<int:pk>/delete/', views.delete_subscription, name='delete_subscription'),
]