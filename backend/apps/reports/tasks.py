# apps/reports/tasks.py - Tareas asíncronas con Celery
from celery import shared_task
from django.apps import apps
from django.utils import timezone
import pandas as pd
import numpy as np
import logging
import os

from .utils.specialized_analyzers import get_specialized_analyzer
from .utils.specialized_html_generators import get_specialized_html_generator

logger = logging.getLogger(__name__)

def convert_to_json_serializable(obj):
    """Convierte objetos numpy y pandas a tipos serializables en JSON"""
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
    
@shared_task(bind=True)
def process_csv_file(self, csv_file_id):
    """Procesar archivo CSV con análisis real de Azure Advisor - VERSIÓN CORREGIDA"""
    csv_file = None
    
    try:
        # Actualizar progreso inicial
        self.update_state(state='PROGRESS', meta={'current': 5, 'total': 100, 'status': 'Iniciando procesamiento...'})
        
        CSVFile = apps.get_model('storage', 'CSVFile')
        csv_file = CSVFile.objects.get(id=csv_file_id)
        
        logger.info(f"Iniciando procesamiento de CSV {csv_file_id}: {csv_file.original_filename}")
        
        # Actualizar estado
        csv_file.processing_status = 'processing'
        csv_file.save(update_fields=['processing_status'])
        
        # Leer archivo CSV
        self.update_state(state='PROGRESS', meta={'current': 20, 'total': 100, 'status': 'Leyendo archivo...'})
        
        csv_data = read_csv_file(csv_file)
        if csv_data is None:
            raise ValueError("No se pudo leer el archivo CSV")
        
        # Procesar datos
        self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100, 'status': 'Analizando contenido...'})
        
        analysis_results = analyze_csv_content(csv_data)
        
        # Actualizar archivo CSV con resultados
        self.update_state(state='PROGRESS', meta={'current': 80, 'total': 100, 'status': 'Guardando resultados...'})
        
        csv_file.analysis_results = convert_to_json_serializable(analysis_results)
        csv_file.processing_status = 'completed'
        csv_file.rows_count = len(csv_data)
        csv_file.columns_count = len(csv_data.columns)
        csv_file.processed_at = timezone.now()
        csv_file.save()
        
        logger.info(f"CSV procesado exitosamente: {csv_file.rows_count} filas, {csv_file.columns_count} columnas")
        
        return f"Procesado exitosamente: {csv_file.rows_count} filas"
        
    except Exception as e:
        error_msg = f"Error procesando CSV {csv_file_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        if csv_file:
            csv_file.processing_status = 'failed'
            csv_file.error_message = str(e)
            csv_file.save(update_fields=['processing_status', 'error_message'])
        
        self.update_state(state='FAILURE', meta={
            'current': 100,
            'total': 100,
            'status': f'Error: {str(e)}',
            'error': str(e)
        })
        
        raise

@shared_task  
def generate_report(report_id):
    """Generar reporte PDF de forma asíncrona - VERSIÓN ACTUALIZADA"""
    report = None
    
    try:
        Report = apps.get_model('reports', 'Report')
        report = Report.objects.get(id=report_id)
        
        logger.info(f"Iniciando generación de reporte {report.id} tipo {report.report_type}")
        
        # Determinar si es especializado o comprehensivo
        if report.report_type in ['security', 'performance', 'cost']:
            # Usar la nueva tarea especializada
            return generate_specialized_report.delay(report_id)
        else:
            # Usar lógica existente para reportes comprehensivos
            return generate_comprehensive_report(report)
            
    except Exception as e:
        error_msg = f"Error determinando tipo de generación para reporte {report_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        if report:
            report.status = 'failed'
            report.error_message = str(e)
            report.save(update_fields=['status', 'error_message'])
        
        raise Exception(error_msg)
    
