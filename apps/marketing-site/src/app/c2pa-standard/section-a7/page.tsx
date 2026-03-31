import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'C2PA Section A.7: Text Provenance Specification | Encypher',
  'Deep dive on C2PA 2.3 Section A.7 - embedding manifests into unstructured text. Three encoding approaches, Unicode variation selectors, and Encypher\'s role in authoring the specification.',
  '/c2pa-standard/section-a7'
);

export default function SectionA7Page() {
  const techArticle = getTechArticleSchema({
    title: 'C2PA Section A.7: Text Provenance Specification',
    description: "C2PA 2.3 Section A.7 defines how C2PA manifests are embedded into unstructured text. Three encoding approaches using Unicode characters invisible to readers. Encypher authored the section.",
    url: `${siteConfig.url}/c2pa-standard/section-a7`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="C2PA Section A.7: Text Provenance Specification"
        whatWeDo="C2PA Section A.7 defines the standard for embedding provenance manifests into unstructured text. Encypher, through Erik Svilich, contributed Section A.7 to the C2PA 2.3 specification. This is the foundational standard for text content provenance."
        whoItsFor="Developers implementing text provenance. Standards researchers and engineers working with C2PA. Publishers and enterprises evaluating text provenance infrastructure. Anyone seeking to understand the technical foundation of text provenance."
        keyDifferentiator="Encypher contributed the text provenance specification to C2PA. Erik Svilich co-chairs the C2PA Text Provenance Task Force. The section defines the encoding approaches that Encypher implements, ensuring full compliance with the open standard."
        primaryValue="Understanding the open standard that governs text provenance. Three encoding approaches for different deployment environments. Direct link to the specification for independent review."
        pagePath="/c2pa-standard/section-a7"
        pageType="WebPage"
      />

      <Script
        id="tech-article-section-a7"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
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
          into unstructured text. Erik Svilich, Encypher's founder, contributed this section
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
            Three encoding approaches are defined, each optimized for different deployment
            environments. All three approaches produce text that is visually identical to
            unsigned text. All three can be decoded by C2PA-compliant verification software.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Approach 1: Variation Selector Encoding</h2>
          <p className="text-muted-foreground mb-4">
            The variation selector encoding uses Unicode variation selectors to encode binary
            data. Unicode allocates 256 variation selector code points:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>VS1-VS16: U+FE00 through U+FE0F (16 characters)</li>
            <li>VS17-VS256: U+E0100 through U+E01EF (240 characters)</li>
          </ul>
          <p className="text-muted-foreground mb-4">
            Variation selectors are designed to specify which glyph variant to use when
            rendering the preceding character. When no variant mapping exists for the
            character-selector combination, the selector is ignored by renderers. Encypher
            uses this property: variation selectors placed between words in English text
            have no rendering effect because no variant glyphs are defined for common
            Latin characters in this range.
          </p>
          <p className="text-muted-foreground mb-4">
            The 256 variation selectors encode 8 bits per character. Manifest data is
            encoded as a sequence of variation selectors placed at defined positions within
            the text. The encoding is deterministic - the same manifest always produces
            the same character sequence.
          </p>
          <p className="text-muted-foreground">
            This approach is the recommended default in Section A.7 and is Encypher's
            primary encoding path. It works correctly in all major web browsers, email
            clients, and text processing systems that comply with Unicode standards.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Approach 2: Zero-Width Character Encoding</h2>
          <p className="text-muted-foreground mb-4">
            The zero-width character encoding uses a set of Unicode characters with zero
            visual width. These characters are placed between visible characters and are
            not rendered, but are present in the character stream and survive most text
            operations.
          </p>
          <p className="text-muted-foreground mb-4">
            Section A.7 defines a character set for this encoding:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>ZWNJ (Zero Width Non-Joiner, U+200C) - assigned value 0</li>
            <li>ZWJ (Zero Width Joiner, U+200D) - assigned value 1</li>
            <li>CGJ (Combining Grapheme Joiner, U+034F) - assigned value 2</li>
            <li>MVS (Mongolian Vowel Separator, U+180E) - assigned value 3</li>
            <li>LRM (Left-to-Right Mark, U+200E) - assigned value 4</li>
            <li>RLM (Right-to-Left Mark, U+200F) - assigned value 5</li>
          </ul>
          <p className="text-muted-foreground mb-4">
            The six-character set enables base-6 (senary) encoding. This encoding is optimized
            for Microsoft Word and other Office-format processing environments where some Unicode
            ranges behave unexpectedly. Word compatibility is achieved by avoiding the Zero Width
            Space (U+200B), which Word strips, and selecting characters from ranges that Word
            preserves during document operations.
          </p>
          <p className="text-muted-foreground">
            This is Encypher's secondary encoding path, used when content is destined for
            Word format distribution. The signing API accepts an encoding parameter to select
            this path.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Approach 3: Whitespace Width Encoding</h2>
          <p className="text-muted-foreground mb-4">
            The whitespace width encoding uses variations in whitespace character widths to
            encode data. Unicode includes multiple whitespace characters with different
            nominal widths: standard space (U+0020), thin space (U+2009), hair space (U+200A),
            and others. By selecting from these width variants, binary data can be encoded
            in the sequence of spaces between words.
          </p>
          <p className="text-muted-foreground mb-4">
            This approach has lower information density than the variation selector encoding
            but survives environments that strip zero-width characters. Its primary use case
            is print-to-scan pipelines - documents that will be printed and then digitized
            via OCR. The width differences are small enough to be visually imperceptible
            but measurable in the resulting pixel data.
          </p>
          <p className="text-muted-foreground">
            This encoding path corresponds to the "Print Leak Detection" feature in the
            Encypher enterprise tier, designed for detecting which distribution channel
            produced a physical copy that was scanned and leaked.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Manifest Encoding Structure</h2>
          <p className="text-muted-foreground mb-4">
            Regardless of which encoding approach is used, the manifest data encoded
            in the text follows the same C2PA structure: a CBOR-serialized C2PA manifest
            containing claims, assertions, and a COSE signature. The only difference
            between text embedding and file container embedding is the physical mechanism
            used to store the manifest data alongside the content.
          </p>
          <p className="text-muted-foreground mb-4">
            Section A.7 defines the positioning algorithm: where in the text the manifest
            characters are placed, how the manifest is split across multiple encoding
            positions, and how verification software should search for and extract the
            manifest from a text string.
          </p>
          <p className="text-muted-foreground">
            Encypher's implementation of Section A.7 extends the positioning algorithm
            with sentence-level Merkle tree integration. Each sentence boundary in the
            text becomes an encoding position anchor, ensuring that the markers for each
            sentence's Merkle leaf are co-located with the sentence content.
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
            The contribution was accepted into C2PA 2.3, which is the current version of
            the specification. C2PA 2.3 is available at spec.c2pa.org. Section A.7 begins
            at the "Embedding Manifests into Unstructured Text" section.
          </p>
          <p className="text-muted-foreground">
            Encypher's implementation fully complies with Section A.7. Content signed by
            Encypher can be verified by any C2PA 2.3 compliant verification tool. The
            sentence-level Merkle tree extension is implemented as a compatible addition
            to the standard manifest structure, not as a modification that breaks
            standard verification.
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
            Encypher's API implements all three Section A.7 encoding approaches.
            Python and TypeScript SDKs available. Free tier for up to 1,000 documents per month.
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
      </div>
    </>
  );
}
