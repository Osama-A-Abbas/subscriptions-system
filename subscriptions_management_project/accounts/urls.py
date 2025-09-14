from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_redirect, name='login_redirect'),
    path('logout/', views.logout_redirect, name='logout_redirect'),
]
