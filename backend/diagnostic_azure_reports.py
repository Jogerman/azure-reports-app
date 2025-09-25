#!/usr/bin/env python
"""
Diagnóstico integral del sistema de reportes Azure
Ejecutar desde el directorio backend: python diagnostic_azure_reports.py
"""

import os
import django
import sys
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def print_section(title):
    """Imprimir sección con formato"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subsection(title):
    """Imprimir subsección con formato"""
    print(f"\n--- {title} ---")

def test_pdf_service():
    """Probar servicio de PDF"""
    print_subsection("PDF SERVICE")
    try:
        from apps.storage.services.pdf_generator_service import PDFGeneratorService
        pdf_service = PDFGeneratorService()
        print(f"✅ PDF Service disponible")
        print(f"   Motores: {pdf_service.available_engines}")
        print(f"   Motor preferido: {pdf_service.preferred_engine}")
        return True, pdf_service
    except Exception as e:
        print(f"❌ PDF Service error: {e}")
        print(f"   Solución: pip install weasyprint")
        return False, None

def test_azure_storage():
    """Probar Azure Storage"""
    print_subsection("AZURE STORAGE")
    try:
        from apps.storage.services.enhanced_azure_storage import enhanced_azure_storage
        info = enhanced_azure_storage.get_storage_info()
        
        print(f"Estado: {info['status']}")
        if info['status'] == 'available':
            print(f"✅ Azure Storage disponible")
            print(f"   Cuenta: {info['account_name']}")
            print(f"   Contenedores: {info['containers']}")
            
            if 'container_stats' in info:
                print(f"   Estadísticas:")
                for container_type, stats in info['container_stats'].items():
                    if 'error' not in stats:
                        print(f"     {container_type}: {stats['blob_count']} blobs, {stats['total_size']} bytes")
                    else:
                        print(f"     {container_type}: {stats['error']}")
            
            return True, enhanced_azure_storage
        else:
            print(f"❌ Azure Storage no disponible: {info.get('reason', 'Unknown')}")
            return False, None
            
    except Exception as e:
        print(f"❌ Azure Storage error: {e}")
        print(f"   Solución: Configurar variables de ambiente AZURE_*")
        return False, None

def test_complete_report_service():
    """Probar servicio completo de reportes"""
    print_subsection("COMPLETE REPORT SERVICE")
    try:
        from apps.storage.services.complete_report_service import complete_report_service
        
        print(f"✅ Complete Report Service disponible")
        print(f"   PDF Service ready: {complete_report_service.pdf_service is not None}")
        print(f"   Azure Service ready: {complete_report_service.azure_service is not None}")
        
        if complete_report_service.azure_service:
            azure_ready = complete_report_service.azure_service.is_available()
            print(f"   Azure Service available: {azure_ready}")
        
        return True, complete_report_service
    except Exception as e:
        print(f"❌ Complete Report Service error: {e}")
        return False, None

def test_with_real_report():
    """Probar con reporte real"""
    print_subsection("TEST CON REPORTE REAL")
    try:
        from apps.reports.models import Report
        
        reports = Report.objects.all()[:5]
        print(f"Reportes disponibles: {reports.count()}")
        
        if not reports.exists():
            print("❌ No hay reportes para probar")
            print("   Solución: Crear un reporte primero")
            return False, None
        
        # Usar el primer reporte
        report = reports.first()
        print(f"✅ Usando reporte: {report.title} (ID: {report.id})")
        print(f"   Estado: {report.status}")
        print(f"   PDF URL: {'Disponible' if report.pdf_file_url else 'No disponible'}")
        print(f"   Analysis Data: {'Disponible' if report.analysis_data else 'No disponible'}")
        
        return True, report
    except Exception as e:
        print(f"❌ Error obteniendo reportes: {e}")
        return False, None

def test_pdf_generation(report):
    """Probar generación completa de PDF"""
    print_subsection("GENERACIÓN DE PDF")
    try:
        from apps.storage.services.complete_report_service import generate_complete_report
        
        print(f"Generando PDF para reporte {report.id}...")
        
        # Ejecutar generación
        result = generate_complete_report(report)
        
        print(f"Resultados:")
        print(f"   ✅ Éxito: {result['success']}")
        print(f"   📄 HTML generado: {result['html_generated']}")
        print(f"   📋 PDF generado: {result['pdf_generated']}")
        print(f"   ☁️  PDF en Azure: {result['pdf_uploaded']}")
        print(f"   📊 DataFrame en Azure: {result['dataframe_uploaded']}")
        
        if result['success']:
            print(f"URLs generadas:")
            for url_type, url in result['urls'].items():
                print(f"   {url_type}: {url[:60]}...")
            
            print(f"Cliente detectado: {result.get('client_name', 'No detectado')}")
            
            if result.get('pdf_size'):
                print(f"Tamaño PDF: {result['pdf_size']:,} bytes")
            
            # Verificar que se guardó en la BD
            report.refresh_from_db()
            print(f"Report actualizado:")
            print(f"   PDF URL en BD: {'Disponible' if report.pdf_file_url else 'No disponible'}")
            print(f"   Analysis data actualizado: {'Sí' if report.analysis_data and 'pdf_info' in report.analysis_data else 'No'}")
            
            return True, result
        else:
            print(f"❌ Errores:")
            for error in result['errors']:
                print(f"   - {error}")
            return False, result
            
    except Exception as e:
        print(f"❌ Error en generación: {e}")
        import traceback
        print(traceback.format_exc())
        return False, None

def test_download_urls():
    """Probar URLs de descarga"""
    print_subsection("URLS DE DESCARGA")
    try:
        from apps.reports.models import Report
        
        reports_with_pdf = Report.objects.filter(pdf_file_url__isnull=False).exclude(pdf_file_url='')
        print(f"Reportes con PDF URL: {reports_with_pdf.count()}")
        
        for report in reports_with_pdf[:3]:  # Probar primeros 3
            print(f"\nReporte {report.id}:")
            print(f"   PDF URL: {report.pdf_file_url[:80]}..." if report.pdf_file_url else "   No URL")
            
            # Verificar si la URL es válida (empieza con https)
            if report.pdf_file_url and report.pdf_file_url.startswith('https://'):
                print(f"   ✅ URL válida")
                
                # Si hay analysis_data, mostrar info del blob
                if report.analysis_data and 'pdf_info' in report.analysis_data:
                    pdf_info = report.analysis_data['pdf_info']
                    print(f"   Blob name: {pdf_info.get('blob_name', 'N/A')}")
                    print(f"   Container: {pdf_info.get('container', 'N/A')}")
                    print(f"   Size: {pdf_info.get('size_bytes', 'N/A')} bytes")
                    print(f"   Uploaded: {pdf_info.get('uploaded_at', 'N/A')}")
            else:
                print(f"   ❌ URL inválida o faltante")
        
        return True
    except Exception as e:
        print(f"❌ Error verificando URLs: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    print_section(f"DIAGNÓSTICO INTEGRAL - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: PDF Service
    print_section("1. SERVICIOS BÁSICOS")
    pdf_ok, pdf_service = test_pdf_service()
    azure_ok, azure_service = test_azure_storage()
    complete_ok, complete_service = test_complete_report_service()
    
    services_ok = pdf_ok and azure_ok and complete_ok
    print(f"\n>>> Estado general de servicios: {'✅ OK' if services_ok else '❌ ERROR'}")
    
    if not services_ok:
        print("\n🚨 ACCIÓN REQUERIDA:")
        if not pdf_ok:
            print("   - Instalar WeasyPrint: pip install weasyprint")
        if not azure_ok:
            print("   - Configurar Azure Storage (variables de ambiente)")
        if not complete_ok:
            print("   - Verificar complete_report_service")
        return
    
    # Test 2: Reportes existentes
    print_section("2. REPORTES EXISTENTES")
    report_ok, report = test_with_real_report()
    
    if not report_ok:
        print("\n🚨 ACCIÓN REQUERIDA:")
        print("   - Crear al menos un reporte para pruebas")
        return
    
    # Test 3: Generación de PDF
    print_section("3. GENERACIÓN DE PDF")
    generation_ok, generation_result = test_pdf_generation(report)
    
    if generation_ok:
        print("\n>>> Generación de PDF: ✅ OK")
    else:
        print("\n>>> Generación de PDF: ❌ ERROR")
        print("\n🚨 ACCIÓN REQUERIDA:")
        print("   - Revisar logs de errores arriba")
        print("   - Verificar configuración de servicios")
    
    # Test 4: URLs de descarga
    print_section("4. URLS DE DESCARGA")
    download_ok = test_download_urls()
    
    # Resumen final
    print_section("RESUMEN FINAL")
    
    all_ok = services_ok and report_ok and generation_ok and download_ok
    
    print(f"Estado general del sistema: {'✅ FUNCIONANDO' if all_ok else '❌ CON ERRORES'}")
    print(f"   Servicios básicos: {'✅' if services_ok else '❌'}")
    print(f"   Reportes disponibles: {'✅' if report_ok else '❌'}")
    print(f"   Generación de PDF: {'✅' if generation_ok else '❌'}")
    print(f"   URLs de descarga: {'✅' if download_ok else '❌'}")
    
    if all_ok:
        print(f"\n🎉 SISTEMA FUNCIONANDO CORRECTAMENTE")
        print(f"   El problema de descarga debería estar resuelto.")
        print(f"   Usar endpoints: /api/reports/{{id}}/generate-pdf-reliable/")
        print(f"                  /api/reports/{{id}}/download/")
    else:
        print(f"\n🚨 SISTEMA CON PROBLEMAS")
        print(f"   Revisar errores específicos arriba")
        print(f"   Ejecutar acciones requeridas")

if __name__ == "__main__":
    main()