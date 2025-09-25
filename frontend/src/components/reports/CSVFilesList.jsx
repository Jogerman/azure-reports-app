/* eslint-disable no-undef */
// src/components/reports/CSVFilesList.jsx
import React, { useState } from 'react';
import { 
  FileText, 
  MoreHorizontal, 
  Eye, 
  Download, 
  RefreshCw,
  Trash2,
  Calendar,
  Database
} from 'lucide-react';
import { formatRelativeTime } from '../../utils/helpers';
import { getStatusColor, getStatusIcon } from '../../utils/formatters';

const CSVFilesList = ({ csvFiles = [], onFileSelect, onRefresh }) => {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    if (onFileSelect) {
      onFileSelect(file);
    }
  };

  if (csvFiles.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-soft border border-gray-200 p-12 text-center">
        <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          No hay archivos CSV
        </h3>
        <p className="text-gray-600 mb-6">
          Sube tu primer archivo CSV para comenzar a generar reportes
        </p>
        <button className="btn-primary">
          Subir Archivo
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Mis Archivos CSV</h2>
          <p className="text-gray-600">Gestiona y selecciona archivos para generar reportes</p>
        </div>
        <button
          onClick={onRefresh}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Actualizar</span>
        </button>
      </div>

      {/* Lista de archivos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {csvFiles.map((file, index) => (
          <motion.div
            key={file.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`bg-white rounded-xl shadow-soft border-2 transition-all duration-200 cursor-pointer hover:shadow-medium ${
              selectedFile?.id === file.id 
                ? 'border-primary-500 bg-primary-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => handleFileSelect(file)}
          >
            <div className="p-6">
              {/* Header del archivo */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-green-500 rounded-xl flex items-center justify-center">
                    <FileText className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 truncate">
                      {file.original_filename}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {formatFileSize(file.file_size)}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(file.processing_status)}`}>
                    <span className="mr-1">{getStatusIcon(file.processing_status)}</span>
                    {file.processing_status}
                  </span>
                  
                  <button className="p-1 text-gray-400 hover:text-gray-600 rounded">
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Metadatos */}
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Filas:</span>
                    <p className="font-medium text-gray-900">
                      {file.rows_count ? file.rows_count.toLocaleString() : 'Procesando...'}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Columnas:</span>
                    <p className="font-medium text-gray-900">
                      {file.columns_count || 'Procesando...'}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center text-sm text-gray-500">
                  <Calendar className="w-4 h-4 mr-1" />
                  <span>Subido {formatRelativeTime(file.upload_date)}</span>
                </div>

                {/* Análisis summary */}
                {file.analysis_summary && (
                  <div className="bg-gray-50 rounded-lg p-3 text-sm">
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <span className="text-gray-500">Calidad:</span>
                        <span className="ml-1 font-medium text-green-600">
                          {file.analysis_summary.data_quality_score}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Insights:</span>
                        <span className="ml-1 font-medium text-blue-600">
                          {file.analysis_summary.total_insights}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Acciones */}
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-2">
                  {file.processing_status === 'completed' && (
                    <>
                      <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                        <Download className="w-4 h-4" />
                      </button>
                    </>
                  )}
                </div>
                
                {selectedFile?.id === file.id && (
                  <span className="text-xs font-medium text-primary-600">
                    Seleccionado
                  </span>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default CSVFilesList;