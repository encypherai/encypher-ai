'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useSearchParams } from 'next/navigation';

interface DemoModeContextValue {
  isDemoMode: boolean;
  setDemoMode: (value: boolean) => void;
}

const DemoModeContext = createContext<DemoModeContextValue>({
  isDemoMode: false,
  setDemoMode: () => {},
});

export function DemoModeProvider({ children }: { children: ReactNode }) {
  const searchParams = useSearchParams();
  const [isDemoMode, setDemoMode] = useState(false);

  useEffect(() => {
    if (searchParams.get('demo') === 'true') {
      setDemoMode(true);
    }
  }, [searchParams]);

  return (
    <DemoModeContext.Provider value={{ isDemoMode, setDemoMode }}>
      {children}
    </DemoModeContext.Provider>
  );
}

export function useDemoMode() {
  return useContext(DemoModeContext);
}

// Realistic demo data: mid-sized publisher, 60 days into implementation
export const DEMO_STATS = {
  total_api_calls: 2847,
  total_documents_signed: 423,
  total_verifications: 156,
  success_rate: 98.2,
  avg_response_time_ms: 142,
  period_start: new Date(Date.now() - 30 * 86400000).toISOString(),
  period_end: new Date().toISOString(),
};

// Prior 60-day stats (so prior 30d = 60d total - 30d total)
export const DEMO_STATS_60D = {
  total_api_calls: 3535, // prior 30d = 688
  total_documents_signed: 647, // prior 30d = 224
  total_verifications: 198, // prior 30d = 42
  success_rate: 97.1,
  avg_response_time_ms: 155,
  period_start: new Date(Date.now() - 60 * 86400000).toISOString(),
  period_end: new Date().toISOString(),
};

// Sparkline data: 30 days of API calls with growth curve
// Use seeded values to avoid hydration mismatch (Math.random not stable across server/client)
const API_SPARKLINE_VALUES = [42, 55, 48, 61, 53, 67, 58, 72, 64, 78, 69, 84, 75, 89, 81, 95, 87, 102, 93, 108, 99, 115, 106, 121, 112, 128, 118, 135, 124, 140];
export const DEMO_SPARKLINE = API_SPARKLINE_VALUES.map((count, i) => ({
  date: new Date(Date.now() - (29 - i) * 86400000).toISOString().split('T')[0],
  count,
}));

// Documents signed sparkline: slower, steadier growth
const DOCS_SPARKLINE_VALUES = [8, 10, 9, 12, 11, 13, 12, 14, 13, 15, 14, 16, 15, 17, 14, 16, 15, 18, 16, 17, 15, 19, 17, 18, 16, 20, 18, 19, 17, 21];
export const DEMO_DOCS_SPARKLINE = DOCS_SPARKLINE_VALUES.map((count, i) => ({
  date: new Date(Date.now() - (29 - i) * 86400000).toISOString().split('T')[0],
  count,
}));

// Demo activity feed events
export const DEMO_ACTIVITY = [
  { type: 'sign', title: 'Article signed: "AI Content Licensing in 2026"', time: '2 hours ago' },
  { type: 'verify', title: 'Verification from OpenAI crawler', time: '4 hours ago' },
  { type: 'sign', title: 'Article signed: "Publisher Rights Under EU AI Act"', time: '6 hours ago' },
  { type: 'api', title: 'API key "Production CMS" used', time: '8 hours ago' },
  { type: 'verify', title: 'Verification from Perplexity bot', time: '12 hours ago' },
  { type: 'sign', title: 'Article signed: "Formal Notice Best Practices"', time: '1 day ago' },
  { type: 'verify', title: 'Verification from Google-Extended', time: '1 day ago' },
  { type: 'api', title: 'API key "WordPress Plugin" used', time: '1 day ago' },
];

export const DEMO_API_KEYS = [
  {
    id: 'demo-key-1',
    name: 'Production CMS',
    is_revoked: false,
    created_at: new Date(Date.now() - 58 * 86400000).toISOString(),
    last_used_at: new Date(Date.now() - 3600000).toISOString(),
    permissions: ['sign', 'verify', 'read'],
  },
  {
    id: 'demo-key-2',
    name: 'Staging',
    is_revoked: false,
    created_at: new Date(Date.now() - 45 * 86400000).toISOString(),
    last_used_at: new Date(Date.now() - 86400000).toISOString(),
    permissions: ['sign', 'verify', 'read'],
  },
  {
    id: 'demo-key-3',
    name: 'WordPress Plugin',
    is_revoked: false,
    created_at: new Date(Date.now() - 12 * 86400000).toISOString(),
    last_used_at: new Date(Date.now() - 7200000).toISOString(),
    permissions: ['sign', 'verify'],
  },
];

export const DEMO_SETUP_STATUS = {
  workflow_category: 'media_publishing',
  dashboard_layout: 'publisher',
  rollout_progress: 6,
  rollout_total: 6,
  steps_completed: ['api_key', 'first_sign', 'first_verify', 'cms_integration', 'team_invite', 'rights_setup'],
};
