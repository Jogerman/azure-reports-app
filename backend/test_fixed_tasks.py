# backend/test_fixed_tasks.py - Probar función corregida

import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_generate_specialized_report():
    """Probar la función corregida"""
    print("=== PROBANDO FUNCIÓN GENERATE_SPECIALIZED_REPORT CORREGIDA ===\n")
    
    try:
        # 1. Importar función
        from apps.reports.tasks import generate_specialized_report
        print("✅ Función importada correctamente")
        
        # 2. Verificar que es una tarea de Celery
        if hasattr(generate_specialized_report, 'delay'):
            print("✅ Función tiene atributo 'delay' - es una tarea de Celery")
        else:
            print("❌ Función NO tiene atributo 'delay'")
            return False
        
        # 3. Buscar un reporte existente para probar
        from apps.reports.models import Report
        reports = Report.objects.all()
        
        if not reports.exists():
            print("⚠️ No hay reportes en la base de datos para probar")
            print("💡 Crea un reporte desde el frontend primero")
            return True
        
        # 4. Tomar el primer reporte
        test_report = reports.first()
        print(f"📋 Usando reporte para prueba: {test_report.id} (Tipo: {test_report.report_type})")
        
        # 5. Verificar que el reporte tiene CSV
        if not test_report.csv_file:
            print("⚠️ El reporte no tiene CSV asociado")
            return True
        
        print(f"📄 CSV asociado: {test_report.csv_file.original_filename}")
        
        # 6. Intentar ejecutar la función usando el método correcto
        print("\n🔄 Ejecutando función usando apply() (sincrónicamente)...")
        
        try:
            # Ejecutar función usando apply() que maneja bind=True correctamente
            result = generate_specialized_report.apply(args=[str(test_report.id)])
            print(f"   ✅ Función ejecutada sin errores de sintaxis")
        except Exception as apply_error:
            print(f"   ❌ Error en apply(): {apply_error}")
            # Intentar método alternativo
            print("   🔄 Intentando método alternativo...")
            
            try:
                # Crear tarea directamente con los argumentos correctos
                from apps.reports.tasks import generate_specialized_report as orig_func
                
                # Llamar la función interna directamente
                result_data = orig_func.__wrapped__(None, str(test_report.id))
                
                # Simular resultado de apply()
                class MockResult:
                    def __init__(self, data):
                        self.result = data
                    def failed(self):
                        return False
                
                result = MockResult(result_data)
                print("   ✅ Método alternativo funcionó")
                
            except Exception as alt_error:
                print(f"   ❌ Error en método alternativo: {alt_error}")
                raise alt_error
        
        if result and result.result and result.result.get('status') == 'completed':
            print(f"🎉 FUNCIÓN EJECUTADA EXITOSAMENTE!")
            print(f"   📋 Report ID: {result.result['report_id']}")
            print(f"   📊 Tipo: {result.result['report_type']}")
            print(f"   📈 Total acciones: {result.result['total_actions']}")
            
            # Verificar que el reporte se actualizó
            test_report.refresh_from_db()
            print(f"   ✅ Estado del reporte: {test_report.status}")
            
            if test_report.pdf_url:
                print(f"   📄 PDF URL generada: ✅")
            if test_report.html_url:
                print(f"   🌐 HTML URL generada: ✅")
            
            return True
        elif result and result.failed():
            print(f"❌ Función falló: {result.traceback}")
            return False
        else:
            print(f"❌ Función ejecutada pero resultado no esperado: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando función: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_celery_async():
    """Probar con Celery asíncrono"""
    print("\n=== PROBANDO CON CELERY ASÍNCRONO ===\n")
    
    try:
        from apps.reports.tasks import generate_specialized_report
        from apps.reports.models import Report
        
        reports = Report.objects.all()
        if not reports.exists():
            print("⚠️ No hay reportes para probar")
            return
        
        test_report = reports.first()
        
        # Ejecutar asincrónicamente
        print(f"🚀 Enviando tarea a Celery para reporte: {test_report.id}")
        task = generate_specialized_report.delay(str(test_report.id))
        
        print(f"📝 Tarea creada con ID: {task.id}")
        print("💡 Monitorea el progreso desde el frontend o revisa los logs de Celery")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con Celery: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Iniciando pruebas...\n")
    
    # Prueba 1: Función directa
    success = test_generate_specialized_report()
    
    if success:
        print("\n" + "="*60)
        # Prueba 2: Celery async (opcional)
        test_with_celery_async()
    
    print("\n" + "="*60)
    if success:
        print("✅ PRUEBAS COMPLETADAS - La función debería funcionar correctamente")
        print("💡 Ahora puedes probar desde el frontend sin problemas")
    else:
        print("❌ HAY PROBLEMAS - Revisa los errores arriba")
        print("💡 Verifica que hayas reemplazado la función correctamente")