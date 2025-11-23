import { ReactNode } from 'react';
import type { Metadata } from 'next';
import { getEnterpriseMetadata } from '@/lib/seo';

export const metadata: Metadata = getEnterpriseMetadata();

export default function EnterprisesLayout({
  children,
}: {
  children: ReactNode;
}) {
  return <>{children}</>;
}
