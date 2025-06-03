'use client';

import React, { useState } from 'react';
import { useQuery } from 'react-query';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import Input from '@/components/ui/Input';
import { 
  DocumentTextIcon, 
  DocumentChartBarIcon,
  ArrowDownTrayIcon,
  FunnelIcon,
  CalendarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '@/lib/notifications';

// Mock service - would be replaced with actual API calls
const reportsService = {
  getReportsList: async (filters: any) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock data
    return {
      reports: [
        {
          id: 1,
          name: 'Monthly Compliance Summary',
          type: 'compliance',
          created_at: '2025-05-01T10:30:00Z',
          status: 'completed',
          download_url: '#'
        },
        {
          id: 2,
          name: 'Audit Log Analysis Q1 2025',
          type: 'audit',
          created_at: '2025-04-15T14:22:00Z',
          status: 'completed',
          download_url: '#'
        },
        {
          id: 3,
          name: 'Policy Validation Failures',
          type: 'validation',
          created_at: '2025-05-28T09:15:00Z',
          status: 'completed',
          download_url: '#'
        },
        {
          id: 4,
          name: 'Security Posture Assessment',
          type: 'security',
          created_at: '2025-05-20T11:45:00Z',
          status: 'completed',
          download_url: '#'
        },
        {
          id: 5,
          name: 'Custom Report - ML Model Metadata',
          type: 'custom',
          created_at: '2025-06-01T08:30:00Z',
          status: 'processing',
          download_url: null
        }
      ],
      total: 5
    };
  },
  
  generateReport: async (reportData: any) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Return success response
    return {
      id: Math.floor(Math.random() * 1000),
      name: reportData.name,
      status: 'processing'
    };
  }
};

interface Report {
  id: number;
  name: string;
  type: string;
  created_at: string;
  status: string;
  download_url: string | null;
}

