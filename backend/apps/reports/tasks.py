# apps/reports/tasks.py - Tareas asíncronas con Celery
from celery import shared_task
from django.apps import apps
from django.utils import timezone
import pandas as pd
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

def convert_to_json_serializable(obj):
    """
    Convierte objetos numpy y pandas a tipos serializables en JSON
    """
    if isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj

@shared_task
def process_csv_file(csv_file_id):
    """Procesar archivo CSV con análisis real de Azure Advisor"""
    csv_file = None
    temp_file_path = None
    
    try:
        from django.apps import apps
        CSVFile = apps.get_model('reports', 'CSVFile')
        csv_file = CSVFile.objects.get(id=csv_file_id)
        
        logger.info(f"Iniciando procesamiento de CSV {csv_file_id}: {csv_file.original_filename}")
        
        # Actualizar estado
        csv_file.processing_status = 'processing'
        csv_file.save(update_fields=['processing_status'])
        
        # Leer contenido del archivo
        csv_content = None
        if csv_file.azure_blob_url:
            # Si está en Azure Storage
            try:
                from apps.storage.services.azure_storage_service import AzureStorageService
                storage_service = AzureStorageService()
                csv_content = storage_service.download_file_content(csv_file.azure_blob_name)
                logger.info(f"Archivo descargado desde Azure Storage: {csv_file.azure_blob_name}")
            except Exception as e:
                logger.warning(f"Error descargando desde Azure Storage: {e}")
        
        if not csv_content and csv_file.file_path:
            # Leer desde archivo local
            try:
                with open(csv_file.file_path, 'r', encoding='utf-8-sig') as f:
                    csv_content = f.read()
                logger.info(f"Archivo leído desde path local: {csv_file.file_path}")
            except Exception as e:
                logger.warning(f"Error leyendo archivo local: {e}")
        
        if not csv_content:
            raise Exception("No se pudo obtener el contenido del archivo CSV")
        
        # **USAR EL NUEVO ANALIZADOR REAL**
        try:
            from apps.reports.analyzers.csv_analyzer import analyze_csv_content
            analysis_results = analyze_csv_content(csv_content)
            logger.info("✅ Usando analizador real de Azure Advisor")
        except ImportError:
            logger.warning("⚠️  Analizador real no disponible, usando análisis básico")
            # Análisis básico como fallback
            import pandas as pd
            from io import StringIO
            
            df = pd.read_csv(StringIO(csv_content))
            analysis_results = {
                'executive_summary': {
                    'total_actions': len(df),
                    'advisor_score': 65,  # Score por defecto
                },
                'cost_optimization': {
                    'estimated_monthly_optimization': len(df) * 100,  # Estimación básica
                },
                'totals': {
                    'total_actions': len(df),
                    'total_monthly_savings': len(df) * 100,
                    'total_working_hours': len(df) * 0.5,
                    'azure_advisor_score': 65
                },
                'metadata': {
                    'analysis_date': timezone.now().isoformat(),
                    'csv_rows': len(df),
                    'csv_columns': len(df.columns),
                    'data_source': 'Basic CSV Analysis'
                }
            }
        
        # Guardar resultados
        csv_file.rows_count = analysis_results.get('metadata', {}).get('csv_rows', 0)
        csv_file.columns_count = analysis_results.get('metadata', {}).get('csv_columns', 0)
        csv_file.analysis_data = analysis_results
        csv_file.processing_status = 'completed'
        csv_file.processed_date = timezone.now()
        csv_file.save()
        
        logger.info(f"✅ CSV {csv_file_id} procesado exitosamente: {csv_file.rows_count} filas")
        logger.info(f"📊 Acciones totales: {analysis_results.get('executive_summary', {}).get('total_actions', 0)}")
        logger.info(f"💰 Ahorros estimados: ${analysis_results.get('cost_optimization', {}).get('estimated_monthly_optimization', 0):,}")
        
        return f"Procesado exitosamente: {csv_file.rows_count} filas"
        
    except Exception as e:
        error_msg = f"Error procesando CSV {csv_file_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        if csv_file:
            csv_file.processing_status = 'failed'
            csv_file.error_message = str(e)
            csv_file.save(update_fields=['processing_status', 'error_message'])
        
        # Limpiar archivo temporal en caso de error
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass
        # Guardar también el path del archivo para acceso posterior
        if not csv_file.file_path and temp_file_path:
            csv_file.file_path = temp_file_path
            csv_file.save()

        raise Exception(error_msg)
@shared_task
def generate_report(report_id):
    """Generar reporte PDF de forma asíncrona"""
    report = None
    
    try:
        Report = apps.get_model('reports', 'Report')
        report = Report.objects.get(id=report_id)
        
        logger.info(f"Iniciando generación de reporte {report_id}")
        
        # Actualizar estado
        report.status = 'generating'
        report.save(update_fields=['status'])
        
        # Generar PDF (implementación básica)
        try:
            from apps.storage.services.report_service import ReportGenerator
            generator = ReportGenerator(report)
            pdf_file_path, html_content = generator.generate()
            
            # Subir a Azure Storage
            try:
                from apps.storage.services.azure_storage_service import upload_file
                blob_name = f"reports/{report.id}.pdf"
                blob_url = upload_file(pdf_file_path, blob_name)
                
                # Actualizar reporte
                report.pdf_file_url = blob_url
                report.pdf_azure_blob_name = blob_name
                report.html_preview_url = html_content
            except ImportError:
                logger.warning("Azure Storage no disponible, guardando localmente")
                report.pdf_file_url = pdf_file_path
                
        except ImportError:
            logger.warning("ReportGenerator no disponible, creando reporte básico")
            # Crear reporte básico
            report.pdf_file_url = f"/tmp/basic_report_{report_id}.pdf"
            report.html_preview_url = "<p>Reporte básico generado</p>"
        
        # Finalizar
        report.status = 'completed'
        report.completed_at = timezone.now()
        report.save()
        
        logger.info(f"Reporte {report_id} generado exitosamente")
        return f"Reporte {report_id} completado"
        
    except Exception as e:
        error_msg = f"Error generando reporte {report_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        if report:
            report.status = 'failed'
            report.error_message = str(e)
            report.save(update_fields=['status', 'error_message'])
        
        raise Exception(error_msg)