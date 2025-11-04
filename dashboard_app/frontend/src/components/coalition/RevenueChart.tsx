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
  ResponsiveContainer
} from 'recharts';
import Card from '@/components/ui/Card';
import { RevenueHistoryItem } from '@/services/coalitionService';

interface RevenueChartProps {
  data: RevenueHistoryItem[];
  className?: string;
  isLoading?: boolean;
}

export default function RevenueChart({ data, className = '', isLoading = false }: RevenueChartProps) {
  if (isLoading) {
    return (
      <Card className={className}>
        <div className="h-[300px] flex items-center justify-center">
          <div className="text-gray-400">Loading chart...</div>
        </div>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card className={className}>
        <div className="h-[300px] flex items-center justify-center">
          <div className="text-gray-400">No revenue data available</div>
        </div>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
          <XAxis
            dataKey="month"
            className="text-xs text-gray-600 dark:text-gray-400"
            tick={{ fill: 'currentColor' }}
          />
          <YAxis
            className="text-xs text-gray-600 dark:text-gray-400"
            tick={{ fill: 'currentColor' }}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--tooltip-bg, #fff)',
              border: '1px solid var(--tooltip-border, #ccc)',
              borderRadius: '0.375rem',
            }}
            formatter={(value: number) => [`$${value.toFixed(2)}`, '']}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="earned"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Earned"
            dot={{ fill: '#3b82f6', r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="paid"
            stroke="#10b981"
            strokeWidth={2}
            name="Paid"
            dot={{ fill: '#10b981', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
