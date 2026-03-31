import type { Metadata } from 'next';
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
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import AISummary from '@/components/seo/AISummary';

export const metadata: Metadata = {
  title: 'Rights Management | Machine-Readable AI Content Licensing | Encypher',
  description: 'Control how AI companies use your content. Bronze (web crawling), Silver (RAG/retrieval), Gold (training) licensing tiers. C2PA 2.3 and RSL 1.0 compatible. Machine-readable terms embedded cryptographically in every document.',
  alternates: {
    canonical: 'https://encypher.com/rights-management',
  },
  openGraph: {
    title: 'Encypher Rights Management: Machine-Readable AI Licensing',
    description: 'Publisher-controlled licensing tiers for crawling, RAG, and AI training. Terms travel with your content. Compatible with C2PA 2.3 and RSL 1.0. Willful infringement documentation included.',
    url: 'https://encypher.com/rights-management',
    images: ['/og-image.png'],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Rights Management | Machine-Readable AI Licensing | Encypher',
    description: 'Bronze/Silver/Gold licensing tiers for AI crawling, RAG, and training. C2PA 2.3 and RSL 1.0 compatible. Terms travel with your content.',
  },
};

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypher.com';

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

const FAQS = [
  {
    q: 'Is Encypher compatible with RSL (Rights Signals Language)?',
    a: "Yes. Encypher is fully RSL 1.0 compatible and adds an extra layer of protection on top. RSL defines how rights signals are expressed in a machine-readable format -- Encypher embeds those signals cryptographically inside every document so they travel with the content itself, not just as a flag on a server. RSL tells AI companies what your terms are. Encypher makes it impossible for them to claim they never saw them.",
  },
  {
    q: 'Is Encypher compatible with C2PA?',
    a: "Yes. Encypher authored Section A.7 of the C2PA 2.3 specification (text provenance) alongside Adobe, Microsoft, Google, OpenAI, and the BBC. Erik Svilich co-chairs the C2PA Text Provenance Task Force. Every document signed with Encypher produces a C2PA 2.3-compliant manifest. If you are already using another C2PA tool, Encypher layers on top and adds the rights-resolution URL so AI companies can retrieve your licensing terms automatically.",
  },
  {
    q: 'Does Encypher work alongside Tollbit, ProRata, or Cloudflare bot management?',
    a: "Yes, and it is actually a deeper layer of security. Think of Tollbit, ProRata, and Cloudflare as locking your front door -- they control who gets in at the server level. Encypher locks every individual piece of content, so your rights terms travel with the content across the internet even after it leaves your site. If an AI company scrapes through a cache, a third-party aggregator, or a data broker, your signed content still carries your rights profile. The two approaches are complementary, not competing.",
  },
  {
    q: 'Do I need a developer to set this up?',
    a: "No. If you publish on WordPress or Ghost, setup is a plugin or webhook -- no code required. If you use a different CMS or publish directly, Encypher provides a simple REST API. Most publishers are fully set up within a day. Once configured, signing happens automatically in the background every time you publish.",
  },
  {
    q: 'Will this affect how my content looks or my search rankings?',
    a: "No. The cryptographic watermark is invisible -- it is embedded in zero-width Unicode characters between words, not in the visible text. Your content reads exactly the same to human visitors. Search engines are not affected. There is no change to your HTML structure, page speed, or SEO.",
  },
  {
    q: 'What about content I published before signing up?',
    a: "You can backfill existing content through the Encypher API or CMS integration. New content is signed automatically going forward. We recommend starting with your highest-value archives first -- evergreen articles, research, and long-form content are the most valuable to AI training datasets and the most worth protecting.",
  },
  {
    q: 'What if an AI company strips the watermark?',
    a: "Deliberate removal of a cryptographic watermark is itself evidence of willful infringement -- it demonstrates they knew the content was marked and chose to circumvent it. Encypher's evidence system logs the signed state of every document at time of publication. If a stripped version appears in a training dataset, the original signed version is the proof of ownership. Stripping the mark makes the legal case stronger, not weaker.",
  },
  {
    q: 'Do AI companies actually check these rights terms?',
    a: "Leading AI companies -- including those building legal compliance programs ahead of the EU AI Act -- are actively building systems to read machine-readable rights signals. The EU AI Act (effective August 2026) requires AI providers to respect machine-readable rights reservations. RSL and C2PA are the two formats being adopted industry-wide. Encypher supports both. Even for companies not yet checking today, having signed content establishes a documented record that your terms were available -- which is what converts unauthorized use into actionable willful infringement.",
  },
];

export default function RightsManagementPage() {
  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": FAQS.map(faq => ({
      "@type": "Question",
      "name": faq.q,
      "acceptedAnswer": { "@type": "Answer", "text": faq.a },
    })),
  };

  return (
    <div className="bg-background text-foreground">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />
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
            License Your Content<br />in the AI Age
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            Every document you sign embeds machine-readable licensing terms. AI companies discover
            your terms automatically. You control scraping, RAG, and training - separately.
            Powered by <Link href="/c2pa-standard" className="text-primary underline underline-offset-2 hover:no-underline">C2PA</Link> and built on <Link href="/content-provenance" className="text-primary underline underline-offset-2 hover:no-underline">content provenance</Link> infrastructure.
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
            {TIERS.map((tier, i) => {
              const IconComponent = tier.icon;
              const tierColor = i === 0
                ? 'text-amber-700 dark:text-amber-500'
                : i === 1
                ? 'text-zinc-500 dark:text-zinc-300'
                : 'text-yellow-600 dark:text-yellow-400';
              return (
                <div
                  key={tier.name}
                  className="bg-card p-6 rounded-lg border border-border hover:border-primary/30 transition-colors"
                >
                  <IconComponent className={`h-10 w-10 mb-4 ${tierColor}`} />
                  <h3 className={`text-lg font-semibold mb-1 ${tierColor}`}>{tier.name}</h3>
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
                Transform Unauthorized Use<br />into <Link href="/cryptographic-watermarking/legal-implications" className="text-primary underline underline-offset-2 hover:no-underline">Willful Infringement</Link>
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

      {/* FAQ */}
      <section className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Frequently Asked Questions
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-2xl mx-auto">
              Common questions from publishers evaluating rights management for their content.
            </p>
          </div>
          <div className="max-w-3xl mx-auto">
            <Accordion type="single" collapsible className="space-y-2">
              {FAQS.map((faq, i) => (
                <AccordionItem
                  key={i}
                  value={`faq-${i}`}
                  className="bg-card border border-border rounded-lg px-6"
                >
                  <AccordionTrigger className="text-left font-medium py-5 hover:no-underline">
                    {faq.q}
                  </AccordionTrigger>
                  <AccordionContent className="text-sm text-muted-foreground pb-5 leading-relaxed">
                    {faq.a}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
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
