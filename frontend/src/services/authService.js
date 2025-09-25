// frontend/src/services/authService.js - CORREGIR EL PROBLEMA DE REDIRECCIÓN
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Crear instancia de axios principal
const axiosInstance = axios.create({
  baseURL: `${API_URL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token automáticamente a TODAS las peticiones
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && token !== 'null' && token !== 'undefined') {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log para debugging
    console.log('🌐 Petición API:', {
      url: config.url,
      method: config.method?.toUpperCase(),
      hasToken: !!token,
      headers: config.headers
    });
    
    return config;
  },
  (error) => {
    console.error('❌ Error en interceptor de request:', error);
    return Promise.reject(error);
  }
);

// Variable para evitar loops infinitos en el refresh
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

// Interceptor mejorado para manejar tokens expirados
axiosInstance.interceptors.response.use(
  (response) => {
    console.log('✅ Respuesta API exitosa:', {
      url: response.config.url,
      status: response.status
    });
    return response;
  },
  async (error) => {
    const original = error.config;
    
    console.error('❌ Error en respuesta API:', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.message
    });
    
    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        // Si ya se está renovando el token, añadir a la cola
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          original.headers.Authorization = `Bearer ${token}`;
          return axiosInstance(original);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      original._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!refreshToken) {
        console.error('❌ No hay refresh token disponible');
        authService.clearAuthData();
        // CAMBIO IMPORTANTE: Redirigir a "/" en lugar de "/login"
        window.location.href = '/';
        return Promise.reject(error);
      }

      try {
        console.log('🔄 Intentando renovar token...');
        const response = await axios.post(`${API_URL}/api/auth/refresh/`, {
          refresh: refreshToken
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);
        
        console.log('✅ Token renovado exitosamente');
        
        // Procesar cola de peticiones fallidas
        processQueue(null, access);
        
        // Reintentar petición original
        original.headers.Authorization = `Bearer ${access}`;
        return axiosInstance(original);
        
      } catch (refreshError) {
        console.error('❌ Error renovando token:', refreshError);
        processQueue(refreshError, null);
        authService.clearAuthData();
        // CAMBIO IMPORTANTE: Redirigir a "/" en lugar de "/login"
        window.location.href = '/';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    
    return Promise.reject(error);
  }
);

export const authService = {
  // Login con email y password
  async login(credentials) {
    try {
      console.log('🔑 Intentando login con:', credentials.email);
      const response = await axiosInstance.post('/auth/login/', credentials);
      const { access, refresh, user } = response.data;
      
      // Validar que tenemos todos los datos necesarios
      if (!access || !refresh) {
        throw new Error('Respuesta inválida del servidor: faltan tokens');
      }
      
      // Guardar tokens y datos del usuario
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user_data', JSON.stringify(user));
      localStorage.setItem('auth_timestamp', Date.now().toString());
      localStorage.setItem('auth_method', 'local');
      
      if (user?.id) {
        localStorage.setItem('user_id', user.id.toString());
      }
      
      console.log('✅ Login exitoso:', user);
      return { user, access, refresh };
    } catch (error) {
      console.error('❌ Error en login:', error);
      throw error;
    }
  },

  // Renovar token
  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      throw new Error('No hay refresh token disponible');
    }

    try {
      console.log('🔄 Renovando access token...');
      const response = await axios.post(`${API_URL}/api/auth/refresh/`, {
        refresh: refreshToken
      });

      const { access } = response.data;
      localStorage.setItem('access_token', access);
      
      console.log('✅ Access token renovado');
      return access;
    } catch (error) {
      console.error('❌ Error renovando token:', error);
      throw error;
    }
  },

  // Obtener datos del usuario actual
  async getCurrentUser() {
    try {
      console.log('👤 Obteniendo datos del usuario actual...');
      
      // Primero intentar el endpoint de perfil específico
      let response;
      try {
        response = await axiosInstance.get('/auth/users/profile/');
      } catch (profileError) {
        // Si falla, intentar el endpoint general de usuarios
        console.log('⚠️ Endpoint de perfil no disponible, intentando endpoint general...');
        response = await axiosInstance.get('/auth/users/');
        
        // Si retorna un array, tomar el primer usuario (debería ser el actual)
        if (Array.isArray(response.data)) {
          response.data = response.data[0];
        }
      }
      
      console.log('✅ Datos de usuario obtenidos:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error obteniendo usuario actual:', error);
      throw error;
    }
  },

  // Logout
  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        console.log('🚪 Cerrando sesión en el servidor...');
        await axiosInstance.post('/auth/logout/', {
          refresh: refreshToken
        });
      }
    } catch (error) {
      console.error('⚠️ Error cerrando sesión en servidor (continuando con logout local):', error);
    } finally {
      // Siempre limpiar datos locales
      this.clearAuthData();
    }
  },

  // Limpiar datos de autenticación
  clearAuthData() {
    console.log('🧹 Limpiando datos de autenticación...');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_data');
    localStorage.removeItem('auth_timestamp');
    localStorage.removeItem('auth_method');
  },

  // Verificar si el usuario está autenticado
  isAuthenticated() {
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    return !!(token && refreshToken);
  },

  // Obtener token actual
  getToken() {
    return localStorage.getItem('access_token');
  },

  // Obtener datos del usuario desde localStorage
  getUserData() {
    const userData = localStorage.getItem('user_data');
    if (userData) {
      try {
        return JSON.parse(userData);
      } catch (error) {
        console.error('❌ Error parsing user data:', error);
        return null;
      }
    }
    return null;
  }
};

// Exportar también la instancia de axios para uso directo si es necesario
export { axiosInstance };
export default authService;