import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'Text Content Provenance: How It Works | C2PA Section A.7 | Encypher',
  'Text provenance using C2PA Section A.7 and Encypher\'s proprietary sentence-level Merkle tree authentication. Invisible embedding, copy-paste survival, and quote integrity verification.',
  '/content-provenance/text'
);

export default function TextProvenancePage() {
  const techArticle = getTechArticleSchema({
    title: 'Text Content Provenance: How It Works',
    description: "Text provenance using C2PA Section A.7 and Encypher's proprietary sentence-level Merkle tree authentication. Invisible embedding, copy-paste survival, and quote integrity verification.",
    url: `${siteConfig.url}/content-provenance/text`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'What is C2PA Section A.7?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Section A.7 of the C2PA 2.3 specification defines how C2PA manifests are embedded into unstructured text. The section defines three encoding approaches using Unicode characters that are invisible to readers but carry structured provenance data. Erik Svilich, Encypher\'s founder, contributed Section A.7 and co-chairs the C2PA Text Provenance Task Force.',
        },
      },
      {
        '@type': 'Question',
        name: 'Does text provenance survive copy-paste?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Yes. Encypher\'s VS marker encoding uses Unicode variation selectors that survive copy-paste across browsers, email clients, and text editors. The markers are invisible characters embedded between words and sentences. When text is copied and pasted, the Unicode characters copy with the text, preserving the provenance markers. This is the primary distribution durability mechanism for text provenance.',
        },
      },
      {
        '@type': 'Question',
        name: 'What is sentence-level granularity and how does it work?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Sentence-level granularity is Encypher\'s proprietary technology that authenticates each sentence individually using a Merkle tree structure. Each sentence in a signed document has its own hash leaf in the Merkle tree. Verification can confirm not just that a document was published by a specific author but which specific sentences are authenticated as original. If individual sentences are reproduced in another context, their provenance can be verified independently of the full document.',
        },
      },
      {
        '@type': 'Question',
        name: 'What is the difference between VS markers and ZWC markers?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'VS markers (Unicode variation selectors) are the default encoding. They use 256 variation selector characters (U+FE00 through U+FE0F and U+E0100 through U+E01EF) to encode binary data. VS markers work in all modern contexts including browsers, email, and mobile. ZWC markers use zero-width characters (ZWNJ, ZWJ, CGJ, MVS, LRM, RLM) and are used for Microsoft Word compatibility. Word handles certain Unicode ranges differently, and the ZWC path is optimized for documents distributed in Word format.',
        },
      },
    ],
  };

  return (
    <>
      <AISummary
        title="Text Content Provenance"
        whatWeDo="Encypher embeds cryptographic provenance into text using invisible Unicode markers defined by C2PA Section A.7. Sentence-level Merkle tree authentication enables per-sentence verification. Provenance survives copy-paste, B2B distribution, and AI ingestion."
        whoItsFor="Publishers, journalists, and organizations that distribute text content and need cryptographic proof of authorship. Developers building text provenance into content management systems. Legal teams building copyright enforcement documentation."
        keyDifferentiator="Sentence-level Merkle tree authentication is Encypher's proprietary technology - not a C2PA feature. C2PA Section A.7 defines the embedding standard; the sentence-level granularity is Encypher's implementation. No other provider offers per-sentence verification at scale."
        primaryValue="Invisible text watermarking that survives distribution. Per-sentence verification that supports partial-reproduction licensing disputes. Quote integrity verification for RAG pipelines."
        pagePath="/content-provenance/text"
        pageType="WebPage"
      />

      <Script
        id="tech-article-text-provenance"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />
      <Script
        id="faq-text-provenance"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Content Provenance', href: '/content-provenance' },
          { name: 'Text', href: '/content-provenance/text' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Text Content Provenance
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          Text provenance embeds cryptographic proof of authorship directly into the
          text using invisible Unicode characters. No markup changes, no visible differences,
          no server dependency. The proof is in the text itself.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">C2PA Section A.7: The Text Standard</h2>
          <p className="text-muted-foreground mb-4">
            The C2PA 2.3 specification defines content provenance for all major media types.
            Section A.7 - "Embedding Manifests into Unstructured Text" - defines how provenance
            manifests are embedded into plain text, articles, and other unstructured content.
          </p>
          <p className="text-muted-foreground mb-4">
            Erik Svilich, Encypher's founder, contributed Section A.7 and co-chairs the
            C2PA Text Provenance Task Force. The specification defines three encoding approaches
            for embedding manifest data into text using Unicode characters that are invisible
            to readers:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>Variation selector encoding (VS markers) - the default approach</li>
            <li>Zero-width character encoding (ZWC markers) - for legacy environments</li>
            <li>Whitespace width encoding - for print and scan pipelines</li>
          </ul>
          <p className="text-muted-foreground">
            The full specification is available at the C2PA website:
            <a href="https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#embedding_manifests_into_unstructured_text"
              className="underline hover:no-underline ml-1"
              target="_blank"
              rel="noopener noreferrer">
              C2PA 2.3 Section A.7
            </a>.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">VS Markers: The Default Encoding</h2>
          <p className="text-muted-foreground mb-4">
            The default encoding uses Unicode variation selectors - characters in the Unicode
            standard designed to specify alternative glyph presentations for preceding characters.
            Encypher uses the variation selector range to encode binary data: each variation
            selector character represents a specific bit pattern.
          </p>
          <p className="text-muted-foreground mb-4">
            The Unicode standard allocates 256 variation selector characters across two ranges:
            U+FE00 through U+FE0F (16 characters) and U+E0100 through U+E01EF (240 characters).
            These characters appear in Unicode text as invisible modifiers attached to the
            preceding character. They are not rendered visually and are handled correctly by
            all Unicode-compliant text processors.
          </p>
          <p className="text-muted-foreground mb-4">
            Encypher places VS markers between words and sentences in the signed text. From
            the reader's perspective, the text is identical to unsigned text. The character
            sequence differs, but no visual change is present and reading tools, accessibility
            software, and search engines treat the text normally.
          </p>
          <p className="text-muted-foreground">
            VS markers survive copy-paste across browsers, email clients, text editors, and
            messaging platforms. When a reader copies text from a signed article and pastes
            it elsewhere, the markers copy with the text. The provenance data is present in
            every copy.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">ZWC Markers: Word-Safe Encoding</h2>
          <p className="text-muted-foreground mb-4">
            Microsoft Word handles certain Unicode ranges differently from web browsers
            and general text processors. Some zero-width characters are stripped during
            Word operations; others display as visible glyphs in certain fonts. The VS
            marker encoding can behave unexpectedly in Word documents.
          </p>
          <p className="text-muted-foreground mb-4">
            The ZWC encoding path uses a different set of zero-width characters that are
            stable in Word environments: ZWNJ (U+200C), ZWJ (U+200D), CGJ (U+034F),
            MVS (U+180E), LRM (U+200E), and RLM (U+200F). These six characters encode
            ternary or senary data and are optimized for the Microsoft Office processing
            pipeline.
          </p>
          <p className="text-muted-foreground">
            Publishers distributing content in Word format - legal documents, press briefings,
            editorial drafts, B2B document distribution - should use the ZWC path. The
            signing API accepts a parameter to select the encoding path. Verification
            handles both paths automatically.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Sentence-Level Merkle Tree Authentication</h2>
          <p className="text-muted-foreground mb-4">
            Standard C2PA provenance authenticates a document as a whole. The C2PA manifest
            records a hash of the entire document, and verification confirms that the document
            matches that hash. Any modification to the document breaks verification.
          </p>
          <p className="text-muted-foreground mb-4">
            Encypher's proprietary sentence-level Merkle tree technology authenticates each
            sentence individually. The structure works as follows:
          </p>
          <ol className="list-decimal list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>Each sentence in the document is hashed individually</li>
            <li>The sentence hashes form the leaves of a Merkle tree</li>
            <li>The Merkle root is included in the C2PA manifest signature</li>
            <li>Verification reconstructs the Merkle path for any target sentence</li>
          </ol>
          <p className="text-muted-foreground mb-4">
            This structure enables partial verification: a party can prove that a specific
            sentence belongs to a specific document and was published by a specific author,
            without needing the full document. This is the mechanism behind quote integrity
            verification.
          </p>
          <p className="text-muted-foreground">
            Sentence-level granularity is Encypher's proprietary technology. It is not
            defined in the C2PA specification. Encypher implements it as an extension to
            the C2PA manifest structure, compatible with standard C2PA verification while
            providing additional granularity for Encypher-signed content.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Quote Integrity Verification</h2>
          <p className="text-muted-foreground mb-4">
            When a sentence from a signed article is reproduced in another context - a
            summary, a citation, a quote in another article - the sentence carries its
            provenance markers. Verification confirms:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>The sentence was published in the claimed source article</li>
            <li>The sentence is unmodified from the original publication</li>
            <li>The publication date and author identity match the claimed source</li>
          </ul>
          <p className="text-muted-foreground mb-4">
            For RAG pipelines, quote integrity verification provides a quality signal that
            improves citation accuracy. Retrieved passages can be verified against the signed
            original before being included in AI-generated responses. If the retrieved text
            has been modified - by scraping errors, OCR artifacts, or deliberate manipulation
            - verification fails and the passage can be flagged.
          </p>
          <p className="text-muted-foreground">
            For copyright enforcement, sentence-level verification enables partial reproduction
            claims. If an AI company reproduces 50 sentences from a publisher's archive across
            multiple outputs, each sentence can be individually verified as originating from
            the publisher's signed content. This supports claims about specific, documented
            reproduction rather than statistical inference about training data composition.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">What Text Provenance Cannot Do</h2>
          <p className="text-muted-foreground mb-4">
            Text provenance has limits worth stating clearly. VS markers and ZWC markers
            survive copy-paste and most text distribution. They do not survive OCR (scanning
            physical text), heavy paraphrasing (rewriting the text in different words), or
            translation into another language.
          </p>
          <p className="text-muted-foreground mb-4">
            If an AI system paraphrases a sentence rather than reproducing it, the paraphrase
            does not carry the original sentence's markers. The provenance markers are in the
            specific Unicode character sequence, not in the semantic content. Paraphrase
            detection is a different problem than provenance verification, and text provenance
            does not solve it.
          </p>
          <p className="text-muted-foreground">
            Text provenance is designed for exact reproduction detection and ownership
            documentation. Combined with licensing terms in the manifest, it converts
            exact reproduction from an ambiguous infringement to a documented infringement
            with provable formal notice.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/c2pa-standard/section-a7" className="underline hover:no-underline">C2PA Section A.7: Technical Deep Dive</Link></li>
            <li><Link href="/content-provenance" className="underline hover:no-underline">Content Provenance: The Definitive Guide</Link></li>
            <li><Link href="/cryptographic-watermarking/text" className="underline hover:no-underline">Cryptographic Watermarking for Text</Link></li>
            <li><Link href="/content-provenance/for-publishers" className="underline hover:no-underline">Content Provenance for Publishers</Link></li>
            <li><Link href="/cryptographic-watermarking/survives-distribution" className="underline hover:no-underline">How Provenance Survives Distribution</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Add Text Provenance to Your Content</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Free tier covers 1,000 documents per month. Python and TypeScript SDKs available.
            Sentence-level Merkle tree authentication included at all tiers.
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
      </div>
    </>
  );
}
