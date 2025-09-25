// src/config/api.js - VERSIÓN CORREGIDA FINAL SIN DUPLICACIONES
export const API_CONFIG = {
  // URL base del backend - CORREGIDA
  BASE_URL: (() => {
    // Para producción
    if (window.location.hostname !== 'localhost') {
      return window.location.origin + '/api';
    }
    
    // Para desarrollo local - CORREGIDO
    return 'http://localhost:8000/api';
  })(),
  
  // Timeouts
  TIMEOUT: 30000, // 30 segundos
  UPLOAD_TIMEOUT: 300000, // 5 minutos para uploads
  
  ENDPOINTS: {
    AUTH: {
      LOGIN: '/auth/login/',
      REGISTER: '/auth/register/',
      LOGOUT: '/auth/logout/',
      REFRESH: '/auth/refresh/',
      PROFILE: '/auth/users/profile/',
      MICROSOFT_LOGIN: '/auth/microsoft/login/',
      MICROSOFT_CALLBACK: '/auth/microsoft/callback/',
    },
    
    FILES: {
      UPLOAD: '/files/upload/',
      LIST: '/files/',
      DETAIL: '/files/:id/',
      DELETE: '/files/:id/',
      DOWNLOAD: '/files/:id/download/',
    },
    
    REPORTS: {
      GENERATE: '/reports/generate/',
      LIST: '/reports/',
      DETAIL: '/reports/:id/',
      HTML: '/reports/:id/html/',
      DOWNLOAD: '/reports/:id/download/',
      DELETE: '/reports/:id/',
    },
    
    DASHBOARD: {
      STATS: '/dashboard/stats/',
      ACTIVITY: '/dashboard/activity/',
    },
    
    HEALTH: '/health/',
  },
  
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  
  // Configuración de retry
  RETRY: {
    ATTEMPTS: 3,
    DELAY: 1000, // 1 segundo
    EXPONENTIAL: true,
  },
};

// Asegurate de que todas las funciones usen BASE_URL correctamente
export const fetchWithAuth = async (url, options = {}) => {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  
  // Construir URL completa si es una URL relativa
  const fullUrl = url.startsWith('http') ? url : `${API_CONFIG.BASE_URL}${url}`;
  
  console.log('🔗 API Request to:', fullUrl); // Para debug
  
  const config = {
    ...options,
    headers: {
      ...API_CONFIG.DEFAULT_HEADERS,
      ...options.headers,
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    timeout: API_CONFIG.TIMEOUT,
  };

  try {
    const response = await fetch(fullUrl, config);
    
    if (response.status === 401) {
      console.error('🔐 Token inválido o expirado');
      localStorage.removeItem('access_token');
      sessionStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      sessionStorage.removeItem('refresh_token');
      window.location.href = '/';
      throw new Error('Sesión expirada');
    }
    
    return response;
  } catch (error) {
    console.error('❌ API Error:', error);
    throw error;
  }
};

// Helper para construir URLs
export const buildApiUrl = (endpoint, params = {}) => {
  // Si ya es una URL completa, devolverla tal como está
  if (endpoint.startsWith('http')) {
    return endpoint;
  }
  
  // Si no empieza con /, agregarlo
  if (!endpoint.startsWith('/')) {
    endpoint = '/' + endpoint;
  }
  
  let url = API_CONFIG.BASE_URL + endpoint;
  
  // Reemplazar parámetros (:id, etc.)
  Object.entries(params).forEach(([key, value]) => {
    url = url.replace(`:${key}`, value);
  });
  
  return url;
};

// Helper para construir URLs (alias para compatibilidad)
export const buildUrl = buildApiUrl;

// Helper para obtener headers con autenticación
export const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  
  return {
    ...API_CONFIG.DEFAULT_HEADERS,
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

// Helper para manejar respuestas de API
export const handleApiResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ 
      detail: 'Error de conexión con el servidor' 
    }));
    
    // Manejar errores específicos
    switch (response.status) {
      case 401:
        // Token expirado o inválido
        localStorage.removeItem('access_token');
        sessionStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        sessionStorage.removeItem('refresh_token');
        window.location.href = '/';
        throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
        
      case 403:
        throw new Error('No tienes permisos para realizar esta acción.');
        
      case 404:
        throw new Error('Recurso no encontrado.');
        
      case 413:
        throw new Error('El archivo es demasiado grande. Máximo 50MB.');
        
      case 422:
        throw new Error('Datos inválidos. Verifica la información enviada.');
        
      case 429:
        throw new Error('Demasiadas solicitudes. Intenta nuevamente en unos minutos.');
        
      case 500:
        throw new Error('Error interno del servidor. Intenta nuevamente.');
        
      default:
        throw new Error(error.detail || error.message || 'Error desconocido');
    }
  }
  
  return response.json();
};

// Helper para realizar peticiones con retry
export const fetchWithRetry = async (url, options = {}, retryCount = 0) => {
  try {
    const response = await fetch(url, {
      timeout: options.timeout || API_CONFIG.TIMEOUT,
      ...options,
    });
    
    return await handleApiResponse(response);
  } catch (error) {
    if (retryCount < API_CONFIG.RETRY.ATTEMPTS) {
      const delay = API_CONFIG.RETRY.EXPONENTIAL 
        ? API_CONFIG.RETRY.DELAY * Math.pow(2, retryCount)
        : API_CONFIG.RETRY.DELAY;
        
      await new Promise(resolve => setTimeout(resolve, delay));
      return fetchWithRetry(url, options, retryCount + 1);
    }
    
    throw error;
  }
};

// Detectar entorno
const isProduction = typeof window !== 'undefined' && window.location.hostname !== 'localhost';
const isDevelopment = !isProduction;

// Configuración específica para desarrollo (OPCIONAL - solo para debugging)
export const DEV_CONFIG = {
  // Debug info
  ENABLE_LOGGING: isDevelopment,
  ENABLE_DEBUGGING: isDevelopment,
  
  // URLs para debugging
  BACKEND_URL: API_CONFIG.BASE_URL,
  FRONTEND_URL: isDevelopment ? 'http://localhost:5173' : window.location.origin,
};

export default API_CONFIG;