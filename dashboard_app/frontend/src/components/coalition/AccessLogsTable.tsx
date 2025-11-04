'use client';

import React from 'react';
import Table from '@/components/ui/Table';
import { RecentAccessItem } from '@/services/coalitionService';

interface AccessLogsTableProps {
  data: RecentAccessItem[];
  isLoading?: boolean;
  onRowClick?: (item: RecentAccessItem) => void;
}

export default function AccessLogsTable({
  data,
  isLoading = false,
  onRowClick
}: AccessLogsTableProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCompanyBadgeColor = (company: string) => {
    const colors: Record<string, string> = {
      'OpenAI': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'Anthropic': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'Google': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      'Microsoft': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      'Meta': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
    };
    return colors[company] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  };

  const columns = [
    {
      header: 'AI Company',
      accessor: (item: RecentAccessItem) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCompanyBadgeColor(item.ai_company)}`}>
          {item.ai_company}
        </span>
      )
    },
    {
      header: 'Content Title',
      accessor: 'content_title',
      className: 'font-medium text-gray-900 dark:text-white max-w-xs truncate'
    },
    {
      header: 'Access Type',
      accessor: (item: RecentAccessItem) => (
        <span className="capitalize text-gray-600 dark:text-gray-400">
          {item.access_type}
        </span>
      )
    },
    {
      header: 'Access Date',
      accessor: (item: RecentAccessItem) => (
        <span className="text-gray-600 dark:text-gray-400">
          {formatDate(item.accessed_at)}
        </span>
      )
    },
    {
      header: 'Revenue',
      accessor: (item: RecentAccessItem) => (
        <span className="font-semibold text-green-600 dark:text-green-400">
          ${item.revenue_amount.toFixed(2)}
        </span>
      ),
      className: 'text-right'
    }
  ] as const;

  return (
    <Table
      columns={columns}
      data={data}
      keyExtractor={(item: RecentAccessItem) => item.id}
      isLoading={isLoading}
      emptyMessage="No access logs available"
      onRowClick={onRowClick}
    />
  );
}
