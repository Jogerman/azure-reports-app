// src/components/reports/ReportViewer.jsx - Componente para visualizar reportes HTML
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  X, 
  Download, 
  Maximize2, 
  Minimize2, 
  RefreshCw, 
  AlertCircle,
  FileText,
  Loader
} from 'lucide-react';
import { useReportHTML, useReportMutations } from '../../hooks/useReports';
import toast from 'react-hot-toast';

const ReportViewer = ({ reportId, reportTitle, onClose, isOpen = false }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Hooks para datos y mutaciones
  const { 
    data: reportHTML, 
    isLoading, 
    error, 
    refetch 
  } = useReportHTML(reportId);
  
  const { downloadReport } = useReportMutations();

  // Manejar descarga del reporte
  const handleDownload = async () => {
    try {
      await downloadReport.mutateAsync({
        reportId,
        filename: `${reportTitle || 'reporte'}.pdf`
      });
    } catch (error) {
      console.error('Error downloading report:', error);
    }
  };

  // Manejar refrescar reporte
  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await refetch();
      toast.success('Reporte actualizado');
    } catch (error) {
      toast.error('Error actualizando reporte');
    } finally {
      setIsRefreshing(false);
    }
  };

  // Manejar fullscreen
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  // Manejar tecla ESC para cerrar
  React.useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        if (isFullscreen) {
          setIsFullscreen(false);
        } else {
          onClose();
        }
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, isFullscreen, onClose]);

  // No renderizar si no está abierto
  if (!isOpen) return null;

  return (
    <div className={`fixed inset-0 z-50 ${isFullscreen ? 'p-0' : 'p-4'}`}>
      {/* Overlay */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={isFullscreen ? undefined : onClose}
      />
      
      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className={`relative bg-white shadow-2xl flex flex-col ${
          isFullscreen 
            ? 'w-full h-full rounded-none' 
            : 'w-full max-w-7xl h-[90vh] mx-auto mt-[5vh] rounded-xl'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50 rounded-t-xl">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {reportTitle || 'Vista Previa del Reporte'}
              </h3>
              <p className="text-sm text-gray-500">
                Reporte ID: {reportId}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Botón refrescar */}
            <button
              onClick={handleRefresh}
              disabled={isRefreshing || isLoading}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
              title="Actualizar reporte"
            >
              <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
            
            {/* Botón descargar */}
            <button
              onClick={handleDownload}
              disabled={downloadReport.isLoading}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
              title="Descargar PDF"
            >
              <Download className={`w-5 h-5 ${downloadReport.isLoading ? 'animate-pulse' : ''}`} />
            </button>
            
            {/* Botón fullscreen */}
            <button
              onClick={toggleFullscreen}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
              title={isFullscreen ? 'Salir de pantalla completa' : 'Pantalla completa'}
            >
              {isFullscreen ? (
                <Minimize2 className="w-5 h-5" />
              ) : (
                <Maximize2 className="w-5 h-5" />
              )}
            </button>
            
            {/* Botón cerrar */}
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
              title="Cerrar"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Contenido del reporte */}
        <div className="flex-1 overflow-hidden bg-white">
          {isLoading ? (
            // Estado de carga
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loader className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-4" />
                <p className="text-gray-600 font-medium">Cargando reporte...</p>
                <p className="text-sm text-gray-500 mt-1">
                  Generando visualizaciones y gráficos
                </p>
              </div>
            </div>
          ) : error ? (
            // Estado de error
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-900 mb-2">
                  Error al cargar el reporte
                </h4>
                <p className="text-gray-600 mb-4">
                  {error.message || 'No se pudo cargar la visualización del reporte.'}
                </p>
                <div className="flex items-center justify-center space-x-3">
                  <button
                    onClick={handleRefresh}
                    className="btn-primary flex items-center"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Reintentar
                  </button>
                  <button
                    onClick={handleDownload}
                    className="btn-secondary flex items-center"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Descargar PDF
                  </button>
                </div>
              </div>
            </div>
          ) : reportHTML ? (
            // Contenido del reporte HTML
            <div className="h-full overflow-auto">
              <div 
                className="report-content"
                dangerouslySetInnerHTML={{ __html: reportHTML }}
                style={{
                  padding: '20px',
                  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                }}
              />
            </div>
          ) : (
            // Estado vacío
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-900 mb-2">
                  Reporte no disponible
                </h4>
                <p className="text-gray-600 mb-4">
                  El contenido del reporte no está disponible en este momento.
                </p>
                <button
                  onClick={handleDownload}
                  className="btn-primary flex items-center mx-auto"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Descargar PDF
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer con información adicional */}
        {reportHTML && (
          <div className="border-t border-gray-200 bg-gray-50 px-4 py-2">
            <div className="flex items-center justify-between text-sm text-gray-500">
              <span>
                Presiona ESC para {isFullscreen ? 'salir de pantalla completa' : 'cerrar'}
              </span>
              <span>
                Última actualización: {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>
        )}
      </motion.div>

      {/* Estilos para el contenido del reporte */}
      <style jsx>{`
        .report-content {
          line-height: 1.6;
        }
        
        .report-content h1,
        .report-content h2,
        .report-content h3,
        .report-content h4,
        .report-content h5,
        .report-content h6 {
          color: #1f2937;
          margin-bottom: 0.5rem;
          margin-top: 1rem;
        }
        
        .report-content h1 {
          font-size: 2rem;
          font-weight: 700;
          border-bottom: 2px solid #e5e7eb;
          padding-bottom: 0.5rem;
        }
        
        .report-content h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #374151;
        }
        
        .report-content h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #4b5563;
        }
        
        .report-content table {
          width: 100%;
          border-collapse: collapse;
          margin: 1rem 0;
          background: white;
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .report-content th,
        .report-content td {
          padding: 0.75rem;
          text-align: left;
          border-bottom: 1px solid #e5e7eb;
        }
        
        .report-content th {
          background-color: #f9fafb;
          font-weight: 600;
          color: #374151;
        }
        
        .report-content tr:hover {
          background-color: #f9fafb;
        }
        
        .report-content .chart-container {
          margin: 1.5rem 0;
          text-align: center;
        }
        
        .report-content .metric-card {
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          padding: 1rem;
          margin: 0.5rem 0;
        }
        
        .report-content .highlight {
          background: #fef3c7;
          padding: 0.125rem 0.25rem;
          border-radius: 4px;
        }
        
        .report-content .success {
          color: #059669;
          font-weight: 600;
        }
        
        .report-content .warning {
          color: #d97706;
          font-weight: 600;
        }
        
        .report-content .error {
          color: #dc2626;
          font-weight: 600;
        }
      `}</style>
    </div>
  );
};

export default ReportViewer;