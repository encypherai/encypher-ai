import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import Script from 'next/script';
import Link from 'next/link';
import { getCompareMetadata, getTechArticleSchema, getBreadcrumbSchema, siteConfig } from '@/lib/seo';
import type { Metadata } from 'next';
import { ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';

export const metadata: Metadata = getCompareMetadata(
  'encypher-vs-wordproof',
  'Encypher vs WordProof: Embedded Provenance vs Blockchain Timestamping',
  "WordProof registers a hash on a blockchain to prove content existed at a point in time. Encypher embeds provenance in the text itself. Timestamping proves existence. Provenance proves ownership wherever content appears."
);

const PAGE_URL = `${siteConfig.url}/compare/encypher-vs-wordproof`;
const DATE = '2026-03-31';

const techArticleSchema = getTechArticleSchema({
  headline: 'Encypher vs WordProof: Embedded Provenance vs Blockchain Timestamping',
  description: "WordProof registers a hash on a blockchain to prove content existed at a point in time. Encypher embeds provenance in the text itself.",
  url: PAGE_URL,
  datePublished: DATE,
});

const breadcrumbSchema = getBreadcrumbSchema([
  { name: 'Home', url: siteConfig.url },
  { name: 'Compare', url: `${siteConfig.url}/compare` },
  { name: 'Encypher vs WordProof', url: PAGE_URL },
]);

const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What does WordProof do?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "WordProof timestamps content by hashing it and recording the hash on a blockchain. This creates an external record proving that a specific version of content existed at a specific time. It integrates with WordPress and other CMS platforms to automate this process at publication."
      }
    },
    {
      "@type": "Question",
      "name": "What is the difference between timestamping and provenance?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Timestamping proves that a specific version of content existed at a point in time - useful for establishing priority in disputes. Provenance proves ownership and carries that proof with the content wherever it travels. A timestamp is an external record you have to look up. Provenance is embedded in the content itself. When text is copied, scraped, or syndicated, the timestamp stays behind. The provenance travels with it."
      }
    },
    {
      "@type": "Question",
      "name": "Why does it matter that the proof is external vs embedded?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "External proof requires a lookup. You have the content, you look up the blockchain record, you see if there is a match. This works when you have both pieces. When an AI scrapes your content and uses it without attribution, you typically only have the output - not a provenance link back to the original. Embedded proof travels with the content. The signing identity, timestamp, and licensing terms are in the text itself, visible during scraping and downstream use."
      }
    },
    {
      "@type": "Question",
      "name": "Does WordProof prevent AI training data use?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. WordProof's external hash record is not readable by an AI crawler at scrape time. There is no signal in the scraped text indicating licensing terms. Encypher's invisible embedded markers are present in the text itself and can be parsed by any system that reads the text, making licensing terms machine-readable at the point of use."
      }
    },
    {
      "@type": "Question",
      "name": "Are WordProof and Encypher complementary?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "They address different aspects of content protection. WordProof provides a public timestamp record on-chain that is useful for establishing priority. Encypher provides ownership proof that travels with the content. A publisher could use both: WordProof for the public, auditable timestamp record and Encypher for the embedded provenance that works during downstream distribution."
      }
    }
  ]
};

function ComparisonRow({ feature, encypher, wordproof, encypherPositive = true }: {
  feature: string;
  encypher: string;
  wordproof: string;
  encypherPositive?: boolean;
}) {
  return (
    <tr className="border-b border-border hover:bg-muted/20 transition-colors">
      <td className="py-3 px-4 font-medium text-sm">{feature}</td>
      <td className="py-3 px-4 text-sm">
        <span className="flex items-start gap-2">
          {encypherPositive
            ? <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
            : <AlertCircle className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
          }
          {encypher}
        </span>
      </td>
      <td className="py-3 px-4 text-sm text-muted-foreground">
        <span className="flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
          {wordproof}
        </span>
      </td>
    </tr>
  );
}

