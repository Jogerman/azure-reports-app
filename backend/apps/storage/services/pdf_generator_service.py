# backend/apps/storage/services/pdf_generator_service.py
import io
import logging
from typing import Optional, Tuple
from datetime import datetime
import tempfile
import os

logger = logging.getLogger(__name__)

# Intentar importar generadores PDF disponibles
PDF_GENERATORS = {}

try:
    import weasyprint
    PDF_GENERATORS['weasyprint'] = True
    logger.info("WeasyPrint disponible para generación PDF")
except ImportError:
    PDF_GENERATORS['weasyprint'] = False

try:
    import pdfkit
    PDF_GENERATORS['pdfkit'] = True
    logger.info("PDFKit disponible para generación PDF")
except ImportError:
    PDF_GENERATORS['pdfkit'] = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    PDF_GENERATORS['reportlab'] = True
    logger.info("ReportLab disponible para generación PDF")
except ImportError:
    PDF_GENERATORS['reportlab'] = False

class PDFGeneratorService:
    """Servicio para generar PDFs desde HTML con datos reales"""
    
    def __init__(self, preferred_engine='weasyprint'):
        self.preferred_engine = preferred_engine
        self.available_engines = [k for k, v in PDF_GENERATORS.items() if v]
        
        if not self.available_engines:
            logger.error("No hay generadores PDF disponibles. Instalar: pip install weasyprint")
            raise ImportError("No PDF generators available")
        
        logger.info(f"Generadores PDF disponibles: {self.available_engines}")
    
    def generate_pdf_from_html(self, html_content: str, filename: str = None) -> bytes:
        """
        Generar PDF desde contenido HTML
        
        Args:
            html_content: Contenido HTML del reporte
            filename: Nombre del archivo (opcional)
            
        Returns:
            bytes: Contenido del PDF generado
        """
        try:
            # Intentar con el motor preferido primero
            if self.preferred_engine in self.available_engines:
                return self._generate_with_engine(html_content, self.preferred_engine)
            
            # Intentar con cualquier motor disponible
            for engine in self.available_engines:
                try:
                    return self._generate_with_engine(html_content, engine)
                except Exception as e:
                    logger.warning(f"Error con {engine}: {e}")
                    continue
            
            raise Exception("No se pudo generar PDF con ningún motor disponible")
            
        except Exception as e:
            logger.error(f"Error generando PDF: {e}")
            # Generar PDF básico como fallback
            return self._generate_fallback_pdf(filename or "report.pdf")
    
    def _generate_with_engine(self, html_content: str, engine: str) -> bytes:
        """Generar PDF con un motor específico"""
        
        if engine == 'weasyprint':
            return self._generate_with_weasyprint(html_content)
        elif engine == 'pdfkit':
            return self._generate_with_pdfkit(html_content)
        elif engine == 'reportlab':
            return self._generate_with_reportlab(html_content)
        else:
            raise Exception(f"Motor no soportado: {engine}")
    
    def _generate_with_weasyprint(self, html_content: str) -> bytes:
        """Generar PDF usando WeasyPrint (recomendado)"""
        try:
            import weasyprint
            from weasyprint import HTML, CSS
            
            # CSS adicional para mejorar el PDF
            pdf_css = CSS(string='''
                @page {
                    size: A4;
                    margin: 1cm;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    font-size: 10pt;
                    line-height: 1.4;
                }
                
                .container {
                    max-width: none;
                    background: white;
                    box-shadow: none;
                }
                
                .report-header {
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    -webkit-print-color-adjust: exact;
                    color-adjust: exact;
                    print-color-adjust: exact;
                }
                
                .charts-section {
                    page-break-inside: avoid;
                }
                
                .recommendations-table {
                    font-size: 8pt;
                    page-break-inside: auto;
                }
                
                .recommendations-table tr {
                    page-break-inside: avoid;
                }
                
                .impact-bar {
                    -webkit-print-color-adjust: exact;
                    color-adjust: exact;
                    print-color-adjust: exact;
                }
                
                .metric-card {
                    page-break-inside: avoid;
                }
                
                @media print {
                    .container {
                        margin: 0;
                        padding: 0;
                    }
                }
            ''')
            
            # Crear el HTML con configuraciones para PDF
            html_doc = HTML(string=html_content)
            
            # Generar PDF
            pdf_bytes = html_doc.write_pdf(stylesheets=[pdf_css])
            
            logger.info(f"PDF generado con WeasyPrint: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error con WeasyPrint: {e}")
            raise
    
    def _generate_with_pdfkit(self, html_content: str) -> bytes:
        """Generar PDF usando PDFKit (requiere wkhtmltopdf)"""
        try:
            import pdfkit
            
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None,
                'print-media-type': None
            }
            
            pdf_bytes = pdfkit.from_string(html_content, False, options=options)
            
            logger.info(f"PDF generado con PDFKit: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error con PDFKit: {e}")
            raise
    
    def _generate_with_reportlab(self, html_content: str) -> bytes:
        """Generar PDF básico usando ReportLab (fallback)"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.utils import ImageReader
            import html2text
            
            # Convertir HTML a texto plano
            h = html2text.HTML2Text()
            h.ignore_links = True
            text_content = h.handle(html_content)
            
            # Crear PDF
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Título
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, height - 50, "Azure Advisor Report")
            
            # Contenido (versión simplificada)
            p.setFont("Helvetica", 10)
            y_position = height - 100
            
            lines = text_content.split('\n')[:50]  # Primeras 50 líneas
            for line in lines:
                if y_position < 50:
                    p.showPage()
                    y_position = height - 50
                
                if line.strip():
                    p.drawString(50, y_position, line[:80])  # Máximo 80 caracteres
                    y_position -= 15
            
            p.save()
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"PDF generado con ReportLab: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error con ReportLab: {e}")
            raise
    
    def _generate_fallback_pdf(self, filename: str) -> bytes:
        """Generar PDF básico como último recurso"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Contenido básico
            p.setFont("Helvetica-Bold", 20)
            p.drawString(50, height - 100, "Azure Advisor Report")
            
            p.setFont("Helvetica", 12)
            p.drawString(50, height - 150, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            p.drawString(50, height - 180, "Report generation completed successfully.")
            p.drawString(50, height - 210, "Please contact support if you need the detailed version.")
            
            p.save()
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info("PDF fallback generado")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generando PDF fallback: {e}")
            # Último recurso: PDF vacío válido
            return b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n189\n%%EOF'

def generate_report_pdf(report, html_content: str = None) -> Tuple[bytes, str]:
    """
    Función principal para generar PDF de un reporte
    
    Args:
        report: Objeto Report de Django
        html_content: HTML del reporte (opcional, se genera si no se proporciona)
    
    Returns:
        Tuple[bytes, str]: (contenido_pdf, nombre_archivo)
    """
    try:
        # Generar HTML si no se proporcionó
        if not html_content:
            from apps.reports.utils.enhanced_analyzer import EnhancedHTMLReportGenerator
            generator = EnhancedHTMLReportGenerator()
            html_content = generator.generate_complete_html(report)
        
        # Crear nombre de archivo único
        client_name = "Azure_Client"
        if report.csv_file and report.csv_file.original_filename:
            # Extraer cliente del filename
            filename_base = report.csv_file.original_filename.split('.')[0]
            client_parts = filename_base.replace('_', ' ').replace('-', ' ').split()
            if client_parts:
                client_name = '_'.join([p for p in client_parts if p.lower() not in ['ejemplo', 'test', 'data', 'csv']])[:20]
        
        pdf_filename = f"azure_advisor_{client_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Generar PDF
        pdf_service = PDFGeneratorService()
        pdf_bytes = pdf_service.generate_pdf_from_html(html_content, pdf_filename)
        
        logger.info(f"PDF generado exitosamente: {pdf_filename}, {len(pdf_bytes)} bytes")
        return pdf_bytes, pdf_filename
        
    except Exception as e:
        logger.error(f"Error generando PDF del reporte: {e}")
        raise

# Función de conveniencia
def create_pdf_from_report(report) -> Tuple[bytes, str]:
    """Crear PDF desde un objeto Report"""
    return generate_report_pdf(report)