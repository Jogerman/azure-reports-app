// frontend/src/services/storageService.js
import api from './api';

export const storageService = {
  // Obtener archivos en storage
  getStorageFiles: async (filters = {}) => {
    const params = new URLSearchParams(filters).toString();
    const response = await api.get(`/storage/files/?${params}`);
    return response.data;
  },

  // Subir archivo al storage
  uploadFile: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/storage/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
    return response.data;
  },

  // Eliminar archivo del storage
  deleteFile: async (fileId) => {
    const response = await api.delete(`/storage/files/${fileId}/`);
    return response.data;
  },

  // Descargar archivo del storage
  downloadFile: async (fileId) => {
    const response = await api.get(`/storage/files/${fileId}/download/`, {
      responseType: 'blob',
    });
    
    // Crear URL para descargar
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'archivo');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  // Obtener detalles de un archivo
  getFileDetails: async (fileId) => {
    const response = await api.get(`/storage/files/${fileId}/`);
    return response.data;
  },

  // Obtener estadísticas de storage
  getStorageStats: async () => {
    const response = await api.get('/storage/stats/');
    return response.data;
  },

  // Organizar archivos en carpetas
  createFolder: async (folderData) => {
    const response = await api.post('/storage/folders/', folderData);
    return response.data;
  },

  // Obtener carpetas
  getFolders: async () => {
    const response = await api.get('/storage/folders/');
    return response.data;
  },

  // Mover archivo a carpeta
  moveToFolder: async (fileId, folderId) => {
    const response = await api.patch(`/storage/files/${fileId}/`, { folder: folderId });
    return response.data;
  }
};