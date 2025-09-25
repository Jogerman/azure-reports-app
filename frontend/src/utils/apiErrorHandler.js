// frontend/src/utils/apiErrorHandler.js
export const handleApiError = (error) => {
  console.error('API Error:', error);
  
  // Error de red
  if (!error.response) {
    if (error.code === 'NETWORK_ERROR') {
      return 'Error de conexión. Verifica tu internet.';
    }
    return 'No se pudo conectar con el servidor';
  }
  
  // Errores HTTP específicos
  const status = error.response.status;
  const data = error.response.data;
  
  switch (status) {
    case 400:
      if (data.error) return data.error;
      if (data.detail) return data.detail;
      return 'Datos inválidos';
      
    case 401:
      // Redirigir al login si no está autenticado
      localStorage.clear();
      sessionStorage.clear();
      window.location.href = '/';
      return 'Sesión expirada';
      
    case 403:
      return 'No tienes permisos para realizar esta acción';
      
    case 404:
      return 'Recurso no encontrado';
      
    case 413:
      return 'El archivo es demasiado grande';
      
    case 415:
      return 'Tipo de archivo no soportado';
      
    case 429:
      return 'Demasiadas solicitudes. Intenta más tarde.';
      
    case 500:
      return 'Error interno del servidor';
      
    case 502:
    case 503:
    case 504:
      return 'Servidor temporalmente no disponible';
      
    default:
      if (data.error) return data.error;
      if (data.detail) return data.detail;
      return `Error ${status}: ${error.response.statusText}`;
  }
};