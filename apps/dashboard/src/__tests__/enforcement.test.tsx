import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// -- Mocks --------------------------------------------------------------------

// Mock next-auth/react
vi.mock('next-auth/react', () => ({
  useSession: () => ({
    data: {
      user: {
        name: 'Test User',
        email: 'test@example.com',
        accessToken: 'test-token-123',
        tier: 'enterprise',
      },
    },
    status: 'authenticated',
  }),
  signOut: vi.fn(),
}));

// Mock next/navigation
const mockPush = vi.fn();
const mockPathname = '/enforcement';
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush, replace: vi.fn() }),
  usePathname: () => mockPathname,
  useParams: () => ({ noticeId: 'notice-001' }),
}));

// Mock next/image
vi.mock('next/image', () => ({
  default: (props: Record<string, unknown>) => {
    const { priority, fill, ...rest } = props;
    return <img {...rest} />;
  },
}));

// Mock OrganizationContext
vi.mock('../contexts/OrganizationContext', () => ({
  useOrganization: () => ({
    activeOrganization: { id: 'org-1', name: 'Test Org', dashboard_layout: 'enterprise' },
    organizations: [],
    setActiveOrganization: vi.fn(),
  }),
}));

// Mock NotificationCenter
vi.mock('../components/NotificationCenter', () => ({
  NotificationCenter: () => <div data-testid="notification-center" />,
}));

// Mock MobileNav
vi.mock('../components/MobileNav', () => ({
  MobileNav: () => null,
}));

// Mock OrganizationSwitcher
vi.mock('../components/OrganizationSwitcher', () => ({
  OrganizationSwitcher: () => null,
}));

// Mock SetupWizard
vi.mock('../components/onboarding/SetupWizard', () => ({
  SetupWizard: () => null,
}));

// Mock ThemeContext
vi.mock('../contexts/ThemeContext', () => ({
  ThemeToggleButton: () => <button>Theme</button>,
}));

// Mock apiClient
const mockNotices = [
  {
    id: 'notice-001',
    organization_id: 'org-1',
    target_entity_name: 'AI Corp',
    target_contact_email: 'legal@aicorp.com',
    recipient_entity: 'AI Corp',
    recipient_contact: 'legal@aicorp.com',
    notice_type: 'cease_and_desist',
    violation_type: 'cease_and_desist',
    status: 'delivered',
    notice_text: 'You are hereby notified...',
    notice_hash: 'abc123def456abc123def456abc123def456abc123def456abc123def456abcd', // pragma: allowlist secret
    delivered_at: '2026-03-10T12:00:00Z',
    delivery_method: 'email',
    created_at: '2026-03-09T10:00:00Z',
  },
  {
    id: 'notice-002',
    organization_id: 'org-1',
    target_entity_name: 'DataBot Inc',
    target_contact_email: null,
    recipient_entity: 'DataBot Inc',
    recipient_contact: null,
    notice_type: 'licensing_notice',
    violation_type: 'licensing_notice',
    status: 'draft',
    notice_text: 'Please be advised...',
    notice_hash: null,
    delivered_at: null,
    created_at: '2026-03-12T09:00:00Z',
  },
];

const mockNoticeDetail = {
  ...mockNotices[0],
  evidence_chain: [
    {
      id: 'ev-1',
      event_type: 'notice_created',
      event_data: { method: 'dashboard' },
      event_hash: 'hash-ev-1',
      previous_hash: null,
      created_at: '2026-03-09T10:00:00Z',
    },
    {
      id: 'ev-2',
      event_type: 'notice_delivered',
      event_data: { delivery_method: 'email' },
      event_hash: 'hash-ev-2',
      previous_hash: 'hash-ev-1',
      created_at: '2026-03-10T12:00:00Z',
    },
  ],
};

