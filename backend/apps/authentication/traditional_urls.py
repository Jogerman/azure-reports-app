# backend/apps/authentication/traditional_urls.py

from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('microsoft/login/', views.microsoft_login, name='microsoft_login'),
    path('microsoft/callback/', views.microsoft_callback, name='microsoft_callback'),
    path('test-config/', views.test_microsoft_config, name='test_microsoft_config'),
]