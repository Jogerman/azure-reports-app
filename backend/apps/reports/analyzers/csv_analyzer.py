# backend/apps/reports/analyzers/csv_analyzer.py
import pandas as pd
import numpy as np
from datetime import datetime
from django.utils import timezone
import logging
import json
from typing import Dict, List, Any
from io import StringIO

logger = logging.getLogger(__name__)

def analyze_csv_content(csv_content: str) -> Dict[str, Any]:
    """
    Analizador principal para CSV de Azure Advisor
    Procesa datos reales y genera métricas como el ejemplo_pdf
    """
    try:
        # Cargar CSV
        df = pd.read_csv(StringIO(csv_content))
        logger.info(f"CSV cargado: {len(df)} filas, {len(df.columns)} columnas")
        
        # Limpiar datos
        df = df.dropna(subset=['Category'])
        
        # Análisis por categorías
        category_counts = df['Category'].value_counts().to_dict()
        
        # Análisis por Business Impact
        impact_counts = df['Business Impact'].value_counts().to_dict()
        
        # Análisis por Resource Type
        type_counts = df['Type'].value_counts().head(10).to_dict()
        
        # Métricas principales
        total_actions = len(df)
        high_impact = impact_counts.get('High', 0)
        medium_impact = impact_counts.get('Medium', 0)
        low_impact = impact_counts.get('Low', 0)
        
        # Calcular Azure Advisor Score (más realista)
        # Score basado en proporción de acciones completadas vs pendientes
        completion_rate = max(0, 100 - (high_impact * 0.5) - (medium_impact * 0.2))
        advisor_score = min(100, max(20, completion_rate))  # Entre 20-100
        
        # Estimaciones de ahorros y horas de trabajo por categoría
        category_estimations = {
            'Cost': {'avg_monthly_savings': 450, 'avg_working_hours': 0.4},
            'Security': {'avg_monthly_savings': 0, 'avg_working_hours': 1.2},
            'Reliability': {'avg_monthly_savings': 0, 'avg_working_hours': 0.8},
            'Performance': {'avg_monthly_savings': 0, 'avg_working_hours': 0.6},
            'Operational Excellence': {'avg_monthly_savings': 0, 'avg_working_hours': 0.5},
            'Operational excellence': {'avg_monthly_savings': 0, 'avg_working_hours': 0.5}  # Variante del nombre
        }
        
        # Calcular totales
        total_monthly_savings = 0
        total_working_hours = 0
        category_details = {}
        
        for category, count in category_counts.items():
            estimation = category_estimations.get(category, {'avg_monthly_savings': 0, 'avg_working_hours': 0.5})
            monthly_savings = count * estimation['avg_monthly_savings']
            working_hours = count * estimation['avg_working_hours']
            
            total_monthly_savings += monthly_savings
            total_working_hours += working_hours
            
            category_details[category] = {
                'count': count,
                'monthly_savings': monthly_savings,
                'working_hours': working_hours
            }
        
        # Estructura de datos compatible con el generador de reportes
        analysis_results = {
            'executive_summary': {
                'total_actions': total_actions,
                'advisor_score': round(advisor_score),
                'high_impact_actions': high_impact,
                'medium_impact_actions': medium_impact,
                'low_impact_actions': low_impact,
                'unique_resources': len(df['Resource Name'].unique()) if 'Resource Name' in df.columns else total_actions,
                'unique_resource_groups': len(df['Resource Group'].unique()) if 'Resource Group' in df.columns else 0
            },
            'cost_optimization': {
                'estimated_monthly_optimization': total_monthly_savings,
                'cost_actions_count': category_counts.get('Cost', 0),
                'cost_working_hours': category_details.get('Cost', {}).get('working_hours', 0)
            },
            'security_optimization': {
                'security_actions_count': category_counts.get('Security', 0),
                'security_working_hours': category_details.get('Security', {}).get('working_hours', 0),
                'security_monthly_investment': 0  # Security no genera ahorros, pero requiere inversión
            },
            'reliability_optimization': {
                'reliability_actions_count': category_counts.get('Reliability', 0),
                'reliability_working_hours': category_details.get('Reliability', {}).get('working_hours', 0)
            },
            'operational_excellence': {
                'opex_actions_count': category_counts.get('Operational Excellence', 0) + category_counts.get('Operational excellence', 0),
                'opex_working_hours': category_details.get('Operational Excellence', {}).get('working_hours', 0) + category_details.get('Operational excellence', {}).get('working_hours', 0)
            },
            'category_analysis': {
                'counts': category_counts,
                'details': category_details
            },
            'impact_analysis': {
                'counts': impact_counts,
                'high_percentage': round((high_impact / total_actions) * 100, 1),
                'medium_percentage': round((medium_impact / total_actions) * 100, 1),
                'low_percentage': round((low_impact / total_actions) * 100, 1)
            },
            'resource_analysis': {
                'type_counts': type_counts,
                'top_resource_types': list(type_counts.keys())[:5]
            },
            'totals': {
                'total_actions': total_actions,
                'total_monthly_savings': total_monthly_savings,
                'total_working_hours': round(total_working_hours, 1),
                'azure_advisor_score': round(advisor_score)
            },
            'dashboard_metrics': {
                'total_recommendations': total_actions,
                'estimated_monthly_optimization': total_monthly_savings,
                'working_hours': round(total_working_hours, 1),
                'advisor_score': round(advisor_score),
                'categories_summary': category_details
            },
            'metadata': {
                'analysis_date': timezone.now().isoformat(),
                'csv_rows': total_actions,
                'csv_columns': len(df.columns),
                'data_source': 'Azure Advisor CSV'
            }
        }
        
        logger.info(f"Análisis completado: {total_actions} acciones, ${total_monthly_savings:,} ahorros mensuales")
        return analysis_results
        
    except Exception as e:
        logger.error(f"Error en análisis CSV: {str(e)}", exc_info=True)
        # Retornar estructura básica en caso de error
        return {
            'executive_summary': {'total_actions': 0, 'advisor_score': 0},
            'cost_optimization': {'estimated_monthly_optimization': 0},
            'totals': {'total_actions': 0, 'total_monthly_savings': 0, 'total_working_hours': 0, 'azure_advisor_score': 0},
            'error': str(e)
        }

class AzureAdvisorCSVAnalyzer:
    """Clase wrapper para compatibilidad"""
    
    def __init__(self, csv_content: str):
        self.csv_content = csv_content
        
    def analyze(self) -> Dict[str, Any]:
        """Método de compatibilidad"""
        return analyze_csv_content(self.csv_content)