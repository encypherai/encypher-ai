// __tests__/ScanList.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import ScanList from '../ScanList';
import * as cliService from '@/services/cliService';
import * as notifications from '@/lib/notifications';
import * as nextRouter from 'next/navigation';

// Mock services and hooks
const mockGetScans = jest.fn();
const mockGetActiveScans = jest.fn();
const mockStopScan = jest.fn();
const mockDownloadScanReport = jest.fn();

jest.mock('@/services/cliService', () => ({
  __esModule: true, // This is important for ES modules
  default: {
    getScans: mockGetScans,
    getActiveScans: mockGetActiveScans,
    stopScan: mockStopScan,
    downloadScanReport: mockDownloadScanReport,
    // Mock other methods from cliService if ScanList starts using them
  },
  // Export CliScan interface if needed for type consistency in tests, though it's usually imported directly
}));

jest.mock('@/lib/notifications', () => ({
  useNotifications: jest.fn(),
}));
const mockedUseNotifications = notifications.useNotifications as jest.Mock;

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(), // Add if ScanList or its children use it
  useSearchParams: jest.fn(), // Add if ScanList or its children use it
}));
const mockedUseRouter = nextRouter.useRouter as jest.Mock;

// Mock UI components that are not the focus of these tests
// This helps simplify tests and avoid issues with their internal logic
jest.mock('@/components/ui/Table', () => (props: any) => <div data-testid="mock-table">{/* Render children to catch 'No scans found' etc. */ props.children}{JSON.stringify(props.data)}</div>);
jest.mock('@/components/ui/LoadingSpinner', () => () => <div data-testid="loading-spinner">Loading...</div>);
jest.mock('@/components/ui/ErrorDisplay', () => (props: any) => <div data-testid="error-display">{props.message || props.error?.message || 'Error'}</div>);
jest.mock('@/components/ui/Modal', () => (props: any) => props.isOpen ? <div data-testid="mock-modal">{props.title}{props.children}</div> : null);


const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false, // Disable retries for testing
      cacheTime: 0, // Disable caching for tests
    },
  },
});

const renderWithClient = (client: QueryClient, ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={client}>
      {ui}
    </QueryClientProvider>
  );
};

