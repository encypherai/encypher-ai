import { Metadata } from 'next';
import { permanentRedirect } from 'next/navigation';
import { getAILabMetadata } from '@/lib/seo';

export const metadata: Metadata = getAILabMetadata();

export default function AIPage() {
  permanentRedirect('/solutions/ai-companies');
}
