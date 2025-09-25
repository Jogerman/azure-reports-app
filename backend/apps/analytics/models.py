# apps/analytics/models.py
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class UserActivity(models.Model):
    """Seguimiento de actividad de usuarios"""
    ACTIVITY_TYPES = [
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('upload_csv', 'Subida de CSV'),
        ('generate_report', 'Generación de reporte'),
        ('download_report', 'Descarga de reporte'),
        ('view_dashboard', 'Ver dashboard'),
        ('api_call', 'Llamada API'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=255)
    
    # Metadatos
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Datos adicionales
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'analytics_activity'
        ordering = ['-timestamp']
        verbose_name = 'Actividad de Usuario'
        verbose_name_plural = 'Actividades de Usuario'
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()}"