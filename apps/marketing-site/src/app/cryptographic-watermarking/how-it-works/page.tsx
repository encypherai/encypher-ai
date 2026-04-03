import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@encypher/design-system';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'How Cryptographic Watermarking Works | Technical Deep Dive | Encypher',
  'How Encypher embeds verifiable content provenance: invisible text markers, sentence-level authentication, C2PA manifest embedding for media, and enterprise distribution fingerprinting.',
  '/cryptographic-watermarking/how-it-works',
  undefined,
  undefined,
  'Invisible markers. Sentence-level proof. The full technical picture.'
);

export default function HowItWorksPage() {
  const techArticle = getTechArticleSchema({
    title: 'How Cryptographic Watermarking Works',
    description: 'How Encypher embeds verifiable content provenance: invisible text markers, sentence-level authentication, C2PA JUMBF embedding for media, and enterprise distribution fingerprinting.',
    url: `${siteConfig.url}/cryptographic-watermarking/how-it-works`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="How Cryptographic Watermarking Works"
        whatWeDo="Encypher embeds cryptographic provenance using two technology stacks: for text, invisible markers with sentence-level authentication; for media, C2PA JUMBF manifests in format-native container locations."
        whoItsFor="Developers, security engineers, and technical decision-makers evaluating content provenance infrastructure. Anyone who needs to understand the capabilities before adopting or recommending Encypher."
        keyDifferentiator="Sentence-level authentication is Encypher's proprietary technology. It is not a C2PA feature - it extends the C2PA standard to individual sentence granularity. C2PA JUMBF embedding for media files follows the open standard. These are distinct technology layers."
        primaryValue="Clear understanding of what Encypher delivers - invisible embedding, tamper detection at the sentence level, and forensic leak identification - and how those capabilities map to C2PA-standard versus proprietary technology."
        pagePath="/cryptographic-watermarking/how-it-works"
        pageType="WebPage"
      />

      <Script
        id="tech-article-how-it-works"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <ArticleShell path="/cryptographic-watermarking/how-it-works">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Cryptographic Watermarking', href: '/cryptographic-watermarking' },
          { name: 'How It Works', href: '/cryptographic-watermarking/how-it-works' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          How Cryptographic Watermarking Works
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          Cryptographic watermarking embeds verifiable proof of origin into content.
          For text, this uses invisible characters woven into the document. For media files,
          this uses format-native container structures. Both are cryptographically signed and
          independently verifiable.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Three Technology Layers</h2>
          <p className="text-muted-foreground mb-4">
            Encypher's cryptographic watermarking implementation spans three distinct layers.
            Understanding each layer clarifies what capabilities you are purchasing and what
            you can verify independently.
          </p>
          <div className="space-y-4 mb-4">
            <div className="p-4 bg-muted/30 rounded-lg border-l-4 border-[#2a87c4]">
              <h3 className="font-semibold mb-1">Layer 1: C2PA Foundation (Open Standard)</h3>
              <p className="text-muted-foreground text-sm">
                The C2PA manifest structure, signed claims, and media file embedding locations
                follow the open C2PA specification, implemented by multiple vendors and verifiable
                with open-source libraries. Encypher contributed Section A.7 (text provenance)
                to this standard. Any C2PA-compliant tool can verify content signed at this layer.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg border-l-4 border-[#2a87c4]">
              <h3 className="font-semibold mb-1">Layer 2: Encypher Proprietary Extensions</h3>
              <p className="text-muted-foreground text-sm">
                Encypher's default encoding embeds a complete C2PA manifest invisibly within text.
                The embedded data is undetectable to readers, survives copy-paste, and can be
                verified cryptographically. Sentence-level authentication extends this to individual
                sentences, enabling tamper detection at granularity the base C2PA standard does not
                provide. These capabilities require Encypher's implementation.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg border-l-4 border-[#2a87c4]">
              <h3 className="font-semibold mb-1">Layer 3: Enterprise Features</h3>
              <p className="text-muted-foreground text-sm">
                Distribution fingerprinting embeds unique, recipient-specific markers into each copy
                of a distributed document. When content leaks, forensic analysis identifies the
                source. This layer requires Enterprise-tier access and is designed for pre-publication
                content, confidential documents, and restricted distribution workflows.
              </p>
            </div>
          </div>
          <p className="text-muted-foreground">
            This distinction determines what you can rely on independently versus what requires
            Encypher's infrastructure. C2PA manifest verification works with open-source tools.
            Sentence-level and fingerprint verification require Encypher's extended verification.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Text: Default Encoding</h2>
          <p className="text-muted-foreground mb-4">
            Encypher's default text encoding embeds a complete C2PA manifest invisibly within
            the document. The embedded data is placed using invisible Unicode characters that
            have no effect on the visible text. From the reader's perspective, the document is
            character-for-character identical to unsigned text. No visual difference is present.
          </p>
          <p className="text-muted-foreground mb-4">
            The encoding is designed for the way text actually moves: copied from a browser,
            pasted into an email, forwarded as a message, or republished on another site.
            Unicode-compliant text processors preserve the embedded markers through these
            operations. The provenance travels with the content.
          </p>
          <p className="text-muted-foreground">
            Verification requires no special tooling beyond Encypher's API or the open-source
            SDK. A single API call returns the signer identity, timestamp, and any custom
            assertions embedded in the manifest.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Text: Word-Optimized Encoding</h2>
          <p className="text-muted-foreground mb-4">
            Encypher offers an alternative encoding optimized for Microsoft Word and Office
            document workflows, ensuring provenance survives Word's text processing pipeline.
            The default encoding is designed for web and email distribution; this encoding
            is designed for enterprise document workflows where Word is the primary format.
          </p>
          <p className="text-muted-foreground mb-4">
            The character set is selected specifically for stability through Word's document
            processing operations. Where the default encoding maximizes information density,
            this encoding prioritizes compatibility with the full range of Word behaviors
            across versions and platforms.
          </p>
          <p className="text-muted-foreground">
            Both encodings produce invisible output and verify through the same API. The choice
            of encoding is determined by the distribution channel, not by the type of content
            or the assertions embedded.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Sentence-Level Authentication</h2>
          <p className="text-muted-foreground mb-4">
            Standard C2PA provenance authenticates a document as a whole: a single signature
            covers the entire content. If any part of the document changes, the whole document
            fails verification. Encypher's proprietary sentence-level technology extends this
            to individual sentences.
          </p>
          <p className="text-muted-foreground mb-4">
            Encypher's proprietary sentence-level technology enables cryptographic proof that
            a specific sentence came from a specific source and has not been altered. This goes
            beyond document-level C2PA authentication to individual sentence granularity.
            A reader can verify a single quoted sentence without access to the full document.
            A publisher can detect which sentences were altered in a modified copy.
          </p>
          <p className="text-muted-foreground">
            This is Encypher's proprietary technology. It is implemented as a custom assertion
            type in the C2PA manifest, compatible with standard C2PA verification while providing
            additional granularity for Encypher-aware verifiers. The sentence-level structure
            is included in the embedded manifest and verified through the same API as document-level
            provenance.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Media: JUMBF Manifest Embedding</h2>
          <p className="text-muted-foreground mb-4">
            For images, audio, and video, Encypher follows the C2PA specification for
            format-native manifest embedding. The C2PA manifest is packaged in a standard
            container format and placed in the format-standard location for extension data.
          </p>
          <p className="text-muted-foreground mb-4">
            Encypher supports the full range of formats covered by the C2PA specification:
            JPEG, PNG, ISO BMFF formats (including MP4, MOV, AVIF, and HEIC), RIFF formats
            (including WAV and AVI), and MP3. The manifest travels with the file and can be
            verified without round-tripping to Encypher's servers.
          </p>
          <p className="text-muted-foreground">
            This layer is entirely defined by the C2PA specification. Any C2PA-compliant tool
            can verify the manifests Encypher embeds in media files. Encypher's contribution
            here is implementation correctness and API accessibility, not proprietary technology.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Enterprise Distribution Fingerprinting</h2>
          <p className="text-muted-foreground mb-4">
            Enterprise-tier distribution fingerprinting embeds unique, recipient-specific markers
            into each copy of a distributed document. When the same document is distributed to
            multiple recipients, each copy carries markers that identify which recipient received
            which copy. The markers are invisible and do not alter the readable content.
          </p>
          <p className="text-muted-foreground mb-4">
            When content is redistributed without authorization, forensic analysis identifies
            the source of the leak. The analysis examines the markers in the leaked copy and
            matches them to the recipient record. This works even when the leaked copy has been
            reformatted, partially edited, or transcribed.
          </p>
          <p className="text-muted-foreground">
            Distribution fingerprinting is used for pre-publication content, confidential
            documents, board materials, and restricted distribution workflows where accountability
            for leaks is a compliance or legal requirement.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/cryptographic-watermarking" className="underline hover:no-underline">Cryptographic Watermarking: Overview</Link></li>
            <li><Link href="/content-provenance/text" className="underline hover:no-underline">Text Provenance Deep Dive</Link></li>
            <li><Link href="/c2pa-standard/section-a7" className="underline hover:no-underline">C2PA Section A.7</Link></li>
            <li><Link href="/c2pa-standard/manifest-structure" className="underline hover:no-underline">C2PA Manifest Structure</Link></li>
            <li><Link href="/cryptographic-watermarking/vs-statistical-watermarking" className="underline hover:no-underline">Cryptographic vs. Statistical Watermarking</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Start With Cryptographic Proof</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Free tier covers 1,000 documents per month. All encoding methods included.
            Sentence-level authentication at all tiers.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/try">Start Free</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/tools/verify">Verify Content</Link>
            </Button>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
