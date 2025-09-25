// src/components/common/Header.jsx
import React, { useState } from 'react';
import { Menu, Search, Bell, User, ChevronDown } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { AnimatePresence } from 'framer-motion';

const Header = ({ onMenuClick }) => {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleSearch = (e) => {
    e.preventDefault();
    // Implementar búsqueda
    console.log('Searching for:', searchQuery);
  };

  return (
    <div className="relative z-10 flex-shrink-0 flex h-16 bg-white border-b border-gray-200 shadow-sm">
      {/* Botón de menú móvil */}
      <button
        className="px-4 border-r border-gray-200 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 lg:hidden"
        onClick={onMenuClick}
      >
        <Menu className="h-6 w-6" />
      </button>

      <div className="flex-1 px-4 flex justify-between items-center">
        {/* Barra de búsqueda */}
        <div className="flex-1 flex max-w-lg">
          <form onSubmit={handleSearch} className="w-full flex md:ml-0">
            <label htmlFor="search_field" className="sr-only">
              Buscar
            </label>
            <div className="relative w-full text-gray-400 focus-within:text-gray-600">
              <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                <Search className="h-5 w-5" />
              </div>
              <input
                id="search_field"
                className="block w-full h-full pl-10 pr-3 py-2 border-transparent text-gray-900 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-0 focus:border-transparent bg-gray-50 rounded-lg transition-colors"
                placeholder="Buscar reportes, archivos..."
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </form>
        </div>

        {/* Acciones del usuario */}
        <div className="ml-4 flex items-center md:ml-6 space-x-3">
          {/* Notificaciones */}
          <div className="relative">
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-full transition-colors relative"
            >
              <Bell className="h-5 w-5" />
              {/* Badge de notificaciones */}
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                3
              </span>
            </button>

            {/* Dropdown de notificaciones */}
            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
                >
                  <div className="p-4 border-b border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-900">Notificaciones</h3>
                  </div>
                  <div className="max-h-64 overflow-y-auto">
                    <div className="p-4 hover:bg-gray-50 border-b border-gray-100">
                      <p className="text-sm text-gray-900">Reporte completado</p>
                      <p className="text-xs text-gray-500">Tu reporte "Análisis Q3" está listo para descargar</p>
                      <p className="text-xs text-gray-400 mt-1">Hace 5 minutos</p>
                    </div>
                    <div className="p-4 hover:bg-gray-50 border-b border-gray-100">
                      <p className="text-sm text-gray-900">Archivo procesado</p>
                      <p className="text-xs text-gray-500">El archivo "datos_ventas.csv" ha sido analizado</p>
                      <p className="text-xs text-gray-400 mt-1">Hace 1 hora</p>
                    </div>
                    <div className="p-4 hover:bg-gray-50">
                      <p className="text-sm text-gray-900">Nuevo insight disponible</p>
                      <p className="text-xs text-gray-500">Se encontraron 5 recomendaciones de optimización</p>
                      <p className="text-xs text-gray-400 mt-1">Hace 2 horas</p>
                    </div>
                  </div>
                  <div className="p-3 border-t border-gray-200">
                    <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                      Ver todas las notificaciones
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Avatar del usuario */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              {user?.profile_picture ? (
                <img
                  className="h-8 w-8 rounded-full object-cover"
                  src={user.profile_picture}
                  alt=""
                />
              ) : (
                <div className="h-8 w-8 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
              )}
              
              <div className="hidden md:block text-left">
                <div className="text-sm font-medium text-gray-900">
                  {user?.first_name ? `${user.first_name} ${user.last_name}` : user?.username}
                </div>
                <div className="text-xs text-gray-500">
                  {user?.department || 'Usuario'}
                </div>
              </div>
              
              <ChevronDown className="h-4 w-4 text-gray-400" />
            </button>

            {/* Dropdown del usuario */}
            <AnimatePresence>
              {showUserMenu && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
                >
                  <div className="p-2">
                    <a
                      href="/app/profile"
                      className="block px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                    >
                      Mi Perfil
                    </a>
                    <a
                      href="/app/settings"
                      className="block px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                    >
                      Configuración
                    </a>
                    <div className="border-t border-gray-100 my-1"></div>
                    <button
                      onClick={() => {/* logout logic */}}
                      className="block w-full text-left px-3 py-2 text-sm text-red-700 hover:bg-red-50 rounded-md"
                    >
                      Cerrar Sesión
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;