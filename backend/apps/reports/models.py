# apps/reports/models.py - VERSIÓN MEJORADA
from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import os

User = get_user_model()

class CSVFile(models.Model):
    """Archivos CSV subidos para análisis"""
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='csv_files')
    
    # Información del archivo
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    content_type = models.CharField(max_length=100, default='text/csv')
    
    # Azure Storage info
    azure_blob_url = models.URLField(null=True, blank=True)
    azure_blob_name = models.CharField(max_length=255, null=True, blank=True)
    
    # Estado de procesamiento
    processing_status = models.CharField(
        max_length=20, 
        choices=PROCESSING_STATUS_CHOICES, 
        default='pending'
    )
    error_message = models.TextField(blank=True)
    
    # Metadatos del análisis
    rows_count = models.PositiveIntegerField(null=True, blank=True)
    columns_count = models.PositiveIntegerField(null=True, blank=True)
    analysis_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    upload_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'reports_csvfile'
        ordering = ['-upload_date']
        verbose_name = 'Archivo CSV'
        verbose_name_plural = 'Archivos CSV'
        indexes = [
            models.Index(fields=['user', 'processing_status']),
            models.Index(fields=['upload_date']),
        ]

    def __str__(self):
        return f"{self.original_filename} - {self.user.email}"

    def save(self, *args, **kwargs):
        if self.processing_status == 'completed' and not self.processed_date:
            self.processed_date = timezone.now()
        super().save(*args, **kwargs)

    @property
    def file_extension(self):
        """Obtener extensión del archivo"""
        return os.path.splitext(self.original_filename)[1].lower()
    
    @property
    def is_valid_csv(self):
        """Verificar si es un CSV válido"""
        return self.file_extension in ['.csv', '.xlsx', '.xls']
    
    @property
    def file_size_mb(self):
        """Tamaño del archivo en MB"""
        return round(self.file_size / (1024 * 1024), 2)

class Report(models.Model):
    """Reportes generados"""
    STATUS_CHOICES = [
        ('generating', 'Generando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('expired', 'Expirado'),
    ]
    
    REPORT_TYPES = [
        ('executive', 'Ejecutivo'),
        ('detailed', 'Detallado'),
        ('summary', 'Resumen'),
        ('comprehensive', 'Análisis Completo'),
        ('custom', 'Personalizado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    
    # FIX: Hacer csv_file opcional para mayor flexibilidad
    csv_file = models.ForeignKey(
        CSVFile, 
        on_delete=models.SET_NULL,  # No CASCADE para preservar reportes
        related_name='reports',
        null=True,  # Permitir null
        blank=True  # Permitir blank en forms
    )
    
    # Información básica
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, default='executive')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating')
    
    # Archivos generados
    pdf_file_url = models.URLField(null=True, blank=True)
    html_preview_url = models.URLField(null=True, blank=True)
    
    # Metadatos
    analysis_data = models.JSONField(default=dict, blank=True)
    generation_time_seconds = models.PositiveIntegerField(null=True, blank=True)
    pages_count = models.PositiveIntegerField(null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'reports_report'
        ordering = ['-created_at']
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['report_type']),
            models.Index(fields=['csv_file']),  # Índice para csv_file
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def source_file_name(self):
        """Nombre del archivo fuente"""
        return self.csv_file.original_filename if self.csv_file else 'N/A'
    
    @property
    def is_expired(self):
        """Verificar si el reporte ha expirado"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def get_csv_file_path(self):
        """Retorna la ruta del archivo CSV asociado"""
        if self.csv_file and self.csv_file.azure_blob_url:
            return self.csv_file.azure_blob_url
        return None
    
    def get_analysis_summary(self):
        """Retorna un resumen del análisis si está disponible"""
        if hasattr(self, 'analysis_data') and self.analysis_data:
            try:
                analysis = json.loads(self.analysis_data) if isinstance(self.analysis_data, str) else self.analysis_data
                return {
                    'total_actions': analysis.get('total_recommendations', 0),
                    'high_priority': analysis.get('high_priority_count', 0),
                    'categories': analysis.get('category_distribution', {}),
                    'has_cost_data': analysis.get('has_cost_optimization', False)
                }
            except (json.JSONDecodeError, AttributeError):
                pass
        return None
    
    @property
    def enhanced_html_available(self):
        """Verifica si el reporte tiene datos suficientes para HTML mejorado"""
        return bool(self.csv_file and self.csv_file.file)
    
    def get_preview_metrics(self):
        """Retorna métricas para preview rápido"""
        summary = self.get_analysis_summary()
        if summary:
            return {
                'total_recommendations': summary['total_actions'],
                'high_priority_count': summary['high_priority'],
                'categories_count': len(summary['categories']),
                'has_cost_optimization': summary['has_cost_data']
            }
        return {}