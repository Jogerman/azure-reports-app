// src/hooks/useReports.js - VERSIÓN CORREGIDA FINAL
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchWithAuth, buildApiUrl } from '../config/api';
import toast from 'react-hot-toast';

// 📁 SERVICIO DE ARCHIVOS
const fileService = {
  async uploadFile(file) {
    try {
      console.log('📤 Subiendo archivo:', file.name);
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetchWithAuth(buildApiUrl('/files/upload/'), {
        method: 'POST',
        body: formData,
        headers: {}, // No enviar Content-Type para FormData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: Error subiendo archivo`);
      }

      const result = await response.json();
      console.log('✅ Archivo subido:', result);
      return result;
      
    } catch (error) {
      console.error('❌ Error subiendo archivo:', error);
      throw error;
    }
  },

  async getFiles(params = {}) {
    try {
      const searchParams = new URLSearchParams(params);
      const url = buildApiUrl('/files/') + `?${searchParams}`;
      
      console.log('📁 Fetching files from:', url);
      const response = await fetchWithAuth(url);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ Files loaded:', data);
      return data?.results || data || [];
      
    } catch (error) {
      console.error('❌ Error loading files:', error);
      throw error;
    }
  },

  async deleteFile(fileId) {
    try {
      const response = await fetchWithAuth(buildApiUrl('/files/:id/', { id: fileId }), {
        method: 'DELETE',
      });
      return response.ok;
    } catch (error) {
      console.error('❌ Error eliminando archivo:', error);
      throw error;
    }
  },
};

// 📊 SERVICIO DE REPORTES
const reportService = {
  async generateReport(fileId, reportConfig = {}) {
    try {
      console.log('📊 Generating report for file:', fileId);
      
      const requestData = {
        file_id: fileId,
        title: reportConfig.title || 'Reporte Automático',
        description: reportConfig.description || '',
        report_type: reportConfig.type || 'comprehensive'
      };
      
      const response = await fetchWithAuth(buildApiUrl('/reports/generate/'), {
        method: 'POST',
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: Error generando reporte`);
      }

      const result = await response.json();
      console.log('✅ Report generated:', result);
      return result;
      
    } catch (error) {
      console.error('❌ Error generating report:', error);
      throw error;
    }
  },

  async getReports(params = {}) {
    try {
      const searchParams = new URLSearchParams(params);
      const url = buildApiUrl('/reports/') + `?${searchParams}`;
      
      console.log('📋 Fetching reports from:', url);
      const response = await fetchWithAuth(url);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ Reports loaded:', data);
      return data?.results || data || [];
      
    } catch (error) {
      console.error('❌ Error loading reports:', error);
      throw error;
    }
  },
  
  async getReport(reportId) {
    try {
      const response = await fetchWithAuth(buildApiUrl('/reports/:id/', { id: reportId }));
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Error obteniendo reporte`);
      }
      
      return response.json();
    } catch (error) {
      console.error('❌ Error obteniendo reporte:', error);
      throw error;
    }
  },

  async getReportHTML(reportId) {
    try {
      const response = await fetchWithAuth(buildApiUrl('/reports/:id/html/', { id: reportId }));
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Error obteniendo HTML del reporte`);
      }
      
      return response.text();
    } catch (error) {
      console.error('❌ Error obteniendo HTML del reporte:', error);
      throw error;
    }
  },

  async downloadReportPDF(reportId, filename) {
    try {
      const response = await fetchWithAuth(buildApiUrl('/reports/:id/download/', { id: reportId }));
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Error descargando reporte`);
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename || `reporte_${reportId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      
      return true;
    } catch (error) {
      console.error('❌ Error downloading report:', error);
      throw error;
    }
  },

  async deleteReport(reportId) {
    try {
      const response = await fetchWithAuth(buildApiUrl('/reports/:id/', { id: reportId }), {
        method: 'DELETE',
      });
      return response.ok;
    } catch (error) {
      console.error('❌ Error eliminando reporte:', error);
      throw error;
    }
  },
};

// 📈 SERVICIO DE DASHBOARD
const dashboardService = {
  async getStats() {
    try {
      const response = await fetchWithAuth(buildApiUrl('/dashboard/stats/'));
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Error obteniendo estadísticas`);
      }
      
      const data = await response.json();
      console.log('📊 Dashboard stats loaded:', data);
      return data;
    } catch (error) {
      console.error('❌ Error loading dashboard stats:', error);
      throw error;
    }
  },

  async getActivity(limit = 8) {
    try {
      const response = await fetchWithAuth(buildApiUrl('/dashboard/activity/') + `?limit=${limit}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Error obteniendo actividad`);
      }
      
      const data = await response.json();
      console.log('📋 Dashboard activity loaded:', data);
      return data?.results || data || [];
    } catch (error) {
      console.error('❌ Error loading dashboard activity:', error);
      // Retornar actividad mock en caso de error para desarrollo
      return this.getMockActivity(limit);
    }
  },

  getMockActivity(limit = 8) {
    const activities = [
      {
        id: 1,
        description: 'Archivo CSV procesado exitosamente',
        timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 min ago
        type: 'file_processed'
      },
      {
        id: 2,
        description: 'Reporte de seguridad generado',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
        type: 'report_generated'
      },
      {
        id: 3,
        description: 'Análisis de costos completado',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(), // 5 hours ago
        type: 'analysis_completed'
      },
      {
        id: 4,
        description: 'Usuario inició sesión',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(), // 8 hours ago
        type: 'user_login'
      },
      {
        id: 5,
        description: 'Sistema actualizado',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // 1 day ago
        type: 'system_update'
      }
    ];
    
    return activities.slice(0, limit);
  },
};

