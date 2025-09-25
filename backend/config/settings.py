# config/settings.py
import os, sys
from pathlib import Path
from datetime import timedelta
from decouple import config


# Configuración de encoding para Windows
if sys.platform.startswith('win'):
    # Configurar encoding UTF-8 para Windows
    os.environ['PYTHONIOENCODING'] = 'utf-8'


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Initialize environment variables

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('I!7LHBovbPAxPMhPYZAKkGBxUqBnD2z&9aR7T3gv5kJjbqbvZyx30%hWpdAfL744Dw49mp', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Crear directorio de logs automáticamente
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Permitir registro local (cambiar a False en producción si solo quieres Microsoft)
ALLOW_LOCAL_REGISTRATION = config('ALLOW_LOCAL_REGISTRATION', default=True, cast=bool)

# Configuración para redirecciones después del login
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'storages',
]

LOCAL_APPS = [
    'apps.core',
    'apps.authentication',
    'apps.reports',
    'apps.storage',
    'apps.analytics',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.ErrorHandlingMiddleware',  # Middleware personalizado para manejo de errores
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='azure_reports_dev'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres123'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': config('DB_SSLMODE', default='prefer'),
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Santo_Domingo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'authentication.User'

# REST Framework
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',  # ← AGREGAR
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    #'DEFAULT_THROTTLE_CLASSES': [
    #    'rest_framework.throttling.AnonRateThrottle',
    #    'rest_framework.throttling.UserRateThrottle'
    #],
    #'DEFAULT_THROTTLE_RATES': {
    #    'anon': '100/hour',
    #    'user': '1000/hour'
    #}
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = config('DEBUG', default=False, cast=bool)  # Solo en desarrollo

# Agregar estos headers adicionales:
CORS_ALLOW_HEADERS = [
   'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-microsoft-auth-token',
]
# Métodos HTTP permitidos
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
# CONFIGURACIÓN ADICIONAL PARA PRODUCCIÓN
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# Azure Blob Storage Settings
USE_AZURE_STORAGE = config('USE_AZURE_STORAGE', default=True, cast=bool)

if USE_AZURE_STORAGE:
    # Azure Storage configuration
    AZURE_STORAGE_ACCOUNT_NAME = config('AZURE_STORAGE_ACCOUNT_NAME', default='')
    AZURE_STORAGE_ACCOUNT_KEY = config('AZURE_STORAGE_ACCOUNT_KEY', default='')
    AZURE_STORAGE_CONTAINER_NAME = config('AZURE_STORAGE_CONTAINER_NAME', default='reports')
    
    # Verificar que las credenciales estén configuradas
    if not AZURE_STORAGE_ACCOUNT_NAME or not AZURE_STORAGE_ACCOUNT_KEY:
        print("⚠️ ADVERTENCIA: Credenciales de Azure Storage no configuradas")
        USE_AZURE_STORAGE = False
else:
    print("💾 Usando almacenamiento local (archivos en media/)")

# Variables de entorno para Microsoft OAuth
MICROSOFT_AUTH_CLIENT_ID = config('MICROSOFT_CLIENT_ID', default='')
MICROSOFT_AUTH_CLIENT_SECRET = config('MICROSOFT_CLIENT_SECRET', default='')
MICROSOFT_AUTH_TENANT_ID = config('MICROSOFT_TENANT_ID', default='common')
MICROSOFT_AUTH_REDIRECT_URI = config('MICROSOFT_REDIRECT_URI', default='http://localhost:8000/api/auth/microsoft/callback/')

# Scopes para Microsoft OAuth
MICROSOFT_AUTH_SCOPES = [
    'email',
    'User.Read'
]

# Configuración adicional para Microsoft OAuth
MICROSOFT_OAUTH = {
    'CLIENT_ID': MICROSOFT_AUTH_CLIENT_ID,
    'CLIENT_SECRET': MICROSOFT_AUTH_CLIENT_SECRET,
    'TENANT_ID': MICROSOFT_AUTH_TENANT_ID,
    'REDIRECT_URI': MICROSOFT_AUTH_REDIRECT_URI,
    'SCOPES': MICROSOFT_AUTH_SCOPES,
    'ENABLED': bool(MICROSOFT_AUTH_CLIENT_ID and MICROSOFT_AUTH_CLIENT_SECRET),
    'AUTHORITY': f'https://login.microsoftonline.com/{MICROSOFT_AUTH_TENANT_ID}',
    'GRAPH_ENDPOINT': 'https://graph.microsoft.com/v1.0/me'
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'microsoft_oauth_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'microsoft_oauth.log',
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },        
        'django_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'reports_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'reports.log',
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 3,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.authentication.services': {
            'handlers': ['microsoft_oauth_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'msal': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.reports': {
            'handlers': ['reports_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['django_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['django_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
       'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
if DEBUG:
    # En desarrollo, mostrar más logs en consola
    LOGGING['handlers']['console']['level'] = 'DEBUG'
    
    # Agregar logger para SQL queries (opcional)
    LOGGING['loggers']['django.db.backends'] = {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    }


# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Email settings (para notificaciones)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@azurereports.com')

# Report generation settings
MAX_CSV_ROWS = config('MAX_CSV_ROWS', default=100000, cast=int)
REPORT_TIMEOUT = config('REPORT_TIMEOUT', default=300, cast=int)  # 5 minutos
PDF_MAX_PAGES = config('PDF_MAX_PAGES', default=50, cast=int)

# Analytics
ENABLE_ANALYTICS = config('ENABLE_ANALYTICS', default=True, cast=bool)
ANALYTICS_RETENTION_DAYS = config('ANALYTICS_RETENTION_DAYS', default=90, cast=int)

# Configuraciones para reportes mejorados
REPORT_CACHE_TIMEOUT = 3600  # 1 hora
REPORT_MAX_CSV_SIZE = 10 * 1024 * 1024  # 10MB
REPORT_ALLOWED_FORMATS = ['csv', 'xlsx']

# Cache para reportes (si usas Redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
