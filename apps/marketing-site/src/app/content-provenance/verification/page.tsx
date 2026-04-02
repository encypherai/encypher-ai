import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'Content Provenance Verification: Free for All Media Types | Encypher',
  'Free verification for 31 MIME types. No authentication required. Public API. Verify text, images, audio, video, and documents instantly. How C2PA manifest verification works.',
  '/content-provenance/verification'
);

export default function VerificationPage() {
  const techArticle = getTechArticleSchema({
    title: 'Content Provenance Verification',
    description: 'Free verification for 31 MIME types. No authentication required. Public API. How C2PA manifest extraction, signature validation, and hash comparison work.',
    url: `${siteConfig.url}/content-provenance/verification`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'Is verification really free and does it require an account?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Yes, verification is free for any content type and does not require an account or API key. Anyone can verify C2PA-signed content by uploading it to the Encypher verification tool or using the public verification API endpoint. The public endpoint does not require authentication. This is a deliberate design choice - verification should be accessible to any party, including journalists, courts, regulators, and opposing counsel.',
        },
      },
      {
        '@type': 'Question',
        name: 'What does verification tell you?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Verification returns the contents of the C2PA manifest if one is present and valid. This includes: signer identity (who signed the content and when), content hash (SHA-256 of the signed content), assertions (rights terms, authorship claims, and other structured claims the signer embedded), and tamper status (whether the content matches the signed hash). If no manifest is present, verification returns that result. If the manifest is present but the signature is invalid or the content does not match the hash, verification returns the specific failure reason.',
        },
      },
      {
        '@type': 'Question',
        name: 'Can verification confirm specific sentences in a text document?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'For content signed with Encypher\'s sentence-level Merkle tree authentication, yes. The verification API accepts a target sentence and returns whether that sentence is authenticated in the signed document, including its position in the document and its Merkle path. This supports partial verification for quote integrity checking.',
        },
      },
      {
        '@type': 'Question',
        name: 'Does verification require internet access?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'For basic signature verification, no. The C2PA verification libraries are open source and can verify manifests locally using the public key embedded in the manifest\'s certificate chain. The only internet access needed is to check certificate revocation status, which is optional. Enterprise customers can run the verification library entirely within their own infrastructure.',
        },
      },
    ],
  };

  const supportedTypes = [
    { category: 'Images (13)', types: 'JPEG, PNG, WebP, TIFF, AVIF, HEIC, HEIC-Sequence, HEIF, HEIF-Sequence, SVG, DNG, GIF, JPEG XL' },
    { category: 'Audio (6)', types: 'WAV, MP3, M4A, AAC, FLAC, MPA' },
    { category: 'Video (4)', types: 'MP4, MOV, M4V, AVI' },
    { category: 'Documents (5)', types: 'PDF, EPUB, DOCX, ODT, OXPS' },
    { category: 'Fonts (3)', types: 'OTF, TTF, SFNT' },
  ];

  return (
    <>
      <AISummary
        title="Content Provenance Verification"
        whatWeDo="Encypher provides free public verification for C2PA-signed content across 31 MIME types. No account required. The verification API extracts the C2PA manifest, validates the cryptographic signature, and compares the content hash to confirm authenticity."
        whoItsFor="Anyone who receives content and wants to verify its provenance. Journalists verifying source material, courts examining documentary evidence, AI companies checking content licenses, and publishers confirming distribution channel integrity."
        keyDifferentiator="Verification is free, public, and requires no account. It is available to any party - including opposing counsel, regulators, and fact-checkers. The openness of verification is a feature: provenance that only the publisher can verify does not create the third-party trust that useful provenance requires."
        primaryValue="Instant verification for any signed content. Works on all 31 supported types. Returns full manifest contents including signer identity, timestamps, rights terms, and tamper status."
        pagePath="/content-provenance/verification"
        pageType="WebPage"
      />

      <Script
        id="tech-article-verification"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />
      <Script
        id="faq-verification"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <ArticleShell path="/content-provenance/verification">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Content Provenance', href: '/content-provenance' },
          { name: 'Verification', href: '/content-provenance/verification' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Content Provenance Verification
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          Free verification for all 31 supported media types. No account required.
          Verify the provenance of any C2PA-signed content in seconds.
        </p>

        <div className="mb-12 flex flex-col sm:flex-row gap-4">
          <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
            <Link href="/tools/verify">Verify Content Now</Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href="/try">Sign Content Free</Link>
          </Button>
        </div>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">How Verification Works</h2>
          <p className="text-muted-foreground mb-4">
            C2PA verification is a three-step process. Each step is independently verifiable
            and can be performed with open-source libraries without trusting any third party.
          </p>

          <div className="space-y-4">
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-2">Step 1: Manifest Extraction</h3>
              <p className="text-muted-foreground text-sm">
                The C2PA manifest is extracted from the content. For images, this means
                locating the JUMBF box in the file container (after the EOI marker for JPEG,
                in a PNG chunk for PNG, in a uuid box for ISO BMFF formats). For text, this
                means extracting the manifest data from the embedded Unicode markers. The
                extracted manifest is a structured CBOR (Concise Binary Object Representation)
                document containing all claims and assertions.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-2">Step 2: Signature Validation</h3>
              <p className="text-muted-foreground text-sm">
                The COSE (CBOR Object Signing and Encryption) signature in the manifest is
                validated against the signer's certificate. The certificate chain is verified
                up to a trusted root. This step confirms that the manifest was genuinely
                created by the claimed signer and has not been altered since signing. If the
                certificate has been revoked, that status is checked against the CA's
                revocation list.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-2">Step 3: Content Hash Comparison</h3>
              <p className="text-muted-foreground text-sm">
                The current content is hashed and compared against the hash recorded in
                the signed manifest. If they match, the content is unmodified since signing.
                If they do not match, the content has been altered after the manifest was
                created. This step is format-specific: for images, the pixel data is hashed;
                for text, the Unicode character sequence (excluding provenance markers) is
                hashed; for audio and video, the media data track is hashed.
              </p>
            </div>
          </div>

          <p className="text-muted-foreground mt-4">
            Verification returns a result for each step. A complete verification result includes
            the manifest contents (if valid), the signature status (valid, invalid, or untrusted),
            and the hash comparison result (match or mismatch). A content can have a valid
            signature but a hash mismatch - this means the manifest is genuine but the content
            was modified after signing.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Supported Media Types</h2>
          <div className="space-y-3">
            {supportedTypes.map(item => (
              <div key={item.category} className="flex gap-4 items-start">
                <span className="font-semibold text-sm w-32 shrink-0 pt-0.5">{item.category}</span>
                <span className="text-muted-foreground text-sm">{item.types}</span>
              </div>
            ))}
          </div>
          <p className="text-muted-foreground mt-4 text-sm">
            All 31 types are supported at the verification endpoint. See the <Link href="/c2pa-standard/media-types" className="underline hover:no-underline">media types reference</Link> for format-specific embedding details.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Verification API</h2>
          <p className="text-muted-foreground mb-4">
            The public verification endpoint requires no authentication:
          </p>
          <div className="bg-muted/30 rounded-lg p-4 font-mono text-sm mb-4">
            <p className="text-muted-foreground mb-2"># Verify a text document (no auth required)</p>
            <p className="mb-1">curl -X POST https://api.encypher.com/v1/verify \</p>
            <p className="mb-1 ml-4">-H "Content-Type: application/json" \</p>
            <p className="mb-4 ml-4">{`-d '{"text": "Your content here"}'`}</p>
            <p className="text-muted-foreground mb-2"># Verify an image file (no auth required)</p>
            <p className="mb-1">curl -X POST https://api.encypher.com/v1/verify \</p>
            <p className="mb-1 ml-4">-F "file=@image.jpg"</p>
          </div>
          <p className="text-muted-foreground mb-4">
            The response includes the manifest contents if verification succeeds:
          </p>
          <div className="bg-muted/30 rounded-lg p-4 font-mono text-sm">
            <p>{`{`}</p>
            <p className="ml-4">{`"verified": true,`}</p>
            <p className="ml-4">{`"signer": {`}</p>
            <p className="ml-8">{`"name": "Encypher Publishing Corp",`}</p>
            <p className="ml-8">{`"certificate": "..."  `}</p>
            <p className="ml-4">{`},`}</p>
            <p className="ml-4">{`"timestamp": "2026-03-15T14:23:00Z",`}</p>
            <p className="ml-4">{`"hash_match": true,`}</p>
            <p className="ml-4">{`"assertions": [`}</p>
            <p className="ml-8">{`{ "label": "c2pa.rights", "value": "bronze" },`}</p>
            <p className="ml-8">{`{ "label": "c2pa.author", "value": "Jane Smith" }`}</p>
            <p className="ml-4">{`]`}</p>
            <p>{`}`}</p>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Text Verification and Quote Integrity</h2>
          <p className="text-muted-foreground mb-4">
            Text verification extracts provenance from the invisible Unicode markers embedded
            in the text. The markers encode the C2PA manifest data. Verification strips the
            markers from the text, reconstructs the manifest, and verifies the signature.
          </p>
          <p className="text-muted-foreground mb-4">
            For content signed with Encypher's sentence-level Merkle tree authentication,
            the verification API supports quote integrity queries: submit a specific sentence
            and a claimed source document, and verification returns whether that sentence is
            cryptographically authenticated in the source document.
          </p>
          <p className="text-muted-foreground">
            This is the mechanism behind quote integrity verification for RAG pipelines.
            An AI system retrieving sentences from a corpus can verify each retrieved sentence
            against its claimed source before including it in a response. If the sentence
            has been altered in the corpus - through scraping errors, OCR artifacts, or
            deliberate modification - verification fails.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Open-Source Verification Libraries</h2>
          <p className="text-muted-foreground mb-4">
            The C2PA verification specification is open. The verification process can be
            implemented independently of Encypher using open-source libraries:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>c2pa-python: Python library for C2PA manifest reading and verification</li>
            <li>c2pa-js: JavaScript/TypeScript library for browser and Node.js verification</li>
            <li>c2pa-rs: Rust implementation underlying both Python and JS libraries</li>
          </ul>
          <p className="text-muted-foreground">
            These libraries verify manifests entirely locally, without any network requests
            to Encypher or any third party (except optional certificate revocation checks).
            Enterprise customers who require zero external dependencies for verification
            can use these libraries within their own infrastructure.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/tools/verify" className="underline hover:no-underline">Verification Tool (no account needed)</Link></li>
            <li><Link href="/content-provenance" className="underline hover:no-underline">Content Provenance: The Definitive Guide</Link></li>
            <li><Link href="/c2pa-standard/manifest-structure" className="underline hover:no-underline">C2PA Manifest Structure</Link></li>
            <li><Link href="/c2pa-standard/media-types" className="underline hover:no-underline">All 31 Supported Media Types</Link></li>
            <li><Link href="/c2pa-standard/implementation-guide" className="underline hover:no-underline">Implementation Guide for Developers</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Verify Content Now</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Free verification for all 31 media types. No account, no API key, no limit.
            Upload or paste content and get verification results in under a second.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/tools/verify">Verify Content</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/try">Start Signing Free</Link>
            </Button>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
