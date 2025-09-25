// src/utils/formatters.js
import { Shield, AlertTriangle, CheckCircle, Clock, XCircle, FileText } from 'lucide-react';

/**
 * Obtiene el color para diferentes estados de reportes
 */
export const getStatusColor = (status) => {
  const statusColors = {
    completed: 'text-green-600 bg-green-100',
    processing: 'text-yellow-600 bg-yellow-100',
    pending: 'text-blue-600 bg-blue-100',
    failed: 'text-red-600 bg-red-100',
    draft: 'text-gray-600 bg-gray-100',
    preview: 'text-purple-600 bg-purple-100'
  };
  
  return statusColors[status] || 'text-gray-600 bg-gray-100';
};

/**
 * Obtiene el icono para diferentes estados
 */
export const getStatusIcon = (status) => {
  const statusIcons = {
    completed: CheckCircle,
    processing: Clock,
    pending: Clock,
    failed: XCircle,
    draft: FileText,
    preview: FileText
  };
  
  return statusIcons[status] || FileText;
};

/**
 * Traduce estados al español
 */
export const getStatusText = (status) => {
  const statusTexts = {
    completed: 'Completado',
    processing: 'Procesando',
    pending: 'Pendiente',
    failed: 'Error',
    draft: 'Borrador',
    preview: 'Vista previa'
  };
  
  return statusTexts[status] || 'Desconocido';
};

/**
 * Obtiene color y configuración para diferentes niveles de riesgo
 */
export const getRiskLevel = (level) => {
  const riskLevels = {
    high: {
      color: 'text-red-600 bg-red-100',
      bgClass: 'bg-red-50 border-red-200',
      textClass: 'text-red-800',
      icon: AlertTriangle,
      label: 'Alto'
    },
    medium: {
      color: 'text-yellow-600 bg-yellow-100',
      bgClass: 'bg-yellow-50 border-yellow-200',
      textClass: 'text-yellow-800',
      icon: AlertTriangle,
      label: 'Medio'
    },
    low: {
      color: 'text-green-600 bg-green-100',
      bgClass: 'bg-green-50 border-green-200',
      textClass: 'text-green-800',
      icon: CheckCircle,
      label: 'Bajo'
    }
  };
  
  return riskLevels[level?.toLowerCase()] || riskLevels.medium;
};

/**
 * Obtiene configuración para categorías de Azure Advisor
 */
export const getCategoryConfig = (category) => {
  const categories = {
    security: {
      color: 'text-red-600 bg-red-100',
      bgClass: 'bg-red-50 border-red-200',
      icon: Shield,
      label: 'Seguridad',
      description: 'Recomendaciones de seguridad'
    },
    cost: {
      color: 'text-green-600 bg-green-100',
      bgClass: 'bg-green-50 border-green-200',
      icon: '💰',
      label: 'Costo',
      description: 'Optimización de costos'
    },
    reliability: {
      color: 'text-blue-600 bg-blue-100',
      bgClass: 'bg-blue-50 border-blue-200',
      icon: '🔧',
      label: 'Confiabilidad',
      description: 'Mejoras de confiabilidad'
    },
    performance: {
      color: 'text-purple-600 bg-purple-100',
      bgClass: 'bg-purple-50 border-purple-200',
      icon: '⚡',
      label: 'Rendimiento',
      description: 'Optimización de rendimiento'
    },
    'operational excellence': {
      color: 'text-indigo-600 bg-indigo-100',
      bgClass: 'bg-indigo-50 border-indigo-200',
      icon: '🎯',
      label: 'Excelencia Operacional',
      description: 'Mejores prácticas operacionales'
    }
  };
  
  return categories[category?.toLowerCase()] || {
    color: 'text-gray-600 bg-gray-100',
    bgClass: 'bg-gray-50 border-gray-200',
    icon: '📊',
    label: category || 'General',
    description: 'Recomendación general'
  };
};

/**
 * Formatea el impacto de negocio
 */
export const formatBusinessImpact = (impact) => {
  const impacts = {
    high: { label: 'Alto', color: 'text-red-600' },
    medium: { label: 'Medio', color: 'text-yellow-600' },
    low: { label: 'Bajo', color: 'text-green-600' }
  };
  
  return impacts[impact?.toLowerCase()] || { label: impact || 'Sin definir', color: 'text-gray-600' };
};

/**
 * Formatea tipos de recursos de Azure
 */
export const formatResourceType = (resourceType) => {
  const resourceTypes = {
    'virtual machine': 'Máquina Virtual',
    'virtual machines': 'Máquinas Virtuales',
    'app service': 'App Service',
    'storage account': 'Cuenta de Almacenamiento',
    'sql database': 'Base de Datos SQL',
    'api management': 'API Management',
    'subscription': 'Suscripción',
    'resource group': 'Grupo de Recursos'
  };
  
  return resourceTypes[resourceType?.toLowerCase()] || resourceType || 'Recurso';
};

/**
 * Formatea puntuación de Azure Advisor (0-100)
 */
