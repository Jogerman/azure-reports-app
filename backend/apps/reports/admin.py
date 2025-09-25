# apps/reports/admin.py - VERSIÓN CORREGIDA
from django.contrib import admin
from .models import CSVFile, Report

@admin.register(CSVFile)
class CSVFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'user', 'processing_status', 'upload_date', 'file_size_mb']
    list_filter = ['processing_status', 'upload_date', 'content_type']
    search_fields = ['original_filename', 'user__email', 'user__username']
    readonly_fields = ['id', 'upload_date', 'processed_date', 'file_size', 'content_type']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'original_filename', 'file_size', 'content_type')
        }),
        ('Estado de Procesamiento', {
            'fields': ('processing_status', 'error_message')
        }),
        ('Metadatos', {
            'fields': ('rows_count', 'columns_count', 'analysis_data')
        }),
        ('Timestamps', {
            'fields': ('upload_date', 'processed_date'),
            'classes': ('collapse',)
        }),
        ('Azure Storage', {
            'fields': ('azure_blob_url', 'azure_blob_name'),
            'classes': ('collapse',)
        })
    )
    
    def file_size_mb(self, obj):
        """Mostrar tamaño en MB"""
        return f"{obj.file_size_mb} MB" if hasattr(obj, 'file_size_mb') else "N/A"
    file_size_mb.short_description = 'Tamaño (MB)'

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'report_type', 'status', 'created_at', 'csv_file_name']
    list_filter = ['status', 'report_type', 'created_at']
    search_fields = ['title', 'user__email', 'user__username', 'description']
    
    # FIX: Usar solo campos que existen en el modelo Report
    readonly_fields = ['id', 'created_at', 'completed_at']  # Removido 'updated_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'csv_file', 'title', 'description', 'report_type')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Archivos Generados', {
            'fields': ('pdf_file_url', 'html_preview_url'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('analysis_data', 'generation_time_seconds', 'pages_count', 'download_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at', 'expires_at'),
            'classes': ('collapse',)
        })
    )
    
    def csv_file_name(self, obj):
        """Mostrar nombre del archivo CSV"""
        return obj.csv_file.original_filename if obj.csv_file else "Sin archivo"
    csv_file_name.short_description = 'Archivo CSV'
    
    def get_queryset(self, request):
        """Optimizar queries con select_related"""
        return super().get_queryset(request).select_related('user', 'csv_file')

# Personalización adicional del admin
admin.site.site_header = "Azure Reports Platform Admin"
admin.site.site_title = "Azure Reports Admin"
admin.site.index_title = "Panel de Administración"