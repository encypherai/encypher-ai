import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { getVerticalMetadata } from '@/lib/seo';
import type { Metadata } from 'next';

export const metadata: Metadata = getVerticalMetadata(
  'news-publishers',
  'Content Provenance for News Publishers | Encypher',
  'Embed cryptographic provenance into every article and image you distribute. Wire services, aggregators, and AI companies cannot claim they did not know the source.'
);

export default function NewsPublishersPage() {
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'How does content provenance protect news publishers from unauthorized AI training?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Encypher embeds a cryptographic C2PA manifest directly into each article and image at publication. The manifest records publisher identity, publication timestamp, and rights terms. When an AI company ingests the content, the manifest travels with it. This creates a timestamped record that the company received content with explicit ownership and rights metadata attached, eliminating any "we did not know" defense in licensing disputes.',
        },
      },
      {
        '@type': 'Question',
        name: 'Does provenance survive copy-paste and re-publishing by aggregators?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'For text content, Encypher uses invisible Unicode provenance markers embedded at the character level. These survive copy-paste, syndication, and re-publication. For images, C2PA manifests are embedded in the file container and travel with downloads. Both methods give publishers a chain of custody that persists beyond their own distribution channels.',
        },
      },
      {
        '@type': 'Question',
        name: 'What is the legal significance of embedded provenance for copyright enforcement?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Embedded provenance supports a willful infringement argument. Under the DMCA and copyright law, damages are significantly higher when infringement is willful. If a party received content with cryptographic ownership metadata and used it without a license, that metadata is evidence they knew or should have known the content was owned. Encypher\'s provenance infrastructure is designed to support this documentation chain.',
        },
      },
      {
        '@type': 'Question',
        name: 'Can wire services embed provenance on behalf of member publishers?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Yes. The Encypher API supports organizational signing, where the wire service or distribution platform signs content on behalf of member publishers using delegated credentials. Each signed asset carries the originating publisher\'s identity, even when the signing occurs at the distribution layer.',
        },
      },
    ],
  };

  return (
    <>
      <AISummary
        title="Content Provenance for News Publishers"
        whatWeDo="Encypher embeds cryptographic C2PA provenance into news articles and images at publication, creating a tamper-evident record of ownership and rights that travels with the content through distribution, aggregation, and AI ingestion."
        whoItsFor="News publishers, wire services, and media organizations that distribute content to aggregators, licensees, and downstream AI companies. Specifically suited for AP, Reuters, BBC, and regional publishers with active licensing programs."
        keyDifferentiator="Provenance that survives copy-paste and downstream redistribution. Text provenance uses invisible Unicode markers at the character level. Image provenance uses C2PA manifests embedded in the file container. Both create a chain of custody that persists outside the publisher's own systems."
        primaryValue="Eliminate the 'we did not know' defense in AI licensing disputes. Document willful infringement. Protect wire service distribution with embedded rights metadata that travels to every subscriber and aggregator."
        pagePath="/content-provenance/news-publishers"
        pageType="WebPage"
      />

      <Script
        id="faq-news-publishers"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <ArticleShell path="/content-provenance/news-publishers">
        <Breadcrumbs
          items={[
            { name: 'Home', href: '/' },
            { name: 'Content Provenance', href: '/content-provenance' },
            { name: 'News Publishers', href: '/content-provenance/news-publishers' },
          ]}
        />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Content Provenance for News Publishers
        </h1>
        <p className="text-lg text-muted-foreground mb-8">
          Cryptographic ownership metadata embedded at publication. Travels through wire distribution,
          aggregation, and AI ingestion. Supports formal notice and willful infringement documentation.
        </p>

        {/* The problem */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">The Distribution Problem</h2>
          <p className="text-base leading-relaxed mb-4">
            News content moves fast and moves far. An article published at 9am appears in a wire subscriber's
            CMS by 9:05, in an aggregator's feed by 9:10, and in an AI training dataset within days. At each
            step, the original publisher's ownership claim degrades. Metadata is stripped. Headers are dropped.
            By the time content reaches an AI model, it looks like unowned text.
          </p>
          <p className="text-base leading-relaxed mb-4">
            This is the gap that AI companies exploit. "We did not know it was owned" is a viable defense when
            the only proof of ownership sits in a publisher's CMS, not in the content itself. Embedding provenance
            in the content eliminates that defense.
          </p>
          <p className="text-base leading-relaxed">
            Encypher signs each article and image at publication. The C2PA manifest travels with the content
            through every downstream channel. Wire subscribers receive content that already carries its own
            proof of origin. Aggregators receive files with embedded rights terms. AI companies receive assets
            that document, at ingestion time, exactly who owns them and under what conditions they may be used.
          </p>
        </section>

        {/* Wire service distribution */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Wire Service Distribution with Embedded Provenance</h2>
          <p className="text-base leading-relaxed mb-4">
            For publishers operating through wire services, the signing can occur at either end of the
            distribution chain. Publishers can sign content before submission to the wire, ensuring provenance
            is established at the point of creation. Wire services can sign on behalf of member publishers
            using delegated credentials through the Encypher API.
          </p>
          <div className="bg-muted/30 border border-border rounded-lg p-6 mb-4">
            <h3 className="font-semibold mb-3">What the manifest records at wire distribution</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>- Originating publisher identity and domain</li>
              <li>- Publication timestamp (RFC 3161 compliant)</li>
              <li>- Rights terms and licensing conditions</li>
              <li>- Cryptographic hash of the original content</li>
              <li>- Signing organization and certificate chain</li>
            </ul>
          </div>
          <p className="text-base leading-relaxed">
            Every wire subscriber receives this manifest embedded in the content. When an AI company scrapes
            or licenses from a subscriber, the manifest travels with the content. The chain of custody is
            unbroken from creation to AI ingestion.
          </p>
        </section>

        {/* Formal notice */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Formal Notice Capability</h2>
          <p className="text-base leading-relaxed mb-4">
            Embedded provenance functions as a form of constructive notice. Content with a C2PA manifest
            carries machine-readable rights metadata that any compliant AI ingestion pipeline can read.
            Publishers who embed provenance before distribution have documentation that their ownership
            claim was present in the content at the time of ingestion.
          </p>
          <p className="text-base leading-relaxed mb-4">
            For publishers pursuing licensing agreements or enforcement actions, this distinction matters.
            An AI company that ingested content with embedded provenance metadata cannot credibly argue
            it was unaware of the ownership claim. The manifest is timestamped, cryptographically signed,
            and embedded in the file. It is not a separate record that can be disclaimed.
          </p>
          <p className="text-base leading-relaxed">
            See the legal implications analysis at{' '}
            <Link href="/cryptographic-watermarking/legal-implications" className="text-[#2a87c4] hover:underline">
              Cryptographic Watermarking: Legal Implications
            </Link>{' '}
            for a detailed treatment of how embedded provenance interacts with copyright and licensing law.
          </p>
        </section>

        {/* Willful infringement */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Documenting Willful Infringement</h2>
          <p className="text-base leading-relaxed mb-4">
            Copyright law distinguishes between innocent and willful infringement. Statutory damages for
            willful infringement reach $150,000 per work. Innocent infringement caps at $200. The
            difference turns on what the infringer knew or should have known.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Embedded provenance shifts that calculus. A party that received content with a cryptographic
            manifest identifying the owner and stating rights terms had notice. Using the content without
            a license, after receiving it with that manifest, supports a willful infringement finding.
          </p>
          <p className="text-base leading-relaxed">
            Publishers who sign their content before distribution are building the evidentiary record
            now, before enforcement actions become necessary. The manifest timestamps predate any
            infringement, which matters for establishing when notice was received.
          </p>
        </section>

        {/* Brand protection */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Brand Protection Through Provenance</h2>
          <p className="text-base leading-relaxed mb-4">
            News publishers face a second problem beyond licensing: misattribution. AI-generated content
            is being falsely attributed to established news brands. Deepfake news articles circulate under
            masthead names. Images are re-captioned with fabricated context.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Authentic content signed by a publisher carries a verifiable identity credential. Readers
            and platforms can verify that a given article or image was actually produced and signed by
            the claimed publisher. Content without that signature, or with a broken signature, is
            distinguishable as potentially inauthentic.
          </p>
          <p className="text-base leading-relaxed">
            This creates a two-sided value: publishers protect their brand by making genuine content
            verifiable, and readers gain a mechanism to distinguish authentic journalism from fabricated
            content that borrows a publisher's name.
          </p>
        </section>

        {/* How it works */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Integration with Existing Publishing Workflows</h2>
          <p className="text-base leading-relaxed mb-4">
            Encypher integrates at the CMS or distribution layer. Publishers do not need to change editorial
            workflows. The signing API is called at the point of publication, adding a C2PA manifest to the
            outgoing content before it enters the distribution pipeline.
          </p>
          <div className="bg-muted/30 border border-border rounded-lg p-6 mb-4">
            <h3 className="font-semibold mb-3">Integration points</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>- CMS publish hook (WordPress, Arc, Brightspot, proprietary CMSs)</li>
              <li>- Wire service submission pipeline</li>
              <li>- CDN or asset management layer for images</li>
              <li>- RSS feed generation for text provenance</li>
              <li>- API-direct for publishers building custom distribution systems</li>
            </ul>
          </div>
          <p className="text-base leading-relaxed">
            For publishers already in the{' '}
            <Link href="/content-provenance/for-publishers" className="text-[#2a87c4] hover:underline">
              Encypher publisher network
            </Link>
            , provenance signing is available as part of the standard publisher tier. Enterprise publishers
            with high-volume wire distribution or custom signing requirements should contact us directly.
          </p>
        </section>

        {/* FAQ section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-6">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">Does provenance survive copy-paste and aggregator re-publishing?</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                For text content, Encypher uses invisible Unicode provenance markers embedded at the character
                level using our proprietary segment-level technology. These survive copy-paste and
                syndication. For images, C2PA manifests are embedded in the file container and travel with
                downloads. Both methods give publishers a chain of custody that persists beyond their
                own distribution channels.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">How does this interact with existing DMCA processes?</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Embedded provenance does not replace DMCA takedown processes. It supplements them by
                providing pre-existing documentation of ownership that predates any infringement. In
                contexts where licensing negotiations or litigation are more appropriate than takedowns,
                the provenance record supports those approaches.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Can publishers compare Encypher against other approaches?</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Yes. See the{' '}
                <Link href="/compare/encypher-vs-tollbit" className="text-[#2a87c4] hover:underline">
                  Encypher vs. Tollbit comparison
                </Link>{' '}
                for a detailed analysis of cryptographic provenance versus access-control approaches
                to AI content licensing.
              </p>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="border-t pt-8">
          <h2 className="text-xl font-semibold mb-4">Start Signing Your Content</h2>
          <p className="text-muted-foreground mb-6">
            Embed provenance into your content before your next distribution run. The record
            needs to predate any infringement to be useful in enforcement.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 mb-6">
            <Button asChild style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/content-provenance/for-publishers">Publisher Network</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/platform">API Documentation</Link>
            </Button>
          </div>
          <div className="flex flex-col sm:flex-row gap-4 text-sm">
            <Link href="/content-provenance" className="text-[#2a87c4] hover:underline">
              What Is Content Provenance?
            </Link>
            <Link href="/cryptographic-watermarking/legal-implications" className="text-[#2a87c4] hover:underline">
              Legal Implications
            </Link>
            <Link href="/compare/encypher-vs-tollbit" className="text-[#2a87c4] hover:underline">
              Encypher vs. Tollbit
            </Link>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
