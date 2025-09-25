// frontend/src/pages/Reports.jsx - VERSIÓN HÍBRIDA CON GENERACIÓN DE REPORTES
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  Upload, 
  BarChart3,
  RefreshCw,
  Zap,
  TrendingUp,
  Shield,
  DollarSign,
  Database,
  AlertCircle,
  Clock,
  CheckCircle,
  FileX,
  X,
  Eye,
  Download,
  Plus,
  Settings
} from 'lucide-react';

import { 
  useFiles,
  useRecentReports,
  useReportGeneration
} from '../hooks/useReports';

import FileUpload from '../components/reports/FileUpload';
import Loading from '../components/common/Loading';
import { formatFileSize, formatRelativeTime } from '../utils/helpers';
import toast from 'react-hot-toast';

const Reports = () => {
  const [showUpload, setShowUpload] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [reportConfig, setReportConfig] = useState({
    title: '',
    description: '',
    type: 'comprehensive',
    includeCharts: true,
    includeTables: true,
    includeRecommendations: true
  });

  // Hooks para datos
  const { data: files, isLoading: filesLoading, refetch: refetchFiles, error: filesError } = useFiles();
  const { data: recentReports, isLoading: reportsLoading, refetch: refetchReports } = useRecentReports(5);
  const { generateReport, isGenerating } = useReportGeneration();

  // Debug en consola
  useEffect(() => {
    console.log('🔍 Debug Reports:', {
      files: files,
      filesCount: files?.length || 0,
      filesLoading,
      filesError: filesError?.message,
      selectedFile,
      recentReports,
      reportsLoading
    });
  }, [files, filesLoading, filesError, selectedFile, recentReports, reportsLoading]);

  // Tipos de reportes disponibles
  const reportTypes = [
    { 
      value: 'comprehensive', 
      label: 'Análisis Completo', 
      icon: BarChart3, 
      description: 'Análisis detallado con todas las métricas' 
    },
    { 
      value: 'security', 
      label: 'Análisis de Seguridad', 
      icon: Shield, 
      description: 'Enfoque en vulnerabilidades y seguridad' 
    },
    { 
      value: 'performance', 
      label: 'Análisis de Rendimiento', 
      icon: Zap, 
      description: 'Optimización y eficiencia del sistema' 
    },
    { 
      value: 'cost', 
      label: 'Análisis de Costos', 
      icon: DollarSign, 
      description: 'Optimización financiera y ahorros' 
    }
  ];

  const handleUploadComplete = (uploadedFiles) => {
    console.log('📤 Upload completado, archivos recibidos:', uploadedFiles);
    
    setShowUpload(false);
    
    // Refrescar lista de archivos
    console.log('🔄 Refrescando lista de archivos...');
    refetchFiles();
    
    toast.success(`${uploadedFiles.length} archivo(s) subido(s) exitosamente`);
    
    // Auto-seleccionar primer archivo
    if (uploadedFiles.length > 0) {
      const firstFile = uploadedFiles[0];
      console.log('🎯 Auto-seleccionando archivo:', firstFile);
      
      setSelectedFile(firstFile);
      setReportConfig(prev => ({ 
        ...prev, 
        title: `Análisis ${firstFile.original_filename?.replace('.csv', '') || 'Archivo'} - ${new Date().toLocaleDateString()}`
      }));
    }
  };

  const handleGenerateReport = async () => {
    if (!selectedFile) {
      toast.error('Selecciona un archivo primero');
      return;
    }

    if (!reportConfig.title.trim()) {
      toast.error('Ingresa un título para el reporte');
      return;
    }

    try {
      console.log('🚀 Generando reporte con:', {
        file: selectedFile,
        config: reportConfig
      });

      const result = await generateReport(selectedFile.id, reportConfig);
      console.log('✅ Reporte generado, resultado:', result);
      
      refetchReports();
      
      // Limpiar formulario
      setReportConfig(prev => ({ 
        ...prev, 
        title: '',
        description: '' 
      }));
      
      toast.success('¡Reporte generado exitosamente!');
      
      // Redirigir a la página del reporte HTML
      if (result && result.id) {
        console.log('🔗 Redirigiendo a reporte:', result.id);
        // Esperar un momento para que se vea el toast
        setTimeout(() => {
          window.location.href = `/app/reports/${result.id}`;
        }, 1500);
      } else if (result && result.report_id) {
        console.log('🔗 Redirigiendo a reporte (report_id):', result.report_id);
        setTimeout(() => {
          window.location.href = `/app/reports/${result.report_id}`;
        }, 1500);
      } else {
        console.warn('⚠️ No se recibió ID del reporte, abriendo en nueva pestaña...');
        // Fallback: Abrir lista de reportes
        setTimeout(() => {
          window.location.href = '/app/history';
        }, 1500);
      }
      
    } catch (error) {
      console.error('❌ Error generando reporte:', error);
      toast.error('Error generando reporte: ' + error.message);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Generador de Reportes</h1>
            <p className="text-blue-100 text-lg">
              Sube archivos CSV y genera reportes inteligentes con IA
            </p>
          </div>
          <div className="hidden md:block">
            <div className="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center">
              <BarChart3 className="w-10 h-10" />
            </div>
          </div>
        </div>
      </div>

      {/* Debug info (solo en desarrollo) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-yellow-800 mb-2">🔍 Debug Info</h3>
          <div className="text-xs text-yellow-700 space-y-1">
            <div>📂 Archivos cargados: {files?.length || 0}</div>
            <div>📊 Cargando archivos: {filesLoading ? 'Sí' : 'No'}</div>
            <div>❌ Error archivos: {filesError ? 'Sí' : 'No'}</div>
            <div>📎 Archivo seleccionado: {selectedFile ? selectedFile.original_filename : 'Ninguno'}</div>
            <div>📈 Reportes recientes: {recentReports?.length || 0}</div>
          </div>
        </div>
      )}

      {/* Contenido Principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Panel Izquierdo - Archivos Disponibles */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <Database className="w-6 h-6 text-blue-600" />
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    Archivos Disponibles ({files?.length || 0})
                  </h2>
                  <p className="text-sm text-gray-500">
                    Selecciona un archivo CSV para generar reportes
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => refetchFiles()}
                  disabled={filesLoading}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${filesLoading ? 'animate-spin' : ''}`} />
                  Actualizar
                </button>
                <button
                  onClick={() => setShowUpload(true)}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Subir Archivo
                </button>
              </div>
            </div>

            {/* Lista de archivos */}
            {filesLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="animate-pulse flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
                    <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : filesError ? (
              <div className="text-center py-12">
                <AlertCircle className="w-16 h-16 text-red-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Error cargando archivos
                </h3>
                <p className="text-gray-500 mb-6">
                  No se pudieron cargar los archivos del servidor
                </p>
                <button
                  onClick={() => refetchFiles()}
                  className="btn-primary"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Reintentar
                </button>
              </div>
            ) : !files || files.length === 0 ? (
              <div className="text-center py-12">
                <FileX className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No hay archivos disponibles
                </h3>
                <p className="text-gray-500 mb-6">
                  Sube tu primer archivo CSV de Azure Advisor para comenzar
                </p>
                <button
                  onClick={() => setShowUpload(true)}
                  className="btn-primary"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Subir Archivo
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {files.map((file, index) => (
                  <motion.div
                    key={file.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`relative p-4 border-2 rounded-xl cursor-pointer transition-all hover:shadow-md ${
                      selectedFile?.id === file.id
                        ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedFile(file)}
                  >
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                          <FileText className="w-6 h-6 text-green-600" />
                        </div>
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-medium text-gray-900 truncate">
                            {file.original_filename || file.filename || `Archivo ${file.id}`}
                          </h3>
                          {selectedFile?.id === file.id && (
                            <CheckCircle className="w-5 h-5 text-blue-600" />
                          )}
                        </div>
                        
                        <div className="mt-1 flex items-center space-x-3 text-xs text-gray-500">
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-green-100 text-green-800 font-medium">
                            {(file.file_type || 'csv').toUpperCase()}
                          </span>
                          <span>{formatFileSize(file.file_size || 0)}</span>
                        </div>
                        
                        <div className="mt-2 flex items-center text-xs text-gray-500">
                          <Clock className="w-3 h-3 mr-1" />
                          <span>
                            {file.upload_date || file.created_at
                              ? formatRelativeTime(file.upload_date || file.created_at)
                              : 'Fecha desconocida'
                            }
                          </span>
                        </div>

                        {file.analysis_data && (
                          <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                            <div className="text-gray-600">
                              <span className="font-medium">{file.analysis_data.total_rows || 0}</span> filas
                            </div>
                            <div className="text-gray-600">
                              <span className="font-medium">{file.analysis_data.total_recommendations || 0}</span> recomendaciones
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Panel Derecho - Generador de Reportes */}
        <div className="space-y-6">
          {/* Configuración de Reporte */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Settings className="w-5 h-5 text-purple-600" />
              <h3 className="text-lg font-semibold text-gray-900">
                Configurar Reporte
              </h3>
            </div>

            {!selectedFile ? (
              <div className="text-center py-8">
                <AlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h4 className="text-lg font-medium text-gray-900 mb-2">
                  Selecciona un archivo
                </h4>
                <p className="text-gray-500 text-sm">
                  Primero selecciona un archivo CSV para configurar el reporte
                </p>
              </div>
            ) : (
              <div className="space-y-5">
                {/* Archivo seleccionado */}
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-4 h-4 text-blue-600" />
                    <div>
                      <div className="text-sm font-medium text-blue-900">
                        {selectedFile.original_filename || selectedFile.filename}
                      </div>
                      <div className="text-xs text-blue-700">
                        {formatFileSize(selectedFile.file_size || 0)} • Listo para análisis
                      </div>
                    </div>
                  </div>
                </div>

                {/* Título del reporte */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Título del Reporte
                  </label>
                  <input
                    type="text"
                    value={reportConfig.title}
                    onChange={(e) => setReportConfig(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Ej: Análisis de Seguridad Azure - Marzo 2025"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                {/* Descripción (opcional) */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Descripción (Opcional)
                  </label>
                  <textarea
                    rows={3}
                    value={reportConfig.description}
                    onChange={(e) => setReportConfig(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Describe el propósito de este reporte..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                {/* Tipo de reporte */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Tipo de Análisis
                  </label>
                  <div className="space-y-2">
                    {reportTypes.map((type) => {
                      const IconComponent = type.icon;
                      return (
                        <label
                          key={type.value}
                          className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                            reportConfig.type === type.value
                              ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-200'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <input
                            type="radio"
                            name="reportType"
                            value={type.value}
                            checked={reportConfig.type === type.value}
                            onChange={(e) => setReportConfig(prev => ({ ...prev, type: e.target.value }))}
                            className="sr-only"
                          />
                          <IconComponent className="w-4 h-4 text-blue-600 mr-3" />
                          <div>
                            <div className="text-sm font-medium text-gray-900">{type.label}</div>
                            <div className="text-xs text-gray-500">{type.description}</div>
                          </div>
                        </label>
                      );
                    })}
                  </div>
                </div>

                {/* Opciones adicionales */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Opciones del Reporte
                  </label>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={reportConfig.includeCharts}
                        onChange={(e) => setReportConfig(prev => ({ ...prev, includeCharts: e.target.checked }))}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Incluir gráficos y visualizaciones</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={reportConfig.includeTables}
                        onChange={(e) => setReportConfig(prev => ({ ...prev, includeTables: e.target.checked }))}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Incluir tablas detalladas</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={reportConfig.includeRecommendations}
                        onChange={(e) => setReportConfig(prev => ({ ...prev, includeRecommendations: e.target.checked }))}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Incluir recomendaciones de IA</span>
                    </label>
                  </div>
                </div>

                {/* Botón de generar */}
                <button
                  onClick={handleGenerateReport}
                  disabled={isGenerating || !reportConfig.title.trim()}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center"
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Generando Reporte...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 mr-2" />
                      Generar Reporte con IA
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Reportes Recientes */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <BarChart3 className="w-5 h-5 text-green-600" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Reportes Recientes
                </h3>
              </div>
              <button
                onClick={() => refetchReports()}
                className="text-green-600 hover:text-green-700 text-sm font-medium"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>

            {reportsLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="animate-pulse flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                    <div className="w-8 h-8 bg-gray-200 rounded"></div>
                    <div className="flex-1 space-y-1">
                      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : recentReports && recentReports.length > 0 ? (
              <div className="space-y-3">
                {recentReports.map((report, index) => (
                  <motion.div
                    key={report.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                      report.status === 'completed' ? 'bg-green-100' : 
                      report.status === 'processing' ? 'bg-yellow-100' : 'bg-gray-100'
                    }`}>
                      <FileText className={`w-4 h-4 ${
                        report.status === 'completed' ? 'text-green-600' : 
                        report.status === 'processing' ? 'text-yellow-600' : 'text-gray-600'
                      }`} />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {report.title || `Reporte ${report.id}`}
                      </h4>
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          report.status === 'completed' ? 'bg-green-100 text-green-800' : 
                          report.status === 'processing' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {report.status === 'completed' ? 'Completado' : 
                           report.status === 'processing' ? 'Procesando' : 'Pendiente'}
                        </span>
                        <span>•</span>
                        <span>{formatRelativeTime(report.created_at)}</span>
                      </div>
                    </div>

                    {report.status === 'completed' && (
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => window.open(`/app/reports/${report.id}`, '_blank')}
                          className="p-1 text-gray-400 hover:text-blue-600"
                          title="Ver reporte"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => toast.info('Descarga en desarrollo')}
                          className="p-1 text-gray-400 hover:text-green-600"
                          title="Descargar PDF"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h4 className="text-sm font-medium text-gray-900 mb-1">
                  No hay reportes recientes
                </h4>
                <p className="text-xs text-gray-500">
                  Los reportes generados aparecerán aquí
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal de Upload */}
      {showUpload && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl shadow-xl w-full max-w-md"
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Subir Archivo CSV
                </h3>
                <button
                  onClick={() => setShowUpload(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <FileUpload
                onUploadComplete={handleUploadComplete}
                onError={(error) => {
                  console.error('Error en upload:', error);
                  toast.error('Error subiendo archivo: ' + error.message);
                }}
              />
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Reports;