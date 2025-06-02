'use client';

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import Card from '@/components/ui/Card';

interface ScanStatusChartProps {
  data: {
    status: string;
    count: number;
  }[];
  title?: string;
  className?: string;
  isLoading?: boolean;
  error?: Error | null;
}

// Define colors for different scan statuses
const STATUS_COLORS: Record<string, string> = {
  completed: '#10B981', // green
  running: '#3B82F6',   // blue
  failed: '#EF4444',    // red
  pending: '#F59E0B',   // amber
  stopped: '#6B7280',   // gray
};

// Default color for any undefined status
const DEFAULT_COLOR = '#A855F7'; // purple

export default function ScanStatusChart({
  data,
  title = 'Scan Status Distribution',
  className = '',
  isLoading = false,
  error = null,
}: ScanStatusChartProps) {
  // Format data for the chart
  const chartData = data?.map(item => ({
    name: item.status.charAt(0).toUpperCase() + item.status.slice(1), // Capitalize status
    value: item.count,
    status: item.status,
  })) || [];

  // Calculate total scans
  const totalScans = chartData.reduce((sum, item) => sum + item.value, 0);

  const renderCustomizedLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
  }: any) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * Math.PI / 180);
    const y = cy + radius * Math.sin(-midAngle * Math.PI / 180);

    return percent > 0.05 ? (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    ) : null;
  };

  return (
    <Card title={title} className={className}>
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="flex justify-center items-center h-64 text-red-500">
          {error.message || 'An error occurred while loading chart data'}
        </div>
      ) : totalScans === 0 ? (
        <div className="flex justify-center items-center h-64 text-gray-500">
          No scan data available
        </div>
      ) : (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomizedLabel}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={STATUS_COLORS[entry.status] || DEFAULT_COLOR} 
                  />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: number) => [`${value} scans`, 'Count']}
                contentStyle={{ 
                  backgroundColor: 'rgba(23, 23, 23, 0.8)',
                  border: 'none',
                  borderRadius: '4px',
                  color: 'white'
                }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
      <div className="mt-2 text-center text-sm text-gray-500">
        Total Scans: {totalScans}
      </div>
    </Card>
  );
}