def generate_comprehensive_report(report):
    """Generar reporte comprehensivo (lógica existente)"""
    try:
        # Aquí va la lógica existente que ya funciona para reportes comprehensivos
        # Esta es la misma lógica que ya tenías funcionando
        
        logger.info(f"Generando reporte comprehensivo para {report.id}")
        
        # Actualizar estado
        report.status = 'generating'
        report.save(update_fields=['status'])
        
        # Usar el generador existente
        from apps.reports.utils.enhanced_analyzer import EnhancedHTMLReportGenerator
        generator = EnhancedHTMLReportGenerator()
        html_content = generator.generate_complete_html(report)
        
        # Generar PDF
        from apps.storage.services.pdf_generator_service import generate_report_pdf
        pdf_bytes, pdf_filename = generate_report_pdf(report, html_content)
        
        # Subir a Azure Storage
        pdf_url, html_url = upload_report_files_to_azure(
            pdf_bytes, html_content, pdf_filename, report
        )
        
        # Actualizar reporte
        report.pdf_url = pdf_url
        report.html_url = html_url
        report.pdf_blob_name = f"reports/{pdf_filename}"
        report.status = 'completed'
        report.completed_at = timezone.now()
        report.save()
        
        logger.info(f"✅ Reporte comprehensivo completado: {report.id}")
        
        return {
            'report_id': str(report.id),
            'report_type': 'comprehensive',
            'status': 'completed',
            'pdf_url': pdf_url,
            'html_url': html_url
        }
        
    except Exception as e:
        logger.error(f"Error en reporte comprehensivo: {e}", exc_info=True)
        report.status = 'failed'
        report.error_message = str(e)
        report.save(update_fields=['status', 'error_message'])
        raise
    
@shared_task(bind=True)
def generate_specialized_report(self, report_id):
    """
    Generar reporte especializado de forma asíncrona - VERSIÓN CORREGIDA
    """
    report = None
    
    try:
        # Actualizar progreso inicial
        self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100, 'status': 'Iniciando...'})
        
        # Obtener modelos
        Report = apps.get_model('reports', 'Report')
        report = Report.objects.get(id=report_id)
        
        logger.info(f"Iniciando generación de reporte especializado {report.id} tipo {report.report_type}")
        
        # Actualizar estado del reporte
        report.status = 'processing'
        report.save(update_fields=['status'])
        
        # Actualizar progreso
        self.update_state(state='PROGRESS', meta={'current': 20, 'total': 100, 'status': 'Procesando CSV...'})
        
        # Obtener datos del CSV
        csv_data = get_csv_dataframe_for_task(report)
        if csv_data is None:
            raise ValueError("No se pudieron obtener datos del CSV para el reporte")
        
        logger.info(f"CSV cargado: {len(csv_data)} filas")
        
        # Actualizar progreso
        self.update_state(state='PROGRESS', meta={'current': 40, 'total': 100, 'status': 'Analizando datos...'})
        
        # Realizar análisis especializado basado en el tipo
        analysis_results = perform_specialized_analysis(csv_data, report.report_type)
        
        # Actualizar progreso
        self.update_state(state='PROGRESS', meta={'current': 60, 'total': 100, 'status': 'Generando HTML...'})
        
        # Generar contenido HTML
        html_content = generate_specialized_html(analysis_results, report)
        
        # Actualizar progreso
        self.update_state(state='PROGRESS', meta={'current': 80, 'total': 100, 'status': 'Generando PDF...'})
        
        # Generar PDF
        try:
            from apps.storage.services.pdf_generator_service import generate_report_pdf
            pdf_bytes, pdf_filename = generate_report_pdf(report, html_content)
        except Exception as pdf_error:
            logger.warning(f"Error generando PDF: {pdf_error}, continuando sin PDF")
            pdf_bytes, pdf_filename = None, None
        
        # Actualizar progreso
        self.update_state(state='PROGRESS', meta={'current': 90, 'total': 100, 'status': 'Guardando resultado...'})
        
        # Actualizar el reporte con los resultados
        report.html_content = html_content
        report.analysis_results = convert_to_json_serializable(analysis_results)
        
        if pdf_bytes:
            # Guardar PDF si se generó exitosamente
            try:
                from apps.storage.services.file_storage_service import save_report_pdf
                pdf_url = save_report_pdf(report, pdf_bytes, pdf_filename)
                report.pdf_url = pdf_url
                report.pdf_blob_name = pdf_filename
            except Exception as save_error:
                logger.warning(f"Error guardando PDF: {save_error}")
        
        # Marcar como completado
        report.status = 'completed'
        report.completed_at = timezone.now()
        report.save(update_fields=['status', 'completed_at', 'html_content', 'analysis_results', 'pdf_url', 'pdf_blob_name'])
        
        logger.info(f"Reporte especializado completado: {report.id}")
        
        # Actualizar progreso final
        self.update_state(state='SUCCESS', meta={
            'current': 100, 
            'total': 100, 
            'status': 'Completado',
            'report_id': str(report.id),
            'report_type': report.report_type
        })
        
        return {
            'report_id': str(report.id),
            'report_type': report.report_type,
            'status': 'completed',
            'total_actions': analysis_results.get('total_actions', 0),
            'estimated_savings': analysis_results.get('estimated_monthly_savings', 0)
        }
        
    except Exception as e:
        logger.error(f"Error en generación de reporte especializado: {e}", exc_info=True)
        
        # Actualizar estado de error
        if report:
            report.status = 'error'
            report.error_message = str(e)
            report.save(update_fields=['status', 'error_message'])
        
        # Actualizar progreso de error
        self.update_state(state='FAILURE', meta={
            'current': 100,
            'total': 100,
            'status': f'Error: {str(e)}',
            'error': str(e)
        })
        
        raise

