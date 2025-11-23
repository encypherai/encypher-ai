import type { Metadata } from 'next';
import { generateMetadata, keywords } from '@/lib/seo';

export const metadata: Metadata = generateMetadata(
  'Publisher Content Protection & Licensing | Encypher',
  'From litigation costs to licensing revenue. Court-admissible evidence with 100% accuracy. Track which sentences were used, where, and when.',
  '/solutions/publishers',
  undefined,
  keywords.publishers
);
