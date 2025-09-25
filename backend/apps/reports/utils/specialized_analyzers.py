# backend/apps/reports/utils/specialized_analyzers.py
"""
Analizadores especializados para cada tipo de reporte
Basado en la lógica existente del análisis completo
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SecurityAnalyzer:
    """Analizador especializado para reportes de seguridad"""
    
    def __init__(self, csv_data: pd.DataFrame):
        self.df = csv_data
        self.security_df = self._filter_security_data()
    
    def _filter_security_data(self) -> pd.DataFrame:
        """Filtrar solo las recomendaciones de seguridad"""
        if 'Category' in self.df.columns:
            return self.df[self.df['Category'].str.lower() == 'security'].copy()
        return pd.DataFrame()
    
    def analyze(self) -> Dict[str, Any]:
        """Realizar análisis completo de seguridad"""
        try:
            if self.security_df.empty:
                logger.warning("No se encontraron recomendaciones de seguridad")
                return self._empty_security_analysis()
            
            analysis = {
                'basic_metrics': self._calculate_basic_metrics(),
                'impact_analysis': self._analyze_impact_distribution(),
                'resource_analysis': self._analyze_resource_types(),
                'priority_recommendations': self._get_priority_recommendations(),
                'compliance_gaps': self._identify_compliance_gaps(),
                'security_score': self._calculate_security_score(),
                'dashboard_metrics': self._create_dashboard_metrics()
            }
            
            logger.info(f"Análisis de seguridad completado: {len(self.security_df)} recomendaciones")
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis de seguridad: {e}")
            return self._empty_security_analysis()
    
    def _calculate_basic_metrics(self) -> Dict[str, Any]:
        """Calcular métricas básicas de seguridad"""
        total_actions = len(self.security_df)
        
        # Análisis por impacto
        impact_counts = self.security_df.get('Business Impact', pd.Series()).value_counts().to_dict()
        high_impact = impact_counts.get('High', 0)
        medium_impact = impact_counts.get('Medium', 0)
        low_impact = impact_counts.get('Low', 0)
        
        # Tipos de recursos únicos
        unique_resources = self.security_df.get('Resource Type', pd.Series()).nunique()
        
        # Estimación de tiempo de implementación (horas)
        working_hours = high_impact * 2.0 + medium_impact * 1.0 + low_impact * 0.5
        
        return {
            'total_security_actions': total_actions,
            'high_impact_actions': high_impact,
            'medium_impact_actions': medium_impact,
            'low_impact_actions': low_impact,
            'unique_resources_affected': unique_resources,
            'estimated_working_hours': round(working_hours, 1),
            'critical_vulnerabilities': high_impact,  # Consideramos High Impact como crítico
            'data_quality_score': min(100, max(0, 100 - (len(self.security_df[self.security_df.isnull().any(axis=1)]) * 10)))
        }
    
    def _analyze_impact_distribution(self) -> Dict[str, Any]:
        """Analizar distribución de impacto de negocio"""
        impact_data = self.security_df.get('Business Impact', pd.Series())
        
        return {
            'impact_distribution': impact_data.value_counts().to_dict(),
            'impact_percentages': (impact_data.value_counts(normalize=True) * 100).round(1).to_dict()
        }
    
    def _analyze_resource_types(self) -> Dict[str, Any]:
        """Analizar tipos de recursos afectados"""
        resource_data = self.security_df.get('Resource Type', pd.Series())
        resource_counts = resource_data.value_counts()
        
        return {
            'resource_counts': resource_counts.to_dict(),
            'most_affected_resource': resource_counts.index[0] if not resource_counts.empty else 'N/A',
            'total_resource_types': len(resource_counts)
        }
    
    def _get_priority_recommendations(self) -> List[Dict]:
        """Obtener las recomendaciones de mayor prioridad"""
        # Filtrar recomendaciones de alto impacto
        high_priority = self.security_df[self.security_df.get('Business Impact', '') == 'High']
        
        recommendations = []
        for _, row in high_priority.head(10).iterrows():  # Top 10
            recommendations.append({
                'recommendation': row.get('Recommendation', ''),
                'resource_type': row.get('Resource Type', ''),
                'business_impact': row.get('Business Impact', ''),
                'category': row.get('Category', '')
            })
        
        return recommendations
    
    def _identify_compliance_gaps(self) -> Dict[str, Any]:
        """Identificar brechas de cumplimiento comunes"""
        recommendations = self.security_df.get('Recommendation', pd.Series()).str.lower()
        
        compliance_patterns = {
            'encryption_gaps': recommendations.str.contains('encrypt', na=False).sum(),
            'access_control_issues': recommendations.str.contains('access|permission|identity', na=False).sum(),
            'update_patches_needed': recommendations.str.contains('update|patch|version', na=False).sum(),
            'monitoring_gaps': recommendations.str.contains('log|monitor|diagnostic', na=False).sum(),
            'network_security_issues': recommendations.str.contains('network|firewall|tls|ssl', na=False).sum()
        }
        
        return compliance_patterns
    
    def _calculate_security_score(self) -> int:
        """Calcular puntuación de seguridad (0-100)"""
        if self.security_df.empty:
            return 0
        
        total_actions = len(self.security_df)
        high_impact = len(self.security_df[self.security_df.get('Business Impact', '') == 'High'])
        
        # Lógica simple: menos vulnerabilidades = mejor puntuación
        # Máximo de 100, se reduce según la cantidad y severidad
        base_score = max(0, 100 - (total_actions * 2) - (high_impact * 5))
        return min(100, max(0, base_score))
    
    def _create_dashboard_metrics(self) -> Dict[str, Any]:
        """Crear métricas para el dashboard"""
        basic_metrics = self._calculate_basic_metrics()
        
        return {
            'total_actions': basic_metrics['total_security_actions'],
            'critical_issues': basic_metrics['high_impact_actions'],
            'working_hours': basic_metrics['estimated_working_hours'],
            'security_score': self._calculate_security_score(),
            'compliance_coverage': max(0, 100 - (basic_metrics['total_security_actions'] * 3)),
            'risk_level': self._calculate_risk_level()
        }
    
    def _calculate_risk_level(self) -> str:
        """Calcular nivel de riesgo general"""
        high_impact = len(self.security_df[self.security_df.get('Business Impact', '') == 'High'])
        
        if high_impact >= 10:
            return 'Critical'
        elif high_impact >= 5:
            return 'High'
        elif high_impact >= 1:
            return 'Medium'
        else:
            return 'Low'
    
    def _empty_security_analysis(self) -> Dict[str, Any]:
        """Retornar análisis vacío cuando no hay datos"""
        return {
            'basic_metrics': {
                'total_security_actions': 0,
                'high_impact_actions': 0,
                'medium_impact_actions': 0,
                'low_impact_actions': 0,
                'unique_resources_affected': 0,
                'estimated_working_hours': 0,
                'critical_vulnerabilities': 0,
                'data_quality_score': 0
            },
            'impact_analysis': {'impact_distribution': {}, 'impact_percentages': {}},
            'resource_analysis': {'resource_counts': {}, 'most_affected_resource': 'N/A', 'total_resource_types': 0},
            'priority_recommendations': [],
            'compliance_gaps': {},
            'security_score': 0,
            'dashboard_metrics': {
                'total_actions': 0,
                'critical_issues': 0,
                'working_hours': 0,
                'security_score': 0,
                'compliance_coverage': 0,
                'risk_level': 'Unknown'
            }
        }


class PerformanceAnalyzer:
    """Analizador especializado para reportes de rendimiento"""
    
    def __init__(self, csv_data: pd.DataFrame):
        self.df = csv_data
        self.performance_df = self._filter_performance_data()
    
    def _filter_performance_data(self) -> pd.DataFrame:
        """Filtrar solo las recomendaciones de rendimiento"""
        if 'Category' in self.df.columns:
            return self.df[self.df['Category'].str.lower() == 'performance'].copy()
        return pd.DataFrame()
    
    def analyze(self) -> Dict[str, Any]:
        """Realizar análisis completo de rendimiento"""
        try:
            if self.performance_df.empty:
                logger.warning("No se encontraron recomendaciones de rendimiento")
                return self._empty_performance_analysis()
            
            analysis = {
                'basic_metrics': self._calculate_basic_metrics(),
                'optimization_opportunities': self._identify_optimization_opportunities(),
                'resource_analysis': self._analyze_resource_performance(),
                'bottleneck_analysis': self._identify_bottlenecks(),
                'performance_score': self._calculate_performance_score(),
                'dashboard_metrics': self._create_dashboard_metrics()
            }
            
            logger.info(f"Análisis de rendimiento completado: {len(self.performance_df)} recomendaciones")
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis de rendimiento: {e}")
            return self._empty_performance_analysis()
    
    def _calculate_basic_metrics(self) -> Dict[str, Any]:
        """Calcular métricas básicas de rendimiento"""
        total_actions = len(self.performance_df)
        
        # Análisis por impacto
        impact_counts = self.performance_df.get('Business Impact', pd.Series()).value_counts().to_dict()
        high_impact = impact_counts.get('High', 0)
        medium_impact = impact_counts.get('Medium', 0)
        low_impact = impact_counts.get('Low', 0)
        
        # Estimación de mejora de rendimiento (%)
        performance_improvement = high_impact * 25 + medium_impact * 15 + low_impact * 5
        
        # Tiempo estimado de implementación
        working_hours = high_impact * 3.0 + medium_impact * 1.5 + low_impact * 0.75
        
        return {
            'total_performance_actions': total_actions,
            'high_impact_optimizations': high_impact,
            'medium_impact_optimizations': medium_impact,
            'low_impact_optimizations': low_impact,
            'estimated_performance_improvement': min(100, performance_improvement),
            'estimated_working_hours': round(working_hours, 1),
            'unique_resources_affected': self.performance_df.get('Resource Type', pd.Series()).nunique()
        }
    
    def _identify_optimization_opportunities(self) -> Dict[str, Any]:
        """Identificar oportunidades de optimización"""
        recommendations = self.performance_df.get('Recommendation', pd.Series()).str.lower()
        
        opportunities = {
            'compute_optimization': recommendations.str.contains('virtual machine|vm|compute', na=False).sum(),
            'storage_optimization': recommendations.str.contains('storage|disk|ssd', na=False).sum(),
            'network_optimization': recommendations.str.contains('network|bandwidth|latency', na=False).sum(),
            'scaling_opportunities': recommendations.str.contains('scale|autoscale|resize', na=False).sum(),
            'caching_opportunities': recommendations.str.contains('cache|cdn', na=False).sum()
        }
        
        return opportunities
    
    def _analyze_resource_performance(self) -> Dict[str, Any]:
        """Analizar rendimiento por tipo de recurso"""
        resource_data = self.performance_df.get('Resource Type', pd.Series())
        resource_counts = resource_data.value_counts()
        
        return {
            'resource_counts': resource_counts.to_dict(),
            'most_affected_resource': resource_counts.index[0] if not resource_counts.empty else 'N/A',
            'performance_critical_resources': len(resource_counts)
        }
    
    def _identify_bottlenecks(self) -> List[Dict]:
        """Identificar cuellos de botella principales"""
        # Enfocarse en recomendaciones de alto impacto
        bottlenecks = self.performance_df[
            self.performance_df.get('Business Impact', '') == 'High'
        ]
        
        bottleneck_list = []
        for _, row in bottlenecks.head(5).iterrows():
            bottleneck_list.append({
                'resource_type': row.get('Resource Type', ''),
                'recommendation': row.get('Recommendation', ''),
                'business_impact': row.get('Business Impact', ''),
                'estimated_improvement': '15-30%'  # Estimación estándar
            })
        
        return bottleneck_list
    
    def _calculate_performance_score(self) -> int:
        """Calcular puntuación de rendimiento (0-100)"""
        if self.performance_df.empty:
            return 100  # Sin problemas = perfecto rendimiento
        
        total_actions = len(self.performance_df)
        high_impact = len(self.performance_df[self.performance_df.get('Business Impact', '') == 'High'])
        
        # Lógica: menos problemas de rendimiento = mejor puntuación
        base_score = max(0, 100 - (total_actions * 3) - (high_impact * 8))
        return min(100, max(0, base_score))
    
    def _create_dashboard_metrics(self) -> Dict[str, Any]:
        """Crear métricas para el dashboard"""
        basic_metrics = self._calculate_basic_metrics()
        
        return {
            'total_actions': basic_metrics['total_performance_actions'],
            'critical_optimizations': basic_metrics['high_impact_optimizations'],
            'working_hours': basic_metrics['estimated_working_hours'],
            'performance_score': self._calculate_performance_score(),
            'optimization_potential': basic_metrics['estimated_performance_improvement'],
            'efficiency_rating': self._calculate_efficiency_rating()
        }
    
    def _calculate_efficiency_rating(self) -> str:
        """Calcular calificación de eficiencia"""
        score = self._calculate_performance_score()
        
        if score >= 90:
            return 'Excellent'
        elif score >= 75:
            return 'Good'
        elif score >= 60:
            return 'Fair'
        else:
            return 'Needs Improvement'
    
    def _empty_performance_analysis(self) -> Dict[str, Any]:
        """Retornar análisis vacío cuando no hay datos"""
        return {
            'basic_metrics': {
                'total_performance_actions': 0,
                'high_impact_optimizations': 0,
                'medium_impact_optimizations': 0,
                'low_impact_optimizations': 0,
                'estimated_performance_improvement': 0,
                'estimated_working_hours': 0,
                'unique_resources_affected': 0
            },
            'optimization_opportunities': {},
            'resource_analysis': {'resource_counts': {}, 'most_affected_resource': 'N/A', 'performance_critical_resources': 0},
            'bottleneck_analysis': [],
            'performance_score': 100,
            'dashboard_metrics': {
                'total_actions': 0,
                'critical_optimizations': 0,
                'working_hours': 0,
                'performance_score': 100,
                'optimization_potential': 0,
                'efficiency_rating': 'Excellent'
            }
        }


class CostAnalyzer:
    """Analizador especializado para reportes de costo"""
    
    def __init__(self, csv_data: pd.DataFrame):
        self.df = csv_data
        self.cost_df = self._filter_cost_data()
    
    def _filter_cost_data(self) -> pd.DataFrame:
        """Filtrar solo las recomendaciones de costo"""
        if 'Category' in self.df.columns:
            return self.df[self.df['Category'].str.lower() == 'cost'].copy()
        return pd.DataFrame()
    
    def analyze(self) -> Dict[str, Any]:
        """Realizar análisis completo de costos"""
        try:
            if self.cost_df.empty:
                logger.warning("No se encontraron recomendaciones de costo")
                return self._empty_cost_analysis()
            
            analysis = {
                'basic_metrics': self._calculate_basic_metrics(),
                'savings_analysis': self._calculate_potential_savings(),
                'cost_optimization_opportunities': self._identify_cost_opportunities(),
                'resource_cost_analysis': self._analyze_resource_costs(),
                'roi_analysis': self._calculate_roi_analysis(),
                'dashboard_metrics': self._create_dashboard_metrics()
            }
            
            logger.info(f"Análisis de costos completado: {len(self.cost_df)} recomendaciones")
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis de costos: {e}")
            return self._empty_cost_analysis()
    
    def _calculate_basic_metrics(self) -> Dict[str, Any]:
        """Calcular métricas básicas de costo"""
        total_actions = len(self.cost_df)
        
        # Análisis por impacto
        impact_counts = self.cost_df.get('Business Impact', pd.Series()).value_counts().to_dict()
        high_impact = impact_counts.get('High', 0)
        medium_impact = impact_counts.get('Medium', 0)
        low_impact = impact_counts.get('Low', 0)
        
        # Estimación de ahorros potenciales (USD/mes)
        estimated_savings = high_impact * 1500 + medium_impact * 500 + low_impact * 150
        
        # Tiempo de implementación
        working_hours = high_impact * 1.0 + medium_impact * 0.5 + low_impact * 0.25
        
        return {
            'total_cost_actions': total_actions,
            'high_value_savings': high_impact,
            'medium_value_savings': medium_impact,
            'low_value_savings': low_impact,
            'estimated_monthly_savings': estimated_savings,
            'estimated_annual_savings': estimated_savings * 12,
            'estimated_working_hours': round(working_hours, 1),
            'unique_resources_affected': self.cost_df.get('Resource Type', pd.Series()).nunique()
        }
    
    def _calculate_potential_savings(self) -> Dict[str, Any]:
        """Calcular ahorros potenciales detallados"""
        basic_metrics = self._calculate_basic_metrics()
        
        monthly_savings = basic_metrics['estimated_monthly_savings']
        annual_savings = basic_metrics['estimated_annual_savings']
        
        # Categorizar los ahorros
        savings_breakdown = {
            'immediate_savings': monthly_savings * 0.3,  # 30% inmediato
            'short_term_savings': monthly_savings * 0.5,  # 50% a corto plazo
            'long_term_savings': monthly_savings * 0.2,   # 20% a largo plazo
            'total_monthly_potential': monthly_savings,
            'total_annual_potential': annual_savings
        }
        
        return savings_breakdown
    
    def _identify_cost_opportunities(self) -> Dict[str, Any]:
        """Identificar oportunidades de optimización de costos"""
        recommendations = self.cost_df.get('Recommendation', pd.Series()).str.lower()
        
        opportunities = {
            'rightsizing_opportunities': recommendations.str.contains('resize|right.size|underutilized', na=False).sum(),
            'reserved_instance_opportunities': recommendations.str.contains('reserved|reservation', na=False).sum(),
            'storage_optimization': recommendations.str.contains('storage|blob|disk', na=False).sum(),
            'compute_optimization': recommendations.str.contains('virtual machine|vm|compute', na=False).sum(),
            'unused_resources': recommendations.str.contains('unused|idle|delete', na=False).sum()
        }
        
        return opportunities
    
    def _analyze_resource_costs(self) -> Dict[str, Any]:
        """Analizar costos por tipo de recurso"""
        resource_data = self.cost_df.get('Resource Type', pd.Series())
        resource_counts = resource_data.value_counts()
        
        # Estimación de costos por tipo de recurso
        cost_estimates = {}
        for resource_type, count in resource_counts.items():
            # Estimación básica basada en el tipo de recurso
            if 'virtual machine' in resource_type.lower():
                cost_estimates[resource_type] = count * 200  # $200/mes por VM
            elif 'storage' in resource_type.lower():
                cost_estimates[resource_type] = count * 50   # $50/mes por storage
            else:
                cost_estimates[resource_type] = count * 100  # $100/mes por defecto
        
        return {
            'resource_counts': resource_counts.to_dict(),
            'estimated_monthly_costs': cost_estimates,
            'highest_cost_resource': max(cost_estimates, key=cost_estimates.get) if cost_estimates else 'N/A'
        }
    
    def _calculate_roi_analysis(self) -> Dict[str, Any]:
        """Calcular análisis de ROI"""
        basic_metrics = self._calculate_basic_metrics()
        
        monthly_savings = basic_metrics['estimated_monthly_savings']
        implementation_hours = basic_metrics['estimated_working_hours']
        
        # Asumiendo $100/hora para implementación
        implementation_cost = implementation_hours * 100
        
        # ROI mensual
        monthly_roi = (monthly_savings / max(implementation_cost, 1)) * 100 if implementation_cost > 0 else 0
        
        # Tiempo para recuperar la inversión (meses)
        payback_months = max(implementation_cost / max(monthly_savings, 1), 0) if monthly_savings > 0 else 999
        
        return {
            'implementation_cost': implementation_cost,
            'monthly_savings': monthly_savings,
            'monthly_roi_percentage': round(monthly_roi, 1),
            'payback_period_months': round(payback_months, 1),
            'three_year_value': (monthly_savings * 36) - implementation_cost
        }
    
    def _create_dashboard_metrics(self) -> Dict[str, Any]:
        """Crear métricas para el dashboard"""
        basic_metrics = self._calculate_basic_metrics()
        roi_analysis = self._calculate_roi_analysis()
        
        return {
            'total_actions': basic_metrics['total_cost_actions'],
            'monthly_savings': basic_metrics['estimated_monthly_savings'],
            'annual_savings': basic_metrics['estimated_annual_savings'],
            'working_hours': basic_metrics['estimated_working_hours'],
            'roi_percentage': roi_analysis['monthly_roi_percentage'],
            'payback_months': roi_analysis['payback_period_months'],
            'optimization_score': self._calculate_optimization_score()
        }
    
    def _calculate_optimization_score(self) -> int:
        """Calcular puntuación de optimización de costos (0-100)"""
        if self.cost_df.empty:
            return 100  # Sin recomendaciones = totalmente optimizado
        
        total_actions = len(self.cost_df)
        high_impact = len(self.cost_df[self.cost_df.get('Business Impact', '') == 'High'])
        
        # Lógica: menos oportunidades de ahorro = mejor optimización actual
        base_score = max(0, 100 - (total_actions * 4) - (high_impact * 10))
        return min(100, max(0, base_score))
    
    def _empty_cost_analysis(self) -> Dict[str, Any]:
        """Retornar análisis vacío cuando no hay datos"""
        return {
            'basic_metrics': {
                'total_cost_actions': 0,
                'high_value_savings': 0,
                'medium_value_savings': 0,
                'low_value_savings': 0,
                'estimated_monthly_savings': 0,
                'estimated_annual_savings': 0,
                'estimated_working_hours': 0,
                'unique_resources_affected': 0
            },
            'savings_analysis': {
                'immediate_savings': 0,
                'short_term_savings': 0,
                'long_term_savings': 0,
                'total_monthly_potential': 0,
                'total_annual_potential': 0
            },
            'cost_optimization_opportunities': {},
            'resource_cost_analysis': {'resource_counts': {}, 'estimated_monthly_costs': {}, 'highest_cost_resource': 'N/A'},
            'roi_analysis': {
                'implementation_cost': 0,
                'monthly_savings': 0,
                'monthly_roi_percentage': 0,
                'payback_period_months': 0,
                'three_year_value': 0
            },
            'dashboard_metrics': {
                'total_actions': 0,
                'monthly_savings': 0,
                'annual_savings': 0,
                'working_hours': 0,
                'roi_percentage': 0,
                'payback_months': 0,
                'optimization_score': 100
            }
        }


# Función principal para obtener el analizador apropiado
def get_specialized_analyzer(report_type: str, csv_data: pd.DataFrame):
    """
    Factory function para obtener el analizador especializado
    
    Args:
        report_type (str): Tipo de reporte ('security', 'performance', 'cost')
        csv_data (pd.DataFrame): Datos del CSV procesado
    
    Returns:
        Analizador especializado correspondiente
    """
    analyzers = {
        'security': SecurityAnalyzer,
        'performance': PerformanceAnalyzer,
        'cost': CostAnalyzer
    }
    
    analyzer_class = analyzers.get(report_type.lower())
    if not analyzer_class:
        raise ValueError(f"Tipo de reporte no soportado: {report_type}")
    
    return analyzer_class(csv_data)