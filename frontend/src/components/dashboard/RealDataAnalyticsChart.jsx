// frontend/src/components/dashboard/RealDataAnalyticsChart.jsx - GRÁFICO CON DATOS REALES
import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { useCSVAnalysis } from '../hooks/useRealData';
import { AlertCircle, BarChart3 } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const RealDataAnalyticsChart = ({ hasRealData = false }) => {
  const { data: csvAnalysis, isLoading, error } = useCSVAnalysis();

  // Si no hay datos reales, mostrar mensaje
  if (!hasRealData || !csvAnalysis) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-600 mb-2">
            Sin Datos para Análisis
          </h3>
          <p className="text-gray-500 text-sm max-w-sm">
            Sube un archivo CSV de Azure Advisor para ver gráficos con análisis real de tus recomendaciones.
          </p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="text-center text-red-600">
          <p>Error cargando análisis: {error.message}</p>
        </div>
      </div>
    );
  }

  // Preparar datos para el gráfico de categorías
  const categoryData = csvAnalysis.analysis?.category_analysis?.distribution || [];
  
  const categoryChartData = {
    labels: categoryData.map(item => item.category),
    datasets: [
      {
        label: 'Recomendaciones por Categoría',
        data: categoryData.map(item => item.count),
        backgroundColor: categoryData.map(item => item.color),
        borderColor: categoryData.map(item => item.color),
        borderWidth: 1,
      },
    ],
  };

  const categoryChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          usePointStyle: true,
        },
      },
      title: {
        display: true,
        text: 'Distribución Real de Recomendaciones por Categoría',
        font: {
          size: 14,
          weight: 'bold'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#1F2937',
        bodyColor: '#1F2937',
        borderColor: '#E5E7EB',
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12,
        callbacks: {
          label: function(context) {
            const percentage = categoryData.find(item => item.category === context.label)?.percentage || 0;
            return `${context.label}: ${context.parsed.y} recomendaciones (${percentage}%)`;
          }
        }
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: '#F3F4F6',
        },
        ticks: {
          color: '#6B7280',
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#6B7280',
          maxRotation: 45,
        },
      },
    },
  };

  return (
    <div className="h-64 relative">
      {/* Indicador de datos reales */}
      <div className="absolute top-2 right-2 z-10">
        <div className="flex items-center gap-1 bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
          <BarChart3 className="w-3 h-3" />
          <span>Datos Reales</span>
        </div>
      </div>
      
      <Bar data={categoryChartData} options={categoryChartOptions} />
    </div>
  );
};

export default RealDataAnalyticsChart;