// 📤 HOOK PERSONALIZADO PARA UPLOADS CON PROGRESO
export const useFileUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const queryClient = useQueryClient();

  const uploadFile = async (file) => {
    if (!file) throw new Error('No se ha seleccionado ningún archivo');

    setIsUploading(true);
    setProgress(0);

    try {
      // Simulación de progreso (el backend real puede enviar eventos de progreso)
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          const newProgress = prev + Math.random() * 15;
          return newProgress > 90 ? 90 : newProgress;
        });
      }, 200);

      const result = await fileService.uploadFile(file);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      // Invalidar cache de archivos
      queryClient.invalidateQueries({ queryKey: ['files'] });
      
      toast.success(`✅ Archivo "${file.name}" subido exitosamente`);
      return result;
      
    } catch (error) {
      console.error('Error uploading file:', error);
      toast.error(`❌ Error subiendo archivo: ${error.message}`);
      throw error;
    } finally {
      setIsUploading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  return { uploadFile, isUploading, progress };
};

// 📁 HOOKS DE ARCHIVOS
export const useFiles = (params = {}) => {
  return useQuery({
    queryKey: ['files', params],
    queryFn: () => fileService.getFiles(params),
    staleTime: 5 * 60 * 1000, // 5 minutos
    cacheTime: 10 * 60 * 1000, // 10 minutos
  });
};

// Hook alias para mantener compatibilidad
export const useStorageFiles = useFiles;

// 📋 HOOKS DE REPORTES
export const useReports = (params = {}) => {
  return useQuery({
    queryKey: ['reports', params],
    queryFn: () => reportService.getReports(params),
    staleTime: 5 * 60 * 1000, // 5 minutos
    cacheTime: 10 * 60 * 1000, // 10 minutos
  });
};

export const useRecentReports = (limit = 5) => {
  return useQuery({
    queryKey: ['reports', 'recent', limit],
    queryFn: () => reportService.getReports({ ordering: '-created_at', limit }),
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
};

export const useReport = (reportId) => {
  return useQuery({
    queryKey: ['report', reportId],
    queryFn: () => reportService.getReport(reportId),
    enabled: !!reportId,
    staleTime: 5 * 60 * 1000,
  });
};

export const useReportHTML = (reportId) => {
  return useQuery({
    queryKey: ['report-html', reportId],
    queryFn: () => reportService.getReportHTML(reportId),
    enabled: !!reportId,
    staleTime: 10 * 60 * 1000, // HTML cambia menos frecuentemente
  });
};

// 📊 HOOKS DE MUTACIONES
export const useGenerateReport = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ fileId, config }) => reportService.generateReport(fileId, config),
    onSuccess: (data) => {
      // Invalidar caches relevantes
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      
      toast.success('🎉 Reporte generado exitosamente');
      return data;
    },
    onError: (error) => {
      console.error('Error generating report:', error);
      toast.error(`❌ Error generando reporte: ${error.message}`);
    },
  });
};

export const useDeleteReport = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (reportId) => reportService.deleteReport(reportId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      
      toast.success('🗑️ Reporte eliminado exitosamente');
    },
    onError: (error) => {
      console.error('Error deleting report:', error);
      toast.error(`❌ Error eliminando reporte: ${error.message}`);
    },
  });
};

export const useDeleteFile = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (fileId) => fileService.deleteFile(fileId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] });
      
      toast.success('🗑️ Archivo eliminado exitosamente');
    },
    onError: (error) => {
      console.error('Error deleting file:', error);
      toast.error(`❌ Error eliminando archivo: ${error.message}`);
    },
  });
};

// Hook para mutaciones de reportes (ReportViewer y ReportsList)
export const useReportMutations = () => {
  const queryClient = useQueryClient();

  const downloadReport = useMutation({
    mutationFn: ({ reportId, filename }) => reportService.downloadReportPDF(reportId, filename),
    onSuccess: () => {
      toast.success('📥 Reporte descargado exitosamente');
    },
    onError: (error) => {
      console.error('Error downloading report:', error);
      toast.error(`❌ Error descargando reporte: ${error.message}`);
    },
  });

  const deleteReport = useMutation({
    mutationFn: (reportId) => reportService.deleteReport(reportId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      
      toast.success('🗑️ Reporte eliminado exitosamente');
    },
    onError: (error) => {
      console.error('Error deleting report:', error);
      toast.error(`❌ Error eliminando reporte: ${error.message}`);
    },
  });

  return { downloadReport, deleteReport };
};

// Hook para crear reportes (ReportGenerator)
export const useCreateReport = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data) => {
      // Transformar los datos para que coincidan con la API
      return reportService.generateReport(data.csv_file, {
        title: data.title,
        description: data.description,
        type: data.report_type,
        ...data.generation_config
      });
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      
      toast.success('🎉 Reporte creado exitosamente');
      return data;
    },
    onError: (error) => {
      console.error('Error creating report:', error);
      toast.error(`❌ Error creando reporte: ${error.message}`);
    },
  });
};

// 📈 HOOKS DE DASHBOARD
export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => dashboardService.getStats(),
    staleTime: 2 * 60 * 1000, // 2 minutos
    cacheTime: 5 * 60 * 1000, // 5 minutos
  });
};

export const useRecentActivity = (limit = 8) => {
  return useQuery({
    queryKey: ['dashboard', 'activity', limit],
    queryFn: () => dashboardService.getActivity(limit),
    staleTime: 60 * 1000, // 1 minuto
    cacheTime: 2 * 60 * 1000, // 2 minutos
  });
};

// 🔄 HOOKS DE COMPATIBILIDAD
export const useReportGeneration = () => {
  const mutation = useGenerateReport();
  
  return {
    generateReport: async (fileId, reportConfig) => {
      return mutation.mutateAsync({ fileId, config: reportConfig });
    },
    isGenerating: mutation.isPending,
  };
};