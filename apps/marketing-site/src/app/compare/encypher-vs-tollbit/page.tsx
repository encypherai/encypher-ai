import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import Script from 'next/script';
import Link from 'next/link';
import { getCompareMetadata, getTechArticleSchema, getBreadcrumbSchema, siteConfig } from '@/lib/seo';
import type { Metadata } from 'next';
import { ArrowRight, CheckCircle2, AlertCircle, Layers } from 'lucide-react';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypher.com';

export const metadata: Metadata = getCompareMetadata(
  'encypher-vs-tollbit',
  'Encypher vs TollBit: Embedded Provenance vs Opt-In Access Gates',
  "TollBit gates AI access for cooperating companies. Encypher embeds proof that works whether AI companies cooperate or not. These are Layer 1 and Layer 2 of the content provenance stack - complementary, not competing.",
  "Gates stop willing crawlers. Provenance covers everyone else."
);

const PAGE_URL = `${siteConfig.url}/compare/encypher-vs-tollbit`;
const DATE = '2026-03-31';

const techArticleSchema = getTechArticleSchema({
  headline: 'Encypher vs TollBit: Embedded Provenance vs Opt-In Access Gates',
  description: "TollBit and Encypher occupy different layers of the content protection stack. This comparison explains the architectural difference and how they work together.",
  url: PAGE_URL,
  datePublished: DATE,
});

const breadcrumbSchema = getBreadcrumbSchema([
  { name: 'Home', url: siteConfig.url },
  { name: 'Compare', url: `${siteConfig.url}/compare` },
  { name: 'Encypher vs TollBit', url: PAGE_URL },
]);

const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What does TollBit do?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "TollBit is a licensing marketplace that allows AI companies to pay for access to publisher content. Publishers register their domains and set pricing for different tiers of content use (indexing, RAG, training). AI companies that want to use the content legitimately connect through TollBit's API, authenticate, pay the fee, and receive access. It functions as a front-door gate for cooperative AI companies."
      }
    },
    {
      "@type": "Question",
      "name": "What is the limitation of access gating approaches?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Access gates only work when the AI company chooses to participate. A crawler that ignores robots.txt will also ignore TollBit's gate. Content that has already been scraped and is in a training corpus bypasses any future gate. Access gating is effective for cooperative actors - AI companies that want legitimate licensing relationships. It has no mechanism for enforcement against non-cooperative actors."
      }
    },
    {
      "@type": "Question",
      "name": "How is Encypher different from TollBit?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "TollBit operates at the access layer - it controls whether an AI company can reach your content. Encypher operates at the content layer - it embeds proof of ownership in the content itself. Encypher's approach works regardless of whether the AI company cooperates, because the provenance is in the text that was scraped, not in a gate that can be bypassed. These are different layers of the same stack."
      }
    },
    {
      "@type": "Question",
      "name": "Should publishers use TollBit, Encypher, or both?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Both. Use TollBit to establish a legitimate licensing channel for AI companies that want to cooperate - it reduces friction for willing partners. Use Encypher so that your content carries proof of ownership regardless of whether any given AI company used TollBit's gate. TollBit handles the cooperative relationship. Encypher handles the enforcement case when cooperation is absent."
      }
    },
    {
      "@type": "Question",
      "name": "What is the three-layer content protection stack?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Layer 1 is access control: robots.txt, TollBit, Cloudflare AI blocking. These are opt-in gates that work when AI companies follow them. Layer 2 is content provenance: Encypher. This is embedded proof in the content itself that works without AI company cooperation. Layer 3 is attribution and monetization: ProRata, Dappier, Microsoft PCM. These estimate which sources contributed to AI outputs and route revenue back - but only inside opted-in systems. The layers are complementary. None replaces the others."
      }
    }
  ]
};

function ComparisonRow({ feature, encypher, tollbit, encypherPositive = true, tollbitPositive = false }: {
  feature: string;
  encypher: string;
  tollbit: string;
  encypherPositive?: boolean;
  tollbitPositive?: boolean;
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
          {tollbitPositive
            ? <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
            : <AlertCircle className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
          }
          {tollbit}
        </span>
      </td>
    </tr>
  );
}

