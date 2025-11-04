'use client';

import React from 'react';
import Table from '@/components/ui/Table';
import { TopContentItem } from '@/services/coalitionService';

interface ContentPerformanceTableProps {
  data: TopContentItem[];
  isLoading?: boolean;
  onRowClick?: (item: TopContentItem) => void;
}

export default function ContentPerformanceTable({
  data,
  isLoading = false,
  onRowClick
}: ContentPerformanceTableProps) {
  const columns = [
    {
      header: 'Title',
      accessor: 'title',
      className: 'font-medium text-gray-900 dark:text-white'
    },
    {
      header: 'Type',
      accessor: 'content_type',
      className: 'text-gray-600 dark:text-gray-400'
    },
    {
      header: 'Word Count',
      accessor: (item: TopContentItem) => item.word_count.toLocaleString(),
      className: 'text-right'
    },
    {
      header: 'Verifications',
      accessor: (item: TopContentItem) => item.verification_count.toLocaleString(),
      className: 'text-right'
    },
    {
      header: 'Access Count',
      accessor: (item: TopContentItem) => item.access_count.toLocaleString(),
      className: 'text-right'
    },
    {
      header: 'Revenue',
      accessor: (item: TopContentItem) => (
        <span className="font-semibold text-green-600 dark:text-green-400">
          ${item.revenue_generated.toFixed(2)}
        </span>
      ),
      className: 'text-right'
    }
  ] as const;

  return (
    <Table
      columns={columns}
      data={data}
      keyExtractor={(item: TopContentItem) => item.id}
      isLoading={isLoading}
      emptyMessage="No content performance data available"
      onRowClick={onRowClick}
    />
  );
}
