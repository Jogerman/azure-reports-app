// src/components/reports/ReportsList.jsx - VERSIÓN ACTUALIZADA CON VISUALIZACIÓN
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  Eye, 
  Download, 
  Trash2, 
  Calendar, 
  User, 
  Clock, 
  BarChart3,
  MoreHorizontal,
  Shield,
  DollarSign,
  TrendingUp,
  Zap
} from 'lucide-react';
import { useReportMutations } from '../../hooks/useReports';
import { formatRelativeTime } from '../../utils/helpers';
import ReportViewer from './ReportViewer';
import toast from 'react-hot-toast';

const ReportsList = ({ reports = [], showActions = true, onUpdate }) => {
  const [selectedReportId, setSelectedReportId] = useState(null);
  const [showViewer, setShowViewer] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);

  const { deleteReport, downloadReport } = useReportMutations();

  // Obtener color según estado del reporte
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
      case 'generating':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Obtener icono según estado del reporte
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'processing':
      case 'generating':
        return '⏳';
      case 'failed':
        return '❌';
      default:
        return '📄';
    }
  };

  // Obtener icono según tipo de reporte
  const getReportTypeIcon = (type) => {
    switch (type) {
      case 'security':
        return <Shield className="w-4 h-4 text-blue-600" />;
      case 'cost':
        return <DollarSign className="w-4 h-4 text-green-600" />;
      case 'performance':
        return <Zap className="w-4 h-4 text-yellow-600" />;
      case 'trend':
        return <TrendingUp className="w-4 h-4 text-purple-600" />;
      default:
        return <BarChart3 className="w-4 h-4 text-gray-600" />;
    }
  };

  // Formatear tipo de reporte
  const formatReportType = (type) => {
    const types = {
      'comprehensive': 'Completo',
      'security': 'Seguridad',
      'cost': 'Costos',
      'performance': 'Rendimiento',
      'trend': 'Tendencias'
    };
    return types[type] || type;
  };

  // Manejar visualización del reporte
  const handleViewReport = (report) => {
    setSelectedReport(report);
    setSelectedReportId(report.id);
    setShowViewer(true);
  };

  // Manejar descarga del reporte
  const handleDownloadReport = async (report) => {
    try {
      await downloadReport.mutateAsync({
        reportId: report.id,
        filename: `${report.title}.pdf`
      });
    } catch (error) {
      console.error('Error downloading report:', error);
    }
  };

  // Manejar eliminación del reporte
  const handleDeleteReport = async (reportId) => {
    try {
      await deleteReport.mutateAsync(reportId);
      setShowDeleteConfirm(null);
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Error deleting report:', error);
    }
  };

  // Cerrar visor de reportes
  const handleCloseViewer = () => {
    setShowViewer(false);
    setSelectedReport(null);
    setSelectedReportId(null);
  };

  if (!reports || reports.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <FileText className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No hay reportes disponibles
        </h3>
        <p className="text-gray-500 mb-4">
          Genera tu primer reporte a partir de un archivo CSV
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-4">
        {reports.map((report, index) => (
          <motion.div
            key={report.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-soft border border-gray-200 p-6 hover:shadow-medium transition-shadow"
          >
            <div className="flex items-center justify-between">
              {/* Información del reporte */}
              <div className="flex items-center space-x-4 flex-1 min-w-0">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="font-semibold text-gray-900 truncate">
                      {report.title}
                    </h3>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                      <span className="mr-1">{getStatusIcon(report.status)}</span>
                      {report.status}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      <User className="w-4 h-4 mr-1" />
                      <span>{report.user_name || 'Usuario'}</span>
                    </div>
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      <span>{formatRelativeTime(report.created_at)}</span>
                    </div>
                    <div className="flex items-center">
                      {getReportTypeIcon(report.report_type)}
                      <span className="ml-1">{formatReportType(report.report_type)}</span>
                    </div>
                    {report.generation_time_seconds && (
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        <span>{report.generation_time_seconds}s</span>
                      </div>
                    )}
                  </div>

                  {/* Información del archivo fuente */}
                  {report.source_filename && (
                    <div className="mt-2 text-xs text-gray-500">
                      📁 Generado desde: {report.source_filename}
                    </div>
                  )}

                  {report.description && (
                    <p className="text-sm text-gray-600 mt-2 truncate">
                      {report.description}
                    </p>
                  )}

                  {/* Análisis summary */}
                  {report.analysis_summary && (
                    <div className="flex items-center space-x-4 mt-3 text-xs">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                        📊 {report.analysis_summary.total_recommendations} recomendaciones
                      </span>
                      {report.analysis_summary.cost_savings_identified && (
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full">
                          💰 Ahorros identificados
                        </span>
                      )}
                      {report.analysis_summary.security_issues_found > 0 && (
                        <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded-full">
                          🔒 {report.analysis_summary.security_issues_found} problemas de seguridad
                        </span>
                      )}
                      {report.analysis_summary.estimated_monthly_savings > 0 && (
                        <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
                          💵 ${Math.round(report.analysis_summary.estimated_monthly_savings)}/mes
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Acciones */}
              {showActions && (
                <div className="flex items-center space-x-2 ml-4">
                  {/* Botón Ver reporte */}
                  <button
                    onClick={() => handleViewReport(report)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Ver reporte"
                  >
                    <Eye className="w-4 h-4" />
                  </button>

                  {/* Botón Descargar */}
                  <button
                    onClick={() => handleDownloadReport(report)}
                    disabled={downloadReport.isLoading}
                    className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors disabled:opacity-50"
                    title="Descargar PDF"
                  >
                    <Download className={`w-4 h-4 ${downloadReport.isLoading ? 'animate-pulse' : ''}`} />
                  </button>

                  {/* Botón Eliminar */}
                  <button
                    onClick={() => setShowDeleteConfirm(report.id)}
                    disabled={deleteReport.isLoading}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                    title="Eliminar reporte"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>

                  {/* Menú de más opciones */}
                  <button
                    className="p-2 text-gray-400 hover:bg-gray-50 rounded-lg transition-colors"
                    title="Más opciones"
                  >
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Modal de confirmación de eliminación */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl shadow-xl p-6 max-w-md w-full mx-4"
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <Trash2 className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Eliminar Reporte
                </h3>
                <p className="text-sm text-gray-500">
                  Esta acción no se puede deshacer
                </p>
              </div>
            </div>
            
            <p className="text-gray-600 mb-6">
              ¿Estás seguro de que quieres eliminar este reporte? Se perderán todos los datos y análisis generados.
            </p>
            
            <div className="flex items-center justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => handleDeleteReport(showDeleteConfirm)}
                disabled={deleteReport.isLoading}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center"
              >
                {deleteReport.isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Eliminando...
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4 mr-2" />
                    Eliminar
                  </>
                )}
              </button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Visor de reportes */}
      <ReportViewer
        reportId={selectedReportId}
        reportTitle={selectedReport?.title}
        isOpen={showViewer}
        onClose={handleCloseViewer}
      />
    </>
  );
};

export default ReportsList;