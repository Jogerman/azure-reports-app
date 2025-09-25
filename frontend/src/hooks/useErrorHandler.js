// frontend/src/hooks/useErrorHandler.js
import { useState, useCallback } from 'react';
import { toast } from 'react-hot-toast';

export const useErrorHandler = () => {
  const [error, setError] = useState(null);

  const handleError = useCallback((error) => {
    console.error('Error handled:', error);
    
    let errorMessage = 'Ha ocurrido un error inesperado';
    
    // Extraer mensaje de error de diferentes formatos
    if (typeof error === 'string') {
      errorMessage = error;
    } else if (error?.response?.data) {
      // Error de axios
      const data = error.response.data;
      if (data.error) errorMessage = data.error;
      else if (data.detail) errorMessage = data.detail;
      else if (data.message) errorMessage = data.message;
    } else if (error?.message) {
      errorMessage = error.message;
    }
    
    setError(errorMessage);
    toast.error(errorMessage);
    
    // Auto-limpiar después de 5 segundos
    setTimeout(() => {
      setError(null);
    }, 5000);
    
    return errorMessage;
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    error,
    handleError,
    clearError
  };
};
