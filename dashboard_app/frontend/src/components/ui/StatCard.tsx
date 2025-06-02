import React from 'react';
import Card from './Card';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: {
    value: string | number;
    isPositive: boolean;
  };
  icon?: React.ReactNode;
  className?: string;
}

export default function StatCard({ title, value, change, icon, className = '' }: StatCardProps) {
  return (
    <Card className={`flex items-center ${className}`}>
      {icon && <div className="mr-4 text-gray-500 dark:text-gray-400">{icon}</div>}
      <div>
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</h3>
        <div className="mt-1 flex items-baseline">
          <p className="text-2xl font-semibold text-gray-900 dark:text-white">{value}</p>
          {change && (
            <p className={`ml-2 flex items-baseline text-sm font-semibold ${change.isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {change.isPositive ? '+' : ''}{change.value}
            </p>
          )}
        </div>
      </div>
    </Card>
  );
}
