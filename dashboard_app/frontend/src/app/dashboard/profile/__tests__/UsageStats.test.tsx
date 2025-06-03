import React from 'react';
import { render, screen } from '@testing-library/react';
import UsageStats from '../UsageStats';

// Mock the components used by UsageStats
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
  StatsSkeleton: ({ count }: { count: number }) => (
    <div data-testid="stats-skeleton" data-count={count}>Loading...</div>
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

describe('UsageStats', () => {
  const mockStats = {
    auditLogsViewed: 247,
    policyValidations: 32,
    cliScansInitiated: 18
  };

  const mockError = new Error('Failed to load usage statistics');
  const mockOnRetry = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading skeleton when isLoading is true', () => {
    render(
      <UsageStats 
        isLoading={true}
        stats={mockStats}
      />
    );

    expect(screen.getByTestId('stats-skeleton')).toBeInTheDocument();
    expect(screen.getByTestId('stats-skeleton')).toHaveAttribute('data-count', '3');
  });

  it('renders error display when isError is true', () => {
    render(
      <UsageStats 
        isLoading={false}
        isError={true}
        error={mockError}
        onRetry={mockOnRetry}
        stats={mockStats}
      />
    );

    expect(screen.getByTestId('error-display')).toBeInTheDocument();
    expect(screen.getByText(mockError.message)).toBeInTheDocument();
  });

  it('renders stats correctly when provided', () => {
    render(
      <UsageStats 
        isLoading={false}
        stats={mockStats}
      />
    );

    // Check if all stats are displayed
    expect(screen.getByText('Audit Logs Viewed')).toBeInTheDocument();
    expect(screen.getByText(mockStats.auditLogsViewed.toString())).toBeInTheDocument();
    
    expect(screen.getByText('Policy Validations')).toBeInTheDocument();
    expect(screen.getByText(mockStats.policyValidations.toString())).toBeInTheDocument();
    
    expect(screen.getByText('CLI Scans Initiated')).toBeInTheDocument();
    expect(screen.getByText(mockStats.cliScansInitiated.toString())).toBeInTheDocument();
    
    // Check if "Last 30 days" appears for each stat
    expect(screen.getAllByText('Last 30 days')).toHaveLength(3);
  });

  it('renders with default stats when not provided', () => {
    render(
      <UsageStats 
        isLoading={false}
      />
    );

    // Check if default stats (0) are displayed
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('calls onRetry when retry button is clicked', () => {
    render(
      <UsageStats 
        isLoading={false}
        isError={true}
        error={mockError}
        onRetry={mockOnRetry}
      />
    );

    // Click retry button
    screen.getByText('Retry').click();
    
    // Check if onRetry was called
    expect(mockOnRetry).toHaveBeenCalledTimes(1);
  });
});
