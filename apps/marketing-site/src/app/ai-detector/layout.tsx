import { ReactNode } from 'react';
import type { Metadata } from 'next';
import { generateMetadata as buildMetadata } from '@/lib/seo';

export const metadata: Metadata = buildMetadata(
  'Better Than AI Detectors: Cryptographic Proof | Encypher',
  'AI detectors provide 26% accuracy with high false positives. Encypher provides cryptographic proof with 100% accuracy and zero false positives. Mathematical certainty, not statistical guessing.',
  '/ai-detector',
  undefined,
  ['AI detector', 'AI detection tool', 'AI content detection', 'detect AI content', 'AI verification']
);

export default function AIDetectorLayout({
  children,
}: {
  children: ReactNode;
}) {
  return <>{children}</>;
}
