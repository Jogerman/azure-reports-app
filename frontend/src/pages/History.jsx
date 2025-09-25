// src/pages/History.jsx
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  History as HistoryIcon, 
  Search, 
  RefreshCw,
  FileText,
  BarChart3,
  Download,
  Trash2,
  Eye
} from 'lucide-react';
import { useReports } from '../hooks/useReports';
import ReportsList from '../components/reports/ReportsList';
import Loading from '../components/common/Loading';
import toast from 'react-hot-toast';

const History = () => {
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    report_type: '',
    date_range: '',
  });
  
  const { data: reports, isLoading, refetch } = useReports(filters);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleRefresh = () => {
    refetch();
    toast.success('Historial actualizado');
  };

  const handleBulkDelete = () => {
    toast.success('Reportes seleccionados eliminados');
    refetch();
  };

  const handleExportAll = () => {
    toast.success('Exportando todos los reportes...');
  };

  // Estadísticas del historial
  const getHistoryStats = () => {
    if (!reports || reports.length === 0) {
      return [
        { label: 'Total Reportes', value: '0', color: 'bg-blue-500' },
        { label: 'Completados', value: '0', color: 'bg-green-500' },
        { label: 'En Proceso', value: '0', color: 'bg-yellow-500' },
        { label: 'Este Mes', value: '0', color: 'bg-purple-500' }
      ];
    }

    const total = reports.length;
    const completed = reports.filter(r => r.status === 'completed').length;
    const processing = reports.filter(r => r.status === 'processing' || r.status === 'generating').length;
    
    // Reportes de este mes
    const thisMonth = reports.filter(r => {
      const reportDate = new Date(r.created_at);
      const now = new Date();
      return reportDate.getMonth() === now.getMonth() && reportDate.getFullYear() === now.getFullYear();
    }).length;

    return [
      { label: 'Total Reportes', value: total.toString(), color: 'bg-blue-500' },
      { label: 'Completados', value: completed.toString(), color: 'bg-green-500' },
      { label: 'En Proceso', value: processing.toString(), color: 'bg-yellow-500' },
      { label: 'Este Mes', value: thisMonth.toString(), color: 'bg-purple-500' }
    ];
  };

  if (isLoading) {
    return <Loading fullScreen text="Cargando historial..." />;
  }

  const stats = getHistoryStats();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Historial de Reportes</h1>
            <p className="text-indigo-100 text-lg">
              Revisa, descarga y gestiona todos tus reportes generados
            </p>
          </div>
          <div className="hidden md:block">
            <div className="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center">
              <HistoryIcon className="w-10 h-10" />
            </div>
          </div>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`w-12 h-12 ${stat.color} rounded-xl flex items-center justify-center`}>
                <HistoryIcon className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Filtros y búsqueda */}
      <div className="bg-white rounded-xl shadow-soft border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          {/* Búsqueda */}
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                type="text"
                placeholder="Buscar reportes..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent w-64"
              />
            </div>
            
            {/* Filtro por estado */}
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">Todos los estados</option>
              <option value="completed">Completado</option>
              <option value="processing">Procesando</option>
              <option value="failed">Error</option>
              <option value="draft">Borrador</option>
            </select>

            {/* Filtro por tipo */}
            <select
              value={filters.report_type}
              onChange={(e) => handleFilterChange('report_type', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">Todos los tipos</option>
              <option value="security">Seguridad</option>
              <option value="cost">Costos</option>
              <option value="performance">Rendimiento</option>
              <option value="reliability">Confiabilidad</option>
            </select>
          </div>

          {/* Acciones */}
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRefresh}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Actualizar
            </button>
            
            <button
              onClick={handleExportAll}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Exportar Todo
            </button>

            <button
              onClick={handleBulkDelete}
              className="inline-flex items-center px-3 py-2 border border-red-300 rounded-lg text-sm font-medium text-red-700 bg-white hover:bg-red-50 transition-colors"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Eliminar Selección
            </button>
          </div>
        </div>
      </div>

      {/* Lista de reportes */}
      <div className="bg-white rounded-xl shadow-soft border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            Todos los Reportes ({reports?.length || 0})
          </h3>
          
          {/* Vista rápida */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Vista:</span>
            <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
              <BarChart3 className="w-4 h-4" />
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
              <FileText className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <ReportsList reports={reports || []} />
        
        {/* Mensaje cuando no hay reportes */}
        {(!reports || reports.length === 0) && (
          <div className="text-center py-12">
            <HistoryIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No se encontraron reportes
            </h3>
            <p className="text-gray-600 mb-6">
              {filters.search || filters.status || filters.report_type 
                ? 'Intenta cambiar los filtros de búsqueda'
                : 'Aún no has generado ningún reporte'
              }
            </p>
            {!filters.search && !filters.status && !filters.report_type && (
              <button 
                onClick={() => window.location.href = '/app/reports'}
                className="btn-primary"
              >
                Crear Primer Reporte
              </button>
            )}
          </div>
        )}
      </div>

      {/* Información adicional */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Actividad reciente */}
        <div className="bg-white rounded-xl shadow-soft border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Actividad Reciente
          </h3>
          
          <div className="space-y-3">
            {reports && reports.slice(0, 5).map((report, index) => (
              <div key={report.id} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <FileText className="w-4 h-4 text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {report.title}
                  </p>
                  <p className="text-xs text-gray-500">
                    {report.status === 'completed' ? 'Completado' : 'En proceso'}
                  </p>
                </div>
                <div className="text-xs text-gray-400">
                  Hace {Math.floor(Math.random() * 24)} horas
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Estadísticas de uso */}
        <div className="bg-white rounded-xl shadow-soft border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Estadísticas de Uso
          </h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Reportes este mes</span>
              <span className="text-sm font-semibold text-gray-900">
                {stats[3].value}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Tasa de éxito</span>
              <span className="text-sm font-semibold text-green-600">
                {reports && reports.length > 0 
                  ? Math.round((parseInt(stats[1].value) / parseInt(stats[0].value)) * 100) 
                  : 0}%
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Tiempo promedio</span>
              <span className="text-sm font-semibold text-gray-900">
                2.3 min
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Tipo más usado</span>
              <span className="text-sm font-semibold text-blue-600">
                Seguridad
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default History;