def perform_specialized_analysis(df, report_type):
    """Realizar análisis especializado según el tipo de reporte"""
    try:
        if report_type == 'security':
            return analyze_security_data(df)
        elif report_type == 'performance':
            return analyze_performance_data(df)
        elif report_type == 'cost':
            return analyze_cost_data(df)
        else:
            return analyze_comprehensive_data(df)
    except Exception as e:
        logger.error(f"Error en análisis especializado: {e}")
        return {'error': str(e)}

def analyze_security_data(df):
    """Análizar datos de seguridad"""
    security_data = df[df['Category'] == 'Security'] if 'Category' in df.columns else df
    
    return {
        'total_actions': len(security_data),
        'high_priority': len(security_data[security_data['Business Impact'] == 'High']) if 'Business Impact' in security_data.columns else 0,
        'medium_priority': len(security_data[security_data['Business Impact'] == 'Medium']) if 'Business Impact' in security_data.columns else 0,
        'security_categories': security_data.groupby('Resource Type').size().to_dict() if 'Resource Type' in security_data.columns else {},
        'analysis_type': 'security'
    }

def analyze_performance_data(df):
    """Analizar datos de rendimiento"""
    performance_data = df[df['Category'] == 'Performance'] if 'Category' in df.columns else df
    
    return {
        'total_actions': len(performance_data),
        'high_impact': len(performance_data[performance_data['Business Impact'] == 'High']) if 'Business Impact' in performance_data.columns else 0,
        'performance_categories': performance_data.groupby('Resource Type').size().to_dict() if 'Resource Type' in performance_data.columns else {},
        'analysis_type': 'performance'
    }

def analyze_cost_data(df):
    """Analizar datos de costos"""
    cost_data = df[df['Category'] == 'Cost'] if 'Category' in df.columns else df
    
    # Calcular ahorros estimados si hay columnas de costos
    estimated_savings = 0
    if 'Monthly Savings (USD)' in cost_data.columns:
        estimated_savings = cost_data['Monthly Savings (USD)'].sum()
    
    return {
        'total_actions': len(cost_data),
        'estimated_monthly_savings': estimated_savings,
        'cost_categories': cost_data.groupby('Resource Type').size().to_dict() if 'Resource Type' in cost_data.columns else {},
        'analysis_type': 'cost'
    }


def analyze_comprehensive_data(df):
    """Análisis completo de todos los datos"""
    return {
        'total_actions': len(df),
        'by_category': df.groupby('Category').size().to_dict() if 'Category' in df.columns else {},
        'by_priority': df.groupby('Business Impact').size().to_dict() if 'Business Impact' in df.columns else {},
        'estimated_monthly_savings': df['Monthly Savings (USD)'].sum() if 'Monthly Savings (USD)' in df.columns else 0,
        'analysis_type': 'comprehensive'
    }

def analyze_csv_content(df):
    """Análizar contenido general del CSV"""
    return {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': list(df.columns),
        'categories': df['Category'].value_counts().to_dict() if 'Category' in df.columns else {},
        'business_impact': df['Business Impact'].value_counts().to_dict() if 'Business Impact' in df.columns else {}
    }

