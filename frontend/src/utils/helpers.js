// src/utils/helpers.js

/**
 * Formatea números grandes con separadores de miles
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined) return '0';
  return new Intl.NumberFormat('es-ES').format(num);
};

/**
 * Formatea moneda en formato USD
 */
export const formatCurrency = (amount, currency = 'USD') => {
  if (amount === null || amount === undefined) return '$0';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(amount);
};

/**
 * Formatea fechas de manera relativa (hace X tiempo)
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

/**
 * Formatea fechas para mostrar
 */
export const formatDate = (date) => {
  if (!date) return '';
  try {
    return new Date(date).toLocaleDateString('es-ES');
  } catch (_err) {
    return '';
  }
};

/**
 * Formatea el tamaño de archivos
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Trunca texto con puntos suspensivos
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Capitaliza la primera letra de una cadena
 */
export const capitalize = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

/**
 * Genera un color basado en una cadena (para avatares, etc.)
 */
export const getColorFromString = (str) => {
  if (!str) return '#6366F1';
  
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  const colors = [
    '#EF4444', '#F97316', '#F59E0B', '#EAB308',
    '#84CC16', '#22C55E', '#10B981', '#14B8A6',
    '#06B6D4', '#0EA5E9', '#3B82F6', '#6366F1',
    '#8B5CF6', '#A855F7', '#D946EF', '#EC4899'
  ];
  
  return colors[Math.abs(hash) % colors.length];
};

/**
 * Valida formato de email
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Debounce function para optimizar renders
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Ordena array por una propiedad
 */
export const sortBy = (array, key, direction = 'asc') => {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    
    if (aVal < bVal) return direction === 'asc' ? -1 : 1;
    if (aVal > bVal) return direction === 'asc' ? 1 : -1;
    return 0;
  });
};

/**
 * Agrupa array de objetos por una propiedad
 */
export const groupBy = (array, key) => {
  return array.reduce((groups, item) => {
    const group = (groups[item[key]] || []);
    group.push(item);
    groups[item[key]] = group;
    return groups;
  }, {});
};

/**
 * Valida si una cadena es una URL válida
 */
export const isValidUrl = (string) => {
  try {
    new URL(string);
    return true;
  } catch (_err) {
    return false;
  }
};

/**
 * Convierte archivo a base64
 */
export const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });
};

/**
 * Función para descargar archivos - AGREGADA para ReportsList
 */
export const downloadFile = (blob, filename) => {
  try {
    // Crear URL temporal para el blob
    const url = window.URL.createObjectURL(blob);
    
    // Crear elemento de enlace temporal
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    
    // Agregar al DOM temporalmente y hacer clic
    document.body.appendChild(link);
    link.click();
    
    // Limpiar
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error al descargar archivo:', error);
    // Fallback: intentar abrir en nueva ventana
    try {
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
      setTimeout(() => window.URL.revokeObjectURL(url), 1000);
    } catch (fallbackError) {
      console.error('Error en fallback de descarga:', fallbackError);
    }
  }
};

/**
 * Obtiene mensaje de error amigable
 */
export const getErrorMessage = (error) => {
  if (error?.response?.data?.message) {
    return error.response.data.message;
  } else if (error?.response?.data?.error) {
    return error.response.data.error;
  } else if (error?.message) {
    return error.message;
  } else if (error?.response?.status === 404) {
    return 'Recurso no encontrado';
  } else if (error?.response?.status === 500) {
    return 'Error interno del servidor';
  } else if (error?.response?.status >= 400 && error?.response?.status < 500) {
    return 'Error en la solicitud';
  } else if (!navigator.onLine) {
    return 'Sin conexión a internet. Verifica tu internet';
  } else {
    return error?.message || 'Error inesperado';
  }
};

/**
 * Formatea el progreso como porcentaje
 */
export const formatProgress = (current, total) => {
  if (total === 0) return '0%';
  return `${Math.round((current / total) * 100)}%`;
};

/**
 * Convierte bytes a formato legible
 */
export const bytesToSize = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Función cn para clases condicionales (como clsx)
 */
export const cn = (...args) => {
  return args
    .flat()
    .filter(x => typeof x === 'string')
    .join(' ')
    .trim();
};