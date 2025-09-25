# backend/scripts/test_specialized_functionality.py
"""
Script de prueba integral para verificar funcionalidad de reportes especializados
Ejecutar con: python manage.py shell < scripts/test_specialized_functionality.py
"""

import os
import django
import pandas as pd
import tempfile
import uuid
from django.contrib.auth import get_user_model

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.reports.models import Report, CSVFile
from apps.reports.utils.specialized_analyzers import SecurityAnalyzer, PerformanceAnalyzer, CostAnalyzer
from apps.reports.utils.specialized_html_generators import SecurityHTMLGenerator, PerformanceHTMLGenerator, CostHTMLGenerator

User = get_user_model()

def test_specialized_functionality():
    """Probar funcionalidad completa de reportes especializados"""
    
    print("🧪 Probando Funcionalidad de Reportes Especializados...")
    print("=" * 60)
    
    # 1. Crear datos de prueba
    test_data = create_test_data()
    
    # 2. Probar analizadores
    test_analyzers(test_data)
    
    # 3. Probar generadores HTML
    test_html_generators(test_data)
    
    # 4. Probar integración completa
    test_full_integration()
    
    print("\n🎉 Todas las pruebas completadas!")

def create_test_data():
    """Crear datos de prueba realistas"""
    print("\n📊 Creando datos de prueba...")
    
    test_data = pd.DataFrame([
        # Datos de seguridad
        {
            'Category': 'Security',
            'Business Impact': 'High', 
            'Recommendation': 'Virtual machines should have encryption at host enabled',
            'Resource Type': 'Virtual machine'
        },
        {
            'Category': 'Security',
            'Business Impact': 'Medium',
            'Recommendation': 'TLS should be updated to the latest version for web apps',
            'Resource Type': 'App service'
        },
        {
            'Category': 'Security',
            'Business Impact': 'High',
            'Recommendation': 'Machines should be configured to periodically check for missing system updates',
            'Resource Type': 'Virtual machine'
        },
        # Datos de rendimiento
        {
            'Category': 'Performance',
            'Business Impact': 'High',
            'Recommendation': 'Right-size or shutdown underutilized virtual machines',
            'Resource Type': 'Virtual machine'
        },
        {
            'Category': 'Performance',
            'Business Impact': 'Medium',
            'Recommendation': 'Enable autoscale to ensure optimal performance',
            'Resource Type': 'App service'
        },
        # Datos de costos
        {
            'Category': 'Cost',
            'Business Impact': 'High',
            'Recommendation': 'Consider virtual machine reserved instance to save over your on-demand costs',
            'Resource Type': 'Subscription'
        },
        {
            'Category': 'Cost',
            'Business Impact': 'Medium',
            'Recommendation': 'Consider Database for PostgreSQL reserved instance to save over your pay-as-you-go costs',
            'Resource Type': 'Subscription'
        }
    ])
    
    print(f"✅ Creados {len(test_data)} registros de prueba")
    return test_data

def test_analyzers(test_data):
    """Probar todos los analizadores especializados"""
    print("\n🔍 Probando analizadores especializados...")
    
    # Probar SecurityAnalyzer
    print("  🔐 Probando SecurityAnalyzer...")
    security_analyzer = SecurityAnalyzer(test_data)
    security_analysis = security_analyzer.analyze()
    
    assert 'basic_metrics' in security_analysis
    assert 'compliance_gaps' in security_analysis
    assert 'security_score' in security_analysis
    assert security_analysis['basic_metrics']['total_security_actions'] == 3
    print("    ✅ SecurityAnalyzer funciona correctamente")
    
    # Probar PerformanceAnalyzer
    print("  ⚡ Probando PerformanceAnalyzer...")
    performance_analyzer = PerformanceAnalyzer(test_data)
    performance_analysis = performance_analyzer.analyze()
    
    assert 'basic_metrics' in performance_analysis
    assert 'optimization_opportunities' in performance_analysis
    assert 'performance_score' in performance_analysis
    assert performance_analysis['basic_metrics']['total_performance_actions'] == 2
    print("    ✅ PerformanceAnalyzer funciona correctamente")
    
    # Probar CostAnalyzer
    print("  💰 Probando CostAnalyzer...")
    cost_analyzer = CostAnalyzer(test_data)
    cost_analysis = cost_analyzer.analyze()
    
    assert 'basic_metrics' in cost_analysis
    assert 'savings_analysis' in cost_analysis
    assert 'roi_analysis' in cost_analysis
    assert cost_analysis['basic_metrics']['total_cost_actions'] == 2
    print("    ✅ CostAnalyzer funciona correctamente")
    
    print("✅ Todos los analizadores funcionan correctamente")