def generate_specialized_html(analysis_results, report):
    """Generar HTML especializado"""
    try:
        # Usar los generadores existentes o crear HTML básico
        from apps.reports.utils.specialized_html_generators import get_specialized_html_generator
        generator = get_specialized_html_generator(report.report_type)
        return generator.generate_html(analysis_results, report)
    except ImportError:
        # Fallback a HTML básico
        return f"""
        <html>
        <head><title>{report.title}</title></head>
        <body>
            <h1>{report.title}</h1>
            <p>Tipo de reporte: {report.report_type}</p>
            <p>Total de acciones: {analysis_results.get('total_actions', 0)}</p>
            <p>Generado: {timezone.now()}</p>
        </body>
        </html>
        """

def get_csv_dataframe_for_task(report):
    """Obtener DataFrame del CSV asociado al reporte"""
    try:
        if not report.csv_file:
            return None
        
        return read_csv_file(report.csv_file)
    except Exception as e:
        logger.error(f"Error obteniendo DataFrame: {e}")
        return None
    
def read_csv_file(csv_file):
    """Leer archivo CSV y retornar DataFrame"""
    try:
        # Leer desde archivo local o Azure Storage
        if csv_file.file_path and os.path.exists(csv_file.file_path):
            return pd.read_csv(csv_file.file_path, encoding='utf-8-sig')
        elif csv_file.azure_blob_url:
            # Implementar lectura desde Azure Storage
            from apps.storage.services.azure_storage_service import AzureStorageService
            storage_service = AzureStorageService()
            content = storage_service.download_file_content(csv_file.azure_blob_name)
            from io import StringIO
            return pd.read_csv(StringIO(content), encoding='utf-8-sig')
        else:
            logger.error("No se encontró ruta del archivo CSV")
            return None
            
    except Exception as e:
        logger.error(f"Error leyendo CSV: {e}")
        return None

def reconstruct_dataframe_from_analysis(analysis_data):
    """Reconstruir DataFrame desde datos de análisis existentes"""
    try:
        synthetic_data = []
        
        # Método 1: Si hay raw_data disponible
        if 'raw_data' in analysis_data:
            return pd.DataFrame(analysis_data['raw_data'])
        
        # Método 2: Reconstruir desde category_analysis
        if 'category_analysis' in analysis_data:
            category_counts = analysis_data['category_analysis'].get('counts', {})
            
            business_impacts = ['High', 'Medium', 'Low']
            resource_types = ['Virtual machine', 'Storage Account', 'App Service', 'Virtual machine', 'Subscription']
            
            idx = 0
            for category, count in category_counts.items():
                for i in range(count):
                    synthetic_data.append({
                        'Category': category,
                        'Business Impact': business_impacts[idx % len(business_impacts)],
                        'Recommendation': f'Sample {category.lower()} recommendation #{i+1}',
                        'Resource Type': resource_types[idx % len(resource_types)]
                    })
                    idx += 1
        
        # Método 3: Generar datos básicos desde métricas
        elif 'dashboard_metrics' in analysis_data or 'executive_summary' in analysis_data:
            metrics = analysis_data.get('dashboard_metrics', analysis_data.get('executive_summary', {}))
            total_actions = metrics.get('total_actions', 10)
            
            categories = ['Security', 'Cost', 'Performance', 'Reliability']
            impacts = ['High', 'Medium', 'Low']
            resources = ['Virtual machine', 'Storage Account', 'App Service']
            
            for i in range(min(total_actions, 100)):  # Máximo 100 registros sintéticos
                synthetic_data.append({
                    'Category': categories[i % len(categories)],
                    'Business Impact': impacts[i % len(impacts)],
                    'Recommendation': f'Synthetic recommendation #{i+1}',
                    'Resource Type': resources[i % len(resources)]
                })
        
        if synthetic_data:
            df = pd.DataFrame(synthetic_data)
            logger.info(f"DataFrame reconstruido con {len(df)} registros sintéticos")
            return df
        
        return None
        
    except Exception as e:
        logger.error(f"Error reconstruyendo DataFrame: {e}")
        return None

