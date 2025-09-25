// frontend/src/services/reportsService.js
import api from './api';

export const reportsService = {
  // Subir archivo CSV
  uploadCSVFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await api.post('/reports/csv-files/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error subiendo archivo:', error);
      throw new Error(
        error.response?.data?.error || 
        error.response?.data?.detail || 
        'Error al subir el archivo'
      );
    }
  },

  // Obtener lista de archivos CSV
  getCSVFiles: async () => {
    try {
      const response = await api.get('/reports/csv-files/');
      return response.data;
    } catch (error) {
      console.error('Error obteniendo archivos:', error);
      throw error;
    }
  },

  // Obtener detalles de análisis de un archivo
  getAnalysisDetails: async (fileId) => {
    try {
      const response = await api.get(`/reports/csv-files/${fileId}/analysis_details/`);
      return response.data;
    } catch (error) {
      console.error('Error obteniendo análisis:', error);
      throw error;
    }
  },

  // Crear reporte
  createReport: async (reportData) => {
    try {
      const response = await api.post('/reports/reports/', reportData);
      return response.data;
    } catch (error) {
      console.error('Error creando reporte:', error);
      throw error;
    }
  },

  // Obtener reportes
  getReports: async () => {
    try {
      const response = await api.get('/reports/reports/');
      return response.data;
    } catch (error) {
      console.error('Error obteniendo reportes:', error);
      throw error;
    }
  },

  // Descargar reporte (agregado para ReportsList)
  downloadReport: async (reportId) => {
    try {
      const response = await api.get(`/reports/reports/${reportId}/download/`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error descargando reporte:', error);
      throw error;
    }
  },

  // Obtener preview de reporte (agregado para ReportsList)
  getReportPreview: async (reportId) => {
    try {
      const response = await api.get(`/reports/reports/${reportId}/preview/`);
      return response.data;
    } catch (error) {
      console.error('Error obteniendo preview:', error);
      throw error;
    }
  }
};

// Exportación por defecto también para compatibilidad
export default reportsService;