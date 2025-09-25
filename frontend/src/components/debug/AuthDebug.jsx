// src/components/debug/AuthDebug.jsx - Componente para debuggear autenticación
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Key, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle, 
  Eye, 
  EyeOff,
  User,
  Clock
} from 'lucide-react';

const AuthDebug = ({ isOpen, onClose }) => {
  const [authState, setAuthState] = useState(null);
  const [showTokens, setShowTokens] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Función para obtener estado completo de auth
  const getAuthState = () => {
    const accessToken = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
    
    let tokenInfo = null;
    let isExpired = false;
    
    if (accessToken) {
      try {
        const payload = JSON.parse(atob(accessToken.split('.')[1]));
        const now = Date.now() / 1000;
        isExpired = payload.exp < now;
        
        tokenInfo = {
          user_id: payload.user_id,
          username: payload.username,
          exp: new Date(payload.exp * 1000).toLocaleString(),
          iat: new Date(payload.iat * 1000).toLocaleString(),
          isExpired
        };
      } catch (error) {
        console.error('Error parsing token:', error);
      }
    }
    
    return {
      hasAccessToken: !!accessToken,
      hasRefreshToken: !!refreshToken,
      accessToken,
      refreshToken,
      tokenInfo,
      isExpired,
      storageContents: {
        localStorage: { ...localStorage },
        sessionStorage: { ...sessionStorage }
      }
    };
  };

  // Actualizar estado
  const updateAuthState = () => {
    setAuthState(getAuthState());
  };

  // Test de endpoints
  const testEndpoint = async (url, name) => {
    const token = localStorage.getItem('access_token');
    
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      return {
        name,
        url,
        status: response.status,
        ok: response.ok,
        statusText: response.statusText
      };
    } catch (error) {
      return {
        name,
        url,
        status: 'ERROR',
        ok: false,
        statusText: error.message
      };
    }
  };

  // Test múltiples endpoints
  const runEndpointTests = async () => {
    const endpoints = [
      { url: 'http://localhost:8000/api/auth/users/profile/', name: 'Profile' },
      { url: 'http://localhost:8000/api/dashboard/stats/', name: 'Dashboard Stats' },
      { url: 'http://localhost:8000/api/reports/', name: 'Reports' },
      { url: 'http://localhost:8000/api/files/', name: 'Files' }
    ];

    const results = await Promise.all(
      endpoints.map(ep => testEndpoint(ep.url, ep.name))
    );

    return results;
  };

  // Refresh token
  const handleRefreshToken = async () => {
    setRefreshing(true);
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      alert('No hay refresh token disponible');
      setRefreshing(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/auth/refresh/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh: refreshToken })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access);
        updateAuthState();
        alert('Token refrescado exitosamente');
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || 'No se pudo refrescar el token'}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setRefreshing(false);
    }
  };

  // Limpiar storage
  const handleClearAuth = () => {
    if (confirm('¿Estás seguro de que quieres limpiar toda la autenticación?')) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      updateAuthState();
      alert('Autenticación limpiada');
    }
  };

  // Test endpoints
  const handleTestEndpoints = async () => {
    const results = await runEndpointTests();
    const message = results.map(r => 
      `${r.name}: ${r.status} ${r.ok ? '✅' : '❌'}`
    ).join('\n');
    alert(`Resultados de endpoints:\n\n${message}`);
  };

  useEffect(() => {
    if (isOpen) {
      updateAuthState();
      // Auto-refresh cada 5 segundos
      const interval = setInterval(updateAuthState, 5000);
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <Key className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              Debug de Autenticación
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
          >
            ✕
          </button>
        </div>

        {/* Contenido */}
        <div className="p-6 space-y-6">
          {/* Estado General */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
              <User className="w-5 h-5 mr-2" />
              Estado de Autenticación
            </h3>
            
            {authState && (
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  {authState.hasAccessToken ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-red-500" />
                  )}
                  <span className="text-sm">
                    Access Token: {authState.hasAccessToken ? 'Presente' : 'Ausente'}
                  </span>
                </div>
                
                <div className="flex items-center space-x-2">
                  {authState.hasRefreshToken ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-red-500" />
                  )}
                  <span className="text-sm">
                    Refresh Token: {authState.hasRefreshToken ? 'Presente' : 'Ausente'}
                  </span>
                </div>
                
                {authState.tokenInfo && (
                  <>
                    <div className="flex items-center space-x-2">
                      {authState.isExpired ? (
                        <AlertCircle className="w-5 h-5 text-orange-500" />
                      ) : (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      )}
                      <span className="text-sm">
                        Estado: {authState.isExpired ? 'Expirado' : 'Válido'}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Clock className="w-5 h-5 text-gray-500" />
                      <span className="text-sm">
                        Usuario: {authState.tokenInfo.username}
                      </span>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Información del Token */}
          {authState?.tokenInfo && (
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">
                Información del Token
              </h3>
              <div className="text-sm space-y-1">
                <p><strong>Usuario ID:</strong> {authState.tokenInfo.user_id}</p>
                <p><strong>Username:</strong> {authState.tokenInfo.username}</p>
                <p><strong>Emitido:</strong> {authState.tokenInfo.iat}</p>
                <p><strong>Expira:</strong> {authState.tokenInfo.exp}</p>
                <p><strong>Estado:</strong> 
                  <span className={authState.isExpired ? 'text-red-600' : 'text-green-600'}>
                    {authState.isExpired ? ' EXPIRADO' : ' VÁLIDO'}
                  </span>
                </p>
              </div>
            </div>
          )}

          {/* Ver Tokens */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900">Tokens</h3>
              <button
                onClick={() => setShowTokens(!showTokens)}
                className="flex items-center text-sm text-blue-600 hover:text-blue-700"
              >
                {showTokens ? <EyeOff className="w-4 h-4 mr-1" /> : <Eye className="w-4 h-4 mr-1" />}
                {showTokens ? 'Ocultar' : 'Mostrar'}
              </button>
            </div>
            
            {showTokens && authState && (
              <div className="space-y-3 text-xs">
                <div>
                  <strong>Access Token:</strong>
                  <div className="bg-white p-2 rounded border mt-1 break-all font-mono">
                    {authState.accessToken || 'No disponible'}
                  </div>
                </div>
                <div>
                  <strong>Refresh Token:</strong>
                  <div className="bg-white p-2 rounded border mt-1 break-all font-mono">
                    {authState.refreshToken || 'No disponible'}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Acciones */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleRefreshToken}
              disabled={refreshing || !authState?.hasRefreshToken}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? 'Refrescando...' : 'Refresh Token'}
            </button>
            
            <button
              onClick={handleTestEndpoints}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <CheckCircle className="w-4 h-4 mr-2" />
              Test Endpoints
            </button>
            
            <button
              onClick={updateAuthState}
              className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Actualizar Estado
            </button>
            
            <button
              onClick={handleClearAuth}
              className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              <AlertCircle className="w-4 h-4 mr-2" />
              Limpiar Auth
            </button>
          </div>

          {/* Instrucciones */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 className="font-semibold text-yellow-800 mb-2">💡 Cómo usar:</h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Si el token está expirado, usa "Refresh Token"</li>
              <li>• Si no hay tokens, necesitas hacer login</li>
              <li>• Usa "Test Endpoints" para verificar conexión con backend</li>
              <li>• Los estados se actualizan automáticamente cada 5 segundos</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default AuthDebug;