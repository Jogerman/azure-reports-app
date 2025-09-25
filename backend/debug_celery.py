# backend/debug_celery.py - Script para diagnosticar problemas de Celery

import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_celery_connection():
    """Probar conexión a Celery y Redis"""
    print("=== DIAGNÓSTICO DE CELERY ===\n")
    
    # 1. Verificar configuración de Celery
    print("1. Configuración de Celery:")
    print(f"   CELERY_BROKER_URL: {getattr(settings, 'CELERY_BROKER_URL', 'NO CONFIGURADO')}")
    print(f"   CELERY_RESULT_BACKEND: {getattr(settings, 'CELERY_RESULT_BACKEND', 'NO CONFIGURADO')}")
    
    # 2. Importar aplicación de Celery
    try:
        from config.celery import app
        print(f"   ✓ Aplicación Celery importada: {app}")
    except Exception as e:
        print(f"   ✗ Error importando aplicación Celery: {e}")
        return False
    
    # 3. Verificar conexión a Redis
    try:
        import redis
        r = redis.Redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        print("   ✓ Conexión a Redis exitosa")
    except Exception as e:
        print(f"   ✗ Error conectando a Redis: {e}")
        return False
    
    # 4. Listar tareas registradas
    print("\n2. Tareas registradas en Celery:")
    try:
        registered_tasks = list(app.tasks.keys())
        for task in registered_tasks:
            print(f"   - {task}")
        
        if not registered_tasks:
            print("   ✗ No hay tareas registradas")
            return False
        
    except Exception as e:
        print(f"   ✗ Error listando tareas: {e}")
        return False
    
    # 5. Probar importación de tareas específicas
    print("\n3. Verificando tareas de reportes:")
    try:
        from apps.reports.tasks import generate_specialized_report
        print(f"   ✓ generate_specialized_report importada: {generate_specialized_report}")
        print(f"   ✓ Tiene atributo 'delay': {hasattr(generate_specialized_report, 'delay')}")
        
        # Verificar si es una tarea de Celery
        from celery import Task
        if hasattr(generate_specialized_report, '_decorated'):
            print("   ✓ Función correctamente decorada con @shared_task")
        else:
            print("   ✗ Función NO está decorada correctamente")
            
    except Exception as e:
        print(f"   ✗ Error importando tareas de reportes: {e}")
        return False
    
    # 6. Probar una tarea simple
    print("\n4. Probando tarea de debug:")
    try:
        from config.celery import debug_task
        result = debug_task.delay()
        print(f"   ✓ Tarea debug enviada: {result.id}")
        return True
    except Exception as e:
        print(f"   ✗ Error enviando tarea debug: {e}")
        return False

if __name__ == "__main__":
    if test_celery_connection():
        print("\n✅ Celery está funcionando correctamente")
    else:
        print("\n❌ Hay problemas con la configuración de Celery")
        print("\nSoluciones sugeridas:")
        print("1. Verificar que Redis esté ejecutándose: redis-cli ping")
        print("2. Reiniciar Celery worker con: celery -A config worker --pool=eventlet --concurrency=10 --loglevel=info")
        print("3. Verificar variables de entorno en .env")