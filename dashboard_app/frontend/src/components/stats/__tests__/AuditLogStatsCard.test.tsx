import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import AuditLogStatsCard from '../AuditLogStatsCard';
import * as hooks from '@/lib/hooks/useAuditLogStats';

// Mock the hook
jest.mock('@/lib/hooks/useAuditLogStats', () => ({
  useAuditLogStats: jest.fn()
}));

describe('AuditLogStatsCard', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const mockStats = {
    total_logs: 150,
    success_rate: 0.85,
    actions_by_type: {
      'document_upload': 50,
      'document_verification': 75,
      'document_download': 25
    },
    logs_by_department: {
      'HR': 30,
      'Finance': 45,
      'Legal': 75
    },
    logs_by_day: [
      { date: '2025-05-26', count: 25, successful: 20, failed: 5 },
      { date: '2025-05-27', count: 30, successful: 28, failed: 2 },
      { date: '2025-05-28', count: 35, successful: 30, failed: 5 }
    ]
  };

  const renderWithQueryClient = (ui: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {ui}
      </QueryClientProvider>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading skeleton when data is loading', () => {
    (hooks.useAuditLogStats as jest.Mock).mockReturnValue({
      isLoading: true,
      data: null,
      error: null,
      refetch: jest.fn()
    });

    renderWithQueryClient(
      <AuditLogStatsCard 
        title="Test Card" 
        statType="total_logs" 
      />
    );

    expect(screen.getByText('Test Card')).toBeInTheDocument();
    // Check for loading state (would need to add a test-id to skeleton for better testing)
    expect(screen.getByText('Test Card').closest('div')).toHaveClass('animate-pulse');
  });

  it('renders error state when there is an error', () => {
    const error = new Error('Test error');
    (hooks.useAuditLogStats as jest.Mock).mockReturnValue({
      isLoading: false,
      data: null,
      error,
      refetch: jest.fn()
    });

    renderWithQueryClient(
      <AuditLogStatsCard 
        title="Test Card" 
        statType="total_logs" 
      />
    );

    expect(screen.getByText('Test Card')).toBeInTheDocument();
    expect(screen.getByText('Failed to load stats')).toBeInTheDocument();
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('renders total logs correctly', () => {
    (hooks.useAuditLogStats as jest.Mock).mockReturnValue({
      isLoading: false,
      data: mockStats,
      error: null,
      refetch: jest.fn()
    });

    renderWithQueryClient(
      <AuditLogStatsCard 
        title="Total Logs" 
        statType="total_logs" 
      />
    );

    expect(screen.getByText('Total Logs')).toBeInTheDocument();
    expect(screen.getByText('150')).toBeInTheDocument();
  });

  it('renders success rate as percentage', () => {
    (hooks.useAuditLogStats as jest.Mock).mockReturnValue({
      isLoading: false,
      data: mockStats,
      error: null,
      refetch: jest.fn()
    });

    renderWithQueryClient(
      <AuditLogStatsCard 
        title="Success Rate" 
        statType="success_rate" 
      />
    );

    expect(screen.getByText('Success Rate')).toBeInTheDocument();
    expect(screen.getByText('85.0%')).toBeInTheDocument();
  });

  it('renders specific action type count', () => {
    (hooks.useAuditLogStats as jest.Mock).mockReturnValue({
      isLoading: false,
      data: mockStats,
      error: null,
      refetch: jest.fn()
    });

    renderWithQueryClient(
      <AuditLogStatsCard 
        title="Document Uploads" 
        statType="actions_by_type"
        actionKey="document_upload"
      />
    );

    expect(screen.getByText('Document Uploads')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
  });

  it('renders specific department count', () => {
    (hooks.useAuditLogStats as jest.Mock).mockReturnValue({
      isLoading: false,
      data: mockStats,
      error: null,
      refetch: jest.fn()
    });

    renderWithQueryClient(
      <AuditLogStatsCard 
        title="HR Department" 
        statType="logs_by_department"
        departmentKey="HR"
      />
    );

    expect(screen.getByText('HR Department')).toBeInTheDocument();
    expect(screen.getByText('30')).toBeInTheDocument();
  });

  it('uses custom value formatter when provided', () => {
    (hooks.useAuditLogStats as jest.Mock).mockReturnValue({
      isLoading: false,
      data: mockStats,
      error: null,
      refetch: jest.fn()
    });

    const valueFormatter = (value: number) => `${value} logs`;

    renderWithQueryClient(
      <AuditLogStatsCard 
        title="Total Logs" 
        statType="total_logs"
        valueFormatter={valueFormatter}
      />
    );

    expect(screen.getByText('Total Logs')).toBeInTheDocument();
    expect(screen.getByText('150 logs')).toBeInTheDocument();
  });
});
