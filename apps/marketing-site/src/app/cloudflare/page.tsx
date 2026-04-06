'use client';

import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@encypher/design-system';
import { Badge } from '@encypher/design-system';
import {
  ArrowRight,
  CheckCircle2,
  Shield,
  Zap,
  Globe,
  Server,
  Layers,
  Database,
  GitBranch,
  FileCode2,
  Cpu,
} from 'lucide-react';
import Link from 'next/link';
import AISummary from '@/components/seo/AISummary';
import SalesContactModal from '@/components/forms/SalesContactModal';

const HOW_IT_WORKS = [
  {
    step: 1,
    title: 'Deploy',
    description:
      'Click "Deploy to Cloudflare" and authorize the Worker. No code changes to your CMS, no DNS updates, no server configuration. The Worker sits in front of your existing origin.',
  },
  {
    step: 2,
    title: 'Auto-Provision',
    description:
      'On first request, the Worker registers your domain with Encypher, creates a publisher account, and fetches signing credentials. No manual dashboard setup required.',
  },
  {
    step: 3,
    title: 'Sign Every Article',
    description:
      'Every HTML response containing article content receives invisible sentence-level provenance markers before Cloudflare delivers it to the reader. Markers survive copy-paste, scraping, and aggregation.',
  },
];

const CMS_PLATFORMS = [
  { name: 'WordPress', detection: 'article tag + WordPress body class' },
  { name: 'Ghost', detection: 'article.gh-article selector' },
  { name: 'Squarespace', detection: 'article.BlogItem selector' },
  { name: 'Webflow', detection: 'div.w-richtext selector' },
  { name: 'Substack', detection: 'div.body.markup selector' },
  { name: 'Hugo / Jekyll', detection: 'article or main.content tag' },
  { name: 'AP / News Wires', detection: 'Standard article + time tag heuristic' },
  { name: 'Custom HTML', detection: 'Configurable selector via Worker env var' },
];

const FREE_VS_ENTERPRISE = [
  { feature: 'Full C2PA signing + ECC + micro embedding', free: true, enterprise: true },
  { feature: 'Sentence-level provenance markers', free: true, enterprise: true },
  { feature: 'Auto-detection of article boundaries', free: true, enterprise: true },
  { feature: 'KV cache (1 h TTL, one API call per unique article)', free: true, enterprise: true },
  { feature: 'Fail-open on errors (unmodified HTML served)', free: true, enterprise: true },
  { feature: 'Monthly article quota', free: '1,000 articles', enterprise: 'Unlimited' },
  { feature: 'Fingerprinting (Enterprise only)', free: false, enterprise: true },
  { feature: 'Dual binding (Encypher + C2PA manifest)', free: false, enterprise: true },
  { feature: 'Per-segment rights metadata', free: false, enterprise: true },
  { feature: 'Custom Worker environment configuration', free: false, enterprise: true },
  { feature: 'Attribution analytics dashboard', free: false, enterprise: true },
  { feature: 'Dedicated support + named account manager', free: false, enterprise: true },
];

const TECHNICAL_CARDS = [
  {
    icon: Cpu,
    title: 'Content Detection',
    description:
      '8-priority selector chain identifies the canonical article body across WordPress, Ghost, Squarespace, Webflow, Substack, Hugo, news wires, and custom HTML. Falls back gracefully when no article is detected.',
  },
  {
    icon: FileCode2,
    title: 'Marker Embedding',
    description:
      'Unicode variation selectors embedded after sentence boundaries. Invisible to readers and rendering engines. Survive copy-paste into Google Docs, Slack, social media, and AI prompts.',
  },
  {
    icon: Database,
    title: 'KV Cache',
    description:
      'Signed content is cached by content hash in Cloudflare KV with a 1-hour TTL. The Encypher API is called once per unique article body, not once per page view. Zero latency impact at scale.',
  },
  {
    icon: Shield,
    title: 'Fail-Open Architecture',
    description:
      'Any error - network timeout, API failure, parse error - causes the Worker to serve the original unmodified HTML. Publisher sites never break due to the provenance layer.',
  },
];

