from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.reports.models import Report, CSVFile
import uuid
import json

User = get_user_model()

class TestSpecializedReportViews(TestCase):
    """Tests para las vistas de reportes especializados"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Crear CSV de prueba
        self.csv_file = CSVFile.objects.create(
            id=uuid.uuid4(),
            user=self.user,
            original_filename='test_security_data.csv',
            file_size=2048,
            rows_count=100,
            columns_count=5,
            processing_status='completed',
            analysis_data={
                'category_analysis': {
                    'counts': {
                        'Security': 60,
                        'Performance': 25,
                        'Cost': 15
                    }
                }
            }
        )
        
        # Crear reporte de seguridad
        self.security_report = Report.objects.create(
            id=uuid.uuid4(),
            user=self.user,
            title='Test Security Analysis',
            report_type='security',
            csv_file=self.csv_file,
            status='completed',
            analysis_results={
                'security_analysis': {
                    'dashboard_metrics': {
                        'total_actions': 60,
                        'critical_issues': 15,
                        'security_score': 70
                    }
                }
            }
        )
    
    def test_create_specialized_report(self):
        """Test creación de reporte especializado"""
        url = reverse('reports-list')
        data = {
            'title': 'New Security Analysis',
            'description': 'Test security report',
            'report_type': 'security',
            'csv_file': str(self.csv_file.id),
            'configuration': {
                'include_graphics': True,
                'include_detailed_tables': True
            }
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar datos del reporte creado
        report_data = response.json()
        self.assertEqual(report_data['title'], 'New Security Analysis')
        self.assertEqual(report_data['report_type'], 'security')
        self.assertEqual(report_data['status'], 'pending')
    
    def test_get_specialized_analysis(self):
        """Test obtener análisis especializado específico"""
        url = reverse(
            'report-specialized-analysis', 
            kwargs={'pk': self.security_report.id, 'analysis_type': 'security'}
        )
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['analysis_type'], 'security')
        self.assertEqual(data['report_id'], str(self.security_report.id))
        self.assertIn('data', data)
        self.assertIn('dashboard_metrics', data['data'])
    
    def test_get_report_preview(self):
        """Test obtener vista previa de reporte"""
        url = reverse(
            'report-preview',
            kwargs={'pk': self.security_report.id, 'format': 'json'}
        )
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('report_info', data)
        self.assertIn('csv_info', data)
        self.assertIn('analysis_summary', data)
        
        # Verificar información del reporte
        self.assertEqual(data['report_info']['type'], 'security')
        self.assertEqual(data['csv_info']['filename'], 'test_security_data.csv')
    
    def test_validate_csv_for_report(self):
        """Test validación de CSV para tipo de reporte"""
        url = reverse('validate-csv')
        data = {
            'csv_file_id': str(self.csv_file.id),
            'report_type': 'security'
        }
        
        response = self.client.post(url, data, format='json')
        # Puede ser 200 (validación inmediata) o 202 (validación async)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED])
    
    def test_get_report_types_config(self):
        """Test obtener configuración de tipos de reporte"""
        url = reverse('report-types-config')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('report_types', data)
        self.assertIn('security', data['report_types'])
        self.assertIn('performance', data['report_types'])
        self.assertIn('cost', data['report_types'])
        self.assertIn('comprehensive', data['report_types'])
        
        # Verificar estructura de configuración
        security_config = data['report_types']['security']
        self.assertIn('label', security_config)
        self.assertIn('description', security_config)
        self.assertIn('features', security_config)
    
    def test_specialized_html_generation(self):
        """Test generación de HTML especializado"""
        url = reverse('reports-html', kwargs={'pk': self.security_report.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['content-type'], 'text/html')
        
        html_content = response.content.decode('utf-8')
        self.assertIn('Security Optimization', html_content)
        self.assertIn('70', html_content)  # Security score
    
    def test_unauthorized_access(self):
        """Test acceso no autorizado"""
        self.client.force_authenticate(user=None)
        
        url = reverse('reports-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_cross_user_access_denied(self):
        """Test que usuarios no pueden acceder a reportes de otros"""
        # Crear otro usuario
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Autenticar como el otro usuario
        self.client.force_authenticate(user=other_user)
        
        # Intentar acceder al reporte del primer usuario
        url = reverse('reports-detail', kwargs={'pk': self.security_report.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)