def test_html_generators(test_data):
    """Probar generadores HTML"""
    print("\n🎨 Probando generadores HTML...")
    
    # Crear objetos de prueba
    user = get_or_create_test_user()
    csv_file = create_test_csv_file(user)
    
    # Crear análisis de prueba
    security_analyzer = SecurityAnalyzer(test_data)
    security_analysis = security_analyzer.analyze()
    
    performance_analyzer = PerformanceAnalyzer(test_data)
    performance_analysis = performance_analyzer.analyze()
    
    cost_analyzer = CostAnalyzer(test_data)
    cost_analysis = cost_analyzer.analyze()
    
    # Probar Security HTML Generator
    print("  🔐 Probando SecurityHTMLGenerator...")
    security_report = create_test_report(user, csv_file, 'security', 'Test Security Report')
    security_generator = SecurityHTMLGenerator(security_report, security_analysis)
    security_html = security_generator.generate_html()
    
    assert '<!DOCTYPE html>' in security_html
    assert 'Security Optimization' in security_html
    assert str(security_analysis['security_score']) in security_html
    print("    ✅ SecurityHTMLGenerator funciona correctamente")
    
    # Probar Performance HTML Generator
    print("  ⚡ Probando PerformanceHTMLGenerator...")
    performance_report = create_test_report(user, csv_file, 'performance', 'Test Performance Report')
    performance_generator = PerformanceHTMLGenerator(performance_report, performance_analysis)
    performance_html = performance_generator.generate_html()
    
    assert '<!DOCTYPE html>' in performance_html
    assert 'Performance Optimization' in performance_html
    print("    ✅ PerformanceHTMLGenerator funciona correctamente")
    
    # Probar Cost HTML Generator
    print("  💰 Probando CostHTMLGenerator...")
    cost_report = create_test_report(user, csv_file, 'cost', 'Test Cost Report')
    cost_generator = CostHTMLGenerator(cost_report, cost_analysis)
    cost_html = cost_generator.generate_html()
    
    assert '<!DOCTYPE html>' in cost_html
    assert 'Cost Optimization' in cost_html
    print("    ✅ CostHTMLGenerator funciona correctamente")
    
    print("✅ Todos los generadores HTML funcionan correctamente")

def test_full_integration():
    """Probar integración completa del flujo"""
    print("\n🔄 Probando integración completa...")
    
    try:
        # Verificar importaciones
        from apps.reports.utils.specialized_analyzers import get_specialized_analyzer
        from apps.reports.utils.specialized_html_generators import get_specialized_html_generator
        print("  ✅ Importaciones correctas")
        
        # Crear datos de prueba
        test_df = create_test_data()
        user = get_or_create_test_user()
        csv_file = create_test_csv_file(user)
        
        # Probar flujo completo para cada tipo
        for report_type in ['security', 'performance', 'cost']:
            print(f"  🔍 Probando flujo completo para {report_type}...")
            
            # 1. Crear reporte
            report = create_test_report(user, csv_file, report_type, f'Integration Test {report_type}')
            
            # 2. Ejecutar análisis
            analyzer = get_specialized_analyzer(report_type, test_df)
            analysis = analyzer.analyze()
            
            # 3. Generar HTML
            generator = get_specialized_html_generator(report_type, report, analysis)
            html = generator.generate_html()
            
            # 4. Verificar resultado
            assert analysis is not None
            assert html is not None
            assert '<!DOCTYPE html>' in html
            
            print(f"    ✅ Flujo {report_type} completado exitosamente")
        
        print("✅ Integración completa funciona correctamente")
        
    except Exception as e:
        print(f"❌ Error en integración completa: {e}")
        raise

def get_or_create_test_user():
    """Obtener o crear usuario de prueba"""
    try:
        user = User.objects.get(username='test_specialized_user')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_specialized_user',
            email='test@specialized.com',
            password='testpass123'
        )
    return user

def create_test_csv_file(user):
    """Crear archivo CSV de prueba"""
    csv_file, created = CSVFile.objects.get_or_create(
        user=user,
        original_filename='test_specialized_data.csv',
        defaults={
            'file_size': 2048,
            'rows_count': 7,
            'columns_count': 4,
            'processing_status': 'completed'
        }
    )
    return csv_file

def create_test_report(user, csv_file, report_type, title):
    """Crear reporte de prueba"""
    report, created = Report.objects.get_or_create(
        user=user,
        title=title,
        report_type=report_type,
        defaults={
            'csv_file': csv_file,
            'status': 'completed'
        }
    )
    return report

if __name__ == '__main__':
    test_specialized_functionality()