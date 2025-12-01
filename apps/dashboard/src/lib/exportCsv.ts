/**
 * CSV Export Utility
 * 
 * Provides functions to export data as CSV files
 */

interface ExportOptions {
  filename: string;
  headers?: string[];
}

/**
 * Convert an array of objects to CSV string
 */
export function objectsToCsv<T extends Record<string, any>>(
  data: T[],
  headers?: string[]
): string {
  if (data.length === 0) return '';

  // Get headers from first object if not provided
  const keys = headers || Object.keys(data[0]);
  
  // Create header row
  const headerRow = keys.map(escapeCell).join(',');
  
  // Create data rows
  const dataRows = data.map(row => 
    keys.map(key => escapeCell(String(row[key] ?? ''))).join(',')
  );

  return [headerRow, ...dataRows].join('\n');
}

/**
 * Escape a cell value for CSV
 */
function escapeCell(value: string): string {
  // If value contains comma, newline, or quote, wrap in quotes and escape quotes
  if (value.includes(',') || value.includes('\n') || value.includes('"')) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

/**
 * Download data as a CSV file
 */
export function downloadCsv<T extends Record<string, any>>(
  data: T[],
  options: ExportOptions
): void {
  const csv = objectsToCsv(data, options.headers);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = `${options.filename}.csv`;
  link.style.display = 'none';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
}

/**
 * Export usage analytics data
 */
export function exportAnalyticsData(
  stats: {
    total_api_calls: number;
    total_documents_signed: number;
    total_verifications: number;
    success_rate: number;
    avg_response_time_ms: number;
    period_start: string;
    period_end: string;
  },
  timeSeries: Array<{ timestamp: string; count: number }>
): void {
  // Export summary
  const summaryData = [{
    metric: 'Total API Calls',
    value: stats.total_api_calls,
    period: `${stats.period_start} to ${stats.period_end}`,
  }, {
    metric: 'Documents Signed',
    value: stats.total_documents_signed,
    period: `${stats.period_start} to ${stats.period_end}`,
  }, {
    metric: 'Verifications',
    value: stats.total_verifications,
    period: `${stats.period_start} to ${stats.period_end}`,
  }, {
    metric: 'Success Rate',
    value: `${stats.success_rate}%`,
    period: `${stats.period_start} to ${stats.period_end}`,
  }, {
    metric: 'Avg Response Time',
    value: `${stats.avg_response_time_ms}ms`,
    period: `${stats.period_start} to ${stats.period_end}`,
  }];

  downloadCsv(summaryData, {
    filename: `encypher-analytics-summary-${new Date().toISOString().split('T')[0]}`,
    headers: ['metric', 'value', 'period'],
  });
}

/**
 * Export time series data
 */
export function exportTimeSeriesData(
  timeSeries: Array<{ timestamp: string; count: number; value?: number }>
): void {
  const formattedData = timeSeries.map(item => ({
    date: new Date(item.timestamp).toLocaleDateString(),
    count: item.count,
    value: item.value ?? '',
  }));

  downloadCsv(formattedData, {
    filename: `encypher-usage-timeseries-${new Date().toISOString().split('T')[0]}`,
    headers: ['date', 'count', 'value'],
  });
}

/**
 * Export API keys list
 */
export function exportApiKeys(
  keys: Array<{
    name: string;
    maskedKey: string;
    createdAt: string;
    lastUsedAt?: string;
    permissions: string[];
  }>
): void {
  const formattedData = keys.map(key => ({
    name: key.name,
    key_prefix: key.maskedKey,
    created_at: key.createdAt,
    last_used: key.lastUsedAt || 'Never',
    permissions: key.permissions.join(', '),
  }));

  downloadCsv(formattedData, {
    filename: `encypher-api-keys-${new Date().toISOString().split('T')[0]}`,
    headers: ['name', 'key_prefix', 'created_at', 'last_used', 'permissions'],
  });
}

/**
 * Export team members list
 */
export function exportTeamMembers(
  members: Array<{
    name: string;
    email: string;
    role: string;
    status: string;
    joinedAt: string;
  }>
): void {
  downloadCsv(members, {
    filename: `encypher-team-members-${new Date().toISOString().split('T')[0]}`,
    headers: ['name', 'email', 'role', 'status', 'joinedAt'],
  });
}
