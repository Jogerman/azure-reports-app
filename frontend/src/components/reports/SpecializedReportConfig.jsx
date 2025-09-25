// frontend/src/components/reports/SpecializedReportConfig.jsx
import React, { useState } from 'react';
import { Shield, Zap, DollarSign, BarChart3, CheckCircle, Info } from 'lucide-react';

const SpecializedReportConfig = ({ 
  reportConfig, 
  setReportConfig, 
  onGenerate, 
  csvFile, 
  isGenerating 
}) => {
  const [selectedType, setSelectedType] = useState(reportConfig.type || 'comprehensive');
  const [validationResults, setValidationResults] = useState(null);

  // Configuración de tipos de reporte especializados
  const reportTypes = [
    {
      value: 'comprehensive',
      label: 'Análisis Completo',
      description: 'Análisis detallado de todas las métricas',
      icon: BarChart3,
      color: 'bg-gradient-to-r from-blue-500 to-purple-600',
      features: ['Todas las categorías', 'Métricas completas', 'Recomendaciones detalladas'],
      estimatedTime: '3-5 minutos',
      dataRequirement: 'Cualquier CSV de Azure Advisor'
    },
    {
      value: 'security',
      label: 'Análisis de Seguridad',
      description: 'Enfoque en vulnerabilidades y configuración de seguridad',
      icon: Shield,
      color: 'bg-gradient-to-r from-red-500 to-pink-600',
      features: ['Análisis de vulnerabilidades', 'Gaps de cumplimiento', 'Score de seguridad'],
      estimatedTime: '2-3 minutos',
      dataRequirement: 'CSV con recomendaciones de seguridad'
    },
    {
      value: 'performance',
      label: 'Análisis de Rendimiento',
      description: 'Optimización de performance y cuellos de botella',
      icon: Zap,
      color: 'bg-gradient-to-r from-orange-500 to-red-500',
      features: ['Cuellos de botella', 'Oportunidades de optimización', 'Score de rendimiento'],
      estimatedTime: '2-3 minutos',
      dataRequirement: 'CSV con recomendaciones de performance'
    },
    {
      value: 'cost',
      label: 'Análisis de Costos',
      description: 'Optimización financiera y ahorro de recursos',
      icon: DollarSign,
      color: 'bg-gradient-to-r from-green-500 to-blue-500',
      features: ['Análisis de ahorros', 'ROI calculado', 'Oportunidades de costo'],
      estimatedTime: '2-3 minutos',
      dataRequirement: 'CSV con recomendaciones de costo'
    }
  ];

  const handleTypeSelection = (type) => {
    setSelectedType(type);
    setReportConfig(prev => ({ ...prev, type }));
  };

  const handleGenerate = () => {
    if (onGenerate) {
      onGenerate({
        ...reportConfig,
        type: selectedType
      });
    }
  };

  const getValidationIcon = (reportType) => {
    if (!validationResults) return null;
    
    const typeData = validationResults[`${reportType}_data`];
    if (typeData?.valid) {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    } else if (typeData?.valid === false) {
      return <Info className="w-5 h-5 text-yellow-500" />;
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Configurar Reporte Especializado
        </h2>
        <p className="text-gray-600">
          Selecciona el tipo de análisis que mejor se adapte a tus necesidades
        </p>
      </div>

      {/* CSV File Info */}
      {csvFile && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 text-blue-500 mr-2" />
            <div>
              <p className="text-sm font-medium text-blue-900">
                Archivo CSV: {csvFile.original_filename}
              </p>
              <p className="text-xs text-blue-700">
                {csvFile.rows_count?.toLocaleString()} filas • Procesado correctamente
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Report Type Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {reportTypes.map((type) => {
          const IconComponent = type.icon;
          const isSelected = selectedType === type.value;
          
          return (
            <div
              key={type.value}
              className={`relative cursor-pointer rounded-xl border-2 transition-all duration-200 ${
                isSelected
                  ? 'border-blue-500 shadow-lg transform scale-[1.02]'
                  : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
              }`}
              onClick={() => handleTypeSelection(type.value)}
            >
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-12 h-12 rounded-lg ${type.color} flex items-center justify-center`}>
                    <IconComponent className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex items-center space-x-2">
                    {getValidationIcon(type.value)}
                    {isSelected && (
                      <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                        <CheckCircle className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </div>
                </div>

                {/* Content */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {type.label}
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    {type.description}
                  </p>

                  {/* Features */}
                  <div className="space-y-2 mb-4">
                    {type.features.map((feature, index) => (
                      <div key={index} className="flex items-center text-xs text-gray-700">
                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mr-2"></div>
                        {feature}
                      </div>
                    ))}
                  </div>

                  {/* Meta info */}
                  <div className="flex justify-between items-center text-xs text-gray-500">
                    <span>⏱️ {type.estimatedTime}</span>
                    <span className="text-right">
                      {type.dataRequirement}
                    </span>
                  </div>
                </div>

                {/* Selected overlay */}
                {isSelected && (
                  <div className="absolute inset-0 rounded-xl bg-blue-500 bg-opacity-5 pointer-events-none"></div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Configuration Form */}
      <div className="bg-gray-50 rounded-lg p-6 space-y-4">
        <h3 className="text-lg font-medium text-gray-900">
          Configuración del Reporte
        </h3>

        {/* Título */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Título del Reporte
          </label>
          <input
            type="text"
            value={reportConfig.title || ''}
            onChange={(e) => setReportConfig(prev => ({ ...prev, title: e.target.value }))}
            placeholder={`Ej: ${reportTypes.find(t => t.value === selectedType)?.label} - ${new Date().toLocaleDateString()}`}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Descripción */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Descripción (Opcional)
          </label>
          <textarea
            rows={3}
            value={reportConfig.description || ''}
            onChange={(e) => setReportConfig(prev => ({ ...prev, description: e.target.value }))}
            placeholder="Describe el propósito específico de este análisis..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Opciones adicionales */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Opciones del Reporte
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={reportConfig.includeGraphics !== false}
                onChange={(e) => setReportConfig(prev => ({ ...prev, includeGraphics: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span className="ml-2 text-sm text-gray-700">Incluir gráficos y visualizaciones</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={reportConfig.includeDetailedTables !== false}
                onChange={(e) => setReportConfig(prev => ({ ...prev, includeDetailedTables: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span className="ml-2 text-sm text-gray-700">Incluir tablas detalladas</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={reportConfig.includeRecommendations !== false}
                onChange={(e) => setReportConfig(prev => ({ ...prev, includeRecommendations: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span className="ml-2 text-sm text-gray-700">Incluir recomendaciones de IA</span>
            </label>
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <div className="flex justify-end">
        <button
          onClick={handleGenerate}
          disabled={!csvFile || isGenerating || !reportConfig.title}
          className={`px-8 py-3 rounded-lg font-medium transition-colors ${
            !csvFile || isGenerating || !reportConfig.title
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl'
          }`}
        >
          {isGenerating ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Generando Reporte...
            </div>
          ) : (
            <div className="flex items-center">
              <BarChart3 className="w-5 h-5 mr-2" />
              Generar Reporte con IA
            </div>
          )}
        </button>
      </div>

      {/* Info panel for selected type */}
      {selectedType && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <Info className="w-5 h-5 text-blue-500 mr-3 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-blue-900 mb-1">
                Sobre {reportTypes.find(t => t.value === selectedType)?.label}
              </h4>
              <p className="text-sm text-blue-800">
                {selectedType === 'security' && 
                  "Este análisis se enfoca en identificar vulnerabilidades de seguridad, gaps de cumplimiento y riesgos potenciales en tu infraestructura de Azure. Incluye un score de seguridad y recomendaciones priorizadas."
                }
                {selectedType === 'performance' && 
                  "Este análisis identifica cuellos de botella de rendimiento, oportunidades de optimización y recursos subutilizados. Incluye métricas de performance y recomendaciones para mejorar la velocidad."
                }
                {selectedType === 'cost' && 
                  "Este análisis se centra en la optimización de costos, identificando ahorros potenciales, instancias reservadas recomendadas y recursos no utilizados. Incluye análisis de ROI y proyecciones de ahorro."
                }
                {selectedType === 'comprehensive' && 
                  "Este análisis completo incluye todas las categorías de Azure Advisor: seguridad, rendimiento, costo, confiabilidad y excelencia operacional. Proporciona una visión holística de tu infraestructura."
                }
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SpecializedReportConfig;