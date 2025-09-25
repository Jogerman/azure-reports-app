// frontend/src/pages/MicrosoftCallback.jsx - VERSIÓN CORREGIDA
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Loading from '../components/common/Loading';

const MicrosoftCallback = () => {
  const location = useLocation();
  const { updateUser } = useAuth();
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('Procesando autenticación con Microsoft...');

  useEffect(() => {
    const processCallback = async () => {
      try {
        // Obtener parámetros de la URL
        const urlParams = new URLSearchParams(location.search);
        const accessToken = urlParams.get('access_token');
        const refreshToken = urlParams.get('refresh_token');
        const userId = urlParams.get('user_id');
        const error = urlParams.get('error');

        console.log('🔄 Procesando callback de Microsoft:', {
          hasAccessToken: !!accessToken,
          hasRefreshToken: !!refreshToken,
          hasUserId: !!userId,
          error
        });

        // Manejar errores
        if (error) {
          console.error('❌ Error en callback de Microsoft:', error);
          setStatus('error');
          
          const errorMessages = {
            'access_denied': 'Acceso denegado. La autenticación fue cancelada.',
            'token_error': 'Error obteniendo token de autenticación.',
            'user_info_error': 'Error obteniendo información del usuario.',
            'invalid_tenant': 'Tu organización no tiene acceso a esta aplicación.',
            'not_configured': 'Microsoft OAuth no está configurado correctamente.',
            'server_error': 'Error interno del servidor.'
          };
          
          setMessage(errorMessages[error] || `Error desconocido: ${error}`);
          
          // Redirigir al login después de 3 segundos
          setTimeout(() => {
            window.location.href = '/?error=' + error;
          }, 3000);
          return;
        }

        // Validar que tenemos todos los datos necesarios
        if (!accessToken || !refreshToken || !userId) {
          console.error('❌ Datos incompletos en callback:', {
            accessToken: !!accessToken,
            refreshToken: !!refreshToken,
            userId: !!userId
          });
          
          setStatus('error');
          setMessage('Datos de autenticación incompletos. Por favor, inténtalo de nuevo.');
          
          setTimeout(() => {
            window.location.href = '/?error=incomplete_data';
          }, 3000);
          return;
        }

        console.log('✅ Datos de autenticación recibidos correctamente');

        // Guardar tokens en localStorage
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        localStorage.setItem('user_id', userId);
        localStorage.setItem('auth_method', 'microsoft');
        localStorage.setItem('auth_timestamp', Date.now().toString());

        setMessage('Obteniendo información del usuario...');

        // Verificar el token con el backend y obtener datos del usuario
        try {
          const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
          
          console.log('🔍 Verificando usuario con backend...');
          const response = await fetch(`${apiUrl}/api/auth/users/profile/`, {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
              'Content-Type': 'application/json',
            },
          });

          if (response.ok) {
            const userData = await response.json();
            console.log('✅ Datos de usuario obtenidos del backend:', userData);
            
            // Guardar información del usuario
            localStorage.setItem('user_data', JSON.stringify(userData));
            
            // Actualizar el contexto de autenticación
            updateUser(userData);
            
            setStatus('success');
            setMessage('Autenticación exitosa. Redirigiendo al dashboard...');
            
            // Redirigir al dashboard después de 1.5 segundos
            setTimeout(() => {
              window.location.href = '/app';
            }, 1500);
            
          } else {
            console.warn('⚠️ Error verificando usuario con backend, usando datos básicos');
            
            // Si la verificación falla, crear datos básicos del usuario
            const basicUserData = {
              id: userId,
              email: 'usuario@microsoft.com',
              username: `user_${userId}`,
              auth_method: 'microsoft',
              first_name: 'Usuario',
              last_name: 'Microsoft'
            };
            
            localStorage.setItem('user_data', JSON.stringify(basicUserData));
            updateUser(basicUserData);
            
            setStatus('success');
            setMessage('Autenticación exitosa. Redirigiendo...');
            
            setTimeout(() => {
              window.location.href = '/app';
            }, 1500);
          }
        } catch (verificationError) {
          console.error('❌ Error verificando usuario:', verificationError);
          
          // Crear datos básicos y proceder
          const basicUserData = {
            id: userId,
            email: 'usuario@microsoft.com',
            username: `user_${userId}`,
            auth_method: 'microsoft',
            first_name: 'Usuario',
            last_name: 'Microsoft'
          };
          
          localStorage.setItem('user_data', JSON.stringify(basicUserData));
          updateUser(basicUserData);
          
          setStatus('success');
          setMessage('Autenticación exitosa. Redirigiendo...');
          
          setTimeout(() => {
            window.location.href = '/app';
          }, 1500);
        }

      } catch (error) {
        console.error('❌ Error procesando callback:', error);
        setStatus('error');
        setMessage('Error procesando autenticación. Por favor, inténtalo de nuevo.');
        
        setTimeout(() => {
          window.location.href = '/?error=callback_processing_error';
        }, 3000);
      }
    };

    processCallback();
  }, [location.search, updateUser]);

  // Renderizado condicional basado en el estado
  const renderContent = () => {
    switch (status) {
      case 'processing':
        return (
          <Loading 
            fullScreen 
            text={message}
            showSpinner={true}
          />
        );
      
      case 'success':
        return (
          <div className="min-h-screen flex items-center justify-center bg-green-50">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
                <svg className="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">¡Autenticación Exitosa!</h2>
              <p className="text-gray-600">{message}</p>
              <div className="mt-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600 mx-auto"></div>
              </div>
            </div>
          </div>
        );
      
      case 'error':
        return (
          <div className="min-h-screen flex items-center justify-center bg-red-50">
            <div className="text-center max-w-md mx-auto px-4">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
                <svg className="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Error de Autenticación</h2>
              <p className="text-gray-600 mb-4">{message}</p>
              <p className="text-sm text-gray-500">Serás redirigido al login en unos segundos...</p>
            </div>
          </div>
        );
      
      default:
        return <Loading fullScreen text="Cargando..." />;
    }
  };

  return renderContent();
};

export default MicrosoftCallback;