export default function EncypherVsTollBitPage() {
  return (
    <>
      <AISummary
        title="Encypher vs TollBit: Layer 2 Content Provenance vs Layer 1 Access Gates"
        whatWeDo="This page explains how TollBit and Encypher occupy different layers of the content protection stack and why publishers need both. TollBit is Layer 1 (cooperative access gating). Encypher is Layer 2 (unilateral embedded provenance)."
        whoItsFor="Publishers evaluating content protection strategies. Teams deciding between access gates and provenance embedding."
        keyDifferentiator="TollBit works when AI companies cooperate. Encypher works regardless of AI company cooperation because the proof is in the content itself."
        primaryValue="Encypher is the only layer that provides enforcement capability against non-cooperative actors. The two tools address complementary use cases."
        pagePath="/compare/encypher-vs-tollbit"
      />
      <Script id="tech-article-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticleSchema) }} />
      <Script id="breadcrumb-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      <Script id="faq-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Compare', href: '/compare' },
          { name: 'Encypher vs TollBit', href: '/compare/encypher-vs-tollbit' },
        ]} />

        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Encypher vs TollBit
        </h1>
        <p className="text-xl text-muted-foreground mb-10">
          TollBit gates the front door for AI companies that cooperate. Encypher embeds proof in your content for enforcement against everyone else. These are different layers of the same stack - both are necessary.
        </p>

        {/* The Three-Layer Stack */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Placing Each Tool in the Stack</h2>
          <p className="mb-4">
            Before comparing the two products, it helps to understand where each sits in the broader content protection architecture. There are three distinct layers, and they address different actors with different approaches.
          </p>
          <div className="grid grid-cols-1 gap-4 my-6">
            <div className="border border-border rounded-lg p-5">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-7 h-7 rounded bg-muted flex items-center justify-center text-sm font-bold">1</div>
                <h3 className="font-semibold">Layer 1: Access Control</h3>
              </div>
              <p className="text-sm text-muted-foreground ml-10">
                robots.txt, TollBit, Cloudflare AI blocking. These tools sit between your server and the AI crawler. They work when AI companies follow the signals - when they send robots.txt-respecting crawlers, when they authenticate through licensing APIs. They are effective for cooperative actors and ineffective for those who bypass them.
              </p>
            </div>
            <div className="border rounded-lg p-5" style={{ borderColor: '#2a87c4' }}>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-7 h-7 rounded flex items-center justify-center text-sm font-bold text-white" style={{ backgroundColor: '#2a87c4' }}>2</div>
                <h3 className="font-semibold" style={{ color: '#2a87c4' }}>Layer 2: Content Provenance (Encypher)</h3>
              </div>
              <p className="text-sm text-muted-foreground ml-10">
                Cryptographic proof embedded in the content itself. Works regardless of how the content was obtained - through a gate, through a bypass, from a pre-existing corpus, from a downstream copy. The proof is in the text.
              </p>
            </div>
            <div className="border border-border rounded-lg p-5">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-7 h-7 rounded bg-muted flex items-center justify-center text-sm font-bold">3</div>
                <h3 className="font-semibold">Layer 3: Attribution / Monetization</h3>
              </div>
              <p className="text-sm text-muted-foreground ml-10">
                ProRata, Dappier, Microsoft PCM. These estimate which sources contributed to AI outputs and route revenue back to publishers. They operate inside systems where AI companies have opted in. No opt-in, no attribution.
              </p>
            </div>
          </div>
          <p className="mb-4">
            The layers are complementary. A publisher who uses all three has the widest possible coverage: a cooperative licensing channel for AI companies that participate, proof embedded in content for enforcement against those who don't, and attribution revenue routing inside opted-in AI systems.
          </p>
        </section>

        {/* What TollBit Does Well */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">What TollBit Does Well</h2>
          <p className="mb-4">
            TollBit solves a real problem: there was no standardized mechanism for AI companies to license content from individual publishers at scale. Negotiating directly with each publisher is impractical. TollBit creates a marketplace where a publisher registers once and AI companies can license access through a single interface.
          </p>
          <p className="mb-4">
            For AI companies that want to operate with clear licensing, TollBit reduces friction substantially. Instead of building bespoke licensing deals with dozens of publishers, an AI company can integrate TollBit's API and access a large catalog of licensed content with defined terms.
          </p>
          <p className="mb-4">
            The tier structure - allowing publishers to set different prices for indexing, RAG, and training use cases - is commercially sensible. Training access is typically priced higher than search indexing, reflecting the different value extraction at each use.
          </p>
          <p className="mb-4">
            TollBit also creates a network effect: as more AI companies integrate, publishers gain broader licensing coverage. As more publishers register, AI companies have richer licensed content catalogs available.
          </p>
        </section>

        {/* The Cooperation Dependency */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Fundamental Limitation: Cooperation Dependency</h2>
          <p className="mb-4">
            TollBit's architecture depends entirely on AI companies choosing to participate. This is the correct framing, not a criticism: access gates are designed for cooperative actors. The question is what happens when cooperation is absent.
          </p>
          <p className="mb-4">
            Three categories of non-cooperation are common:
          </p>
          <ul className="list-disc list-outside ml-6 mb-4 space-y-2 text-muted-foreground">
            <li><strong className="text-foreground">Crawlers that bypass robots.txt and access gates.</strong> Some AI data collection pipelines do not respect these signals. A gate that is bypassed provides no protection.</li>
            <li><strong className="text-foreground">Content already in training corpora.</strong> If an AI model was trained on your content before you implemented TollBit, the gate has no retroactive effect. The content is already inside the model.</li>
            <li><strong className="text-foreground">AI companies that have not integrated TollBit.</strong> TollBit's licensing network covers participating companies. An AI company that builds its own crawler and has not joined TollBit's marketplace is outside the gate entirely.</li>
          </ul>
          <p className="mb-4">
            None of these are unusual scenarios. Most current AI training runs predate publisher access gating infrastructure. Encypher's embedded approach addresses all three cases: the proof is in the scraped text, regardless of when scraping occurred or whether a gate was in place.
          </p>
        </section>

        {/* How They Complement Each Other */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">How TollBit and Encypher Work Together</h2>
          <p className="mb-4">
            The practical deployment for a publisher who wants comprehensive coverage:
          </p>
          <ol className="list-decimal list-outside ml-6 mb-4 space-y-3 text-muted-foreground">
            <li><strong className="text-foreground">Register on TollBit.</strong> Set pricing tiers for indexing, RAG, and training. This creates a legitimate licensing channel for AI companies that want to cooperate. Cooperative actors get a clear path; you get revenue from willing licensees.</li>
            <li><strong className="text-foreground">Sign your content with Encypher.</strong> Embed provenance and machine-readable licensing terms in your published articles, retroactively across your archive and prospectively for new content. This is the enforcement layer.</li>
            <li><strong className="text-foreground">When cooperation is absent.</strong> If an AI company bypasses TollBit's gate and uses your content, the Encypher signature is evidence. The embedded licensing terms establish that the content was marked with rights reservations. Using the content in violation of those terms triggers willful infringement, not innocent infringement.</li>
          </ol>
          <p className="mb-4">
            Encypher is not a replacement for TollBit. It is what covers the gap when TollBit's cooperative model does not apply.
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
                  <th className="text-left py-3 px-4 font-semibold text-muted-foreground">TollBit</th>
                </tr>
              </thead>
              <tbody>
                <ComparisonRow
                  feature="Layer in the stack"
                  encypher="Layer 2 - Content provenance"
                  tollbit="Layer 1 - Access control"
                  tollbitPositive={true}
                />
                <ComparisonRow
                  feature="Requires AI company cooperation"
                  encypher="No - works unilaterally"
                  tollbit="Yes - AI company must integrate"
                />
                <ComparisonRow
                  feature="Works on existing training corpora"
                  encypher="Yes (if content was signed pre-scrape)"
                  tollbit="No (retroactive effect impossible)"
                />
                <ComparisonRow
                  feature="Works if crawler bypasses gate"
                  encypher="Yes (proof in the scraped text)"
                  tollbit="No"
                />
                <ComparisonRow
                  feature="Machine-readable licensing terms"
                  encypher="Embedded in every document"
                  tollbit="In TollBit's API (external)"
                />
                <ComparisonRow
                  feature="Formal notice capability"
                  encypher="Yes (willful infringement trigger)"
                  tollbit="No"
                />
                <ComparisonRow
                  feature="Revenue from cooperative AI companies"
                  encypher="Via Encypher coalition"
                  tollbit="Yes (primary purpose)"
                  encypherPositive={true}
                  tollbitPositive={true}
                />
                <ComparisonRow
                  feature="Works when AI company has not joined"
                  encypher="Yes"
                  tollbit="No"
                />
                <ComparisonRow
                  feature="Proof travels with content"
                  encypher="Yes"
                  tollbit="No (gate is at the server)"
                />
                <ComparisonRow
                  feature="Publisher integration"
                  encypher="API + SDK + WordPress plugin"
                  tollbit="Registration + domain setup"
                  encypherPositive={true}
                  tollbitPositive={true}
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
          <h2 className="text-2xl font-bold mb-3">Add Layer 2 to your content strategy</h2>
          <p className="text-muted-foreground mb-6">
            Access gates handle willing partners. Embedded provenance handles everyone else.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href={`${DASHBOARD_URL}/auth/signin?mode=signup`}
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
