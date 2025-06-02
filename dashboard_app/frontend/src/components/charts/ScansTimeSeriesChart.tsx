'use client';

import React from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import Card from '@/components/ui/Card';

interface ScansTimeSeriesChartProps {
  data: {
    date: string;
    count: number;
    completed?: number;
    failed?: number;
    running?: number;
  }[];
  title?: string;
  className?: string;
  isLoading?: boolean;
  error?: Error | null;
  showArea?: boolean;
  timeRange?: 'day' | 'week' | 'month';
  onTimeRangeChange?: (range: 'day' | 'week' | 'month') => void;
}

export default function ScansTimeSeriesChart({
  data,
  title = 'Scans Over Time',
  className = '',
  isLoading = false,
  error = null,
  showArea = true,
  timeRange = 'week',
  onTimeRangeChange
}: ScansTimeSeriesChartProps) {
  // Format dates for display based on timeRange
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    switch (timeRange) {
      case 'day':
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      case 'week':
        return date.toLocaleDateString([], { weekday: 'short', month: 'numeric', day: 'numeric' });
      case 'month':
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
      default:
        return dateStr;
    }
  };

  // Format data for the chart
  const chartData = data?.map(item => ({
    ...item,
    formattedDate: formatDate(item.date)
  })) || [];

  const renderTimeRangeSelector = () => {
    if (!onTimeRangeChange) return null;
    
    return (
      <div className="flex justify-end mb-2 space-x-2 text-sm">
        <button
          className={`px-2 py-1 rounded ${timeRange === 'day' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
          onClick={() => onTimeRangeChange('day')}
        >
          Day
        </button>
        <button
          className={`px-2 py-1 rounded ${timeRange === 'week' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
          onClick={() => onTimeRangeChange('week')}
        >
          Week
        </button>
        <button
          className={`px-2 py-1 rounded ${timeRange === 'month' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
          onClick={() => onTimeRangeChange('month')}
        >
          Month
        </button>
      </div>
    );
  };

  return (
    <Card 
      title={title} 
      className={className}
      headerContent={renderTimeRangeSelector()}
    >
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="flex justify-center items-center h-64 text-red-500">
          {error.message || 'An error occurred while loading chart data'}
        </div>
      ) : chartData.length === 0 ? (
        <div className="flex justify-center items-center h-64 text-gray-500">
          No scan data available
        </div>
      ) : showArea ? (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={chartData}
              margin={{
                top: 10,
                right: 30,
                left: 0,
                bottom: 0,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="formattedDate" />
              <YAxis />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(23, 23, 23, 0.8)',
                  border: 'none',
                  borderRadius: '4px',
                  color: 'white'
                }}
              />
              <Legend />
              {chartData[0]?.completed !== undefined && (
                <Area 
                  type="monotone" 
                  dataKey="completed" 
                  stackId="1"
                  stroke="#10B981" 
                  fill="#10B981" 
                  name="Completed"
                />
              )}
              {chartData[0]?.running !== undefined && (
                <Area 
                  type="monotone" 
                  dataKey="running" 
                  stackId="1"
                  stroke="#3B82F6" 
                  fill="#3B82F6" 
                  name="Running"
                />
              )}
              {chartData[0]?.failed !== undefined && (
                <Area 
                  type="monotone" 
                  dataKey="failed" 
                  stackId="1"
                  stroke="#EF4444" 
                  fill="#EF4444" 
                  name="Failed"
                />
              )}
              {(chartData[0]?.completed === undefined && 
                chartData[0]?.running === undefined && 
                chartData[0]?.failed === undefined) && (
                <Area 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#8884d8" 
                  fill="#8884d8" 
                  name="Total Scans"
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={{
                top: 10,
                right: 30,
                left: 0,
                bottom: 0,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="formattedDate" />
              <YAxis />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(23, 23, 23, 0.8)',
                  border: 'none',
                  borderRadius: '4px',
                  color: 'white'
                }}
              />
              <Legend />
              {chartData[0]?.completed !== undefined && (
                <Line 
                  type="monotone" 
                  dataKey="completed" 
                  stroke="#10B981" 
                  activeDot={{ r: 8 }} 
                  name="Completed"
                />
              )}
              {chartData[0]?.running !== undefined && (
                <Line 
                  type="monotone" 
                  dataKey="running" 
                  stroke="#3B82F6" 
                  activeDot={{ r: 8 }} 
                  name="Running"
                />
              )}
              {chartData[0]?.failed !== undefined && (
                <Line 
                  type="monotone" 
                  dataKey="failed" 
                  stroke="#EF4444" 
                  activeDot={{ r: 8 }} 
                  name="Failed"
                />
              )}
              {(chartData[0]?.completed === undefined && 
                chartData[0]?.running === undefined && 
                chartData[0]?.failed === undefined) && (
                <Line 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#8884d8" 
                  activeDot={{ r: 8 }} 
                  name="Total Scans"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
