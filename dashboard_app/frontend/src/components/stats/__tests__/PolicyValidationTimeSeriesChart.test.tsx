import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import PolicyValidationTimeSeriesChart from '../PolicyValidationTimeSeriesChart';
import * as hooks from '@/lib/hooks/usePolicyValidationStats';

// Mock the hook
jest.mock('@/lib/hooks/usePolicyValidationStats', () => ({
  usePolicyValidationStats: jest.fn()
}));

// Mock recharts to avoid rendering issues in tests
jest.mock('recharts', () => {
  const OriginalModule = jest.requireActual('recharts');
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="responsive-container">{children}</div>
    ),
    AreaChart: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="area-chart">{children}</div>
    ),
    Area: () => <div data-testid="area" />,
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    CartesianGrid: () => <div data-testid="cartesian-grid" />,
    Tooltip: () => <div data-testid="tooltip" />,
    Legend: () => <div data-testid="legend" />
  };
});

describe('PolicyValidationTimeSeriesChart', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const mockStats = {
    total_validations: 200,
    valid_rate: 0.92,
    validations_by_schema: {
      'basic_schema': 80,
      'advanced_schema': 120
    },
    validations_by_department: {
      'HR': 40,
      'Finance': 60,
      'Legal': 100
    },
    validations_by_day: [
      { date: '2025-05-26', count: 50, valid: 45 },
      { date: '2025-05-27', count: 70, valid: 65 },
      { date: '2025-05-28', count: 80, valid: 75 }
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
    (hooks.usePolicyValidationStats as jest.Mock).mockReturnValue({
      isLoading: true,
      data: null,
      error: null,
      refetch: jest.fn()
    });

    renderWithQueryClient(
      <PolicyValidationTimeSeriesChart 
        title="Test Chart" 
      />
    );

    expect(screen.getByText('Test Chart')).toBeInTheDocument();
    // Check for loading state (would need to add a test-id to skeleton for better testing)
    expect(screen.getByText('Test Chart').closest('div')).toHaveClass('animate-pulse');
  });

  it('renders error state when there is an error', () => {
    const error = new Error('Test error');
    (hooks.usePolicyValidationStats as jest.Mock).mockReturnValue({
      isLoading: false,
      data: null,
      error,
      refetch: jest.fn()
    });

    renderWithQueryClient(
      <PolicyValidationTimeSeriesChart 
        title="Test Chart" 
      />
    );

    expect(screen.getByText('Test Chart')).toBeInTheDocument();
    expect(screen.getByText('Failed to load chart data')).toBeInTheDocument();
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('renders chart with data correctly', () => {
    (hooks.usePolicyValidationStats as jest.Mock).mockReturnValue({
      isLoading: false,
      data: mockStats,
      error: null,
      refetch: jest.fn()
    });

    renderWithQueryClient(
      <PolicyValidationTimeSeriesChart 
        title="Validation Trends" 
      />
    );

    expect(screen.getByText('Validation Trends')).toBeInTheDocument();
    expect(screen.getByText('24h')).toBeInTheDocument();
    expect(screen.getByText('7d')).toBeInTheDocument();
    expect(screen.getByText('30d')).toBeInTheDocument();
    
    // Check for chart components
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    expect(screen.getByTestId('area-chart')).toBeInTheDocument();
    expect(screen.getAllByTestId('area').length).toBe(3); // 3 Area components
  });

  it('changes time range when buttons are clicked', async () => {
    const refetchMock = jest.fn();
    (hooks.usePolicyValidationStats as jest.Mock).mockReturnValue({
      isLoading: false,
      data: mockStats,
      error: null,
      refetch: refetchMock
    });

    renderWithQueryClient(
      <PolicyValidationTimeSeriesChart 
        title="Validation Trends" 
      />
    );

    // Default is 'week', so '7d' button should be primary
    const dayButton = screen.getByText('24h');
    const weekButton = screen.getByText('7d');
    const monthButton = screen.getByText('30d');

    // Week button should have primary variant by default
    expect(weekButton.closest('button')).toHaveClass('bg-primary-600');
    
    // Click day button
    fireEvent.click(dayButton);
    
    // Now day button should have primary variant
    await waitFor(() => {
      expect(dayButton.closest('button')).toHaveClass('bg-primary-600');
      expect(weekButton.closest('button')).not.toHaveClass('bg-primary-600');
    });
    
    // Click month button
    fireEvent.click(monthButton);
    
    // Now month button should have primary variant
    await waitFor(() => {
      expect(monthButton.closest('button')).toHaveClass('bg-primary-600');
      expect(dayButton.closest('button')).not.toHaveClass('bg-primary-600');
    });
  });

  it('calls refetch when refresh button is clicked', () => {
    const refetchMock = jest.fn();
    (hooks.usePolicyValidationStats as jest.Mock).mockReturnValue({
      isLoading: false,
      data: mockStats,
      error: null,
      refetch: refetchMock
    });

    renderWithQueryClient(
      <PolicyValidationTimeSeriesChart 
        title="Validation Trends" 
      />
    );

    // Find and click the refresh button
    const refreshButton = screen.getByLabelText('Refresh chart');
    fireEvent.click(refreshButton);

    // Check if refetch was called
    expect(refetchMock).toHaveBeenCalledTimes(1);
  });
});
