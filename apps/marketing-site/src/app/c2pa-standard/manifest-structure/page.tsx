import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import AISummary from '@/components/seo/AISummary';
import { ArticleShell } from '@/components/content/ArticleShell';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@encypher/design-system';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'C2PA Manifest Structure: JUMBF, COSE, Claims, Assertions | Encypher',
  'Technical explainer of C2PA manifest structure. JUMBF containers, COSE signatures, claim structure, assertion types, certificate chains, and ingredient lists. Accessible to non-engineers.',
  '/c2pa-standard/manifest-structure',
  undefined,
  undefined,
  'JUMBF containers, COSE signatures, claims. How a manifest works.'
);

export default function ManifestStructurePage() {
  const techArticle = getTechArticleSchema({
    title: 'C2PA Manifest Structure: JUMBF, COSE, Claims, and Assertions',
    description: 'Technical explainer of C2PA manifest structure. JUMBF containers, COSE signatures, claim structure, assertion types, certificate chains, and ingredient lists.',
    url: `${siteConfig.url}/c2pa-standard/manifest-structure`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="C2PA Manifest Structure"
        whatWeDo="The C2PA manifest is a structured data package embedded in or alongside content. It contains claims about the content (what it is, who created it, when), cryptographic assertions (signed statements), and the COSE signature that proves who made the claims."
        whoItsFor="Developers implementing C2PA verification. Engineers building content provenance infrastructure. Anyone who needs to understand what a C2PA manifest contains and how its components relate."
        keyDifferentiator="JUMBF (JPEG Universal Metadata Box Format) is the container. COSE (CBOR Object Signing and Encryption) is the signature format. Claims are what is being asserted. Assertions are the specific claims. The certificate chain proves signer identity."
        primaryValue="Technical understanding of C2PA manifest structure to support implementation, verification, and evaluation of C2PA-based provenance infrastructure."
        pagePath="/c2pa-standard/manifest-structure"
        pageType="WebPage"
      />

      <Script
        id="tech-article-manifest-structure"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <ArticleShell path="/c2pa-standard/manifest-structure">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'C2PA Standard', href: '/c2pa-standard' },
          { name: 'Manifest Structure', href: '/c2pa-standard/manifest-structure' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          C2PA Manifest Structure
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          A C2PA manifest is a structured record of who created content, what was asserted
          about it, and a cryptographic proof that those assertions are authentic. Here is
          how the components fit together.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Container: JUMBF</h2>
          <p className="text-muted-foreground mb-4">
            JUMBF stands for JPEG Universal Metadata Box Format. It is an ISO standard
            (ISO 19566-5) for embedding structured metadata inside media files. Think of
            JUMBF as a container inside the container: the manifest data lives in a JUMBF
            structure that is itself stored inside the file format's own container.
          </p>
          <p className="text-muted-foreground mb-4">
            A JUMBF structure consists of boxes. Each box has a type label and a content
            payload. Boxes can be nested - a JUMBF box can contain other JUMBF boxes.
            The C2PA specification defines a specific JUMBF hierarchy for manifests:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>A top-level JUMBF box labeled as a C2PA manifest store</li>
            <li>One or more manifest boxes within the store (for content with history)</li>
            <li>Within each manifest: claim, signature, and assertion boxes</li>
          </ul>
          <p className="text-muted-foreground">
            The manifest store can contain multiple manifests, representing a content history.
            An image edited by multiple parties might carry a manifest store with the original
            creator's manifest and a subsequent editor's manifest. Each manifest extends the
            history without replacing prior manifests.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Signature: COSE</h2>
          <p className="text-muted-foreground mb-4">
            COSE stands for CBOR Object Signing and Encryption (RFC 8152). CBOR is a binary
            data format similar to JSON but more compact. COSE defines how CBOR objects are
            cryptographically signed. C2PA uses COSE_Sign1 (a single-signer signature format)
            to sign the manifest claim.
          </p>
          <p className="text-muted-foreground mb-4">
            The COSE signature contains:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>The protected header (signature algorithm, certificate chain)</li>
            <li>The unprotected header (additional metadata that is not signed)</li>
            <li>The payload (the signed claim data)</li>
            <li>The signature bytes (the cryptographic signature)</li>
          </ul>
          <p className="text-muted-foreground">
            The protected header includes the signer's X.509 certificate chain. This is what
            allows verification to establish identity: the certificate chain traces back to a
            Certificate Authority that vouches for the signer's identity. If you trust the CA,
            you can trust the signer's identity in the manifest.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Claim</h2>
          <p className="text-muted-foreground mb-4">
            The claim is the central assertion in a C2PA manifest. It is a CBOR-serialized
            data structure that records what the signer is asserting about the content at
            the time of signing. The COSE signature covers the claim, so the claim is
            tamper-evident: any modification to the claim after signing breaks the signature.
          </p>
          <p className="text-muted-foreground mb-4">
            The claim includes:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>The content hash (SHA-256 of the signed content, or of a specific data segment)</li>
            <li>References to assertion boxes (which assertions belong to this claim)</li>
            <li>The claim generator identifier (which software created this manifest)</li>
            <li>A timestamp (when the claim was created)</li>
          </ul>
          <p className="text-muted-foreground">
            The content hash is the link between the manifest and the content. If the content
            changes after the manifest is created, the hash in the claim no longer matches the
            content hash, and verification reports a mismatch. This is the tamper detection
            mechanism.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Assertions</h2>
          <p className="text-muted-foreground mb-4">
            Assertions are specific claims about the content. They are separate JUMBF boxes
            within the manifest that are referenced by the claim. The claim's reference list
            includes a hash of each assertion, so the assertions are also tamper-evident:
            modifying an assertion changes its hash and breaks the claim's reference.
          </p>
          <p className="text-muted-foreground mb-4">
            Common assertion types in C2PA manifests:
          </p>
          <div className="space-y-3">
            <div className="flex gap-3 items-start">
              <span className="font-mono text-xs bg-muted px-2 py-1 rounded h-fit">c2pa.actions</span>
              <p className="text-muted-foreground text-sm">Records what happened to the content: created, opened, edited, published. Each action has a timestamp and optionally an actor identity. AI-generated content carries a c2pa.ai.generated action.</p>
            </div>
            <div className="flex gap-3 items-start">
              <span className="font-mono text-xs bg-muted px-2 py-1 rounded h-fit">stds.schema-org.CreativeWork</span>
              <p className="text-muted-foreground text-sm">Schema.org metadata about the content: title, author, copyright notice, creation date. Structured as a JSON-LD object embedded in the manifest.</p>
            </div>
            <div className="flex gap-3 items-start">
              <span className="font-mono text-xs bg-muted px-2 py-1 rounded h-fit">c2pa.hash.data</span>
              <p className="text-muted-foreground text-sm">The data hash assertion: a SHA-256 hash of the content data. This is what links the manifest to the specific content and detects tampering.</p>
            </div>
            <div className="flex gap-3 items-start">
              <span className="font-mono text-xs bg-muted px-2 py-1 rounded h-fit">c2pa.rights</span>
              <p className="text-muted-foreground text-sm">Machine-readable rights terms. Encypher uses this for Bronze/Silver/Gold tier licensing terms that AI systems can parse.</p>
            </div>
            <div className="flex gap-3 items-start">
              <span className="font-mono text-xs bg-muted px-2 py-1 rounded h-fit">c2pa.location.precise</span>
              <p className="text-muted-foreground text-sm">GPS coordinates for photojournalism. Records where the content was captured.</p>
            </div>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Certificate Chain</h2>
          <p className="text-muted-foreground mb-4">
            The certificate chain in the COSE protected header establishes signer identity.
            The chain follows the X.509 certificate standard: a leaf certificate identifying
            the signer, signed by an intermediate certificate, signed by a root Certificate
            Authority (CA).
          </p>
          <p className="text-muted-foreground mb-4">
            When verifying, the verifier checks:
          </p>
          <ol className="list-decimal list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>The leaf certificate is signed by the intermediate</li>
            <li>The intermediate is signed by the root CA</li>
            <li>The root CA is trusted (in the verifier's trust anchor list)</li>
            <li>None of the certificates have been revoked</li>
            <li>The certificates were valid at the time of signing (timestamp check)</li>
          </ol>
          <p className="text-muted-foreground">
            For Encypher-signed content, the leaf certificate identifies the publisher (or
            Encypher on behalf of the publisher). The intermediate and root CAs are operated
            by a trusted Certificate Authority. Enterprise customers with BYOK can use their
            own certificate infrastructure.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Ingredient Lists</h2>
          <p className="text-muted-foreground mb-4">
            When content is created from other signed content - an edited image derived from
            an original, a document that incorporates a signed image - the manifest can include
            an ingredient list. Each ingredient references another C2PA-signed asset and records
            how it was used.
          </p>
          <p className="text-muted-foreground mb-4">
            This creates provenance chains: the derivative content's manifest proves it
            was derived from specific signed originals. For editorial workflows where images
            are cropped, color-corrected, or composed into layouts, the ingredient list
            documents the full lineage.
          </p>
          <p className="text-muted-foreground">
            The Encypher API supports ingredient relationships in signing requests. The
            /sign/media endpoint accepts ingredient identifiers that reference previously
            signed assets. The resulting manifest includes the ingredient relationships
            in accordance with the C2PA specification.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">What a Verification Result Looks Like</h2>
          <p className="text-muted-foreground mb-4">
            When you verify a C2PA-signed file, the output maps directly to the manifest
            structure described above:
          </p>
          <div className="bg-muted/30 rounded-lg p-4 font-mono text-sm">
            <p>{`{`}</p>
            <p className="ml-4">{`"active_manifest": {`}</p>
            <p className="ml-8">{`"claim_generator": "Encypher/1.0",`}</p>
            <p className="ml-8">{`"signer": "Publisher Corp",`}</p>
            <p className="ml-8">{`"timestamp": "2026-03-15T14:23:00Z",`}</p>
            <p className="ml-8">{`"assertions": [`}</p>
            <p className="ml-12">{`{ "label": "c2pa.actions", "value": [{"action": "c2pa.published"}] },`}</p>
            <p className="ml-12">{`{ "label": "c2pa.rights", "value": "bronze" }`}</p>
            <p className="ml-8">{`],`}</p>
            <p className="ml-8">{`"hash_match": true,`}</p>
            <p className="ml-8">{`"signature_valid": true`}</p>
            <p className="ml-4">{`}`}</p>
            <p>{`}`}</p>
          </div>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/c2pa-standard" className="underline hover:no-underline">The C2PA Standard</Link></li>
            <li><Link href="/c2pa-standard/implementation-guide" className="underline hover:no-underline">Implementation Guide for Developers</Link></li>
            <li><Link href="/c2pa-standard/media-types" className="underline hover:no-underline">Supported Media Types</Link></li>
            <li><Link href="/content-provenance/verification" className="underline hover:no-underline">Verification: How It Works</Link></li>
            <li><Link href="/c2pa-standard/section-a7" className="underline hover:no-underline">Section A.7: Text Provenance</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">See a Manifest in Action</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            The verification tool shows the full manifest contents for any C2PA-signed content.
            No account required.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/tools/verify">Verify Content</Link>
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
