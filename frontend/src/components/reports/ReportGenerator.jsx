/* eslint-disable no-unused-vars */
/* eslint-disable no-undef */
// src/components/reports/ReportGenerator.jsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { 
  Sparkles, 
  FileText, 
  Settings, 
  Loader2,
  ChevronDown,
  Info
} from 'lucide-react';
import { useCreateReport } from '../../hooks/useReports';
import { REPORT_TYPES } from '../../utils/constants';
import { formatRelativeTime } from '../../utils/helpers';

const ReportGenerator = ({ csvFiles = [], selectedFile, onReportGenerated }) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const createReportMutation = useCreateReport();
  
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    setValue,
  } = useForm({
    defaultValues: {
      csv_file: selectedFile?.id || '',
      report_type: 'executive',
      title: '',
      description: '',
      user_prompt: '',
      generation_config: {
        include_charts: true,
        include_recommendations: true,
        include_cost_analysis: true,
        include_security_analysis: true,
      }
    }
  });

  const selectedCSVId = watch('csv_file');
  const selectedCSVFile = csvFiles.find(file => file.id === selectedCSVId);

  const onSubmit = async (data) => {
    try {
      await createReportMutation.mutateAsync(data);
      if (onReportGenerated) {
        onReportGenerated();
      }
    } catch (_error) {
      // Error ya manejado en el hook
    }
  };

  // Auto-generar título si no se ha especificado
  React.useEffect(() => {
    if (selectedCSVFile && !watch('title')) {
      const fileName = selectedCSVFile.original_filename.replace(/\.(csv|xlsx?|xls)$/i, '');
      setValue('title', `Análisis de ${fileName}`);
    }
  }, [selectedCSVFile, setValue, watch]);

  return (
    <div className="space-y-8">
      {/* Información del archivo seleccionado */}
      {selectedCSVFile && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-blue-50 rounded-xl p-6 border border-blue-200"
        >
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-blue-900 mb-2">
                Archivo Seleccionado
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-blue-600 font-medium">Nombre:</span>
                  <p className="text-blue-800">{selectedCSVFile.original_filename}</p>
                </div>
                <div>
                  <span className="text-blue-600 font-medium">Tamaño:</span>
                  <p className="text-blue-800">{formatFileSize(selectedCSVFile.file_size)}</p>
                </div>
                <div>
                  <span className="text-blue-600 font-medium">Filas:</span>
                  <p className="text-blue-800">{selectedCSVFile.rows_count?.toLocaleString() || 'Procesando...'}</p>
                </div>
                <div>
                  <span className="text-blue-600 font-medium">Subido:</span>
                  <p className="text-blue-800">{formatRelativeTime(selectedCSVFile.upload_date)}</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Formulario de generación */}
      <div className="bg-white rounded-xl shadow-soft border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Generar Reporte</h2>
              <p className="text-gray-600">Configura tu reporte inteligente</p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          {/* Selección de archivo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Archivo CSV *
            </label>
            <select
              {...register('csv_file', { required: 'Selecciona un archivo CSV' })}
              className={`input-field ${errors.csv_file ? 'border-red-500' : ''}`}
            >
              <option value="">Selecciona un archivo...</option>
              {csvFiles
                .filter(file => file.processing_status === 'completed')
                .map(file => (
                  <option key={file.id} value={file.id}>
                    {file.original_filename} ({formatFileSize(file.file_size)})
                  </option>
                ))
              }
            </select>
            {errors.csv_file && (
              <p className="mt-1 text-sm text-red-600">{errors.csv_file.message}</p>
            )}
          </div>

          {/* Título del reporte */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Título del Reporte *
            </label>
            <input
              type="text"
              {...register('title', { required: 'El título es requerido' })}
              className={`input-field ${errors.title ? 'border-red-500' : ''}`}
              placeholder="Ej: Análisis de Ventas Q3 2024"
            />
            {errors.title && (
              <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
            )}
          </div>

          {/* Tipo de reporte */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Reporte
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(REPORT_TYPES).map(([key, label]) => (
                <label key={key} className="relative">
                  <input
                    type="radio"
                    {...register('report_type')}
                    value={key}
                    className="sr-only peer"
                  />
                  <div className="p-4 border border-gray-200 rounded-lg cursor-pointer peer-checked:border-primary-500 peer-checked:bg-primary-50 hover:border-gray-300 transition-colors">
                    <div className="text-sm font-medium text-gray-900">{label}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Descripción */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descripción (Opcional)
            </label>
            <textarea
              {...register('description')}
              rows={3}
              className="input-field"
              placeholder="Describe el propósito de este reporte..."
            />
          </div>

          {/* Configuración avanzada */}
          <div>
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              <Settings className="w-4 h-4" />
              <span>Configuración Avanzada</span>
              <ChevronDown className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
            </button>

            {showAdvanced && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 p-4 bg-gray-50 rounded-lg space-y-4"
              >
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prompt Personalizado
                  </label>
                  <textarea
                    {...register('user_prompt')}
                    rows={3}
                    className="input-field"
                    placeholder="Ej: Enfócate en identificar oportunidades de ahorro de costos y problemas de seguridad..."
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Instrucciones específicas para el análisis con IA
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Incluir en el reporte:
                  </label>
                  <div className="space-y-2">
                    {[
                      { key: 'include_charts', label: 'Gráficos y visualizaciones' },
                      { key: 'include_recommendations', label: 'Recomendaciones automáticas' },
                      { key: 'include_cost_analysis', label: 'Análisis de costos' },
                      { key: 'include_security_analysis', label: 'Análisis de seguridad' },
                    ].map(({ key, label }) => (
                      <label key={key} className="flex items-center">
                        <input
                          type="checkbox"
                          {...register(`generation_config.${key}`)}
                          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                        <span className="ml-2 text-sm text-gray-700">{label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Submit button */}
          <div className="flex items-center justify-between pt-6 border-t border-gray-200">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Info className="w-4 h-4" />
              <span>La generación puede tomar 2-5 minutos</span>
            </div>
            
            <button
              type="submit"
              disabled={createReportMutation.isLoading || !selectedCSVId}
              className="btn-primary flex items-center space-x-2"
            >
              {createReportMutation.isLoading && (
                <Loader2 className="w-4 h-4 animate-spin" />
              )}
              <Sparkles className="w-4 h-4" />
              <span>
                {createReportMutation.isLoading ? 'Generando...' : 'Generar Reporte'}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ReportGenerator;