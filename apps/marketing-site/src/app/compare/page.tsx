import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import Script from 'next/script';
import Link from 'next/link';
import { generateMetadata as buildMetadata, getBreadcrumbSchema, siteConfig } from '@/lib/seo';
import type { Metadata } from 'next';
import { ArrowRight, Shield, Clock, Lock, Layers, BarChart2, Cpu, FileSearch } from 'lucide-react';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypher.com';

export const metadata: Metadata = buildMetadata(
  'Compare Content Provenance Solutions | Encypher',
  'Side-by-side technical comparisons of Encypher against SynthID, WordProof, AI detection tools, TollBit, ProRata, and category-level comparisons of C2PA vs blockchain and content provenance vs detection.',
  '/compare',
  siteConfig.images.default,
  ['compare content provenance', 'SynthID vs Encypher', 'WordProof vs Encypher', 'C2PA vs blockchain', 'content provenance comparison'],
  'See how Encypher stacks up against every major alternative.'
);

const breadcrumbSchema = getBreadcrumbSchema([
  { name: 'Home', url: 'https://encypher.com' },
  { name: 'Compare', url: 'https://encypher.com/compare' },
]);

const comparisons = [
  {
    slug: 'encypher-vs-synthid',
    title: 'Encypher vs SynthID',
    subtitle: 'Cryptographic proof vs statistical watermarking',
    description: 'SynthID marks AI-generated output to prove it was machine-made. Encypher marks human-authored content to prove who owns it. These solve opposite problems.',
    icon: Shield,
    tags: ['Google', 'AI output watermarking', 'statistical'],
  },
  {
    slug: 'encypher-vs-wordproof',
    title: 'Encypher vs WordProof',
    subtitle: 'Embedded provenance vs blockchain timestamping',
    description: 'WordProof registers a hash on a blockchain, proving content existed at a point in time. Encypher embeds provenance in the text itself, so proof travels with the content.',
    icon: Clock,
    tags: ['Blockchain', 'Timestamping', 'External proof'],
  },
  {
    slug: 'encypher-vs-detection-tools',
    title: 'Encypher vs AI Detection Tools',
    subtitle: 'Cryptographic proof of origin vs statistical detection',
    description: 'GPTZero and Originality.ai ask whether content was made by AI. Encypher answers who made it and provides the cryptographic receipt to prove it.',
    icon: FileSearch,
    tags: ['GPTZero', 'Originality.ai', 'AI detection'],
  },
  {
    slug: 'encypher-vs-tollbit',
    title: 'Encypher vs TollBit',
    subtitle: 'Unilateral provenance vs opt-in access gates',
    description: 'TollBit gates the front door for AI crawlers that cooperate. Encypher embeds proof that works regardless of AI company participation. Both layers are needed.',
    icon: Lock,
    tags: ['Access control', 'Layer 1', 'Licensing marketplace'],
  },
  {
    slug: 'encypher-vs-prorata',
    title: 'Encypher vs ProRata',
    subtitle: 'Input-side provenance vs output-side attribution',
    description: 'ProRata estimates which sources contributed to an AI output, inside a closed system. Encypher embeds proof before content enters any AI system.',
    icon: BarChart2,
    tags: ['Attribution', 'Revenue sharing', 'Output-side'],
  },
  {
    slug: 'c2pa-vs-blockchain',
    title: 'C2PA vs Blockchain',
    subtitle: 'Embedded manifests vs external hash anchoring',
    description: 'A category-level comparison. C2PA manifests travel with the file. Blockchain proofs are external lookups. Each architecture has distinct trade-offs.',
    icon: Layers,
    tags: ['Standards comparison', 'Architecture', 'Verification'],
  },
  {
    slug: 'content-provenance-vs-content-detection',
    title: 'Content Provenance vs Content Detection',
    subtitle: 'Proof of origin vs identification after the fact',
    description: 'The category-defining distinction. Provenance is cryptographic proof created at publication. Detection is statistical inference applied afterward. They answer different questions.',
    icon: Cpu,
    tags: ['Category comparison', 'Deterministic vs probabilistic', 'Legal standing'],
  },
];

