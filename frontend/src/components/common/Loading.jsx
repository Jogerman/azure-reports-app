// src/components/common/Loading.jsx
import React from 'react';
import { Loader2 } from 'lucide-react';

const Loading = ({ 
  size = 'default', 
  text = 'Cargando...', 
  fullScreen = false,
  className = '' 
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    default: 'w-6 h-6',
    large: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  const textSizes = {
    small: 'text-sm',
    default: 'text-base',
    large: 'text-lg',
    xl: 'text-xl',
  };

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className={`animate-spin text-primary-600 ${sizeClasses.xl}`} />
          <p className={`text-gray-600 font-medium ${textSizes.large}`}>{text}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex items-center justify-center space-x-3 ${className}`}>
      <Loader2 className={`animate-spin text-primary-600 ${sizeClasses[size]}`} />
      {text && (
        <span className={`text-gray-600 ${textSizes[size]}`}>{text}</span>
      )}
    </div>
  );
};

export default Loading;