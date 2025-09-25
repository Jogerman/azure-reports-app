// src/pages/Storage.jsx - VERSIÓN DE PRODUCCIÓN LIMPIA
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Cloud, 
  FolderOpen, 
  FileText, 
  Download, 
  Search, 
  Upload,
  Trash2,
  Eye,
  RefreshCw,
  MoreVertical,
  File,
  Database,
  HardDrive
} from 'lucide-react';

// ✅ SOLO IMPORT DE PRODUCCIÓN
import { useFiles } from '../hooks/useReports';

import Loading from '../components/common/Loading';
import { formatFileSize, formatRelativeTime } from '../utils/helpers';
import toast from 'react-hot-toast';

const Storage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [fileType, setFileType] = useState('all');
  const [selectedFiles, setSelectedFiles] = useState(new Set());
  
  // ✅ HOOK DE PRODUCCIÓN
  const { data: allFiles, isLoading, refetch } = useFiles();

  // Filtrar archivos en el frontend
  const files = React.useMemo(() => {
    if (!allFiles) return [];
    
    let filtered = allFiles;
    
    // Filtro por búsqueda
    if (searchTerm) {
      filtered = filtered.filter(file => {
        const filename = file.original_filename || file.filename || '';
        return filename.toLowerCase().includes(searchTerm.toLowerCase());
      });
    }
    
    // Filtro por tipo
    if (fileType !== 'all') {
      filtered = filtered.filter(file => {
        const filename = file.original_filename || file.filename || '';
        const extension = filename.split('.').pop()?.toLowerCase();
        return extension === fileType;
      });
    }
    
    return filtered;
  }, [allFiles, searchTerm, fileType]);

  const handleFileSelect = (fileId) => {
    const newSelected = new Set(selectedFiles);
    if (newSelected.has(fileId)) {
      newSelected.delete(fileId);
    } else {
      newSelected.add(fileId);
    }
    setSelectedFiles(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedFiles.size === files?.length) {
      setSelectedFiles(new Set());
    } else {
      setSelectedFiles(new Set(files?.map(f => f.id) || []));
    }
  };

  const handleDeleteSelected = () => {
    if (selectedFiles.size === 0) return;
    
    // TODO: Implementar eliminación real con API
    toast.success(`${selectedFiles.size} archivo(s) marcado(s) para eliminación`);
    setSelectedFiles(new Set());
    // refetch(); // Descomentar cuando se implemente la API
  };

  const handleDownloadFile = (file) => {
    // TODO: Implementar descarga real
    toast.success(`Descargando ${file.original_filename || file.filename}`);
  };

  const getFileIcon = (filename) => {
    const extension = filename?.split('.').pop()?.toLowerCase();
    if (extension === 'csv') return <FileText className="w-6 h-6 text-green-500" />;
    if (['xlsx', 'xls'].includes(extension)) return <File className="w-6 h-6 text-blue-500" />;
    return <File className="w-6 h-6 text-gray-500" />;
  };

  // Estadísticas calculadas
  const stats = React.useMemo(() => {
    if (!allFiles) return { totalFiles: 0, totalRows: 0, totalSize: 0 };
    
    return {
      totalFiles: allFiles.length,
      totalRows: allFiles.reduce((sum, file) => sum + (file.rows_count || 0), 0),
      totalSize: allFiles.reduce((sum, file) => sum + (file.file_size || file.size || 0), 0)
    };
  }, [allFiles]);

  if (isLoading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Almacenamiento</h1>
          <p className="text-gray-600 mt-1">
            Gestiona tus archivos CSV y datos procesados
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={refetch}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Actualizar
          </button>
          <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
            <Upload className="w-4 h-4" />
            Subir Archivo
          </button>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <HardDrive className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Archivos</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalFiles}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Database className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Filas Totales</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.totalRows.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Cloud className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Tamaño Total</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatFileSize(stats.totalSize)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <FolderOpen className="w-6 h-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Seleccionados</p>
              <p className="text-2xl font-bold text-gray-900">{selectedFiles.size}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Controles */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
          <div className="flex items-center gap-4 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-64">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Buscar archivos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <select
              value={fileType}
              onChange={(e) => setFileType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Todos los tipos</option>
              <option value="csv">CSV</option>
              <option value="xlsx">Excel</option>
              <option value="json">JSON</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            {selectedFiles.size > 0 && (
              <button
                onClick={handleDeleteSelected}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                Eliminar ({selectedFiles.size})
              </button>
            )}
            
            <button
              onClick={handleSelectAll}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              {selectedFiles.size === files?.length ? 'Deseleccionar Todo' : 'Seleccionar Todo'}
            </button>
          </div>
        </div>
      </div>

      {/* Lista de archivos */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {files && files.length > 0 ? (
          <div className="overflow-hidden">
            <div className="grid grid-cols-1 divide-y divide-gray-200">
              {files.map((file) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`p-6 hover:bg-gray-50 transition-colors ${
                    selectedFiles.has(file.id) ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <input
                        type="checkbox"
                        checked={selectedFiles.has(file.id)}
                        onChange={() => handleFileSelect(file.id)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      
                      {getFileIcon(file.original_filename || file.filename)}
                      
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">
                          {file.original_filename || file.filename || 'Archivo sin nombre'}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                          <span>{formatFileSize(file.file_size || file.size || 0)}</span>
                          <span>•</span>
                          <span>{(file.rows_count || 0).toLocaleString()} filas</span>
                          <span>•</span>
                          <span>{formatRelativeTime(file.upload_date || file.created_at)}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleDownloadFile(file)}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                        title="Descargar"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                      
                      <button
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                        title="Ver detalles"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      
                      <button
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                        title="Más opciones"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <FolderOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No hay archivos</h3>
            <p className="text-gray-500 mb-4">
              {searchTerm || fileType !== 'all' 
                ? 'No se encontraron archivos con esos criterios' 
                : 'Sube tu primer archivo para comenzar'
              }
            </p>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              <Upload className="w-4 h-4 inline mr-2" />
              Subir Archivo
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Storage;