describe('ScanList Component', () => {
  let queryClient: QueryClient;
  let mockAddNotification: jest.Mock;
  let mockRouterPush: jest.Mock;

  beforeEach(() => {
    queryClient = createTestQueryClient();
    mockAddNotification = jest.fn();
    mockRouterPush = jest.fn();
    mockedUseNotifications.mockReturnValue({ addNotification: mockAddNotification });
    mockedUseRouter.mockReturnValue({ push: mockRouterPush });

    // Reset all mocks
    mockGetScans.mockReset();
    mockGetActiveScans.mockReset();
    mockStopScan.mockReset();
  });

  it('should render the title and refresh button', () => {
    mockGetScans.mockResolvedValue({ items: [], total: 0, page: 1, limit: 10, totalPages: 0 });
    renderWithClient(queryClient, <ScanList />);
    expect(screen.getByRole('heading', { name: 'CLI Scans' })).toBeInTheDocument();
    // The refresh button is an icon button, so we might need a more specific selector if "Refresh Scans" is not its accessible name
    // For now, assuming it has a title or aria-label that includes "Refresh"
    expect(screen.getByRole('button', { name: /refresh/i })).toBeInTheDocument();
  });

  it('should display loading spinner when isLoading is true', () => {
    mockGetScans.mockImplementation(() => new Promise(() => {})); // Never resolves
    renderWithClient(queryClient, <ScanList />);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('should display error message when isError is true', async () => {
    const errorMessage = 'Failed to fetch scans';
    mockGetScans.mockRejectedValue(new Error(errorMessage));
    renderWithClient(queryClient, <ScanList />);
    await waitFor(() => {
      expect(screen.getByTestId('error-display')).toHaveTextContent(errorMessage);
    });
    // Also check if notification was called
    await waitFor(() => {
        expect(mockAddNotification).toHaveBeenCalledWith(expect.objectContaining({
            type: 'error',
            title: 'Error fetching scans',
            message: errorMessage,
        }));
    });
  });

  it('should display empty state when there are no scans', async () => {
    mockGetScans.mockResolvedValue({ items: [], total: 0, page: 1, limit: 10, totalPages: 0 });
    renderWithClient(queryClient, <ScanList />);
    await waitFor(() => {
      // The text is inside the Table component's children when empty
      expect(screen.getByText('No scans found.')).toBeInTheDocument();
    });
  });

  // More tests to come for data display, actions, filtering, pagination

  const mockScans: cliService.CliScan[] = [
    {
      id: 1,
      scan_type: 'audit_log',
      status: 'completed',
      started_at: '2023-10-01T10:00:00Z',
      completed_at: '2023-10-01T11:00:00Z',
      user_id: 1,
      user_email: 'admin@example.com',
      progress: 100,
      output: 'Completed successfully'
    },
    {
      id: 2,
      scan_type: 'policy_validation',
      status: 'running',
      started_at: '2023-10-02T14:00:00Z',
      user_id: 2,
      user_email: 'system@example.com',
      target_path: 'DatabaseX',
      progress: 50,
    },
    {
      id: 3,
      scan_type: 'audit_log',
      status: 'failed',
      started_at: '2023-10-03T09:00:00Z',
      completed_at: '2023-10-03T09:30:00Z',
      user_id: 3,
      user_email: 'auditor@example.com',
      error_message: 'Critical vulnerabilities found',
      progress: 100,
    },
  ];

  it('should display scans when data is loaded', async () => {
    mockGetScans.mockResolvedValue({ items: mockScans, total: mockScans.length, page: 1, limit: 10, totalPages: 1 });
    renderWithClient(queryClient, <ScanList />);
    
    await waitFor(() => {
      // Check if mock table received data (stringified in mock)
      expect(screen.getByTestId('mock-table')).toHaveTextContent(JSON.stringify(mockScans));
      // Check for some specific data points if Table was not mocked or mocked differently
      // For example, check if scan IDs are present
      // Note: The Table mock currently just stringifies its data prop.
      // If we were testing against a real or more sophisticated mock Table, 
      // we'd query for actual rendered text based on scan_type.
      // For now, this confirms the data is passed.
      // Example of more specific check if Table rendered individual items:
      // expect(screen.getByText(mockScans[0].scan_type)).toBeInTheDocument(); 
      // expect(screen.getByText(mockScans[1].scan_type)).toBeInTheDocument();
    });
  });

  it('should call getActiveScans when activeOnly is true', async () => {
    mockGetActiveScans.mockResolvedValue({ items: [mockScans[1]], total: 1, page: 1, limit: 10, totalPages: 1 }); // Only the running scan
    renderWithClient(queryClient, <ScanList activeOnly={true} />);
    
    await waitFor(() => {
      expect(mockGetActiveScans).toHaveBeenCalledTimes(1);
      expect(mockGetScans).not.toHaveBeenCalled();
      expect(screen.getByTestId('mock-table')).toHaveTextContent(JSON.stringify([mockScans[1]]));
      // Similar to above, this confirms data is passed to the mock Table.
      // If testing against a real Table, we'd check for rendered text:
      // expect(screen.getByText(mockScans[1].scan_type)).toBeInTheDocument();
    });
  });

  it('should show "View All Scans" link if limit is exceeded and showAllLink is true (no pagination)', async () => {
    const limitedScans = [mockScans[0]]; // Only one scan to display initially
    mockGetScans.mockResolvedValue({ items: mockScans, total: mockScans.length, page: 1, limit: 10, totalPages: 1 }); // Service returns all
    
    renderWithClient(queryClient, <ScanList limit={1} showAllLink={true} enablePagination={false}/>);

    await waitFor(() => {
      // The table itself will be limited by the component's internal logic before passing to the Table mock
      // So we check what's actually rendered by ScanList's logic
      expect(screen.getByText(mockScans[0].scan_type)).toBeInTheDocument();
      expect(screen.queryByText(mockScans[1].scan_type)).not.toBeInTheDocument(); 
      expect(screen.getByRole('button', { name: 'View All Scans' })).toBeInTheDocument();
    });
  });

  it('should navigate when "View All Scans" link is clicked', async () => {
    mockGetScans.mockResolvedValue({ items: mockScans, total: mockScans.length, page: 1, limit: 10, totalPages: Math.ceil(mockScans.length / 10) });
    renderWithClient(queryClient, <ScanList limit={1} showAllLink={true} enablePagination={false}/>);

    await waitFor(() => {
      fireEvent.click(screen.getByRole('button', { name: 'View All Scans' }));
    });
    expect(mockRouterPush).toHaveBeenCalledWith('/dashboard/cli-integration');
  });

  it('should not show "View All Scans" link if limit is not exceeded', async () => {
    mockGetScans.mockResolvedValue({ items: [mockScans[0]], total: 1, page: 1, limit: 10, totalPages: 1 });
    renderWithClient(queryClient, <ScanList limit={1} showAllLink={true} enablePagination={false}/>);

    await waitFor(() => {
      expect(screen.getByText(mockScans[0].scan_type)).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: 'View All Scans' })).not.toBeInTheDocument();
    });
  });

  it('should not show "View All Scans" link if showAllLink is false', async () => {
    mockGetScans.mockResolvedValue({ items: mockScans, total: mockScans.length, page: 1, limit: 10, totalPages: Math.ceil(mockScans.length / 10) });
    renderWithClient(queryClient, <ScanList limit={1} showAllLink={false} enablePagination={false}/>);

    await waitFor(() => {
      expect(screen.queryByRole('button', { name: 'View All Scans' })).not.toBeInTheDocument();
    });
  });

  describe('Scan Actions - Stop Scan', () => {
    const runningScan = mockScans.find(s => s.status === 'running')!;

    beforeEach(() => {
      // Ensure a running scan is part of the default data for these tests
      mockGetScans.mockResolvedValue({ items: mockScans, total: mockScans.length, page: 1, limit: 10, totalPages: 1 });
      mockStopScan.mockResolvedValue({ ...runningScan, status: 'failed' }); // Simulate scan becoming 'failed' after stop
    });

    it('should open stop confirmation modal when stop button is clicked for a running scan', async () => {
      renderWithClient(queryClient, <ScanList />);
      await waitFor(() => expect(screen.getByTestId('mock-table')).toBeInTheDocument());

      // Find the stop button for the running scan
      // Assuming table rows can be identified or stop buttons are unique enough
      // For the mock table, data is stringified. We need a way to click a specific row's button.
      // Let's assume the actual Table component renders accessible buttons.
      // We'll simulate this by finding a button with aria-label or text "Stop scan {scanId}" or similar.
      // Since our Table is heavily mocked, we can't directly query for specific row buttons easily.
      // For now, we'll assume the first "Stop" button corresponds to the first stoppable scan.
      // A better mock for Table would allow querying specific row actions.
      const stopButtons = await screen.findAllByRole('button', { name: /stop scan/i });
      // This will need adjustment if the table mock or actual table structure is different.
      // Let's assume the Stop button for `runningScan` (id: 2) is identifiable.
      // The `ScanList` component itself generates these buttons with specific onClick handlers.
      // To test this properly, we might need to render the component with a less abstract Table mock or test the row component.
      
      // For this test, let's refine the mockScans to have only one running scan to simplify button finding
      const singleRunningScan = { ...runningScan };
      mockGetScans.mockResolvedValue({ items: [singleRunningScan], total: 1, page: 1, limit: 10, totalPages: 1 });
      renderWithClient(queryClient, <ScanList />); // Re-render with specific data
      await waitFor(() => expect(screen.getByTestId('mock-table')).toBeInTheDocument());

      const stopButton = screen.getByRole('button', { name: `Stop scan ${singleRunningScan.id}` });
      fireEvent.click(stopButton);

      await waitFor(() => {
        expect(screen.getByTestId('mock-modal')).toBeInTheDocument();
        expect(screen.getByText('Stop Scan')).toBeInTheDocument(); // Modal Title
        expect(screen.getByText('Are you sure you want to stop this scan? This action cannot be undone.')).toBeInTheDocument();
      });
    });

    it('should call stopScan service and show success notification when stop is confirmed', async () => {
      const singleRunningScan = { ...runningScan };
      mockGetScans.mockResolvedValue({ items: [singleRunningScan], total: 1, page: 1, limit: 10, totalPages: 1 });
      renderWithClient(queryClient, <ScanList />); 
      await waitFor(() => expect(screen.getByTestId('mock-table')).toBeInTheDocument());

      const stopButtonInRow = screen.getByRole('button', { name: `Stop scan ${singleRunningScan.id}` });
      fireEvent.click(stopButtonInRow);

      await waitFor(() => expect(screen.getByTestId('mock-modal')).toBeInTheDocument());
      const confirmStopButton = screen.getByRole('button', { name: 'Stop Scan' }); // Modal's stop button
      fireEvent.click(confirmStopButton);

      await waitFor(() => {
        expect(mockStopScan).toHaveBeenCalledWith(singleRunningScan.id);
        expect(mockAddNotification).toHaveBeenCalledWith(expect.objectContaining({
          type: 'success',
          title: 'Scan stopped',
        }));
      });
      expect(screen.queryByTestId('mock-modal')).not.toBeInTheDocument(); // Modal closes
    });

    it('should show error notification if stopScan service fails', async () => {
      const singleRunningScan = { ...runningScan };
      mockGetScans.mockResolvedValue({ items: [singleRunningScan], total: 1, page: 1, limit: 10, totalPages: 1 });
      const errorMessage = 'Failed to stop scan';
      mockStopScan.mockRejectedValue(new Error(errorMessage));
      renderWithClient(queryClient, <ScanList />); 
      await waitFor(() => expect(screen.getByTestId('mock-table')).toBeInTheDocument());

      const stopButtonInRow = screen.getByRole('button', { name: `Stop scan ${singleRunningScan.id}` });
      fireEvent.click(stopButtonInRow);

      await waitFor(() => expect(screen.getByTestId('mock-modal')).toBeInTheDocument());
      const confirmStopButton = screen.getByRole('button', { name: 'Stop Scan' });
      fireEvent.click(confirmStopButton);

      await waitFor(() => {
        expect(mockStopScan).toHaveBeenCalledWith(singleRunningScan.id);
        expect(mockAddNotification).toHaveBeenCalledWith(expect.objectContaining({
          type: 'error',
          title: 'Error stopping scan',
          message: errorMessage,
        }));
      });
      // Modal might stay open or close depending on error handling logic in component for mutations
      // Based on ScanList, it seems to close on success, but not explicitly on error within stopScanMutation's direct handlers.
      // The global onError for useMutation in cliService might handle it, or a finally block.
      // For now, let's assume the modal might still be open or closed based on specific implementation.
      // The component's stopScanMutation has onSettled, but not specifically closing modal on error.
      // Let's check if it's still open or not. The current modal mock closes if isOpen is false.
      // The component sets setIsStopModalOpen(false) in stopScanMutation.onSuccess, not onError.
      // So, it should remain open on error.
      expect(screen.getByTestId('mock-modal')).toBeInTheDocument();
    });

    it('should close modal when cancel button is clicked', async () => {
      const singleRunningScan = { ...runningScan };
      mockGetScans.mockResolvedValue({ items: [singleRunningScan], total: 1, page: 1, limit: 10, totalPages: 1 });
      renderWithClient(queryClient, <ScanList />); 
      await waitFor(() => expect(screen.getByTestId('mock-table')).toBeInTheDocument());

      const stopButtonInRow = screen.getByRole('button', { name: `Stop scan ${singleRunningScan.id}` });
      fireEvent.click(stopButtonInRow);

      await waitFor(() => expect(screen.getByTestId('mock-modal')).toBeInTheDocument());
      const cancelButton = screen.getByRole('button', { name: 'Cancel' });
      fireEvent.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByTestId('mock-modal')).not.toBeInTheDocument();
      });
      expect(mockStopScan).not.toHaveBeenCalled();
    });
  });

  describe('Scan Actions - View Scan Details', () => {
    const viewableScan = mockScans[0]; // Use the first scan for these tests

    beforeEach(() => {
      mockGetScans.mockResolvedValue({ items: [viewableScan], total: 1, page: 1, limit: 10, totalPages: 1 });
      mockRouterPush.mockClear(); // Clear router mock before each test
    });

    it('should call onScanSelect with scan ID when view button is clicked and prop is provided', async () => {
      const mockOnScanSelect = jest.fn();
      renderWithClient(queryClient, <ScanList onScanSelect={mockOnScanSelect} />); 
      await waitFor(() => expect(screen.getByTestId('mock-table')).toBeInTheDocument());

      const viewButton = screen.getByRole('button', { name: `View scan ${viewableScan.id}` });
      fireEvent.click(viewButton);

      expect(mockOnScanSelect).toHaveBeenCalledWith(viewableScan.id);
      expect(mockRouterPush).not.toHaveBeenCalled();
    });

    it('should call router.push with correct URL when view button is clicked and onScanSelect is not provided', async () => {
      renderWithClient(queryClient, <ScanList />); 
      await waitFor(() => expect(screen.getByTestId('mock-table')).toBeInTheDocument());

      const viewButton = screen.getByRole('button', { name: `View scan ${viewableScan.id}` });
      fireEvent.click(viewButton);

      expect(mockRouterPush).toHaveBeenCalledWith(`/dashboard/cli-integration/scans/${viewableScan.id}`);
    });
  });

  describe('Scan Actions - Download Report', () => {
    const completedScanWithReport = mockScans[2]; // This scan (ID 3) is completed and has report_path in output object
    const completedScanWithoutReport = {
      ...mockScans[2], // Base it on a scan known to have an object output
      id: 99, // Ensure different ID
      output: {
        // Assuming mockScans[2].output is an object, copy relevant fields if any, then set report_path
        ...(mockScans[2].output && typeof mockScans[2].output === 'object' ? mockScans[2].output as Record<string, any> : {}),
        report_path: undefined, 
      },
    };

    beforeEach(() => {
      mockDownloadScanReport.mockResolvedValue(new Blob(['report content'], { type: 'application/pdf' }));
      mockAddNotification.mockClear();
    });

    it('should show download button for completed scan with report_path and call download service on click', async () => {
      mockGetScans.mockResolvedValue({ items: [completedScanWithReport], total: 1, page: 1, limit: 10, totalPages: 1 });
      renderWithClient(queryClient, <ScanList />); 
      await waitFor(() => expect(screen.getByTestId('mock-table')).toBeInTheDocument());

      const downloadButton = screen.getByRole('button', { name: `Download report for scan ${completedScanWithReport.id}` });
      expect(downloadButton).toBeInTheDocument();
      fireEvent.click(downloadButton);

      const expectedFilename = completedScanWithReport.parameters?.target_systems?.[0] || completedScanWithReport.id.toString();
      await waitFor(() => {
        expect(mockDownloadScanReport).toHaveBeenCalledWith(completedScanWithReport.id, expectedFilename + '_report.pdf');
        expect(mockAddNotification).toHaveBeenCalledWith(expect.objectContaining({
          type: 'success',
          title: 'Report Downloaded',
          message: `Report ${expectedFilename}_report.pdf has started downloading.`,
        }));
      });
    });

    it('should not show download button if scan is not completed or has no report_path', async () => {
      const runningScan = mockScans.find(s => s.status === 'running')!;
      mockGetScans.mockResolvedValue({ items: [runningScan, completedScanWithoutReport], total: 2, page: 1, limit: 10, totalPages: 1 });
      renderWithClient(queryClient, <ScanList />); 
      await waitFor(() => expect(screen.getByTestId('mock-table')).toBeInTheDocument());

      expect(screen.queryByRole('button', { name: `Download report for scan ${runningScan.id}` })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: `Download report for scan ${completedScanWithoutReport.id}` })).not.toBeInTheDocument();
    });

    it('should show error notification if downloadScanReport service fails', async () => {
      mockGetScans.mockResolvedValue({ items: [completedScanWithReport], total: 1, page: 1, limit: 10, totalPages: 1 });
      const errorMessage = 'Failed to download report';
      mockDownloadScanReport.mockRejectedValue(new Error(errorMessage));
      renderWithClient(queryClient, <ScanList />); 
      await waitFor(() => expect(screen.getByTestId('mock-table')).toBeInTheDocument());

      const downloadButton = screen.getByRole('button', { name: `Download report for scan ${completedScanWithReport.id}` });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(mockAddNotification).toHaveBeenCalledWith(expect.objectContaining({
          type: 'error',
          title: 'Download Error',
          message: errorMessage,
        }));
      });
    });
  });

  describe('Filtering Functionality', () => {
    beforeEach(() => {
      // Reset mocks before each filter test
      mockGetScans.mockClear();
      mockGetScans.mockResolvedValue({ items: mockScans, total: mockScans.length, page: 1, limit: 10, totalPages: 1 });
      // Render the component with filtering enabled
      renderWithClient(queryClient, <ScanList enableFiltering={true} />);
      // Open the filter section by default for these tests if there's a button for it
      // Based on ScanList.tsx, filters are visible if enableFiltering is true and a button might toggle 'isFilterOpen'
      // Let's assume for testing, we'll need to click a 'Filter' button to reveal options.
      // The ScanList component uses a FunnelIcon button to toggle filter visibility.
      const filterToggleButton = screen.getByRole('button', { name: /toggle filters/i });
      fireEvent.click(filterToggleButton);
    });

    it('should call getScans with type filter when applied', async () => {
      const filterTypeSelect = screen.getByLabelText(/filter by type/i);
      const applyButton = screen.getByRole('button', { name: /apply filters/i });

      fireEvent.change(filterTypeSelect, { target: { value: 'audit_log' } });
      fireEvent.click(applyButton);

      await waitFor(() => {
        expect(mockGetScans).toHaveBeenCalledWith(expect.objectContaining({
          scan_type: 'audit_log',
          page: 1, // Should reset to page 1 on filter apply
        }));
      });
    });

    it('should call getScans with status filter when applied', async () => {
      const filterStatusSelect = screen.getByLabelText(/filter by status/i);
      const applyButton = screen.getByRole('button', { name: /apply filters/i });

      fireEvent.change(filterStatusSelect, { target: { value: 'completed' } });
      fireEvent.click(applyButton);

      await waitFor(() => {
        expect(mockGetScans).toHaveBeenCalledWith(expect.objectContaining({
          status: 'completed',
          page: 1,
        }));
      });
    });

    it('should call getScans with both type and status filters when applied', async () => {
      const filterTypeSelect = screen.getByLabelText(/filter by type/i);
      const filterStatusSelect = screen.getByLabelText(/filter by status/i);
      const applyButton = screen.getByRole('button', { name: /apply filters/i });

      fireEvent.change(filterTypeSelect, { target: { value: 'policy_validation' } });
      fireEvent.change(filterStatusSelect, { target: { value: 'running' } });
      fireEvent.click(applyButton);

      await waitFor(() => {
        expect(mockGetScans).toHaveBeenCalledWith(expect.objectContaining({
          scan_type: 'policy_validation',
          status: 'running',
          page: 1,
        }));
      });
    });

    it('should call getScans without filters when filters are cleared', async () => {
      const filterTypeSelect = screen.getByLabelText(/filter by type/i);
      const applyButton = screen.getByRole('button', { name: /apply filters/i });
      const clearButton = screen.getByRole('button', { name: /clear filters/i });

      // Apply a filter first
      fireEvent.change(filterTypeSelect, { target: { value: 'audit_log' } });
      fireEvent.click(applyButton);

      await waitFor(() => {
        expect(mockGetScans).toHaveBeenCalledWith(expect.objectContaining({ scan_type: 'audit_log' }));
      });

      mockGetScans.mockClear(); // Clear mock before testing clear action
      mockGetScans.mockResolvedValue({ items: mockScans, total: mockScans.length, page: 1, limit: 10, totalPages: 1 }); // Reset for the next call

      fireEvent.click(clearButton);

      await waitFor(() => {
        // After clearing, it should call getScans without scan_type or status, but with pagination defaults
        expect(mockGetScans).toHaveBeenCalledWith(expect.objectContaining({
          page: 1,
          limit: 10, // Assuming default limit
        }));
        // Ensure specific filter params are not present
        const lastCallArgs = mockGetScans.mock.calls[mockGetScans.mock.calls.length - 1][0];
        expect(lastCallArgs).not.toHaveProperty('scan_type');
        expect(lastCallArgs).not.toHaveProperty('status');
      });
    });
  });

  describe('Pagination Functionality', () => {
    it('should be on page 1 initially and call getScans with page 1', () => {
      mockGetScans.mockResolvedValue({ items: mockScans.slice(0, 5), total: mockScans.length, page: 1, limit: 5, totalPages: 2 });
      renderWithClient(queryClient, <ScanList />);
      expect(mockGetScans).toHaveBeenCalledWith(expect.objectContaining({ page: 1, limit: 10 })); // Default limit is 10 from component
    });

    it('should go to the next page when Next button is clicked', async () => {
      mockGetScans.mockResolvedValueOnce({ items: mockScans.slice(0, 5), total: mockScans.length, page: 1, limit: 5, totalPages: 3 });
      renderWithClient(queryClient, <ScanList />);
      
      // Wait for initial load
      await screen.findByText(mockScans[0].id.toString());

      mockGetScans.mockClear();
      mockGetScans.mockResolvedValueOnce({ items: mockScans.slice(5, 10), total: mockScans.length, page: 2, limit: 5, totalPages: 3 });

      const nextButton = screen.getByRole('button', { name: /next page/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(mockGetScans).toHaveBeenCalledWith(expect.objectContaining({ page: 2 }));
      });
    });

    it('should go to the previous page when Previous button is clicked', async () => {
      // Start on page 1, go to page 2, then go back to page 1
      mockGetScans.mockResolvedValueOnce({ items: mockScans.slice(0, 5), total: mockScans.length, page: 1, limit: 5, totalPages: 3 });
      renderWithClient(queryClient, <ScanList />); 
      await screen.findByText(mockScans[0].id.toString()); // Wait for initial load (page 1)

      // Go to page 2
      mockGetScans.mockClear();
      mockGetScans.mockResolvedValueOnce({ items: mockScans.slice(5, 10), total: mockScans.length, page: 2, limit: 5, totalPages: 3 });
      const nextButton = screen.getByRole('button', { name: /next page/i });
      fireEvent.click(nextButton);
      await screen.findByText(mockScans[5].id.toString()); // Wait for page 2 to load

      // Now, go back to page 1
      mockGetScans.mockClear();
      mockGetScans.mockResolvedValueOnce({ items: mockScans.slice(0, 5), total: mockScans.length, page: 1, limit: 5, totalPages: 3 });
      const prevButton = screen.getByRole('button', { name: /previous page/i });
      fireEvent.click(prevButton);

      await waitFor(() => {
        expect(mockGetScans).toHaveBeenCalledWith(expect.objectContaining({ page: 1 }));
      });
    });

    it('should disable Previous button on the first page', async () => {
      mockGetScans.mockResolvedValue({ items: mockScans.slice(0, 5), total: mockScans.length, page: 1, limit: 5, totalPages: 2 });
      renderWithClient(queryClient, <ScanList />);
      await screen.findByText(mockScans[0].id.toString()); // Wait for content

      const prevButton = screen.getByRole('button', { name: /previous page/i });
      expect(prevButton).toBeDisabled();
    });

    it('should disable Next button on the last page', async () => {
      // Mock getScans to return data for the last page (e.g., page 2 of 2)
      mockGetScans.mockResolvedValue({ items: mockScans.slice(5, 10), total: mockScans.length, page: 2, limit: 5, totalPages: 2 });
      renderWithClient(queryClient, <ScanList />); 
      // The component will fetch with page 1 by default, then we'd need to navigate to page 2.
      // Or, more simply, ensure the initial fetch reflects being on the last page.
      // The ScanList uses useSearchParams to get initial page, defaulting to 1.
      // For this test, we'll rely on the mock response indicating it's the last page.
      // We need to ensure the component's internal state reflects page 2.
      // A better way: Render, let it fetch page 1. If totalPages is 1, next is disabled.
      // If totalPages > 1, click next until last page.

      // Simpler: Mock the initial load to be the last page.
      // The component's `currentPage` state is driven by `useSearchParams` or defaults to 1.
      // The `getScans` mock will determine `totalPages`.
      // Let's ensure the component renders and processes this initial state correctly.
      await screen.findByText(mockScans[5].id.toString()); // Wait for content of page 2 to render
      
      const nextButton = screen.getByRole('button', { name: /next page/i });
      expect(nextButton).toBeDisabled();
    });

    it('should fetch data for the entered page number', async () => {
      mockGetScans.mockResolvedValueOnce({ items: mockScans.slice(0, 5), total: mockScans.length, page: 1, limit: 5, totalPages: 5 });
      renderWithClient(queryClient, <ScanList />);
      await screen.findByText(mockScans[0].id.toString());

      mockGetScans.mockClear();
      mockGetScans.mockResolvedValueOnce({ items: mockScans.slice(10, 15), total: mockScans.length, page: 3, limit: 5, totalPages: 5 });

      const pageInput = screen.getByRole('spinbutton', { name: /current page/i });
      fireEvent.change(pageInput, { target: { value: '3' } });
      // The component might debounce or require a blur/enter press. Let's assume change is enough or use fireEvent.blur if needed.
      // For this test, we'll assume the component refetches on valid input change that results in a different page.
      // In ScanList.tsx, onPageChange is called, which updates query params and triggers refetch.

      await waitFor(() => {
        expect(mockGetScans).toHaveBeenCalledWith(expect.objectContaining({ page: 3 }));
      });
    });
  });

  // TODO: Add tests for filtering
  // TODO: Add tests for pagination
});
