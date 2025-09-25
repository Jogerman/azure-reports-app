// frontend/src/hooks/useRealData.js - HOOK PARA DATOS REALES
import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchWithAuth, buildApiUrl } from '../config/api';
import toast from 'react-hot-toast';

// Servicio para obtener análisis real
const realDataService = {
  async getDashboardStats() {
    try {
      const response = await fetchWithAuth(buildApiUrl('/analytics/stats/'));
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Error obteniendo estadísticas reales`);
      }
      
      const data = await response.json();
      console.log('📊 Estadísticas reales cargadas:', data);
      return data;
    } catch (error) {
      console.error('❌ Error cargando estadísticas reales:', error);
      throw error;
    }
  },

  async getRealActivity(limit = 8) {
    try {
      const response = await fetchWithAuth(buildApiUrl(`/analytics/activity/?limit=${limit}`));
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Error obteniendo actividad real`);
      }
      
      const data = await response.json();
      console.log('📋 Actividad real cargada:', data);
      return data?.results || data || [];
    } catch (error) {
      console.error('❌ Error cargando actividad real:', error);
      throw error;
    }
  },

  async getCSVAnalysis(csvId = null) {
    try {
      const url = csvId 
        ? buildApiUrl(`/analytics/csv_analysis/?csv_id=${csvId}`)
        : buildApiUrl('/analytics/csv_analysis/');
        
      const response = await fetchWithAuth(url);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Error obteniendo análisis CSV`);
      }
      
      const data = await response.json();
      console.log('📈 Análisis CSV cargado:', data);
      return data;
    } catch (error) {
      console.error('❌ Error cargando análisis CSV:', error);
      throw error;
    }
  }
};

// Hook principal para estadísticas reales del dashboard
export const useRealDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboard', 'real-stats'],
    queryFn: () => realDataService.getDashboardStats(),
    staleTime: 2 * 60 * 1000, // 2 minutos
    cacheTime: 5 * 60 * 1000, // 5 minutos
    retry: 3,
    retryDelay: 1000
  });
};

// Hook para actividad real
export const useRealActivity = (limit = 8) => {
  return useQuery({
    queryKey: ['dashboard', 'real-activity', limit],
    queryFn: () => realDataService.getRealActivity(limit),
    staleTime: 60 * 1000, // 1 minuto
    cacheTime: 2 * 60 * 1000, // 2 minutos
  });
};

// Hook para análisis CSV específico
export const useCSVAnalysis = (csvId = null) => {
  return useQuery({
    queryKey: ['csv-analysis', csvId],
    queryFn: () => realDataService.getCSVAnalysis(csvId),
    enabled: true, // Siempre habilitado, buscará el CSV más reciente si no se especifica ID
    staleTime: 5 * 60 * 1000, // 5 minutos
    cacheTime: 10 * 60 * 1000, // 10 minutos
  });
};

// Hook para detectar si hay datos reales disponibles
export const useHasRealData = () => {
  const { data: stats } = useRealDashboardStats();
  
  return {
    hasRealData: stats?.data_source === 'real_csv_analysis',
    dataSource: stats?.data_source,
    lastAnalysisDate: stats?.last_analysis_date,
    csvFilename: stats?.csv_filename,
    qualityScore: stats?.analysis_quality_score
  };
};
