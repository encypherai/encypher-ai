import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import Script from 'next/script';
import Link from 'next/link';
import { getCompareMetadata, getTechArticleSchema, getBreadcrumbSchema, siteConfig } from '@/lib/seo';
import type { Metadata } from 'next';
import { ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';

export const metadata: Metadata = getCompareMetadata(
  'c2pa-vs-blockchain',
  'C2PA vs Blockchain for Content Provenance: Embedded Manifests vs External Hash Anchoring',
  "C2PA manifests are embedded in the file and travel with it. Blockchain proofs are external records that require a lookup. A technical comparison of the two architectural approaches to content provenance."
);

const PAGE_URL = `${siteConfig.url}/compare/c2pa-vs-blockchain`;
const DATE = '2026-03-31';

const techArticleSchema = getTechArticleSchema({
  headline: 'C2PA vs Blockchain for Content Provenance: Embedded Manifests vs External Hash Anchoring',
  description: "A technical comparison of C2PA manifest embedding and blockchain hash anchoring as approaches to content provenance. Architecture, trade-offs, standards backing.",
  url: PAGE_URL,
  datePublished: DATE,
});

const breadcrumbSchema = getBreadcrumbSchema([
  { name: 'Home', url: siteConfig.url },
  { name: 'Compare', url: `${siteConfig.url}/compare` },
  { name: 'C2PA vs Blockchain', url: PAGE_URL },
]);

const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is C2PA?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The Coalition for Content Provenance and Authenticity (C2PA) is an industry standards body with over 200 member organizations including Adobe, Microsoft, Google, OpenAI, the BBC, Reuters, and the Associated Press. The C2PA standard defines how content provenance metadata is embedded inside digital files - images, video, audio, and documents - using JUMBF containers and COSE digital signatures. The manifest travels with the file, not in a separate record."
      }
    },
    {
      "@type": "Question",
      "name": "How does blockchain content provenance work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Blockchain content provenance works by hashing a document and recording the hash on a blockchain. The hash is a short cryptographic fingerprint of the document; if the document changes, the hash changes. Recording it on a public blockchain creates a timestamped, immutable record that the document existed in that exact state at that time. Verification requires querying the blockchain, finding the hash record, and comparing it to the current document hash."
      }
    },
    {
      "@type": "Question",
      "name": "What is the main architectural difference between C2PA and blockchain provenance?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "C2PA embeds provenance metadata inside the file. The manifest, including signatures and provenance claims, is part of the file and travels wherever the file goes. Blockchain provenance is external: the file and the proof are separate. The file is on your server or distributed across the web; the proof is on the blockchain. This means C2PA provenance is available offline and without network calls; blockchain provenance requires looking up a record."
      }
    },
    {
      "@type": "Question",
      "name": "What happens when content is stripped of metadata?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "For C2PA: stripping is detectable. Removing the C2PA manifest is itself a tamper event. Content that arrives without a manifest, when it was known to have one, indicates manipulation. The original signed record on the Content Credentials infrastructure shows the manifest was present. For blockchain: stripping has no visible consequence because the proof and the content are already separate. The file just circulates without any indication that a blockchain record exists."
      }
    },
    {
      "@type": "Question",
      "name": "Which approach is better for AI training data provenance?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "C2PA is better suited for AI training data provenance. When AI systems scrape content, they process the file contents - text, images, metadata. A C2PA manifest embedded in the file is present in the scraped content. A blockchain record is not scraped alongside the content; it is a separate entry on a separate system. For content that needs to carry its provenance into AI pipelines, an embedded approach is architecturally stronger."
      }
    },
    {
      "@type": "Question",
      "name": "Is blockchain content provenance reliable long-term?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "It depends on the blockchain. Records on major public blockchains (Ethereum, Bitcoin) are highly durable. Records on smaller or experimental blockchains carry significant longevity risk. If the chain is abandoned or forked, historical records may become inaccessible. C2PA provenance stored in the file itself is durable as long as the file exists, with no dependency on any network or service remaining operational."
      }
    }
  ]
};

