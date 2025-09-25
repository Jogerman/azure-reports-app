// frontend/src/pages/Reports.jsx - VERSIÓN ACTUALIZADA PARA REPORTES ESPECIALIZADOS

import React, { useState, useEffect } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Clock, Download, Eye, BarChart3 } from 'lucide-react';
import SpecializedReportConfig from '../components/reports/SpecializedReportConfig';

const Reports = () => {
  // Estados existentes
  const [csvFile, setCsvFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [generatedReport, setGeneratedReport] = useState(null);
  
  // Nuevos estados para reportes especializados
  const [reportConfig, setReportConfig] = useState({
    title: '',
    description: '',
    type: 'comprehensive', // Por defecto completo
    includeGraphics: true,
    includeDetailedTables: true,
    includeRecommendations: true
  });
  
  const [reports, setReports] = useState([]);
  const [currentStep, setCurrentStep] = useState(1); // 1: Upload, 2: Config, 3: Generate

  // Cargar reportes existentes
  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const response = await fetch('/api/reports/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setReports(data.results || []);
      }
    } catch (error) {
      console.error('Error fetching reports:', error);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const xhr = new XMLHttpRequest();
      
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = (event.loaded / event.total) * 100;
          setUploadProgress(progress);
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200 || xhr.status === 201) {
          const response = JSON.parse(xhr.responseText);
          setCsvFile(response);
          setCurrentStep(2); // Ir a configuración
          
          // Auto-generar título basado en el filename
          const baseTitle = response.original_filename.split('.')[0].replace(/[_-]/g, ' ');
          setReportConfig(prev => ({
            ...prev,
            title: `${getReportTypeLabel(prev.type)} - ${baseTitle} - ${new Date().toLocaleDateString()}`
          }));
        }
        setIsUploading(false);
      };

      xhr.onerror = () => {
        console.error('Error uploading file');
        setIsUploading(false);
      };

      xhr.open('POST', '/api/files/upload/');
      xhr.setRequestHeader('Authorization', `Bearer ${localStorage.getItem('token')}`);
      xhr.send(formData);

    } catch (error) {
      console.error('Upload error:', error);
      setIsUploading(false);
    }
  };

  const getReportTypeLabel = (type) => {
    const types = {
      'comprehensive': 'Análisis Completo',
      'security': 'Análisis de Seguridad',
      'performance': 'Análisis de Rendimiento',
      'cost': 'Análisis de Costos'
    };
    return types[type] || 'Análisis';
  };

  const handleGenerateReport = async (config) => {
    if (!csvFile) return;

    setIsGenerating(true);
    setGenerationProgress(0);
    setCurrentStep(3);

    // Simular progreso de generación
    const progressInterval = setInterval(() => {
      setGenerationProgress(prev => {
        if (prev >= 90) return prev;
        return prev + Math.random() * 10;
      });
    }, 500);

    try {
      const response = await fetch('/api/reports/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          title: config.title,
          description: config.description,
          report_type: config.type,
          csv_file: csvFile.id,
          configuration: {
            include_graphics: config.includeGraphics,
            include_detailed_tables: config.includeDetailedTables,
            include_recommendations: config.includeRecommendations
          }
        })
      });

      if (response.ok) {
        const newReport = await response.json();
        
        // Polling para verificar el estado del reporte
        pollReportStatus(newReport.id, progressInterval);
        
      } else {
        throw new Error('Error creating report');
      }

    } catch (error) {
      console.error('Error generating report:', error);
      clearInterval(progressInterval);
      setIsGenerating(false);
    }
  };

  const pollReportStatus = async (reportId, progressInterval) => {
    const maxAttempts = 60; // 5 minutos máximo
    let attempts = 0;

    const checkStatus = async () => {
      try {
        const response = await fetch(`/api/reports/${reportId}/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (response.ok) {
          const report = await response.json();
          
          if (report.status === 'completed') {
            clearInterval(progressInterval);
            setGenerationProgress(100);
            setGeneratedReport(report);
            setIsGenerating(false);
            fetchReports(); // Actualizar lista
            
          } else if (report.status === 'failed') {
            clearInterval(progressInterval);
            setIsGenerating(false);
            console.error('Report generation failed:', report.error_message);
            
          } else if (attempts < maxAttempts) {
            // Continuar polling
            attempts++;
            setTimeout(checkStatus, 5000); // Check every 5 seconds
            
          } else {
            // Timeout
            clearInterval(progressInterval);
            setIsGenerating(false);
          }
        }
        
      } catch (error) {
        console.error('Error checking report status:', error);
        clearInterval(progressInterval);
        setIsGenerating(false);
      }
    };

    // Iniciar primera verificación después de 3 segundos
    setTimeout(checkStatus, 3000);
  };

  const handleReset = () => {
    setCsvFile(null);
    setGeneratedReport(null);
    setCurrentStep(1);
    setReportConfig({
      title: '',
      description: '',
      type: 'comprehensive',
      includeGraphics: true,
      includeDetailedTables: true,
      includeRecommendations: true
    });
    setUploadProgress(0);
    setGenerationProgress(0);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'processing':
      case 'generating':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <FileText className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusLabel = (status) => {
    const labels = {
      'draft': 'Borrador',
      'pending': 'Pendiente',
      'processing': 'Procesando',
      'generating': 'Generando',
      'completed': 'Completado',
      'failed': 'Fallido'
    };
    return labels[status] || status;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Reportes de Azure</h1>
          <p className="mt-2 text-gray-600">
            Genera reportes especializados basados en los datos de Azure Advisor
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center">
            {[
              { step: 1, label: 'Subir CSV', icon: Upload },
              { step: 2, label: 'Configurar', icon: BarChart3 },
              { step: 3, label: 'Generar', icon: FileText }
            ].map((item, index) => {
              const Icon = item.icon;
              const isActive = currentStep === item.step;
              const isCompleted = currentStep > item.step;
              
              return (
                <React.Fragment key={item.step}>
                  <div className="flex items-center">
                    <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                      isCompleted 
                        ? 'bg-green-500 border-green-500 text-white'
                        : isActive 
                          ? 'border-blue-500 text-blue-500'
                          : 'border-gray-300 text-gray-400'
                    }`}>
                      {isCompleted ? (
                        <CheckCircle className="w-6 h-6" />
                      ) : (
                        <Icon className="w-5 h-5" />
                      )}
                    </div>
                    <span className={`ml-3 text-sm font-medium ${
                      isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                    }`}>
                      {item.label}
                    </span>
                  </div>
                  {index < 2 && (
                    <div className={`flex-1 h-0.5 mx-4 ${
                      currentStep > item.step ? 'bg-green-500' : 'bg-gray-300'
                    }`} />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Step 1: File Upload */}
            {currentStep === 1 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Subir Archivo CSV
                </h2>
                
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Subir archivo de Azure Advisor
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Arrastra tu archivo CSV aquí, o haz clic para seleccionar
                  </p>
                  
                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => handleFileUpload(e.target.files[0])}
                    className="hidden"
                    id="file-upload"
                    disabled={isUploading}
                  />
                  
                  <label
                    htmlFor="file-upload"
                    className={`inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white ${
                      isUploading 
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 hover:bg-blue-700 cursor-pointer'
                    } transition-colors`}
                  >
                    {isUploading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Subiendo... {Math.round(uploadProgress)}%
                      </>
                    ) : (
                      'Seleccionar Archivo'
                    )}
                  </label>
                </div>

                {isUploading && (
                  <div className="mt-4">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="flex items-center mb-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                        <span className="text-sm font-medium text-blue-900">
                          Subiendo archivo...
                        </span>
                      </div>
                      <div className="w-full bg-blue-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${uploadProgress}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Step 2: Configuration */}
            {currentStep === 2 && csvFile && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <SpecializedReportConfig
                  reportConfig={reportConfig}
                  setReportConfig={setReportConfig}
                  onGenerate={handleGenerateReport}
                  csvFile={csvFile}
                  isGenerating={isGenerating}
                />
              </div>
            )}

            {/* Step 3: Generation */}
            {currentStep === 3 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                {isGenerating ? (
                  <div className="text-center">
                    <div className="mb-6">
                      <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                        <BarChart3 className="w-8 h-8 text-blue-600 animate-pulse" />
                      </div>
                      <h2 className="text-xl font-semibold text-gray-900 mb-2">
                        Generando Reporte
                      </h2>
                      <p className="text-gray-600">
                        Tu reporte de {getReportTypeLabel(reportConfig.type).toLowerCase()} está siendo procesado...
                      </p>
                    </div>

                    <div className="mb-6">
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${generationProgress}%` }}
                        ></div>
                      </div>
                      <p className="text-sm text-gray-500 mt-2">
                        {Math.round(generationProgress)}% completado
                      </p>
                    </div>

                    <div className="text-sm text-gray-600">
                      <p>⚡ Analizando datos con IA...</p>
                      <p>📊 Generando visualizaciones...</p>
                      <p>📄 Creando documento PDF...</p>
                    </div>
                  </div>
                ) : generatedReport ? (
                  <div className="text-center">
                    <div className="mb-6">
                      <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                        <CheckCircle className="w-8 h-8 text-green-600" />
                      </div>
                      <h2 className="text-xl font-semibold text-gray-900 mb-2">
                        ¡Reporte Completado!
                      </h2>
                      <p className="text-gray-600">
                        Tu reporte ha sido generado exitosamente
                      </p>
                    </div>

                    <div className="flex justify-center space-x-4">
                      <a
                        href={`/api/reports/${generatedReport.id}/html/`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                      >
                        <Eye className="w-5 h-5 mr-2" />
                        Ver Reporte
                      </a>
                      <a
                        href={`/api/reports/${generatedReport.id}/pdf/`}
                        className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                      >
                        <Download className="w-5 h-5 mr-2" />
                        Descargar PDF
                      </a>
                    </div>

                    <button
                      onClick={handleReset}
                      className="mt-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      Generar otro reporte
                    </button>
                  </div>
                ) : null}
              </div>
            )}
          </div>

          {/* Sidebar - Recent Reports */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Reportes Recientes
              </h3>
              
              {reports.length > 0 ? (
                <div className="space-y-3">
                  {reports.slice(0, 5).map((report) => (
                    <div
                      key={report.id}
                      className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(report.status)}
                        <div>
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {report.title}
                          </p>
                          <p className="text-xs text-gray-500">
                            {getStatusLabel(report.status)} • {new Date(report.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      
                      {report.status === 'completed' && (
                        <div className="flex space-x-1">
                          <a
                            href={`/api/reports/${report.id}/html/`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1 text-gray-400 hover:text-blue-600"
                            title="Ver reporte"
                          >
                            <Eye className="w-4 h-4" />
                          </a>
                          <a
                            href={`/api/reports/${report.id}/pdf/`}
                            className="p-1 text-gray-400 hover:text-green-600"
                            title="Descargar PDF"
                          >
                            <Download className="w-4 h-4" />
                          </a>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">
                  No hay reportes generados aún
                </p>
              )}
            </div>

            {/* Help Panel */}
            <div className="mt-6 bg-blue-50 rounded-lg border border-blue-200 p-4">
              <h4 className="text-sm font-medium text-blue-900 mb-2">
                💡 Tipos de Reporte
              </h4>
              <div className="space-y-2 text-xs text-blue-800">
                <p><strong>Completo:</strong> Análisis integral de todas las categorías</p>
                <p><strong>Seguridad:</strong> Enfoque en vulnerabilidades y cumplimiento</p>
                <p><strong>Rendimiento:</strong> Optimización de performance</p>
                <p><strong>Costos:</strong> Análisis de ahorros y ROI</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;