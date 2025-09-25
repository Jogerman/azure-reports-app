// src/components/debug/DebugButton.jsx - Botón flotante para debug
import React, { useState } from 'react';
import { Bug, Key, Database, Activity } from 'lucide-react';
import AuthDebug from './AuthDebug';

const DebugButton = () => {
  const [showAuthDebug, setShowAuthDebug] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  // Solo mostrar en desarrollo
  if (process.env.NODE_ENV === 'production') {
    return null;
  }

  return (
    <>
      {/* Botón flotante principal */}
      <div className="fixed bottom-4 right-4 z-40">
        <div className="relative">
          {/* Menú de opciones */}
          {showMenu && (
            <div className="absolute bottom-16 right-0 bg-white rounded-lg shadow-lg border border-gray-200 p-2 min-w-48">
              <button
                onClick={() => {
                  setShowAuthDebug(true);
                  setShowMenu(false);
                }}
                className="w-full flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                <Key className="w-4 h-4 mr-2" />
                Debug Auth
              </button>
              
              <button
                onClick={() => {
                  console.log('=== STORAGE DEBUG ===');
                  console.log('localStorage:', { ...localStorage });
                  console.log('sessionStorage:', { ...sessionStorage });
                  console.log('====================');
                  alert('Revisa la consola para ver el contenido del storage');
                  setShowMenu(false);
                }}
                className="w-full flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                <Database className="w-4 h-4 mr-2" />
                Debug Storage
              </button>
              
              <button
                onClick={() => {
                  console.log('=== NETWORK DEBUG ===');
                  console.log('API Base URL:', 'http://localhost:8000/api');
                  console.log('Current Token:', localStorage.getItem('access_token') ? 'PRESENT' : 'MISSING');
                  console.log('======================');
                  setShowMenu(false);
                }}
                className="w-full flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                <Activity className="w-4 h-4 mr-2" />
                Debug Network
              </button>
              
              <hr className="my-1" />
              
              <button
                onClick={() => {
                  localStorage.clear();
                  sessionStorage.clear();
                  alert('Storage limpiado. Recarga la página.');
                  setShowMenu(false);
                }}
                className="w-full flex items-center px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg"
              >
                <Database className="w-4 h-4 mr-2" />
                Limpiar Todo
              </button>
            </div>
          )}
          
          {/* Botón principal */}
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="w-12 h-12 bg-purple-600 hover:bg-purple-700 text-white rounded-full shadow-lg flex items-center justify-center transition-colors"
            title="Debug Tools"
          >
            <Bug className="w-6 h-6" />
          </button>
        </div>
      </div>

      {/* Modal de debug de auth */}
      <AuthDebug 
        isOpen={showAuthDebug} 
        onClose={() => setShowAuthDebug(false)} 
      />
    </>
  );
};

export default DebugButton;