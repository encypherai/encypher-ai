import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import { ChartSkeleton } from '@/components/skeletons';
import ErrorDisplay from '@/components/ui/ErrorDisplay';
import { useAuditLogStats } from '@/lib/hooks/useAuditLogStats';
import { AuditLogFilters } from '@/lib/services/audit-logs';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import Button from '@/components/ui/Button';
import CustomTooltip from '@/components/ui/CustomTooltip';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

type TimeRange = 'day' | 'week' | 'month';

interface AuditLogTimeSeriesChartProps {
  title?: string;
  filters?: Omit<AuditLogFilters, 'page' | 'limit'>;
  className?: string;
  height?: string;
}

/**
 * A time series chart component that displays audit log data over time
 */
export default function AuditLogTimeSeriesChart({
  title = 'Audit Logs Over Time',
  filters = {},
  className = '',
  height = 'h-80'
}: AuditLogTimeSeriesChartProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('week');
  
  // Calculate date range based on selected time range
  const getDateRange = () => {
    const endDate = new Date();
    const startDate = new Date();
    
    switch (timeRange) {
      case 'day':
        startDate.setDate(endDate.getDate() - 1);
        break;
      case 'week':
        startDate.setDate(endDate.getDate() - 7);
        break;
      case 'month':
        startDate.setDate(endDate.getDate() - 30);
        break;
    }
    
    return {
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    };
  };
  
  const dateRangeFilters = getDateRange();
  
  const { 
    data: stats, 
    isLoading, 
    error, 
    refetch 
  } = useAuditLogStats({
    ...filters,
    ...dateRangeFilters
  });

  // Handle loading state
  if (isLoading) {
    return <ChartSkeleton title={title} height={height} className={className} />;
  }

  // Handle error state
  if (error || !stats) {
    return (
      <Card title={title} className={`${className} border-red-200 dark:border-red-800`}>
        <div className="p-4">
          <ErrorDisplay 
            error={error as Error} 
            message="Failed to load chart data" 
            onRetry={() => refetch()}
          />
        </div>
      </Card>
    );
  }

  // Format the data for the chart
  const chartData = Array.isArray(stats.logs_by_day) 
    ? stats.logs_by_day.map((item: any) => {
        // Ensure count and successful are proper numbers
        const count = Number(item.count || 0);
        const successful = Number(item.successful || 0);
        return {
          date: new Date(item.date).toLocaleDateString(),
          logs: count,
          successful: successful,
          failed: count - successful
        };
      }) 
    : [];

  // Time range selector buttons
  const TimeRangeSelector = () => (
    <div className="flex space-x-2 mb-4">
      <Button 
        size="sm" 
        variant={timeRange === 'day' ? 'primary' : 'outline'} 
        onClick={() => setTimeRange('day')}
      >
        24h
      </Button>
      <Button 
        size="sm" 
        variant={timeRange === 'week' ? 'primary' : 'outline'} 
        onClick={() => setTimeRange('week')}
      >
        7d
      </Button>
      <Button 
        size="sm" 
        variant={timeRange === 'month' ? 'primary' : 'outline'} 
        onClick={() => setTimeRange('month')}
      >
        30d
      </Button>
    </div>
  );

  return (
    <Card title={title} className={className}>
      <div className="p-4">
        <div className="flex justify-between items-center">
          <TimeRangeSelector />
          <Button 
            size="sm" 
            variant="ghost" 
            onClick={() => refetch()} 
            aria-label="Refresh chart"
          >
            <ArrowPathIcon className="h-4 w-4" />
          </Button>
        </div>
        
        <div className={`${height} w-full`}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={chartData}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip 
                content={<CustomTooltip 
                  formatter={(value, name) => [Number(value).toLocaleString(), name]}
                  labelFormatter={(label) => `Date: ${label}`}
                />}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="logs" 
                stackId="1"
                stroke="#8884d8" 
                fill="#8884d8" 
                name="Total Logs"
              />
              <Area 
                type="monotone" 
                dataKey="successful" 
                stackId="2"
                stroke="#82ca9d" 
                fill="#82ca9d" 
                name="Successful"
              />
              <Area 
                type="monotone" 
                dataKey="failed" 
                stackId="2"
                stroke="#ffc658" 
                fill="#ffc658" 
                name="Failed"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </Card>
  );
}
