# apps/storage/services/__init__.py

# Importar servicios principales
from .azure_storage_service import AzureStorageService

# Importar generador de reportes actualizado (ReportLab)
try:
    from .report_service import ReportGenerator, generate_html_preview
    from .reportlab_generator import generate_azure_advisor_pdf
    REPORT_GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Report generator not available: {e}")
    print("Install with: pip install reportlab pillow")
    REPORT_GENERATOR_AVAILABLE = False
    
    # Crear clases dummy para evitar errores
    class ReportGenerator:
        def __init__(self, *args, **kwargs):
            pass
        def generate_pdf(self):
            raise ImportError("ReportLab not installed")
        def generate_html_preview(self):
            return "<html><body><h1>Error: ReportLab not installed</h1></body></html>"
    
    def generate_html_preview(*args, **kwargs):
        return "<html><body><h1>Error: ReportLab not installed</h1></body></html>"
    
    def generate_azure_advisor_pdf(*args, **kwargs):
        raise ImportError("ReportLab not installed")

# Exportar todo
__all__ = [
    'AzureStorageService',
    'ReportGenerator', 
    'generate_html_preview',
    'generate_azure_advisor_pdf',
    'REPORT_GENERATOR_AVAILABLE'
]