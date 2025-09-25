// frontend/src/components/dashboard/SpecializedMetrics.jsx

import React, { useState, useEffect } from 'react';
import { Shield, Zap, DollarSign, TrendingUp, AlertTriangle, CheckCircle, Clock, Target } from 'lucide-react';

const SpecializedMetrics = ({ reportType, analysisData }) => {
  if (!analysisData || !reportType) {
    return <div className="text-gray-500">No hay datos de análisis disponibles</div>;
  }

  const renderSecurityMetrics = () => {
    const metrics = analysisData.dashboard_metrics || {};
    const basicMetrics = analysisData.basic_metrics || {};

    return (
      <div className="space-y-6">
        {/* Security Score */}
        <div className="bg-gradient-to-r from-red-500 to-pink-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold mb-2">Security Score</h3>
              <div className="text-3xl font-bold">{metrics.security_score || 0}/100</div>
              <p className="text-red-100 text-sm">Nivel de riesgo: {metrics.risk_level || 'Unknown'}</p>
            </div>
            <Shield className="w-12 h-12 text-red-200" />
          </div>
        </div>

        {/* Security Metrics Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Issues Críticos"
            value={metrics.critical_issues || 0}
            icon={AlertTriangle}
            color="text-red-600"
            bgColor="bg-red-50"
          />
          <MetricCard
            title="Total Acciones"
            value={metrics.total_actions || 0}
            icon={Target}
            color="text-orange-600"
            bgColor="bg-orange-50"
          />
          <MetricCard
            title="Horas Trabajo"
            value={`${metrics.working_hours || 0}h`}
            icon={Clock}
            color="text-blue-600"
            bgColor="bg-blue-50"
          />
          <MetricCard
            title="Cobertura Cumplimiento"
            value={`${metrics.compliance_coverage || 0}%`}
            icon={CheckCircle}
            color="text-green-600"
            bgColor="bg-green-50"
          />
        </div>

        {/* Compliance Gaps */}
        {analysisData.compliance_gaps && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-semibold text-gray-900 mb-4">Gaps de Cumplimiento</h4>
            <ComplianceGapsChart gaps={analysisData.compliance_gaps} />
          </div>
        )}
      </div>
    );
  };

  const renderPerformanceMetrics = () => {
    const metrics = analysisData.dashboard_metrics || {};
    
    return (
      <div className="space-y-6">
        {/* Performance Score */}
        <div className="bg-gradient-to-r from-orange-500 to-red-500 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold mb-2">Performance Score</h3>
              <div className="text-3xl font-bold">{metrics.performance_score || 100}/100</div>
              <p className="text-orange-100 text-sm">Rating: {metrics.efficiency_rating || 'Good'}</p>
            </div>
            <Zap className="w-12 h-12 text-orange-200" />
          </div>
        </div>

        {/* Performance Metrics Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Optimizaciones Críticas"
            value={metrics.critical_optimizations || 0}
            icon={AlertTriangle}
            color="text-red-600"
            bgColor="bg-red-50"
          />
          <MetricCard
            title="Total Acciones"
            value={metrics.total_actions || 0}
            icon={Target}
            color="text-orange-600"
            bgColor="bg-orange-50"
          />
          <MetricCard
            title="Mejora Potencial"
            value={`${metrics.optimization_potential || 0}%`}
            icon={TrendingUp}
            color="text-green-600"
            bgColor="bg-green-50"
          />
          <MetricCard
            title="Horas Trabajo"
            value={`${metrics.working_hours || 0}h`}
            icon={Clock}
            color="text-blue-600"
            bgColor="bg-blue-50"
          />
        </div>

        {/* Optimization Opportunities */}
        {analysisData.optimization_opportunities && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-semibold text-gray-900 mb-4">Oportunidades de Optimización</h4>
            <OptimizationChart opportunities={analysisData.optimization_opportunities} />
          </div>
        )}
      </div>
    );
  };

  const renderCostMetrics = () => {
    const metrics = analysisData.dashboard_metrics || {};
    const roi = analysisData.roi_analysis || {};
    
    return (
      <div className="space-y-6">
        {/* Cost Savings */}
        <div className="bg-gradient-to-r from-green-500 to-blue-500 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold mb-2">Ahorros Mensuales</h3>
              <div className="text-3xl font-bold">${(metrics.monthly_savings || 0).toLocaleString()}</div>
              <p className="text-green-100 text-sm">Anuales: ${(metrics.annual_savings || 0).toLocaleString()}</p>
            </div>
            <DollarSign className="w-12 h-12 text-green-200" />
          </div>
        </div>

        {/* Cost Metrics Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="ROI Mensual"
            value={`${roi.monthly_roi_percentage || 0}%`}
            icon={TrendingUp}
            color="text-green-600"
            bgColor="bg-green-50"
          />
          <MetricCard
            title="Total Acciones"
            value={metrics.total_actions || 0}
            icon={Target}
            color="text-blue-600"
            bgColor="bg-blue-50"
          />
          <MetricCard
            title="Payback (Meses)"
            value={roi.payback_months || 0}
            icon={Clock}
            color="text-purple-600"
            bgColor="bg-purple-50"
          />
          <MetricCard
            title="Score Optimización"
            value={`${metrics.optimization_score || 100}%`}
            icon={CheckCircle}
            color="text-indigo-600"
            bgColor="bg-indigo-50"
          />
        </div>

        {/* Cost Opportunities */}
        {analysisData.cost_optimization_opportunities && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-semibold text-gray-900 mb-4">Oportunidades de Ahorro</h4>
            <CostOpportunitiesChart opportunities={analysisData.cost_optimization_opportunities} />
          </div>
        )}

        {/* Savings Breakdown */}
        {analysisData.savings_analysis && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-semibold text-gray-900 mb-4">Desglose de Ahorros</h4>
            <SavingsBreakdownChart savings={analysisData.savings_analysis} />
          </div>
        )}
      </div>
    );
  };

  // Render based on report type
  switch (reportType) {
    case 'security':
      return renderSecurityMetrics();
    case 'performance':
      return renderPerformanceMetrics();
    case 'cost':
      return renderCostMetrics();
    default:
      return <div className="text-gray-500">Tipo de reporte no reconocido</div>;
  }
};