const mockEvidencePackage = {
  notice: {
    id: 'notice-001',
    notice_hash: 'abc123def456abc123def456abc123def456abc123def456abc123def456abcd', // pragma: allowlist secret
    notice_text: 'You are hereby notified...',
    target_entity_name: 'AI Corp',
    status: 'delivered',
    delivered_at: '2026-03-10T12:00:00Z',
  },
  evidence_chain: [
    {
      id: 'ev-1',
      event_type: 'notice_created',
      event_hash: 'hash-ev-1',
      previous_hash: null,
      created_at: '2026-03-09T10:00:00Z',
      event_data: null,
      hash_verified: true,
    },
    {
      id: 'ev-2',
      event_type: 'notice_delivered',
      event_hash: 'hash-ev-2',
      previous_hash: 'hash-ev-1',
      created_at: '2026-03-10T12:00:00Z',
      event_data: { delivery_method: 'email' },
      hash_verified: true,
    },
  ],
  chain_integrity_verified: true,
  package_hash: 'pkg-hash-abc123',
  generated_at: '2026-03-15T00:00:00Z',
};

vi.mock('../lib/api', () => ({
  default: {
    listNotices: vi.fn().mockResolvedValue(mockNotices),
    getNoticeDetail: vi.fn().mockResolvedValue(mockNoticeDetail),
    getNoticeEvidence: vi.fn().mockResolvedValue(mockEvidencePackage),
    downloadEvidencePackagePdf: vi.fn().mockResolvedValue(undefined),
    isSuperAdmin: vi.fn().mockResolvedValue(false),
    getSetupStatus: vi.fn().mockResolvedValue({ setup_completed: true, dashboard_layout: 'enterprise' }),
  },
}));

// -- Helpers ------------------------------------------------------------------

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

// -- Tests: Enforcement list page ---------------------------------------------

describe('Enforcement Dashboard Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders summary cards and notice table with mock data', async () => {
    // Dynamic import to ensure mocks are set up first
    const { default: EnforcementPage } = await import('../app/enforcement/page');

    const Wrapper = createWrapper();
    render(
      <Wrapper>
        <EnforcementPage />
      </Wrapper>,
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Enforcement Dashboard')).toBeInTheDocument();
    });

    // Summary cards
    await waitFor(() => {
      expect(screen.getByText('Notices Sent')).toBeInTheDocument();
      expect(screen.getByText('Delivery Rate')).toBeInTheDocument();
      expect(screen.getByText('Pending Responses')).toBeInTheDocument();
      expect(screen.getByText('Active Escalations')).toBeInTheDocument();
    });

    // Table rows
    await waitFor(() => {
      expect(screen.getByText('AI Corp')).toBeInTheDocument();
      expect(screen.getByText('DataBot Inc')).toBeInTheDocument();
    });

    // Status badges
    await waitFor(() => {
      expect(screen.getByText('delivered')).toBeInTheDocument();
      expect(screen.getByText('draft')).toBeInTheDocument();
    });

    // Notice type badges
    await waitFor(() => {
      expect(screen.getByText('cease and desist')).toBeInTheDocument();
      expect(screen.getByText('licensing notice')).toBeInTheDocument();
    });
  });
});

// -- Tests: Notice detail page ------------------------------------------------

describe('Notice Detail Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders notice detail with evidence chain timeline', async () => {
    const { default: NoticeDetailPage } = await import('../app/enforcement/[noticeId]/page');

    const Wrapper = createWrapper();
    render(
      <Wrapper>
        <NoticeDetailPage />
      </Wrapper>,
    );

    // Wait for header to appear (AI Corp appears in header + executive summary)
    await waitFor(() => {
      expect(screen.getAllByText('AI Corp').length).toBeGreaterThanOrEqual(1);
    });

    // Notice type and status (appear in header + executive summary)
    await waitFor(() => {
      expect(screen.getAllByText('cease and desist').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('delivered').length).toBeGreaterThanOrEqual(1);
    });

    // Notice content section
    await waitFor(() => {
      expect(screen.getByText('Notice Content')).toBeInTheDocument();
      expect(screen.getByText('You are hereby notified...')).toBeInTheDocument();
    });

    // Evidence chain timeline
    await waitFor(() => {
      expect(screen.getByText('Evidence Chain Timeline')).toBeInTheDocument();
      expect(screen.getByText('notice created')).toBeInTheDocument();
      expect(screen.getByText('notice delivered')).toBeInTheDocument();
    });

    // Executive summary section
    await waitFor(() => {
      expect(screen.getByText('Executive Summary')).toBeInTheDocument();
    });

    // Download button
    await waitFor(() => {
      expect(screen.getByText('Download Evidence Package (PDF)')).toBeInTheDocument();
    });
  });
});
