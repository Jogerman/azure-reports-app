# backend/scripts/setup_specialized_reports.py
"""
Script de configuración inicial para reportes especializados
Ejecutar con: python manage.py shell < scripts/setup_specialized_reports.py
"""

import os
import sys
import django
from django.core.management import call_command
from django.conf import settings

def setup_specialized_reports():
    """Configurar el sistema para reportes especializados"""
    
    print("🚀 Configurando Reportes Especializados de Azure...")
    print("=" * 60)
    
    # 1. Verificar estructura de directorios
    print("\n📁 Verificando estructura de directorios...")
    required_dirs = [
        'backend/apps/reports/utils',
        'backend/apps/reports/tests',
        'frontend/src/components/reports',
        'frontend/src/components/dashboard'
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"✅ Creado directorio: {dir_path}")
            except Exception as e:
                print(f"❌ Error creando {dir_path}: {e}")
        else:
            print(f"✅ Directorio existe: {dir_path}")
    
    # 2. Verificar archivos requeridos
    print("\n📄 Verificando archivos requeridos...")
    required_files = [
        'backend/apps/reports/utils/__init__.py',
        'backend/apps/reports/utils/specialized_analyzers.py',
        'backend/apps/reports/utils/specialized_html_generators.py',
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ Archivo existe: {file_path}")
        else:
            print(f"⚠️  Falta archivo: {file_path}")
            
            # Crear __init__.py si no existe
            if file_path.endswith('__init__.py'):
                try:
                    with open(file_path, 'w') as f:
                        f.write('# Auto-generated __init__.py\n')
                    print(f"✅ Creado archivo: {file_path}")
                except Exception as e:
                    print(f"❌ Error creando {file_path}: {e}")
    
    # 3. Verificar dependencias de Python
    print("\n📦 Verificando dependencias de Python...")
    required_packages = [
        'pandas',
        'numpy', 
        'celery',
        'django',
        'djangorestframework'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} instalado")
        except ImportError:
            print(f"❌ {package} NO instalado")
            print(f"   Instalar con: pip install {package}")
    
    # 4. Verificar configuración de base de datos
    print("\n🗄️  Verificando configuración de base de datos...")
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Conexión a base de datos OK")
    except Exception as e:
        print(f"❌ Error de base de datos: {e}")
    
    # 5. Ejecutar migraciones si es necesario
    print("\n⚡ Ejecutando migraciones...")
    try:
        call_command('migrate', '--noinput')
        print("✅ Migraciones completadas")
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
    
    # 6. Verificar configuración de Celery
    print("\n🔄 Verificando configuración de Celery...")
    try:
        from config.celery import app
        print("✅ Configuración de Celery OK")
        print(f"   Broker: {app.conf.broker_url}")
        print(f"   Backend: {app.conf.result_backend}")
    except Exception as e:
        print(f"❌ Error en configuración de Celery: {e}")
    
    # 7. Verificar permisos de archivos
    print("\n🔐 Verificando permisos...")
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if media_root and os.path.exists(media_root):
        if os.access(media_root, os.R_OK | os.W_OK):
            print(f"✅ Permisos OK para MEDIA_ROOT: {media_root}")
        else:
            print(f"❌ Permisos insuficientes para MEDIA_ROOT: {media_root}")
    
    print("\n🎉 Configuración completada!")
    print("\nPróximos pasos:")
    print("1. Copiar los archivos de analizadores especializados")
    print("2. Actualizar views.py y tasks.py con los nuevos métodos")
    print("3. Instalar componentes de frontend")
    print("4. Ejecutar tests: python manage.py test apps.reports.tests")
    print("5. Iniciar worker de Celery: celery -A config worker -l info")

if __name__ == '__main__':
    # Configurar Django si no está configurado
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
    
    setup_specialized_reports()