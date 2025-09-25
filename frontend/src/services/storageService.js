// frontend/src/services/storageService.js - VERSIÓN CORREGIDA
import api from './api';

export const storageService = {
  // ✅ CORREGIDO: Usar /files/ en lugar de /storage/files/
  getStorageFiles: async (filters = {}) => {
    const params = new URLSearchParams(filters).toString();
    const response = await api.get(`/files/?${params}`);
    return response.data;
  },

  // ✅ CORREGIDO: Usar /files/upload/ en lugar de /storage/upload/
  uploadFile: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/files/upload/', formData, {
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

  // ✅ CORREGIDO: Usar /files/ en lugar de /storage/files/
  deleteFile: async (fileId) => {
    const response = await api.delete(`/files/${fileId}/`);
    return response.data;
  },

  // ✅ CORREGIDO: Usar /files/ en lugar de /storage/files/
  downloadFile: async (fileId) => {
    const response = await api.get(`/files/${fileId}/download/`, {
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

  // ✅ CORREGIDO: Usar /files/ en lugar de /storage/files/
  getFileDetails: async (fileId) => {
    const response = await api.get(`/files/${fileId}/`);
    return response.data;
  },

  // ✅ CORREGIDO: Usar /files/stats/ en lugar de /storage/stats/
  getStorageStats: async () => {
    const response = await api.get('/files/stats/');
    return response.data;
  },

  // ✅ CORREGIDO: Usar /files/folders/ en lugar de /storage/folders/
  createFolder: async (folderData) => {
    const response = await api.post('/files/folders/', folderData);
    return response.data;
  },

  // ✅ CORREGIDO: Usar /files/folders/ en lugar de /storage/folders/
  getFolders: async () => {
    const response = await api.get('/files/folders/');
    return response.data;
  },

  // ✅ CORREGIDO: Usar /files/ en lugar de /storage/files/
  moveToFolder: async (fileId, folderId) => {
    const response = await api.patch(`/files/${fileId}/`, { folder: folderId });
    return response.data;
  }
};