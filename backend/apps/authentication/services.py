# backend/apps/authentication/services.py
import logging
import requests
import msal
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decouple import config
import uuid

logger = logging.getLogger(__name__)
User = get_user_model()

def is_microsoft_configured():
    """Función helper para verificar si Microsoft OAuth está configurado"""
    try:
        client_id = config('MICROSOFT_CLIENT_ID', default='')
        client_secret = config('MICROSOFT_CLIENT_SECRET', default='')
        
        return bool(client_id and client_secret and 
                   client_id != 'your-client-id' and 
                   client_secret != 'your-client-secret')
    except Exception:
        return False

class MicrosoftAuthService:
    """
    Servicio para autenticación con Microsoft OAuth usando MSAL
    """
    
    def __init__(self, request=None):
        self.request = request
        self.client_id = config('MICROSOFT_CLIENT_ID', default='')
        self.client_secret = config('MICROSOFT_CLIENT_SECRET', default='')
        self.tenant_id = config('MICROSOFT_TENANT_ID', default='common')
        self.redirect_uri = config('MICROSOFT_REDIRECT_URI', default='http://localhost:8000/api/auth/microsoft/callback/')
        
        # Scopes para obtener información del usuario
        # Nota: 'openid' y 'profile' son automáticos, no deben incluirse explícitamente
        self.scopes = [
            'User.Read',
            'email'
        ]
        
        # URLs de Microsoft
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.graph_endpoint = "https://graph.microsoft.com/v1.0/me"
    
    def is_configured(self):
        """Verificar si Microsoft OAuth está configurado correctamente"""
        try:
            required_settings = [
                self.client_id,
                self.client_secret,
            ]
            
            configured = all(setting and setting != 'your-client-id' for setting in required_settings)
            
            if not configured:
                logger.warning("Microsoft OAuth no está completamente configurado")
                return False
            
            # Verificar que MSAL esté disponible
            return True
            
        except Exception as e:
            logger.error(f"Error verificando configuración Microsoft OAuth: {e}")
            return False
    
    def get_auth_url(self, state=None):
        """Generar URL de autorización de Microsoft"""
        try:
            if not self.is_configured():
                raise ValidationError("Microsoft OAuth no está configurado")
            
            # Crear aplicación MSAL
            app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.authority
            )
            
            # Generar state si no se proporciona
            if not state:
                state = str(uuid.uuid4())
            
            # Construir URL de autorización
            auth_url = app.get_authorization_request_url(
                scopes=self.scopes,
                state=state,
                redirect_uri=self.redirect_uri
            )
            
            logger.info(f"URL de autorización generada para Microsoft OAuth")
            return auth_url
            
        except Exception as e:
            logger.error(f"Error generando URL de autorización: {e}")
            raise ValidationError(f"Error en Microsoft OAuth: {str(e)}")
    
    def get_authorization_url(self, state=None):
        """Alias para mantener compatibilidad"""
        return self.get_auth_url(state)
    
    def get_token_from_code(self, authorization_code, state=None):
        """Intercambiar código de autorización por tokens"""
        try:
            if not self.is_configured():
                raise ValidationError("Microsoft OAuth no está configurado")
            
            # Crear aplicación MSAL
            app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.authority
            )
            
            # Intercambiar código por token
            result = app.acquire_token_by_authorization_code(
                code=authorization_code,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            if 'error' in result:
                error_msg = result.get('error_description', result.get('error', 'Error desconocido'))
                logger.error(f"Error obteniendo token de Microsoft: {error_msg}")
                raise ValidationError(f"Error de autenticación: {error_msg}")
            
            logger.info("Token obtenido exitosamente de Microsoft")
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado obteniendo token: {e}")
            raise ValidationError(f"Error interno: {str(e)}")
    
    def get_user_info(self, access_token):
        """Obtener información del usuario desde Microsoft Graph"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(self.graph_endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Información de usuario obtenida: {user_data.get('userPrincipalName', 'unknown')}")
                
                # Log completo para debugging
                logger.debug(f"Datos completos del usuario: {user_data}")
                
                # Si no hay tid, intentar obtenerlo del dominio del email
                if 'tid' not in user_data or not user_data['tid']:
                    email = user_data.get('mail') or user_data.get('userPrincipalName', '')
                    if '@' in email:
                        domain = email.split('@')[1]
                        logger.info(f"No se encontró tid, usuario del dominio: {domain}")
                
                return user_data
            else:
                logger.error(f"Error obteniendo info del usuario: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error en petición a Microsoft Graph: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado obteniendo info del usuario: {e}")
            return None
    
    def validate_tenant(self, user_info):
        """Validar que el usuario pertenece al tenant correcto"""
        try:
            # Si el tenant es 'common', permitir cualquier usuario de Microsoft
            if self.tenant_id == 'common':
                logger.info(f"Tenant común configurado - permitiendo usuario de cualquier organización")
                return True
            
            # Verificar el tenant del usuario
            user_tenant = user_info.get('tid', '')
            
            # Si no hay tid en la respuesta, pero el usuario viene del tenant correcto
            # (porque estamos usando el tenant específico en la URL de autorización),
            # entonces aceptar el usuario
            if not user_tenant:
                logger.info(f"No se recibió tenant ID en la respuesta, pero usuario viene del tenant configurado: {self.tenant_id}")
                return True
            
            if user_tenant == self.tenant_id:
                logger.info(f"Usuario de tenant autorizado: {user_tenant}")
                return True
            
            # Si llegamos aquí, el tenant no coincide
            logger.warning(f"Usuario de tenant no autorizado. Esperado: {self.tenant_id}, Recibido: {user_tenant}")
            logger.info(f"Para permitir este usuario, cambia MICROSOFT_TENANT_ID a: {user_tenant}")
            return False
            
        except Exception as e:
            logger.error(f"Error validando tenant: {e}")
            return False
    
    def create_or_update_user(self, user_info):
        """Crear o actualizar usuario basado en información de Microsoft"""
        try:
            email = user_info.get('mail') or user_info.get('userPrincipalName', '')
            
            if not email:
                raise ValidationError("Email no disponible en la respuesta de Microsoft")
            
            # Buscar usuario existente
            user = None
            try:
                user = User.objects.get(email__iexact=email)
                logger.info(f"Usuario existente encontrado: {email}")
                
                # Actualizar información si es necesario
                updated = False
                
                if user_info.get('givenName') and user.first_name != user_info['givenName']:
                    user.first_name = user_info['givenName']
                    updated = True
                
                if user_info.get('surname') and user.last_name != user_info['surname']:
                    user.last_name = user_info['surname']
                    updated = True
                
                if updated:
                    user.save()
                    logger.info(f"Usuario actualizado: {email}")
                
            except User.DoesNotExist:
                # Crear nuevo usuario
                username = email.split('@')[0]  # Usar la parte antes del @ como username
                
                # Asegurar username único
                counter = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=user_info.get('givenName', ''),
                    last_name=user_info.get('surname', ''),
                    is_active=True
                )
                
                # Configurar último método de login si el campo existe
                if hasattr(user, 'last_login_provider'):
                    user.last_login_provider = 'microsoft'
                    user.save()
                
                logger.info(f"Nuevo usuario creado: {email}")
            
            return user
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error creando/actualizando usuario: {e}")
            raise ValidationError(f"Error procesando usuario: {str(e)}")
    
    def refresh_token(self, refresh_token):
        """Renovar token de acceso usando refresh token"""
        try:
            if not self.is_configured():
                raise ValidationError("Microsoft OAuth no está configurado")
            
            app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.authority
            )
            
            # Intentar renovar token
            result = app.acquire_token_by_refresh_token(
                refresh_token=refresh_token,
                scopes=self.scopes
            )
            
            if 'error' in result:
                error_msg = result.get('error_description', result.get('error', 'Error renovando token'))
                logger.error(f"Error renovando token: {error_msg}")
                raise ValidationError(f"Error renovando token: {error_msg}")
            
            logger.info("Token renovado exitosamente")
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado renovando token: {e}")
            raise ValidationError(f"Error interno renovando token: {str(e)}")