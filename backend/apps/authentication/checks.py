# backend/apps/authentication/checks.py
from django.core.checks import Error, Warning, register
from decouple import config

@register()
def check_microsoft_oauth_config(app_configs, **kwargs):
    """Verificar configuración de Microsoft OAuth"""
    errors = []
    
    client_id = config('MICROSOFT_CLIENT_ID', default='')
    client_secret = config('MICROSOFT_CLIENT_SECRET', default='')
    
    if not client_id or client_id == 'your-microsoft-app-client-id':
        errors.append(
            Warning(
                'Microsoft OAuth Client ID no está configurado',
                hint='Configurar MICROSOFT_CLIENT_ID en .env',
                id='auth.W001',
            )
        )
    
    if not client_secret or client_secret == 'your-microsoft-app-client-secret':
        errors.append(
            Warning(
                'Microsoft OAuth Client Secret no está configurado', 
                hint='Configurar MICROSOFT_CLIENT_SECRET en .env',
                id='auth.W002',
            )
        )
    
    try:
        import msal
    except ImportError:
        errors.append(
            Error(
                'MSAL library no está instalada',
                hint='Ejecutar: pip install msal>=1.24.1.0',
                id='auth.E001',
            )
        )
    
    return errors