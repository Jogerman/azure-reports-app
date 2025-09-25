# backend/apps/storage/services/complete_report_service.py
import logging
from typing import Optional, Dict, Any, Tuple
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)

class CompleteReportService:
    """Servicio completo para generar reportes PDF y almacenar en Azure"""
    
    def __init__(self):
        self.pdf_service = None
        self.azure_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Inicializar servicios requeridos"""
        try:
            from .pdf_generator_service import PDFGeneratorService
            self.pdf_service = PDFGeneratorService()
            logger.info("✅ PDF service inicializado")
        except Exception as e:
            logger.warning(f"⚠️ PDF service no disponible: {e}")
        
        try:
            from .enhanced_azure_storage import enhanced_azure_storage
            if  enhanced_azure_storage.is_available():
                self.azure_service = enhanced_azure_storage
                logger.info("✅ Azure Storage service inicializado")
            else:
                logger.warning("⚠️ Azure Storage no configurado")
        except Exception as e:
            logger.error(f"⚠️ Azure service no disponible: {e}")
    
    def generate_complete_report(self, report) -> Dict[str, Any]:
        """
        Generar reporte completo con HTML, PDF y almacenar en Azure
        
        Args:
            report: Objeto Report de Django
            
        Returns:
            Dict con información del procesamiento
        """
        result = {
            'success': False,
            'html_generated': False,
            'pdf_generated': False,
            'pdf_uploaded': False,
            'dataframe_uploaded': False,
            'errors': [],
            'urls': {},
            'metadata': {}
        }
        
        try:
                logger.info(f"🚀 Iniciando generación completa para reporte {report.id}")
                # 1. Generar HTML con datos reales
                html_content, client_name = self._generate_html(report)
                if html_content:
                    result['html_generated'] = True
                    result['client_name'] = client_name
                    logger.info(f"✅ HTML generado para {client_name}")
                else:
                    result['errors'].append("Error generando HTML")
                    return result
                
                # 2. Generar PDF desde HTML
                if self.pdf_service:
                    pdf_bytes, pdf_filename = self._generate_pdf(report, html_content)
                    if pdf_bytes:
                        result['pdf_generated'] = True
                        result['pdf_filename'] = pdf_filename
                        result['pdf_size'] = len(pdf_bytes)
                        logger.info(f"✅ PDF generado: {pdf_filename} ({len(pdf_bytes)} bytes)")
                        
                        # 3. Subir PDF a Azure
                        if self.azure_service and self.azure_service.is_available():
                            pdf_info = self._upload_pdf_to_azure(pdf_bytes, report, client_name)
                            if pdf_info:
                                result['pdf_uploaded'] = True
                                result['urls']['pdf'] = pdf_info['blob_url']
                                result['metadata']['pdf'] = pdf_info
                                logger.info(f"✅ PDF subido a Azure: {pdf_info['blob_name']}")

                                # 4. Actualizar Report en transacción separada y segura
                                update_success = self._update_report_with_pdf_info(report, pdf_info)
                                if not update_success:
                                    logger.info(f"✅ PDF subido a Azure: {pdf_info['blob_name']}")
                            else:
                                result['errors'].append("Error subiendo PDF a Azure")
                        else:
                            result['errors'].append("Azure Storage no disponible")
                    else:
                        result['errors'].append("Error generando PDF")
                else:
                    result['errors'].append("PDF service no disponible")
                
                # 5. Subir DataFrame a Azure (operación separada)
                if self.azure_service and self.azure_service.is_available():
                    dataframe_info = self._upload_dataframe_to_azure(report)
                    if dataframe_info:
                        result['dataframe_uploaded'] = True
                        result['urls']['dataframe'] = dataframe_info.get('primary_url')
                        result['metadata']['dataframe'] = dataframe_info
                        logger.info(f"✅ DataFrame subido a Azure")
                        
                        # 6. Actualizar CSVFile en transacción separada y segura
                        csv_update_success  = self._update_csvfile_with_dataframe_info(report.csv_file, dataframe_info)
                        if not csv_update_success:
                            logger.warning("⚠️ Error actualizando CSVFile, pero DataFrame subido exitosamente")
                
                # 7. Actualizar estado final en transacción separada
                final_update_success = self._safe_update_report_status(report, 'completed')
                
                # Determinar éxito general
                # Considerar exitoso si al menos PDF fue generado y subido
                if result['pdf_generated'] and result['pdf_uploaded']:
                    result['success'] = True
                    logger.info(f"🎉 Reporte completo generado exitosamente para {client_name}")
                else:
                    result['success'] = False
                    logger.error(f"❌ Falló generación completa para {client_name}")
                
        except Exception as e:
            logger.error(f"❌ Error en generate_complete_report: {e}")
            result['errors'].append(str(e))
            
            # Actualizar estado de error
            try:
                self._safe_update_report_status(report, 'failed') 
            except Exception:
                pass
        
        return result
    
    def _safe_update_report_status(self, report, status: str) -> bool:
        """Actualizar estado del reporte de forma segura"""
        try:
            with transaction.atomic():
                report.status = status
                if status == 'completed':
                    report.completed_at = timezone.now()
                    report.save(update_fields=['status', 'completed_at'])
                else:
                    report.save(update_fields=['status'])
                
                logger.info(f"✅ Report status actualizado a: {status}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error actualizando status del report: {e}")
            return False
    
    def _generate_html(self, report) -> Tuple[Optional[str], str]:
        """Generar HTML del reporte"""
        try:
            from apps.reports.utils.enhanced_analyzer import EnhancedHTMLReportGenerator
            
            generator = EnhancedHTMLReportGenerator()
            html_content = generator.generate_complete_html(report)
            
            # Extraer nombre del cliente
            client_name = "Azure Client"
            if report.csv_file and report.csv_file.original_filename:
                client_name = self._extract_client_name(report.csv_file.original_filename)
            
            return html_content, client_name
            
        except Exception as e:
            logger.error(f"Error generando HTML: {e}")
            return None, "Azure Client"
    
    def _generate_pdf(self, report, html_content: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Generar PDF desde HTML"""
        try:
            from .pdf_generator_service import generate_report_pdf
            return generate_report_pdf(report, html_content)
        except Exception as e:
            logger.error(f"Error generando PDF: {e}")
            return None, None
    
    def _upload_pdf_to_azure(self, pdf_bytes: bytes, report, client_name: str) -> Optional[Dict[str, Any]]:
        """Subir PDF a Azure Storage"""
        try:
            return self.azure_service.upload_pdf(pdf_bytes, str(report.id), client_name)
        except Exception as e:
            logger.error(f"Error subiendo PDF: {e}")
            return None
    
    def _upload_dataframe_to_azure(self, report) -> Optional[Dict[str, Any]]:
        """Subir DataFrame a Azure Storage"""
        try:
            if not report.csv_file:
                logger.info("No CSV file disponible para subir DataFrame")
                return None
            
            # Obtener DataFrame desde el generador HTML
            from apps.reports.utils.enhanced_analyzer import EnhancedHTMLReportGenerator
            generator = EnhancedHTMLReportGenerator()
            df, _ = generator._get_csv_data(report)
            
            if len(df) > 0:
                # Crear metadatos adicionales
                metadata = {
                    'report_id': str(report.id),
                    'original_filename': report.csv_file.original_filename,
                    'processing_status':  getattr(report.csv_file, 'processing_status', 'completed'),
                    'row_count': len(df),
                    'columns': list(df.columns)
                }
                
                return self.azure_service.upload_dataframe(df, str(report.csv_file.id), metadata)
            
                if result:
                    logger.info(f"✅ DataFrame subido exitosamente: {len(df)} filas")
                return result
                
            else:
                logger.warning("DataFrame vacío, no se sube a Azure")
                return None
            
        except Exception as e:
            logger.error(f"Error subiendo DataFrame: {e}")
            return None
    
    def _update_report_with_pdf_info(self, report, pdf_info: Dict[str, Any]) -> bool:
        """Actualizar Report con información del PDF de forma segura"""

        try:
            with transaction.atomic():
                 # Truncar URL si es muy larga para evitar errores
                pdf_url = pdf_info['blob_url']
                if len(pdf_url) > 450:  # Dejar margen para seguridad
                    logger.warning(f"URL muy larga ({len(pdf_url)} chars), truncando...")
                    pdf_url = pdf_url[:450]
                
                report.pdf_file_url = pdf_url
            
                # Actualizar blob_name si el campo existe
                if hasattr(report, 'pdf_azure_blob_name'):
                    blob_name = pdf_info['blob_name']
                    if len(blob_name) > 250:  # Dejar margen
                        blob_name = blob_name[:250]
                    report.pdf_azure_blob_name = blob_name
            
                # Actualizar analysis_data con información del PDF
                if not report.analysis_data:
                    report.analysis_data = {}
            
                report.analysis_data['pdf_info'] = {
                    'blob_name': pdf_info['blob_name'],
                    'blob_url': pdf_info['blob_url'],  # Guardar también aquí como backup
                    'size_bytes': pdf_info['size_bytes'],
                    'uploaded_at': pdf_info['uploaded_at'],
                    'container': pdf_info['container']
                }
            
                # Guardar con campos específicos
                update_fields = ['pdf_file_url', 'analysis_data']
                if hasattr(report, 'pdf_azure_blob_name'):
                    update_fields.append('pdf_azure_blob_name')
                
                report.save(update_fields=update_fields)
                
                logger.info(f"✅ Report actualizado con PDF info")
                return True
            
        except Exception as e:
            logger.error(f"Error actualizando Report con PDF info: {e}")
            
    def _update_csvfile_with_dataframe_info(self, csv_file, dataframe_info: Dict[str, Any])-> bool:
        """Actualizar modelo CSVFile con información del DataFrame"""
        try:
            if not csv_file:
                return True  # No hay CSV, no es error
            
            with transaction.atomic():
                # Actualizar analysis_data
                if not csv_file.analysis_data:
                    csv_file.analysis_data = {}
            
                csv_file.analysis_data['azure_dataframe'] = {
                    'base_path': dataframe_info['base_path'],
                    'primary_url': dataframe_info.get('primary_url'),
                    'sample_url': dataframe_info.get('sample_url'),
                    'files': dataframe_info['files'],
                    'metadata': dataframe_info['metadata']
                }
                
                # Actualizar URL de Azure si no existe y cabe en el campo
                if not csv_file.azure_blob_url and dataframe_info.get('primary_url'):
                    url = dataframe_info['primary_url']
                    # Verificar longitud del campo azure_blob_url
                    if len(url) <= 200:  # Suponiendo que este campo también es de 200
                        csv_file.azure_blob_url = url
                        csv_file.azure_blob_name = dataframe_info['base_path']
                
                csv_file.save(update_fields=['analysis_data', 'azure_blob_url', 'azure_blob_name'])
                
                logger.info("✅ CSVFile actualizado con info DataFrame")
                return True
            
        except Exception as e:
            logger.error(f"Error actualizando CSVFile: {e}")
            return False
    
    def _extract_client_name(self, filename: str) -> str:
        """Extraer nombre del cliente del filename"""
        try:
            name_without_ext = filename.split('.')[0]
            parts = name_without_ext.replace('_', ' ').replace('-', ' ').split()
            
            exclude_words = {'recommendations', 'advisor', 'azure', 'report', 'data', 'export', 'csv', 'ejemplo', 'test'}
            client_parts = [part for part in parts if part.lower() not in exclude_words and len(part) > 1]
            
            if client_parts:
                return ' '.join(client_parts[:3]).upper()
            
            return "Azure Client"
            
        except Exception:
            return "Azure Client"
    
    def regenerate_report_pdf(self, report) -> Dict[str, Any]:
        """Regenerar solo el PDF de un reporte existente"""
        try:
            logger.info(f"Regenerando PDF para reporte {report.id}")
            
            # Generar HTML actualizado
            html_content, client_name = self._generate_html(report)
            if not html_content:
                return {'success': False, 'error': 'Error generando HTML'}
            
            # Generar PDF
            pdf_bytes, pdf_filename = self._generate_pdf(report, html_content)
            if not pdf_bytes:
                return {'success': False, 'error': 'Error generando PDF'}
            
            # Subir a Azure
            if self.azure_service and self.azure_service.is_available():
                pdf_info = self._upload_pdf_to_azure(pdf_bytes, report, client_name)
                if pdf_info:
                    update_success = self._update_report_with_pdf_info(report, pdf_info)
                    return {
                        'success': True,
                        'pdf_url': pdf_info['blob_url'],
                        'pdf_filename': pdf_filename,
                        'size_bytes': len(pdf_bytes),
                        'db_updated': update_success
                    }
            
            return {'success': False, 'error': 'Error subiendo PDF a Azure'}
            
        except Exception as e:
            logger.error(f"Error regenerando PDF: {e}")
            return {'success': False, 'error': str(e)}

# Instancia global del servicio
complete_report_service = CompleteReportService()

# Funciones de conveniencia
def generate_complete_report(report) -> Dict[str, Any]:
    """Generar reporte completo con PDF y Azure Storage"""
    return complete_report_service.generate_complete_report(report)

def regenerate_pdf(report) -> Dict[str, Any]:
    """Regenerar solo PDF de un reporte"""
    return complete_report_service.regenerate_report_pdf(report)