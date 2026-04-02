import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'Cryptographic Watermarking for Text | Invisible, Durable, Verifiable | Encypher',
  'Invisible cryptographic text watermarking using proprietary invisible encoding. Survives copy-paste, B2B distribution, and aggregator scraping. Sentence-level granularity for partial attribution.',
  '/cryptographic-watermarking/text',
  undefined,
  undefined,
  'Invisible. Durable. Verifiable. Ownership baked into every sentence.'
);

export default function CryptographicWatermarkingTextPage() {
  const techArticle = getTechArticleSchema({
    title: 'Cryptographic Watermarking for Text',
    description: 'Invisible cryptographic text watermarking using proprietary invisible encoding. Survives copy-paste, B2B distribution, and aggregator scraping.',
    url: `${siteConfig.url}/cryptographic-watermarking/text`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="Cryptographic Watermarking for Text"
        whatWeDo="Encypher embeds cryptographic watermarks into text using proprietary invisible encoding. The watermarks survive copy-paste, B2B distribution, and aggregator scraping. Each text string carries its own proof of origin, without any visible changes to the text."
        whoItsFor="Publishers, journalists, and organizations distributing text content who need durable proof of ownership that travels with content through downstream distribution channels."
        keyDifferentiator="Sentence-level Merkle tree authentication enables per-sentence verification. This is Encypher's proprietary technology. Combined with invisible embedding, it means specific sentences can be cryptographically traced to their source document even when reproduced out of context."
        primaryValue="Invisible watermarking with no content changes, copy-paste survival, and sentence-level granularity for partial reproduction attribution."
        pagePath="/cryptographic-watermarking/text"
        pageType="WebPage"
      />

      <Script
        id="tech-article-cwm-text"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <ArticleShell path="/cryptographic-watermarking/text">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Cryptographic Watermarking', href: '/cryptographic-watermarking' },
          { name: 'Text', href: '/cryptographic-watermarking/text' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Cryptographic Watermarking for Text
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          Invisible provenance markers embedded in every article, post, and document you publish.
          Readers see nothing different. Verification tools see cryptographic proof of ownership.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Invisible by Design</h2>
          <p className="text-muted-foreground mb-4">
            Encypher embeds cryptographic provenance markers directly within the text character
            stream. The markers produce no visible output. The text looks identical to readers,
            screen readers handle it correctly, and search engine indexes treat it as the
            underlying text content. The watermark is invisible in every practical context.
          </p>
          <p className="text-muted-foreground mb-4">
            There is no markup change, no visible tag, no alteration to the reading experience.
            A signed article and an unsigned article are indistinguishable to any reader. The
            difference only appears when a verification tool examines the content and extracts
            the embedded proof.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Copy-Paste Survival</h2>
          <p className="text-muted-foreground mb-4">
            Text processors preserve the full character stream in copy operations.
            When text is copied from a web page, the character stream is copied
            intact - including embedded provenance markers. When that text is pasted into an email,
            a document, a CMS, or a messaging platform, the markers are present in the
            pasted text.
          </p>
          <p className="text-muted-foreground mb-4">
            This has been verified across:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-1 ml-4">
            <li>Major web browsers (Chrome, Firefox, Safari, Edge)</li>
            <li>Email clients (Gmail, Outlook, Apple Mail)</li>
            <li>Document editors (Google Docs, Pages, LibreOffice)</li>
            <li>Messaging platforms (Slack, Teams, WhatsApp)</li>
            <li>CMS platforms (WordPress, Contentful, Drupal)</li>
          </ul>
          <p className="text-muted-foreground">
            Microsoft Word is handled separately with the ZWC marker encoding, which uses
            a different character set optimized for Word's document processing behavior.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">B2B Distribution and Wire Services</h2>
          <p className="text-muted-foreground mb-4">
            Wire service distribution is the highest-volume text distribution channel for
            professional content. AP and Reuters distribute thousands of stories per day
            to hundreds or thousands of subscriber outlets. Each distribution event is a
            potential ownership record.
          </p>
          <p className="text-muted-foreground mb-4">
            When signed text passes through a wire service, the markers travel with the
            article. The subscriber outlet receives the article with the markers intact.
            Their CMS ingests it with the markers. Their readers copy and paste from the
            published article with the markers.
          </p>
          <p className="text-muted-foreground">
            The chain of custody is not just documented at the source - it is present in
            every copy at every distribution point. Any downstream party that has the text
            also has the cryptographic proof of where it came from and whose rights terms
            apply to it.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Aggregator Scraping and AI Training Data</h2>
          <p className="text-muted-foreground mb-4">
            Web scrapers that collect text content from HTML pages extract the text content
            of the page - which includes the Unicode character stream with embedded markers.
            Standard scraping tools that use HTML parsers to extract text content preserve
            Unicode characters in the extracted text.
          </p>
          <p className="text-muted-foreground mb-4">
            AI training corpus builders that scrape web content and process HTML to extract
            readable text are subject to the same behavior. If a scraper extracts the text
            content of a signed article, the markers are present in the scraped text unless
            the scraper explicitly strips invisible provenance markers - which is not a standard
            scraping operation.
          </p>
          <p className="text-muted-foreground">
            This means that signed articles that end up in AI training corpora carry their
            provenance markers. The AI company that trained on the content has the cryptographic
            evidence of the content's origin in their training data. This is the mechanism that
            establishes formal notice for willful infringement claims.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Sentence-Level Granularity</h2>
          <p className="text-muted-foreground mb-4">
            Encypher's proprietary sentence-level Merkle tree authenticates each sentence
            individually. When a specific sentence from a signed article is reproduced in
            another context - an AI output, a summary, a quote in another article - the
            sentence carries its own proof of origin.
          </p>
          <p className="text-muted-foreground mb-4">
            Verification can confirm, for a given sentence, that it came from a specific
            article by a specific publisher on a specific date. This supports two distinct
            use cases:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>Quote integrity checking: confirm that a quoted passage matches the original publication</li>
            <li>Partial reproduction claims: trace specific sentences in AI outputs back to their source documents</li>
          </ul>
          <p className="text-muted-foreground">
            For publishers with large archives, this means that even partial reproduction of
            their content - a few sentences from an article, not the full text - can be
            cryptographically attributed to the original source. The evidentiary record
            covers specific sentences, not just document-level ownership.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Works in Any Text Context</h2>
          <p className="text-muted-foreground mb-4">
            The text watermarking approach is not tied to any specific content format or
            distribution channel. It works in:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-1 ml-4">
            <li>Web articles (HTML text content)</li>
            <li>Email newsletters</li>
            <li>Social media posts (where platform character limits allow)</li>
            <li>API responses delivering text content</li>
            <li>CMS-managed content</li>
            <li>Word documents (with ZWC encoding)</li>
            <li>PDF documents (via the document signing path)</li>
          </ul>
          <p className="text-muted-foreground">
            The signing API accepts a plain text string and returns the same string with
            embedded markers. How that string is subsequently stored, formatted, or displayed
            does not affect the provenance.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/content-provenance/text" className="underline hover:no-underline">Text Provenance: Technical Deep Dive</Link></li>
            <li><Link href="/c2pa-standard/section-a7" className="underline hover:no-underline">C2PA Section A.7</Link></li>
            <li><Link href="/cryptographic-watermarking/how-it-works" className="underline hover:no-underline">How Cryptographic Watermarking Works</Link></li>
            <li><Link href="/cryptographic-watermarking/survives-distribution" className="underline hover:no-underline">How Provenance Survives Distribution</Link></li>
            <li><Link href="/content-provenance/for-publishers" className="underline hover:no-underline">Content Provenance for Publishers</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Add Invisible Watermarks to Your Text</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            No visible changes. Copy-paste durable. Sentence-level granularity included.
            Free for up to 1,000 documents per month.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/try">Start Free</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/tools/verify">Verify Text</Link>
            </Button>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
