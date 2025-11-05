import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import CoalitionPage from '../page';
import { useCoalitionStats } from '@/lib/hooks/useCoalition';
import { NotificationProvider } from '@/lib/notifications';

// Mock the hooks
jest.mock('@/lib/hooks/useCoalition');
jest.mock('@/lib/notifications', () => ({
  useNotifications: () => ({
    addNotification: jest.fn(),
  }),
  NotificationProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock the chart components
jest.mock('@/components/coalition/RevenueChart', () => ({
  __esModule: true,
  default: ({ data, isLoading }: any) => (
    <div data-testid="revenue-chart">
      {isLoading ? 'Loading...' : `Chart with ${data?.length || 0} items`}
    </div>
  ),
}));

jest.mock('@/components/coalition/ContentPerformanceTable', () => ({
  __esModule: true,
  default: ({ data, isLoading }: any) => (
    <div data-testid="content-performance-table">
      {isLoading ? 'Loading...' : `Table with ${data?.length || 0} items`}
    </div>
  ),
}));

jest.mock('@/components/coalition/AccessLogsTable', () => ({
  __esModule: true,
  default: ({ data, isLoading }: any) => (
    <div data-testid="access-logs-table">
      {isLoading ? 'Loading...' : `Logs with ${data?.length || 0} items`}
    </div>
  ),
}));

const mockCoalitionStats = {
  content_stats: {
    total_documents: 42,
    verification_count: 128,
    recent_documents: 15,
    trend_percentage: 12.5,
  },
  revenue_stats: {
    total_earned: 487.50,
    pending: 125.00,
    paid: 362.50,
    next_payout_date: '2025-02-01',
    monthly_average: 162.50,
  },
  revenue_history: [
    { month: 'Jan', earned: 150, paid: 150 },
    { month: 'Feb', earned: 175, paid: 0 },
  ],
  top_content: [
    {
      id: '1',
      title: 'Top Article',
      content_type: 'article',
      word_count: 1500,
      access_count: 45,
      revenue: 75.00,
    },
  ],
  recent_access: [
    {
      id: '1',
      ai_company: 'OpenAI',
      content_title: 'Test Article',
      accessed_at: '2025-01-04T10:00:00Z',
      access_type: 'training',
    },
  ],
};

describe('CoalitionPage', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderWithProviders = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <NotificationProvider>
          {component}
        </NotificationProvider>
      </QueryClientProvider>
    );
  };

  it('renders loading state', () => {
    (useCoalitionStats as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    });

    renderWithProviders(<CoalitionPage />);

    expect(screen.getByText('Coalition Dashboard')).toBeInTheDocument();
    expect(screen.getAllByText('-')).toHaveLength(4); // 4 stat cards with "-"
  });

  it('renders error state', () => {
    const errorMessage = 'Failed to load coalition data';
    (useCoalitionStats as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error(errorMessage),
    });

    renderWithProviders(<CoalitionPage />);

    expect(screen.getByText('Error Loading Coalition Dashboard')).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('renders coalition stats successfully', async () => {
    (useCoalitionStats as jest.Mock).mockReturnValue({
      data: mockCoalitionStats,
      isLoading: false,
      isError: false,
      error: null,
    });

    renderWithProviders(<CoalitionPage />);

    await waitFor(() => {
      // Check stat cards
      expect(screen.getByText('42')).toBeInTheDocument(); // total_documents
      expect(screen.getByText('128')).toBeInTheDocument(); // verification_count
      expect(screen.getByText('$487.50')).toBeInTheDocument(); // total_earned
      expect(screen.getByText('$125.00')).toBeInTheDocument(); // pending
    });
  });

  it('displays revenue stats correctly', async () => {
    (useCoalitionStats as jest.Mock).mockReturnValue({
      data: mockCoalitionStats,
      isLoading: false,
      isError: false,
      error: null,
    });

    renderWithProviders(<CoalitionPage />);

    await waitFor(() => {
      expect(screen.getByText('Feb 1, 2025')).toBeInTheDocument(); // next_payout_date
      expect(screen.getByText('$162.50')).toBeInTheDocument(); // monthly_average
      expect(screen.getByText('15')).toBeInTheDocument(); // recent_documents
    });
  });

  it('renders revenue chart', async () => {
    (useCoalitionStats as jest.Mock).mockReturnValue({
      data: mockCoalitionStats,
      isLoading: false,
      isError: false,
      error: null,
    });

    renderWithProviders(<CoalitionPage />);

    await waitFor(() => {
      const chart = screen.getByTestId('revenue-chart');
      expect(chart).toBeInTheDocument();
      expect(chart).toHaveTextContent('Chart with 2 items');
    });
  });

  it('renders content performance table', async () => {
    (useCoalitionStats as jest.Mock).mockReturnValue({
      data: mockCoalitionStats,
      isLoading: false,
      isError: false,
      error: null,
    });

    renderWithProviders(<CoalitionPage />);

    await waitFor(() => {
      const table = screen.getByTestId('content-performance-table');
      expect(table).toBeInTheDocument();
      expect(table).toHaveTextContent('Table with 1 items');
    });
  });

  it('renders access logs table', async () => {
    (useCoalitionStats as jest.Mock).mockReturnValue({
      data: mockCoalitionStats,
      isLoading: false,
      isError: false,
      error: null,
    });

    renderWithProviders(<CoalitionPage />);

    await waitFor(() => {
      const logs = screen.getByTestId('access-logs-table');
      expect(logs).toBeInTheDocument();
      expect(logs).toHaveTextContent('Logs with 1 items');
    });
  });

  it('displays trend percentage when available', async () => {
    (useCoalitionStats as jest.Mock).mockReturnValue({
      data: mockCoalitionStats,
      isLoading: false,
      isError: false,
      error: null,
    });

    renderWithProviders(<CoalitionPage />);

    await waitFor(() => {
      // The trend percentage should be displayed in the first stat card
      expect(screen.getByText('12.5%')).toBeInTheDocument();
    });
  });

  it('handles missing next payout date gracefully', async () => {
    const statsWithoutPayoutDate = {
      ...mockCoalitionStats,
      revenue_stats: {
        ...mockCoalitionStats.revenue_stats,
        next_payout_date: undefined,
      },
    };

    (useCoalitionStats as jest.Mock).mockReturnValue({
      data: statsWithoutPayoutDate,
      isLoading: false,
      isError: false,
      error: null,
    });

    renderWithProviders(<CoalitionPage />);

    await waitFor(() => {
      expect(screen.getByText('Not scheduled')).toBeInTheDocument();
    });
  });

  it('renders all section headers', async () => {
    (useCoalitionStats as jest.Mock).mockReturnValue({
      data: mockCoalitionStats,
      isLoading: false,
      isError: false,
      error: null,
    });

    renderWithProviders(<CoalitionPage />);

    await waitFor(() => {
      expect(screen.getByText('Revenue Over Time')).toBeInTheDocument();
      expect(screen.getByText('Top Performing Content')).toBeInTheDocument();
      expect(screen.getByText('Recent Content Access')).toBeInTheDocument();
    });
  });
});
