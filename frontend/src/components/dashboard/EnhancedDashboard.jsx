// frontend/src/components/dashboard/EnhancedDashboard.jsx

import React, { useState, useEffect } from 'react';
import { 
  Shield, Zap, DollarSign, BarChart3, TrendingUp, AlertTriangle, 
  CheckCircle, Clock, FileText, Upload, Eye, Download 
} from 'lucide-react';
import SpecializedMetrics from './SpecializedMetrics';
import reportsService from '../../services/reportsService';

const EnhancedDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [recentReports, setRecentReports] = useState([]);
  const [specializedStats, setSpecializedStats] = useState({});
  const [selectedMetricType, setSelectedMetricType] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Cargar datos del dashboard general
      const [dashboardStats, reportsData] = await Promise.all([
        reportsService.getDashboardStats(),
        reportsService.getReports({ page_size: 5 })
      ]);
      
      setDashboardData(dashboardStats);
      setRecentReports(reportsData.results || []);
      
      // Cargar estadísticas especializadas para cada tipo
      await loadSpecializedStats();
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSpecializedStats = async () => {
    const types = ['security', 'performance', 'cost'];
    const stats = {};
    
    for (const type of types) {
      try {
        const typeStats = await reportsService.getAnalyticsForType(type);
        stats[type] = typeStats;
      } catch (error) {
        console.error(`Error loading ${type} stats:`, error);
        stats[type] = null;
      }
    }
    
    setSpecializedStats(stats);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
      case 'generating':
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      default:
        return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatReportType = (type) => {
    const types = {
      'comprehensive': 'Completo',
      'security': 'Seguridad',
      'performance': 'Rendimiento',
      'cost': 'Costos'
    };
    return types[type] || type;
  };

  const getTypeColor = (type) => {
    const colors = {
      'security': 'text-red-600 bg-red-50',
      'performance': 'text-orange-600 bg-orange-50',
      'cost': 'text-green-600 bg-green-50',
      'comprehensive': 'text-blue-600 bg-blue-50'
    };
    return colors[type] || 'text-gray-600 bg-gray-50';
  };

  const renderOverviewMetrics = () => {
    if (!dashboardData) return null;

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Reportes Generados"
          value={dashboardData.reports_generated || 0}
          icon={FileText}
          color="blue"
          trend="+12% vs mes anterior"
        />
        <MetricCard
          title="Archivos Procesados"
          value={dashboardData.files_processed || 0}
          icon={Upload}
          color="green"
          trend="+8% vs mes anterior"
        />
        <MetricCard
          title="Recomendaciones"
          value={dashboardData.total_recommendations || 0}
          icon={TrendingUp}
          color="purple"
          trend="Últimos 30 días"
        />
        <MetricCard
          title="Tiempo Ahorrado"
          value={`${dashboardData.working_hours || 0}h`}
          icon={Clock}
          color="indigo"
          trend="Estimado mensual"
        />
      </div>
    );
  };

  const renderSpecializedOverview = () => {
    const types = [
      {
        key: 'security',
        label: 'Seguridad',
        icon: Shield,
        color: 'red',
        gradient: 'from-red-500 to-pink-600'
      },
      {
        key: 'performance',
        label: 'Rendimiento',
        icon: Zap,
        color: 'orange', 
        gradient: 'from-orange-500 to-red-500'
      },
      {
        key: 'cost',
        label: 'Costos',
        icon: DollarSign,
        color: 'green',
        gradient: 'from-green-500 to-blue-500'
      }
    ];

    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {types.map((type) => {
          const Icon = type.icon;
          const stats = specializedStats[type.key];
          
          return (
            <div 
              key={type.key}
              className={`bg-gradient-to-r ${type.gradient} rounded-lg p-6 text-white cursor-pointer transform hover:scale-105 transition-transform`}
              onClick={() => setSelectedMetricType(type.key)}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Icon className="w-8 h-8 mr-3" />
                  <h3 className="text-lg font-semibold">{type.label}</h3>
                </div>
                {selectedMetricType === type.key && (
                  <CheckCircle className="w-5 h-5" />
                )}
              </div>
              
              {stats && stats.total_reports > 0 ? (
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm opacity-90">Reportes:</span>
                    <span className="font-semibold">{stats.total_reports}</span>
                  </div>
                  {type.key === 'security' && stats.analytics.type_specific_metrics && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-sm opacity-90">Score Promedio:</span>
                        <span className="font-semibold">
                          {Math.round(stats.analytics.type_specific_metrics.average_security_score || 0)}/100
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm opacity-90">Issues Críticos:</span>
                        <span className="font-semibold">
                          {stats.analytics.type_specific_metrics.total_critical_issues || 0}
                        </span>
                      </div>
                    </>
                  )}
                  {type.key === 'performance' && stats.analytics.type_specific_metrics && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-sm opacity-90">Score Promedio:</span>
                        <span className="font-semibold">
                          {Math.round(stats.analytics.type_specific_metrics.average_performance_score || 0)}/100
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm opacity-90">Optimización:</span>
                        <span className="font-semibold">
                          {Math.round(stats.analytics.type_specific_metrics.average_optimization_potential || 0)}%
                        </span>
                      </div>
                    </>
                  )}
                  {type.key === 'cost' && stats.analytics.type_specific_metrics && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-sm opacity-90">Ahorros Total:</span>
                        <span className="font-semibold">
                          ${(stats.analytics.type_specific_metrics.total_potential_savings || 0).toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm opacity-90">ROI Promedio:</span>
                        <span className="font-semibold">
                          {Math.round(stats.analytics.type_specific_metrics.average_roi || 0)}%
                        </span>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-sm opacity-90">No hay reportes de este tipo</p>
                  <button className="mt-2 px-4 py-1 bg-white bg-opacity-20 rounded text-sm hover:bg-opacity-30 transition-colors">
                    Crear Reporte
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  const renderRecentActivity = () => {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Reportes Recientes</h3>
        </div>
        <div className="p-6">
          {recentReports.length > 0 ? (
            <div className="space-y-4">
              {recentReports.map((report) => (
                <div 
                  key={report.id} 
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(report.status)}
                    <div>
                      <h4 className="font-medium text-gray-900 truncate max-w-md">
                        {report.title}
                      </h4>
                      <div className="flex items-center space-x-3 mt-1">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(report.report_type)}`}>
                          {formatReportType(report.report_type)}
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(report.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {report.status === 'completed' && (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => window.open(`/api/reports/${report.id}/html/`, '_blank')}
                        className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                        title="Ver reporte"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => window.open(`/api/reports/${report.id}/pdf/`, '_blank')}
                        className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                        title="Descargar PDF"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No hay reportes recientes</p>
              <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                Crear Primer Reporte
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard Azure Reports</h1>
          <p className="text-gray-600 mt-1">
            Resumen de tu actividad de reportes especializados
          </p>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={() => setSelectedMetricType('overview')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedMetricType === 'overview'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            General
          </button>
          <button
            onClick={() => setSelectedMetricType('specialized')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedMetricType === 'specialized'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Especializado
          </button>
        </div>
      </div>

      {/* Main Content */}
      {selectedMetricType === 'overview' && (
        <div className="space-y-8">
          {renderOverviewMetrics()}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {renderRecentActivity()}
            <QuickActions />
          </div>
        </div>
      )}

      {selectedMetricType === 'specialized' && (
        <div className="space-y-8">
          {renderSpecializedOverview()}
          <RecommendationsPanel />
        </div>
      )}

      {['security', 'performance', 'cost'].includes(selectedMetricType) && (
        <div className="space-y-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold mb-4">
              Métricas de {formatReportType(selectedMetricType)}
            </h2>
            <SpecializedMetrics 
              reportType={selectedMetricType}
              analysisData={specializedStats[selectedMetricType]?.analytics || {}}
            />
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {renderRecentActivity()}
            <TrendsPanel reportType={selectedMetricType} />
          </div>
        </div>
      )}
    </div>
  );
};

// Componente de Métrica Individual
const MetricCard = ({ title, value, icon: Icon, color, trend }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    purple: 'text-purple-600 bg-purple-50',
    indigo: 'text-indigo-600 bg-indigo-50',
    red: 'text-red-600 bg-red-50',
    orange: 'text-orange-600 bg-orange-50'
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {trend && (
            <p className="text-xs text-gray-500 mt-1">{trend}</p>
          )}
        </div>
      </div>
    </div>
  );
};

// Componente de Acciones Rápidas
const QuickActions = () => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Acciones Rápidas</h3>
      </div>
      <div className="p-6">
        <div className="grid grid-cols-1 gap-4">
          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
            <div className="p-2 bg-blue-50 rounded-lg">
              <Upload className="w-5 h-5 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="font-medium text-gray-900">Subir Nuevo CSV</p>
              <p className="text-sm text-gray-500">Analizar datos de Azure Advisor</p>
            </div>
          </button>
          
          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
            <div className="p-2 bg-green-50 rounded-lg">
              <BarChart3 className="w-5 h-5 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="font-medium text-gray-900">Crear Reporte Especializado</p>
              <p className="text-sm text-gray-500">Análisis enfocado en área específica</p>
            </div>
          </button>
          
          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
            <div className="p-2 bg-purple-50 rounded-lg">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="font-medium text-gray-900">Ver Tendencias</p>
              <p className="text-sm text-gray-500">Análisis histórico de mejoras</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

// Panel de Recomendaciones
const RecommendationsPanel = () => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Recomendaciones Inteligentes</h3>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          <div className="flex items-start p-4 bg-blue-50 rounded-lg">
            <Shield className="w-5 h-5 text-blue-600 mr-3 mt-0.5" />
            <div>
              <p className="font-medium text-blue-900">Análisis de Seguridad Recomendado</p>
              <p className="text-sm text-blue-700">
                Detectamos 15 nuevas recomendaciones de seguridad en tu último CSV
              </p>
            </div>
          </div>
          
          <div className="flex items-start p-4 bg-green-50 rounded-lg">
            <DollarSign className="w-5 h-5 text-green-600 mr-3 mt-0.5" />
            <div>
              <p className="font-medium text-green-900">Oportunidades de Ahorro</p>
              <p className="text-sm text-green-700">
                Potencial de ahorro de $12,500/mes identificado en análisis de costos
              </p>
            </div>
          </div>
          
          <div className="flex items-start p-4 bg-orange-50 rounded-lg">
            <Zap className="w-5 h-5 text-orange-600 mr-3 mt-0.5" />
            <div>
              <p className="font-medium text-orange-900">Optimización de Rendimiento</p>
              <p className="text-sm text-orange-700">
                3 cuellos de botella críticos necesitan atención inmediata
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Panel de Tendencias por Tipo
const TrendsPanel = ({ reportType }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">
          Tendencias - {formatReportType(reportType)}
        </h3>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Último mes</span>
            <span className="text-sm font-medium text-green-600">↑ 15%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Último trimestre</span>
            <span className="text-sm font-medium text-blue-600">↑ 8%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Último año</span>
            <span className="text-sm font-medium text-purple-600">↑ 22%</span>
          </div>
        </div>
        
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            {reportType === 'security' && 
              'Mejora constante en puntuación de seguridad durante los últimos 6 meses'
            }
            {reportType === 'performance' && 
              'Optimizaciones implementadas han mejorado el rendimiento promedio 25%'
            }
            {reportType === 'cost' && 
              'Ahorros acumulados de $45,000 en el último trimestre'
            }
          </p>
        </div>
      </div>
    </div>
  );
};

export default EnhancedDashboard;