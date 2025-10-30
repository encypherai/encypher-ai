import type { Metadata } from 'next';
import '@encypher/design-system/styles';
import './globals.css';

export const metadata: Metadata = {
  title: 'Encypher - Cryptographic Content Authentication',
  description: 'Enterprise-grade content authentication and verification powered by cryptographic signatures.',
  keywords: ['content authentication', 'cryptographic signatures', 'C2PA', 'provenance', 'verification'],
  authors: [{ name: 'Encypher Team' }],
  openGraph: {
    title: 'Encypher - Cryptographic Content Authentication',
    description: 'Enterprise-grade content authentication and verification',
    url: 'https://encypherai.com',
    siteName: 'Encypher',
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Encypher - Cryptographic Content Authentication',
    description: 'Enterprise-grade content authentication and verification',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
