# backend/apps/analytics/urls.py - CREAR/CORREGIR ESTE ARCHIVO
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
    # URLs específicas para dashboard
    path('stats/', views.AnalyticsViewSet.as_view({'get': 'stats'}), name='analytics-stats'),
    path('activity/', views.AnalyticsViewSet.as_view({'get': 'activity'}), name='analytics-activity'),
]