'use client';

import React from 'react';
import Table from '@/components/ui/Table';
import { MemberListItem } from '@/services/coalitionService';

interface MembersTableProps {
  data: MemberListItem[];
  isLoading?: boolean;
  onRowClick?: (item: MemberListItem) => void;
}

export default function MembersTable({
  data,
  isLoading = false,
  onRowClick
}: MembersTableProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, string> = {
      'active': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'inactive': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
      'suspended': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    };
    return statusColors[status.toLowerCase()] || statusColors['inactive'];
  };

  const columns = [
    {
      header: 'Member',
      accessor: (item: MemberListItem) => (
        <div>
          <div className="font-medium text-gray-900 dark:text-white">{item.full_name || 'N/A'}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">{item.email}</div>
        </div>
      )
    },
    {
      header: 'Status',
      accessor: (item: MemberListItem) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadge(item.status)}`}>
          {item.status}
        </span>
      )
    },
    {
      header: 'Documents',
      accessor: (item: MemberListItem) => item.total_documents.toLocaleString(),
      className: 'text-right'
    },
    {
      header: 'Verifications',
      accessor: (item: MemberListItem) => item.total_verifications.toLocaleString(),
      className: 'text-right'
    },
    {
      header: 'Total Earned',
      accessor: (item: MemberListItem) => (
        <span className="font-semibold text-gray-900 dark:text-white">
          ${item.total_earned.toFixed(2)}
        </span>
      ),
      className: 'text-right'
    },
    {
      header: 'Pending Payout',
      accessor: (item: MemberListItem) => (
        <span className="font-semibold text-green-600 dark:text-green-400">
          ${item.pending_payout.toFixed(2)}
        </span>
      ),
      className: 'text-right'
    },
    {
      header: 'Joined',
      accessor: (item: MemberListItem) => (
        <span className="text-gray-600 dark:text-gray-400">
          {formatDate(item.joined_date)}
        </span>
      )
    }
  ] as const;

  return (
    <Table
      columns={columns}
      data={data}
      keyExtractor={(item: MemberListItem) => item.id}
      isLoading={isLoading}
      emptyMessage="No coalition members found"
      onRowClick={onRowClick}
    />
  );
}
