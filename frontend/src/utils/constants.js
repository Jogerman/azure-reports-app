// src/utils/constants.js

// Estados de reportes
export const REPORT_STATUS = {
  DRAFT: 'draft',
  PENDING: 'pending',
  PROCESSING: 'processing',
  GENERATING: 'generating',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled'
};

// Tipos de reportes
export const REPORT_TYPES = {
  SECURITY: 'security',
  COST: 'cost',
  PERFORMANCE: 'performance',
  RELIABILITY: 'reliability',
  OPERATIONAL_EXCELLENCE: 'operational_excellence',
  COMPREHENSIVE: 'comprehensive'
};

// Estados de archivos
export const FILE_STATUS = {
  UPLOADING: 'uploading',
  UPLOADED: 'uploaded',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CORRUPTED: 'corrupted'
};

// Tipos de archivo soportados
export const SUPPORTED_FILE_TYPES = {
  CSV: '.csv',
  EXCEL: '.xlsx,.xls',
  PDF: '.pdf'
};

// Límites de archivo
export const FILE_LIMITS = {
  MAX_SIZE: 50 * 1024 * 1024, // 50MB
  MAX_FILES: 10,
  ALLOWED_EXTENSIONS: ['.csv']
};

// Categorías de Azure Advisor
export const AZURE_CATEGORIES = {
  SECURITY: 'Security',
  COST: 'Cost',
  RELIABILITY: 'Reliability',
  PERFORMANCE: 'Performance',
  OPERATIONAL_EXCELLENCE: 'Operational excellence'
};

// Niveles de riesgo
export const RISK_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
};

// Impacto de negocio
export const BUSINESS_IMPACT = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high'
};

// Tipos de notificación
export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

// Configuración de paginación
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100]
};

// Configuración de filtros
export const FILTER_OPTIONS = {
  DATE_RANGES: [
    { value: 'today', label: 'Hoy' },
    { value: 'week', label: 'Esta semana' },
    { value: 'month', label: 'Este mes' },
    { value: 'quarter', label: 'Este trimestre' },
    { value: 'year', label: 'Este año' },
    { value: 'custom', label: 'Personalizado' }
  ],
  SORT_OPTIONS: [
    { value: 'created_at', label: 'Fecha de creación' },
    { value: 'name', label: 'Nombre' },
    { value: 'size', label: 'Tamaño' },
    { value: 'status', label: 'Estado' }
  ],
  SORT_DIRECTIONS: [
    { value: 'asc', label: 'Ascendente' },
    { value: 'desc', label: 'Descendente' }
  ]
};

// Configuración de API
export const API_CONFIG = {
  TIMEOUT: 30000, // 30 segundos
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000 // 1 segundo
};

// Rutas de la aplicación
export const ROUTES = {
  HOME: '/',
  DASHBOARD: '/app',
  REPORTS: '/app/reports',
  HISTORY: '/app/history',
  STORAGE: '/app/storage',
  SETTINGS: '/app/settings',
  PROFILE: '/app/profile'
};

// Mensajes de error comunes
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Error de conexión. Verifica tu internet.',
  UNAUTHORIZED: 'No tienes permisos para realizar esta acción.',
  NOT_FOUND: 'El recurso solicitado no fue encontrado.',
  SERVER_ERROR: 'Error interno del servidor. Intenta más tarde.',
  FILE_TOO_LARGE: 'El archivo es demasiado grande.',
  INVALID_FILE_TYPE: 'Tipo de archivo no soportado.',
  UPLOAD_FAILED: 'Error al subir el archivo.',
  PROCESSING_FAILED: 'Error al procesar el archivo.'
};

// Mensajes de éxito
export const SUCCESS_MESSAGES = {
  FILE_UPLOADED: 'Archivo subido exitosamente.',
  REPORT_GENERATED: 'Reporte generado exitosamente.',
  DATA_SAVED: 'Datos guardados correctamente.',
  EMAIL_SENT: 'Email enviado exitosamente.',
  PROFILE_UPDATED: 'Perfil actualizado correctamente.'
};

// Configuración de colores para gráficos
export const CHART_COLORS = {
  PRIMARY: '#3B82F6',
  SECONDARY: '#8B5CF6',
  SUCCESS: '#10B981',
  WARNING: '#F59E0B',
  DANGER: '#EF4444',
  INFO: '#06B6D4',
  GRAY: '#6B7280'
};

// Configuración de temas
export const THEME_CONFIG = {
  COLORS: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      900: '#1e3a8a'
    },
    secondary: {
      50: '#f5f3ff',
      100: '#ede9fe',
      500: '#8b5cf6',
      600: '#7c3aed',
      700: '#6d28d9',
      900: '#4c1d95'
    }
  }
};

// Configuración de animaciones
export const ANIMATION_CONFIG = {
  DURATIONS: {
    FAST: 150,
    NORMAL: 300,
    SLOW: 500
  },
  EASINGS: {
    EASE_IN: 'cubic-bezier(0.4, 0, 1, 1)',
    EASE_OUT: 'cubic-bezier(0, 0, 0.2, 1)',
    EASE_IN_OUT: 'cubic-bezier(0.4, 0, 0.2, 1)'
  }
};

// Configuración de almacenamiento local
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  THEME: 'theme',
  LANGUAGE: 'language',
  SETTINGS: 'app_settings'
};

// Configuración de idiomas
export const LANGUAGES = {
  ES: 'es',
  EN: 'en'
};

// Configuración de exportación
export const EXPORT_FORMATS = {
  PDF: 'pdf',
  EXCEL: 'xlsx',
  CSV: 'csv',
  JSON: 'json'
};

// Tipos de análisis disponibles
export const ANALYSIS_TYPES = {
  SECURITY_ANALYSIS: 'security_analysis',
  COST_OPTIMIZATION: 'cost_optimization',
  PERFORMANCE_REVIEW: 'performance_review',
  RELIABILITY_CHECK: 'reliability_check',
  COMPLIANCE_AUDIT: 'compliance_audit'
};

// Configuración de métricas
export const METRICS = {
  CURRENCY_FORMAT: 'USD',
  DATE_FORMAT: 'DD/MM/YYYY',
  TIME_FORMAT: 'HH:mm:ss',
  DECIMAL_PLACES: 2
};

export default {
  REPORT_STATUS,
  REPORT_TYPES,
  FILE_STATUS,
  SUPPORTED_FILE_TYPES,
  FILE_LIMITS,
  AZURE_CATEGORIES,
  RISK_LEVELS,
  BUSINESS_IMPACT,
  NOTIFICATION_TYPES,
  PAGINATION,
  FILTER_OPTIONS,
  API_CONFIG,
  ROUTES,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  CHART_COLORS,
  THEME_CONFIG,
  ANIMATION_CONFIG,
  STORAGE_KEYS,
  LANGUAGES,
  EXPORT_FORMATS,
  ANALYSIS_TYPES,
  METRICS
};