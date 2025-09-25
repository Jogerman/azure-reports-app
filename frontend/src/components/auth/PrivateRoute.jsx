// frontend/src/components/auth/PrivateRoute.jsx - VERSIÓN CORREGIDA
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Loading from '../common/Loading';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, isLoading, isInitialized } = useAuth();

  console.log('🔒 PrivateRoute - Estado actual:', {
    isAuthenticated,
    isLoading,
    isInitialized,
    hasTokens: !!(localStorage.getItem('access_token') && localStorage.getItem('refresh_token'))
  });

  // Mostrar loading mientras se verifica la autenticación inicial
  if (isLoading || !isInitialized) {
    console.log('⏳ PrivateRoute - Mostrando loading...');
    return <Loading fullScreen text="Verificando autenticación..." />;
  }

  // Si no está autenticado después de la verificación inicial, redirigir al login
  if (!isAuthenticated) {
    console.log('🚫 PrivateRoute - Usuario no autenticado, redirigiendo a login...');
    return <Navigate to="/" replace />;
  }

  // Si todo está bien, mostrar el contenido protegido
  console.log('✅ PrivateRoute - Usuario autenticado, mostrando contenido...');
  return children;
};

export default PrivateRoute;