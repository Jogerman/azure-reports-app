# backend/apps/reports/utils/specialized_html_generators.py
"""
Generadores HTML especializados para cada tipo de reporte
Basados en el diseño del ejemplo PDF
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from .specialized_analyzers import SecurityAnalyzer, PerformanceAnalyzer, CostAnalyzer
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SpecializedHTMLGenerator:
    """Clase base para generadores HTML especializados"""
    
    def __init__(self, report, analysis_data=None):
        self.report = report
        self.analysis_data = analysis_data or {}
        self.client_name = self._extract_client_name()
        self.generated_date = datetime.now().strftime('%A, %B %d, %Y')
    
    def _extract_client_name(self) -> str:
        """Extraer nombre del cliente desde el filename del CSV"""
        if self.report.csv_file and self.report.csv_file.original_filename:
            filename = self.report.csv_file.original_filename
            # Extraer nombre del cliente (asumiendo formato como "CONTOSO.csv" o "cliente_data.csv")
            base_name = filename.split('.')[0].replace('_', ' ').replace('-', ' ')
            words = base_name.split()
            # Filtrar palabras comunes y tomar las primeras palabras válidas
            filtered_words = [w for w in words if w.lower() not in ['data', 'csv', 'example', 'test', 'sample']]
            if filtered_words:
                return ' '.join(filtered_words[:2]).upper()  # Máximo 2 palabras
        return "AZURE CLIENT"
    
    def _get_base_styles(self) -> str:
        """Estilos CSS base para todos los reportes"""
        return """
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                min-height: 100vh;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
                position: relative;
            }
            
            .logo {
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 20px;
            }
            
            .cloud-icon {
                width: 60px;
                height: 60px;
                background: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 20px;
                font-size: 24px;
                color: #667eea;
            }
            
            .company-name {
                font-size: 36px;
                font-weight: bold;
                margin: 0;
            }
            
            .report-title {
                font-size: 48px;
                font-weight: 300;
                margin: 20px 0;
                letter-spacing: 2px;
            }
            
            .client-name {
                font-size: 72px;
                font-weight: bold;
                margin: 30px 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .date-info {
                position: absolute;
                bottom: 20px;
                right: 40px;
                font-size: 14px;
                opacity: 0.9;
            }
            
            .content {
                padding: 40px;
            }
            
            .section {
                margin-bottom: 40px;
            }
            
            .section-header {
                display: flex;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 15px;
                border-bottom: 3px solid #e0e0e0;
            }
            
            .section-icon {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 20px;
                font-size: 24px;
                color: white;
            }
            
            .security-icon {
                background: linear-gradient(135deg, #667eea, #764ba2);
            }
            
            .performance-icon {
                background: linear-gradient(135deg, #f093fb, #f5576c);
            }
            
            .cost-icon {
                background: linear-gradient(135deg, #4facfe, #00f2fe);
            }
            
            .section-title {
                font-size: 32px;
                font-weight: bold;
                color: #333;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 30px;
                margin: 30px 0;
            }
            
            .metric-card {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
            }
            
            .metric-value {
                font-size: 48px;
                font-weight: bold;
                color: #667eea;
                margin: 15px 0;
            }
            
            .metric-label {
                font-size: 14px;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 10px;
            }
            
            .chart-container {
                background: white;
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .recommendations-table {
                width: 100%;
                border-collapse: collapse;
                margin: 30px 0;
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .recommendations-table th {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .recommendations-table td {
                padding: 15px;
                border-bottom: 1px solid #e0e0e0;
                vertical-align: top;
            }
            
            .recommendations-table tr:nth-child(even) {
                background: #f8f9fa;
            }
            
            .impact-high {
                background: #dc3545;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }
            
            .impact-medium {
                background: #ffc107;
                color: #333;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }
            
            .impact-low {
                background: #28a745;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }
            
            .score-container {
                text-align: center;
                margin: 30px 0;
            }
            
            .score-circle {
                display: inline-block;
                width: 150px;
                height: 150px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea, #764ba2);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 36px;
                font-weight: bold;
                margin: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            
            .summary-box {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
                border-left: 5px solid #667eea;
            }
            
            .summary-title {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin-bottom: 15px;
            }
            
            .summary-text {
                font-size: 16px;
                line-height: 1.6;
                color: #555;
            }
            
            .footer {
                background: #333;
                color: white;
                text-align: center;
                padding: 20px;
                margin-top: 50px;
            }
            
            @media print {
                body {
                    background: white;
                }
                
                .container {
                    box-shadow: none;
                }
                
                .metric-card:hover {
                    transform: none;
                }
            }
        </style>
        """

class SecurityHTMLGenerator(SpecializedHTMLGenerator):
    """Generador HTML especializado para reportes de seguridad"""
    
    def generate_html(self) -> str:
        """Generar HTML completo para reporte de seguridad"""
        try:
            # Obtener datos del análisis
            dashboard_metrics = self.analysis_data.get('dashboard_metrics', {})
            basic_metrics = self.analysis_data.get('basic_metrics', {})
            compliance_gaps = self.analysis_data.get('compliance_gaps', {})
            priority_recommendations = self.analysis_data.get('priority_recommendations', [])
            
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Análisis de Seguridad - {self.client_name}</title>
                {self._get_base_styles()}
            </head>
            <body>
                <div class="container">
                    {self._generate_header("SECURITY OPTIMIZATION", "🔒")}
                    
                    <div class="content">
                        {self._generate_security_metrics(dashboard_metrics, basic_metrics)}
                        {self._generate_compliance_analysis(compliance_gaps)}
                        {self._generate_priority_recommendations(priority_recommendations)}
                        {self._generate_security_summary(dashboard_metrics)}
                    </div>
                    
                    {self._generate_footer()}
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error generando HTML de seguridad: {e}")
            return self._generate_error_html("Error generando reporte de seguridad")
    
    def _generate_header(self, title: str, icon: str) -> str:
        """Generar header del reporte"""
        return f"""
        <div class="header">
            <div class="logo">
                <div class="cloud-icon">☁️</div>
                <h1 class="company-name">The Cloud Mastery</h1>
            </div>
            <h2 class="report-title">Azure Advisor Analyzer</h2>
            <h1 class="client-name">{self.client_name}</h1>
            <div class="date-info">Data retrieved on {self.generated_date}</div>
        </div>
        """
    
    def _generate_security_metrics(self, dashboard_metrics: Dict, basic_metrics: Dict) -> str:
        """Generar métricas de seguridad"""
        total_actions = dashboard_metrics.get('total_actions', 0)
        critical_issues = dashboard_metrics.get('critical_issues', 0)
        security_score = dashboard_metrics.get('security_score', 0)
        working_hours = dashboard_metrics.get('working_hours', 0)
        risk_level = dashboard_metrics.get('risk_level', 'Unknown')
        
        return f"""
        <div class="section">
            <div class="section-header">
                <div class="section-icon security-icon">🔒</div>
                <h2 class="section-title">Security Optimization</h2>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{total_actions}</div>
                    <div class="metric-label">Actions To Take</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color: #dc3545;">{critical_issues}</div>
                    <div class="metric-label">Critical Issues</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{working_hours}</div>
                    <div class="metric-label">Working Hours</div>
                </div>
            </div>
            
            <div class="score-container">
                <div class="score-circle">
                    <div>
                        <div style="font-size: 48px;">{security_score}</div>
                        <div style="font-size: 14px;">Security Score</div>
                    </div>
                </div>
                <div class="metric-label">Risk Level: <strong>{risk_level}</strong></div>
            </div>
        </div>
        """
    
    def _generate_compliance_analysis(self, compliance_gaps: Dict) -> str:
        """Generar análisis de cumplimiento"""
        encryption_gaps = compliance_gaps.get('encryption_gaps', 0)
        access_control = compliance_gaps.get('access_control_issues', 0)
        monitoring_gaps = compliance_gaps.get('monitoring_gaps', 0)
        network_security = compliance_gaps.get('network_security_issues', 0)
        
        return f"""
        <div class="section">
            <h3 style="font-size: 24px; margin-bottom: 20px; color: #333;">Compliance Gap Analysis</h3>
            
            <div class="chart-container">
                <div class="metrics-grid" style="grid-template-columns: repeat(2, 1fr);">
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #dc3545; font-weight: bold;">{encryption_gaps}</div>
                        <div style="font-size: 14px; color: #666;">Encryption Issues</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #ffc107; font-weight: bold;">{access_control}</div>
                        <div style="font-size: 14px; color: #666;">Access Control Issues</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #17a2b8; font-weight: bold;">{monitoring_gaps}</div>
                        <div style="font-size: 14px; color: #666;">Monitoring Gaps</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #6f42c1; font-weight: bold;">{network_security}</div>
                        <div style="font-size: 14px; color: #666;">Network Security Issues</div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_priority_recommendations(self, recommendations: List[Dict]) -> str:
        """Generar tabla de recomendaciones prioritarias"""
        if not recommendations:
            return ""
        
        table_rows = ""
        for rec in recommendations[:10]:  # Top 10
            impact_class = f"impact-{rec.get('business_impact', 'low').lower()}"
            table_rows += f"""
            <tr>
                <td>{rec.get('resource_type', 'N/A')}</td>
                <td>{rec.get('recommendation', 'N/A')[:100]}...</td>
                <td><span class="{impact_class}">{rec.get('business_impact', 'Low')}</span></td>
            </tr>
            """
        
        return f"""
        <div class="section">
            <h3 style="font-size: 24px; margin-bottom: 20px; color: #333;">Priority Security Recommendations</h3>
            
            <table class="recommendations-table">
                <thead>
                    <tr>
                        <th>Resource Type</th>
                        <th>Recommendation</th>
                        <th>Business Impact</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_security_summary(self, dashboard_metrics: Dict) -> str:
        """Generar resumen de seguridad"""
        total_actions = dashboard_metrics.get('total_actions', 0)
        risk_level = dashboard_metrics.get('risk_level', 'Unknown')
        security_score = dashboard_metrics.get('security_score', 0)
        
        summary_text = f"""
        El análisis de seguridad de Azure Advisor ha identificado <strong>{total_actions} recomendaciones</strong> 
        para mejorar la postura de seguridad de su infraestructura. Con un nivel de riesgo actual de <strong>{risk_level}</strong> 
        y una puntuación de seguridad de <strong>{security_score}/100</strong>, es fundamental implementar las 
        recomendaciones de alta prioridad para reducir la exposición a amenazas.
        """
        
        return f"""
        <div class="summary-box">
            <div class="summary-title">Resumen Ejecutivo</div>
            <div class="summary-text">{summary_text}</div>
        </div>
        """
    
    def _generate_footer(self) -> str:
        """Generar footer del reporte"""
        return f"""
        <div class="footer">
            <p>© 2025 The Cloud Mastery - Azure Security Analysis Report</p>
            <p>Generated on {self.generated_date}</p>
        </div>
        """
    
    def _generate_error_html(self, error_message: str) -> str:
        """Generar HTML de error"""
        return f"""
        <!DOCTYPE html>
        <html><head><title>Error</title></head>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>Error en Reporte de Seguridad</h1>
            <p>{error_message}</p>
        </body></html>
        """


class PerformanceHTMLGenerator(SpecializedHTMLGenerator):
    """Generador HTML especializado para reportes de rendimiento"""
    
    def generate_html(self) -> str:
        """Generar HTML completo para reporte de rendimiento"""
        try:
            dashboard_metrics = self.analysis_data.get('dashboard_metrics', {})
            basic_metrics = self.analysis_data.get('basic_metrics', {})
            optimization_opportunities = self.analysis_data.get('optimization_opportunities', {})
            bottlenecks = self.analysis_data.get('bottleneck_analysis', [])
            
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Análisis de Rendimiento - {self.client_name}</title>
                {self._get_base_styles()}
            </head>
            <body>
                <div class="container">
                    {self._generate_header("PERFORMANCE OPTIMIZATION", "⚡")}
                    
                    <div class="content">
                        {self._generate_performance_metrics(dashboard_metrics, basic_metrics)}
                        {self._generate_optimization_analysis(optimization_opportunities)}
                        {self._generate_bottlenecks_analysis(bottlenecks)}
                        {self._generate_performance_summary(dashboard_metrics)}
                    </div>
                    
                    {self._generate_footer()}
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error generando HTML de rendimiento: {e}")
            return self._generate_error_html("Error generando reporte de rendimiento")
    
    def _generate_header(self, title: str, icon: str) -> str:
        """Generar header del reporte"""
        return f"""
        <div class="header">
            <div class="logo">
                <div class="cloud-icon">☁️</div>
                <h1 class="company-name">The Cloud Mastery</h1>
            </div>
            <h2 class="report-title">Azure Advisor Analyzer</h2>
            <h1 class="client-name">{self.client_name}</h1>
            <div class="date-info">Data retrieved on {self.generated_date}</div>
        </div>
        """
    
    def _generate_performance_metrics(self, dashboard_metrics: Dict, basic_metrics: Dict) -> str:
        """Generar métricas de rendimiento"""
        total_actions = dashboard_metrics.get('total_actions', 0)
        critical_optimizations = dashboard_metrics.get('critical_optimizations', 0)
        performance_score = dashboard_metrics.get('performance_score', 100)
        optimization_potential = dashboard_metrics.get('optimization_potential', 0)
        working_hours = dashboard_metrics.get('working_hours', 0)
        efficiency_rating = dashboard_metrics.get('efficiency_rating', 'Good')
        
        return f"""
        <div class="section">
            <div class="section-header">
                <div class="section-icon performance-icon">⚡</div>
                <h2 class="section-title">Performance Optimization</h2>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{total_actions}</div>
                    <div class="metric-label">Optimization Actions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color: #f5576c;">{critical_optimizations}</div>
                    <div class="metric-label">Critical Optimizations</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{optimization_potential}%</div>
                    <div class="metric-label">Performance Improvement</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{working_hours}</div>
                    <div class="metric-label">Working Hours</div>
                </div>
            </div>
            
            <div class="score-container">
                <div class="score-circle" style="background: linear-gradient(135deg, #f093fb, #f5576c);">
                    <div>
                        <div style="font-size: 48px;">{performance_score}</div>
                        <div style="font-size: 14px;">Performance Score</div>
                    </div>
                </div>
                <div class="metric-label">Efficiency Rating: <strong>{efficiency_rating}</strong></div>
            </div>
        </div>
        """
    
    def _generate_optimization_analysis(self, opportunities: Dict) -> str:
        """Generar análisis de oportunidades de optimización"""
        compute_opt = opportunities.get('compute_optimization', 0)
        storage_opt = opportunities.get('storage_optimization', 0)
        network_opt = opportunities.get('network_optimization', 0)
        scaling_opt = opportunities.get('scaling_opportunities', 0)
        
        return f"""
        <div class="section">
            <h3 style="font-size: 24px; margin-bottom: 20px; color: #333;">Optimization Opportunities</h3>
            
            <div class="chart-container">
                <div class="metrics-grid" style="grid-template-columns: repeat(2, 1fr);">
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #f5576c; font-weight: bold;">{compute_opt}</div>
                        <div style="font-size: 14px; color: #666;">Compute Optimizations</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #f093fb; font-weight: bold;">{storage_opt}</div>
                        <div style="font-size: 14px; color: #666;">Storage Optimizations</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #667eea; font-weight: bold;">{network_opt}</div>
                        <div style="font-size: 14px; color: #666;">Network Optimizations</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #764ba2; font-weight: bold;">{scaling_opt}</div>
                        <div style="font-size: 14px; color: #666;">Scaling Opportunities</div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_bottlenecks_analysis(self, bottlenecks: List[Dict]) -> str:
        """Generar análisis de cuellos de botella"""
        if not bottlenecks:
            return ""
        
        table_rows = ""
        for bottleneck in bottlenecks[:5]:  # Top 5
            table_rows += f"""
            <tr>
                <td>{bottleneck.get('resource_type', 'N/A')}</td>
                <td>{bottleneck.get('recommendation', 'N/A')[:100]}...</td>
                <td>{bottleneck.get('estimated_improvement', 'N/A')}</td>
            </tr>
            """
        
        return f"""
        <div class="section">
            <h3 style="font-size: 24px; margin-bottom: 20px; color: #333;">Performance Bottlenecks</h3>
            
            <table class="recommendations-table">
                <thead>
                    <tr>
                        <th>Resource Type</th>
                        <th>Issue</th>
                        <th>Est. Improvement</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_performance_summary(self, dashboard_metrics: Dict) -> str:
        """Generar resumen de rendimiento"""
        total_actions = dashboard_metrics.get('total_actions', 0)
        performance_score = dashboard_metrics.get('performance_score', 100)
        optimization_potential = dashboard_metrics.get('optimization_potential', 0)
        
        summary_text = f"""
        El análisis de rendimiento ha identificado <strong>{total_actions} oportunidades de optimización</strong> 
        que pueden mejorar el rendimiento de su infraestructura hasta un <strong>{optimization_potential}%</strong>. 
        Con una puntuación actual de <strong>{performance_score}/100</strong>, implementar estas recomendaciones 
        resultará en una mejor experiencia de usuario y reducción de latencias.
        """
        
        return f"""
        <div class="summary-box">
            <div class="summary-title">Resumen Ejecutivo</div>
            <div class="summary-text">{summary_text}</div>
        </div>
        """
    
    def _generate_footer(self) -> str:
        """Generar footer del reporte"""
        return f"""
        <div class="footer">
            <p>© 2025 The Cloud Mastery - Azure Performance Analysis Report</p>
            <p>Generated on {self.generated_date}</p>
        </div>
        """
    
    def _generate_error_html(self, error_message: str) -> str:
        """Generar HTML de error"""
        return f"""
        <!DOCTYPE html>
        <html><head><title>Error</title></head>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>Error en Reporte de Rendimiento</h1>
            <p>{error_message}</p>
        </body></html>
        """


class CostHTMLGenerator(SpecializedHTMLGenerator):
    """Generador HTML especializado para reportes de costo"""
    
    def generate_html(self) -> str:
        """Generar HTML completo para reporte de costos"""
        try:
            dashboard_metrics = self.analysis_data.get('dashboard_metrics', {})
            savings_analysis = self.analysis_data.get('savings_analysis', {})
            roi_analysis = self.analysis_data.get('roi_analysis', {})
            cost_opportunities = self.analysis_data.get('cost_optimization_opportunities', {})
            
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Análisis de Costos - {self.client_name}</title>
                {self._get_base_styles()}
            </head>
            <body>
                <div class="container">
                    {self._generate_header("COST OPTIMIZATION", "💰")}
                    
                    <div class="content">
                        {self._generate_cost_metrics(dashboard_metrics, savings_analysis)}
                        {self._generate_savings_breakdown(savings_analysis)}
                        {self._generate_roi_analysis(roi_analysis)}
                        {self._generate_cost_opportunities(cost_opportunities)}
                        {self._generate_cost_summary(dashboard_metrics, savings_analysis)}
                    </div>
                    
                    {self._generate_footer()}
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error generando HTML de costos: {e}")
            return self._generate_error_html("Error generando reporte de costos")
    
    def _generate_header(self, title: str, icon: str) -> str:
        """Generar header del reporte"""
        return f"""
        <div class="header">
            <div class="logo">
                <div class="cloud-icon">☁️</div>
                <h1 class="company-name">The Cloud Mastery</h1>
            </div>
            <h2 class="report-title">Azure Advisor Analyzer</h2>
            <h1 class="client-name">{self.client_name}</h1>
            <div class="date-info">Data retrieved on {self.generated_date}</div>
        </div>
        """
    
    def _generate_cost_metrics(self, dashboard_metrics: Dict, savings_analysis: Dict) -> str:
        """Generar métricas principales de costo"""
        total_actions = dashboard_metrics.get('total_actions', 0)
        monthly_savings = dashboard_metrics.get('monthly_savings', 0)
        annual_savings = dashboard_metrics.get('annual_savings', 0)
        working_hours = dashboard_metrics.get('working_hours', 0)
        
        return f"""
        <div class="section">
            <div class="section-header">
                <div class="section-icon cost-icon">💰</div>
                <h2 class="section-title">Cost Optimization</h2>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{total_actions}</div>
                    <div class="metric-label">Total Actions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color: #00f2fe;">${monthly_savings:,.0f}</div>
                    <div class="metric-label">Estimated Monthly Savings</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color: #4facfe;">${annual_savings:,.0f}</div>
                    <div class="metric-label">Estimated Annual Savings</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{working_hours}</div>
                    <div class="metric-label">Working Hours</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_savings_breakdown(self, savings_analysis: Dict) -> str:
        """Generar desglose de ahorros"""
        immediate = savings_analysis.get('immediate_savings', 0)
        short_term = savings_analysis.get('short_term_savings', 0)
        long_term = savings_analysis.get('long_term_savings', 0)
        
        return f"""
        <div class="section">
            <h3 style="font-size: 24px; margin-bottom: 20px; color: #333;">Sources Of Savings</h3>
            
            <div class="chart-container">
                <div class="metrics-grid" style="grid-template-columns: repeat(3, 1fr);">
                    <div style="text-align: center;">
                        <div style="font-size: 28px; color: #00f2fe; font-weight: bold;">${immediate:,.0f}</div>
                        <div style="font-size: 14px; color: #666;">Immediate Savings</div>
                        <div style="font-size: 12px; color: #999;">Next 30 days</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 28px; color: #4facfe; font-weight: bold;">${short_term:,.0f}</div>
                        <div style="font-size: 14px; color: #666;">Short-term Savings</div>
                        <div style="font-size: 12px; color: #999;">3-6 months</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 28px; color: #667eea; font-weight: bold;">${long_term:,.0f}</div>
                        <div style="font-size: 14px; color: #666;">Long-term Savings</div>
                        <div style="font-size: 12px; color: #999;">6+ months</div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_roi_analysis(self, roi_analysis: Dict) -> str:
        """Generar análisis de ROI"""
        implementation_cost = roi_analysis.get('implementation_cost', 0)
        monthly_roi = roi_analysis.get('monthly_roi_percentage', 0)
        payback_months = roi_analysis.get('payback_period_months', 0)
        three_year_value = roi_analysis.get('three_year_value', 0)
        
        return f"""
        <div class="section">
            <h3 style="font-size: 24px; margin-bottom: 20px; color: #333;">Return on Investment Analysis</h3>
            
            <div class="chart-container">
                <div class="metrics-grid" style="grid-template-columns: repeat(2, 1fr);">
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #28a745; font-weight: bold;">{monthly_roi:.1f}%</div>
                        <div style="font-size: 14px; color: #666;">Monthly ROI</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #17a2b8; font-weight: bold;">{payback_months:.1f}</div>
                        <div style="font-size: 14px; color: #666;">Payback Period (Months)</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 24px; color: #6f42c1; font-weight: bold;">${implementation_cost:,.0f}</div>
                        <div style="font-size: 14px; color: #666;">Implementation Cost</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 24px; color: #fd7e14; font-weight: bold;">${three_year_value:,.0f}</div>
                        <div style="font-size: 14px; color: #666;">3-Year Net Value</div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_cost_opportunities(self, opportunities: Dict) -> str:
        """Generar oportunidades de optimización de costos"""
        rightsizing = opportunities.get('rightsizing_opportunities', 0)
        reserved_instances = opportunities.get('reserved_instance_opportunities', 0)
        storage_opt = opportunities.get('storage_optimization', 0)
        unused_resources = opportunities.get('unused_resources', 0)
        
        return f"""
        <div class="section">
            <h3 style="font-size: 24px; margin-bottom: 20px; color: #333;">Cost Optimization Opportunities</h3>
            
            <div class="chart-container">
                <div class="metrics-grid" style="grid-template-columns: repeat(2, 1fr);">
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #4facfe; font-weight: bold;">{rightsizing}</div>
                        <div style="font-size: 14px; color: #666;">Right-sizing Opportunities</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #00f2fe; font-weight: bold;">{reserved_instances}</div>
                        <div style="font-size: 14px; color: #666;">Reserved Instance Opportunities</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #667eea; font-weight: bold;">{storage_opt}</div>
                        <div style="font-size: 14px; color: #666;">Storage Optimizations</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; color: #dc3545; font-weight: bold;">{unused_resources}</div>
                        <div style="font-size: 14px; color: #666;">Unused Resources</div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_cost_summary(self, dashboard_metrics: Dict, savings_analysis: Dict) -> str:
        """Generar resumen de costos"""
        monthly_savings = dashboard_metrics.get('monthly_savings', 0)
        annual_savings = dashboard_metrics.get('annual_savings', 0)
        total_actions = dashboard_metrics.get('total_actions', 0)
        
        summary_text = f"""
        El análisis de optimización de costos ha identificado <strong>{total_actions} oportunidades</strong> 
        que pueden generar ahorros de <strong>${monthly_savings:,.0f} mensuales</strong> y 
        <strong>${annual_savings:,.0f} anuales</strong>. Implementar estas recomendaciones permitirá 
        optimizar significativamente los costos operacionales de Azure mientras mantiene el rendimiento.
        """
        
        return f"""
        <div class="summary-box">
            <div class="summary-title">Resumen Ejecutivo</div>
            <div class="summary-text">{summary_text}</div>
        </div>
        """
    
    def _generate_footer(self) -> str:
        """Generar footer del reporte"""
        return f"""
        <div class="footer">
            <p>© 2025 The Cloud Mastery - Azure Cost Analysis Report</p>
            <p>Generated on {self.generated_date}</p>
        </div>
        """
    
    def _generate_error_html(self, error_message: str) -> str:
        """Generar HTML de error"""
        return f"""
        <!DOCTYPE html>
        <html><head><title>Error</title></head>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>Error en Reporte de Costos</h1>
            <p>{error_message}</p>
        </body></html>
        """


# Factory function para obtener el generador HTML apropiado
def get_specialized_html_generator(report_type: str, report, analysis_data: Dict):
    """
    Factory function para obtener el generador HTML especializado
    
    Args:
        report_type (str): Tipo de reporte ('security', 'performance', 'cost')
        report: Objeto Report de Django
        analysis_data (Dict): Datos del análisis especializado
    
    Returns:
        Generador HTML especializado correspondiente
    """
    generators = {
        'security': SecurityHTMLGenerator,
        'performance': PerformanceHTMLGenerator,
        'cost': CostHTMLGenerator
    }
    
    generator_class = generators.get(report_type.lower())
    if not generator_class:
        raise ValueError(f"Tipo de reporte no soportado: {report_type}")
    
    return generator_class(report, analysis_data)