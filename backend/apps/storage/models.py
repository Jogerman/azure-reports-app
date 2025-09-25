from django.db import models

# Create your models here.
# apps/storage/models.py
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class StorageFile(models.Model):
    """Gestión de archivos en Azure Blob Storage"""
    FILE_TYPES = [
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('image', 'Imagen'),
        ('document', 'Documento'),
        ('other', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='storage_files')
    
    # Información del archivo
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FILE_TYPES)
    file_size = models.PositiveIntegerField()
    content_type = models.CharField(max_length=100)
    
    # Azure Storage info
    container_name = models.CharField(max_length=100)
    blob_name = models.CharField(max_length=255, unique=True)
    blob_url = models.URLField()
    
    # Metadatos
    upload_date = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    access_count = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=False)
    
    # Tags y descripción
    tags = models.JSONField(default=list)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'storage_file'
        ordering = ['-upload_date']
        verbose_name = 'Archivo de Storage'
        verbose_name_plural = 'Archivos de Storage'
        indexes = [
            models.Index(fields=['user', 'file_type']),
            models.Index(fields=['upload_date']),
            models.Index(fields=['blob_name']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.file_type})"
