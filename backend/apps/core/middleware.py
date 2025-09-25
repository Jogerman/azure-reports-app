# apps/core/middleware.py - NUEVO ARCHIVO
import logging
import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework import status
from django.db import IntegrityError
from django.conf import settings

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    """Middleware para manejo centralizado de errores"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """Procesar excepciones no manejadas"""
        
        # Log del error
        logger.error(f"Error no manejado: {str(exception)}", exc_info=True)
        
        # Errores de base de datos
        if isinstance(exception, IntegrityError):
            if 'null value in column' in str(exception):
                return JsonResponse({
                    'error': 'Error de datos requeridos',
                    'detail': 'Faltan campos obligatorios',
                    'type': 'validation_error'
                }, status=400)
            
            if 'violates not-null constraint' in str(exception):
                return JsonResponse({
                    'error': 'Error de restricción de base de datos',
                    'detail': 'Campo requerido no puede estar vacío',
                    'type': 'constraint_error'
                }, status=400)
        
        # Errores de validación
        if isinstance(exception, ValidationError):
            return JsonResponse({
                'error': 'Error de validación',
                'detail': str(exception),
                'type': 'validation_error'
            }, status=400)
        
        # Para APIs, devolver JSON
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Error interno del servidor',
                'detail': str(exception) if settings.DEBUG else 'Ha ocurrido un error inesperado',
                'type': 'server_error'
            }, status=500)
        
        # Para otras rutas, dejar que Django maneje
        return None