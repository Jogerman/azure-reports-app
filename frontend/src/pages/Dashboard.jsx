// frontend/src/pages/Dashboard.jsx - DISEÑO MODERNO RENOVADO
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  FileText, 
  Upload,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Info,
  Activity,
  DollarSign,
  Clock,
  Target,
  Zap,
  Download,
  Eye,
  Plus,
  ArrowRight,
  Shield,
  Server,
  Settings,
  TrendingDown
} from 'lucide-react';
import { 
  useRealDashboardStats, 
  useRealActivity, 
  useHasRealData
} from '../hooks/useRealData';
import Loading from '../components/common/Loading';
import FileUpload from '../components/reports/FileUpload';
import { formatCurrency, formatNumber } from '../utils/helpers';
import toast from 'react-hot-toast';

const ModernDashboard = () => {
  const [showUpload, setShowUpload] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  const { data: stats, isLoading: statsLoading, error: statsError, refetch: refetchStats } = useRealDashboardStats();
  const { data: recentActivity, refetch: refetchActivity } = useRealActivity(8);
  const { hasRealData, dataSource, lastAnalysisDate, csvFilename, qualityScore } = useHasRealData();

  const handleRefreshDashboard = async () => {
    setRefreshing(true);
    try {
      await Promise.all([refetchStats(), refetchActivity()]);
      toast.success('🔄 Dashboard actualizado con datos reales');
    } catch (error) {
      toast.error('❌ Error al actualizar dashboard');
    } finally {
      setRefreshing(false);
    }
  };

  const handleActionClick = (action) => {
    switch (action) {
      case 'upload':
        setShowUpload(true);
        break;
      case 'generate-report':
        window.location.href = '/app/reports';
        break;
      case 'view-history':
        window.location.href = '/app/history';
        break;
      case 'manage-storage':
        window.location.href = '/app/storage';
        break;
      case 'settings':
        window.location.href = '/app/settings';
        break;
      default:
        console.log('Action:', action);
    }
  };

  const handleFileUploaded = () => {
    setShowUpload(false);
    setTimeout(() => {
      handleRefreshDashboard();
      toast.success('🎉 ¡Análisis actualizado con tu nuevo archivo CSV!');
    }, 2000);
  };

  if (statsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <Loading message="Cargando análisis real de datos..." />
      </div>
    );
  }

  if (statsError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-2xl mx-auto"
        >
          <div className="bg-white rounded-2xl shadow-xl border border-red-100 p-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                <AlertCircle className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-red-800">Error Cargando Datos</h3>
                <p className="text-red-600 mt-1">{statsError.message}</p>
              </div>
            </div>
            <button
              onClick={handleRefreshDashboard}
              disabled={refreshing}
              className="w-full px-6 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700 disabled:opacity-50 transition-all duration-200 font-medium"
            >
              {refreshing ? 'Reintentando...' : 'Reintentar Conexión'}
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  const categories = [
    { key: 'all', name: 'Todas', icon: BarChart3, color: 'blue' },
    { key: 'cost', name: 'Costo', icon: DollarSign, color: 'green' },
    { key: 'reliability', name: 'Confiabilidad', icon: Server, color: 'blue' },
    { key: 'security', name: 'Seguridad', icon: Shield, color: 'orange' },
    { key: 'operational', name: 'Operacional', icon: Settings, color: 'purple' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="p-6 max-w-7xl mx-auto space-y-8">
        
        {/* Header Moderno */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative overflow-hidden bg-gradient-to-r from-blue-600 to-purple-700 rounded-3xl p-8 text-white"
        >
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative z-10 flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Dashboard de Optimización</h1>
              <div className="flex items-center gap-6">
                {hasRealData ? (
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-300" />
                    <span className="text-green-100 font-medium">
                      Análisis real de "{csvFilename}"
                    </span>
                    <span className="px-3 py-1 bg-white/20 rounded-full text-sm">
                      Calidad: {qualityScore}%
                    </span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-amber-300" />
                    <span className="text-amber-100 font-medium">
                      Esperando archivo CSV para análisis real
                    </span>
                    <button
                      onClick={() => setShowUpload(true)}
                      className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-xl text-sm font-medium transition-colors"
                    >
                      Subir Ahora →
                    </button>
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleRefreshDashboard}
                disabled={refreshing}
                className="flex items-center gap-2 px-6 py-3 bg-white/20 backdrop-blur-sm rounded-xl hover:bg-white/30 disabled:opacity-50 transition-all font-medium"
              >
                <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
                {refreshing ? 'Actualizando...' : 'Actualizar'}
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowUpload(true)}
                className="flex items-center gap-2 px-6 py-3 bg-white text-blue-600 rounded-xl hover:bg-gray-50 transition-all font-medium shadow-lg"
              >
                <Upload className="w-5 h-5" />
                Nuevo CSV
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Métricas Principales - Diseño Moderno */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {/* Total Recomendaciones */}
          <motion.div 
            whileHover={{ scale: 1.02, y: -5 }}
            className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-blue-100"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                hasRealData ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
              }`}>
                {hasRealData ? 'Real' : 'Demo'}
              </div>
            </div>
            <div>
              <h3 className="text-gray-600 text-sm font-medium mb-1">Total Recomendaciones</h3>
              <p className="text-3xl font-bold text-gray-900 mb-2">
                {formatNumber(stats?.total_recommendations || 0)}
              </p>
              <div className="flex items-center text-sm">
                {hasRealData ? (
                  <div className="flex items-center text-green-600">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    <span>Datos actuales</span>
                  </div>
                ) : (
                  <div className="flex items-center text-gray-500">
                    <TrendingDown className="w-4 h-4 mr-1" />
                    <span>Esperando CSV</span>
                  </div>
                )}
              </div>
            </div>
          </motion.div>

          {/* Optimización Mensual */}
          <motion.div 
            whileHover={{ scale: 1.02, y: -5 }}
            className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-green-100"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
              <div className="text-green-600 font-medium text-sm">
                /mes
              </div>
            </div>
            <div>
              <h3 className="text-gray-600 text-sm font-medium mb-1">Ahorro Potencial</h3>
              <p className="text-3xl font-bold text-gray-900 mb-2">
                {formatCurrency(stats?.monthly_optimization || 0)}
              </p>
              <div className="flex items-center text-sm text-green-600">
                <TrendingUp className="w-4 h-4 mr-1" />
                <span>Optimización estimada</span>
              </div>
            </div>
          </motion.div>

          {/* Horas de Trabajo */}
          <motion.div 
            whileHover={{ scale: 1.02, y: -5 }}
            className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-orange-100"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center">
                <Clock className="w-6 h-6 text-white" />
              </div>
              <div className="text-orange-600 font-medium text-sm">
                horas
              </div>
            </div>
            <div>
              <h3 className="text-gray-600 text-sm font-medium mb-1">Tiempo Estimado</h3>
              <p className="text-3xl font-bold text-gray-900 mb-2">
                {formatNumber(stats?.working_hours || 0)}
              </p>
              <div className="flex items-center text-sm text-orange-600">
                <Activity className="w-4 h-4 mr-1" />
                <span>Implementación</span>
              </div>
            </div>
          </motion.div>

          {/* Alto Impacto */}
          <motion.div 
            whileHover={{ scale: 1.02, y: -5 }}
            className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-red-100"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-red-500 rounded-xl flex items-center justify-center">
                <Target className="w-6 h-6 text-white" />
              </div>
              <div className="text-red-600 font-medium text-sm">
                críticas
              </div>
            </div>
            <div>
              <h3 className="text-gray-600 text-sm font-medium mb-1">Prioridad Alta</h3>
              <p className="text-3xl font-bold text-gray-900 mb-2">
                {formatNumber(stats?.high_impact_actions || 0)}
              </p>
              <div className="flex items-center text-sm text-red-600">
                <Zap className="w-4 h-4 mr-1" />
                <span>Requieren atención</span>
              </div>
            </div>
          </motion.div>
        </motion.div>

        {/* Análisis por Categorías - Solo si hay datos reales */}
        {hasRealData && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100"
          >
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Análisis Detallado por Categoría</h2>
                <p className="text-gray-600 mt-1">Desglose completo de recomendaciones y costos</p>
              </div>
              
              {/* Filtros de Categoría */}
              <div className="flex items-center gap-2">
                {categories.map((category) => (
                  <button
                    key={category.key}
                    onClick={() => setSelectedCategory(category.key)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all ${
                      selectedCategory === category.key
                        ? 'bg-blue-100 text-blue-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <category.icon className="w-4 h-4" />
                    <span>{category.name}</span>
                  </button>
                ))}
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Cost Optimization */}
              <motion.div 
                whileHover={{ scale: 1.02 }}
                className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                    <DollarSign className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-bold text-green-900">Optimización de Costos</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-green-700">Recomendaciones:</span>
                    <span className="font-bold text-green-900 text-lg">
                      {stats.cost_optimization?.actions || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-green-700">Ahorro mensual:</span>
                    <span className="font-bold text-green-900">
                      ${formatNumber(stats.cost_optimization?.estimated_monthly_savings || 0)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-green-700">Tiempo:</span>
                    <span className="font-bold text-green-900">
                      {stats.cost_optimization?.working_hours || 0}h
                    </span>
                  </div>
                  <button className="w-full mt-4 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm font-medium">
                    Ver Detalles
                  </button>
                </div>
              </motion.div>

              {/* Reliability */}
              <motion.div 
                whileHover={{ scale: 1.02 }}
                className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                    <Server className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-bold text-blue-900">Confiabilidad</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-blue-700">Recomendaciones:</span>
                    <span className="font-bold text-blue-900 text-lg">
                      {stats.reliability_optimization?.actions || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-blue-700">Inversión/mes:</span>
                    <span className="font-bold text-blue-900">
                      ${formatNumber(stats.reliability_optimization?.monthly_investment || 0)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-blue-700">Tiempo:</span>
                    <span className="font-bold text-blue-900">
                      {stats.reliability_optimization?.working_hours || 0}h
                    </span>
                  </div>
                  <button className="w-full mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium">
                    Ver Detalles
                  </button>
                </div>
              </motion.div>

              {/* Security */}
              <motion.div 
                whileHover={{ scale: 1.02 }}
                className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 border border-orange-200"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
                    <Shield className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-bold text-orange-900">Seguridad</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-orange-700">Recomendaciones:</span>
                    <span className="font-bold text-orange-900 text-lg">
                      {stats.security_optimization?.actions || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-orange-700">Inversión/mes:</span>
                    <span className="font-bold text-orange-900">
                      ${formatNumber(stats.security_optimization?.monthly_investment || 0)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-orange-700">Tiempo:</span>
                    <span className="font-bold text-orange-900">
                      {stats.security_optimization?.working_hours || 0}h
                    </span>
                  </div>
                  <button className="w-full mt-4 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors text-sm font-medium">
                    Ver Detalles
                  </button>
                </div>
              </motion.div>

              {/* Operational Excellence */}
              <motion.div 
                whileHover={{ scale: 1.02 }}
                className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                    <Settings className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-bold text-purple-900">Excelencia Operacional</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-purple-700">Recomendaciones:</span>
                    <span className="font-bold text-purple-900 text-lg">
                      {stats.operational_optimization?.actions || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-purple-700">Inversión/mes:</span>
                    <span className="font-bold text-purple-900">
                      ${formatNumber(stats.operational_optimization?.monthly_investment || 0)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-purple-700">Tiempo:</span>
                    <span className="font-bold text-purple-900">
                      {stats.operational_optimization?.working_hours || 0}h
                    </span>
                  </div>
                  <button className="w-full mt-4 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors text-sm font-medium">
                    Ver Detalles
                  </button>
                </div>
              </motion.div>
            </div>
          </motion.div>
        )}

        {/* Acciones Rápidas Modernas */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-8"
        >
          {/* Panel de Acciones */}
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900">Acciones Rápidas</h3>
                <p className="text-gray-600 mt-1">Gestiona tu análisis de Azure</p>
              </div>
              <Plus className="h-6 w-6 text-gray-400" />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <motion.button
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleActionClick('upload')}
                className="flex flex-col items-center p-6 rounded-xl border-2 border-blue-200 hover:border-blue-300 hover:bg-blue-50 transition-all group"
              >
                <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <Upload className="w-6 h-6 text-white" />
                </div>
                <h4 className="font-semibold text-gray-900 group-hover:text-blue-700">Subir CSV</h4>
                <p className="text-sm text-gray-500 text-center mt-1">Analizar nuevos datos de Azure Advisor</p>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleActionClick('generate-report')}
                className="flex flex-col items-center p-6 rounded-xl border-2 border-green-200 hover:border-green-300 hover:bg-green-50 transition-all group"
              >
                <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <h4 className="font-semibold text-gray-900 group-hover:text-green-700">Crear Reporte</h4>
                <p className="text-sm text-gray-500 text-center mt-1">Generar análisis detallado</p>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleActionClick('view-history')}
                className="flex flex-col items-center p-6 rounded-xl border-2 border-purple-200 hover:border-purple-300 hover:bg-purple-50 transition-all group"
              >
                <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <Eye className="w-6 h-6 text-white" />
                </div>
                <h4 className="font-semibold text-gray-900 group-hover:text-purple-700">Ver Historial</h4>
                <p className="text-sm text-gray-500 text-center mt-1">Revisar análisis anteriores</p>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleActionClick('manage-storage')}
                className="flex flex-col items-center p-6 rounded-xl border-2 border-orange-200 hover:border-orange-300 hover:bg-orange-50 transition-all group"
              >
                <div className="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <Server className="w-6 h-6 text-white" />
                </div>
                <h4 className="font-semibold text-gray-900 group-hover:text-orange-700">Almacenamiento</h4>
                <p className="text-sm text-gray-500 text-center mt-1">Gestionar archivos</p>
              </motion.button>
            </div>
          </div>

          {/* Panel de Actividad Reciente */}
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900">Actividad Reciente</h3>
                <p className="text-gray-600 mt-1">Últimas acciones realizadas</p>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                onClick={() => window.location.href = '/app/history'}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1"
              >
                Ver todo <ArrowRight className="w-4 h-4" />
              </motion.button>
            </div>
            
            <div className="space-y-4">
              {recentActivity && recentActivity.length > 0 ? (
                recentActivity.slice(0, 5).map((activity, index) => (
                  <motion.div 
                    key={activity.id || index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center gap-4 p-4 rounded-xl hover:bg-gray-50 transition-colors"
                  >
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      activity.type === 'file_processed' ? 'bg-blue-100' :
                      activity.type === 'report_generated' ? 'bg-green-100' : 'bg-gray-100'
                    }`}>
                      {activity.type === 'file_processed' ? (
                        <Upload className={`w-5 h-5 ${
                          activity.type === 'file_processed' ? 'text-blue-600' : 'text-gray-600'
                        }`} />
                      ) : (
                        <FileText className={`w-5 h-5 ${
                          activity.type === 'report_generated' ? 'text-green-600' : 'text-gray-600'
                        }`} />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{activity.description}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(activity.timestamp).toLocaleString('es-ES')}
                      </p>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      activity.status === 'completed' ? 'bg-green-100 text-green-700' :
                      activity.status === 'processing' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {activity.status}
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Activity className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 font-medium">No hay actividad reciente</p>
                  <p className="text-sm text-gray-400 mt-1">Los análisis aparecerán aquí</p>
                </div>
              )}
            </div>
          </div>
        </motion.div>

        {/* Información del Análisis - Solo si hay datos reales */}
        {hasRealData && lastAnalysisDate && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-200"
          >
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <Info className="w-6 h-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-blue-900 mb-2">Información del Análisis Actual</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-blue-700 font-medium">Último análisis:</span>
                    <p className="text-blue-900">{new Date(lastAnalysisDate).toLocaleString('es-ES')}</p>
                  </div>
                  <div>
                    <span className="text-blue-700 font-medium">Archivo procesado:</span>
                    <p className="text-blue-900 font-mono text-xs">{csvFilename}</p>
                  </div>
                  <div>
                    <span className="text-blue-700 font-medium">Calidad de datos:</span>
                    <p className="text-blue-900">{qualityScore}% - Excelente</p>
                  </div>
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                onClick={() => handleActionClick('generate-report')}
                className="px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Generar Reporte
              </motion.button>
            </div>
          </motion.div>
        )}
      </div>

      {/* Modal de Upload Mejorado */}
      {showUpload && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-3xl p-8 w-full max-w-2xl shadow-2xl"
          >
            <div className="flex items-center justify-between mb-8">
              <div>
                <h3 className="text-2xl font-bold text-gray-900">
                  Subir Archivo CSV de Azure Advisor
                </h3>
                <p className="text-gray-600 mt-2">
                  Sube tu archivo CSV para obtener análisis real y detallado de tus recomendaciones
                </p>
              </div>
              <button
                onClick={() => setShowUpload(false)}
                className="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
              >
                ✕
              </button>
            </div>
            <FileUpload 
              onFileUploaded={handleFileUploaded}
              acceptedTypes=".csv"
              maxSize={50}
              instructions="Arrastra tu archivo CSV aquí o haz clic para seleccionar. Archivos CSV de Azure Advisor hasta 50MB."
            />
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default ModernDashboard;