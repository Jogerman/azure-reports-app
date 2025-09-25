# apps/reports/urls.py - VERSIÓN COMPLETAMENTE CORREGIDA
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router principal
router = DefaultRouter()
router.register(r'', views.ReportViewSet, basename='reports')  # ✅ Cambio importante: ruta raíz

app_name = 'reports'

urlpatterns = [
    # ✅ INCLUIR EL ROUTER PRIMERO
    path('', include(router.urls)),
    
    # ✅ ENDPOINTS ESPECÍFICOS DESPUÉS DEL ROUTER
    path('generate/', 
         views.ReportViewSet.as_view({'post': 'create'}),  # ✅ Usar 'create' en lugar de 'generate_report'
         name='generate-report'),
    
    path('<uuid:pk>/status/', 
         views.ReportViewSet.as_view({'get': 'status'}), 
         name='report-status'),
    
    path('<uuid:pk>/html/', 
         views.ReportViewSet.as_view({'get': 'get_html'}), 
         name='report-html'),
    
    path('<uuid:pk>/download/', 
         views.ReportViewSet.as_view({'get': 'download'}), 
         name='report-download'),
    
    # Endpoints de análisis especializado
    path('<uuid:pk>/analysis/<str:analysis_type>/', 
         views.ReportViewSet.as_view({'get': 'get_specialized_analysis'}), 
         name='report-specialized-analysis'),
    
    # Validación de CSV
    path('validate-csv/', 
         views.ReportViewSet.as_view({'post': 'validate_csv_for_report'}), 
         name='validate-csv'),
    
    # Configuración de tipos de reporte
    path('types/config/', 
         views.ReportViewSet.as_view({'get': 'get_report_types_config'}), 
         name='report-types-config'),
]

# NOTA: Con esta configuración:
# - POST /api/reports/ -> Crear reporte (views.ReportViewSet.create)
# - GET /api/reports/ -> Listar reportes (views.ReportViewSet.list)
# - GET /api/reports/{id}/ -> Detalle de reporte (views.ReportViewSet.retrieve)
# - POST /api/reports/generate/ -> Endpoint específico de generación