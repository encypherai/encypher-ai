import { ReactNode } from 'react';
import type { Metadata } from 'next';
import { generateMetadata as buildMetadata } from '@/lib/seo';

export const metadata: Metadata = buildMetadata(
  'Licensing & Pricing | Encypher',
  'Flexible licensing from WordPress plugins to enterprise infrastructure. Success-based models aligned with your outcomes. Contact us to discuss your specific needs.',
  '/licensing'
);

export default function LicensingLayout({
  children,
}: {
  children: ReactNode;
}) {
  return <>{children}</>;
}
