import React from 'react';
import Card from '@/components/ui/Card';
import { StatCardSkeleton } from '@/components/skeletons';
import ErrorDisplay from '@/components/ui/ErrorDisplay';
import { usePolicyValidationStats } from '@/lib/hooks/usePolicyValidationStats';
import { ValidationFilters } from '@/lib/services/policy-validation';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import Button from '@/components/ui/Button';

interface PolicyValidationStatsCardProps {
  title: string;
  statType: 'total_validations' | 'valid_rate' | 'validations_by_schema' | 'validations_by_department';
  filters?: Omit<ValidationFilters, 'page' | 'limit'>;
  className?: string;
  valueFormatter?: (value: number) => string;
  schemaKey?: string;
  departmentKey?: string;
}

/**
 * A card component that displays a specific policy validation statistic
 */
export default function PolicyValidationStatsCard({
  title,
  statType,
  filters = {},
  className = '',
  valueFormatter,
  schemaKey,
  departmentKey
}: PolicyValidationStatsCardProps) {
  const { 
    data: stats, 
    isLoading, 
    error, 
    refetch 
  } = usePolicyValidationStats(filters);

  // Handle loading state
  if (isLoading) {
    return <StatCardSkeleton title={title} className={className} />;
  }

  // Handle error state
  if (error || !stats) {
    return (
      <Card title={title} className={`${className} border-red-200 dark:border-red-800`}>
        <div className="p-4">
          <ErrorDisplay 
            error={error as Error} 
            message="Failed to load stats" 
            onRetry={() => refetch()}
          />
        </div>
      </Card>
    );
  }

  // Format the value based on the stat type
  let displayValue: React.ReactNode;
  
  switch (statType) {
    case 'total_validations':
      displayValue = valueFormatter ? valueFormatter(stats.total_validations) : stats.total_validations.toLocaleString();
      break;
    case 'valid_rate':
      const percentage = stats.valid_rate * 100;
      displayValue = valueFormatter ? valueFormatter(stats.valid_rate) : `${percentage.toFixed(1)}%`;
      break;
    case 'validations_by_schema':
      if (schemaKey && stats.validations_by_schema) {
        const value = stats.validations_by_schema[schemaKey] || 0;
        displayValue = valueFormatter ? valueFormatter(value) : value.toLocaleString();
      } else {
        displayValue = 'N/A';
      }
      break;
    case 'validations_by_department':
      if (departmentKey && stats.validations_by_department) {
        const value = stats.validations_by_department[departmentKey] || 0;
        displayValue = valueFormatter ? valueFormatter(value) : value.toLocaleString();
      } else {
        displayValue = 'N/A';
      }
      break;
    default:
      displayValue = 'N/A';
  }

  return (
    <Card title={title} className={className}>
      <div className="flex flex-col items-center justify-center h-full p-4">
        <span className="text-4xl font-bold">{displayValue}</span>
        <div className="flex justify-end w-full mt-4">
          <Button 
            size="xs" 
            variant="ghost" 
            onClick={() => refetch()} 
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            aria-label="Refresh stats"
          >
            <ArrowPathIcon className="h-3 w-3" />
          </Button>
        </div>
      </div>
    </Card>
  );
}
