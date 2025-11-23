import type { Metadata } from 'next';
import { generateMetadata, keywords } from '@/lib/seo';

export const metadata: Metadata = generateMetadata(
  'AI Performance Intelligence | Encypher',
  'See which parameters drive viral content. Track every output at sentence-level. One integration covers the entire publisher ecosystem.',
  '/solutions/ai-companies',
  undefined,
  keywords.aiLabs
);
