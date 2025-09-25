# apps/storage/services/reportlab_generator.py
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import Image as ReportLabImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib import colors
import logging

logger = logging.getLogger(__name__)

class AzureAdvisorPDFGenerator:
    """Generador de PDFs para reportes de Azure Advisor usando ReportLab"""
    
    def __init__(self, insights_data, client_name="Cliente", csv_filename=""):
        self.insights_data = insights_data
        self.client_name = client_name
        self.csv_filename = csv_filename
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Colores corporativos de Azure
        self.colors = {
            'primary': HexColor('#0066CC'),
            'secondary': HexColor('#6366F1'),
            'accent': HexColor('#10B981'),
            'dark': HexColor('#1F2937'),
            'light': HexColor('#F3F4F6'),
            'white': white,
            'gray': HexColor('#6B7280')
        }
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#0066CC'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceBefore=20,
            spaceAfter=15,
            textColor=HexColor('#1F2937'),
            fontName='Helvetica-Bold'
        ))
        
        # Texto de resumen
        self.styles.add(ParagraphStyle(
            name='SummaryText',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=10,
            textColor=HexColor('#374151'),
            fontName='Helvetica'
        ))
        
        # Texto de métricas
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=28,
            spaceBefore=5,
            spaceAfter=5,
            textColor=HexColor('#0066CC'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        # Texto de descripción de métrica
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=0,
            spaceAfter=15,
            textColor=HexColor('#6B7280'),
            fontName='Helvetica',
            alignment=TA_CENTER
        ))

    def generate_pdf(self):
        """Generar el PDF completo"""
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title=f"Azure Advisor Report - {self.client_name}"
        )
        
        # Construir el contenido
        story = []
        
        # Página de portada
        story.extend(self._build_cover_page())
        story.append(PageBreak())
        
        # Resumen ejecutivo
        story.extend(self._build_executive_summary())
        story.append(PageBreak())
        
        # Métricas principales
        story.extend(self._build_key_metrics())
        story.append(PageBreak())
        
        # Análisis por categorías
        story.extend(self._build_category_analysis())
        story.append(PageBreak())
        
        # Recomendaciones prioritarias
        story.extend(self._build_priority_recommendations())
        story.append(PageBreak())
        
        # Tabla detallada de recomendaciones
        story.extend(self._build_detailed_table())
        
        # Generar PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue()

    def _build_cover_page(self):
        """Construir página de portada"""
        story = []
        
        # Logo/Header (simulado con rectángulo)
        story.append(Spacer(1, 0.5*inch))
        
        # Título principal
        story.append(Paragraph("Azure Advisor Analyzer", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Cliente
        story.append(Paragraph(f"<b>{self.client_name}</b>", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Fecha del reporte
        today = datetime.now().strftime("%d de %B, %Y")
        story.append(Paragraph(f"Reporte generado el {today}", self.styles['SummaryText']))
        story.append(Spacer(1, 1*inch))
        
        # Resumen de métricas en la portada
        summary = self.insights_data.get('summary', {})
        total_recommendations = summary.get('total_recommendations', 0)
        advisor_score = self.insights_data.get('azure_advisor_score', 0)
        
        # Crear tabla de métricas destacadas
        cover_metrics = [
            ['Recomendaciones Totales', 'Puntuación Azure Advisor'],
            [str(total_recommendations), f"{advisor_score}/100"]
        ]
        
        cover_table = Table(cover_metrics, colWidths=[2.5*inch, 2.5*inch])
        cover_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 24),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['gray'])
        ]))
        
        story.append(cover_table)
        story.append(Spacer(1, 1*inch))
        
        # Descripción del reporte
        description = """
        Este reporte presenta un análisis detallado de las recomendaciones de Azure Advisor 
        para optimizar la seguridad, rendimiento, confiabilidad y costos de su infraestructura 
        en Microsoft Azure.
        """
        story.append(Paragraph(description, self.styles['SummaryText']))
        
        return story

    def _build_executive_summary(self):
        """Construir resumen ejecutivo"""
        story = []
        
        story.append(Paragraph("Resumen Ejecutivo", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        summary = self.insights_data.get('summary', {})
        cost_analysis = self.insights_data.get('cost_analysis', {})
        
        # Texto del resumen
        summary_text = f"""
        <b>Análisis de Infraestructura Azure</b><br/><br/>
        
        Se han identificado <b>{summary.get('total_recommendations', 0)} recomendaciones</b> 
        para optimizar su infraestructura Azure, distribuidas across 
        <b>{len(summary.get('categories', {}))}</b> categorías principales.<br/><br/>
        
        <b>Puntos Destacados:</b><br/>
        • Puntuación actual de Azure Advisor: <b>{self.insights_data.get('azure_advisor_score', 0)}/100</b><br/>
        • Ahorro mensual estimado: <b>${cost_analysis.get('estimated_monthly_savings', 0):,.2f}</b><br/>
        • Recursos únicos analizados: <b>{summary.get('unique_resources', 0)}</b><br/>
        • Categoría con más recomendaciones: <b>{self._get_top_category()}</b><br/><br/>
        
        <b>Recomendación Principal:</b><br/>
        Priorizar la implementación de las recomendaciones de seguridad de alto impacto 
        para mejorar la postura de seguridad general de la infraestructura.
        """
        
        story.append(Paragraph(summary_text, self.styles['SummaryText']))
        
        return story

    def _build_key_metrics(self):
        """Construir página de métricas clave"""
        story = []
        
        story.append(Paragraph("Métricas Principales", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.3*inch))
        
        summary = self.insights_data.get('summary', {})
        cost_analysis = self.insights_data.get('cost_analysis', {})
        
        # Crear grid de métricas 2x2
        metrics_data = [
            [
                self._create_metric_cell("Recomendaciones", str(summary.get('total_recommendations', 0))),
                self._create_metric_cell("Puntuación Advisor", f"{self.insights_data.get('azure_advisor_score', 0)}/100")
            ],
            [
                self._create_metric_cell("Ahorro Mensual", f"${cost_analysis.get('estimated_monthly_savings', 0):,.0f}"),
                self._create_metric_cell("Recursos Únicos", str(summary.get('unique_resources', 0)))
            ]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2.5*inch], rowHeights=[1.2*inch, 1.2*inch])
        metrics_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['light']),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['gray']),
            ('ROUNDEDCORNERS', [5, 5, 5, 5])
        ]))
        
        story.append(metrics_table)
        
        return story

    def _create_metric_cell(self, label, value):
        """Crear celda de métrica"""
        content = f"""
        <para alignment="center">
            <font size="24" color="#0066CC"><b>{value}</b></font><br/>
            <font size="10" color="#6B7280">{label}</font>
        </para>
        """
        return Paragraph(content, self.styles['Normal'])

    def _build_category_analysis(self):
        """Construir análisis por categorías"""
        story = []
        
        story.append(Paragraph("Análisis por Categorías", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        categories = self.insights_data.get('summary', {}).get('categories', {})
        
        if categories:
            # Crear tabla de categorías
            cat_data = [['Categoría', 'Recomendaciones', 'Porcentaje']]
            total_recs = sum(categories.values())
            
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_recs * 100) if total_recs > 0 else 0
                cat_data.append([
                    category.title(),
                    str(count),
                    f"{percentage:.1f}%"
                ])
            
            cat_table = Table(cat_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, self.colors['gray']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light']])
            ]))
            
            story.append(cat_table)
        
        return story

    def _build_priority_recommendations(self):
        """Construir recomendaciones prioritarias"""
        story = []
        
        story.append(Paragraph("Recomendaciones Prioritarias", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Obtener top 5 recomendaciones (simulado)
        priority_recs = [
            "Habilitar cifrado de disco para máquinas virtuales",
            "Configurar Azure Security Center",
            "Optimizar tamaño de máquinas virtuales",
            "Implementar Azure Backup",
            "Configurar monitoreo con Azure Monitor"
        ]
        
        for i, rec in enumerate(priority_recs[:5], 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['SummaryText']))
            story.append(Spacer(1, 0.1*inch))
        
        return story

    def _build_detailed_table(self):
        """Construir tabla detallada de recomendaciones"""
        story = []
        
        story.append(Paragraph("Detalle de Recomendaciones", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Datos de ejemplo (en producción vendría de insights_data)
        recs_data = [
            ['#', 'Categoría', 'Impacto', 'Recomendación', 'Recurso'],
            ['1', 'Seguridad', 'Alto', 'Habilitar cifrado', 'VM-001'],
            ['2', 'Costo', 'Medio', 'Redimensionar VM', 'VM-002'],
            ['3', 'Seguridad', 'Alto', 'Configurar NSG', 'Red-001'],
            ['4', 'Rendimiento', 'Bajo', 'Optimizar disco', 'Disk-001'],
            ['5', 'Confiabilidad', 'Medio', 'Configurar backup', 'VM-003']
        ]
        
        recs_table = Table(recs_data, 
                          colWidths=[0.4*inch, 1*inch, 0.8*inch, 2.5*inch, 1*inch])
        recs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['gray']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light']]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(recs_table)
        
        return story

    def _get_top_category(self):
        """Obtener la categoría con más recomendaciones"""
        categories = self.insights_data.get('summary', {}).get('categories', {})
        if categories:
            return max(categories, key=categories.get).title()
        return "Seguridad"


def generate_azure_advisor_pdf(insights_data, client_name="Cliente", csv_filename=""):
    """Función principal para generar PDF de Azure Advisor"""
    try:
        generator = AzureAdvisorPDFGenerator(insights_data, client_name, csv_filename)
        pdf_content = generator.generate_pdf()
        return pdf_content
    except Exception as e:
        logger.error(f"Error generando PDF: {str(e)}")
        raise