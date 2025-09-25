// frontend/src/services/reportsService.js

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class ReportsService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Helper para obtener headers con autenticación
  getHeaders(contentType = 'application/json') {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': contentType,
      ...(token && { Authorization: `Bearer ${token}` })
    };
  }

  // Helper para manejar errores de API
  async handleResponse(response) {
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP error! status: ${response.status}`);
    }
    return response.json();
  }

  // ========== MÉTODOS DE REPORTES ==========

  // Obtener lista de reportes
  async getReports(params = {}) {
    const queryString = new URLSearchParams({
      page: params.page || 1,
      page_size: params.pageSize || 20,
      ...params.filters
    }).toString();

    const response = await fetch(`${this.baseURL}/reports/?${queryString}`, {
      method: 'GET',
      headers: this.getHeaders()
    });

    return this.handleResponse(response);
  }

  // Obtener reporte específico
  async getReport(reportId) {
    const response = await fetch(`${this.baseURL}/reports/${reportId}/`, {
      method: 'GET',
      headers: this.getHeaders()
    });

    return this.handleResponse(response);
  }

  // Crear nuevo reporte especializado
  async createReport(reportData) {
    const response = await fetch(`${this.baseURL}/reports/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        title: reportData.title,
        description: reportData.description,
        report_type: reportData.type, // 'security', 'performance', 'cost', 'comprehensive'
        csv_file: reportData.csvFileId,
        configuration: {
          include_graphics: reportData.includeGraphics,
          include_detailed_tables: reportData.includeDetailedTables,
          include_recommendations: reportData.includeRecommendations
        }
      })
    });

    return this.handleResponse(response);
  }

  // Obtener estado de un reporte (para polling)
  async getReportStatus(reportId) {
    const response = await fetch(`${this.baseURL}/reports/${reportId}/status/`, {
      method: 'GET',
      headers: this.getHeaders()
    });

    return this.handleResponse(response);
  }

  // Obtener HTML del reporte
  async getReportHTML(reportId) {
    const response = await fetch(`${this.baseURL}/reports/${reportId}/html/`, {
      method: 'GET',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error(`Error fetching report HTML: ${response.status}`);
    }

    return response.text(); // Return raw HTML
  }

  // Obtener URL de descarga del PDF
  getReportPDFUrl(reportId) {
    return `${this.baseURL}/reports/${reportId}/pdf/`;
  }

  // Eliminar reporte
  async deleteReport(reportId) {
    const response = await fetch(`${this.baseURL}/reports/${reportId}/`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error(`Error deleting report: ${response.status}`);
    }

    return true;
  }

  // ========== MÉTODOS DE ANÁLISIS ESPECIALIZADOS ==========

  // Validar CSV para análisis especializado
  async validateCSVForSpecializedAnalysis(csvFileId, reportType) {
    const response = await fetch(`${this.baseURL}/reports/validate-csv/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        csv_file_id: csvFileId,
        report_type: reportType
      })
    });

    return this.handleResponse(response);
  }

  // Obtener métricas de análisis por tipo
  async getAnalysisMetrics(reportId, analysisType) {
    const response = await fetch(`${this.baseURL}/reports/${reportId}/analysis/${analysisType}/`, {
      method: 'GET',
      headers: this.getHeaders()
    });

    return this.handleResponse(response);
  }

  // ========== MÉTODOS DE ARCHIVOS CSV ==========

  // Subir archivo CSV con progreso
  async uploadCSVFile(file, onProgress = null) {
    return new Promise((resolve, reject) => {
      const formData = new FormData();
      formData.append('file', file);

      const xhr = new XMLHttpRequest();

      // Configurar progreso de subida
      if (onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = (event.loaded / event.total) * 100;
            onProgress(Math.round(progress));
          }
        });
      }

      // Configurar manejo de respuesta
      xhr.addEventListener('load', async () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid response format'));
          }
        } else {
          try {
            const error = JSON.parse(xhr.responseText);
            reject(new Error(error.message || `Upload failed with status ${xhr.status}`));
          } catch {
            reject(new Error(`Upload failed with status ${xhr.status}`));
          }
        }
      });

      // Configurar manejo de errores
      xhr.addEventListener('error', () => {
        reject(new Error('Network error during upload'));
      });

      // Configurar timeout
      xhr.timeout = 300000; // 5 minutos
      xhr.addEventListener('timeout', () => {
        reject(new Error('Upload timeout'));
      });

      // Enviar request
      xhr.open('POST', `${this.baseURL}/storage/files/`);
      
      const token = localStorage.getItem('token');
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }

      xhr.send(formData);
    });
  }

  // Obtener archivos CSV del usuario
  async getUserCSVFiles() {
    const response = await fetch(`${this.baseURL}/storage/files/`, {
      method: 'GET',
      headers: this.getHeaders()
    });

    return this.handleResponse(response);
  }

  // Obtener análisis de un archivo CSV específico
  async getCSVFileAnalysis(csvFileId) {
    const response = await fetch(`${this.baseURL}/storage/files/${csvFileId}/analysis/`, {
      method: 'GET',
      headers: this.getHeaders()
    });

    return this.handleResponse(response);
  }

  // ========== MÉTODOS DE DASHBOARD ==========

  // Obtener estadísticas del dashboard
  async getDashboardStats() {
    const response = await fetch(`${this.baseURL}/analytics/stats/`, {
      method: 'GET',
      headers: this.getHeaders()
    });

    return this.handleResponse(response);
  }

  // Obtener actividad reciente
  async getRecentActivity(limit = 10) {
    const response = await fetch(`${this.baseURL}/analytics/activity/?limit=${limit}`, {
      method: 'GET',
      headers: this.getHeaders()
    });

    return this.handleResponse(response);
  }

  // ========== MÉTODOS HELPER ==========

  // Polling helper para verificar estado de reportes
  async pollReportStatus(reportId, onStatusUpdate = null, maxAttempts = 60) {
    let attempts = 0;
    
    return new Promise((resolve, reject) => {
      const checkStatus = async () => {
        try {
          const report = await this.getReport(reportId);
          
          if (onStatusUpdate) {
            onStatusUpdate(report);
          }

          if (report.status === 'completed') {
            resolve(report);
          } else if (report.status === 'failed') {
            reject(new Error(report.error_message || 'Report generation failed'));
          } else if (attempts >= maxAttempts) {
            reject(new Error('Polling timeout - report generation took too long'));
          } else {
            attempts++;
            setTimeout(checkStatus, 5000); // Check every 5 seconds
          }
        } catch (error) {
          reject(error);
        }
      };

      // Start polling after 3 seconds
      setTimeout(checkStatus, 3000);
    });
  }

  // Obtener configuración de tipos de reporte
  getReportTypeConfig() {
    return {
      comprehensive: {
        label: 'Análisis Completo',
        description: 'Análisis integral de todas las métricas de Azure Advisor',
        estimatedTime: '3-5 minutos',
        features: [
          'Todas las categorías incluidas',
          'Métricas detalladas',
          'Recomendaciones completas',
          'Visualizaciones avanzadas'
        ]
      },
      security: {
        label: 'Análisis de Seguridad',
        description: 'Enfoque especializado en seguridad y cumplimiento',
        estimatedTime: '2-3 minutos',
        features: [
          'Análisis de vulnerabilidades',
          'Gaps de cumplimiento',
          'Score de seguridad',
          'Recomendaciones priorizadas'
        ]
      },
      performance: {
        label: 'Análisis de Rendimiento',
        description: 'Optimización de performance y detección de cuellos de botella',
        estimatedTime: '2-3 minutos',
        features: [
          'Identificación de bottlenecks',
          'Oportunidades de optimización',
          'Score de rendimiento',
          'Métricas de eficiencia'
        ]
      },
      cost: {
        label: 'Análisis de Costos',
        description: 'Optimización financiera y cálculo de ROI',
        estimatedTime: '2-3 minutos',
        features: [
          'Análisis de ahorros potenciales',
          'Cálculo de ROI',
          'Instancias reservadas',
          'Recursos subutilizados'
        ]
      }
    };
  }

  // Validar configuración de reporte
  validateReportConfig(config) {
    const errors = [];

    if (!config.title || config.title.trim().length < 3) {
      errors.push('El título debe tener al menos 3 caracteres');
    }

    if (!config.type || !['comprehensive', 'security', 'performance', 'cost'].includes(config.type)) {
      errors.push('Tipo de reporte inválido');
    }

    if (!config.csvFileId) {
      errors.push('Debe seleccionar un archivo CSV');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Formatear datos de análisis para visualización
  formatAnalysisData(analysisData, reportType) {
    if (!analysisData || typeof analysisData !== 'object') {
      return null;
    }

    const formatted = {
      reportType,
      generatedAt: new Date().toISOString(),
      ...analysisData
    };

    // Asegurar que existan las métricas del dashboard
    if (!formatted.dashboard_metrics) {
      formatted.dashboard_metrics = this.extractDashboardMetrics(analysisData, reportType);
    }

    return formatted;
  }

  // Extraer métricas del dashboard desde datos de análisis
  extractDashboardMetrics(analysisData, reportType) {
    const basic = analysisData.basic_metrics || {};
    
    switch (reportType) {
      case 'security':
        return {
          total_actions: basic.total_security_actions || 0,
          critical_issues: basic.high_impact_actions || 0,
          security_score: analysisData.security_score || 0,
          working_hours: basic.estimated_working_hours || 0,
          risk_level: basic.risk_level || 'Unknown'
        };
        
      case 'performance':
        return {
          total_actions: basic.total_performance_actions || 0,
          critical_optimizations: basic.high_impact_optimizations || 0,
          performance_score: analysisData.performance_score || 100,
          optimization_potential: basic.estimated_performance_improvement || 0,
          working_hours: basic.estimated_working_hours || 0
        };
        
      case 'cost':
        return {
          total_actions: basic.total_cost_actions || 0,
          monthly_savings: basic.estimated_monthly_savings || 0,
          annual_savings: basic.estimated_annual_savings || 0,
          working_hours: basic.estimated_working_hours || 0,
          optimization_score: analysisData.optimization_score || 100
        };
        
      default:
        return {
          total_actions: basic.total_actions || 0,
          working_hours: basic.estimated_working_hours || 0
        };
    }
  }
}

// Instancia singleton del servicio
const reportsService = new ReportsService();

export default reportsService;