function ComparisonRow({ feature, c2pa, blockchain, c2paPositive = true, blockchainPositive = false }: {
  feature: string;
  c2pa: string;
  blockchain: string;
  c2paPositive?: boolean;
  blockchainPositive?: boolean;
}) {
  return (
    <tr className="border-b border-border hover:bg-muted/20 transition-colors">
      <td className="py-3 px-4 font-medium text-sm">{feature}</td>
      <td className="py-3 px-4 text-sm">
        <span className="flex items-start gap-2">
          {c2paPositive
            ? <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
            : <AlertCircle className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
          }
          {c2pa}
        </span>
      </td>
      <td className="py-3 px-4 text-sm text-muted-foreground">
        <span className="flex items-start gap-2">
          {blockchainPositive
            ? <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
            : <AlertCircle className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
          }
          {blockchain}
        </span>
      </td>
    </tr>
  );
}

export default function C2PAVsBlockchainPage() {
  return (
    <>
      <AISummary
        title="C2PA vs Blockchain for Content Provenance"
        whatWeDo="A technical comparison of C2PA embedded manifests and blockchain hash anchoring as approaches to content provenance. Covers architecture, verification speed, standards, and trade-offs."
        whoItsFor="Developers, architects, publishers, and enterprises evaluating content provenance infrastructure."
        keyDifferentiator="C2PA manifests are embedded in the file and travel with it. Blockchain proofs are external records requiring a lookup. The architectural difference determines behavior in offline, distributed, and AI pipeline contexts."
        primaryValue="C2PA is the industry standard backed by 200+ organizations. It provides offline verification, no vendor dependency, and provenance that follows the file everywhere."
        pagePath="/compare/c2pa-vs-blockchain"
      />
      <Script id="tech-article-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticleSchema) }} />
      <Script id="breadcrumb-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      <Script id="faq-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Compare', href: '/compare' },
          { name: 'C2PA vs Blockchain', href: '/compare/c2pa-vs-blockchain' },
        ]} />

        <div className="mb-4 text-sm text-muted-foreground bg-muted/30 border border-border rounded px-4 py-2 inline-block">
          Category-level comparison - not specific to any vendor
        </div>

        <h1 className="text-4xl font-bold tracking-tight mb-4">
          C2PA vs Blockchain for Content Provenance
        </h1>
        <p className="text-xl text-muted-foreground mb-10">
          Two architectural approaches to proving content provenance: C2PA embeds the manifest inside the file, blockchain anchors a hash in an external ledger. The choice has consequences for distribution, verification, and AI pipeline behavior.
        </p>

        {/* What Each Approach Is */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Two Approaches to Content Provenance</h2>
          <p className="mb-4">
            Both C2PA and blockchain provenance solve the same core problem: how do you prove that a specific piece of content was created by a specific party at a specific time, and that it has not been altered since?
          </p>
          <p className="mb-4">
            They reach different answers to the question of where to store the proof.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-6">
            <div className="border rounded-lg p-6" style={{ borderColor: '#2a87c4' }}>
              <h3 className="font-semibold mb-3">C2PA: Embedded Manifests</h3>
              <p className="text-sm text-muted-foreground mb-3">
                The Coalition for Content Provenance and Authenticity standard defines a container format (JUMBF) for embedding provenance metadata directly inside a digital file. The container includes COSE-signed claims: who created the content, when, with what tools, and what has happened to it since.
              </p>
              <p className="text-sm text-muted-foreground">
                The manifest is part of the file. The file and the proof travel together. Verification requires only the file and the signer's public key - no network call, no external lookup.
              </p>
            </div>
            <div className="border border-border rounded-lg p-6">
              <h3 className="font-semibold mb-3">Blockchain: External Hash Anchoring</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Blockchain content provenance creates a hash of the document and records it on a distributed ledger. The hash is immutable and timestamped by the blockchain's consensus mechanism. Anyone who has the document and can query the blockchain can verify whether a record exists.
              </p>
              <p className="text-sm text-muted-foreground">
                The blockchain record and the document are separate. Verification requires querying the chain, finding the matching hash record, and comparing. The file itself carries no provenance metadata.
              </p>
            </div>
          </div>
        </section>

        {/* C2PA Technical Architecture */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">C2PA Technical Architecture</h2>
          <p className="mb-4">
            The C2PA standard specifies content provenance at two levels: the container format and the signing model.
          </p>
          <p className="mb-4">
            The container is JUMBF (JPEG Universal Metadata Box Format), which is an ISO standard for metadata boxes in media files. JUMBF provides a structured way to embed arbitrary metadata inside image, video, audio, and document formats without affecting the content itself.
          </p>
          <p className="mb-4">
            The signing model uses COSE (CBOR Object Signing and Encryption), an IETF standard for cryptographic signing and encryption. Each provenance claim is signed with the creator's or publisher's private key. A C2PA manifest can contain multiple claim generators, representing the chain of custody from original creation through any subsequent processing.
          </p>
          <p className="mb-4">
            For text content, the C2PA Section A.7 specification - contributed by Encypher, with co-chair Erik Svilich leading the Text Provenance Task Force - defines how sentence-level granularity is achieved. Rather than signing the document as a whole, Section A.7 enables signing at individual content segment level, producing a Merkle tree where each node represents a segment and the root represents the document.
          </p>
          <p className="mb-4">
            Verification against a C2PA manifest requires the signed content, the manifest, and the signer's public key (or a certificate chain to a trusted root). The Content Credentials infrastructure maintained by the C2PA provides a public lookup for signer certificates, but verification of the signature itself is local - no network call required.
          </p>
        </section>

        {/* Blockchain Architecture */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Blockchain Hash Anchoring Architecture</h2>
          <p className="mb-4">
            Blockchain content provenance typically works in three steps. First, a hash of the document is computed. Second, a transaction is submitted to the blockchain containing the hash, the claimant's address or identity, and a timestamp. Third, when the transaction is confirmed, the record is immutable: the blockchain's consensus mechanism makes retroactive modification computationally infeasible.
          </p>
          <p className="mb-4">
            The hash can use any standard algorithm (SHA-256 is common). Some implementations add additional metadata to the transaction - the claimant's name, the document type, associated URLs - but the core proof is the hash-timestamp pair.
          </p>
          <p className="mb-4">
            Verification requires: the document (to recompute the hash), the blockchain address or transaction ID where the record was stored, and network access to query the blockchain. On a public chain, this is permissionless: anyone can verify without trusting a third party. On a private or permissioned chain, verification requires network access to that specific chain.
          </p>
          <p className="mb-4">
            Gas costs (on chains like Ethereum) add a per-transaction cost to each provenance record. At scale - a large publisher signing millions of documents - these costs are material. Some implementations batch-hash multiple documents into a single transaction to reduce costs, using Merkle trees to maintain per-document proofs.
          </p>
        </section>

        {/* The Embedded vs External Trade-Off */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Embedded vs External Trade-Off</h2>
          <p className="mb-4">
            The most consequential difference between the two approaches is what happens to the proof when the content is distributed.
          </p>
          <p className="mb-4">
            When a C2PA-signed document is copied, scraped, emailed, published on a mirror site, or processed as AI training data, the JUMBF manifest travels with it. Any system processing the file can access the provenance metadata without any additional lookup. The proof is available offline, in disconnected environments, inside proprietary AI pipelines, and anywhere else the file ends up.
          </p>
          <p className="mb-4">
            When a blockchain-anchored document is distributed, only the document travels. The blockchain record stays on the blockchain. A system processing the file has no indication that a blockchain record exists, does not know which chain or transaction to look up, and cannot verify provenance without external information. In most distribution scenarios - RSS syndication, web scraping, email forwarding, AI scraping - the blockchain proof is effectively absent.
          </p>
          <p className="mb-4">
            This is not an argument that blockchain provenance is wrong. For use cases where provenance is verified at a known point (a legal proceeding, a structured verification workflow), the external lookup is manageable. For use cases where content travels through many hands before provenance is relevant - which describes most web content and AI training data - embedded provenance has a significant practical advantage.
          </p>
        </section>

        {/* Standards and Adoption */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Standards and Industry Adoption</h2>
          <p className="mb-4">
            C2PA has over 200 member organizations. Adobe, Microsoft, Google, OpenAI, the BBC, Reuters, the Associated Press, and Nikon are among the founding and active members. The standard is integrated into Adobe's creative tools, Microsoft's Bing Image Creator, and multiple major camera manufacturers' firmware. The Content Authenticity Initiative (CAI), an industry coalition, implements C2PA in tools used by major newsrooms globally.
          </p>
          <p className="mb-4">
            Blockchain provenance is implemented by multiple vendors using different chains, transaction formats, and metadata schemas. There is no single standard: WordProof uses the EOSIO chain, other tools use Ethereum, Polygon, or Tezos. This fragmentation means that a verifier needs to know which blockchain and which implementation was used - there is no universal verification path.
          </p>
          <p className="mb-4">
            The EU's eIDAS 2.0 regulation and several digital media authenticity frameworks reference C2PA or compatible embedded-manifest approaches. Blockchain provenance is not referenced in major content authenticity regulatory frameworks as of 2026.
          </p>
        </section>

        {/* Comparison Table */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Side-by-Side Technical Comparison</h2>
          <div className="overflow-x-auto my-6">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  <th className="text-left py-3 px-4 font-semibold">Feature</th>
                  <th className="text-left py-3 px-4 font-semibold" style={{ color: '#2a87c4' }}>C2PA</th>
                  <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Blockchain</th>
                </tr>
              </thead>
              <tbody>
                <ComparisonRow
                  feature="Proof location"
                  c2pa="Embedded in the file (JUMBF container)"
                  blockchain="External ledger record"
                />
                <ComparisonRow
                  feature="Travels with content"
                  c2pa="Yes"
                  blockchain="No (record stays on chain)"
                />
                <ComparisonRow
                  feature="Offline verification"
                  c2pa="Yes (file + public key only)"
                  blockchain="No (requires chain query)"
                />
                <ComparisonRow
                  feature="Signing format"
                  c2pa="COSE (IETF standard)"
                  blockchain="Varies by chain and implementation"
                />
                <ComparisonRow
                  feature="Industry standard"
                  c2pa="Yes (ISO/IETF-aligned, 200+ members)"
                  blockchain="No universal standard (fragmented)"
                />
                <ComparisonRow
                  feature="Works during AI scraping"
                  c2pa="Yes (metadata in the scraped file)"
                  blockchain="No (chain not queried during scraping)"
                />
                <ComparisonRow
                  feature="Metadata stripping detection"
                  c2pa="Yes (absence of manifest is detectable)"
                  blockchain="No (file has no indication of external record)"
                />
                <ComparisonRow
                  feature="Transaction cost"
                  c2pa="None (embedded)"
                  blockchain="Gas cost per record (on public chains)"
                />
                <ComparisonRow
                  feature="Long-term durability"
                  c2pa="File-dependent, no network dependency"
                  blockchain="Chain-dependent (small chains carry longevity risk)"
                />
                <ComparisonRow
                  feature="Granularity"
                  c2pa="Document-level to segment-level (Section A.7)"
                  blockchain="Document-level hash only"
                />
                <ComparisonRow
                  feature="Decentralized"
                  c2pa="Verification is decentralized (uses public keys)"
                  blockchain="Yes (record on distributed ledger)"
                  blockchainPositive={true}
                />
                <ComparisonRow
                  feature="Public auditability"
                  c2pa="Via Content Credentials lookup"
                  blockchain="Yes (public chain is transparent)"
                  c2paPositive={true}
                  blockchainPositive={true}
                />
              </tbody>
            </table>
          </div>
        </section>

        {/* FAQ */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions</h2>
          <div className="space-y-6">
            {faqSchema.mainEntity.map((item, i) => (
              <div key={i} className="border-b border-border pb-6 last:border-0">
                <h3 className="font-semibold mb-2">{item.name}</h3>
                <p className="text-muted-foreground text-sm">{item.acceptedAnswer.text}</p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <div className="bg-muted/30 border border-border rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold mb-3">Encypher implements C2PA Section A.7</h2>
          <p className="text-muted-foreground mb-6">
            Segment-level text provenance, embedded in your content, verified offline. Built on the standard backed by Adobe, Microsoft, Google, and the BBC.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/signin?mode=signup"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-semibold text-white transition-opacity hover:opacity-90"
              style={{ backgroundColor: '#2a87c4' }}
            >
              Get Started Free <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/publisher-demo"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-semibold border border-border hover:bg-muted/30 transition-colors"
            >
              See the Demo
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
