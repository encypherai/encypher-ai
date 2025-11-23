import { Metadata } from 'next';
import { redirect } from 'next/navigation';
import { getPublisherMetadata } from '@/lib/seo';

export const metadata: Metadata = getPublisherMetadata();

export default function PublishersPage() {
  redirect('/solutions/publishers');
}
