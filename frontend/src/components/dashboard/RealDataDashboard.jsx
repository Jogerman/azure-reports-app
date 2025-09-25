// frontend/src/components/dashboard/RealDataDashboard.jsx - DASHBOARD CON DATOS REALES
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
  Database,
  Activity,
  Eye,
  Download,
  Info
} from 'lucide-react';
import { useRealDashboardStats, useRealActivity, useHasRealData } from '../hooks/useRealData';
import DashboardCard from './DashboardCard';
import QuickActions from './QuickActions';
import RecentReports from './RecentReports';
import Loading from '../common/Loading';
import FileUpload from '../reports/FileUpload';
import RealDataAnalyticsChart from './RealDataAnalyticsChart';
import { formatCurrency, formatNumber } from '../utils/helpers';
import toast from 'react-hot-toast';

const RealDataDashboard = () => {
  const [showUpload, setShowUpload] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  const { data: stats, isLoading: statsLoading, error: statsError, refetch: refetchStats } = useRealDashboardStats();
  const { data: recentActivity, isLoading: activityLoading, refetch: refetchActivity } = useRealActivity(8);
  const { hasRealData, dataSource, lastAnalysisDate, csvFilename, qualityScore } = useHasRealData();

  const handleRefreshDashboard = async () => {
    setRefreshing(true);
    try {
      await Promise.all([refetchStats(), refetchActivity()]);
      toast.success('🔄 Dashboard actualizado con datos reales');
    } catch (error) {
      toast.error('❌ Error al actualizar dashboard');
      console.error('Error refreshing dashboard:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleQuickAction = (action) => {
    switch (action) {
      case 'upload':
        setShowUpload(true);
        break;
      case 'create-report':
        window.location.href = '/app/reports';
        break;
      case 'view-analytics':
        window.location.href = '/app/analytics';
        break;
      default:
        console.log('Action:', action);
    }
  };

  const handleFileUploaded = () => {
    setShowUpload(false);
    // Refresh dashboard después de subir archivo para mostrar nuevos datos
    setTimeout(() => {
      handleRefreshDashboard();
      toast.success('🎉 ¡Datos reales actualizados! El dashboard ahora muestra análisis de tu archivo CSV.');
    }, 2000);
  };

  // Mostrar loading mientras carga
  if (statsLoading) {
    return <Loading message="Cargando análisis real de datos..." />;
  }

  // Mostrar error si hay problemas
  if (statsError) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-6 w-6 text-red-600" />
            <div>
              <h3 className="text-lg font-semibold text-red-800">Error Cargando Datos</h3>
              <p className="text-red-600 mt-1">
                No se pudieron cargar las estadísticas reales: {statsError.message}
              </p>
              <button
                onClick={handleRefreshDashboard}
                className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                disabled={refreshing}
              >
                {refreshing ? 'Reintentando...' : 'Reintentar'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      {/* Header con información del estado de los datos */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard - Análisis Real</h1>
          <div className="flex items-center gap-4 mt-2">
            {hasRealData ? (
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="text-green-700 font-medium">
                  Datos reales de "{csvFilename}"
                </span>
                <span className="text-sm text-gray-500">
                  (Calidad: {qualityScore}%)
                </span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-amber-600" />
                <span className="text-amber-700 font-medium">
                  Sin archivos CSV - Mostrando datos de ejemplo
                </span>
                <button
                  onClick={() => setShowUpload(true)}
                  className="ml-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  Subir CSV →
                </button>
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={handleRefreshDashboard}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? 'Actualizando...' : 'Actualizar'}
          </button>
          
          <button
            onClick={() => setShowUpload(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Upload className="w-4 h-4" />
            Subir CSV
          </button>
        </div>
      </div>

      {/* Métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <DashboardCard
          title="Total Recomendaciones"
          value={formatNumber(stats?.total_recommendations || 0)}
          icon={FileText}
          color="blue"
          change={hasRealData ? "Datos reales" : "Esperando CSV"}
          changeType={hasRealData ? "increase" : "decrease"}
        />
        
        <DashboardCard
          title="Optimización Mensual"
          value={formatCurrency(stats?.monthly_optimization || 0)}
          icon={TrendingUp}
          color="green"
          change={hasRealData ? "Análisis real" : "Estimación"}
          changeType={hasRealData ? "increase" : "decrease"}
        />
        
        <DashboardCard
          title="Horas de Trabajo"
          value={formatNumber(stats?.working_hours || 0)}
          icon={Activity}
          color="orange"
          change={hasRealData ? "Calculado" : "Pendiente"}
          changeType={hasRealData ? "increase" : "decrease"}
        />
        
        <DashboardCard
          title="Alto Impacto"
          value={formatNumber(stats?.high_impact_actions || 0)}
          icon={AlertCircle}
          color="red"
          change={hasRealData ? "Identificados" : "N/A"}
          changeType={hasRealData ? "increase" : "decrease"}
        />
      </div>

      {/* Métricas detalladas por categoría - Solo si hay datos reales */}
      {hasRealData && (
        <div className="bg-white rounded-xl shadow-soft border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Análisis por Categoría</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Cost Optimization */}
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-semibold text-green-900">Cost Optimization</h3>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-green-700">Acciones:</span>
                  <span className="font-medium text-green-900">
                    {stats.cost_optimization?.actions || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-green-700">Ahorro/mes:</span>
                  <span className="font-medium text-green-900">
                    ${formatNumber(stats.cost_optimization?.estimated_monthly_savings || 0)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-green-700">Horas:</span>
                  <span className="font-medium text-green-900">
                    {stats.cost_optimization?.working_hours || 0}h
                  </span>
                </div>
              </div>
            </div>

            {/* Reliability Optimization */}
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                  <Database className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-semibold text-blue-900">Reliability</h3>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-blue-700">Acciones:</span>
                  <span className="font-medium text-blue-900">
                    {stats.reliability_optimization?.actions || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-blue-700">Inversión/mes:</span>
                  <span className="font-medium text-blue-900">
                    ${formatNumber(stats.reliability_optimization?.monthly_investment || 0)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-blue-700">Horas:</span>
                  <span className="font-medium text-blue-900">
                    {stats.reliability_optimization?.working_hours || 0}h
                  </span>
                </div>
              </div>
            </div>

            {/* Security Optimization */}
            <div className="bg-orange-50 rounded-lg p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
                  <AlertCircle className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-semibold text-orange-900">Security</h3>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-orange-700">Acciones:</span>
                  <span className="font-medium text-orange-900">
                    {stats.security_optimization?.actions || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-orange-700">Inversión/mes:</span>
                  <span className="font-medium text-orange-900">
                    ${formatNumber(stats.security_optimization?.monthly_investment || 0)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-orange-700">Horas:</span>
                  <span className="font-medium text-orange-900">
                    {stats.security_optimization?.working_hours || 0}h
                  </span>
                </div>
              </div>
            </div>

            {/* Operational Excellence */}
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-semibold text-purple-900">Operational</h3>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-purple-700">Acciones:</span>
                  <span className="font-medium text-purple-900">
                    {stats.operational_optimization?.actions || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-purple-700">Inversión/mes:</span>
                  <span className="font-medium text-purple-900">
                    ${formatNumber(stats.operational_optimization?.monthly_investment || 0)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-purple-700">Horas:</span>
                  <span className="font-medium text-purple-900">
                    {stats.operational_optimization?.working_hours || 0}h
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Gráfico de análisis - usando datos reales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-soft border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {hasRealData ? 'Análisis Real de Datos' : 'Esperando Datos CSV'}
          </h2>
          <RealDataAnalyticsChart hasRealData={hasRealData} />
        </div>
        
        <div className="space-y-6">
          <QuickActions onAction={handleQuickAction} />
          <RecentReports />
        </div>
      </div>

      {/* Información del estado de datos */}
      {lastAnalysisDate && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-900">Información del Análisis</h4>
              <p className="text-sm text-blue-700 mt-1">
                Último análisis: {new Date(lastAnalysisDate).toLocaleString('es-ES')}
              </p>
              <p className="text-sm text-blue-700">
                Archivo: {csvFilename} | Calidad de datos: {qualityScore}%
              </p>
              <p className="text-sm text-blue-700">
                Fuente de datos: {dataSource === 'real_csv_analysis' ? 'Análisis real de CSV' : 'Datos de ejemplo'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Modal de upload */}
      {showUpload && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl mx-4">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">
                Subir Archivo CSV para Análisis Real
              </h3>
              <button
                onClick={() => setShowUpload(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <FileUpload 
              onFileUploaded={handleFileUploaded}
              acceptedTypes=".csv"
              maxSize={50}
              instructions="Sube tu archivo CSV de Azure Advisor para ver análisis real de tus recomendaciones."
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default RealDataDashboard;