def upload_report_files_to_azure(pdf_bytes, html_content, pdf_filename, report):
    """Subir archivos de reporte a Azure Storage"""
    try:
        from apps.storage.services.azure_storage_service import AzureStorageService
        storage_service = AzureStorageService()
        
        # Subir PDF
        pdf_blob_name = f"reports/{pdf_filename}"
        pdf_url = storage_service.upload_file_content(pdf_bytes, pdf_blob_name, 'application/pdf')
        
        # Subir HTML
        html_filename = pdf_filename.replace('.pdf', '.html')
        html_blob_name = f"reports/{html_filename}"
        html_bytes = html_content.encode('utf-8')
        html_url = storage_service.upload_file_content(html_bytes, html_blob_name, 'text/html')
        
        logger.info(f"Archivos subidos - PDF: {pdf_url}, HTML: {html_url}")
        return pdf_url, html_url
        
    except Exception as e:
        logger.error(f"Error subiendo archivos a Azure: {e}")
        # En caso de error, retornar None para que el reporte se marque como completado sin URLs
        return None, None
    
@shared_task
def validate_csv_for_specialized_analysis(csv_file_id, report_type):
    """Validar que el CSV tenga los datos necesarios para análisis especializado"""
    try:
        CSVFile = apps.get_model('reports', 'CSVFile')
        csv_file = CSVFile.objects.get(id=csv_file_id)
        
        logger.info(f"Validando CSV {csv_file_id} para análisis {report_type}")
        
        # Obtener DataFrame
        df = get_csv_dataframe_for_task_by_csv_file(csv_file)
        if df is None or df.empty:
            return {'valid': False, 'error': 'No se pudieron cargar datos del CSV'}
        
        # Validaciones específicas por tipo
        validation_results = {
            'valid': True,
            'total_records': len(df),
            'columns_found': list(df.columns),
            'type_specific_data': {}
        }
        
        if report_type == 'security':
            security_records = df[df.get('Category', pd.Series()).str.lower() == 'security']
            validation_results['type_specific_data'] = {
                'security_records': len(security_records),
                'has_security_data': len(security_records) > 0
            }
            if len(security_records) == 0:
                validation_results['valid'] = False
                validation_results['error'] = 'No se encontraron registros de seguridad en el CSV'
        
        elif report_type == 'performance':
            performance_records = df[df.get('Category', pd.Series()).str.lower() == 'performance']
            validation_results['type_specific_data'] = {
                'performance_records': len(performance_records),
                'has_performance_data': len(performance_records) > 0
            }
            if len(performance_records) == 0:
                validation_results['valid'] = False
                validation_results['error'] = 'No se encontraron registros de rendimiento en el CSV'
        
        elif report_type == 'cost':
            cost_records = df[df.get('Category', pd.Series()).str.lower() == 'cost']
            validation_results['type_specific_data'] = {
                'cost_records': len(cost_records),
                'has_cost_data': len(cost_records) > 0
            }
            if len(cost_records) == 0:
                validation_results['valid'] = False
                validation_results['error'] = 'No se encontraron registros de costo en el CSV'
        
        logger.info(f"Validación completada: {validation_results}")
        return validation_results
        
    except Exception as e:
        logger.error(f"Error validando CSV {csv_file_id}: {e}")
        return {'valid': False, 'error': str(e)}

def get_csv_dataframe_for_task_by_csv_file(csv_file):
    """Helper para obtener DataFrame desde CSVFile object"""
    try:
        if csv_file.azure_blob_url and csv_file.azure_blob_name:
            from apps.storage.services.azure_storage_service import AzureStorageService
            storage_service = AzureStorageService()
            csv_content = storage_service.download_file_content(csv_file.azure_blob_name)
            
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
                temp_file.write(csv_content)
                temp_path = temp_file.name
            
            df = pd.read_csv(temp_path)
            os.unlink(temp_path)
            
            return df
        
        elif csv_file.analysis_data:
            return reconstruct_dataframe_from_analysis(csv_file.analysis_data)
        
        return None
        
    except Exception as e:
        logger.error(f"Error obteniendo DataFrame desde CSVFile: {e}")
        return None