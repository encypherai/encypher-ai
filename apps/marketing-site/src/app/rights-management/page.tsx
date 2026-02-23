import Link from 'next/link';
import {
  ArrowRight,
  CheckCircle2,
  Globe,
  Database,
  Cpu,
  Shield,
  ListChecks,
  Bot,
  Scale,
  FileSearch,
  ScrollText,
  Users,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import AISummary from '@/components/seo/AISummary';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypherai.com';

const TIERS = [
  {
    icon: Globe,
    name: 'Bronze',
    use: 'Crawling & Scraping',
    description:
      'Controls broad read-only access: search indexing, price comparisons, web archiving, and general AI data collection.',
    items: [
      'Web crawlers (Googlebot, GPTBot)',
      'Training data collection',
      'RSS / feed aggregation',
      'robots.txt-aligned signals',
    ],
  },
  {
    icon: Database,
    name: 'Silver',
    use: 'RAG & Retrieval',
    description:
      'Controls AI-powered search and retrieval-augmented generation pipelines — the largest current use case.',
    items: [
      'RAG grounding data',
      'Real-time AI search',
      'Perplexity, SearchGPT, Bing AI',
      'Enterprise AI assistants',
    ],
  },
  {
    icon: Cpu,
    name: 'Gold',
    use: 'Training & Fine-tuning',
    description:
      'Controls use of your content for AI model training and fine-tuning — the highest-value licensing category.',
    items: [
      'LLM pre-training datasets',
      'Fine-tuning & RLHF',
      'Model evaluation benchmarks',
      'Synthetic data generation',
    ],
  },
];

const HOW_IT_WORKS = [
  {
    icon: Shield,
    step: '1',
    title: 'Sign',
    desc: 'Publish content with Encypher. Every document gets a C2PA 2.3-compliant signature with your rights_resolution_url embedded in the manifest.',
  },
  {
    icon: ListChecks,
    step: '2',
    title: 'Publish Profile',
    desc: 'Set your Bronze / Silver / Gold terms once. They apply to all signed content automatically.',
  },
  {
    icon: Bot,
    step: '3',
    title: 'AI Discovers',
    desc: 'AI crawlers resolve the rights URL and receive W3C ODRL-compatible terms in RSL 1.0 format — machine-readable, no manual review required.',
  },
  {
    icon: Scale,
    step: '4',
    title: 'License or Notice',
    desc: 'Compliant AI companies license through the coalition. Non-compliant ones face a formal infringement notice.',
  },
];

const ENFORCEMENT_ITEMS = [
  'Immutable notice with tamper-evident evidence chain',
  'Delivery confirmation and timestamped proof of receipt',
  'Documentation of marked content in their pipeline',
  'Chain-of-custody from signing through detection',
];

const FORMAL_NOTICE_FEATURES = [
  'Cryptographically-backed notice letter',
  'Verification API access instructions for recipient',
  'Evidence of marked content in training pipeline',
  'Tamper-evident delivery receipt',
];

const EVIDENCE_FEATURES = [
  'Merkle tree proofs — sentence-level provenance',
  'Chain-of-custody documentation',
  'Tamper-evident manifest records',
  'Formal notice delivery records',
  'Timeline reconstruction',
  'Cryptographic verification instructions for counsel',
  'Export in standard litigation support formats',
];

const PRICING_ROWS = [
  { feature: 'Document signing (C2PA 2.3)', price: 'Free (1,000 / mo)' },
  { feature: 'Rights profile (Bronze / Silver / Gold)', price: 'Free' },
  { feature: 'Public rights resolution URL', price: 'Free' },
  { feature: 'Coalition enrollment & content indexing', price: 'Free' },
  { feature: 'Attribution Analytics dashboard', price: '$299 / mo' },
  { feature: 'Formal Notice Package', price: '$499 / notice' },
  { feature: 'Evidence Package', price: '$999 / package' },
  { feature: 'Enforcement Bundle (all enforcement tools)', price: '$999 / mo — save 57%' },
];

const AI_COMPANY_FEATURES = [
  {
    icon: FileSearch,
    title: 'Quote Integrity API',
    desc: 'Verify AI attribution accuracy before publishing. Prove whether a cited quote is accurate, approximate, or hallucinated.',
  },
  {
    icon: ScrollText,
    title: 'RSL 1.0 & W3C ODRL Compatible',
    desc: 'GET /public/rights/organization/{id} returns RSL 1.0 XML and W3C ODRL-compatible JSON. Drop into existing rights infrastructure without format conversion.',
  },
  {
    icon: Users,
    title: 'Coalition Licensing',
    desc: 'Single agreement covers all coalition publishers. Structured licensing at scale, not 1:1 negotiations.',
  },
];

export default function RightsManagementPage() {
  return (
    <div className="bg-background text-foreground">
      <AISummary
        title="Rights Management — Machine-Readable Licensing for the AI Age"
        whatWeDo="Publisher-controlled licensing terms embedded cryptographically in every piece of content. Bronze (crawling), Silver (RAG), Gold (training) tiers. Formal notice system establishes willful infringement. Evidence packages provide court-ready proof."
        whoItsFor="Publishers, media organizations, and content creators who want to control how their content is used by AI companies. AI companies who want to license content at scale with machine-readable terms."
        keyDifferentiator="Every signed document embeds a rights_resolution_url. AI crawlers that resolve this URL receive machine-readable licensing terms. The three-tier model aligns with how AI companies actually use content."
        primaryValue="Transform unauthorized AI use from innocent mistake to willful infringement. Establish a formal licensing framework backed by cryptographic proof."
      />

      {/* Hero */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4 text-center">
          <Badge variant="outline" className="mb-6 text-sm px-4 py-1.5">
            <Scale className="h-3.5 w-3.5 mr-1.5" />
            C2PA 2.3 Compatible &middot; RSL 1.0 Compatible
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            License Your Content<br />to the AI Age
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            Every document you sign embeds machine-readable licensing terms. AI companies discover
            your terms automatically. You control scraping, RAG, and training — separately.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold">
              <Link href={`${DASHBOARD_URL}/rights`}>
                Set Up Your Rights Profile <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="#how-it-works">
                How it works <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Three Tiers */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Three Tiers, Three Use Cases
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Control AI access to your content at three distinct levels, each aligned to how AI
              companies actually use content.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {TIERS.map((tier) => {
              const IconComponent = tier.icon;
              return (
                <div
                  key={tier.name}
                  className="bg-card p-6 rounded-lg border border-border hover:border-primary/30 transition-colors"
                >
                  <IconComponent className="h-10 w-10 text-primary mb-4" />
                  <h3 className="text-lg font-semibold mb-1">{tier.name}</h3>
                  <p className="text-xs text-muted-foreground mb-3">{tier.use}</p>
                  <p className="text-sm text-muted-foreground mb-4">{tier.description}</p>
                  <ul className="space-y-1.5">
                    {tier.items.map((item) => (
                      <li key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
                        <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">How It Works</h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              From your first signed document to a machine-readable rights infrastructure in four steps.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 max-w-5xl mx-auto">
            {HOW_IT_WORKS.map((item) => {
              const IconComponent = item.icon;
              return (
                <div key={item.step} className="text-center">
                  <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                    <IconComponent className="h-7 w-7 text-primary" />
                  </div>
                  <h3 className="font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-muted-foreground">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Enforcement */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="max-w-5xl mx-auto grid gap-10 lg:grid-cols-2 items-center">
            <div>
              <p className="text-xs font-semibold text-primary uppercase tracking-wide mb-3">
                Enforcement
              </p>
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
                Transform Unauthorized Use<br />into Willful Infringement
              </h2>
              <p className="text-muted-foreground mb-4">
                AI companies can no longer claim ignorance. When your rights profile is embedded in
                every signed document, using your content without a license is knowingly ignoring
                machine-readable terms.
              </p>
              <p className="text-muted-foreground mb-6">
                Issue a formal notice at any time. Our cryptographic evidence system creates an
                immutable record: when you published it, when they accessed it, and that your terms
                were available and ignored.
              </p>
              <ul className="space-y-2">
                {ENFORCEMENT_ITEMS.map((item) => (
                  <li key={item} className="flex items-start gap-2 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-card rounded-lg border border-border p-6">
              <p className="text-sm font-semibold mb-1">Formal Notice Package</p>
              <p className="text-2xl font-bold mb-1">$499</p>
              <p className="text-xs text-muted-foreground mb-5">
                One-time fee per formal notice issued to a specific AI company.
              </p>
              <ul className="space-y-2">
                {FORMAL_NOTICE_FEATURES.map((item) => (
                  <li key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Evidence Package */}
      <section className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="max-w-5xl mx-auto grid gap-10 lg:grid-cols-2 items-center">
            <div className="bg-card rounded-lg border border-border p-6">
              <p className="text-sm font-semibold mb-1">Evidence Package</p>
              <p className="text-2xl font-bold mb-1">$999</p>
              <p className="text-xs text-muted-foreground mb-5">
                Complete litigation-support package for any infringement claim.
              </p>
              <ul className="space-y-2">
                {EVIDENCE_FEATURES.map((item) => (
                  <li key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-xs font-semibold text-primary uppercase tracking-wide mb-3">
                Litigation Ready
              </p>
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
                Court-Ready Evidence<br />in Minutes
              </h2>
              <p className="text-muted-foreground">
                Generate a complete evidence package for any infringement claim. Merkle proofs
                establish sentence-level provenance from the moment of signing. Every event in the
                chain is cryptographically linked and independently verifiable.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Simple, Transparent Pricing
            </h2>
            <p className="text-lg text-muted-foreground mt-4">
              Free signing infrastructure. Paid only for enforcement tools.
            </p>
          </div>
          <div className="max-w-3xl mx-auto overflow-x-auto">
            <table className="w-full text-sm border border-border rounded-lg overflow-hidden">
              <thead>
                <tr className="border-b border-border bg-muted/50">
                  <th className="text-left px-5 py-3 font-medium text-muted-foreground">Feature</th>
                  <th className="text-right px-5 py-3 font-medium text-muted-foreground">Price</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {PRICING_ROWS.map((row, i) => (
                  <tr key={row.feature} className={i % 2 === 0 ? 'bg-card/50' : ''}>
                    <td className="px-5 py-3 text-foreground">{row.feature}</td>
                    <td className="px-5 py-3 text-right font-medium">{row.price}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="mt-4 p-4 rounded-lg bg-primary/5 border border-primary/10 text-sm text-muted-foreground">
              <strong className="text-foreground">Coalition licensing revenue:</strong> When AI
              companies license content through the Encypher Coalition, the majority of revenue goes
              to publishers. Same splits for all tiers — contact us for details.
            </div>
          </div>
        </div>
      </section>

      {/* For AI Companies */}
      <section className="py-20 w-full bg-[#1B2F50] border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-white">
              For AI Companies
            </h2>
            <p className="text-lg mt-4 max-w-2xl mx-auto text-slate-300">
              Access machine-readable licensing terms for every Encypher-signed publisher. Build
              your provenance infrastructure once — stay compliant across the entire ecosystem.
            </p>
          </div>
          <div className="grid sm:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {AI_COMPANY_FEATURES.map((item) => {
              const IconComponent = item.icon;
              return (
                <div
                  key={item.title}
                  className="rounded-lg bg-white/5 border border-white/10 p-6 hover:bg-white/10 transition-colors"
                >
                  <IconComponent className="h-8 w-8 text-sky-300 mb-4" />
                  <h3 className="font-semibold text-white mb-2">{item.title}</h3>
                  <p className="text-sm text-slate-300">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Take Control?
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            Set up your rights profile in minutes. Free to start. Enforcement tools available when
            you need them.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold">
              <Link href={`${DASHBOARD_URL}/rights`}>
                Set Up Your Rights Profile <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/pricing">
                View Pricing <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
