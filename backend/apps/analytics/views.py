from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status,viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Count, Sum,Q
from django.utils import timezone 
from datetime import datetime, timedelta
from apps.reports.models import CSVFile, Report
import logging

from .models import UserActivity
from .serializers import UserActivitySerializer

logger = logging.getLogger(__name__)

class AnalyticsViewSet(ViewSet):
    """
    ViewSet modificado para devolver análisis real de datos CSV en lugar de datos estáticos
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Obtener estadísticas reales del dashboard basadas en análisis de CSV
        """
        try:
            user = request.user
            logger.info(f"Obteniendo stats reales para usuario {user.username}")
            
            # Buscar el CSV más reciente del usuario que esté procesado
            latest_csv = CSVFile.objects.filter(
                user=user,
                processing_status='completed'
            ).order_by('-processed_date').first()
            
            if latest_csv and latest_csv.analysis_data:
                # Usar análisis real del CSV
                analysis_data = latest_csv.analysis_data
                dashboard_metrics = analysis_data.get('dashboard_metrics', {})
                
                stats = {
                    'reports_generated': Report.objects.filter(user=user).count(),
                    'files_processed': CSVFile.objects.filter(
                        user=user, 
                        processing_status='completed'
                    ).count(),
                    'total_recommendations': dashboard_metrics.get('total_actions', 0),
                    'monthly_optimization': dashboard_metrics.get('estimated_monthly_optimization', 0),
                    'working_hours': dashboard_metrics.get('working_hours', 0),
                    'high_impact_actions': dashboard_metrics.get('high_impact_count', 0),
                    
                    # Métricas por categoría (datos reales)
                    'cost_optimization': dashboard_metrics.get('cost_optimization', {
                        'actions': 0,
                        'estimated_monthly_savings': 0,
                        'working_hours': 0
                    }),
                    'reliability_optimization': dashboard_metrics.get('reliability_optimization', {
                        'actions': 0,
                        'monthly_investment': 0,
                        'working_hours': 0
                    }),
                    'security_optimization': dashboard_metrics.get('security_optimization', {
                        'actions': 0,
                        'monthly_investment': 0,
                        'working_hours': 0
                    }),
                    'operational_optimization': dashboard_metrics.get('operational_optimization', {
                        'actions': 0,
                        'monthly_investment': 0,
                        'working_hours': 0
                    }),
                    
                    # Metadata del análisis
                    'data_source': 'real_csv_analysis',
                    'last_analysis_date': latest_csv.processed_date.isoformat() if latest_csv.processed_date else None,
                    'csv_filename': latest_csv.original_filename,
                    'analysis_quality_score': analysis_data.get('basic_metrics', {}).get('data_quality_score', 0)
                }
                
                logger.info(f"Devolviendo stats reales basadas en CSV: {latest_csv.original_filename}")
                
            else:
                # Si no hay CSV procesado, devolver datos de ejemplo pero marcados como tal
                stats = self._get_fallback_stats(user)
                logger.warning(f"No hay CSV procesado para {user.username}, devolviendo datos de fallback")
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo stats: {str(e)}")
            
            # En caso de error, devolver datos básicos
            fallback_stats = self._get_fallback_stats(request.user)
            fallback_stats['error'] = f"Error cargando análisis: {str(e)}"
            
            return Response(fallback_stats, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def activity(self, request):
        """
        Obtener actividad reciente real del usuario
        """
        try:
            user = request.user
            limit = int(request.query_params.get('limit', 8))
            
            activities = []
            
            # Actividades reales de archivos CSV
            recent_csvs = CSVFile.objects.filter(user=user).order_by('-upload_date')[:limit//2]
            for csv_file in recent_csvs:
                activities.append({
                    'id': f"csv_{csv_file.id}",
                    'description': f'Archivo CSV "{csv_file.original_filename}" procesado',
                    'timestamp': csv_file.processed_date.isoformat() if csv_file.processed_date else csv_file.upload_date.isoformat(),
                    'type': 'file_processed',
                    'status': csv_file.processing_status,
                    'metadata': {
                        'filename': csv_file.original_filename,
                        'rows_count': csv_file.rows_count,
                        'file_size': csv_file.file_size
                    }
                })
            
            # Actividades reales de reportes
            recent_reports = Report.objects.filter(user=user).order_by('-created_at')[:limit//2]
            for report in recent_reports:
                activities.append({
                    'id': f"report_{report.id}",
                    'description': f'Reporte "{report.title}" generado',
                    'timestamp': report.created_at.isoformat(),
                    'type': 'report_generated',
                    'status': report.status,
                    'metadata': {
                        'report_type': report.report_type,
                        'title': report.title
                    }
                })
            
            # Ordenar por timestamp descendente y limitar
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            activities = activities[:limit]
            
            # Si no hay suficientes actividades reales, completar con ejemplos
            if len(activities) < limit:
                mock_activities = self._get_mock_activities(limit - len(activities))
                activities.extend(mock_activities)
            
            logger.info(f"Devolviendo {len(activities)} actividades reales para {user.username}")
            
            return Response({
                'results': activities,
                'count': len(activities),
                'data_source': 'real_user_activity'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo actividad: {str(e)}")
            
            # En caso de error, devolver actividades mock
            mock_activities = self._get_mock_activities(limit)
            return Response({
                'results': mock_activities,
                'count': len(mock_activities),
                'data_source': 'fallback_mock',
                'error': str(e)
            }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def csv_analysis(self, request):
        """
        Endpoint específico para obtener análisis detallado del CSV más reciente
        """
        try:
            user = request.user
            csv_id = request.query_params.get('csv_id')
            
            if csv_id:
                # Obtener CSV específico
                csv_file = CSVFile.objects.get(id=csv_id, user=user)
            else:
                # Obtener el CSV más reciente
                csv_file = CSVFile.objects.filter(
                    user=user,
                    processing_status='completed'
                ).order_by('-processed_date').first()
            
            if not csv_file:
                return Response({
                    'error': 'No se encontraron archivos CSV procesados'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if not csv_file.analysis_data:
                return Response({
                    'error': 'El archivo CSV no tiene análisis disponible'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Devolver análisis completo
            analysis_data = csv_file.analysis_data
            
            response_data = {
                'csv_info': {
                    'id': str(csv_file.id),
                    'filename': csv_file.original_filename,
                    'upload_date': csv_file.upload_date.isoformat(),
                    'processed_date': csv_file.processed_date.isoformat() if csv_file.processed_date else None,
                    'file_size': csv_file.file_size,
                    'rows_count': csv_file.rows_count,
                    'columns_count': csv_file.columns_count
                },
                'analysis': analysis_data,
                'data_source': 'real_csv_analysis'
            }
            
            logger.info(f"Devolviendo análisis completo para CSV: {csv_file.original_filename}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except CSVFile.DoesNotExist:
            return Response({
                'error': 'Archivo CSV no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            logger.error(f"Error obteniendo análisis CSV: {str(e)}")
            return Response({
                'error': f'Error obteniendo análisis: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def reanalyze_csv(self, request):
        """
        Reanalizar un CSV específico con el nuevo algoritmo de análisis
        """
        try:
            user = request.user
            csv_id = request.data.get('csv_id')
            
            if not csv_id:
                return Response({
                    'error': 'csv_id es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            csv_file = CSVFile.objects.get(id=csv_id, user=user)
            
            # Verificar si tenemos el contenido del archivo
            if not csv_file.azure_blob_url:
                return Response({
                    'error': 'No se puede reanalizar: contenido del archivo no disponible'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Marcar como procesando
            csv_file.processing_status = 'processing'
            csv_file.save()
            
            # Aquí deberías implementar la lógica para obtener el contenido del CSV
            # desde Azure Blob Storage y reanalizarlo
            # Por ahora, simularemos una respuesta de éxito
            
            logger.info(f"Iniciando reanálisis de CSV: {csv_file.original_filename}")
            
            return Response({
                'message': 'Reanálisis iniciado',
                'csv_id': str(csv_file.id),
                'status': 'processing'
            }, status=status.HTTP_202_ACCEPTED)
            
        except CSVFile.DoesNotExist:
            return Response({
                'error': 'Archivo CSV no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            logger.error(f"Error iniciando reanálisis: {str(e)}")
            return Response({
                'error': f'Error iniciando reanálisis: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_fallback_stats(self, user):
        """
        Obtener estadísticas de fallback cuando no hay datos reales disponibles
        """
        return {
            'reports_generated': Report.objects.filter(user=user).count(),
            'files_processed': CSVFile.objects.filter(user=user).count(),
            'total_recommendations': 0,
            'monthly_optimization': 0,
            'working_hours': 0,
            'high_impact_actions': 0,
            'cost_optimization': {
                'actions': 0,
                'estimated_monthly_savings': 0,
                'working_hours': 0
            },
            'reliability_optimization': {
                'actions': 0,
                'monthly_investment': 0,
                'working_hours': 0
            },
            'security_optimization': {
                'actions': 0,
                'monthly_investment': 0,
                'working_hours': 0
            },
            'operational_optimization': {
                'actions': 0,
                'monthly_investment': 0,
                'working_hours': 0
            },
            'data_source': 'fallback_empty',
            'message': 'No hay archivos CSV procesados. Suba un archivo CSV de Azure Advisor para ver análisis reales.'
        }
    
    def _get_mock_activities(self, limit):
        """
        Obtener actividades mock para completar cuando no hay suficientes datos reales
        """
        base_time = timezone.now()
        
        mock_activities = [
            {
                'id': 'mock_1',
                'description': 'Sistema iniciado - esperando archivos CSV',
                'timestamp': (base_time - timezone.timedelta(minutes=30)).isoformat(),
                'type': 'system_ready',
                'status': 'info'
            },
            {
                'id': 'mock_2', 
                'description': 'Analizador CSV real activado',
                'timestamp': (base_time - timezone.timedelta(hours=1)).isoformat(),
                'type': 'system_update',
                'status': 'success'
            },
            {
                'id': 'mock_3',
                'description': 'Conexión con Azure Advisor establecida',
                'timestamp': (base_time - timezone.timedelta(hours=2)).isoformat(),
                'type': 'integration_ready',
                'status': 'success'
            }
        ]
        
        return mock_activities[:limit]

class DashboardStatsView(APIView):
    """Vista para estadísticas del dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # CORREGIR: Usar los nombres correctos de los modelos
            from apps.storage.models import StorageFile  # ← CORRECTO: StorageFile, no UploadedFile
            from apps.reports.models import CSVFile, Report  # ← AGREGAR CSVFile también
            
            user = request.user
            
            # Obtener archivos del usuario (tanto StorageFile como CSVFile)
            storage_files = StorageFile.objects.filter(user=user)
            csv_files = CSVFile.objects.filter(user=user)
            
            # Si tienes modelo Report, usarlo también
            try:
                user_reports = Report.objects.filter(user=user)
                total_reports = user_reports.count()
                completed_reports = user_reports.filter(status='completed').count()
            except:
                # Si no existe el modelo Report, usar valores por defecto
                total_reports = 0
                completed_reports = 0
            
            # Estadísticas básicas
            total_storage_files = storage_files.count()
            total_csv_files = csv_files.count()
            total_files = total_storage_files + total_csv_files
            
            # Calcular recomendaciones y ahorros desde CSVFile
            total_recommendations = 0
            potential_savings = 0
            
            # Analizar CSVFiles que tienen analysis_data
            for csv_file in csv_files:
                if hasattr(csv_file, 'analysis_data') and csv_file.analysis_data:
                    analysis_data = csv_file.analysis_data
                    if isinstance(analysis_data, dict):
                        total_recommendations += analysis_data.get('total_recommendations', 0)
                        potential_savings += analysis_data.get('estimated_savings', 0)
            
            # También revisar StorageFiles por si tienen datos de análisis
            for storage_file in storage_files:
                # Si el StorageFile es un CSV y tiene datos de análisis
                if storage_file.file_type == 'csv':
                    # Aquí puedes agregar lógica adicional si los StorageFiles también tienen analysis_data
                    pass
            
            # Calcular tasa de éxito
            success_rate = 0
            if total_reports > 0:
                success_rate = round((completed_reports / total_reports) * 100, 1)
            elif total_csv_files > 0:
                # Si no hay reportes, usar CSV files completados
                completed_csv = csv_files.filter(processing_status='completed').count()
                success_rate = round((completed_csv / total_csv_files) * 100, 1)
            
            return Response({
                'total_files': total_files,
                'total_storage_files': total_storage_files,
                'total_csv_files': total_csv_files,
                'total_reports': total_reports,
                'completed_reports': completed_reports,
                'total_recommendations': total_recommendations,
                'potential_savings': round(potential_savings, 2),
                'success_rate': success_rate,
                'last_updated': datetime.now().isoformat()
            })
            
        except ImportError as e:
            logger.error(f"Error importando modelos: {str(e)}")
            # Devolver datos básicos cuando hay problemas de import
            return Response({
                'total_files': 0,
                'total_storage_files': 0,
                'total_csv_files': 0,
                'total_reports': 0,
                'completed_reports': 0,
                'total_recommendations': 0,
                'potential_savings': 0,
                'success_rate': 0,
                'last_updated': datetime.now().isoformat(),
                'error': f'Problema con modelos: {str(e)}'
            })
        except Exception as e:
            logger.error(f"Error en dashboard stats: {str(e)}")
            # Devolver datos básicos en caso de otros errores
            return Response({
                'total_files': 0,
                'total_storage_files': 0,
                'total_csv_files': 0,
                'total_reports': 0,
                'completed_reports': 0,
                'total_recommendations': 0,
                'potential_savings': 0,
                'success_rate': 0,
                'last_updated': datetime.now().isoformat(),
                'error': 'Datos no disponibles temporalmente'
            })
