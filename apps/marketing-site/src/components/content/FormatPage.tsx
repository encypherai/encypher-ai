import React from 'react';
import Link from 'next/link';
import Script from 'next/script';
import { ArrowRight, FileCheck, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import type { FormatData, categoryInfo as CategoryInfoType } from '@/data/formats';

// NOTE: Breadcrumbs component is at src/components/seo/Breadcrumbs.tsx

interface FormatPageProps {
  format: FormatData;
  categoryInfo: typeof CategoryInfoType[keyof typeof CategoryInfoType];
}

export function FormatPage({ format, categoryInfo }: FormatPageProps) {
  const categorySlugMap: Record<string, string> = {
    image: 'images',
    audio: 'audio-video',
    video: 'audio-video',
    document: 'text',
    font: 'text',
  };
  const categoryClusterSlug = categorySlugMap[format.category] || 'text';

  const techArticleSchema = {
    "@context": "https://schema.org",
    "@type": "TechArticle",
    "headline": `${format.name} Content Provenance: Sign, Embed, Verify`,
    "description": format.description,
    "url": `https://encypher.com/content-provenance/${format.slug}`,
    "author": { "@type": "Organization", "name": "Encypher", "url": "https://encypher.com" },
    "publisher": { "@type": "Organization", "name": "Encypher", "url": "https://encypher.com" },
    "datePublished": new Date().toISOString(),
    "mainEntityOfPage": { "@type": "WebPage", "@id": `https://encypher.com/content-provenance/${format.slug}` },
  };

  return (
    <>
      <AISummary
        title={`${format.name} Content Provenance`}
        whatWeDo={`Encypher signs ${format.name} files with C2PA manifests, embedding cryptographic proof of origin directly into the ${format.category} file. ${format.embeddingMethod}. Verification is free.`}
        whoItsFor={`Content creators and publishers who produce ${format.name} files and need provenance infrastructure. ${format.useCases.join(', ')}.`}
        keyDifferentiator={`C2PA manifest embedding via ${format.containerType}. Verification pipeline: ${format.verificationPipeline === 'c2pa-python-native' ? 'c2pa-python (native support)' : 'custom JUMBF/COSE structural verification'}.`}
        primaryValue={`Embed proof of origin into ${format.name} files. Sign at creation, verify anywhere, free. Part of 31 media types supported by Encypher's content provenance infrastructure.`}
        pagePath={`/content-provenance/${format.slug}`}
        pageType="WebPage"
      />

      <Script
        id={`tech-article-${format.slug}`}
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticleSchema) }}
      />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Content Provenance', href: '/content-provenance' },
          { name: categoryInfo.name, href: `/content-provenance/${categoryClusterSlug}` },
          { name: format.name, href: `/content-provenance/${format.slug}` },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          {format.name} Content Provenance
        </h1>
        <p className="text-lg text-muted-foreground mb-8">
          Sign, embed, and verify C2PA manifests in {format.name} files ({format.extensions.join(', ')})
        </p>

        {/* Overview */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">What Is {format.name} Provenance?</h2>
          <p className="text-base leading-relaxed mb-4">{format.description}</p>
          <p className="text-base leading-relaxed">
            With Encypher, {format.name} files carry their own cryptographic proof of origin. A{' '}
            <Link href="/c2pa-standard" className="text-[#2a87c4] hover:underline">C2PA manifest</Link>{' '}
            is embedded directly into the file, recording who created it, when, and whether it has been modified.
            Anyone can{' '}
            <Link href="/content-provenance/verification" className="text-[#2a87c4] hover:underline">verify</Link>{' '}
            a signed {format.name} file for free, without authentication.
          </p>
        </section>

        {/* How it works */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">How C2PA Manifests Are Embedded in {format.name} Files</h2>
          <div className="bg-muted/50 rounded-lg p-6 mb-4">
            <dl className="space-y-3">
              <div>
                <dt className="font-medium">MIME Type</dt>
                <dd className="text-muted-foreground font-mono text-sm">{format.mimeType}</dd>
              </div>
              <div>
                <dt className="font-medium">File Extensions</dt>
                <dd className="text-muted-foreground">{format.extensions.join(', ')}</dd>
              </div>
              <div>
                <dt className="font-medium">Embedding Method</dt>
                <dd className="text-muted-foreground">{format.embeddingMethod}</dd>
              </div>
              <div>
                <dt className="font-medium">Container Type</dt>
                <dd className="text-muted-foreground">{format.containerType}</dd>
              </div>
              <div>
                <dt className="font-medium">Verification Pipeline</dt>
                <dd className="text-muted-foreground">
                  {format.verificationPipeline === 'c2pa-python-native'
                    ? 'c2pa-python (native C2PA library support)'
                    : 'Custom JUMBF/COSE structural verification (Encypher implementation)'}
                </dd>
              </div>
            </dl>
          </div>
          <p className="text-base leading-relaxed">
            The C2PA manifest contains a JUMBF (JPEG Universal Metadata Box Format) store with COSE-signed claims.
            For {format.name} files, the manifest is stored using {format.embeddingMethod.toLowerCase()}.
            The signing process does not alter the {format.category} content itself. The manifest is metadata,
            not a modification of the {format.category === 'image' ? 'pixels' : format.category === 'audio' ? 'audio samples' : format.category === 'video' ? 'video frames' : 'content'}.
          </p>
        </section>

        {/* Use cases */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Use Cases for {format.name} Provenance</h2>
          <ul className="space-y-2">
            {format.useCases.map(useCase => (
              <li key={useCase} className="flex items-start gap-2">
                <FileCheck className="h-5 w-5 text-[#2a87c4] mt-0.5 flex-shrink-0" />
                <span>{useCase}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* How to sign */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">How to Sign {format.name} Content with Encypher</h2>
          <p className="text-base leading-relaxed mb-4">
            {format.name} signing is available at the Enterprise tier through the unified /sign/media API endpoint.
            Upload your {format.name} file, and the API returns a signed copy with an embedded C2PA manifest.
          </p>
          <div className="bg-[#1B2F50] text-white rounded-lg p-6 font-mono text-sm overflow-x-auto">
            <pre>{`curl -X POST https://api.encypher.com/api/v1/sign/media \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -F "file=@example${format.extensions[0]}" \\
  -F "title=My ${format.name} Content" \\
  -F "action=c2pa.created" \\
  -o signed${format.extensions[0]}`}</pre>
          </div>
        </section>

        {/* Verification */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Verify {format.name} Provenance (Free)</h2>
          <p className="text-base leading-relaxed mb-4">
            Verification is free and requires no authentication. Any third party can verify a signed {format.name} file
            to confirm its origin, check for tampering, and read the embedded rights information.
          </p>
          <div className="flex flex-col sm:flex-row gap-3">
            <Button asChild style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/tools/verify">
                <span className="flex items-center">
                  <Eye className="mr-2 h-4 w-4" />
                  Verify a {format.name} File
                </span>
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/platform">
                <span className="flex items-center">
                  API Documentation <ArrowRight className="ml-2 h-4 w-4" />
                </span>
              </Link>
            </Button>
          </div>
        </section>

        {/* Related formats */}
        {format.relatedFormats.length > 0 && (
          <section className="mb-12">
            <h2 className="text-2xl font-semibold mb-4">Related Formats</h2>
            <div className="flex flex-wrap gap-2">
              {format.relatedFormats.map(slug => (
                <Link
                  key={slug}
                  href={`/content-provenance/${slug}`}
                  className="px-3 py-1.5 bg-muted rounded-md text-sm hover:bg-muted/80 transition-colors"
                >
                  {slug.toUpperCase()} Provenance
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Back to pillar */}
        <section className="border-t pt-8">
          <h2 className="text-xl font-semibold mb-3">Learn More About Content Provenance</h2>
          <div className="flex flex-col sm:flex-row gap-3">
            <Link href="/content-provenance" className="text-[#2a87c4] hover:underline flex items-center">
              What Is Content Provenance? <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
            <Link href="/c2pa-standard/media-types" className="text-[#2a87c4] hover:underline flex items-center">
              All 31 Supported Media Types <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
            <Link href="/cryptographic-watermarking" className="text-[#2a87c4] hover:underline flex items-center">
              Cryptographic Watermarking <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
          </div>
        </section>
      </div>
    </>
  );
}

export default FormatPage;
