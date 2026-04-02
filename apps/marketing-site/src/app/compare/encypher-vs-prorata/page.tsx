import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import Script from 'next/script';
import Link from 'next/link';
import { getCompareMetadata, getTechArticleSchema, getBreadcrumbSchema, siteConfig } from '@/lib/seo';
import type { Metadata } from 'next';
import { ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypher.com';

export const metadata: Metadata = getCompareMetadata(
  'encypher-vs-prorata',
  'Encypher vs ProRata: Input-Side Provenance vs Output-Side Attribution',
  "ProRata estimates which sources contributed to an AI output, inside a closed opted-in system. Encypher embeds proof before content enters any AI system. One requires participation. The other works unilaterally."
);

const PAGE_URL = `${siteConfig.url}/compare/encypher-vs-prorata`;
const DATE = '2026-03-31';

const techArticleSchema = getTechArticleSchema({
  headline: 'Encypher vs ProRata: Input-Side Provenance vs Output-Side Attribution',
  description: "ProRata estimates attribution inside opted-in AI systems. Encypher embeds proof in content before it enters any AI system.",
  url: PAGE_URL,
  datePublished: DATE,
});

const breadcrumbSchema = getBreadcrumbSchema([
  { name: 'Home', url: siteConfig.url },
  { name: 'Compare', url: `${siteConfig.url}/compare` },
  { name: 'Encypher vs ProRata', url: PAGE_URL },
]);

const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What does ProRata do?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "ProRata is an output-side attribution system. When an AI model generates a response, ProRata's algorithm estimates which source documents contributed to that output and what weight each should receive. Publishers who join ProRata's network receive revenue proportional to their estimated contribution. This only works inside AI systems that have voluntarily integrated ProRata's attribution API."
      }
    },
    {
      "@type": "Question",
      "name": "What is the difference between input-side provenance and output-side attribution?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Input-side provenance is established at content creation, before any AI system touches it. Encypher embeds a signature at publication that identifies the publisher, timestamp, and licensing terms. Output-side attribution is estimated at generation time, inside the AI system. ProRata analyzes what an AI outputs and works backward to estimate which sources contributed. Input-side is a cryptographic fact. Output-side is an algorithmic estimate."
      }
    },
    {
      "@type": "Question",
      "name": "What happens if an AI company doesn't integrate ProRata?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "ProRata has zero visibility. Attribution requires the AI company to instrument their inference pipeline with ProRata's API. If a model was trained on your content without integrating ProRata, there is no way to recover attribution through ProRata's system. Publishers in ProRata's network only receive attribution from AI companies that have opted in."
      }
    },
    {
      "@type": "Question",
      "name": "Does Encypher compete with ProRata?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "They occupy different positions in the same stack. Encypher is Layer 2 - content provenance embedded in the source material. ProRata is Layer 3 - attribution and monetization inside opted-in AI systems. A publisher who uses both gets the widest coverage: Encypher provides enforcement-grade proof regardless of AI company participation, and ProRata routes revenue from AI companies that have opted into attribution."
      }
    },
    {
      "@type": "Question",
      "name": "Which is better for publishers who want to be paid for AI training data use?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "For publishers negotiating with AI companies that have already opted into licensing systems, ProRata provides a revenue routing mechanism. For publishers dealing with AI companies that have not opted in - the majority of the market - Encypher provides the enforcement foundation. The embedded signature establishes that rights were reserved, enabling licensing negotiations and formal notice. The most comprehensive approach uses both: Encypher for the baseline proof layer, ProRata for revenue in opted-in systems."
      }
    }
  ]
};

function ComparisonRow({ feature, encypher, prorata, encypherPositive = true, prorataPositive = false }: {
  feature: string;
  encypher: string;
  prorata: string;
  encypherPositive?: boolean;
  prorataPositive?: boolean;
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
          {prorataPositive
            ? <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
            : <AlertCircle className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
          }
          {prorata}
        </span>
      </td>
    </tr>
  );
}

