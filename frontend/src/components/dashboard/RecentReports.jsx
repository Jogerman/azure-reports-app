// src/components/dashboard/RecentReports.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Download, Eye, MoreHorizontal } from 'lucide-react';
import { formatRelativeTime, getStatusColor, getStatusIcon } from '../../utils/formatters';

const RecentReports = ({ reports = [] }) => {
  if (!reports || reports.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-soft border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">
          Reportes Recientes
        </h3>
        <div className="text-center py-8">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No tienes reportes aún</p>
          <Link
            to="/app/reports"
            className="mt-4 inline-flex items-center text-primary-600 hover:text-primary-700 font-medium"
          >
            Crear tu primer reporte
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-soft border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Reportes Recientes
        </h3>
        <Link
          to="/app/history"
          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          Ver todos
        </Link>
      </div>
      
      <div className="space-y-4">
        {reports.slice(0, 5).map((report, index) => (
          <motion.div
            key={report.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center justify-between p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
          >
            <div className="flex items-center space-x-3 flex-1 min-w-0">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-gray-900 truncate">
                  {report.title}
                </h4>
                <p className="text-sm text-gray-500">
                  {formatRelativeTime(report.created_at)}
                </p>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                  <span className="mr-1">{getStatusIcon(report.status)}</span>
                  {report.status}
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-2 ml-4">
              {report.status === 'completed' && (
                <>
                  <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                    <Eye className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                    <Download className="w-4 h-4" />
                  </button>
                </>
              )}
              <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                <MoreHorizontal className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default RecentReports;