export default function ReportsPage() {
  const { addNotification } = useNotifications();
  const [filters, setFilters] = useState({
    type: 'all',
    dateRange: 'last30days',
    search: ''
  });
  
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [newReportData, setNewReportData] = useState({
    name: '',
    type: 'compliance',
    dateRange: 'last30days',
    includeCharts: true
  });
  
  const [showNewReportForm, setShowNewReportForm] = useState(false);
  
  // Fetch reports list
  const { 
    data, 
    isLoading, 
    isError, 
    error, 
    refetch 
  } = useQuery(
    ['reports', filters],
    () => reportsService.getReportsList(filters),
    {
      keepPreviousData: true,
      refetchOnWindowFocus: false
    }
  );
  
  const handleFilterChange = (name: string, value: string) => {
    setFilters(prev => ({ ...prev, [name]: value }));
  };
  
  const handleNewReportChange = (name: string, value: any) => {
    setNewReportData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleGenerateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGeneratingReport(true);
    
    try {
      const result = await reportsService.generateReport(newReportData);
      
      addNotification({
        type: 'success',
        title: 'Report Generation Started',
        message: `Your report "${newReportData.name}" is being generated. You'll be notified when it's ready.`
      });
      
      setShowNewReportForm(false);
      setNewReportData({
        name: '',
        type: 'compliance',
        dateRange: 'last30days',
        includeCharts: true
      });
      
      // Refetch the reports list after a short delay
      setTimeout(() => refetch(), 1000);
      
    } catch (err: any) {
      addNotification({
        type: 'error',
        title: 'Report Generation Failed',
        message: err.message || 'Failed to generate report. Please try again.'
      });
    } finally {
      setIsGeneratingReport(false);
    }
  };
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric'
    }).format(date);
  };
  
  const getReportTypeIcon = (type: string) => {
    switch (type) {
      case 'compliance':
        return <DocumentChartBarIcon className="h-5 w-5 text-blue-500" />;
      case 'audit':
        return <DocumentTextIcon className="h-5 w-5 text-purple-500" />;
      case 'validation':
        return <DocumentTextIcon className="h-5 w-5 text-green-500" />;
      case 'security':
        return <DocumentTextIcon className="h-5 w-5 text-red-500" />;
      default:
        return <DocumentTextIcon className="h-5 w-5 text-gray-500" />;
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Reports</h1>
        
        <Button
          variant="primary"
          onClick={() => setShowNewReportForm(!showNewReportForm)}
        >
          {showNewReportForm ? 'Cancel' : 'Generate New Report'}
        </Button>
      </div>
      
      {/* New Report Form */}
      {showNewReportForm && (
        <Card title="Generate New Report">
          <form onSubmit={handleGenerateReport} className="space-y-4">
            <Input
              label="Report Name"
              name="name"
              value={newReportData.name}
              onChange={(e) => handleNewReportChange('name', e.target.value)}
              required
              placeholder="Enter a descriptive name for your report"
            />
            
            <Select
              label="Report Type"
              options={[
                { value: 'compliance', label: 'Compliance Summary' },
                { value: 'audit', label: 'Audit Log Analysis' },
                { value: 'validation', label: 'Policy Validation' },
                { value: 'security', label: 'Security Posture' },
                { value: 'custom', label: 'Custom Report' }
              ]}
              value={newReportData.type}
              onChange={(value) => handleNewReportChange('type', value)}
            />
            
            <Select
              label="Date Range"
              options={[
                { value: 'last7days', label: 'Last 7 Days' },
                { value: 'last30days', label: 'Last 30 Days' },
                { value: 'last90days', label: 'Last 90 Days' },
                { value: 'thisyear', label: 'This Year' },
                { value: 'custom', label: 'Custom Range' }
              ]}
              value={newReportData.dateRange}
              onChange={(value) => handleNewReportChange('dateRange', value)}
            />
            
            <div className="flex items-center">
              <input
                id="includeCharts"
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                checked={newReportData.includeCharts}
                onChange={(e) => handleNewReportChange('includeCharts', e.target.checked)}
              />
              <label htmlFor="includeCharts" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                Include charts and visualizations
              </label>
            </div>
            
            <div className="flex justify-end">
              <Button
                type="submit"
                variant="primary"
                isLoading={isGeneratingReport}
              >
                Generate Report
              </Button>
            </div>
          </form>
        </Card>
      )}
      
      {/* Filters */}
      <Card>
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FunnelIcon className="h-5 w-5 text-gray-400" />
              </div>
              <Input
                placeholder="Search reports..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          
          <div className="w-full md:w-48">
            <Select
              label="Report Type"
              options={[
                { value: 'all', label: 'All Types' },
                { value: 'compliance', label: 'Compliance' },
                { value: 'audit', label: 'Audit' },
                { value: 'validation', label: 'Validation' },
                { value: 'security', label: 'Security' },
                { value: 'custom', label: 'Custom' }
              ]}
              value={filters.type}
              onChange={(value) => handleFilterChange('type', value)}
            />
          </div>
          
          <div className="w-full md:w-48">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Date Range</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <CalendarIcon className="h-5 w-5 text-gray-400" />
                </div>
                <Select
                  options={[
                    { value: 'all', label: 'All Time' },
                    { value: 'last7days', label: 'Last 7 Days' },
                    { value: 'last30days', label: 'Last 30 Days' },
                    { value: 'last90days', label: 'Last 90 Days' }
                  ]}
                  value={filters.dateRange}
                  onChange={(value) => handleFilterChange('dateRange', value)}
                  className="pl-10"
                />
              </div>
            </div>
          </div>
        </div>
      </Card>
      
      {/* Reports List */}
      <Card title="Available Reports">
        {isLoading ? (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
          </div>
        ) : isError ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mb-2" />
            <p className="text-red-600 dark:text-red-400 mb-1">Failed to load reports.</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
              {error instanceof Error ? error.message : 'An unexpected error occurred.'}
            </p>
            <Button onClick={() => refetch()} variant="outline" size="sm">
              Retry
            </Button>
          </div>
        ) : data?.reports.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">No reports found. Generate a new report to get started.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Report
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Created
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                {data?.reports.map((report: Report) => (
                  <tr key={report.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getReportTypeIcon(report.type)}
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {report.name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500 dark:text-gray-400 capitalize">
                        {report.type}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {formatDate(report.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${report.status === 'completed' 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'}`}>
                        {report.status === 'completed' ? 'Completed' : 'Processing'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {report.status === 'completed' ? (
                        <a 
                          href={report.download_url || '#'} 
                          className="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 inline-flex items-center"
                        >
                          <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                          Download
                        </a>
                      ) : (
                        <span className="text-gray-400 dark:text-gray-500">
                          Processing...
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