export const formatAdvisorScore = (score) => {
  if (score >= 80) {
    return {
      score,
      level: 'Excelente',
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      description: 'Tu infraestructura sigue las mejores prácticas'
    };
  } else if (score >= 60) {
    return {
      score,
      level: 'Bueno',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      description: 'Hay algunas oportunidades de mejora'
    };
  } else if (score >= 40) {
    return {
      score,
      level: 'Regular',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
      description: 'Se recomienda implementar varias mejoras'
    };
  } else {
    return {
      score,
      level: 'Crítico',
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      description: 'Requiere atención inmediata'
    };
  }
};

/**
 * Formatea el progreso de implementación
 */
export const formatImplementationProgress = (implemented, total) => {
  const percentage = total > 0 ? Math.round((implemented / total) * 100) : 0;
  
  return {
    percentage,
    implemented,
    total,
    remaining: total - implemented,
    label: `${implemented} de ${total} implementadas (${percentage}%)`
  };
};

/**
 * Formatea tiempo estimado de implementación
 */
export const formatEstimatedTime = (hours) => {
  if (hours < 1) {
    return 'Menos de 1 hora';
  } else if (hours < 8) {
    return `${hours} horas`;
  } else if (hours < 40) {
    const days = Math.ceil(hours / 8);
    return `${days} día${days > 1 ? 's' : ''} laborales`;
  } else {
    const weeks = Math.ceil(hours / 40);
    return `${weeks} semana${weeks > 1 ? 's' : ''}`;
  }
};

/**
 * Formatea el ahorro estimado mensual
 */
export const formatMonthlySavings = (amount) => {
  if (amount < 100) {
    return {
      amount: Math.round(amount),
      formatted: `$${Math.round(amount)}`,
      impact: 'Bajo',
      color: 'text-green-600'
    };
  } else if (amount < 1000) {
    return {
      amount: Math.round(amount),
      formatted: `$${Math.round(amount)}`,
      impact: 'Medio',
      color: 'text-blue-600'
    };
  } else {
    return {
      amount: Math.round(amount),
      formatted: `$${Math.round(amount).toLocaleString()}`,
      impact: 'Alto',
      color: 'text-purple-600'
    };
  }
};

/**
 * Obtiene prioridad basada en impacto y esfuerzo
 */
export const calculatePriority = (businessImpact, effort) => {
  const impactScore = { high: 3, medium: 2, low: 1 }[businessImpact?.toLowerCase()] || 1;
  const effortScore = { low: 3, medium: 2, high: 1 }[effort?.toLowerCase()] || 2;
  
  const priority = impactScore + effortScore;
  
  if (priority >= 5) {
    return {
      level: 'high',
      label: 'Alta',
      color: 'text-red-600 bg-red-100',
      description: 'Implementar inmediatamente'
    };
  } else if (priority >= 4) {
    return {
      level: 'medium',
      label: 'Media',
      color: 'text-yellow-600 bg-yellow-100',
      description: 'Implementar en 1-2 semanas'
    };
  } else {
    return {
      level: 'low',
      label: 'Baja',
      color: 'text-green-600 bg-green-100',
      description: 'Implementar cuando sea posible'
    };
  }
};

/**
 * Formatea fechas para la interfaz de usuario
 */
export const formatDisplayDate = (date, options = {}) => {
  if (!date) return '';
  
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options
  };
  
  try {
    return new Date(date).toLocaleDateString('es-ES', defaultOptions);
  } catch (_err) {
    return '';
  }
};

/**
 * Formatea nombres de archivos para mostrar
 */
export const formatFileName = (fileName, maxLength = 30) => {
  if (!fileName) return '';
  
  if (fileName.length <= maxLength) return fileName;
  
  const extension = fileName.split('.').pop();
  const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'));
  const truncatedName = nameWithoutExt.substring(0, maxLength - extension.length - 4);
  
  return `${truncatedName}...${extension}`;
};

/**
 * Formatea tipo de reporte
 */
export const formatReportType = (type) => {
  const types = {
    'azure_advisor': 'Azure Advisor',
    'security': 'Seguridad',
    'cost': 'Costos',
    'performance': 'Rendimiento',
    'reliability': 'Confiabilidad'
  };
  
  return types[type] || type || 'General';
};

/**
 * Formatea fechas de manera relativa (hace X tiempo) - duplicado de helpers para compatibilidad
 */
export const formatRelativeTime = (date) => {
  if (!date) return '';
  
  try {
    const now = new Date();
    const targetDate = new Date(date);
    const diffMs = now - targetDate;
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSeconds < 60) {
      return 'Hace unos segundos';
    } else if (diffMinutes < 60) {
      return `Hace ${diffMinutes} minuto${diffMinutes !== 1 ? 's' : ''}`;
    } else if (diffHours < 24) {
      return `Hace ${diffHours} hora${diffHours !== 1 ? 's' : ''}`;
    } else if (diffDays < 7) {
      return `Hace ${diffDays} día${diffDays !== 1 ? 's' : ''}`;
    } else {
      return targetDate.toLocaleDateString('es-ES');
    }
  } catch (_err) {
    return '';
  }
};