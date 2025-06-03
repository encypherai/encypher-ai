import React from 'react';
import Card from '@/components/ui/Card';
import { StatCardSkeleton } from '@/components/skeletons';
import ErrorDisplay from '@/components/ui/ErrorDisplay';
import { useAuditLogStats } from '@/lib/hooks/useAuditLogStats';
import { AuditLogFilters } from '@/lib/services/audit-logs';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import Button from '@/components/ui/Button';

interface AuditLogStatsCardProps {
  title: string;
  statType: 'total_logs' | 'success_rate' | 'actions_by_type' | 'logs_by_department';
  filters?: Omit<AuditLogFilters, 'page' | 'limit'>;
  className?: string;
  valueFormatter?: (value: number) => string;
  actionKey?: string;
  departmentKey?: string;
}

/**
 * A card component that displays a specific audit log statistic
 */
export default function AuditLogStatsCard({
  title,
  statType,
  filters = {},
  className = '',
  valueFormatter,
  actionKey,
  departmentKey
}: AuditLogStatsCardProps) {
  const { 
    data: stats, 
    isLoading, 
    error, 
    refetch 
  } = useAuditLogStats(filters);

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
    case 'total_logs':
      displayValue = valueFormatter ? valueFormatter(stats.total_logs) : stats.total_logs.toLocaleString();
      break;
    case 'success_rate':
      const percentage = stats.success_rate * 100;
      displayValue = valueFormatter ? valueFormatter(stats.success_rate) : `${percentage.toFixed(1)}%`;
      break;
    case 'actions_by_type':
      if (actionKey && stats.actions_by_type) {
        const value = stats.actions_by_type[actionKey] || 0;
        displayValue = valueFormatter ? valueFormatter(value) : value.toLocaleString();
      } else {
        displayValue = 'N/A';
      }
      break;
    case 'logs_by_department':
      if (departmentKey && stats.logs_by_department) {
        const value = stats.logs_by_department[departmentKey] || 0;
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
