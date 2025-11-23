import { Metadata } from 'next';
import { redirect } from 'next/navigation';
import { getAILabMetadata } from '@/lib/seo';

export const metadata: Metadata = getAILabMetadata();

export default function AIPage() {
  redirect('/solutions/ai-companies');
}