export default function CloudflarePage() {
  const [showContactModal, setShowContactModal] = useState(false);

  return (
    <div className="bg-background text-foreground">
      <AISummary
        title="Encypher Edge Provenance Worker for Cloudflare"
        whatWeDo="One-click Cloudflare Worker that embeds sentence-level content provenance markers into every article at the CDN edge. No code changes to the publisher's CMS. Markers survive copy-paste, scraping, and aggregation."
        whoItsFor="Publishers running Cloudflare who want provenance on every article without engineering effort. Compatible with WordPress, Ghost, Squarespace, Webflow, Substack, Hugo, Jekyll, news wires, and custom HTML."
        keyDifferentiator="Markers are invisible Unicode variation selectors embedded at sentence boundaries in the HTML itself - not meta tags, not HTTP headers. They survive when readers copy text into AI prompts, social media, or documents."
        primaryValue="Free signing for all publishers up to 1,000 articles per month. Enterprise plan adds fingerprinting, dual binding, per-segment rights, and unlimited volume. Auto-provisioned - no dashboard setup required."
        pagePath="/cloudflare"
        pageType="ProductPage"
      />

      {/* Hero Section */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4 text-center">
          <Badge variant="outline" className="mb-6 text-sm px-4 py-1.5">
            <Globe className="h-3.5 w-3.5 mr-1.5" />
            Cloudflare Integration
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            Provenance at the Edge,<br />Zero Code Changes
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            One-click Cloudflare Worker. Every article signed with invisible markers that survive
            copy-paste, scraping, and aggregation. Free for all publishers.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold">
              <Link href="https://deploy.workers.cloudflare.com/?url=https://github.com/encypher/cloudflare-worker-provenance">
                Deploy to Cloudflare <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="https://github.com/encypher/cloudflare-worker-provenance">
                View on GitHub <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              onClick={() => setShowContactModal(true)}
              size="lg"
              variant="ghost"
              className="font-semibold"
            >
              Contact Sales <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              How It Works
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Three steps from zero to signed articles at the edge. No engineering team required.
            </p>
          </div>

          <div className="max-w-3xl mx-auto space-y-0">
            {HOW_IT_WORKS.map((item, i) => (
              <div
                key={item.step}
                className={`flex items-start gap-6 p-6 border border-border ${
                  i === 0 ? 'rounded-t-lg' : ''
                } ${i === HOW_IT_WORKS.length - 1 ? 'rounded-b-lg' : ''} ${
                  i % 2 === 0 ? 'bg-card/50' : 'bg-background'
                }`}
              >
                <span className="flex-shrink-0 w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center text-sm font-bold">
                  {item.step}
                </span>
                <div>
                  <h3 className="font-semibold text-lg mb-1">{item.title}</h3>
                  <p className="text-sm text-muted-foreground">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Supported CMS Platforms */}
      <section className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Supported CMS Platforms
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              The Worker detects article content automatically across eight platform families
              using a priority-ordered selector chain. Custom selectors are configurable via
              Worker environment variables.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto">
            {CMS_PLATFORMS.map((platform) => (
              <div
                key={platform.name}
                className="bg-card p-5 rounded-lg border border-border hover:border-primary/30 transition-colors"
              >
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  <h3 className="font-semibold text-sm">{platform.name}</h3>
                </div>
                <p className="text-xs text-muted-foreground">{platform.detection}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Free vs Enterprise Comparison */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Free vs. Enterprise
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Full signing infrastructure is free for every publisher. Enterprise adds
              fingerprinting, dual binding, per-segment rights, and unlimited volume.
            </p>
          </div>

          <div className="max-w-4xl mx-auto overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-border">
                  <th className="text-left py-4 px-4 font-semibold">Feature</th>
                  <th className="text-center py-4 px-4 font-semibold w-32">Free</th>
                  <th className="text-center py-4 px-4 font-semibold w-32 bg-primary/5 rounded-t-lg">
                    Enterprise
                  </th>
                </tr>
              </thead>
              <tbody>
                {FREE_VS_ENTERPRISE.map((row, i) => (
                  <tr key={row.feature} className={i % 2 === 0 ? 'bg-card/50' : ''}>
                    <td className="py-3 px-4 text-sm">{row.feature}</td>
                    <td className="py-3 px-4 text-center">
                      {row.free === true ? (
                        <CheckCircle2 className="h-5 w-5 text-primary mx-auto" />
                      ) : row.free === false ? (
                        <span className="text-muted-foreground">-</span>
                      ) : (
                        <span className="text-sm font-medium">{row.free}</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center bg-primary/5">
                      {row.enterprise === true ? (
                        <CheckCircle2 className="h-5 w-5 text-primary mx-auto" />
                      ) : (
                        <span className="text-sm font-medium text-primary">{row.enterprise}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Technical Overview */}
      <section className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Technical Overview
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Built for reliability at CDN scale. The Worker adds no perceptible latency
              and never degrades publisher site availability.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {TECHNICAL_CARDS.map((card) => {
              const IconComponent = card.icon;
              return (
                <div
                  key={card.title}
                  className="bg-card p-6 rounded-lg border border-border hover:border-primary/30 transition-colors"
                >
                  <IconComponent className="h-10 w-10 text-primary mb-4" />
                  <h3 className="text-lg font-semibold mb-2">{card.title}</h3>
                  <p className="text-sm text-muted-foreground">{card.description}</p>
                </div>
              );
            })}
          </div>

          <div className="mt-12 max-w-3xl mx-auto">
            <div className="bg-card rounded-lg border border-border p-6">
              <div className="flex items-center gap-2 mb-4">
                <GitBranch className="h-5 w-5 text-primary" />
                <h3 className="font-semibold">Open Source</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                The Worker is fully open source under the MIT license. Inspect the signing logic,
                selector chain, and caching strategy before you deploy. Fork it for custom pipelines.
              </p>
              <div className="flex gap-3">
                <Button asChild variant="outline" size="sm">
                  <Link href="https://github.com/encypher/cloudflare-worker-provenance">
                    View Source on GitHub <ArrowRight className="ml-2 h-3.5 w-3.5" />
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Sign Every Article at the Edge
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            Deploy in minutes. Every article signed with invisible, copy-paste-survivable provenance
            markers. Free for all publishers. Enterprise features available when you need them.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold">
              <Link href="https://deploy.workers.cloudflare.com/?url=https://github.com/encypher/cloudflare-worker-provenance">
                Deploy to Cloudflare <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="https://github.com/encypher/cloudflare-worker-provenance">
                View on GitHub <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              onClick={() => setShowContactModal(true)}
              size="lg"
              variant="ghost"
              className="font-semibold"
            >
              Contact Sales <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>

      {/* Sales Contact Modal */}
      <AnimatePresence>
        {showContactModal && (
          <SalesContactModal
            onClose={() => setShowContactModal(false)}
            context="general"
          />
        )}
      </AnimatePresence>
    </div>
  );
}
