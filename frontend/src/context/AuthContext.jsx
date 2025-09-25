// frontend/src/context/AuthContext.jsx - VERSIÓN CORREGIDA
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authService } from '../services/authService';
import toast from 'react-hot-toast';

// Estados del contexto de autenticación
const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  isInitialized: false,
  error: null
};

// Acciones del reducer
const AUTH_ACTIONS = {
  LOADING: 'LOADING',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGOUT: 'LOGOUT',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  UPDATE_USER: 'UPDATE_USER',
  SET_INITIALIZED: 'SET_INITIALIZED'
};

// Reducer para manejar el estado de autenticación
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOADING:
      return {
        ...state,
        isLoading: action.payload
      };
    
    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        isAuthenticated: true,
        isLoading: false,
        isInitialized: true,
        error: null
      };
    
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        isInitialized: true,
        error: null
      };
    
    case AUTH_ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        isLoading: false,
        isInitialized: true
      };
    
    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };
    
    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload },
        isAuthenticated: true,
        isInitialized: true
      };
    
    case AUTH_ACTIONS.SET_INITIALIZED:
      return {
        ...state,
        isInitialized: true,
        isLoading: false
      };
    
    default:
      return state;
  }
};

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Función mejorada para verificar tokens válidos
  const hasValidTokens = () => {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    console.log('🔍 Verificando tokens:', { 
      hasAccess: !!accessToken, 
      hasRefresh: !!refreshToken 
    });
    
    if (!accessToken || !refreshToken) {
      console.log('❌ No hay tokens disponibles');
      return false;
    }

    try {
      // Decodificar el payload del token
      const payload = JSON.parse(atob(accessToken.split('.')[1]));
      const now = Date.now() / 1000;
      
      console.log('🕒 Token expira en:', new Date(payload.exp * 1000));
      console.log('🕒 Hora actual:', new Date(now * 1000));
      
      if (payload.exp < now) {
        console.log('⏰ Access token expirado, necesita renovación');
        return 'refresh_needed';
      }
      
      console.log('✅ Tokens válidos');
      return true;
    } catch (error) {
      console.error('❌ Error parsing token:', error);
      return false;
    }
  };

  // Función mejorada para verificar autenticación
  const checkAuthStatus = async () => {
    console.log('🔄 Iniciando verificación de autenticación...');
    dispatch({ type: AUTH_ACTIONS.LOADING, payload: true });
    
    try {
      const tokenStatus = hasValidTokens();
      
      if (tokenStatus === false) {
        console.log('🚫 No hay tokens válidos, cerrando sesión');
        dispatch({ type: AUTH_ACTIONS.LOGOUT });
        return;
      }

      if (tokenStatus === 'refresh_needed') {
        console.log('🔄 Renovando token...');
        try {
          await authService.refreshToken();
          console.log('✅ Token renovado exitosamente');
        } catch (refreshError) {
          console.error('❌ Error renovando token:', refreshError);
          // Limpiar tokens inválidos
          localStorage.clear();
          dispatch({ type: AUTH_ACTIONS.LOGOUT });
          return;
        }
      }

      // Obtener datos del usuario
      const userData = localStorage.getItem('user_data');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          console.log('👤 Usuario encontrado en localStorage:', user);
          dispatch({ 
            type: AUTH_ACTIONS.LOGIN_SUCCESS, 
            payload: { user } 
          });
        } catch (parseError) {
          console.error('❌ Error parsing user data:', parseError);
          // Datos del usuario corruptos, intentar obtener del backend
          await fetchUserFromBackend();
        }
      } else {
        console.log('🔄 No hay datos de usuario, obteniendo del backend...');
        await fetchUserFromBackend();
      }
    } catch (error) {
      console.error('❌ Error verificando autenticación:', error);
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  };

  // Función para obtener datos del usuario del backend
  const fetchUserFromBackend = async () => {
    try {
      const userData = await authService.getCurrentUser();
      localStorage.setItem('user_data', JSON.stringify(userData));
      dispatch({ 
        type: AUTH_ACTIONS.LOGIN_SUCCESS, 
        payload: { user: userData } 
      });
      console.log('✅ Datos de usuario obtenidos del backend:', userData);
    } catch (error) {
      console.error('❌ Error obteniendo datos del usuario del backend:', error);
      
      // Si falla, crear datos básicos del usuario con la info disponible
      const userId = localStorage.getItem('user_id');
      if (userId) {
        const basicUser = {
          id: userId,
          email: 'usuario@microsoft.com',
          username: 'Usuario',
          auth_method: localStorage.getItem('auth_method') || 'unknown'
        };
        
        localStorage.setItem('user_data', JSON.stringify(basicUser));
        dispatch({ 
          type: AUTH_ACTIONS.LOGIN_SUCCESS, 
          payload: { user: basicUser } 
        });
        console.log('⚠️ Usando datos básicos del usuario:', basicUser);
      } else {
        // Si no hay ninguna info, hacer logout
        dispatch({ type: AUTH_ACTIONS.LOGOUT });
      }
    }
  };

  // Verificar autenticación al cargar la app
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const login = async (credentials) => {
    dispatch({ type: AUTH_ACTIONS.LOADING, payload: true });
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
    
    try {
      const response = await authService.login(credentials);
      
      // Guardar timestamp de autenticación
      localStorage.setItem('auth_timestamp', Date.now().toString());
      localStorage.setItem('auth_method', 'local');
      
      dispatch({ 
        type: AUTH_ACTIONS.LOGIN_SUCCESS, 
        payload: { user: response.user } 
      });
      
      toast.success(`¡Bienvenido, ${response.user?.username || 'usuario'}!`);
      return response;
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.error || 
                          error.message ||
                          'Error al iniciar sesión';
      
      dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: errorMessage });
      toast.error(errorMessage);
      throw error;
    }
  };

  const register = async (userData) => {
    dispatch({ type: AUTH_ACTIONS.LOADING, payload: true });
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
    
    try {
      const response = await authService.register(userData);
      toast.success('Cuenta creada exitosamente. Por favor inicia sesión.');
      return response;
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.error || 
                          error.message ||
                          'Error al crear cuenta';
      
      dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: errorMessage });
      toast.error(errorMessage);
      throw error;
    } finally {
      dispatch({ type: AUTH_ACTIONS.SET_INITIALIZED });
    }
  };

  const logout = async () => {
    dispatch({ type: AUTH_ACTIONS.LOADING, payload: true });
    
    try {
      await authService.logout();
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      // Limpiar todos los datos de autenticación
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('user_data');
      localStorage.removeItem('auth_timestamp');
      localStorage.removeItem('auth_method');
      
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
      toast.success('Sesión cerrada exitosamente');
    }
  };

  const updateUser = (userData) => {
    console.log('Actualizando usuario en contexto:', userData);
    
    // Actualizar también en localStorage
    const existingUserData = localStorage.getItem('user_data');
    if (existingUserData) {
      try {
        const currentUser = JSON.parse(existingUserData);
        const updatedUser = { ...currentUser, ...userData };
        localStorage.setItem('user_data', JSON.stringify(updatedUser));
      } catch (error) {
        console.error('Error actualizando user data:', error);
        localStorage.setItem('user_data', JSON.stringify(userData));
      }
    } else {
      localStorage.setItem('user_data', JSON.stringify(userData));
    }

    dispatch({ type: AUTH_ACTIONS.UPDATE_USER, payload: userData });
  };

  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Valor del contexto
  const value = {
    ...state,
    login,
    register,
    logout,
    updateUser,
    clearError,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook personalizado para usar el contexto de autenticación
// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  
  return context;
};

export default AuthContext;