export default function EncypherVsWordProofPage() {
  return (
    <>
      <AISummary
        title="Encypher vs WordProof: Embedded Provenance vs Blockchain Timestamping"
        whatWeDo="This page compares Encypher and WordProof. WordProof timestamps content on-chain; Encypher embeds provenance in the text. Timestamping proves existence. Provenance proves ownership wherever content appears."
        whoItsFor="Publishers and content creators evaluating content protection and ownership proof solutions."
        keyDifferentiator="Encypher's proof is embedded in the content and travels with it. WordProof's proof is an external blockchain record that stays behind when content is copied or scraped."
        primaryValue="Ownership proof that follows your content into any distribution channel, AI training corpus, or downstream use."
        pagePath="/compare/encypher-vs-wordproof"
      />
      <Script id="tech-article-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticleSchema) }} />
      <Script id="breadcrumb-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      <Script id="faq-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Compare', href: '/compare' },
          { name: 'Encypher vs WordProof', href: '/compare/encypher-vs-wordproof' },
        ]} />

        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Encypher vs WordProof
        </h1>
        <p className="text-xl text-muted-foreground mb-10">
          Blockchain timestamping proves your content existed at a point in time. Embedded provenance proves you own it, wherever it travels.
        </p>

        {/* The Core Distinction */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Timestamping vs Provenance</h2>
          <p className="mb-4">
            WordProof and Encypher both aim to help content creators prove ownership. The difference is architectural, and it has real consequences for how enforcement works.
          </p>
          <p className="mb-4">
            WordProof works by hashing your content - producing a short cryptographic fingerprint - and recording that hash on a blockchain. The blockchain creates a timestamped, immutable record. If someone disputes when you published something, you point to the on-chain record. This is a timestamp: evidence that a specific version of content existed at a specific time.
          </p>
          <p className="mb-4">
            The limitation is that this proof is external. The blockchain record lives on a blockchain. The content lives on your server. When an AI system scrapes your article, it gets the text. It does not get the blockchain record, the lookup link, or any indication that a record exists. The proof stays behind.
          </p>
          <p className="mb-4">
            Encypher embeds the ownership proof in the text itself, using proprietary invisible encoding. When an AI scraper copies your article, the provenance record travels with it. When the scraped text is processed as training data, the embedded signature is there. When a downstream output is examined, the marker identifies the source content. The proof follows the content.
          </p>
          <div className="bg-muted/30 border border-border rounded-lg p-6 my-6">
            <p className="font-semibold text-lg mb-2">The Distinction in One Line</p>
            <p className="text-muted-foreground">
              Timestamping proves content existed. Provenance proves ownership wherever content appears.
            </p>
          </div>
        </section>

        {/* What WordProof Does Well */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">What WordProof Does Well</h2>
          <p className="mb-4">
            For its intended purpose, WordProof works. Blockchain timestamping has several genuine advantages.
          </p>
          <p className="mb-4">
            The on-chain record is decentralized and auditable. Anyone can verify the timestamp without trusting WordProof specifically - the record is on a public blockchain. This is valuable for content disputes where the question is "who published this first?" and both parties have external records to compare.
          </p>
          <p className="mb-4">
            WordProof integrates cleanly with WordPress, which is where a large portion of the world's web content lives. The friction to adopt is low. You install the plugin, authenticate, and your content is timestamped at publication without changing your workflow.
          </p>
          <p className="mb-4">
            The Schema.org integration in WordProof is a practical SEO benefit: timestamped content can carry structured data indicating when it was published, which some search engines use for freshness ranking.
          </p>
        </section>

        {/* Why External Proof Has Limits */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Where External Proof Reaches Its Limits</h2>
          <p className="mb-4">
            The architectural constraint of external proof becomes most visible in the AI training data context.
          </p>
          <p className="mb-4">
            When AI companies train models on web content, they scrape text. They do not follow the provenance links. They do not query blockchain records. They get the raw text, and the raw text - in WordProof's architecture - contains no ownership signal.
          </p>
          <p className="mb-4">
            Once your content is inside a training corpus, or inside an AI system's knowledge, or reproduced in an AI-generated output, there is no path back to the blockchain record. The timestamp proved that the content existed. It cannot prove, at that point, that this specific piece of training data was sourced from your article.
          </p>
          <p className="mb-4">
            The second limitation is licensing signals. A blockchain timestamp records a hash and a timestamp. It does not encode licensing terms. There is no way to express "this content is licensed for indexing but not for training" inside a WordProof timestamp. Those terms exist somewhere else - perhaps in a robots.txt file, perhaps in a terms of service page - and AI systems have varying degrees of compliance with those mechanisms.
          </p>
          <p className="mb-4">
            Encypher addresses both gaps by embedding a signed payload directly in the content. The payload includes the publisher identity, publication timestamp, content hash, and machine-readable licensing terms. Every copy of the content carries this information regardless of how it was distributed.
          </p>
        </section>

        {/* The Syndication Problem */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Syndication Problem</h2>
          <p className="mb-4">
            Publishers syndicate content. Articles appear on partner sites, in RSS feeds, in news aggregators, in email newsletters, in social media reposts. Each of these is a copy that has traveled outside the original publication context.
          </p>
          <p className="mb-4">
            With WordProof, each of these copies is a dead end for provenance: the text is present, the blockchain record is not. Tracking which copies exist, who published them, and whether they have licensing authority requires manual tracking or third-party tools.
          </p>
          <p className="mb-4">
            With Encypher, every copy carries the same embedded signature. Verification is possible on any copy, anywhere it appears. The signing identity in the payload identifies the original publisher. When an AI system is queried about where it learned something, if the source content was marked with Encypher, the signature provides a chain back to the original publisher.
          </p>
        </section>

        {/* Comparison Table */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Side-by-Side Comparison</h2>
          <div className="overflow-x-auto my-6">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  <th className="text-left py-3 px-4 font-semibold">Feature</th>
                  <th className="text-left py-3 px-4 font-semibold" style={{ color: '#2a87c4' }}>Encypher</th>
                  <th className="text-left py-3 px-4 font-semibold text-muted-foreground">WordProof</th>
                </tr>
              </thead>
              <tbody>
                <ComparisonRow
                  feature="Proof location"
                  encypher="Embedded in content (travels with text)"
                  wordproof="External blockchain record (stays behind)"
                />
                <ComparisonRow
                  feature="Proof type"
                  encypher="Ownership + identity + licensing terms"
                  wordproof="Existence + timestamp only"
                />
                <ComparisonRow
                  feature="Survives copy-paste"
                  encypher="Yes (invisible chars in the text)"
                  wordproof="No (hash is separate from text)"
                />
                <ComparisonRow
                  feature="Machine-readable licensing"
                  encypher="Yes (Bronze/Silver/Gold tiers embedded)"
                  wordproof="No"
                />
                <ComparisonRow
                  feature="Works during AI scraping"
                  encypher="Yes (markers present in scraped text)"
                  wordproof="No (blockchain not queried at scrape time)"
                />
                <ComparisonRow
                  feature="Publisher identity"
                  encypher="Cryptographically signed, in the content"
                  wordproof="Associated with hash in external record"
                />
                <ComparisonRow
                  feature="Verification without lookup"
                  encypher="Yes (signature in the text itself)"
                  wordproof="No (requires blockchain query)"
                />
                <ComparisonRow
                  feature="Blockchain dependency"
                  encypher="None"
                  wordproof="Requires accessible blockchain"
                />
                <ComparisonRow
                  feature="Tamper detection"
                  encypher="Yes (hash mismatch detects modification)"
                  wordproof="Yes (hash mismatch detects modification)"
                  encypherPositive={true}
                />
                <ComparisonRow
                  feature="Priority dispute evidence"
                  encypher="Yes (signed timestamp embedded)"
                  wordproof="Yes (blockchain timestamp)"
                  encypherPositive={true}
                />
                <ComparisonRow
                  feature="CMS integration"
                  encypher="API + WordPress plugin + SDK"
                  wordproof="WordPress plugin (primary)"
                />
                <ComparisonRow
                  feature="Formal notice capability"
                  encypher="Yes (willful infringement trigger)"
                  wordproof="No"
                />
              </tbody>
            </table>
          </div>
        </section>

        {/* Use Case Fit */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Use Case Fit</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border border-border rounded-lg p-6">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                Choose WordProof when...
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>The primary need is a public, auditable timestamp for priority disputes</li>
                <li>You are a WordPress publisher looking for low-friction adoption</li>
                <li>Blockchain-anchored evidence fits your legal or compliance requirements</li>
                <li>You want Schema.org timestamp data for SEO freshness signals</li>
              </ul>
            </div>
            <div className="border border-border rounded-lg p-6" style={{ borderColor: '#2a87c4' }}>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                Choose Encypher when...
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>You need proof that travels with your content into AI training pipelines</li>
                <li>Machine-readable licensing terms must be embedded in every copy</li>
                <li>You are building an enforcement case for AI copyright use</li>
                <li>Your content is syndicated widely and you need tracking across channels</li>
                <li>You want formal notice capability against willful infringement</li>
              </ul>
            </div>
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
          <h2 className="text-2xl font-bold mb-3">Sign your archive, free</h2>
          <p className="text-muted-foreground mb-6">
            The free tier signs 1,000 documents per month. Embed ownership proof before your next article goes out.
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
