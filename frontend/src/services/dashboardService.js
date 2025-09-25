// frontend/src/services/dashboardService.js
import api from './api';

export const dashboardService = {
  // Obtener estadísticas del dashboard
  getStats: async () => {
    const response = await api.get('/dashboard/stats/');
    return response.data;
  },

  // Obtener reportes recientes
  getRecentReports: async (limit = 5) => {
    const response = await api.get(`/dashboard/recent-reports/?limit=${limit}`);
    return response.data;
  },

  // Obtener actividad reciente
  getRecentActivity: async (limit = 10) => {
    const response = await api.get(`/dashboard/recent-activity/?limit=${limit}`);
    return response.data;
  },

  // Obtener datos de gráficos
  getChartData: async (type, period = '7d') => {
    const response = await api.get(`/dashboard/charts/${type}/?period=${period}`);
    return response.data;
  },

  // Obtener resumen de reportes por estado
  getReportsByStatus: async () => {
    const response = await api.get('/dashboard/reports-by-status/');
    return response.data;
  },

  // Obtener métricas de rendimiento
  getPerformanceMetrics: async () => {
    const response = await api.get('/dashboard/performance/');
    return response.data;
  }
};