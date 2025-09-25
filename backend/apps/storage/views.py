# apps/storage/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from apps.reports.models import CSVFile
from rest_framework import serializers
from django.utils import timezone
from apps.reports.analyzers.csv_analyzer import analyze_csv_content
import pandas as pd
import logging
import uuid
import csv
import io

logger = logging.getLogger(__name__)

class CSVFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVFile
        fields = [
            'id', 'original_filename', 'file_size', 'processing_status',
            'rows_count', 'columns_count', 'analysis_data', 'upload_date'
        ]

class FilesListView(APIView):
    """Vista que lista CSVFiles para el frontend"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            
            # Obtener CSVFiles usando el campo correcto
            csv_files = CSVFile.objects.filter(user=user).order_by('-upload_date')
            
            files_data = []
            
            for csv_file in csv_files:
                files_data.append({
                    'id': str(csv_file.id),
                    'original_filename': csv_file.original_filename,
                    'file_size': csv_file.file_size,
                    'file_type': 'csv',
                    'created_at': csv_file.upload_date.isoformat(),
                    'status': csv_file.processing_status,
                    'source': 'csv',
                    'analysis_data': {
                        'total_rows': csv_file.rows_count or 0,
                        'total_columns': csv_file.columns_count or 0,
                        'total_recommendations': (csv_file.analysis_data or {}).get('total_recommendations', 0),
                        'estimated_savings': (csv_file.analysis_data or {}).get('estimated_savings', 0),
                    }
                })
            
            logger.info(f"Devolviendo {len(files_data)} archivos para el usuario {user.username}")
            
            return Response({
                'results': files_data,
                'count': len(files_data)
            })
            
        except Exception as e:
            logger.error(f"Error obteniendo archivos: {str(e)}")
            return Response({
                'results': [],
                'count': 0,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileUploadViewWithRealAnalysis(APIView):
    """
    Vista de upload modificada para realizar análisis real del CSV inmediatamente
    """
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        try:
            logger.info(f"Upload con análisis real - usuario: {request.user.username}")
            
            # Verificar archivo
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return Response({
                    'error': 'No se recibió ningún archivo'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar CSV
            if not uploaded_file.name.lower().endswith('.csv'):
                return Response({
                    'error': 'Solo se permiten archivos CSV'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar tamaño (50MB max)
            max_size = 50 * 1024 * 1024
            if uploaded_file.size > max_size:
                return Response({
                    'error': 'El archivo debe ser menor a 50MB'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Procesando CSV con análisis real: {uploaded_file.name}")
            
            # Crear CSVFile
            csv_file = CSVFile.objects.create(
                user=request.user,
                original_filename=uploaded_file.name,
                file_size=uploaded_file.size,
                content_type=uploaded_file.content_type or 'text/csv',
                processing_status='processing'
            )
            
            try:
                # Leer contenido del archivo
                file_content = uploaded_file.read().decode('utf-8-sig')
                
                # Análisis básico con pandas para validar
                df = pd.read_csv(io.StringIO(file_content))
                csv_file.rows_count = len(df)
                csv_file.columns_count = len(df.columns)
                
                logger.info(f"CSV básico procesado: {len(df)} filas, {len(df.columns)} columnas")
                
                # ANÁLISIS REAL usando el nuevo servicio
                try:
                    logger.info("Iniciando análisis completo del CSV...")
                    analysis_results = analyze_csv_content(file_content)
                    
                    # Guardar resultados del análisis
                    csv_file.analysis_data = analysis_results
                    csv_file.processing_status = 'completed'
                    csv_file.processed_date = timezone.now()
                    csv_file.save()
                    
                    logger.info(f"Análisis completo exitoso para {uploaded_file.name}")
                    
                    # Preparar respuesta con análisis incluido
                    response_data = {
                        'id': str(csv_file.id),
                        'original_filename': csv_file.original_filename,
                        'file_size': csv_file.file_size,
                        'status': csv_file.processing_status,
                        'rows_count': csv_file.rows_count,
                        'columns_count': csv_file.columns_count,
                        'upload_date': csv_file.upload_date.isoformat(),
                        'processed_date': csv_file.processed_date.isoformat(),
                        
                        # Incluir métricas clave del análisis
                        'analysis_summary': {
                            'total_recommendations': analysis_results.get('basic_metrics', {}).get('total_recommendations', 0),
                            'categories_found': list(analysis_results.get('category_analysis', {}).get('counts', {}).keys()),
                            'data_quality_score': analysis_results.get('basic_metrics', {}).get('data_quality_score', 0),
                            'estimated_monthly_savings': analysis_results.get('dashboard_metrics', {}).get('estimated_monthly_optimization', 0)
                        },
                        
                        'message': '¡Archivo procesado y analizado exitosamente! Los datos reales ya están disponibles en el dashboard.'
                    }
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
                    
                except Exception as analysis_error:
                    logger.error(f"Error en análisis completo: {str(analysis_error)}")
                    
                    # Guardar con análisis básico en caso de error del análisis avanzado
                    csv_file.analysis_data = {
                        'basic_metrics': {
                            'total_recommendations': len(df),
                            'total_columns': len(df.columns),
                            'data_quality_score': 75.0,
                            'last_updated': timezone.now().isoformat()
                        },
                        'error': f'Error en análisis avanzado: {str(analysis_error)}'
                    }
                    csv_file.processing_status = 'completed'
                    csv_file.processed_date = timezone.now()
                    csv_file.save()
                    
                    return Response({
                        'id': str(csv_file.id),
                        'original_filename': csv_file.original_filename,
                        'status': 'completed_with_basic_analysis',
                        'message': 'Archivo procesado con análisis básico. Algunos análisis avanzados no están disponibles.',
                        'error': str(analysis_error)
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as processing_error:
                logger.error(f"Error procesando CSV: {str(processing_error)}")
                
                # Marcar como fallido
                csv_file.processing_status = 'failed'
                csv_file.error_message = str(processing_error)
                csv_file.save()
                
                return Response({
                    'error': f'Error procesando archivo: {str(processing_error)}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error general en upload: {str(e)}")
            return Response({
                'error': f'Error interno: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)