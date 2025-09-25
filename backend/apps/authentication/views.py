# backend/apps/authentication/views.py
import logging
from django.contrib.auth import login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from .models import User
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer, 
    CustomTokenObtainPairSerializer
)
from .forms import CustomAuthenticationForm, CustomUserCreationForm

logger = logging.getLogger(__name__)

# ================================================================
# API VIEWS
# ================================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Vista para gestión de usuarios"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        """Endpoint específico para obtener el perfil del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        """Override del list para retornar solo el usuario actual"""
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class LogoutView(APIView):
    """Vista para logout (blacklist del token)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Sesión cerrada exitosamente"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Error cerrando sesión"}, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationView(viewsets.GenericViewSet):
    """Vista para registro de usuarios"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request):
        """Registrar nuevo usuario"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

# ================================================================
# API VIEWS para Microsoft OAuth
# ================================================================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def microsoft_login_api(request):
    """API endpoint para iniciar autenticación con Microsoft"""
    try:
        from .services import MicrosoftAuthService
        
        ms_auth_service = MicrosoftAuthService(request)
        
        if not ms_auth_service.is_configured():
            logger.error("Microsoft OAuth no está configurado correctamente")
            return Response({
                'error': 'Microsoft OAuth no está configurado correctamente.',
                'details': 'Verificar variables MICROSOFT_CLIENT_ID y MICROSOFT_CLIENT_SECRET en .env'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        auth_url = ms_auth_service.get_auth_url()
        
        if auth_url:
            logger.info("Generando URL de autenticación Microsoft para API")
            # Redirigir directamente a Microsoft
            return redirect(auth_url)
        else:
            logger.error("Error al generar la URL de autenticación con Microsoft")
            return Response({
                'error': 'Error al generar la URL de autenticación con Microsoft.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except ImportError as e:
        logger.error(f"MSAL no está disponible: {e}")
        return Response({
            'error': 'Microsoft OAuth no está disponible. Instala la librería msal.',
            'details': 'pip install msal>=1.24.1'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error en Microsoft login API: {e}")
        return Response({
            'error': 'Servicio de Microsoft no disponible temporalmente.',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def microsoft_callback_api(request):
    """API endpoint para manejar callback de Microsoft"""
    auth_code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    error_description = request.GET.get('error_description', '')
    
    # Manejar errores de OAuth
    if error:
        logger.warning(f"Error en callback de Microsoft: {error} - {error_description}")
        if error == 'access_denied':
            return redirect('http://localhost:5173/?error=access_denied')
        else:
            return redirect(f'http://localhost:5173/?error={error}')
    
    if not auth_code:
        logger.error("Código de autorización faltante en callback")
        return redirect('http://localhost:5173/?error=missing_code')
    
    try:
        from .services import MicrosoftAuthService
        
        ms_auth_service = MicrosoftAuthService(request)
        
        if not ms_auth_service.is_configured():
            logger.error("Microsoft OAuth no está configurado en callback")
            return redirect('http://localhost:5173/?error=not_configured')
        
        # Obtener token
        logger.info(f"Procesando callback con código de autorización")
        token_response = ms_auth_service.get_token_from_code(auth_code, state)
        
        if not token_response or 'access_token' not in token_response:
            error_msg = token_response.get('error_description', 'Token inválido') if token_response else 'Token inválido'
            logger.error(f"Error obteniendo token: {error_msg}")
            return redirect(f'http://localhost:5173/?error=token_error&description={error_msg}')
        
        # Obtener información del usuario
        user_info = ms_auth_service.get_user_info(token_response['access_token'])
        
        if not user_info:
            logger.error("Error obteniendo información del usuario")
            return redirect('http://localhost:5173/?error=user_info_error')
        
        # Validar tenant si está configurado
        if not ms_auth_service.validate_tenant(user_info):
            logger.warning("Usuario de tenant no autorizado")
            return redirect('http://localhost:5173/?error=invalid_tenant')
        
        # Crear o actualizar usuario
        user = ms_auth_service.create_or_update_user(user_info)
        
        if user:
            # Generar tokens JWT para el frontend
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Actualizar último método de login
            if hasattr(user, 'update_last_login_provider'):
                user.update_last_login_provider('microsoft')
            elif hasattr(user, 'last_login_provider'):
                user.last_login_provider = 'microsoft'
                user.save(update_fields=['last_login_provider'])
            
            # Redirigir al frontend con los tokens
            redirect_url = f'http://localhost:5173/auth/callback?access_token={access_token}&refresh_token={refresh_token}&user_id={user.id}'
            logger.info(f"Login exitoso para usuario: {user.email}")
            return redirect(redirect_url)
        else:
            logger.error("Error creando o actualizando usuario")
            return redirect('http://localhost:5173/?error=user_creation_error')
            
    except ImportError:
        logger.error("MSAL no está disponible en callback")
        return redirect('http://localhost:5173/?error=msal_not_available')
    except Exception as e:
        logger.error(f"Error inesperado en callback de Microsoft: {e}")
        return redirect('http://localhost:5173/?error=server_error')

# ================================================================
# TRADITIONAL DJANGO VIEWS (para templates)
# ================================================================

@never_cache
@csrf_protect
def login_view(request):
    """Vista de login unificada con soporte para Microsoft OAuth y login local"""
    if request.user.is_authenticated:
        messages.info(request, 'Ya tienes una sesión activa.')
        return redirect('dashboard:index')
    
    # Verificar si Microsoft OAuth está configurado
    microsoft_available = False
    microsoft_auth_url = None
    
    try:
        # Verificar configuración básica de Microsoft
        from .services import MicrosoftAuthService, is_microsoft_configured
        
        if is_microsoft_configured():
            ms_auth_service = MicrosoftAuthService(request)
            
            if ms_auth_service.is_configured():
                microsoft_auth_url = ms_auth_service.get_auth_url()
                microsoft_available = bool(microsoft_auth_url)
                
    except ImportError:
        logger.warning("Servicio Microsoft no disponible - msal no instalado")
        microsoft_available = False
    except Exception as e:
        logger.warning(f"Microsoft OAuth no disponible: {e}")
        microsoft_available = False
    
    # Manejar login local
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Verificar si el usuario puede hacer login local
            if hasattr(user, 'auth_provider') and user.auth_provider == 'microsoft':
                messages.warning(
                    request, 
                    'Esta cuenta está vinculada a Microsoft. '
                    'Usa el botón "Iniciar con Microsoft" para acceder.'
                )
                form = CustomAuthenticationForm()  # Limpiar formulario
            else:
                # Login exitoso
                login(request, user)
                
                # Actualizar último método de login si está disponible
                if hasattr(user, 'update_last_login_provider'):
                    user.update_last_login_provider('local')
                elif hasattr(user, 'last_login_provider'):
                    user.last_login_provider = 'local'
                    user.save(update_fields=['last_login_provider'])
                
                messages.success(
                    request, 
                    f'¡Bienvenido, {user.get_full_name() if hasattr(user, "get_full_name") else user.username}!'
                )
                
                # Redireccionar según parámetro next o dashboard
                next_url = request.GET.get('next', 'dashboard:index')
                return redirect(next_url)
        else:
            messages.error(request, 'Credenciales incorrectas. Inténtalo de nuevo.')
    else:
        form = CustomAuthenticationForm()
    
    context = {
        'form': form,
        'microsoft_auth_url': microsoft_auth_url,
        'microsoft_available': microsoft_available,
        'show_microsoft_login': microsoft_available,
        'show_local_registration': getattr(settings, 'ALLOW_LOCAL_REGISTRATION', True),
    }
    
    return render(request, 'authentication/login.html', context)

def microsoft_login(request):
    """Inicia el proceso de autenticación con Microsoft"""
    try:
        from .services import MicrosoftAuthService
        
        ms_auth_service = MicrosoftAuthService(request)
        
        if not ms_auth_service.is_configured():
            messages.error(request, 'Microsoft OAuth no está configurado correctamente.')
            return redirect('auth:login')
        
        auth_url = ms_auth_service.get_auth_url()
        
        if auth_url:
            logger.info("Redirigiendo a Microsoft para autenticación")
            return redirect(auth_url)
        else:
            messages.error(request, 'Error al generar la URL de autenticación con Microsoft.')
            return redirect('auth:login')
            
    except ImportError:
        messages.error(request, 'Microsoft OAuth no está disponible. Instala la librería msal.')
        return redirect('auth:login')
    except Exception as e:
        logger.error(f"Error en Microsoft login: {e}")
        messages.error(request, 'Servicio de Microsoft no disponible temporalmente.')
        return redirect('auth:login')

def microsoft_callback(request):
    """Callback para Microsoft OAuth - NO USAR PARA REACT, usar microsoft_callback_api"""
    auth_code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    error_description = request.GET.get('error_description', '')
    
    # Manejar errores de OAuth
    if error:
        if error == 'access_denied':
            return redirect('http://localhost:5173/?error=access_denied')
        else:
            return redirect(f'http://localhost:5173/?error={error}')
    
    if not auth_code:
        return redirect('http://localhost:5173/?error=missing_code')
    
    try:
        from .services import MicrosoftAuthService
        
        ms_auth_service = MicrosoftAuthService(request)
        
        if not ms_auth_service.is_configured():
            return redirect('http://localhost:5173/?error=not_configured')
        
        # Obtener token
        logger.info(f"Procesando callback con código de autorización")
        token_response = ms_auth_service.get_token_from_code(auth_code, state)
        
        if not token_response or 'access_token' not in token_response:
            error_msg = token_response.get('error_description', 'Token inválido') if token_response else 'Token inválido'
            logger.error(f"Error obteniendo token: {error_msg}")
            return redirect(f'http://localhost:5173/?error=token_error&description={error_msg}')
        
        # Obtener información del usuario
        user_info = ms_auth_service.get_user_info(token_response['access_token'])
        
        if not user_info:
            logger.error("Error obteniendo información del usuario")
            return redirect('http://localhost:5173/?error=user_info_error')
        
        # Validar tenant si está configurado
        if not ms_auth_service.validate_tenant(user_info):
            logger.warning("Usuario de tenant no autorizado")
            return redirect('http://localhost:5173/?error=invalid_tenant')
        
        # Crear o actualizar usuario
        user = ms_auth_service.create_or_update_user(user_info)
        
        if user:
            # Generar tokens JWT para el frontend
            from rest_framework_simplejwt.tokens import RefreshToken
            
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Actualizar último método de login
            if hasattr(user, 'update_last_login_provider'):
                user.update_last_login_provider('microsoft')
            elif hasattr(user, 'last_login_provider'):
                user.last_login_provider = 'microsoft'
                user.save(update_fields=['last_login_provider'])
            
            # Redirigir al frontend con los tokens
            redirect_url = f'http://localhost:5173/auth/callback?access_token={access_token}&refresh_token={refresh_token}&user_id={user.id}'
            logger.info(f"Login exitoso para usuario: {user.email}")
            return redirect(redirect_url)
        else:
            logger.error("Error creando o actualizando usuario")
            return redirect('http://localhost:5173/?error=user_creation_error')
            
    except ImportError:
        logger.error("MSAL no está disponible en callback")
        return redirect('http://localhost:5173/?error=msal_not_available')
    except Exception as e:
        logger.error(f"Error inesperado en callback de Microsoft: {e}")
        return redirect('http://localhost:5173/?error=server_error')

@never_cache
def register_view(request):
    """Vista de registro para usuarios locales"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    # Verificar si el registro local está permitido
    if not getattr(settings, 'ALLOW_LOCAL_REGISTRATION', True):
        messages.error(request, 'El registro de usuarios locales está deshabilitado.')
        return redirect('auth:login')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Cuenta creada exitosamente. ¡Bienvenido!')
            login(request, user)
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'authentication/register.html', {'form': form})

