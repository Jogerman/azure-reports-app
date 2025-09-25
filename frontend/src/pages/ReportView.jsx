// src/pages/ReportView.jsx - Página para visualizar reporte individual
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Download, 
  Share2, 
  Eye, 
  FileText,
  Calendar,
  User,
  BarChart3,
  RefreshCw
} from 'lucide-react';
import { useReportHTML } from '../hooks/useReports';
import Loading from '../components/common/Loading';
import { formatRelativeTime } from '../utils/helpers';
import toast from 'react-hot-toast';

const ReportView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const { data: reportHTML, isLoading, error, refetch } = useReportHTML(id);

  const handleDownloadPDF = async () => {
    try {
      // Crear enlace de descarga
      const downloadUrl = `${import.meta.env.VITE_API_URL}/reports/${id}/download/`;
      const token = localStorage.getItem('token');
      
      // Descargar archivo
      const response = await fetch(downloadUrl, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Error descargando reporte');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `reporte_${id.slice(0, 8)}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Reporte descargado exitosamente');
    } catch (error) {
      console.error('Error descargando reporte:', error);
      toast.error('Error descargando reporte');
    }
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    toast.success('Enlace copiado al portapapeles');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Cargando reporte...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <FileText className="w-16 h-16 text-red-300 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error cargando reporte</h2>
          <p className="text-gray-600 mb-4">{error.message}</p>
          <div className="space-x-4">
            <button
              onClick={() => navigate('/app/reports')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Volver a Reportes
            </button>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/app/reports')}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                Volver a Reportes
              </button>
              <div className="h-6 w-px bg-gray-300" />
              <div className="flex items-center gap-2">
                <BarChart3 className="w-6 h-6 text-blue-600" />
                <h1 className="text-xl font-semibold text-gray-900">
                  Reporte de Análisis
                </h1>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleShare}
                className="flex items-center gap-2 px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Share2 className="w-4 h-4" />
                Compartir
              </button>
              
              <button
                onClick={handleDownloadPDF}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Download className="w-4 h-4" />
                Descargar PDF
              </button>
            </div>
          </div>

          {/* Metadata del reporte */}
          <div className="flex items-center gap-6 mt-4 text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              Generado {formatRelativeTime(new Date().toISOString())}
            </div>
            <div className="flex items-center gap-1">
              <FileText className="w-4 h-4" />
              ID: {id.slice(0, 8)}...
            </div>
            <div className="flex items-center gap-1">
              <Eye className="w-4 h-4" />
              Vista HTML
            </div>
          </div>
        </div>
      </div>

      {/* Contenido del reporte */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {reportHTML ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
          >
            <div 
              className="report-content p-8"
              dangerouslySetInnerHTML={{ __html: reportHTML }}
            />
          </motion.div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12">
            <div className="text-center">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Reporte generado exitosamente
              </h3>
              <p className="text-gray-600 mb-6">
                Tu reporte ha sido creado y está listo para descargar.
              </p>
              <button
                onClick={handleDownloadPDF}
                className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Download className="w-5 h-5" />
                Descargar Reporte PDF
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportView;