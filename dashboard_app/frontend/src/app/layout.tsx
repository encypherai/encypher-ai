import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'EncypherAI Dashboard',
  description: 'Compliance Readiness Dashboard',
};

'use client';

import { useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { AuthProvider } from '@/lib/auth';
import { NotificationProvider } from '@/lib/notifications';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Create a client for React Query
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
      },
    },
  }));

  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <QueryClientProvider client={queryClient}>
          <NotificationProvider>
            <AuthProvider>
              {children}
            </AuthProvider>
          </NotificationProvider>
          <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
      </body>
    </html>
  );
}
