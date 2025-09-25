# scripts/test_migration.py
import os
import sys
import django

# Agregar el directorio padre al path para encontrar 'config'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def test_user_creation():
    """Probar creación de usuarios"""
    print("Probando creación de usuarios...")
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'username': 'testuser',
                'first_name': 'Usuario',
                'last_name': 'Prueba',
                'department': 'IT',
                'job_title': 'Desarrollador'
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            print("Usuario creado exitosamente")
        else:
            print("Usuario ya existe")
        
        return user
    except Exception as e:
        print(f"Error creando usuario: {e}")
        return None

def test_database_connection():
    """Probar conexión a la base de datos"""
    print("Probando conexión a base de datos...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print("Conexión a base de datos exitosa")
        return True
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return False

def test_models():
    """Probar que los modelos funcionan"""
    print("Probando modelos...")
    
    try:
        from apps.authentication.models import User
        print(f"Modelo User encontrado: {User}")
        
        # Contar usuarios
        user_count = User.objects.count()
        print(f"Usuarios en BD: {user_count}")
        
        return True
    except Exception as e:
        print(f"Error con modelos: {e}")
        return False

if __name__ == '__main__':
    print("Iniciando pruebas de migración...")
    
    try:
        # Configurar Django
        django.setup()
        print("Django configurado correctamente")
        
        # Ejecutar pruebas
        db_ok = test_database_connection()
        models_ok = test_models()
        user = test_user_creation()
        
        if db_ok and models_ok and user:
            print("\nTodas las pruebas pasaron exitosamente!")
            print(f"Usuario de prueba: {user.email}")
        else:
            print("\nAlgunas pruebas fallaron")
            
    except Exception as e:
        print(f"Error en configuración Django: {e}")
        import traceback
        traceback.print_exc()