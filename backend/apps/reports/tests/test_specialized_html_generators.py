from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.reports.models import Report, CSVFile
from apps.reports.utils.specialized_html_generators import (
    SecurityHTMLGenerator,
    PerformanceHTMLGenerator, 
    CostHTMLGenerator,
    get_specialized_html_generator
)
import uuid

User = get_user_model()

class TestSpecializedHTMLGenerators(TestCase):
    """Tests para los generadores HTML especializados"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear archivo CSV de prueba
        self.csv_file = CSVFile.objects.create(
            id=uuid.uuid4(),
            user=self.user,
            original_filename='test_azure_data.csv',
            file_size=1024,
            rows_count=50,
            columns_count=4,
            processing_status='completed',
            analysis_data={
                'dashboard_metrics': {
                    'total_actions': 25,
                    'estimated_monthly_optimization': 5000
                }
            }
        )
        
        # Crear reporte de prueba
        self.report = Report.objects.create(
            id=uuid.uuid4(),
            user=self.user,
            title='Test Security Report',
            report_type='security',
            csv_file=self.csv_file,
            status='completed'
        )
        
        # Datos de análisis de prueba
        self.security_analysis_data = {
            'dashboard_metrics': {
                'total_actions': 15,
                'critical_issues': 5,
                'security_score': 75,
                'working_hours': 8.5,
                'risk_level': 'Medium'
            },
            'basic_metrics': {
                'total_security_actions': 15,
                'high_impact_actions': 5,
                'medium_impact_actions': 7,
                'low_impact_actions': 3
            },
            'compliance_gaps': {
                'encryption_gaps': 3,
                'access_control_issues': 4,
                'monitoring_gaps': 2
            },
            'priority_recommendations': [
                {
                    'resource_type': 'Virtual machine',
                    'recommendation': 'Enable encryption at host',
                    'business_impact': 'High'
                }
            ]
        }
    
    def test_security_html_generator_initialization(self):
        """Test inicialización del generador HTML de seguridad"""
        generator = SecurityHTMLGenerator(self.report, self.security_analysis_data)
        
        self.assertEqual(generator.report, self.report)
        self.assertEqual(generator.analysis_data, self.security_analysis_data)
        self.assertIn('AZURE', generator.client_name.upper())
    
    def test_security_html_generation(self):
        """Test generación de HTML de seguridad"""
        generator = SecurityHTMLGenerator(self.report, self.security_analysis_data)
        html_content = generator.generate_html()
        
        # Verificar que el HTML contiene elementos esperados
        self.assertIn('<!DOCTYPE html>', html_content)
        self.assertIn('Security Optimization', html_content)
        self.assertIn('75', html_content)  # Security score
        self.assertIn('Medium', html_content)  # Risk level
        self.assertIn('15', html_content)  # Total actions
        
        # Verificar estilos CSS
        self.assertIn('font-family:', html_content)
        self.assertIn('security-icon', html_content)
        
        # Verificar métricas específicas
        self.assertIn('Critical Issues', html_content)
        self.assertIn('Working Hours', html_content)
    
    def test_performance_html_generator(self):
        """Test generador HTML de rendimiento"""
        performance_data = {
            'dashboard_metrics': {
                'total_actions': 10,
                'critical_optimizations': 3,
                'performance_score': 85,
                'optimization_potential': 20,
                'efficiency_rating': 'Good'
            },
            'optimization_opportunities': {
                'compute_optimization': 4,
                'storage_optimization': 3,
                'network_optimization': 2
            }
        }
        
        self.report.report_type = 'performance'
        generator = PerformanceHTMLGenerator(self.report, performance_data)
        html_content = generator.generate_html()
        
        self.assertIn('Performance Optimization', html_content)
        self.assertIn('85', html_content)  # Performance score
        self.assertIn('Good', html_content)  # Efficiency rating
        self.assertIn('20%', html_content)  # Optimization potential
    
    def test_cost_html_generator(self):
        """Test generador HTML de costos"""
        cost_data = {
            'dashboard_metrics': {
                'total_actions': 8,
                'monthly_savings': 15000,
                'annual_savings': 180000,
                'working_hours': 4.5
            },
            'savings_analysis': {
                'immediate_savings': 4500,
                'short_term_savings': 7500,
                'long_term_savings': 3000
            },
            'roi_analysis': {
                'monthly_roi_percentage': 250,
                'payback_months': 2.5,
                'implementation_cost': 2000
            }
        }
        
        self.report.report_type = 'cost'
        generator = CostHTMLGenerator(self.report, cost_data)
        html_content = generator.generate_html()
        
        self.assertIn('Cost Optimization', html_content)
        self.assertIn('15,000', html_content)  # Monthly savings (formatted)
        self.assertIn('250%', html_content)  # ROI percentage
        self.assertIn('2.5', html_content)  # Payback months
    
    def test_factory_function_html_generators(self):
        """Test función factory para generadores HTML"""
        # Test generador de seguridad
        security_gen = get_specialized_html_generator(
            'security', self.report, self.security_analysis_data
        )
        self.assertIsInstance(security_gen, SecurityHTMLGenerator)
        
        # Test generador de rendimiento
        performance_gen = get_specialized_html_generator(
            'performance', self.report, {}
        )
        self.assertIsInstance(performance_gen, PerformanceHTMLGenerator)
        
        # Test generador de costos
        cost_gen = get_specialized_html_generator(
            'cost', self.report, {}
        )
        self.assertIsInstance(cost_gen, CostHTMLGenerator)
        
        # Test tipo inválido
        with self.assertRaises(ValueError):
            get_specialized_html_generator('invalid', self.report, {})
    
    def test_html_structure_validation(self):
        """Test validación de estructura HTML"""
        generator = SecurityHTMLGenerator(self.report, self.security_analysis_data)
        html_content = generator.generate_html()
        
        # Verificar estructura HTML básica
        self.assertIn('<html', html_content)
        self.assertIn('<head>', html_content)
        self.assertIn('<body>', html_content)
        self.assertIn('</html>', html_content)
        
        # Verificar meta tags
        self.assertIn('charset="UTF-8"', html_content)
        self.assertIn('viewport', html_content)
        
        # Verificar clases CSS específicas
        self.assertIn('container', html_content)
        self.assertIn('header', html_content)
        self.assertIn('content', html_content)
    
    def test_error_handling_missing_data(self):
        """Test manejo de errores con datos faltantes"""
        # Test con análisis vacío
        generator = SecurityHTMLGenerator(self.report, {})
        html_content = generator.generate_html()
        
        # Debe generar HTML válido incluso sin datos
        self.assertIn('<!DOCTYPE html>', html_content)
        self.assertIn('Security Optimization', html_content)
        
        # Debe mostrar valores por defecto (0, Unknown, etc.)
        self.assertIn('0', html_content)
        self.assertIn('Unknown', html_content)
