/**
 * Utility functions for exporting data from the admin dashboard
 */

import { InvestorAccessRecord } from './admin-api';

/**
 * Convert an array of investor access records to CSV format
 */
export function convertInvestorRecordsToCSV(records: InvestorAccessRecord[]): string {
  if (!records || records.length === 0) {
    return '';
  }

  // Define CSV headers
  const headers = [
    'ID',
    'Name',
    'Email',
    'Company',
    'Status',
    'Visit Count',
    'Last Visited',
    'Email Verified',
    'Created At',
    'Updated At',
  ];

  // Format date function
  const formatDate = (dateString: string | null): string => {
    if (!dateString) return '';
    try {
      return new Date(dateString).toISOString().split('T')[0];
    } catch {
      return '';
    }
  };

  // Create CSV content
  const csvContent = [
    // Add headers
    headers.join(','),
    // Add data rows
    ...records.map((record) => {
      return [
        record.id,
        record.investor_name ? `"${record.investor_name.replace(/"/g, '""')}"` : '',
        `"${record.investor_email.replace(/"/g, '""')}"`,
        record.investor_company ? `"${record.investor_company.replace(/"/g, '""')}"` : '',
        record.status,
        record.visit_count || 0,
        formatDate(record.last_visited_at),
        formatDate(record.email_verified_at),
        formatDate(record.created_at),
        formatDate(record.updated_at),
      ].join(',');
    }),
  ].join('\n');

  return csvContent;
}

/**
 * Download data as a CSV file
 */
export function downloadCSV(csvContent: string, filename: string): void {
  // Create a blob with the CSV content
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  
  // Create a download link
  const link = document.createElement('a');
  
  // Create a URL for the blob
  const url = URL.createObjectURL(blob);
  
  // Set link properties
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  // Add link to document
  document.body.appendChild(link);
  
  // Click the link to trigger download
  link.click();
  
  // Clean up
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Export investor records to CSV and trigger download
 */
export function exportInvestorRecordsToCSV(records: InvestorAccessRecord[]): void {
  const csvContent = convertInvestorRecordsToCSV(records);
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `investor-records-${timestamp}.csv`;
  
  downloadCSV(csvContent, filename);
}
