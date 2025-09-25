// frontend/src/services/apiService.js
import { apiClient } from './authService';

// Servicio centralizado para todas las peticiones API
export const apiService = {
  // Dashboard
  async getDashboardStats() {
    try {
      const response = await apiClient.get('/dashboard/stats/');
      return response.data;
    } catch (error) {
      console.error('Error obteniendo stats del dashboard:', error);
      throw error;
    }
  },

  async getDashboardActivity() {
    try {
      const response = await apiClient.get('/dashboard/activity/');
      return response.data;
    } catch (error) {
      console.error('Error obteniendo actividad del dashboard:', error);
      throw error;
    }
  },

  // Reportes
  async getReports(params = {}) {
    try {
      const response = await apiClient.get('/reports/', { params });
      return response.data;
    } catch (error) {
      console.error('Error obteniendo reportes:', error);
      throw error;
    }
  },

  async getReport(id) {
    try {
      const response = await apiClient.get(`/reports/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error obteniendo reporte:', error);
      throw error;
    }
  },

  async createReport(data) {
    try {
      const response = await apiClient.post('/reports/', data);
      return response.data;
    } catch (error) {
      console.error('Error creando reporte:', error);
      throw error;
    }
  },

  async updateReport(id, data) {
    try {
      const response = await apiClient.put(`/reports/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('Error actualizando reporte:', error);
      throw error;
    }
  },

  async deleteReport(id) {
    try {
      const response = await apiClient.delete(`/reports/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error eliminando reporte:', error);
      throw error;
    }
  },

  // Archivos
  async getFiles(params = {}) {
    try {
      const response = await apiClient.get('/files/', { params });
      return response.data;
    } catch (error) {
      console.error('Error obteniendo archivos:', error);
      throw error;
    }
  },

  async uploadFile(formData) {
    try {
      const response = await apiClient.post('/files/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error subiendo archivo:', error);
      throw error;
    }
  },

  // Usuario
  async getCurrentUser() {
    try {
      const response = await apiClient.get('/auth/users/');
      return response.data.results?.[0] || response.data;
    } catch (error) {
      console.error('Error obteniendo usuario actual:', error);
      throw error;
    }
  },

  async updateUser(id, data) {
    try {
      const response = await apiClient.put(`/auth/users/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('Error actualizando usuario:', error);
      throw error;
    }
  }
};

export default apiService;