@login_required
def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('auth:login')

def test_microsoft_config(request):
    """Vista para probar configuración de Microsoft (solo para desarrollo)"""
    if not getattr(settings, 'DEBUG', False):
        from django.http import Http404
        raise Http404("Esta vista solo está disponible en modo DEBUG")
    
    try:
        from .services import MicrosoftAuthService, is_microsoft_configured
        
        config_status = {
            'configured': is_microsoft_configured(),
            'client_id': bool(getattr(settings, 'MICROSOFT_AUTH_CLIENT_ID', '')),
            'client_secret': bool(getattr(settings, 'MICROSOFT_AUTH_CLIENT_SECRET', '')),
            'tenant_id': bool(getattr(settings, 'MICROSOFT_AUTH_TENANT_ID', '')),
            'redirect_uri': getattr(settings, 'MICROSOFT_AUTH_REDIRECT_URI', ''),
            'scopes': getattr(settings, 'MICROSOFT_AUTH_SCOPES', []),
        }
        
        if config_status['configured']:
            try:
                ms_service = MicrosoftAuthService(request)
                auth_url = ms_service.get_auth_url()
                config_status['auth_url_generated'] = bool(auth_url)
                if auth_url:
                    config_status['sample_auth_url'] = auth_url[:100] + "..." if len(auth_url) > 100 else auth_url
            except Exception as e:
                config_status['auth_url_error'] = str(e)
        
        # Template simple para mostrar estado
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Microsoft OAuth Configuration Test</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .success {{ background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
                .error {{ background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }}
            </style>
        </head>
        <body>
            <h1>Microsoft OAuth Configuration Test</h1>
            <div class="status {'success' if config_status['configured'] else 'error'}">
                Configuration Status: {'✅ CONFIGURED' if config_status['configured'] else '❌ NOT CONFIGURED'}
            </div>
            <ul>
                <li>Client ID: {'✅' if config_status['client_id'] else '❌'}</li>
                <li>Client Secret: {'✅' if config_status['client_secret'] else '❌'}</li>
                <li>Tenant ID: {'✅' if config_status['tenant_id'] else '❌'}</li>
                <li>Redirect URI: {config_status['redirect_uri']}</li>
                <li>Auth URL Generated: {'✅' if config_status.get('auth_url_generated', False) else '❌'}</li>
            </ul>
            
            {f'<p><strong>Sample Auth URL:</strong> {config_status["sample_auth_url"]}</p>' if config_status.get('sample_auth_url') else ''}
            {f'<p><strong>Error:</strong> {config_status["auth_url_error"]}</p>' if config_status.get('auth_url_error') else ''}
            
            <h2>Environment Variables</h2>
            <pre>
MICROSOFT_CLIENT_ID = {'SET' if config_status['client_id'] else 'NOT SET'}
MICROSOFT_CLIENT_SECRET = {'SET' if config_status['client_secret'] else 'NOT SET'}
MICROSOFT_TENANT_ID = {'SET' if config_status['tenant_id'] else 'NOT SET'}
MICROSOFT_REDIRECT_URI = {config_status['redirect_uri']}
            </pre>
            
            <h2>Next Steps</h2>
            {'<p>✅ Microsoft OAuth is properly configured! You can now test the login.</p>' if config_status['configured'] else '<p>❌ Please configure the missing environment variables in your .env file.</p>'}
        </body>
        </html>
        """
        
        from django.http import HttpResponse
        return HttpResponse(html_content)
        
    except ImportError as e:
        return JsonResponse({
            'error': 'MSAL library not available',
            'details': 'Install with: pip install msal>=1.24.1',
            'exception': str(e)
        })
    except Exception as e:
        return JsonResponse({
            'error': 'Unexpected error',
            'details': str(e)
        })