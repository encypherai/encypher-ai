import React from 'react';
import { render, screen } from '@testing-library/react';
import ActivityLogList from '../ActivityLogList';
import { ActivityLog } from '@/lib/hooks/useActivityLogs';

// Mock the components used by ActivityLogList
jest.mock('@/components/ui/Card', () => {
  return function MockCard({ children, title }: { children: React.ReactNode, title?: string }) {
    return (
      <div data-testid="card">
        {title && <h2>{title}</h2>}
        {children}
      </div>
    );
  };
});

jest.mock('@/components/ui/Skeleton', () => ({
  ActivityLogSkeleton: ({ count }: { count: number }) => (
    <div data-testid="activity-log-skeleton" data-count={count}>Loading...</div>
  )
}));

jest.mock('@/components/ui/ErrorDisplay', () => {
  return function MockErrorDisplay({ message, onRetry }: { message: string, onRetry?: () => void }) {
    return (
      <div data-testid="error-display">
        {message}
        {onRetry && <button onClick={onRetry}>Retry</button>}
      </div>
    );
  };
});

describe('ActivityLogList', () => {
  const mockLogs: ActivityLog[] = [
    {
      id: '1',
      user_id: 1,
      action: 'Login',
      details: 'User logged in from 192.168.1.1',
      timestamp: '2023-06-01T10:00:00Z',
      ip_address: '192.168.1.1',
      user_agent: 'Mozilla/5.0'
    },
    {
      id: '2',
      user_id: 1,
      action: 'Profile Update',
      details: 'User updated their profile information',
      timestamp: '2023-06-02T11:30:00Z',
      ip_address: '192.168.1.1',
      user_agent: 'Mozilla/5.0'
    },
    {
      id: '3',
      user_id: 1,
      action: 'Password Change',
      details: 'User changed their password',
      timestamp: '2023-06-03T14:15:00Z',
      ip_address: '192.168.1.1',
      user_agent: 'Mozilla/5.0'
    }
  ];

  const mockError = new Error('Failed to load activity logs');
  const mockOnRetry = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading skeleton when isLoading is true', () => {
    render(
      <ActivityLogList 
        isLoading={true}
        logs={mockLogs}
      />
    );

    expect(screen.getByTestId('activity-log-skeleton')).toBeInTheDocument();
    expect(screen.getByTestId('activity-log-skeleton')).toHaveAttribute('data-count', '5');
  });

  it('renders error display when isError is true', () => {
    render(
      <ActivityLogList 
        isLoading={false}
        isError={true}
        error={mockError}
        onRetry={mockOnRetry}
        logs={mockLogs}
      />
    );

    expect(screen.getByTestId('error-display')).toBeInTheDocument();
    expect(screen.getByText(mockError.message)).toBeInTheDocument();
  });

  it('renders empty message when logs array is empty', () => {
    render(
      <ActivityLogList 
        isLoading={false}
        logs={[]}
        emptyMessage="No logs found"
      />
    );

    expect(screen.getByText('No logs found')).toBeInTheDocument();
  });

  it('renders logs correctly when provided', () => {
    render(
      <ActivityLogList 
        isLoading={false}
        logs={mockLogs}
      />
    );

    // Check if all log actions and details are displayed
    mockLogs.forEach(log => {
      expect(screen.getByText(log.action)).toBeInTheDocument();
      expect(screen.getByText(log.details)).toBeInTheDocument();
    });

    // Check if timestamps are formatted correctly
    expect(screen.getAllByText(/\d{1,2}:\d{2}/)).toHaveLength(mockLogs.length);
  });

  it('renders with default empty message when not provided', () => {
    render(
      <ActivityLogList 
        isLoading={false}
        logs={[]}
      />
    );

    expect(screen.getByText('No recent activity found.')).toBeInTheDocument();
  });

  it('uses custom empty message when provided', () => {
    const customEmptyMessage = 'Custom empty message';
    render(
      <ActivityLogList 
        isLoading={false}
        logs={[]}
        emptyMessage={customEmptyMessage}
      />
    );

    expect(screen.getByText(customEmptyMessage)).toBeInTheDocument();
  });
});
