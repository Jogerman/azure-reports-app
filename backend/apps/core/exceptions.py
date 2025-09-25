# apps/core/exceptions.py - NUEVO ARCHIVO
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """Manejador personalizado de excepciones para DRF"""
    
    # Llamar al manejador por defecto primero
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log del error
        logger.error(f"API Error: {str(exc)}", exc_info=True)
        
        # Personalizar respuesta
        custom_response_data = {
            'error': True,
            'message': 'Ha ocurrido un error',
            'details': response.data,
            'status_code': response.status_code
        }
        
        # Manejar errores específicos
        if response.status_code == 400:
            custom_response_data['message'] = 'Datos inválidos'
        elif response.status_code == 401:
            custom_response_data['message'] = 'No autorizado'
        elif response.status_code == 403:
            custom_response_data['message'] = 'Permisos insuficientes'
        elif response.status_code == 404:
            custom_response_data['message'] = 'Recurso no encontrado'
        elif response.status_code == 500:
            custom_response_data['message'] = 'Error interno del servidor'
        
        response.data = custom_response_data
    
    return response