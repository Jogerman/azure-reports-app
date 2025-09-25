// src/components/common/Sidebar.jsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  History,
  Database,
  Settings,
  User,
  LogOut,
  BarChart3,
  Upload,
  TrendingUp,
  Shield,
  X
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { cn } from '../../utils/helpers';

const navigation = [
  { name: 'Dashboard', href: '/app', icon: LayoutDashboard },
  { name: 'Crear Reporte', href: '/app/reports', icon: FileText },
  { name: 'Historial', href: '/app/history', icon: History },
  { name: 'Almacenamiento', href: '/app/storage', icon: Database },
];

const Sidebar = ({ onClose }) => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    if (onClose) onClose();
  };

  return (
    <div className="flex flex-col h-full bg-white border-r border-gray-200 shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center shadow-lg">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
          </div>
          <div className="ml-3">
            <h1 className="text-xl font-bold text-gray-900">
              Azure Reports
            </h1>
            <p className="text-xs text-gray-500">
              Análisis inteligente de datos
            </p>
          </div>
        </div>
        
        {/* Botón cerrar móvil */}
        {onClose && (
          <button
            onClick={onClose}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        )}
      </div>

      {/* Navegación principal */}
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "relative group flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200",
                isActive
                  ? "bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg"
                  : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
              )}
              onClick={onClose}
            >
              <item.icon
                className={cn(
                  "mr-3 h-5 w-5 transition-colors",
                  isActive ? "text-white" : "text-gray-400 group-hover:text-gray-600"
                )}
              />
              {item.name}
              
              {/* Indicador activo */}
              {isActive && (
                <motion.div
                  className="absolute right-2 w-2 h-2 bg-white rounded-full"
                  layoutId="activeIndicator"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Stats rápidas */}
      <div className="px-4 py-4 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gradient-to-r from-green-50 to-green-100 p-3 rounded-lg">
            <div className="flex items-center">
              <TrendingUp className="w-4 h-4 text-green-600 mr-2" />
              <div>
                <p className="text-xs text-green-600 font-medium">Reportes</p>
                <p className="text-lg font-bold text-green-700">12</p>
              </div>
            </div>
          </div>
          <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-3 rounded-lg">
            <div className="flex items-center">
              <Shield className="w-4 h-4 text-blue-600 mr-2" />
              <div>
                <p className="text-xs text-blue-600 font-medium">Seguridad</p>
                <p className="text-lg font-bold text-blue-700">98%</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Usuario y configuración */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center mb-4">
          <div className="flex-shrink-0">
            {user?.profile_picture ? (
              <img
                className="w-10 h-10 rounded-full object-cover"
                src={user.profile_picture}
                alt={user.first_name || user.username}
              />
            ) : (
              <div className="w-10 h-10 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
          <div className="ml-3 min-w-0 flex-1">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.first_name ? `${user.first_name} ${user.last_name}` : user?.username}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {user?.job_title || user?.email}
            </p>
          </div>
        </div>

        <div className="space-y-1">
          <Link
            to="/app/profile"
            className="group flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 hover:text-gray-900 transition-colors"
            onClick={onClose}
          >
            <User className="mr-3 h-4 w-4 text-gray-400 group-hover:text-gray-600" />
            Perfil
          </Link>
          
          <Link
            to="/app/settings"
            className="group flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 hover:text-gray-900 transition-colors"
            onClick={onClose}
          >
            <Settings className="mr-3 h-4 w-4 text-gray-400 group-hover:text-gray-600" />
            Configuración
          </Link>
          
          <button
            onClick={handleLogout}
            className="w-full group flex items-center px-3 py-2 text-sm font-medium text-red-700 rounded-lg hover:bg-red-50 hover:text-red-900 transition-colors"
          >
            <LogOut className="mr-3 h-4 w-4 text-red-400 group-hover:text-red-600" />
            Cerrar Sesión
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
