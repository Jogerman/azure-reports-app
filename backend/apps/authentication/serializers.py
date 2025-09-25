# apps/authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'department', 'job_title', 'phone_number', 'profile_picture',
            'is_azure_user', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_azure_user', 'created_at', 'updated_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'department', 'job_title'
        ]
    
    def validate(self, data):
        """Validar que las contraseñas coincidan"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data
    
    def create(self, validated_data):
        """Crear nuevo usuario"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            is_azure_user=False,
            **validated_data
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para JWT tokens"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregar información personalizada al token
        token['email'] = user.email
        token['is_azure_user'] = user.is_azure_user
        token['department'] = user.department
        
        return token
    
    def validate(self, attrs):
        """Validación personalizada con logging de actividad"""
        data = super().validate(attrs)
        
        # Log de actividad
        from apps.analytics.models import UserActivity
        UserActivity.objects.create(
            user=self.user,
            activity_type='login',
            description=f'Login exitoso desde {self.context["request"].META.get("REMOTE_ADDR")}',
            ip_address=self.context["request"].META.get('REMOTE_ADDR', ''),
            user_agent=self.context["request"].META.get('HTTP_USER_AGENT', ''),
        )
        
        return data
