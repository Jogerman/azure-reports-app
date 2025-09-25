/* eslint-disable no-unused-vars */
// src/components/dashboard/DashboardCard.jsx
import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '../../utils/helpers';

const DashboardCard = ({ 
  title, 
  value, 
  icon: IconComponent, // Renombrar para uso
  color = 'blue', 
  change, 
  changeType = 'increase' 
}) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500',
  };

  const changeColorClasses = {
    increase: 'text-green-600 bg-green-100',
    decrease: 'text-red-600 bg-red-100',
  };

  return (
    <div className="bg-white rounded-xl shadow-soft border border-gray-200 p-6 hover:shadow-medium transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          
          {change && (
            <div className="flex items-center mt-3">
              <div className={cn(
                'flex items-center px-2 py-1 rounded-full text-xs font-medium',
                changeColorClasses[changeType]
              )}>
                {changeType === 'increase' ? (
                  <TrendingUp className="w-3 h-3 mr-1" />
                ) : (
                  <TrendingDown className="w-3 h-3 mr-1" />
                )}
                <span>{change}</span>
              </div>
              <span className="text-xs text-gray-500 ml-2">vs. mes anterior</span>
            </div>
          )}
        </div>
        
        <div className={cn(
          'w-12 h-12 rounded-xl flex items-center justify-center',
          colorClasses[color]
        )}>
          <IconComponent className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );
};

export default DashboardCard;