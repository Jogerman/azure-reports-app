# backend/apps/reports/utils/advanced_analytics.py
"""
Analytics avanzados para reportes especializados
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    """Clase para analytics avanzados de reportes"""
    
    @staticmethod
    def calculate_improvement_trends(reports_queryset) -> Dict[str, Any]:
        """Calcular tendencias de mejora a lo largo del tiempo"""
        try:
            trends = {
                'security_trends': [],
                'performance_trends': [],
                'cost_trends': [],
                'overall_improvement': 0
            }
            
            # Agrupar reportes por mes
            monthly_data = {}
            for report in reports_queryset.filter(status='completed').order_by('completed_at'):
                month_key = report.completed_at.strftime('%Y-%m')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'security_scores': [],
                        'performance_scores': [],
                        'monthly_savings': [],
                        'total_reports': 0
                    }
                
                monthly_data[month_key]['total_reports'] += 1
                
                # Extraer métricas según tipo de reporte
                if report.analysis_results:
                    if report.report_type == 'security' and 'security_analysis' in report.analysis_results:
                        security_data = report.analysis_results['security_analysis']
                        score = security_data.get('dashboard_metrics', {}).get('security_score', 0)
                        if score > 0:
                            monthly_data[month_key]['security_scores'].append(score)
                    
                    elif report.report_type == 'performance' and 'performance_analysis' in report.analysis_results:
                        perf_data = report.analysis_results['performance_analysis'] 
                        score = perf_data.get('dashboard_metrics', {}).get('performance_score', 0)
                        if score > 0:
                            monthly_data[month_key]['performance_scores'].append(score)
                    
                    elif report.report_type == 'cost' and 'cost_analysis' in report.analysis_results:
                        cost_data = report.analysis_results['cost_analysis']
                        savings = cost_data.get('dashboard_metrics', {}).get('monthly_savings', 0)
                        if savings > 0:
                            monthly_data[month_key]['monthly_savings'].append(savings)
            
            # Calcular promedios mensuales y tendencias
            sorted_months = sorted(monthly_data.keys())
            
            for month in sorted_months:
                data = monthly_data[month]
                
                # Tendencias de seguridad
                if data['security_scores']:
                    trends['security_trends'].append({
                        'month': month,
                        'average_score': np.mean(data['security_scores']),
                        'report_count': len(data['security_scores'])
                    })
                
                # Tendencias de performance
                if data['performance_scores']:
                    trends['performance_trends'].append({
                        'month': month,
                        'average_score': np.mean(data['performance_scores']),
                        'report_count': len(data['performance_scores'])
                    })
                
                # Tendencias de costos
                if data['monthly_savings']:
                    trends['cost_trends'].append({
                        'month': month,
                        'total_savings': sum(data['monthly_savings']),
                        'average_savings': np.mean(data['monthly_savings']),
                        'report_count': len(data['monthly_savings'])
                    })
            
            # Calcular mejora general
            if len(sorted_months) >= 2:
                first_month = monthly_data[sorted_months[0]]
                last_month = monthly_data[sorted_months[-1]]
                
                first_avg_score = 0
                last_avg_score = 0
                score_count = 0
                
                # Promediar todas las puntuaciones disponibles
                for scores_key in ['security_scores', 'performance_scores']:
                    if first_month[scores_key]:
                        first_avg_score += np.mean(first_month[scores_key])
                        score_count += 1
                    if last_month[scores_key]:
                        last_avg_score += np.mean(last_month[scores_key])
                
                if score_count > 0:
                    first_avg_score /= score_count
                    last_avg_score /= score_count
                    trends['overall_improvement'] = ((last_avg_score - first_avg_score) / first_avg_score) * 100
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculando tendencias: {e}")
            return {'security_trends': [], 'performance_trends': [], 'cost_trends': [], 'overall_improvement': 0}
    
    @staticmethod
    def identify_optimization_patterns(reports_queryset) -> Dict[str, Any]:
        """Identificar patrones de optimización más efectivos"""
        try:
            patterns = {
                'most_impactful_categories': {},
                'resource_type_patterns': {},
                'timing_patterns': {},
                'success_rate_by_type': {}
            }
            
            completed_reports = reports_queryset.filter(status='completed')
            
            # Análisis por categoría de recomendaciones
            category_impact = {}
            resource_impact = {}
            
            for report in completed_reports:
                if report.analysis_results:
                    # Buscar análisis específico según tipo de reporte
                    analysis_key = f'{report.report_type}_analysis'
                    if analysis_key in report.analysis_results:
                        analysis_data = report.analysis_results[analysis_key]
                        
                        # Analizar recomendaciones prioritarias
                        priority_recs = analysis_data.get('priority_recommendations', [])
                        for rec in priority_recs:
                            category = rec.get('category', 'Unknown')
                            resource_type = rec.get('resource_type', 'Unknown')
                            impact = rec.get('business_impact', 'Medium')
                            
                            # Acumular impacto por categoría
                            if category not in category_impact:
                                category_impact[category] = {'High': 0, 'Medium': 0, 'Low': 0}
                            category_impact[category][impact] = category_impact[category].get(impact, 0) + 1
                            
                            # Acumular por tipo de recurso
                            if resource_type not in resource_impact:
                                resource_impact[resource_type] = {'High': 0, 'Medium': 0, 'Low': 0}
                            resource_impact[resource_type][impact] = resource_impact[resource_type].get(impact, 0) + 1
            
            # Calcular patrones más impactantes
            patterns['most_impactful_categories'] = dict(sorted(
                category_impact.items(), 
                key=lambda x: x[1].get('High', 0), 
                reverse=True
            ))
            
            patterns['resource_type_patterns'] = dict(sorted(
                resource_impact.items(),
                key=lambda x: x[1].get('High', 0),
                reverse=True
            ))
            
            # Análisis de timing (día de la semana, hora)
            timing_analysis = {}
            for report in completed_reports:
                if report.completed_at:
                    day_of_week = report.completed_at.strftime('%A')
                    hour = report.completed_at.hour
                    
                    if day_of_week not in timing_analysis:
                        timing_analysis[day_of_week] = {'count': 0, 'avg_duration': []}
                    
                    timing_analysis[day_of_week]['count'] += 1
                    
                    # Calcular duración si tenemos created_at
                    if report.created_at:
                        duration = (report.completed_at - report.created_at).total_seconds() / 60  # minutos
                        timing_analysis[day_of_week]['avg_duration'].append(duration)
            
            # Calcular promedios
            for day, data in timing_analysis.items():
                if data['avg_duration']:
                    data['avg_duration'] = np.mean(data['avg_duration'])
                else:
                    data['avg_duration'] = 0
            
            patterns['timing_patterns'] = timing_analysis
            
            # Tasa de éxito por tipo
            total_reports = reports_queryset.count()
            completed_reports_count = completed_reports.count()
            failed_reports_count = reports_queryset.filter(status='failed').count()
            
            patterns['success_rate_by_type'] = {
                'overall_success_rate': (completed_reports_count / total_reports * 100) if total_reports > 0 else 0,
                'overall_failure_rate': (failed_reports_count / total_reports * 100) if total_reports > 0 else 0
            }
            
            # Tasa por tipo específico
            for report_type in ['security', 'performance', 'cost', 'comprehensive']:
                type_total = reports_queryset.filter(report_type=report_type).count()
                type_completed = completed_reports.filter(report_type=report_type).count()
                
                if type_total > 0:
                    patterns['success_rate_by_type'][f'{report_type}_success_rate'] = (type_completed / type_total) * 100
                else:
                    patterns['success_rate_by_type'][f'{report_type}_success_rate'] = 0
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error identificando patrones: {e}")
            return {
                'most_impactful_categories': {},
                'resource_type_patterns': {},
                'timing_patterns': {},
                'success_rate_by_type': {}
            }
    
    @staticmethod
    def calculate_cost_benefit_analysis(reports_queryset) -> Dict[str, Any]:
        """Calcular análisis de costo-beneficio agregado"""
        try:
            analysis = {
                'total_potential_savings': 0,
                'total_implementation_hours': 0,
                'average_roi': 0,
                'payback_analysis': {},
                'savings_by_category': {},
                'cost_trends': []
            }
            
            cost_reports = reports_queryset.filter(
                report_type='cost',
                status='completed'
            )
            
            monthly_savings = []
            implementation_hours = []
            roi_values = []
            
            for report in cost_reports:
                if report.analysis_results and 'cost_analysis' in report.analysis_results:
                    cost_data = report.analysis_results['cost_analysis']
                    dashboard_metrics = cost_data.get('dashboard_metrics', {})
                    
                    # Acumular ahorros
                    monthly_saving = dashboard_metrics.get('monthly_savings', 0)
                    if monthly_saving > 0:
                        monthly_savings.append(monthly_saving)
                        analysis['total_potential_savings'] += monthly_saving
                    
                    # Acumular horas
                    hours = dashboard_metrics.get('working_hours', 0)
                    if hours > 0:
                        implementation_hours.append(hours)
                        analysis['total_implementation_hours'] += hours
                    
                    # ROI
                    roi = dashboard_metrics.get('roi_percentage', 0)
                    if roi > 0:
                        roi_values.append(roi)
            
            # Calcular promedios
            if roi_values:
                analysis['average_roi'] = np.mean(roi_values)
            
            # Análisis de payback
            if monthly_savings and implementation_hours:
                avg_monthly_savings = np.mean(monthly_savings)
                avg_implementation_hours = np.mean(implementation_hours)
                # Asumiendo $100/hora de costo de implementación
                avg_implementation_cost = avg_implementation_hours * 100
                
                analysis['payback_analysis'] = {
                    'average_monthly_savings': avg_monthly_savings,
                    'average_implementation_cost': avg_implementation_cost,
                    'average_payback_months': (avg_implementation_cost / avg_monthly_savings) if avg_monthly_savings > 0 else 999,
                    'three_year_net_benefit': (avg_monthly_savings * 36) - avg_implementation_cost
                }
            
            # Análisis anualizado
            analysis['annualized_savings'] = analysis['total_potential_savings'] * 12
            analysis['roi_on_time_investment'] = (
                (analysis['total_potential_savings'] * 12) / (analysis['total_implementation_hours'] * 100)
            ) * 100 if analysis['total_implementation_hours'] > 0 else 0
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis costo-beneficio: {e}")
            return {
                'total_potential_savings': 0,
                'total_implementation_hours': 0,
                'average_roi': 0,
                'payback_analysis': {},
                'annualized_savings': 0
            }