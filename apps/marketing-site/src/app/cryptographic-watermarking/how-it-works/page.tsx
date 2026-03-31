import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'How Cryptographic Watermarking Works | Technical Deep Dive | Encypher',
  'Technical deep dive into cryptographic watermarking: VS markers, ZWC markers, sentence-level Merkle trees, and C2PA JUMBF manifest embedding. How text and media provenance works.',
  '/cryptographic-watermarking/how-it-works'
);

export default function HowItWorksPage() {
  const techArticle = getTechArticleSchema({
    title: 'How Cryptographic Watermarking Works',
    description: 'Technical deep dive into VS markers, ZWC markers, Merkle tree authentication, and C2PA JUMBF embedding. How text and media provenance is implemented.',
    url: `${siteConfig.url}/cryptographic-watermarking/how-it-works`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="How Cryptographic Watermarking Works"
        whatWeDo="Encypher embeds cryptographic provenance using two technology stacks: for text, invisible Unicode variation selector markers with sentence-level Merkle tree authentication; for media, C2PA JUMBF manifests in format-native container locations."
        whoItsFor="Developers, security engineers, and technical decision-makers evaluating content provenance infrastructure. Anyone who needs to understand the technical implementation before adopting or recommending Encypher."
        keyDifferentiator="VS markers and sentence-level Merkle tree authentication are Encypher's proprietary technology. They are not C2PA features - they extend the C2PA standard. C2PA JUMBF embedding for media files follows the open standard. These are distinct technology layers."
        primaryValue="Technical accuracy about what is Encypher-proprietary versus what is the open C2PA standard. Practical understanding of the implementation for evaluation and integration."
        pagePath="/cryptographic-watermarking/how-it-works"
        pageType="WebPage"
      />

      <Script
        id="tech-article-how-it-works"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
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
          For text, this uses invisible Unicode characters. For media files, this uses
          format-native container structures. Both are cryptographically signed and
          independently verifiable.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Two Technology Layers</h2>
          <p className="text-muted-foreground mb-4">
            Encypher's cryptographic watermarking implementation has two distinct layers
            that are worth understanding separately:
          </p>
          <div className="space-y-4 mb-4">
            <div className="p-4 bg-muted/30 rounded-lg border-l-4 border-[#2a87c4]">
              <h3 className="font-semibold mb-1">Layer 1: C2PA Standard (Open)</h3>
              <p className="text-muted-foreground text-sm">
                The C2PA manifest structure, JUMBF container format, COSE signature scheme, and
                media file embedding locations. This layer is defined by the open C2PA specification,
                implemented by multiple vendors, and verifiable with open-source libraries.
                Encypher contributed Section A.7 (text provenance) to this standard.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg border-l-4 border-[#2a87c4]">
              <h3 className="font-semibold mb-1">Layer 2: Encypher Proprietary Extensions</h3>
              <p className="text-muted-foreground text-sm">
                VS marker encoding (variation selector Unicode characters), sentence-level
                Merkle tree authentication, HMAC-based distribution fingerprinting, and
                pHash attribution search. These are Encypher's proprietary technology.
                They build on the C2PA standard without breaking standard verification,
                but require Encypher's implementation for their specific capabilities.
              </p>
            </div>
          </div>
          <p className="text-muted-foreground">
            This distinction matters because it determines what you can rely on independently
            versus what requires Encypher's infrastructure. C2PA manifest verification works
            with open-source tools for any C2PA-signed content. Sentence-level Merkle tree
            verification requires Encypher's extended verification.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Text: VS Markers (Default)</h2>
          <p className="text-muted-foreground mb-4">
            Encypher's primary text encoding uses Unicode variation selectors (VS markers).
            Unicode allocates 256 variation selector code points across two ranges:
            U+FE00 through U+FE0F and U+E0100 through U+E01EF. These characters are designed
            to specify alternative glyph renderings for preceding characters.
          </p>
          <p className="text-muted-foreground mb-4">
            In practice, variation selectors placed after common Latin characters have no
            rendering effect - no alternative glyph is defined for most Latin-variation
            selector combinations. The selectors are invisible in rendered output.
          </p>
          <p className="text-muted-foreground mb-4">
            The 256 available selectors encode 8 bits per character. The C2PA manifest
            (serialized as CBOR) is encoded as a sequence of variation selectors placed
            at defined positions within the text. The specific placement algorithm follows
            C2PA Section A.7. From the reader's perspective, the text is character-for-character
            identical to unsigned text. No visual difference is present.
          </p>
          <p className="text-muted-foreground">
            VS markers survive copy-paste across all major browsers, email clients, and text
            processing environments. Unicode-compliant text processors preserve unknown
            variation selectors in copy operations. The markers are stable through the typical
            text distribution workflows that publishers use.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Text: ZWC Markers (Word-Safe)</h2>
          <p className="text-muted-foreground mb-4">
            For content distributed in Microsoft Word format, Encypher uses zero-width
            character markers (ZWC markers). This encoding uses six specific Unicode characters
            that are stable through Word's document processing operations:
          </p>
          <div className="overflow-x-auto mb-4">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 pr-4 font-semibold">Character</th>
                  <th className="text-left py-3 pr-4 font-semibold">Unicode</th>
                  <th className="text-left py-3 font-semibold">Value</th>
                </tr>
              </thead>
              <tbody className="text-muted-foreground">
                <tr className="border-b border-border/50">
                  <td className="py-2 pr-4">ZWNJ (Zero Width Non-Joiner)</td>
                  <td className="py-2 pr-4 font-mono text-xs">U+200C</td>
                  <td className="py-2">0</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-2 pr-4">ZWJ (Zero Width Joiner)</td>
                  <td className="py-2 pr-4 font-mono text-xs">U+200D</td>
                  <td className="py-2">1</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-2 pr-4">CGJ (Combining Grapheme Joiner)</td>
                  <td className="py-2 pr-4 font-mono text-xs">U+034F</td>
                  <td className="py-2">2</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-2 pr-4">MVS (Mongolian Vowel Separator)</td>
                  <td className="py-2 pr-4 font-mono text-xs">U+180E</td>
                  <td className="py-2">3</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-2 pr-4">LRM (Left-to-Right Mark)</td>
                  <td className="py-2 pr-4 font-mono text-xs">U+200E</td>
                  <td className="py-2">4</td>
                </tr>
                <tr>
                  <td className="py-2 pr-4">RLM (Right-to-Left Mark)</td>
                  <td className="py-2 pr-4 font-mono text-xs">U+200F</td>
                  <td className="py-2">5</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="text-muted-foreground mb-4">
            Six characters allow base-6 (senary) encoding. The encoding is less information-dense
            than VS markers but stable in Word environments where certain other zero-width
            characters are stripped.
          </p>
          <p className="text-muted-foreground">
            The ZWSP (Zero Width Space, U+200B) is specifically excluded from this character set.
            Word strips ZWSP during certain operations. CGJ and MVS may display as visible glyphs
            in certain fonts on certain versions of Word - this is a known Word behavior and the
            encoding is designed to minimize the impact of this edge case.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Sentence-Level Merkle Tree Authentication</h2>
          <p className="text-muted-foreground mb-4">
            Standard C2PA provenance authenticates a document as a whole: one hash covers
            the entire content. Encypher's sentence-level Merkle tree extends this to
            authenticate each sentence individually.
          </p>
          <p className="text-muted-foreground mb-4">
            The construction:
          </p>
          <ol className="list-decimal list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>The document is segmented into sentences using a deterministic sentence boundary detection algorithm</li>
            <li>Each sentence is hashed individually with SHA-256</li>
            <li>The sentence hashes form the leaf nodes of a Merkle tree</li>
            <li>Internal nodes are computed by hashing pairs of child nodes</li>
            <li>The Merkle root is included in the C2PA manifest as a custom assertion</li>
            <li>The manifest is signed with the signer's private key</li>
          </ol>
          <p className="text-muted-foreground mb-4">
            To verify a specific sentence, the verifier computes the Merkle path from the
            sentence's leaf to the root and checks that the path matches the signed root.
            This requires only the target sentence, the Merkle path (a logarithmic-size
            sibling hash sequence), and the signed root from the manifest.
          </p>
          <p className="text-muted-foreground">
            This is Encypher's proprietary technology. It is not defined in the current
            C2PA specification. It is implemented as a custom assertion type in the C2PA
            manifest, compatible with standard C2PA verification (which ignores unknown
            assertion types) while providing additional granularity for Encypher-aware verifiers.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Media: JUMBF Manifest Embedding</h2>
          <p className="text-muted-foreground mb-4">
            For images, audio, and video, Encypher follows the C2PA specification for
            format-native manifest embedding. The C2PA manifest is packaged in a JUMBF
            (JPEG Universal Metadata Box Format) container and placed in the format-standard
            location for extension data.
          </p>
          <p className="text-muted-foreground mb-4">
            Container types by format category:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>JPEG: JUMBF box appended after the End of Image (EOI) marker</li>
            <li>PNG: JUMBF data in a custom PNG chunk</li>
            <li>ISO BMFF (MP4, MOV, AVIF, HEIC): JUMBF in a uuid box</li>
            <li>RIFF (WAV, AVI): JUMBF in a RIFF chunk</li>
            <li>MP3: JUMBF in an ID3v2 GEOB (General Encapsulated Object) frame</li>
          </ul>
          <p className="text-muted-foreground mb-4">
            The JUMBF container holds the C2PA manifest: the claim (content hash, assertion
            references, timestamp), the assertions (specific claims about the content), and
            the COSE signature (cryptographic proof of the claim).
          </p>
          <p className="text-muted-foreground">
            This is entirely defined by the C2PA specification. Encypher's contribution here
            is implementation correctness and API accessibility, not proprietary technology.
            Any C2PA-compliant tool can verify the manifests Encypher embeds in media files.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">HMAC Fingerprinting</h2>
          <p className="text-muted-foreground mb-4">
            Enterprise-tier accounts can use distribution fingerprinting to embed recipient-specific
            markers into distributed content. When the same document is distributed to multiple
            recipients, each copy carries unique markers that identify which recipient received
            which copy.
          </p>
          <p className="text-muted-foreground mb-4">
            The implementation uses HMAC-based pseudorandom number generation (HMAC-DRBG) to
            determine marker positions. The HMAC key is derived from the recipient identifier
            and a document-specific secret. The same recipient always gets the same marker
            positions for the same document, but different recipients get different positions.
          </p>
          <p className="text-muted-foreground">
            When a fingerprinted document leaks, fingerprint analysis examines the marker
            positions in the leaked copy and identifies the recipient whose fingerprint matches.
            This is used for identifying leak sources in pre-publication content, confidential
            documents, and restricted distribution materials.
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
            Sentence-level Merkle tree authentication at all tiers.
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
      </div>
    </>
  );
}
