'use client';

import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { 
  ClipboardDocumentCheckIcon, 
  ShieldCheckIcon, 
  ExclamationTriangleIcon, 
  DocumentChartBarIcon 
} from '@heroicons/react/24/outline';
import Button from '@/components/ui/Button';
import { useNotifications } from '@/lib/notifications';
import Card from '@/components/ui/Card';
import StatCard from '@/components/ui/StatCard';
import { auditLogService } from '@/lib/services/audit-logs';
import { policyValidationService } from '@/lib/services/policy-validation';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import CustomTooltip from '@/components/ui/CustomTooltip';
import { safeTransformTimeSeriesData, safeTransformCategoryData, formatNumber } from '@/lib/utils/chart-helpers';

export default function DashboardPage() {
  const { addNotification } = useNotifications();
  const [dateRange, setDateRange] = useState({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
    endDate: new Date().toISOString().split('T')[0], // today
  });

  // Fetch audit log stats
  const { 
    data: auditLogStats, 
    isLoading: isLoadingAuditLogs,
    isError: isErrorAuditLogs,
    error: errorAuditLogs,
    refetch: refetchAuditLogs 
  } = useQuery<any, Error>(
    ['auditLogStats', dateRange],
    () => auditLogService.getAuditLogStats({
      start_date: dateRange.startDate,
      end_date: dateRange.endDate,
    }),
    {
      refetchInterval: 300000, // Refetch every 5 minutes
      onError: (err: Error) => {
        addNotification({
          type: 'error',
          title: 'Failed to load Audit Log Stats',
          message: err.message || 'An unexpected error occurred.',
        });
      }
    }
  );

  // Fetch policy validation stats
  const { 
    data: validationStats, 
    isLoading: isLoadingValidation,
    isError: isErrorValidation,
    error: errorValidation,
    refetch: refetchValidation
  } = useQuery<any, Error>(
    ['validationStats', dateRange],
    () => policyValidationService.getValidationStats({
      start_date: dateRange.startDate,
      end_date: dateRange.endDate,
    }),
    {
      refetchInterval: 300000, // Refetch every 5 minutes
      onError: (err: Error) => {
        addNotification({
          type: 'error',
          title: 'Failed to load Policy Validation Stats',
          message: err.message || 'An unexpected error occurred.',
        });
      }
    }
  );

  // Prepare data for charts using safe transformation utilities
  const auditLogsByDay = safeTransformTimeSeriesData(auditLogStats?.logs_by_day);
  const validationsByDay = safeTransformTimeSeriesData(validationStats?.validations_by_day);
  const auditLogsByDepartment = safeTransformCategoryData(auditLogStats?.logs_by_department);
  const validationsBySchema = safeTransformCategoryData(validationStats?.validations_by_schema);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Dashboard Overview</h1>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Audit Logs"
          value={auditLogStats?.total_logs || 0}
          icon={<ClipboardDocumentCheckIcon className="h-8 w-8" />}
        />
        <StatCard
          title="Audit Success Rate"
          value={`${auditLogStats?.success_rate ? Math.round(auditLogStats.success_rate * 100) : 0}%`}
          icon={<DocumentChartBarIcon className="h-8 w-8" />}
        />
        <StatCard
          title="Total Validations"
          value={validationStats?.total_validations || 0}
          icon={<ShieldCheckIcon className="h-8 w-8" />}
        />
        <StatCard
          title="Policy Compliance Rate"
          value={`${validationStats?.valid_rate ? Math.round(validationStats.valid_rate * 100) : 0}%`}
          icon={<ExclamationTriangleIcon className="h-8 w-8" />}
        />
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Audit Logs by Day */}
        <Card title="Audit Logs Activity">
          {isLoadingAuditLogs ? (
            <div className="h-80 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
            </div>
          ) : isErrorAuditLogs ? (
            <div className="h-80 flex flex-col items-center justify-center p-4 text-center">
              <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mb-2" />
              <p className="text-red-600 dark:text-red-400 mb-1">Failed to load audit log activity.</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">{errorAuditLogs?.message}</p>
              <Button onClick={() => refetchAuditLogs()} variant="outline" size="sm">Retry</Button>
            </div>
          ) : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={auditLogsByDay}
                  margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    angle={-45} 
                    textAnchor="end" 
                    height={60} 
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis />
                  <Tooltip 
                    content={<CustomTooltip 
                      formatter={(value, name) => [formatNumber(value), name]}
                      labelFormatter={(label) => `Date: ${label}`}
                    />}
                  />
                  <Bar dataKey="count" fill="#0ea5e9" name="Logs" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>
        
        {/* Validation Results by Day */}
        <Card title="Policy Validation Activity">
          {isLoadingValidation ? (
            <div className="h-80 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
            </div>
          ) : isErrorValidation ? (
            <div className="h-80 flex flex-col items-center justify-center p-4 text-center">
              <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mb-2" />
              <p className="text-red-600 dark:text-red-400 mb-1">Failed to load policy validation activity.</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">{errorValidation?.message}</p>
              <Button onClick={() => refetchValidation()} variant="outline" size="sm">Retry</Button>
            </div>
          ) : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={validationsByDay}
                  margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    angle={-45} 
                    textAnchor="end" 
                    height={60} 
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis />
                  <Tooltip 
                    content={<CustomTooltip 
                      formatter={(value, name) => [formatNumber(value), name]}
                      labelFormatter={(label) => `Date: ${label}`}
                    />}
                  />
                  <Bar dataKey="count" fill="#10b981" name="Validations" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>
        
        {/* Audit Logs by Department */}
        <Card title="Audit Logs by Department">
          {isLoadingAuditLogs ? (
            <div className="h-80 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
            </div>
          ) : isErrorAuditLogs ? (
            <div className="h-80 flex flex-col items-center justify-center p-4 text-center">
              <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mb-2" />
              <p className="text-red-600 dark:text-red-400 mb-1">Failed to load audit logs by department.</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">{errorAuditLogs?.message}</p>
              <Button onClick={() => refetchAuditLogs()} variant="outline" size="sm">Retry</Button>
            </div>
          ) : auditLogsByDepartment.length === 0 ? (
            <div className="h-80 flex items-center justify-center">
              <p className="text-gray-500 dark:text-gray-400">No audit log data by department.</p>
            </div>
          ) : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={auditLogsByDepartment}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {auditLogsByDepartment.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    content={<CustomTooltip 
                      formatter={(value, name) => [formatNumber(value), name]}
                      labelFormatter={(label) => `Department: ${label}`}
                    />}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>
        
        {/* Validations by Policy Schema */}
        <Card title="Validations by Policy Schema">
          {isLoadingValidation ? (
            <div className="h-80 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
            </div>
          ) : isErrorValidation ? (
            <div className="h-80 flex flex-col items-center justify-center p-4 text-center">
              <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mb-2" />
              <p className="text-red-600 dark:text-red-400 mb-1">Failed to load validations by schema.</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">{errorValidation?.message}</p>
              <Button onClick={() => refetchValidation()} variant="outline" size="sm">Retry</Button>
            </div>
          ) : validationsBySchema.length === 0 ? (
            <div className="h-80 flex items-center justify-center">
              <p className="text-gray-500 dark:text-gray-400">No validation data by schema.</p>
            </div>
          ) : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={validationsBySchema}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {validationsBySchema.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    content={<CustomTooltip 
                      formatter={(value, name) => [formatNumber(value), name]}
                      labelFormatter={(label) => `Schema: ${label}`}
                    />}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
