# apps/reports/urls.py - VERSIÓN CORREGIDA
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reports', views.ReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),

    # ✅ AGREGAR ESTE ENDPOINT ESPECÍFICO PARA GENERAR REPORTES
    path('reports/generate/', 
         views.ReportViewSet.as_view({'post': 'generate_report'}), 
         name='generate-report'),
    
    # Endpoints especializados adicionales
    path('reports/<uuid:pk>/analysis/<str:analysis_type>/', 
         views.ReportViewSet.as_view({'get': 'get_specialized_analysis'}), 
         name='report-specialized-analysis'),
    
    # 🔧 CORRECCIÓN: Cambiar 'format' por 'preview_type' para evitar conflicto con DRF
    path('reports/<uuid:pk>/preview/<str:preview_type>/', 
         views.ReportViewSet.as_view({'get': 'preview_report'}), 
         name='report-preview'),
    
    path('reports/validate-csv/', 
         views.ReportViewSet.as_view({'post': 'validate_csv_for_report'}), 
         name='validate-csv'),
    
    path('reports/types/config/', 
         views.ReportViewSet.as_view({'get': 'get_report_types_config'}), 
         name='report-types-config'),
         
    # Endpoints de métricas especializadas
    path('analytics/specialized-stats/<str:report_type>/', 
         views.SpecializedAnalyticsView.as_view(), 
         name='specialized-analytics'),
]