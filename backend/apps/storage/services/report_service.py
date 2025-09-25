# apps/storage/services/report_service.py
from io import BytesIO
from datetime import datetime
import logging
from django.template.loader import render_to_string

# Importar el nuevo generador de ReportLab
try:
    from .reportlab_generator import generate_azure_advisor_pdf
    PDF_GENERATOR_AVAILABLE = True
except ImportError:
    PDF_GENERATOR_AVAILABLE = False
    logging.warning("ReportLab no disponible. Instala con: pip install reportlab")

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generador de reportes mejorado con soporte para ReportLab"""
    
    def __init__(self, insights_data, client_name="Cliente", csv_filename=""):
        self.insights_data = insights_data
        self.client_name = client_name
        self.csv_filename = csv_filename

    def generate_pdf(self):
        """Generar PDF usando ReportLab"""
        if not PDF_GENERATOR_AVAILABLE:
            raise ImportError(
                "ReportLab no está disponible. "
                "Instala con: pip install reportlab pillow"
            )
        
        try:
            pdf_content = generate_azure_advisor_pdf(
                self.insights_data,
                self.client_name,
                self.csv_filename
            )
            return pdf_content
        except Exception as e:
            logger.error(f"Error generando PDF: {str(e)}")
            raise

    def generate_html_preview(self):
        """Generar vista previa HTML mejorada"""
        try:
            summary = self.insights_data.get('summary', {})
            cost_analysis = self.insights_data.get('cost_analysis', {})
            
            context = {
                'client_name': self.client_name,
                'csv_filename': self.csv_filename,
                'generated_date': datetime.now().strftime('%d de %B, %Y'),
                'insights_data': self.insights_data,
                'summary': summary,
                'cost_analysis': cost_analysis,
                'azure_advisor_score': self.insights_data.get('azure_advisor_score', 0),
                'total_recommendations': summary.get('total_recommendations', 0),
                'categories': summary.get('categories', {}),
                'estimated_savings': cost_analysis.get('estimated_monthly_savings', 0),
                'unique_resources': summary.get('unique_resources', 0),
            }
            
            # Usar template HTML mejorado
            html_content = render_to_string('reports/azure_advisor_preview.html', context)
            return html_content
            
        except Exception as e:
            logger.error(f"Error generando vista previa HTML: {str(e)}")
            # Generar HTML básico como fallback
            return self._generate_basic_html()

    def _generate_basic_html(self):
        """Generar HTML básico como fallback"""
        summary = self.insights_data.get('summary', {})
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Azure Advisor Report - {self.client_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #0066CC; color: white; padding: 20px; text-align: center; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
                .recommendations {{ margin-top: 20px; }}
                .category {{ margin: 10px 0; padding: 10px; border-left: 4px solid #0066CC; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Azure Advisor Analyzer</h1>
                <h2>{self.client_name}</h2>
                <p>Reporte generado el {datetime.now().strftime('%d/%m/%Y')}</p>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <h3>{summary.get('total_recommendations', 0)}</h3>
                    <p>Recomendaciones Totales</p>
                </div>
                <div class="metric">
                    <h3>{self.insights_data.get('azure_advisor_score', 0)}/100</h3>
                    <p>Puntuación Azure Advisor</p>
                </div>
                <div class="metric">
                    <h3>${self.insights_data.get('cost_analysis', {}).get('estimated_monthly_savings', 0):,.0f}</h3>
                    <p>Ahorro Mensual Estimado</p>
                </div>
            </div>
            
            <div class="recommendations">
                <h3>Distribución por Categorías</h3>
        """
        
        # Agregar categorías
        categories = summary.get('categories', {})
        for category, count in categories.items():
            html += f"""
                <div class="category">
                    <strong>{category.title()}:</strong> {count} recomendaciones
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html


# Función de conveniencia para compatibilidad
def generate_html_preview(insights_data, client_name="Cliente", csv_filename=""):
    """Función para generar vista previa HTML"""
    generator = ReportGenerator(insights_data, client_name, csv_filename)
    return generator.generate_html_preview()


class EnhancedAzureHTMLReportGenerator:
    """Generador HTML mejorado para reportes de Azure Advisor"""
    
    def __init__(self, insights_data, client_name="Cliente", csv_filename=""):
        self.insights_data = insights_data
        self.client_name = client_name
        self.csv_filename = csv_filename

    def generate_html_preview(self):
        """Generar vista previa HTML completa y moderna"""
        return self._generate_modern_html()

    def _generate_modern_html(self):
        """Generar HTML moderno con diseño mejorado"""
        summary = self.insights_data.get('summary', {})
        cost_analysis = self.insights_data.get('cost_analysis', {})
        categories = summary.get('categories', {})
        
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Azure Advisor Report - {self.client_name}</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    line-height: 1.6; color: #333; background: #f8f9fa;
                }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{ 
                    background: linear-gradient(135deg, #0066CC, #6366F1); 
                    color: white; padding: 40px 20px; text-align: center; 
                    border-radius: 10px; margin-bottom: 30px;
                }}
                .header h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
                .header h2 {{ font-size: 1.8rem; margin-bottom: 5px; opacity: 0.9; }}
                .header p {{ opacity: 0.8; }}
                
                .metrics-grid {{ 
                    display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                    gap: 20px; margin-bottom: 30px; 
                }}
                .metric-card {{ 
                    background: white; padding: 25px; border-radius: 10px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center;
                }}
                .metric-value {{ 
                    font-size: 2.5rem; font-weight: bold; 
                    color: #0066CC; margin-bottom: 5px; 
                }}
                .metric-label {{ color: #666; font-size: 0.9rem; }}
                
                .section {{ 
                    background: white; margin-bottom: 20px; 
                    border-radius: 10px; padding: 25px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .section h3 {{ 
                    color: #0066CC; margin-bottom: 20px; 
                    font-size: 1.5rem; border-bottom: 2px solid #e9ecef; 
                    padding-bottom: 10px;
                }}
                
                .categories-grid {{ 
                    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 15px; 
                }}
                .category-item {{ 
                    padding: 15px; background: #f8f9fa; 
                    border-radius: 8px; border-left: 4px solid #0066CC;
                }}
                .category-name {{ font-weight: bold; color: #333; }}
                .category-count {{ color: #666; font-size: 0.9rem; }}
                
                .score-circle {{ 
                    width: 120px; height: 120px; border-radius: 50%; 
                    background: conic-gradient(#0066CC 0deg, #0066CC {self.insights_data.get('azure_advisor_score', 0) * 3.6}deg, #e9ecef {self.insights_data.get('azure_advisor_score', 0) * 3.6}deg 360deg);
                    display: flex; align-items: center; justify-content: center;
                    margin: 0 auto 20px; position: relative;
                }}
                .score-inner {{ 
                    width: 90px; height: 90px; background: white; 
                    border-radius: 50%; display: flex; align-items: center; 
                    justify-content: center; flex-direction: column;
                }}
                .score-number {{ font-size: 1.8rem; font-weight: bold; color: #0066CC; }}
                .score-label {{ font-size: 0.7rem; color: #666; }}
                
                .recommendations {{ margin-top: 20px; }}
                .recommendation-item {{ 
                    padding: 15px; margin-bottom: 10px; 
                    background: #f8f9fa; border-radius: 8px; 
                    border-left: 4px solid #10B981;
                }}
                .recommendation-item.high {{ border-left-color: #EF4444; }}
                .recommendation-item.medium {{ border-left-color: #F59E0B; }}
                .recommendation-item.low {{ border-left-color: #10B981; }}
                
                .priority-badge {{ 
                    display: inline-block; padding: 4px 8px; 
                    border-radius: 4px; font-size: 0.8rem; 
                    font-weight: bold; margin-bottom: 5px;
                }}
                .priority-high {{ background: #FEE2E2; color: #DC2626; }}
                .priority-medium {{ background: #FEF3C7; color: #D97706; }}
                .priority-low {{ background: #D1FAE5; color: #065F46; }}
                
                @media print {{
                    body {{ background: white; }}
                    .container {{ max-width: none; padding: 0; }}
                    .section {{ box-shadow: none; border: 1px solid #ddd; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <h1>Azure Advisor Analyzer</h1>
                    <h2>{self.client_name}</h2>
                    <p>Reporte generado el {datetime.now().strftime('%d de %B, %Y')}</p>
                    <p>Archivo analizado: {self.csv_filename}</p>
                </div>

                <!-- Métricas principales -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{summary.get('total_recommendations', 0)}</div>
                        <div class="metric-label">Recomendaciones Totales</div>
                    </div>
                    <div class="metric-card">
                        <div class="score-circle">
                            <div class="score-inner">
                                <div class="score-number">{self.insights_data.get('azure_advisor_score', 0)}</div>
                                <div class="score-label">/ 100</div>
                            </div>
                        </div>
                        <div class="metric-label">Puntuación Azure Advisor</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${cost_analysis.get('estimated_monthly_savings', 0):,.0f}</div>
                        <div class="metric-label">Ahorro Mensual Estimado</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{summary.get('unique_resources', 0)}</div>
                        <div class="metric-label">Recursos Únicos</div>
                    </div>
                </div>

                <!-- Resumen Ejecutivo -->
                <div class="section">
                    <h3>📊 Resumen Ejecutivo</h3>
                    <p>Se han identificado <strong>{summary.get('total_recommendations', 0)} recomendaciones</strong> 
                    para optimizar su infraestructura Azure, distribuidas en <strong>{len(categories)}</strong> 
                    categorías principales.</p>
                    
                    <p style="margin-top: 15px;">Con una puntuación actual de Azure Advisor de 
                    <strong>{self.insights_data.get('azure_advisor_score', 0)}/100</strong>, 
                    existe un potencial de ahorro mensual estimado de 
                    <strong>${cost_analysis.get('estimated_monthly_savings', 0):,.2f}</strong>.</p>
                </div>

                <!-- Distribución por Categorías -->
                <div class="section">
                    <h3>🎯 Distribución por Categorías</h3>
                    <div class="categories-grid">"""

        # Agregar categorías dinámicamente
        total_recs = sum(categories.values()) if categories else 1
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_recs * 100) if total_recs > 0 else 0
            html += f"""
                        <div class="category-item">
                            <div class="category-name">{category.title()}</div>
                            <div class="category-count">{count} recomendaciones ({percentage:.1f}%)</div>
                        </div>"""

        html += """
                    </div>
                </div>

                <!-- Recomendaciones Prioritarias -->
                <div class="section">
                    <h3>⚡ Recomendaciones Prioritarias</h3>
                    <div class="recommendations">"""

        # Agregar recomendaciones prioritarias (ejemplo)
        priority_recommendations = [
            {"title": "Habilitar cifrado de disco para máquinas virtuales", "priority": "high", "impact": "Seguridad crítica"},
            {"title": "Configurar Azure Security Center Standard", "priority": "high", "impact": "Protección avanzada"},
            {"title": "Optimizar tamaño de máquinas virtuales subutilizadas", "priority": "medium", "impact": "Reducción de costos"},
            {"title": "Implementar Azure Backup para recursos críticos", "priority": "medium", "impact": "Continuidad del negocio"},
            {"title": "Configurar monitoreo con Azure Monitor", "priority": "low", "impact": "Visibilidad operacional"}
        ]

        for i, rec in enumerate(priority_recommendations, 1):
            html += f"""
                        <div class="recommendation-item {rec['priority']}">
                            <span class="priority-badge priority-{rec['priority']}">{rec['priority'].upper()}</span>
                            <div><strong>{i}. {rec['title']}</strong></div>
                            <div style="color: #666; font-size: 0.9rem; margin-top: 5px;">{rec['impact']}</div>
                        </div>"""

        html += """
                    </div>
                </div>

                <!-- Análisis de Costos -->
                <div class="section">
                    <h3>💰 Análisis de Costos</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                        <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                            <div style="font-size: 1.5rem; color: #10B981; font-weight: bold;">
                                ${cost_analysis.get('estimated_monthly_savings', 0):,.0f}
                            </div>
                            <div style="color: #666; font-size: 0.9rem;">Ahorro Mensual</div>
                        </div>
                        <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                            <div style="font-size: 1.5rem; color: #0066CC; font-weight: bold;">
                                ${cost_analysis.get('estimated_monthly_savings', 0) * 12:,.0f}
                            </div>
                            <div style="color: #666; font-size: 0.9rem;">Ahorro Anual</div>
                        </div>
                    </div>
                </div>

                <!-- Próximos Pasos -->
                <div class="section">
                    <h3>🎯 Próximos Pasos Recomendados</h3>
                    <ol style="padding-left: 20px; line-height: 1.8;">
                        <li><strong>Revisar recomendaciones de alta prioridad</strong> - Implementar medidas de seguridad críticas</li>
                        <li><strong>Optimizar costos</strong> - Redimensionar recursos subutilizados</li>
                        <li><strong>Implementar monitoreo</strong> - Configurar alertas y métricas</li>
                        <li><strong>Planificar backup</strong> - Asegurar continuidad del negocio</li>
                        <li><strong>Revisión mensual</strong> - Establecer proceso de mejora continua</li>
                    </ol>
                </div>

                <!-- Footer -->
                <div style="text-align: center; margin-top: 40px; padding: 20px; color: #666; border-top: 1px solid #ddd;">
                    <p>Generado por Azure Advisor Analyzer - {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    <p style="font-size: 0.8rem; margin-top: 5px;">
                        Este reporte se basa en el análisis de datos de Azure Advisor y proporciona recomendaciones para optimizar su infraestructura.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html