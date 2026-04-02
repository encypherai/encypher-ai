import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { ExternalLink } from 'lucide-react';
import AISummary from '@/components/seo/AISummary';
import { ArticleShell } from '@/components/content/ArticleShell';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';
import ConformanceExplorer from './ConformanceExplorer';

export const metadata: Metadata = seoMetadata(
  'C2PA Conformance Explorer: Conformant Products and Implementations | Encypher',
  'Browse all C2PA conformant products and implementations. Search by company, product type, or media format. Live data from the official C2PA conformance program.',
  '/c2pa-standard/conformance',
  undefined,
  undefined,
  'Every C2PA conformant product, searchable. Live data.'
);

export default function ConformancePage() {
  const techArticle = getTechArticleSchema({
    title: 'C2PA Conformance Explorer',
    description: 'Browse all C2PA conformant products and implementations. Live data from the official C2PA conformance program.',
    url: `${siteConfig.url}/c2pa-standard/conformance`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="C2PA Conformance Explorer"
        whatWeDo="Encypher hosts a searchable directory of all C2PA conformant products, sourced live from the official C2PA conformance program. Users can search by company, filter by product type (generator or validator), and filter by media category."
        whoItsFor="Publishers evaluating C2PA adoption who need to verify which products have completed conformance testing. Enterprise buyers requiring standards-compliant tools. Developers building C2PA integrations."
        keyDifferentiator="Live data from the official C2PA conformance list. Every product listed has passed the C2PA conformance testing program, not a self-reported compatibility claim."
        primaryValue="Verify which tools and platforms have earned official C2PA conformance status before making adoption decisions."
        pagePath="/c2pa-standard/conformance"
      />

      <Script
        id="tech-article-conformance"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <ArticleShell path="/c2pa-standard/conformance">
        <Breadcrumbs
          items={[
            { name: 'Home', href: '/' },
            { name: 'C2PA Standard', href: '/c2pa-standard' },
            { name: 'Conformance Explorer', href: '/c2pa-standard/conformance' },
          ]}
        />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          C2PA Conformance Explorer
        </h1>
        <p className="text-lg text-muted-foreground mb-8 max-w-3xl">
          Browse products and implementations that have completed the{' '}
          <a
            href="https://c2pa.org/conformance/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#2a87c4] hover:underline inline-flex items-center gap-0.5"
          >
            C2PA Conformance Program
            <ExternalLink className="h-4 w-4" />
          </a>
          . Conformance testing verifies that a product correctly implements the C2PA
          specification for generating or validating content provenance manifests.
        </p>

        {/* Why conformance matters */}
        <section className="mb-12 bg-muted/30 rounded-lg p-6 border border-border">
          <h2 className="text-xl font-semibold mb-3">Why Conformance Matters</h2>
          <p className="text-base leading-relaxed mb-3">
            Any vendor can claim C2PA support. The conformance program provides independent
            verification. Products that pass conformance testing have demonstrated correct
            manifest generation or validation against the{' '}
            <Link href="/c2pa-standard" className="text-[#2a87c4] hover:underline">
              C2PA specification
            </Link>
            , including proper{' '}
            <Link href="/c2pa-standard/manifest-structure" className="text-[#2a87c4] hover:underline">
              JUMBF/COSE manifest structure
            </Link>
            , certificate chain validation, and format-specific embedding.
          </p>
          <p className="text-base leading-relaxed">
            Publishers and enterprises evaluating content provenance infrastructure should
            require conformance test results rather than accepting self-reported compatibility
            claims. Encypher is actively pursuing C2PA conformance for its Enterprise API.
          </p>
        </section>

        {/* Explorer component */}
        <ConformanceExplorer />

        {/* Context section */}
        <section className="mt-12 border-t border-border pt-8">
          <h2 className="text-xl font-semibold mb-4">Understanding Conformance Categories</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium mb-2">Generators</h3>
              <p className="text-sm text-muted-foreground">
                Products that create C2PA manifests and embed them into content files. A
                conformant generator produces valid JUMBF stores with correctly signed COSE
                claims, proper assertion structures, and format-specific embedding per the
                C2PA specification.
              </p>
            </div>
            <div>
              <h3 className="font-medium mb-2">Validators</h3>
              <p className="text-sm text-muted-foreground">
                Products that read, parse, and verify C2PA manifests from content files.
                A conformant validator correctly extracts JUMBF stores, validates COSE
                signatures against certificate chains, checks claim integrity, and reports
                manifest status accurately.
              </p>
            </div>
          </div>
        </section>

        {/* Related pages */}
        <section className="mt-8 border-t border-border pt-8">
          <h2 className="text-xl font-semibold mb-3">Learn More</h2>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              href="/c2pa-standard"
              className="text-[#2a87c4] hover:underline"
            >
              The C2PA Standard
            </Link>
            <Link
              href="/c2pa-standard/members"
              className="text-[#2a87c4] hover:underline"
            >
              C2PA Members
            </Link>
            <Link
              href="/c2pa-standard/media-types"
              className="text-[#2a87c4] hover:underline"
            >
              Supported Media Types
            </Link>
            <Link
              href="/c2pa-standard/implementation-guide"
              className="text-[#2a87c4] hover:underline"
            >
              Implementation Guide
            </Link>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
