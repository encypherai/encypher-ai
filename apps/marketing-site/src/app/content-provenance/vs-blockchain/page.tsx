import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'Content Provenance vs. Blockchain Timestamping | Encypher',
  'Why embedded C2PA provenance beats blockchain timestamping for content authentication. Proof that travels with content versus proof that requires an external lookup.',
  '/content-provenance/vs-blockchain'
);

export default function VsBlockchainPage() {
  const techArticle = getTechArticleSchema({
    title: 'Content Provenance vs. Blockchain Timestamping',
    description: 'Why embedded C2PA provenance beats blockchain timestamping for content authentication. Proof that travels with content versus proof that requires an external lookup.',
    url: `${siteConfig.url}/content-provenance/vs-blockchain`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="Content Provenance vs. Blockchain Timestamping"
        whatWeDo="Encypher embeds C2PA provenance directly into content files and text - not into a blockchain registry. The proof travels with the content through every distribution channel without requiring an external lookup."
        whoItsFor="Publishers and enterprises evaluating blockchain timestamping services (such as WordProof) versus embedded provenance infrastructure. Anyone asking whether blockchain-based content authentication is appropriate for their use case."
        keyDifferentiator="Embedded provenance travels with content. Blockchain records require the blockchain to remain accessible for verification. When content moves through wire services and aggregators, embedded proof stays with it. A blockchain record does not."
        primaryValue="Proof that cannot be separated from the content. No external lookup required. Verifiable by anyone with open-source tools. Survives any distribution pathway."
        pagePath="/content-provenance/vs-blockchain"
        pageType="WebPage"
      />

      <Script
        id="tech-article-vs-blockchain"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <ArticleShell path="/content-provenance/vs-blockchain">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Content Provenance', href: '/content-provenance' },
          { name: 'vs. Blockchain', href: '/content-provenance/vs-blockchain' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Content Provenance vs. Blockchain Timestamping
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          Both approaches create a record of content at a point in time.
          The difference is where that record lives and whether it can
          follow the content through downstream distribution.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">How Blockchain Timestamping Works</h2>
          <p className="text-muted-foreground mb-4">
            Services like WordProof create a cryptographic hash of your content and record
            that hash on a blockchain - typically a public blockchain like Ethereum or a
            purpose-built chain. The hash is deterministic: the same content always produces
            the same hash, and any change produces a different hash.
          </p>
          <p className="text-muted-foreground mb-4">
            To verify a piece of content against the blockchain record, a verifier takes the
            current content, computes the hash, and checks whether that hash appears in the
            blockchain at the claimed timestamp. If it does, the content existed in that form
            at that time. If it does not, the content was either never recorded or was
            modified after recording.
          </p>
          <p className="text-muted-foreground">
            The record is real and the cryptographic guarantee is sound. The problem is not
            with the cryptography. The problem is with the architecture: the record and the
            content are separate. When the content moves, the record stays behind.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Separation Problem</h2>
          <p className="text-muted-foreground mb-4">
            A publisher timestamps an article on-chain and distributes it to AP. AP distributes
            to 1,500 subscriber outlets. Those outlets publish on their own CMS, which strips
            metadata. The article is scraped by aggregators, some of which strip headers.
            Eventually, a version ends up in an AI training corpus.
          </p>
          <p className="text-muted-foreground mb-4">
            At every step in that chain, the blockchain record exists on the blockchain.
            But the content that traveled through the chain has no connection to that record.
            There is nothing in the article text or the file that points to the blockchain
            transaction. Verification requires knowing where to look and having the original
            hash to compare against.
          </p>
          <p className="text-muted-foreground">
            The AI company that received the content in its training corpus has no way to
            discover the blockchain record. They would need to know the original publisher,
            look up the blockchain registration, obtain the transaction details, and perform
            the hash comparison. In practice, this does not happen. The ownership record is
            effectively invisible to anyone downstream.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">How Embedded Provenance Solves This</h2>
          <p className="text-muted-foreground mb-4">
            C2PA manifests are embedded in the content itself - in the file container for
            images and media, and in invisible Unicode markers for text. The proof does not
            live on a separate server or blockchain. It is part of the content.
          </p>
          <p className="text-muted-foreground mb-4">
            When that content moves through distribution channels, the proof moves with it.
            When AP distributes the article, the manifest is in the text. When an aggregator
            scrapes it, the manifest is still in the text. When an AI company ingests it into
            a training corpus, the manifest is still in the text.
          </p>
          <p className="text-muted-foreground">
            Any party downstream - without needing to contact the publisher, without needing
            to access a blockchain, without needing any external lookup - can verify the
            content's provenance using open-source C2PA verification libraries. The proof is
            self-contained and self-verifying.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Technical Architecture Comparison</h2>
          <div className="overflow-x-auto mb-4">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 pr-4 font-semibold">Property</th>
                  <th className="text-left py-3 pr-4 font-semibold">Blockchain Timestamping</th>
                  <th className="text-left py-3 font-semibold">C2PA Embedded Provenance</th>
                </tr>
              </thead>
              <tbody className="text-muted-foreground">
                <tr className="border-b border-border/50">
                  <td className="py-3 pr-4 font-medium text-foreground">Record location</td>
                  <td className="py-3 pr-4">External blockchain</td>
                  <td className="py-3">Embedded in content</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 pr-4 font-medium text-foreground">Travels with content</td>
                  <td className="py-3 pr-4">No</td>
                  <td className="py-3">Yes</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 pr-4 font-medium text-foreground">Requires external lookup</td>
                  <td className="py-3 pr-4">Yes</td>
                  <td className="py-3">No</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 pr-4 font-medium text-foreground">Discoverable by downstream parties</td>
                  <td className="py-3 pr-4">Only if they know to look</td>
                  <td className="py-3">Yes, embedded in content</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 pr-4 font-medium text-foreground">Author identity included</td>
                  <td className="py-3 pr-4">Optional, in transaction metadata</td>
                  <td className="py-3">Yes, in manifest</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 pr-4 font-medium text-foreground">Rights terms included</td>
                  <td className="py-3 pr-4">Rarely</td>
                  <td className="py-3">Yes, machine-readable</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 pr-4 font-medium text-foreground">Sentence-level granularity</td>
                  <td className="py-3 pr-4">No</td>
                  <td className="py-3">Yes (Encypher proprietary)</td>
                </tr>
                <tr>
                  <td className="py-3 pr-4 font-medium text-foreground">Open standard</td>
                  <td className="py-3 pr-4">Depends on implementation</td>
                  <td className="py-3">Yes, C2PA 2.3</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Rights Terms Advantage</h2>
          <p className="text-muted-foreground mb-4">
            Blockchain timestamping records that content existed. It does not record what
            rights apply to it. A blockchain timestamp does not make content's licensing
            terms machine-readable. It does not encode Bronze/Silver/Gold tier permissions.
            It does not create the formal notice that converts innocent infringement to
            willful infringement.
          </p>
          <p className="text-muted-foreground mb-4">
            C2PA manifests include structured rights assertions. The manifest can encode
            whether content is available for indexing, RAG use, or training. It can specify
            attribution requirements, geographic restrictions, and commercial versus
            non-commercial use permissions. These terms are machine-readable - AI systems
            can parse them without human interpretation.
          </p>
          <p className="text-muted-foreground">
            When an AI company ingests content with embedded rights terms, they have formal
            notice of those terms regardless of whether they read them. The embedded notice
            is the mechanism that shifts the legal burden from innocent to willful infringement.
            A blockchain timestamp without rights terms does not create that shift.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">When Blockchain Timestamps Have Value</h2>
          <p className="text-muted-foreground mb-4">
            Blockchain timestamping is useful for priority disputes - proving you created
            something before a competitor did. Patent applicants, inventors, and researchers
            use blockchain timestamps to establish a dated public record that does not depend
            on a trusted third party.
          </p>
          <p className="text-muted-foreground mb-4">
            In this narrow use case, the separation of record and content is not a problem.
            The goal is a dated public record, not a proof that travels with the content.
            A blockchain timestamp serves that goal.
          </p>
          <p className="text-muted-foreground">
            For content that will be distributed, syndicated, and consumed by third parties
            who need to discover its provenance - published articles, licensed images,
            audio recordings, video content - embedded provenance is more useful than a
            blockchain record that requires a separate lookup chain.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/compare/c2pa-vs-blockchain" className="underline hover:no-underline">Full Comparison: C2PA vs. Blockchain</Link></li>
            <li><Link href="/compare/encypher-vs-wordproof" className="underline hover:no-underline">Encypher vs. WordProof</Link></li>
            <li><Link href="/content-provenance" className="underline hover:no-underline">Content Provenance: The Definitive Guide</Link></li>
            <li><Link href="/c2pa-standard/manifest-structure" className="underline hover:no-underline">C2PA Manifest Structure</Link></li>
            <li><Link href="/cryptographic-watermarking/how-it-works" className="underline hover:no-underline">How Cryptographic Watermarking Works</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Proof That Travels With Your Content</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Embedded C2PA provenance requires no external lookup, no blockchain dependency,
            and no separate record-keeping. Start signing for free.
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
