// frontend/src/services/api.js - VERSIÓN COMPLETAMENTE CORREGIDA

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Función para obtener el token de autenticación
const getAuthToken = () => {
  return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
};

// Función para hacer requests con autenticación
const fetchWithAuth = async (url, options = {}) => {
  const token = getAuthToken();
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }
  
  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(url, config);
    
    // Si el token expiró, intentar refrescar
    if (response.status === 401) {
      console.warn('Token expirado, intentando refrescar...');
      // Aquí podrías implementar refresh token logic
      throw new Error('Token de autenticación expirado');
    }
    
    return response;
  } catch (error) {
    console.error('Error en request:', error);
    throw error;
  }
};

// Servicio de API corregido
export const apiService = {
  // REPORTES - ENDPOINTS CORREGIDOS
  async createReport(reportData) {
    console.log('Creando reporte con datos:', reportData);
    
    const response = await fetchWithAuth(`${API_BASE_URL}/reports/`, {
      method: 'POST',
      body: JSON.stringify({
        title: reportData.title,
        description: reportData.description || '',
        report_type: reportData.type || reportData.report_type,
        csv_file: reportData.csvFileId || reportData.csv_file,
        configuration: reportData.configuration || {
          include_graphics: reportData.includeGraphics || true,
          include_detailed_tables: reportData.includeDetailedTables || true,
          include_recommendations: reportData.includeRecommendations || true
        }
      })
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || error.detail || `HTTP ${response.status}: Error creando reporte`);
    }
    
    return await response.json();
  },
  
  async getReports(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = `${API_BASE_URL}/reports/${queryString ? '?' + queryString : ''}`;
    
    const response = await fetchWithAuth(url);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Error obteniendo reportes`);
    }
    
    const data = await response.json();
    return data.results || data || [];
  },
  
  async getReport(reportId) {
    const response = await fetchWithAuth(`${API_BASE_URL}/reports/${reportId}/`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Error obteniendo reporte`);
    }
    
    return await response.json();
  },
  
  async getReportStatus(reportId) {
    const response = await fetchWithAuth(`${API_BASE_URL}/reports/${reportId}/status/`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Error obteniendo estado del reporte`);
    }
    
    return await response.json();
  },
  
  async getReportHTML(reportId) {
    const response = await fetchWithAuth(`${API_BASE_URL}/reports/${reportId}/html/`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Error obteniendo HTML del reporte`);
    }
    
    return await response.json();
  },
  
  // ARCHIVOS - ENDPOINTS CORREGIDOS
  async uploadFile(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', 'csv');
    formData.append('original_filename', file.name);
    
    const token = getAuthToken();
    
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable && onProgress) {
          const percentComplete = (event.loaded / event.total) * 100;
          onProgress(Math.round(percentComplete));
        }
      };
      
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const result = JSON.parse(xhr.responseText);
            resolve(result);
          } catch (error) {
            reject(new Error('Error parseando respuesta del servidor'));
          }
        } else {
          try {
            const error = JSON.parse(xhr.responseText);
            reject(new Error(error.error || error.detail || `HTTP ${xhr.status}: Error subiendo archivo`));
          } catch {
            reject(new Error(`HTTP ${xhr.status}: Error subiendo archivo`));
          }
        }
      };
      
      xhr.onerror = () => {
        reject(new Error('Error de red subiendo archivo'));
      };
      
      xhr.open('POST', `${API_BASE_URL}/files/upload/`);
      
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }
      
      xhr.send(formData);
    });
  },
  
  async getFiles(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = `${API_BASE_URL}/files/${queryString ? '?' + queryString : ''}`;
    
    const response = await fetchWithAuth(url);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Error obteniendo archivos`);
    }
    
    const data = await response.json();
    return data.results || data || [];
  },
  
  // DASHBOARD
  async getDashboardStats() {
    const response = await fetchWithAuth(`${API_BASE_URL}/dashboard/stats/`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Error obteniendo estadísticas`);
    }
    
    return await response.json();
  },
  
  // AUTENTICACIÓN
  async getCurrentUser() {
    const response = await fetchWithAuth(`${API_BASE_URL}/auth/users/profile/`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Error obteniendo perfil de usuario`);
    }
    
    return await response.json();
  }
};

// Exportar función helper
export { fetchWithAuth, getAuthToken };
export default apiService;