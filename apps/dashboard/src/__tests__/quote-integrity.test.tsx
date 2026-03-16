import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// -- Mocks -------------------------------------------------------------------

// Mock next-auth/react
vi.mock('next-auth/react', () => ({
  useSession: () => ({
    data: {
      user: { name: 'Test', email: 'test@test.com', accessToken: 'tok', tier: 'free' },
    },
    status: 'authenticated',
  }),
  signOut: vi.fn(),
  SessionProvider: ({ children }: { children: React.ReactNode }) => children,
}));

// Mock next/navigation
vi.mock('next/navigation', () => ({
  usePathname: () => '/quote-integrity',
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
}));

// Mock next/image
vi.mock('next/image', () => ({
  default: (props: Record<string, unknown>) => {
    // eslint-disable-next-line @next/next/no-img-element
    const { priority, ...rest } = props;
    return <img {...(rest as React.ImgHTMLAttributes<HTMLImageElement>)} />;
  },
}));

// Mock OrganizationContext
vi.mock('../contexts/OrganizationContext', () => ({
  useOrganization: () => ({ activeOrganization: null, organizations: [], setActiveOrg: vi.fn() }),
}));

// Mock sonner
const toastErrorSpy = vi.fn();
vi.mock('sonner', () => ({
  toast: { error: (...args: unknown[]) => toastErrorSpy(...args), success: vi.fn(), info: vi.fn() },
}));

// Stub DashboardLayout to avoid deep rendering of sidebar/nav
vi.mock('../components/layout/DashboardLayout', () => ({
  DashboardLayout: ({ children }: { children: React.ReactNode }) => <div data-testid="layout">{children}</div>,
}));

// Mock API client
const verifyQuoteIntegritySpy = vi.fn();
vi.mock('../lib/api', () => ({
  default: {
    verifyQuoteIntegrity: (...args: unknown[]) => verifyQuoteIntegritySpy(...args),
    getSetupStatus: vi.fn().mockResolvedValue({ setup_completed: true }),
    isSuperAdmin: vi.fn().mockResolvedValue(false),
  },
}));

// -- Helpers ------------------------------------------------------------------

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

async function renderPage() {
  // Dynamic import so mocks are applied first
  const { default: QuoteIntegrityPage } = await import('../app/quote-integrity/page');
  return render(<QuoteIntegrityPage />, { wrapper: createWrapper() });
}

// -- Tests --------------------------------------------------------------------

