# config/celery.py - VERSIÓN CORREGIDA
import os
from celery import Celery
from django.conf import settings

# Establecer el módulo de configuración de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Crear aplicación de Celery
app = Celery('azure_reports_platform')

# Cargar configuración desde Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# ✅ CONFIGURACIÓN EXPLÍCITA PARA ASEGURAR AUTODISCOVERY
app.conf.update(
    # Broker settings
    broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Worker settings
    worker_pool='eventlet',  # Para Windows
    worker_concurrency=10,
    
    # Autodiscovery settings
    include=[
        'apps.reports.tasks',
        'apps.storage.tasks',
    ],
    
    # Task routing
    task_routes={
        'apps.reports.tasks.*': {'queue': 'reports'},
        'apps.storage.tasks.*': {'queue': 'storage'},
    },
)

# ✅ AUTODISCOVERY EXPLÍCITO
app.autodiscover_tasks([
    'apps.reports',
    'apps.storage',
    'apps.authentication',
    'apps.analytics',
])

# ✅ TAREA DE DEBUG MEJORADA
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    return f'Debug task executed successfully: {self.request.id}'

# ✅ CONFIGURACIÓN ADICIONAL PARA WINDOWS
import sys
if sys.platform.startswith('win'):
    # Configuraciones específicas para Windows
    app.conf.update(
        worker_hijack_root_logger=False,
        worker_log_color=False,
        broker_connection_retry_on_startup=True,
        broker_connection_max_retries=10,
    )