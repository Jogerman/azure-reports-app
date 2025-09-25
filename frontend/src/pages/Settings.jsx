/* eslint-disable no-unused-vars */
// src/pages/Settings.jsx
import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Bell, 
  Shield, 
  Palette,
  Database,
  Key,
  Mail,
  Globe,
  Save
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const Settings = () => {
  const { _user, _updateProfile } = useAuth();
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      push: false,
      reports: true,
      security: true,
    },
    preferences: {
      theme: 'light',
      language: 'es',
      timezone: 'America/Santo_Domingo',
      defaultReportType: 'executive',
    },
    privacy: {
      shareAnalytics: false,
      publicProfile: false,
      dataRetention: '90',
    }
  });

  const tabs = [
    { id: 'general', label: 'General', icon: SettingsIcon },
    { id: 'notifications', label: 'Notificaciones', icon: Bell },
    { id: 'security', label: 'Seguridad', icon: Shield },
    { id: 'privacy', label: 'Privacidad', icon: Key },
  ];

  const handleSettingChange = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const handleSave = async () => {
    try {
      // Aquí enviarías los settings al backend
      toast.success('Configuración guardada exitosamente');
    } catch (_error) {
      toast.error('Error al guardar la configuración');
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-600 to-gray-800 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Configuración</h1>
            <p className="text-gray-200 text-lg">
              Personaliza tu experiencia en Azure Reports
            </p>
          </div>
          <div className="hidden md:block">
            <div className="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center">
              <SettingsIcon className="w-10 h-10" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar de navegación */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-soft border border-gray-200 p-4">
            <nav className="space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary-500 text-white'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <tab.icon className="w-5 h-5" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Contenido principal */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-xl shadow-soft border border-gray-200 p-6">
            {activeTab === 'general' && (
              <motion.div
                key="general"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Configuración General</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tema de la aplicación
                    </label>
                    <select
                      value={settings.preferences.theme}
                      onChange={(e) => handleSettingChange('preferences', 'theme', e.target.value)}
                      className="input-field"
                    >
                      <option value="light">Claro</option>
                      <option value="dark">Oscuro</option>
                      <option value="auto">Automático</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Idioma
                    </label>
                    <select
                      value={settings.preferences.language}
                      onChange={(e) => handleSettingChange('preferences', 'language', e.target.value)}
                      className="input-field"
                    >
                      <option value="es">Español</option>
                      <option value="en">English</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Zona horaria
                    </label>
                    <select
                      value={settings.preferences.timezone}
                      onChange={(e) => handleSettingChange('preferences', 'timezone', e.target.value)}
                      className="input-field"
                    >
                      <option value="America/Santo_Domingo">Santo Domingo (GMT-4)</option>
                      <option value="America/New_York">New York (GMT-5)</option>
                      <option value="Europe/Madrid">Madrid (GMT+1)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tipo de reporte por defecto
                    </label>
                    <select
                      value={settings.preferences.defaultReportType}
                      onChange={(e) => handleSettingChange('preferences', 'defaultReportType', e.target.value)}
                      className="input-field"
                    >
                      <option value="executive">Ejecutivo</option>
                      <option value="detailed">Detallado</option>
                      <option value="summary">Resumen</option>
                    </select>
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'notifications' && (
              <motion.div
                key="notifications"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Notificaciones</h3>
                
                <div className="space-y-4">
                  {[
                    { key: 'email', label: 'Notificaciones por email', description: 'Recibe actualizaciones importantes por correo' },
                    { key: 'push', label: 'Notificaciones push', description: 'Notificaciones en tiempo real en el navegador' },
                    { key: 'reports', label: 'Reportes completados', description: 'Te avisamos cuando tus reportes estén listos' },
                    { key: 'security', label: 'Alertas de seguridad', description: 'Notificaciones sobre la seguridad de tu cuenta' },
                  ].map((notification) => (
                    <div key={notification.key} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div>
                        <h4 className="font-medium text-gray-900">{notification.label}</h4>
                        <p className="text-sm text-gray-600">{notification.description}</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.notifications[notification.key]}
                          onChange={(e) => handleSettingChange('notifications', notification.key, e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'security' && (
              <motion.div
                key="security"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Seguridad</h3>
                
                <div className="space-y-6">
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Shield className="w-5 h-5 text-blue-600" />
                      <div>
                        <h4 className="font-medium text-blue-900">Autenticación de dos factores</h4>
                        <p className="text-sm text-blue-700">Agrega una capa extra de seguridad a tu cuenta</p>
                      </div>
                    </div>
                    <button className="mt-3 btn-primary">Configurar 2FA</button>
                  </div>

                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">Cambiar contraseña</h4>
                    <p className="text-sm text-gray-600 mb-4">Actualiza tu contraseña regularmente para mantener tu cuenta segura</p>
                    <button className="btn-secondary">Cambiar Contraseña</button>
                  </div>

                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">Sesiones activas</h4>
                    <p className="text-sm text-gray-600 mb-4">Revisa y cierra sesiones activas en otros dispositivos</p>
                    <button className="btn-secondary">Ver Sesiones</button>
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'privacy' && (
              <motion.div
                key="privacy"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Privacidad</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div>
                      <h4 className="font-medium text-gray-900">Compartir datos de análisis</h4>
                      <p className="text-sm text-gray-600">Ayúdanos a mejorar compartiendo datos anónimos de uso</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.privacy.shareAnalytics}
                        onChange={(e) => handleSettingChange('privacy', 'shareAnalytics', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Retención de datos (días)
                    </label>
                    <select
                      value={settings.privacy.dataRetention}
                      onChange={(e) => handleSettingChange('privacy', 'dataRetention', e.target.value)}
                      className="input-field"
                    >
                      <option value="30">30 días</option>
                      <option value="90">90 días</option>
                      <option value="180">180 días</option>
                      <option value="365">1 año</option>
                    </select>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Botón de guardar */}
            <div className="flex justify-end pt-6 border-t border-gray-200 mt-8">
              <button
                onClick={handleSave}
                className="btn-primary flex items-center space-x-2"
              >
                <Save className="w-4 h-4" />
                <span>Guardar Cambios</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;