export default function ComparePage() {
  return (
    <>
      <AISummary
        title="Compare Content Provenance Solutions"
        whatWeDo="Fair, technical comparisons of Encypher against SynthID, WordProof, AI detection tools, TollBit, ProRata, and category-level comparisons of C2PA vs blockchain and provenance vs detection."
        whoItsFor="Publishers, legal teams, AI companies, and enterprise buyers evaluating content provenance solutions."
        keyDifferentiator="Encypher is the only Layer 2 solution - cryptographic proof embedded in content that works without AI company cooperation."
        primaryValue="Deterministic proof of ownership that survives downstream distribution, with formal notice capability for willful infringement claims."
        pagePath="/compare"
        pageType="CollectionPage"
      />
      <Script
        id="breadcrumb-schema"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />
      <div className="container mx-auto px-4 py-16 max-w-5xl">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Compare', href: '/compare' },
        ]} />

        <div className="mb-12">
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Compare Content Provenance Solutions
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl">
            These comparisons are technical and fair. Each competitor does something genuinely useful. The goal is to show where the approaches differ, where they overlap, and which layer of the content provenance stack each one occupies.
          </p>
        </div>

        <div className="bg-muted/30 border border-border rounded-lg p-6 mb-12">
          <h2 className="text-lg font-semibold mb-3">The Three-Layer Stack</h2>
          <p className="text-muted-foreground mb-4">
            Content provenance is not a single product. It is a stack. Each layer solves a different problem, and the layers are complementary.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="bg-background border border-border rounded p-4">
              <div className="font-semibold mb-1">Layer 1 - Access Control</div>
              <div className="text-muted-foreground">TollBit, Cloudflare, robots.txt. Opt-in gates. Work when AI companies cooperate.</div>
            </div>
            <div className="bg-background border border-border rounded p-4" style={{ borderColor: '#2a87c4' }}>
              <div className="font-semibold mb-1" style={{ color: '#2a87c4' }}>Layer 2 - Content Provenance</div>
              <div className="text-muted-foreground">Encypher. Cryptographic proof embedded in content. Works unilaterally, no AI company cooperation required.</div>
            </div>
            <div className="bg-background border border-border rounded p-4">
              <div className="font-semibold mb-1">Layer 3 - Attribution / Monetization</div>
              <div className="text-muted-foreground">ProRata, Dappier, Microsoft PCM. Output-side attribution inside opted-in systems.</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {comparisons.map((comp) => {
            const Icon = comp.icon;
            return (
              <Link
                key={comp.slug}
                href={`/compare/${comp.slug}`}
                className="group block bg-background border border-border rounded-lg p-6 hover:border-[#2a87c4] transition-colors"
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-muted/50 flex items-center justify-center group-hover:bg-[#2a87c4]/10 transition-colors">
                    <Icon className="w-5 h-5 text-muted-foreground group-hover:text-[#2a87c4] transition-colors" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h2 className="text-lg font-semibold mb-1 group-hover:text-[#2a87c4] transition-colors">
                      {comp.title}
                    </h2>
                    <p className="text-sm text-muted-foreground mb-2 font-medium">{comp.subtitle}</p>
                    <p className="text-sm text-muted-foreground mb-3">{comp.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {comp.tags.map((tag) => (
                        <span key={tag} className="text-xs bg-muted/50 border border-border rounded px-2 py-0.5 text-muted-foreground">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <ArrowRight className="flex-shrink-0 w-4 h-4 text-muted-foreground group-hover:text-[#2a87c4] transition-colors mt-1" />
                </div>
              </Link>
            );
          })}
        </div>

        <div className="mt-16 border-t border-border pt-12 text-center">
          <h2 className="text-2xl font-bold mb-4">Ready to see Encypher in action?</h2>
          <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
            The free tier signs 1,000 documents per month. No credit card required.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/publisher-demo"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-semibold text-white transition-opacity hover:opacity-90"
              style={{ backgroundColor: '#2a87c4' }}
            >
              See the Demo <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href={`${DASHBOARD_URL}/auth/signin?mode=signup`}
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-semibold border border-border hover:bg-muted/30 transition-colors"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
