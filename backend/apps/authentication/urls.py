# backend/apps/authentication/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

# Router para ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'register', views.UserRegistrationView, basename='register')

# URLs principales
urlpatterns = [
    # Router URLs (para /api/auth/users/, /api/auth/register/, etc.)
    path('', include(router.urls)),
    path('auth/users/profile/', views.UserViewSet.as_view({'get': 'profile'}), name='user-profile'),
    
    # Autenticación JWT
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Microsoft OAuth para API (estas son las URLs que usa React)
    path('microsoft/login/', views.microsoft_login_api, name='microsoft_login_api'),
    path('microsoft/callback/', views.microsoft_callback_api, name='microsoft_callback_api'),
]

# IMPORTANTE: Este archivo maneja las URLs bajo /api/auth/
# Las URLs tradicionales (templates) están en traditional_urls.py bajo /auth/