export default function EncypherVsProRataPage() {
  return (
    <>
      <AISummary
        title="Encypher vs ProRata: Layer 2 Content Provenance vs Layer 3 Output Attribution"
        whatWeDo="This page compares Encypher and ProRata. ProRata is an output-side attribution system that routes revenue inside opted-in AI networks. Encypher is an input-side provenance system that embeds proof in content before it enters any AI system."
        whoItsFor="Publishers evaluating AI content monetization and enforcement strategies."
        keyDifferentiator="ProRata requires AI company participation and estimates contribution algorithmically. Encypher works unilaterally and establishes proof cryptographically."
        primaryValue="Encypher covers the enforcement gap when AI companies have not opted into attribution systems. ProRata covers revenue routing when they have."
        pagePath="/compare/encypher-vs-prorata"
      />
      <Script id="tech-article-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticleSchema) }} />
      <Script id="breadcrumb-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      <Script id="faq-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Compare', href: '/compare' },
          { name: 'Encypher vs ProRata', href: '/compare/encypher-vs-prorata' },
        ]} />

        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Encypher vs ProRata
        </h1>
        <p className="text-xl text-muted-foreground mb-10">
          ProRata routes revenue inside AI systems that have opted in. Encypher embeds proof before content enters any AI system. One requires participation. The other works unilaterally.
        </p>

        {/* Core Architectural Difference */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Input-Side vs Output-Side: A Fundamental Architectural Difference</h2>
          <p className="mb-4">
            ProRata and Encypher are both aimed at helping publishers capture value from AI use of their content. The architectural difference between them determines when each works and what it can prove.
          </p>
          <p className="mb-4">
            ProRata works on the output side. When an AI model generates a response, ProRata's algorithm examines that output and traces which source documents likely contributed to it. The attribution is then used to route revenue: publishers whose content contributed more to an AI's output receive a larger share of licensing fees. The process requires the AI company to instrument their inference pipeline with ProRata's attribution API.
          </p>
          <p className="mb-4">
            Encypher works on the input side. Before your content enters any AI system, you embed a cryptographic signature in it. That signature carries your identity, publication timestamp, and licensing terms. When the content is scraped, processed as training data, or referenced in an AI output, the signature is already there - a signed receipt established at the moment you published, not after an AI company decided to participate.
          </p>
          <div className="bg-muted/30 border border-border rounded-lg p-6 my-6">
            <p className="font-semibold text-lg mb-2">The Canonical Distinction</p>
            <p className="text-muted-foreground">
              ProRata and Dappier estimate which sources contributed to an AI output, but only when AI companies voluntarily integrate. That is algorithmic attribution scoring inside a closed system. Encypher's provenance is cryptographic proof embedded in the content before it enters any AI system - it works regardless of whether the AI company participates.
            </p>
          </div>
        </section>

        {/* What ProRata Does Well */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">What ProRata Does Well</h2>
          <p className="mb-4">
            For AI companies that want to operate with legitimate attribution, ProRata provides a credible mechanism. The attribution algorithm is sophisticated, designed to measure actual content contribution rather than rough approximations.
          </p>
          <p className="mb-4">
            The revenue-sharing model ProRata enables is commercially meaningful. Rather than a flat licensing fee, publishers receive payment proportional to how much their content actually contributed to AI outputs. High-quality sources that AI models draw on heavily earn more. This aligns incentives: publishers who produce content that AI finds valuable capture more value.
          </p>
          <p className="mb-4">
            ProRata also handles the accounting complexity that makes direct publisher-AI licensing difficult. Each query draws on hundreds of sources. Calculating fair attribution across all of them, then routing micro-payments to each publisher, is a problem that requires infrastructure. ProRata provides that infrastructure.
          </p>
        </section>

        {/* The Participation Dependency */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Participation Dependency</h2>
          <p className="mb-4">
            ProRata's architecture has one critical dependency: the AI company must integrate ProRata. Without that integration, ProRata has no visibility into what the model outputs or which sources it draws on.
          </p>
          <p className="mb-4">
            This is not a flaw unique to ProRata. It is the nature of output-side systems. Attribution can only be estimated from inside the generation process, and the generation process is inside the AI company's infrastructure. There is no way to instrument from outside.
          </p>
          <p className="mb-4">
            The practical consequence: ProRata's publisher network covers revenue from AI companies that have opted in. For AI companies that have not - whether because they have not evaluated ProRata, do not want to participate, or are smaller players outside the major licensing networks - there is no path to attribution through ProRata.
          </p>
          <p className="mb-4">
            The same applies retroactively. AI models that were trained before any integration was in place, on content already in their training corpus, are outside ProRata's reach regardless of current opt-in status. Attribution requires knowing what contributed at generation time; it cannot be reconstructed for past training runs.
          </p>
          <p className="mb-4">
            Encypher's signed content carries evidence regardless of what any AI company has or has not opted into. The signature is in the text. If that text was scraped into a training corpus before Encypher existed as a company, there is no retroactive remedy - but for all new content, the proof is established at publication and exists independent of any AI company's participation decision.
          </p>
        </section>

        {/* Proof vs Estimate */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Cryptographic Proof vs Algorithmic Estimate</h2>
          <p className="mb-4">
            For licensing negotiations and enforcement, the nature of the underlying claim matters.
          </p>
          <p className="mb-4">
            ProRata's attribution is an estimate - the algorithm's best assessment of which sources contributed to an output, weighted by inferred relevance and contribution. This is a sophisticated estimate, but it is still an estimate. An AI company challenging the attribution could dispute the weights, the algorithm, or the assumption of what "contribution" means for a model trained on billions of documents.
          </p>
          <p className="mb-4">
            Encypher's provenance is a cryptographic fact. The signature either verifies against the publisher's public key or it does not. The timestamp is embedded in the signature. The content hash is embedded in the signature. There is nothing algorithmic to dispute: the signature is either valid or forged, and ECDSA forgery is computationally infeasible.
          </p>
          <p className="mb-4">
            In a dispute - whether a licensing negotiation or a litigation proceeding - a cryptographic fact is a stronger foundation than an algorithmic estimate. This does not mean ProRata's attribution is worthless in disputes; it means it serves a different function. Attribution estimates are useful for showing the scope of usage and calculating fair compensation. Provenance proof is useful for establishing that the content was owned by the claimant, that rights were reserved, and that use without license constituted willful infringement.
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
                  <th className="text-left py-3 px-4 font-semibold text-muted-foreground">ProRata</th>
                </tr>
              </thead>
              <tbody>
                <ComparisonRow
                  feature="Layer in the stack"
                  encypher="Layer 2 - Content provenance (input-side)"
                  prorata="Layer 3 - Attribution / monetization (output-side)"
                  prorataPositive={true}
                />
                <ComparisonRow
                  feature="Requires AI company participation"
                  encypher="No - works unilaterally"
                  prorata="Yes - AI company must integrate API"
                />
                <ComparisonRow
                  feature="Proof type"
                  encypher="Cryptographic (deterministic)"
                  prorata="Algorithmic (estimated attribution)"
                />
                <ComparisonRow
                  feature="Established when"
                  encypher="At publication (prospective)"
                  prorata="At query time (retrospective)"
                />
                <ComparisonRow
                  feature="Works for non-participating AI companies"
                  encypher="Yes"
                  prorata="No"
                />
                <ComparisonRow
                  feature="Revenue from opted-in AI companies"
                  encypher="Via Encypher coalition"
                  prorata="Yes (primary value proposition)"
                  encypherPositive={true}
                  prorataPositive={true}
                />
                <ComparisonRow
                  feature="Proportional revenue by contribution"
                  encypher="No (tier-based licensing)"
                  prorata="Yes (attribution-weighted)"
                  encypherPositive={false}
                  prorataPositive={true}
                />
                <ComparisonRow
                  feature="Formal notice capability"
                  encypher="Yes (willful infringement trigger)"
                  prorata="No"
                />
                <ComparisonRow
                  feature="Machine-readable licensing terms in content"
                  encypher="Yes"
                  prorata="No"
                />
                <ComparisonRow
                  feature="Works for content already in training corpus"
                  encypher="Yes (if signed before scraping)"
                  prorata="No"
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
                Choose ProRata when...
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>You are working with AI companies that have opted into licensing</li>
                <li>You want proportional revenue based on actual content contribution</li>
                <li>You are a large publisher seeking structured revenue from cooperating AI companies</li>
                <li>Fair-value distribution per query is a priority</li>
              </ul>
            </div>
            <div className="border border-border rounded-lg p-6" style={{ borderColor: '#2a87c4' }}>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                Choose Encypher when...
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>You need enforcement capability against non-participating AI companies</li>
                <li>Cryptographic proof for licensing negotiations or litigation is required</li>
                <li>You want machine-readable rights embedded in every document at publication</li>
                <li>You are building a proactive ownership record, not waiting for opt-in</li>
                <li>Willful infringement documentation is part of your enforcement strategy</li>
              </ul>
            </div>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            The comprehensive strategy uses both: Encypher for the baseline proof layer that works unilaterally, ProRata for revenue routing from AI companies that have opted into attribution systems.
          </p>
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
          <h2 className="text-2xl font-bold mb-3">Establish proof before AI companies decide to participate</h2>
          <p className="text-muted-foreground mb-6">
            Encypher signs your content at publication. The proof is there when you need it - whether or not the AI company has opted into any attribution system.
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
