import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.reports.models import Report
from apps.storage.services.complete_report_service import generate_complete_report

def test_complete_system():
    print("=== TESTING COMPLETE SYSTEM ===")
    
    # 1. Verificar servicios
    print("\n1. Verificando servicios...")
    
    try:
        from apps.storage.services.pdf_generator_service import PDFGeneratorService
        pdf_service = PDFGeneratorService()
        print(f"✅ PDF Service: {pdf_service.available_engines}")
    except Exception as e:
        print(f"❌ PDF Service: {e}")
        return
    
    try:
        from apps.storage.services.enhanced_azure_storage import enhanced_azure_storage
        azure_info = enhanced_azure_storage.get_storage_info()
        print(f"✅ Azure Storage: {azure_info['status']}")
        if azure_info['status'] != 'available':
            print(f"⚠️ Azure not configured: {azure_info}")
    except Exception as e:
        print(f"❌ Azure Storage: {e}")
    
    # 2. Probar con reporte real
    print("\n2. Probando generación completa...")
    
    report = Report.objects.first()
    if not report:
        print("❌ No hay reportes para probar")
        return
    
    print(f"Usando reporte: {report.title}")
    
    # 3. Generar reporte completo
    result = generate_complete_report(report)
    
    print(f"\n3. Resultados:")
    print(f"   ✅ Éxito: {result['success']}")
    print(f"   📄 HTML: {result['html_generated']}")
    print(f"   📋 PDF: {result['pdf_generated']}")
    print(f"   ☁️  PDF en Azure: {result['pdf_uploaded']}")
    print(f"   📊 DataFrame en Azure: {result['dataframe_uploaded']}")
    
    if result['success']:
        print(f"\n4. URLs generadas:")
        if 'pdf' in result['urls']:
            print(f"   PDF: {result['urls']['pdf'][:60]}...")
        if 'dataframe' in result['urls']:
            print(f"   DataFrame: {result['urls']['dataframe'][:60]}...")
        
        print(f"\n5. Cliente detectado: {result.get('client_name', 'No detectado')}")
        
        if result.get('pdf_size'):
            print(f"   Tamaño PDF: {result['pdf_size']:,} bytes")
    
    else:
        print(f"\n❌ Errores:")
        for error in result['errors']:
            print(f"   - {error}")

if __name__ == "__main__":
    test_complete_system()