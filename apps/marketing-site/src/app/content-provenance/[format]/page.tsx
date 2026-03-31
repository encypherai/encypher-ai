import { notFound } from 'next/navigation';
import { getFormatBySlug, getAllFormatSlugs, categoryInfo } from '@/data/formats';
import { FormatPage } from '@/components/content/FormatPage';
import { getFormatPageMetadata } from '@/lib/seo';
import type { Metadata } from 'next';

// Generate static params for all 33 formats (generates 33 static pages at build)
export function generateStaticParams() {
  return getAllFormatSlugs().map(slug => ({ format: slug }));
}

// Generate metadata per format
export async function generateMetadata({
  params,
}: {
  params: { format: string };
}): Promise<Metadata> {
  const resolvedParams = await Promise.resolve(params);
  const format = getFormatBySlug(resolvedParams.format);
  if (!format) return {};
  return getFormatPageMetadata(format.name, format.mimeType, format.category);
}

export default async function FormatPageRoute({
  params,
}: {
  params: { format: string };
}) {
  const resolvedParams = await Promise.resolve(params);
  const format = getFormatBySlug(resolvedParams.format);
  if (!format) notFound();
  const info = categoryInfo[format.category];
  return <FormatPage format={format} categoryInfo={info} />;
}
