import type { Metadata } from 'next';
import '@encypher/design-system/styles';
import './globals.css';

export const metadata: Metadata = {
  title: 'Dashboard - Encypher',
  description: 'Manage your Encypher API keys, usage, and content authentication',
  robots: {
    index: false, // Don't index dashboard pages
    follow: false,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased bg-background">
        {children}
      </body>
    </html>
  );
}
