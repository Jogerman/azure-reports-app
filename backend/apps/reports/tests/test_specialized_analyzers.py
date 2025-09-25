import unittest
import pandas as pd
from django.test import TestCase
from apps.reports.utils.specialized_analyzers import (
    SecurityAnalyzer, 
    PerformanceAnalyzer, 
    CostAnalyzer,
    get_specialized_analyzer
)

class TestSpecializedAnalyzers(TestCase):
    """Tests para los analizadores especializados"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear DataFrame de prueba con datos similares a Azure Advisor
        self.test_data = pd.DataFrame({
            'Category': ['Security', 'Security', 'Performance', 'Cost', 'Security'],
            'Business Impact': ['High', 'Medium', 'High', 'Medium', 'Low'],
            'Recommendation': [
                'Enable encryption at host',
                'Update TLS version',
                'Right-size virtual machines',
                'Consider reserved instances',
                'Enable diagnostic logs'
            ],
            'Resource Type': [
                'Virtual machine',
                'App service',
                'Virtual machine',
                'Subscription',
                'Storage Account'
            ]
        })
    
    def test_security_analyzer_initialization(self):
        """Test inicialización del analizador de seguridad"""
        analyzer = SecurityAnalyzer(self.test_data)
        self.assertIsInstance(analyzer, SecurityAnalyzer)
        self.assertEqual(len(analyzer.security_df), 3)  # 3 registros de seguridad
    
    def test_security_analyzer_basic_metrics(self):
        """Test métricas básicas de seguridad"""
        analyzer = SecurityAnalyzer(self.test_data)
        analysis = analyzer.analyze()
        
        self.assertIn('basic_metrics', analysis)
        basic_metrics = analysis['basic_metrics']
        
        # Verificar métricas calculadas
        self.assertEqual(basic_metrics['total_security_actions'], 3)
        self.assertEqual(basic_metrics['high_impact_actions'], 1)
        self.assertEqual(basic_metrics['medium_impact_actions'], 1)
        self.assertEqual(basic_metrics['low_impact_actions'], 1)
        self.assertGreater(basic_metrics['estimated_working_hours'], 0)
    
    def test_security_analyzer_compliance_gaps(self):
        """Test identificación de gaps de cumplimiento"""
        analyzer = SecurityAnalyzer(self.test_data)
        analysis = analyzer.analyze()
        
        self.assertIn('compliance_gaps', analysis)
        gaps = analysis['compliance_gaps']
        
        # Verificar que identifica gaps de encriptación y actualizaciones
        self.assertIn('encryption_gaps', gaps)
        self.assertIn('update_patches_needed', gaps)
        self.assertGreaterEqual(gaps['encryption_gaps'], 1)  # 'Enable encryption' recommendation
        self.assertGreaterEqual(gaps['update_patches_needed'], 1)  # 'Update TLS' recommendation
    
    def test_performance_analyzer_initialization(self):
        """Test inicialización del analizador de rendimiento"""
        analyzer = PerformanceAnalyzer(self.test_data)
        self.assertIsInstance(analyzer, PerformanceAnalyzer)
        self.assertEqual(len(analyzer.performance_df), 1)  # 1 registro de performance
    
    def test_performance_analyzer_basic_metrics(self):
        """Test métricas básicas de rendimiento"""
        analyzer = PerformanceAnalyzer(self.test_data)
        analysis = analyzer.analyze()
        
        self.assertIn('basic_metrics', analysis)
        basic_metrics = analysis['basic_metrics']
        
        self.assertEqual(basic_metrics['total_performance_actions'], 1)
        self.assertEqual(basic_metrics['high_impact_optimizations'], 1)
        self.assertGreater(basic_metrics['estimated_performance_improvement'], 0)
    
    def test_cost_analyzer_initialization(self):
        """Test inicialización del analizador de costos"""
        analyzer = CostAnalyzer(self.test_data)
        self.assertIsInstance(analyzer, CostAnalyzer)
        self.assertEqual(len(analyzer.cost_df), 1)  # 1 registro de costo
    
    def test_cost_analyzer_savings_calculation(self):
        """Test cálculo de ahorros"""
        analyzer = CostAnalyzer(self.test_data)
        analysis = analyzer.analyze()
        
        self.assertIn('basic_metrics', analysis)
        basic_metrics = analysis['basic_metrics']
        
        self.assertEqual(basic_metrics['total_cost_actions'], 1)
        self.assertGreater(basic_metrics['estimated_monthly_savings'], 0)
        self.assertGreater(basic_metrics['estimated_annual_savings'], 0)
        
        # Verificar que los ahorros anuales son 12x los mensuales
        monthly = basic_metrics['estimated_monthly_savings']
        annual = basic_metrics['estimated_annual_savings']
        self.assertEqual(annual, monthly * 12)
    
    def test_cost_analyzer_roi_analysis(self):
        """Test análisis de ROI"""
        analyzer = CostAnalyzer(self.test_data)
        analysis = analyzer.analyze()
        
        self.assertIn('roi_analysis', analysis)
        roi = analysis['roi_analysis']
        
        self.assertIn('implementation_cost', roi)
        self.assertIn('monthly_savings', roi)
        self.assertIn('monthly_roi_percentage', roi)
        self.assertIn('payback_period_months', roi)
        self.assertGreaterEqual(roi['monthly_roi_percentage'], 0)
    
    def test_factory_function(self):
        """Test función factory para obtener analizadores"""
        # Test analyzer de seguridad
        security_analyzer = get_specialized_analyzer('security', self.test_data)
        self.assertIsInstance(security_analyzer, SecurityAnalyzer)
        
        # Test analyzer de rendimiento
        performance_analyzer = get_specialized_analyzer('performance', self.test_data)
        self.assertIsInstance(performance_analyzer, PerformanceAnalyzer)
        
        # Test analyzer de costos
        cost_analyzer = get_specialized_analyzer('cost', self.test_data)
        self.assertIsInstance(cost_analyzer, CostAnalyzer)
        
        # Test tipo inválido
        with self.assertRaises(ValueError):
            get_specialized_analyzer('invalid_type', self.test_data)
    
    def test_empty_dataframe_handling(self):
        """Test manejo de DataFrames vacíos"""
        empty_df = pd.DataFrame()
        
        security_analyzer = SecurityAnalyzer(empty_df)
        security_analysis = security_analyzer.analyze()
        
        # Verificar que retorna análisis vacío sin errores
        self.assertEqual(security_analysis['basic_metrics']['total_security_actions'], 0)
        self.assertEqual(security_analysis['security_score'], 0)
    
    def test_missing_columns_handling(self):
        """Test manejo de columnas faltantes"""
        incomplete_df = pd.DataFrame({
            'Category': ['Security'],
            # Faltan otras columnas esperadas
        })
        
        analyzer = SecurityAnalyzer(incomplete_df)
        analysis = analyzer.analyze()
        
        # Debe manejar columnas faltantes sin errores
        self.assertIsInstance(analysis, dict)
        self.assertIn('basic_metrics', analysis)