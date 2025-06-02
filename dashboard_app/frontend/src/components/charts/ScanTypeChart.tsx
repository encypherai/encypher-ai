'use client';

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import Card from '@/components/ui/Card';

interface ScanTypeChartProps {
  data: {
    type: string;
    count: number;
  }[];
  title?: string;
  className?: string;
  isLoading?: boolean;
  error?: Error | null;
}

// Define colors for different scan types
const TYPE_COLORS: Record<string, string> = {
  'audit-log': '#3B82F6',    // blue
  'policy-validator': '#8B5CF6', // purple
  'custom': '#EC4899',       // pink
};

// Default color for any undefined type
const DEFAULT_COLOR = '#10B981'; // green

export default function ScanTypeChart({
  data,
  title = 'Scan Type Distribution',
  className = '',
  isLoading = false,
  error = null,
}: ScanTypeChartProps) {
  // Format data for the chart
  const chartData = data?.map(item => ({
    name: formatTypeName(item.type),
    count: item.count,
    type: item.type,
  })) || [];

  // Calculate total scans
  const totalScans = chartData.reduce((sum, item) => sum + item.count, 0);

  // Helper function to format type names for display
  function formatTypeName(type: string): string {
    // Convert kebab-case to Title Case
    return type
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

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
            <BarChart
              data={chartData}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
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
              <Bar 
                dataKey="count" 
                name="Number of Scans" 
                fill="#8884d8"
                radius={[4, 4, 0, 0]}
              >
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={TYPE_COLORS[entry.type] || DEFAULT_COLOR} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
      <div className="mt-2 text-center text-sm text-gray-500">
        Total Scans: {totalScans}
      </div>
    </Card>
  );
}
