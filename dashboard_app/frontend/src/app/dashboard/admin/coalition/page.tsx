'use client';

import React, { useState } from 'react';
import {
  UsersIcon,
  DocumentTextIcon,
  CurrencyDollarIcon,
  CircleStackIcon
} from '@heroicons/react/24/outline';
import StatCard from '@/components/ui/StatCard';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Pagination from '@/components/ui/Pagination';
import { useAdminOverview, useCoalitionMembers } from '@/lib/hooks/useCoalition';
import { useNotifications } from '@/lib/notifications';
import MembersTable from '@/components/coalition/MembersTable';

// Tabs Component
interface TabsProps {
  defaultValue: string;
  children: React.ReactNode;
}

function Tabs({ defaultValue, children }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultValue);

  return (
    <div>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, { activeTab, setActiveTab } as any);
        }
        return child;
      })}
    </div>
  );
}

function TabsList({ children, activeTab, setActiveTab }: any) {
  return (
    <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
      <nav className="-mb-px flex space-x-8">
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child)) {
            return React.cloneElement(child, { activeTab, setActiveTab } as any);
          }
          return child;
        })}
      </nav>
    </div>
  );
}

function TabsTrigger({ value, children, activeTab, setActiveTab }: any) {
  const isActive = activeTab === value;

  return (
    <button
      onClick={() => setActiveTab(value)}
      className={`
        py-4 px-1 border-b-2 font-medium text-sm transition-colors
        ${
          isActive
            ? 'border-primary-500 text-primary-600 dark:text-primary-400'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
        }
      `}
    >
      {children}
    </button>
  );
}

function TabsContent({ value, children, activeTab }: any) {
  if (activeTab !== value) return null;
  return <div>{children}</div>;
}

export default function AdminCoalitionPage() {
  const { addNotification } = useNotifications();
  const [page, setPage] = useState(1);
  const limit = 20;

  const {
    data: overview,
    isLoading: overviewLoading,
    isError: overviewError,
    error: overviewErrorMsg
  } = useAdminOverview({
    onError: (err) => {
      addNotification({
        type: 'error',
        title: 'Failed to load coalition overview',
        message: err.message || 'An unexpected error occurred.',
      });
    },
  });

  const {
    data: membersData,
    isLoading: membersLoading,
    isError: membersError,
    error: membersErrorMsg,
    refetch: refetchMembers
  } = useCoalitionMembers((page - 1) * limit, limit, {
    onError: (err) => {
      addNotification({
        type: 'error',
        title: 'Failed to load coalition members',
        message: err.message || 'An unexpected error occurred.',
      });
    },
  });

  if (overviewError) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <h3 className="text-red-800 dark:text-red-200 font-medium">Error Loading Coalition Management</h3>
          <p className="text-red-600 dark:text-red-400 text-sm mt-1">{overviewErrorMsg?.message}</p>
        </div>
      </div>
    );
  }

  const totalPages = membersData ? Math.ceil(membersData.total / limit) : 1;

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Coalition Management</h1>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Members"
          value={overviewLoading ? '-' : overview?.total_members.toLocaleString() || '0'}
          icon={<UsersIcon className="h-8 w-8" />}
        />
        <StatCard
          title="Active Members"
          value={overviewLoading ? '-' : overview?.active_members.toLocaleString() || '0'}
          icon={<UsersIcon className="h-8 w-8" />}
        />
        <StatCard
          title="Total Revenue (MTD)"
          value={overviewLoading ? '-' : `$${overview?.total_revenue_mtd.toLocaleString() || '0'}`}
          icon={<CurrencyDollarIcon className="h-8 w-8" />}
        />
        <StatCard
          title="Content Pool"
          value={overviewLoading ? '-' : overview?.total_content.toLocaleString() || '0'}
          icon={<CircleStackIcon className="h-8 w-8" />}
        />
      </div>

      {/* Tabs */}
      <Tabs defaultValue="members">
        <TabsList>
          <TabsTrigger value="members">Members</TabsTrigger>
          <TabsTrigger value="agreements">Agreements</TabsTrigger>
          <TabsTrigger value="revenue">Revenue</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="members">
          <Card>
            <div className="mb-4 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Coalition Members</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Manage coalition members and their statistics
                </p>
              </div>
              <Button variant="primary" size="sm">
                Add Member
              </Button>
            </div>

            {membersError ? (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <p className="text-red-600 dark:text-red-400 text-sm">{membersErrorMsg?.message}</p>
                <Button onClick={() => refetchMembers()} variant="outline" size="sm" className="mt-2">
                  Retry
                </Button>
              </div>
            ) : (
              <>
                <MembersTable
                  data={membersData?.items || []}
                  isLoading={membersLoading}
                />

                {membersData && membersData.total > limit && (
                  <div className="mt-4">
                    <Pagination
                      currentPage={page}
                      totalPages={totalPages}
                      onPageChange={setPage}
                    />
                  </div>
                )}
              </>
            )}
          </Card>
        </TabsContent>

        <TabsContent value="agreements">
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Licensing Agreements</h2>
            <p className="text-gray-500 dark:text-gray-400">
              Agreements management coming soon. This will integrate with PRD-002 Licensing Agreement Management.
            </p>
          </Card>
        </TabsContent>

        <TabsContent value="revenue">
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Revenue Distribution</h2>
            <p className="text-gray-500 dark:text-gray-400">
              Revenue distribution controls coming soon.
            </p>
          </Card>
        </TabsContent>

        <TabsContent value="analytics">
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Coalition Analytics</h2>
            <p className="text-gray-500 dark:text-gray-400">
              Analytics dashboard coming soon.
            </p>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
