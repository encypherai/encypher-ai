import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import AISummary from '@/components/seo/AISummary';
import { ArticleShell } from '@/components/content/ArticleShell';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'C2PA Section A.7: Text Provenance Specification | Encypher',
  'C2PA 2.3 Section A.7 defines how C2PA manifests are embedded into unstructured text. Encypher authored Section A.7 and leads the C2PA Text Provenance Task Force.',
  '/c2pa-standard/section-a7'
);

export default function SectionA7Page() {
  const techArticle = getTechArticleSchema({
    title: 'C2PA Section A.7: Text Provenance Specification',
    description: "C2PA 2.3 Section A.7 defines how C2PA manifests are embedded into unstructured text. Encypher authored the section and co-chairs the C2PA Text Provenance Task Force.",
    url: `${siteConfig.url}/c2pa-standard/section-a7`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="C2PA Section A.7: Text Provenance Specification"
        whatWeDo="C2PA Section A.7 defines the standard for embedding provenance manifests into unstructured text. Encypher, through Erik Svilich, authored Section A.7 of the C2PA 2.3 specification. This is the foundational open standard for text content provenance."
        whoItsFor="Developers implementing text provenance. Standards researchers and engineers working with C2PA. Publishers and enterprises evaluating text provenance infrastructure. Anyone seeking to understand the technical foundation of text provenance."
        keyDifferentiator="Encypher authored the text provenance specification for C2PA. Erik Svilich co-chairs the C2PA Text Provenance Task Force. Encypher's implementation extends C2PA's document-level authentication to individual sentence granularity, a capability proprietary to Encypher."
        primaryValue="Understanding the open standard that governs text provenance. Two encoding modes for different deployment environments. Direct link to the specification for independent review."
        pagePath="/c2pa-standard/section-a7"
        pageType="WebPage"
      />

      <Script
        id="tech-article-section-a7"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <ArticleShell path="/c2pa-standard/section-a7">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'C2PA Standard', href: '/c2pa-standard' },
          { name: 'Section A.7', href: '/c2pa-standard/section-a7' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          C2PA Section A.7: Text Provenance
        </h1>
        <p className="text-xl text-muted-foreground mb-4">
          Section A.7 of the C2PA 2.3 specification defines how C2PA manifests are embedded
          into unstructured text. Erik Svilich, Encypher's founder, authored this section
          and co-chairs the C2PA Text Provenance Task Force.
        </p>
        <p className="text-muted-foreground mb-12">
          Read the specification:{' '}
          <a
            href="https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#embedding_manifests_into_unstructured_text"
            className="underline hover:no-underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            C2PA 2.3, Section A.7: Embedding Manifests into Unstructured Text
          </a>
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">What Section A.7 Defines</h2>
          <p className="text-muted-foreground mb-4">
            The main C2PA specification defines how manifests are embedded into structured
            file formats - images, audio, video, and documents that have defined container
            structures with designated locations for metadata. Unstructured text - plain text,
            web articles, social media posts, email content - does not have such a container.
            The manifest must be embedded into the text character stream itself.
          </p>
          <p className="text-muted-foreground mb-4">
            Section A.7 solves this by defining how Unicode characters can carry manifest data
            invisibly within text. The Unicode standard includes character ranges whose values
            have no direct glyph rendering: they are present in the character stream but do not
            produce visible output in standard text rendering environments.
          </p>
          <p className="text-muted-foreground">
            Two encoding modes are defined, each optimized for different deployment environments.
            Both produce text that is visually identical to unsigned text. Both can be decoded
            by C2PA-compliant verification software.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Encoding Mode 1: Web and Digital Distribution</h2>
          <p className="text-muted-foreground mb-4">
            The default encoding mode is optimized for web and digital distribution. It uses
            Unicode characters that are invisible to readers and have no rendering effect in
            standard web browsers, email clients, and text processing systems that comply
            with Unicode standards.
          </p>
          <p className="text-muted-foreground mb-4">
            This mode achieves high information density, allowing full C2PA manifests to be
            embedded without meaningfully expanding the character count of the document. The
            encoding is deterministic: the same manifest always produces the same embedded
            character sequence, and the same character sequence always decodes to the same
            manifest.
          </p>
          <p className="text-muted-foreground">
            Embedded content survives copy-paste, email forwarding, and CMS processing. A
            signed passage either passes verification or fails - there is no probabilistic
            uncertainty. This is Encypher's primary encoding path and the recommended default
            in Section A.7.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Encoding Mode 2: Microsoft Word Compatibility</h2>
          <p className="text-muted-foreground mb-4">
            The second encoding mode is optimized for Microsoft Word and Office-format
            processing environments. Word applies its own normalization to Unicode characters
            during document operations, which can strip or alter certain character ranges that
            the default mode relies on.
          </p>
          <p className="text-muted-foreground mb-4">
            This mode selects characters from Unicode ranges that Word preserves reliably,
            ensuring that content signed for Word distribution remains verifiable after
            round-trips through Word's editing and save operations. The trade-off is lower
            information density compared to the default mode.
          </p>
          <p className="text-muted-foreground">
            Encypher's signing API accepts a parameter to select this mode. Use it when content
            is destined for Word format distribution or any environment where Office-format
            compatibility is required.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Encoding Durability</h2>
          <p className="text-muted-foreground mb-4">
            Both encoding modes are designed to survive the operations that text undergoes in
            normal distribution: copy-paste between applications, email forwarding through
            standard mail servers, publication through CMS platforms, and aggregation by
            content syndication systems. The embedded manifest travels with the text through
            these operations without requiring any special handling by intermediaries.
          </p>
          <p className="text-muted-foreground">
            Verification is deterministic. A signed passage either passes or fails. There is
            no probabilistic threshold or confidence score - the cryptographic signature either
            validates against the content or it does not. This makes text provenance suitable
            for compliance and legal contexts where binary verification outcomes are required.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Encypher's Extension: Sentence-Level Attribution</h2>
          <p className="text-muted-foreground mb-4">
            C2PA Section A.7 defines document-level authentication: a manifest that covers
            the text document as a whole. A verification check confirms that the entire signed
            text is authentic and unmodified. This matches how C2PA handles images and other
            media formats.
          </p>
          <p className="text-muted-foreground mb-4">
            Encypher's implementation extends this with proprietary sentence-level attribution.
            Each sentence in a signed document carries its own attribution data, allowing
            verification at the granularity of individual sentences rather than the document
            as a whole. This means a passage extracted from a larger article can be verified
            on its own, and a document that mixes authentic and modified sentences can identify
            exactly which sentences remain intact.
          </p>
          <p className="text-muted-foreground">
            This sentence-level capability is Encypher's proprietary technology, built on top
            of the C2PA standard. Content signed by Encypher passes standard C2PA document-level
            verification with any compliant tool. The sentence-level attribution requires
            Encypher's verification infrastructure to resolve.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Encypher's Contribution</h2>
          <p className="text-muted-foreground mb-4">
            Erik Svilich contributed the text provenance encoding approaches to the C2PA
            specification and co-chairs the C2PA Text Provenance Task Force. The task force
            is responsible for maintaining and extending Section A.7 as text provenance
            requirements evolve.
          </p>
          <p className="text-muted-foreground mb-4">
            The contribution was accepted into C2PA 2.3, the current version of the
            specification. C2PA 2.3 is available at spec.c2pa.org. Section A.7 begins
            at the "Embedding Manifests into Unstructured Text" section.
          </p>
          <p className="text-muted-foreground">
            Encypher's implementation fully complies with Section A.7. Content signed by
            Encypher can be verified by any C2PA 2.3 compliant verification tool. The
            sentence-level extension is implemented as a compatible addition to the standard
            manifest structure, not as a modification that breaks standard verification.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li>
              <a
                href="https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#embedding_manifests_into_unstructured_text"
                className="underline hover:no-underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                C2PA 2.3 Specification: Section A.7 (external link)
              </a>
            </li>
            <li><Link href="/content-provenance/text" className="underline hover:no-underline">Text Provenance: How It Works</Link></li>
            <li><Link href="/cryptographic-watermarking/text" className="underline hover:no-underline">Cryptographic Watermarking for Text</Link></li>
            <li><Link href="/c2pa-standard" className="underline hover:no-underline">The C2PA Standard</Link></li>
            <li><Link href="/c2pa-standard/manifest-structure" className="underline hover:no-underline">C2PA Manifest Structure</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Implement Section A.7 Text Provenance</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Encypher's API implements both Section A.7 encoding modes with sentence-level
            attribution. Python and TypeScript SDKs available. Free tier for up to 1,000
            documents per month.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/try">Start Free</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/c2pa-standard/implementation-guide">Implementation Guide</Link>
            </Button>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