// Metric Card Component
const MetricCard = ({ title, value, icon: Icon, color, bgColor }) => (
  <div className={`${bgColor} rounded-lg p-4`}>
    <div className="flex items-center">
      <Icon className={`w-6 h-6 ${color} mr-2`} />
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className={`text-lg font-bold ${color}`}>{value}</p>
      </div>
    </div>
  </div>
);

// Compliance Gaps Chart Component
const ComplianceGapsChart = ({ gaps }) => {
  const gapEntries = Object.entries(gaps || {});
  const maxValue = Math.max(...gapEntries.map(([, value]) => value), 1);

  return (
    <div className="space-y-3">
      {gapEntries.map(([category, count]) => (
        <div key={category}>
          <div className="flex justify-between text-sm mb-1">
            <span className="capitalize text-gray-600">
              {category.replace(/_/g, ' ')}
            </span>
            <span className="font-medium text-gray-900">{count}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-red-500 h-2 rounded-full"
              style={{ width: `${(count / maxValue) * 100}%` }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Optimization Chart Component
const OptimizationChart = ({ opportunities }) => {
  const oppEntries = Object.entries(opportunities || {});
  const maxValue = Math.max(...oppEntries.map(([, value]) => value), 1);

  return (
    <div className="space-y-3">
      {oppEntries.map(([category, count]) => (
        <div key={category}>
          <div className="flex justify-between text-sm mb-1">
            <span className="capitalize text-gray-600">
              {category.replace(/_/g, ' ')}
            </span>
            <span className="font-medium text-gray-900">{count}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-orange-500 h-2 rounded-full"
              style={{ width: `${(count / maxValue) * 100}%` }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Cost Opportunities Chart Component
const CostOpportunitiesChart = ({ opportunities }) => {
  const oppEntries = Object.entries(opportunities || {});
  const maxValue = Math.max(...oppEntries.map(([, value]) => value), 1);

  const getColor = (category) => {
    switch (category) {
      case 'rightsizing_opportunities':
        return 'bg-blue-500';
      case 'reserved_instance_opportunities':
        return 'bg-green-500';
      case 'storage_optimization':
        return 'bg-purple-500';
      case 'unused_resources':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-3">
      {oppEntries.map(([category, count]) => (
        <div key={category}>
          <div className="flex justify-between text-sm mb-1">
            <span className="capitalize text-gray-600">
              {category.replace(/_/g, ' ')}
            </span>
            <span className="font-medium text-gray-900">{count}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`${getColor(category)} h-2 rounded-full`}
              style={{ width: `${(count / maxValue) * 100}%` }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Savings Breakdown Chart Component
const SavingsBreakdownChart = ({ savings }) => {
  const total = savings.total_monthly_potential || 1;
  const immediate = savings.immediate_savings || 0;
  const shortTerm = savings.short_term_savings || 0;
  const longTerm = savings.long_term_savings || 0;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4 text-center">
        <div className="bg-green-50 rounded p-3">
          <div className="text-lg font-bold text-green-600">
            ${immediate.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Inmediato</div>
        </div>
        <div className="bg-blue-50 rounded p-3">
          <div className="text-lg font-bold text-blue-600">
            ${shortTerm.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Corto Plazo</div>
        </div>
        <div className="bg-purple-50 rounded p-3">
          <div className="text-lg font-bold text-purple-600">
            ${longTerm.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Largo Plazo</div>
        </div>
      </div>
      
      {/* Visual breakdown */}
      <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
        <div className="flex h-full">
          <div 
            className="bg-green-500" 
            style={{ width: `${(immediate / total) * 100}%` }}
          ></div>
          <div 
            className="bg-blue-500" 
            style={{ width: `${(shortTerm / total) * 100}%` }}
          ></div>
          <div 
            className="bg-purple-500" 
            style={{ width: `${(longTerm / total) * 100}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default SpecializedMetrics;