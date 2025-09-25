"""
Script para ejecutar tests de reportes especializados
Uso: python manage.py shell < scripts/run_specialized_tests.py
"""
import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

def run_specialized_tests():
    """Ejecutar todos los tests de reportes especializados"""
    
    print("🧪 Ejecutando Tests de Reportes Especializados...")
    print("=" * 60)
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    # Obtener test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    # Lista de tests a ejecutar
    test_modules = [
        'apps.reports.tests.test_specialized_analyzers',
        'apps.reports.tests.test_specialized_html_generators', 
        'apps.reports.tests.test_views_specialized',
        'apps.reports.tests.test_tasks_specialized'
    ]
    
    # Ejecutar tests
    failures = test_runner.run_tests(test_modules)
    
    if failures:
        print(f"\n❌ {failures} tests fallaron")
        sys.exit(1)
    else:
        print(f"\n✅ Todos los tests pasaron exitosamente!")
        print("\n🎉 Reportes especializados funcionando correctamente")

if __name__ == '__main__':
    run_specialized_tests()