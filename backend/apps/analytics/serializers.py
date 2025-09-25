# backend/apps/analytics/serializers.py 
from rest_framework import serializers
from .models import UserActivity

class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer para actividades de usuario"""
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'activity_type', 'activity_type_display', 'description', 
            'timestamp', 'time_ago', 'metadata'
        ]
        read_only_fields = ['id', 'timestamp', 'activity_type_display', 'time_ago']
    
    def get_time_ago(self, obj):
        """Calcular tiempo transcurrido desde la actividad"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        delta = now - obj.timestamp
        
        if delta < timedelta(minutes=1):
            return "Hace menos de un minuto"
        elif delta < timedelta(hours=1):
            minutes = int(delta.total_seconds() // 60)
            return f"Hace {minutes} minuto{'s' if minutes != 1 else ''}"
        elif delta < timedelta(days=1):
            hours = int(delta.total_seconds() // 3600)
            return f"Hace {hours} hora{'s' if hours != 1 else ''}"
        elif delta < timedelta(days=7):
            days = delta.days
            return f"Hace {days} día{'s' if days != 1 else ''}"
        else:
            return obj.timestamp.strftime("%d/%m/%Y")

class UserActivityCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear actividades de usuario"""
    
    class Meta:
        model = UserActivity
        fields = [
            'activity_type', 'description', 'metadata'
        ]
    
    def create(self, validated_data):
        """Crear actividad con datos del request"""
        request = self.context['request']
        
        activity = UserActivity.objects.create(
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            **validated_data
        )
        
        return activity