describe('QuoteIntegrityPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the form elements', async () => {
    await renderPage();

    expect(screen.getByTestId('qi-quote')).toBeInTheDocument();
    expect(screen.getByTestId('qi-attribution')).toBeInTheDocument();
    expect(screen.getByTestId('qi-submit')).toBeInTheDocument();
    expect(screen.getByTestId('qi-placeholder')).toHaveTextContent(
      'Enter a quote and click Verify to check its integrity'
    );
  });

  it('displays "Accurate" verdict (green)', async () => {
    verifyQuoteIntegritySpy.mockResolvedValueOnce({
      verdict: 'accurate',
      similarity_score: 0.98,
      confidence: 'high',
      explanation: 'Exact match found.',
      matched_excerpt: 'The quick brown fox.',
      matched_document: { id: 'doc1', org_id: 'org1' },
      merkle_proof: null,
    });

    await renderPage();

    fireEvent.change(screen.getByTestId('qi-quote'), { target: { value: 'The quick brown fox.' } });
    fireEvent.change(screen.getByTestId('qi-attribution'), { target: { value: 'Reuters' } });
    fireEvent.click(screen.getByTestId('qi-submit'));

    await waitFor(() => expect(screen.getByTestId('qi-verdict')).toBeInTheDocument());

    expect(screen.getByTestId('qi-verdict')).toHaveTextContent('Accurate');
    expect(screen.getByTestId('qi-score')).toHaveTextContent('98%');
    expect(screen.getByTestId('qi-confidence')).toHaveTextContent('high');
    expect(screen.getByTestId('qi-excerpt')).toHaveTextContent('The quick brown fox.');
    expect(screen.getByTestId('qi-explanation')).toHaveTextContent('Exact match found.');
  });

  it('displays "Approximate" verdict (yellow)', async () => {
    verifyQuoteIntegritySpy.mockResolvedValueOnce({
      verdict: 'approximate',
      similarity_score: 0.72,
      confidence: 'medium',
      explanation: 'Close but not exact.',
      matched_excerpt: 'A fast brown fox.',
      matched_document: null,
      merkle_proof: null,
    });

    await renderPage();

    fireEvent.change(screen.getByTestId('qi-quote'), { target: { value: 'Some quote' } });
    fireEvent.change(screen.getByTestId('qi-attribution'), { target: { value: 'AP' } });
    fireEvent.click(screen.getByTestId('qi-submit'));

    await waitFor(() => expect(screen.getByTestId('qi-verdict')).toBeInTheDocument());
    expect(screen.getByTestId('qi-verdict')).toHaveTextContent('Approximate');
    expect(screen.getByTestId('qi-score')).toHaveTextContent('72%');
  });

  it('displays "Hallucinated" verdict (red)', async () => {
    verifyQuoteIntegritySpy.mockResolvedValueOnce({
      verdict: 'hallucinated',
      similarity_score: 0.12,
      confidence: 'high',
      explanation: 'No matching content found.',
      matched_excerpt: null,
      matched_document: null,
      merkle_proof: null,
    });

    await renderPage();

    fireEvent.change(screen.getByTestId('qi-quote'), { target: { value: 'Fake content' } });
    fireEvent.change(screen.getByTestId('qi-attribution'), { target: { value: 'Nobody' } });
    fireEvent.click(screen.getByTestId('qi-submit'));

    await waitFor(() => expect(screen.getByTestId('qi-verdict')).toBeInTheDocument());
    expect(screen.getByTestId('qi-verdict')).toHaveTextContent('Hallucinated');
    expect(screen.getByTestId('qi-score')).toHaveTextContent('12%');
  });

  it('displays "Unverifiable" verdict (gray)', async () => {
    verifyQuoteIntegritySpy.mockResolvedValueOnce({
      verdict: 'unverifiable',
      similarity_score: 0,
      confidence: 'low',
      explanation: 'Source not in the registry.',
      matched_excerpt: null,
      matched_document: null,
      merkle_proof: null,
    });

    await renderPage();

    fireEvent.change(screen.getByTestId('qi-quote'), { target: { value: 'Unknown quote' } });
    fireEvent.change(screen.getByTestId('qi-attribution'), { target: { value: 'Unknown' } });
    fireEvent.click(screen.getByTestId('qi-submit'));

    await waitFor(() => expect(screen.getByTestId('qi-verdict')).toBeInTheDocument());
    expect(screen.getByTestId('qi-verdict')).toHaveTextContent('Unverifiable');
  });

  it('submit button triggers API call with correct params', async () => {
    verifyQuoteIntegritySpy.mockResolvedValueOnce({
      verdict: 'accurate',
      similarity_score: 1,
      confidence: 'high',
      explanation: 'Match.',
      matched_excerpt: null,
      matched_document: null,
      merkle_proof: null,
    });

    await renderPage();

    fireEvent.change(screen.getByTestId('qi-quote'), { target: { value: 'Hello world' } });
    fireEvent.change(screen.getByTestId('qi-attribution'), { target: { value: 'AP News' } });
    fireEvent.click(screen.getByTestId('qi-submit'));

    await waitFor(() => expect(verifyQuoteIntegritySpy).toHaveBeenCalledTimes(1));
    expect(verifyQuoteIntegritySpy).toHaveBeenCalledWith({
      quote: 'Hello world',
      attribution: 'AP News',
    });
  });

  it('shows toast on error', async () => {
    verifyQuoteIntegritySpy.mockRejectedValueOnce(new Error('Server error'));

    await renderPage();

    fireEvent.change(screen.getByTestId('qi-quote'), { target: { value: 'Broken' } });
    fireEvent.change(screen.getByTestId('qi-attribution'), { target: { value: 'Source' } });
    fireEvent.click(screen.getByTestId('qi-submit'));

    await waitFor(() => expect(toastErrorSpy).toHaveBeenCalledWith('Server error'));
  });
});
