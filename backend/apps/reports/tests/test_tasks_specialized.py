# backend/apps/reports/tests/test_tasks_specialized.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.reports.models import Report, CSVFile
from apps.reports.tasks import generate_specialized_report, validate_csv_for_specialized_analysis
from unittest.mock import patch, MagicMock
import uuid
import pandas as pd

User = get_user_model()

class TestSpecializedTasks(TestCase):
    """Tests para las tareas Celery especializadas"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.csv_file = CSVFile.objects.create(
            id=uuid.uuid4(),
            user=self.user,
            original_filename='test_azure_security.csv',
            file_size=1024,
            rows_count=50,
            columns_count=4,
            processing_status='completed',
            analysis_data={
                'raw_data': [
                    {
                        'Category': 'Security',
                        'Business Impact': 'High',
                        'Recommendation': 'Enable encryption',
                        'Resource Type': 'Virtual machine'
                    },
                    {
                        'Category': 'Security',
                        'Business Impact': 'Medium',
                        'Recommendation': 'Update TLS version',
                        'Resource Type': 'App service'
                    }
                ]
            }
        )
        
        self.report = Report.objects.create(
            id=uuid.uuid4(),
            user=self.user,
            title='Test Security Task',
            report_type='security',
            csv_file=self.csv_file,
            status='pending'
        )
    
    @patch('apps.reports.tasks.get_csv_dataframe_for_task')
    @patch('apps.reports.tasks.upload_report_files_to_azure')
    @patch('apps.storage.services.pdf_generator_service.generate_report_pdf')
    def test_generate_specialized_report_success(self, mock_pdf_gen, mock_upload, mock_csv):
        """Test generación exitosa de reporte especializado"""
        # Configurar mocks
        mock_csv.return_value = pd.DataFrame([
            {'Category': 'Security', 'Business Impact': 'High', 'Recommendation': 'Test'},
            {'Category': 'Security', 'Business Impact': 'Medium', 'Recommendation': 'Test 2'}
        ])
        mock_pdf_gen.return_value = (b'fake_pdf_content', 'test_report.pdf')
        mock_upload.return_value = ('https://fake-pdf-url', 'https://fake-html-url')
        
        # Ejecutar tarea
        result = generate_specialized_report(str(self.report.id))
        
        # Verificar resultado
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['report_type'], 'security')
        self.assertIn('total_actions', result)
        
        # Verificar que el reporte se actualizó
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, 'completed')
        self.assertIsNotNone(self.report.analysis_results)
        self.assertIn('security_analysis', self.report.analysis_results)
    
    @patch('apps.reports.tasks.get_csv_dataframe_for_task')
    def test_generate_specialized_report_no_data(self, mock_csv):
        """Test generación de reporte sin datos CSV"""
        # Configurar mock para retornar None
        mock_csv.return_value = None
        
        # Ejecutar tarea y verificar que falla
        with self.assertRaises(Exception) as context:
            generate_specialized_report(str(self.report.id))
        
        self.assertIn('No se pudieron obtener datos del CSV', str(context.exception))
        
        # Verificar que el reporte se marcó como fallido
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, 'failed')
        self.assertIsNotNone(self.report.error_message)
    
    def test_validate_csv_for_specialized_analysis_security(self):
        """Test validación de CSV para análisis de seguridad"""
        result = validate_csv_for_specialized_analysis(
            str(self.csv_file.id), 
            'security'
        )
        
        self.assertTrue(result['valid'])
        self.assertGreater(result['total_records'], 0)
        self.assertIn('type_specific_data', result)
        
        type_data = result['type_specific_data']
        self.assertIn('security_records', type_data)
        self.assertTrue(type_data['has_security_data'])
    
    def test_validate_csv_no_security_data(self):
        """Test validación de CSV sin datos de seguridad"""
        # Crear CSV sin datos de seguridad
        csv_no_security = CSVFile.objects.create(
            id=uuid.uuid4(),
            user=self.user,
            original_filename='no_security.csv',
            file_size=512,
            analysis_data={
                'raw_data': [
                    {
                        'Category': 'Performance',
                        'Business Impact': 'High',
                        'Recommendation': 'Optimize VM',
                        'Resource Type': 'Virtual machine'
                    }
                ]
            }
        )
        
        result = validate_csv_for_specialized_analysis(
            str(csv_no_security.id), 
            'security'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('error', result)
        self.assertIn('seguridad', result['error'])
    
    @patch('apps.reports.tasks.get_csv_dataframe_for_task_by_csv_file')
    def test_validate_csv_error_handling(self, mock_csv):
        """Test manejo de errores en validación de CSV"""
        # Configurar mock para simular error
        mock_csv.side_effect = Exception('Test error')
        
        result = validate_csv_for_specialized_analysis(
            str(self.csv_file.id),
            'security'
        )
        
        self.assertFalse(result['valid'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Test error')