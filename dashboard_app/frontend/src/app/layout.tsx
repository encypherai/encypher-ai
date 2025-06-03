import type { Metadata } from 'next';
import './globals.css';
import ClientProviders from './client-providers';

export const metadata: Metadata = {
  title: 'EncypherAI Dashboard',
  description: 'Compliance Readiness Dashboard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ClientProviders>
          {children}
        </ClientProviders>
      </body>
    </html>
  );
}
