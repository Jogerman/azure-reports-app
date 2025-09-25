// frontend/src/hooks/useSafeQuery.js
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';

// Hook que solo ejecuta queries cuando la autenticación está lista
export const useSafeQuery = (queryKey, queryFn, options = {}) => {
  const { isAuthenticated, isInitialized } = useAuth();
  
  return useQuery({
    queryKey,
    queryFn,
    enabled: isAuthenticated && isInitialized && (options.enabled !== false),
    retry: false, // No retry automático para evitar spam de peticiones sin token
    ...options
  });
};

// Hooks específicos para dashboard que usan useSafeQuery
export const useSafeDashboardStats = () => {
  return useSafeQuery(
    ['dashboard-stats'],
    async () => {
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('No token available');
      
      const response = await fetch('/api/dashboard/stats/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Error obteniendo estadísticas');
      }
      
      return response.json();
    },
    {
      staleTime: 60000, // 1 minuto
      onError: (error) => {
        console.error('Error en dashboard stats:', error);
      }
    }
  );
};

export const useSafeRecentReports = (limit = 5) => {
  return useSafeQuery(
    ['recent-reports', limit],
    async () => {
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('No token available');
      
      const response = await fetch(`/api/reports/?limit=${limit}&ordering=-created_at`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Token expirado');
        }
        throw new Error('Error obteniendo reportes');
      }
      
      const data = await response.json();
      return data.results || data || [];
    },
    {
      staleTime: 30000, // 30 segundos
      onError: (error) => {
        console.error('Error en recent reports:', error);
      }
    }
  );
};

export const useSafeRecentActivity = (limit = 8) => {
  return useSafeQuery(
    ['recent-activity', limit],
    async () => {
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('No token available');
      
      const response = await fetch(`/api/dashboard/activity/?limit=${limit}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        // Si el endpoint no existe, devolver datos mock
        if (response.status === 404) {
          return [];
        }
        throw new Error('Error obteniendo actividad');
      }
      
      const data = await response.json();
      return data.results || data || [];
    },
    {
      staleTime: 30000,
      onError: (error) => {
        console.error('Error en recent activity:', error);
      }
    }
  );
};