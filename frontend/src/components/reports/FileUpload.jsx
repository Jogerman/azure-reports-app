// src/components/reports/FileUpload.jsx - VERSIÓN CON DEBUG
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';
import { useFileUpload } from '../../hooks/useReports';
import toast from 'react-hot-toast';

const FileUpload = ({ onUploadComplete }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const { uploadFile, isUploading, progress } = useFileUpload();

  const onDrop = useCallback(async (acceptedFiles) => {
    console.log('🔄 Archivos seleccionados:', acceptedFiles);
    
    const results = [];
    
    for (const file of acceptedFiles) {
      try {
        console.log('📤 Subiendo archivo:', file.name);
        
        // Subir archivo
        const result = await uploadFile(file);
        
        console.log('✅ Respuesta del servidor:', result);
        
        // Verificar estructura de la respuesta
        const fileData = {
          id: result.id || result.file_id,
          original_filename: result.original_filename || result.filename || file.name,
          filename: result.filename || file.name,
          file_size: result.file_size || result.size || file.size,
          rows_count: result.rows_count || result.row_count || 0,
          upload_date: result.upload_date || result.created_at || new Date().toISOString(),
          created_at: result.created_at || new Date().toISOString(),
          processing_status: result.processing_status || 'completed'
        };
        
        console.log('📋 Archivo procesado:', fileData);
        
        results.push(fileData);
        setUploadedFiles(prev => [...prev, fileData]);
        
      } catch (error) {
        console.error('❌ Error subiendo archivo:', file.name, error);
        toast.error(`Error subiendo ${file.name}: ${error.message}`);
      }
    }
    
    if (results.length > 0) {
      console.log('🎉 Notificando archivos subidos:', results);
      
      // Notificar al componente padre
      if (onUploadComplete) {
        onUploadComplete(results);
      }
      
      // Limpiar estado local después de un delay
      setTimeout(() => {
        setUploadedFiles([]);
      }, 2000);
    }
  }, [uploadFile, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    multiple: true,
    disabled: isUploading
  });

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      {/* Zona de drop */}
      <motion.div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : isUploading 
            ? 'border-gray-300 bg-gray-50 cursor-not-allowed'
            : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
        }`}
        whileHover={!isUploading ? { scale: 1.02 } : {}}
        whileTap={!isUploading ? { scale: 0.98 } : {}}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-3">
          <Upload className={`w-12 h-12 ${isDragActive ? 'text-blue-500' : 'text-gray-400'}`} />
          
          {isUploading ? (
            <div className="space-y-2">
              <p className="text-gray-600">Subiendo archivo...</p>
              <div className="w-64 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm text-gray-500">{Math.round(progress)}%</p>
            </div>
          ) : (
            <div>
              <p className="text-gray-600 text-lg font-medium">
                {isDragActive ? 'Suelta los archivos aquí' : 'Arrastra archivos CSV o haz clic para seleccionar'}
              </p>
              <p className="text-gray-500 text-sm mt-1">
                Formatos soportados: CSV, XLS, XLSX
              </p>
            </div>
          )}
        </div>
      </motion.div>

      {/* Lista de archivos subidos */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium text-gray-900">Archivos procesados:</h3>
          {uploadedFiles.map((file, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <FileText className="w-5 h-5 text-green-600" />
                <div>
                  <p className="font-medium text-green-900">{file.original_filename}</p>
                  <p className="text-sm text-green-700">
                    {file.rows_count?.toLocaleString()} filas • ID: {file.id}
                  </p>
                </div>
              </div>
              <button
                onClick={() => removeFile(index)}
                className="text-green-500 hover:text-green-700"
              >
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          ))}
        </div>
      )}

      {/* Debug info */}
      {process.env.NODE_ENV === 'development' && uploadedFiles.length > 0 && (
        <details className="mt-4">
          <summary className="cursor-pointer text-sm text-gray-500">Debug: Ver respuesta del servidor</summary>
          <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-auto">
            {JSON.stringify(uploadedFiles, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
};

export default FileUpload;