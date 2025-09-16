"""
URL configuration for subscriptions_management_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def redirect_to_dashboard(request):
    """Redirect to dashboard if authenticated, otherwise to login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # All authentication views
    path('subscriptions/', include('subscriptions.urls')),  # subscription management
    path('', redirect_to_dashboard, name='home'),  # redirect to appropriate page
]