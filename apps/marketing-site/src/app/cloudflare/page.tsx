'use client';

import { useState, useCallback } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@encypher/design-system';
import { Badge } from '@encypher/design-system';
import {
  ArrowRight,
  CheckCircle2,
  Shield,
  Globe,
  Database,
  FileCode2,
  Cpu,
  GitBranch,
  Clipboard,
  ClipboardCheck,
} from 'lucide-react';
import Link from 'next/link';
import AISummary from '@/components/seo/AISummary';
import SalesContactModal from '@/components/forms/SalesContactModal';

const DEPLOY_BASE_URL =
  'https://deploy.workers.cloudflare.com/?url=https://github.com/encypherai/edge-provenance-worker';

const HOW_IT_WORKS = [
  {
    step: 1,
    title: 'Deploy',
    description:
      'Add the Encypher Worker to your Cloudflare zone. No changes to your CMS, no DNS migration, no engineering resources. Works alongside your existing setup.',
  },
  {
    step: 2,
    title: 'Automatic Setup',
    description:
      'The Worker connects to your Encypher account and begins protecting content immediately. No manual configuration required.',
  },
  {
    step: 3,
    title: 'Protect Every Article',
    description:
      'Every article on your site receives invisible provenance markers before it reaches readers. When that content is copied, scraped, or republished, you can trace it back to its source.',
  },
];

const CMS_PLATFORMS = [
  { name: 'WordPress', detection: 'Self-hosted and WordPress.com' },
  { name: 'Ghost', detection: 'All Ghost-powered publications' },
  { name: 'Squarespace', detection: 'Blog and article pages' },
  { name: 'Webflow', detection: 'Rich text content blocks' },
  { name: 'Substack', detection: 'Newsletter and post pages' },
  { name: 'Hugo / Jekyll', detection: 'Static site generators' },
  { name: 'News Wires', detection: 'AP, Reuters, and wire formats' },
  { name: 'Custom HTML', detection: 'Any site with configurable selectors' },
];

const FREE_VS_ENTERPRISE = [
  { feature: 'Content provenance on every article', free: true, enterprise: true },
  { feature: 'Sentence-level content tracking', free: true, enterprise: true },
  { feature: 'Automatic CMS compatibility', free: true, enterprise: true },
  { feature: 'Zero performance impact', free: true, enterprise: true },
  { feature: 'Guaranteed site availability', free: true, enterprise: true },
  { feature: 'Monthly article volume', free: '1,000 articles', enterprise: 'Unlimited' },
  { feature: 'Leak source identification', free: false, enterprise: true },
  { feature: 'C2PA manifest compliance', free: false, enterprise: true },
  { feature: 'Granular content licensing per segment', free: false, enterprise: true },
  { feature: 'Custom deployment configuration', free: false, enterprise: true },
  { feature: 'Attribution analytics dashboard', free: false, enterprise: true },
  { feature: 'Dedicated support and named account manager', free: false, enterprise: true },
];

const TECHNICAL_CARDS = [
  {
    icon: Cpu,
    title: 'Works With Every CMS',
    description:
      'Automatic content detection across WordPress, Ghost, Squarespace, Webflow, Substack, Hugo, news wires, and custom HTML. No per-CMS configuration needed.',
  },
  {
    icon: FileCode2,
    title: 'Invisible, Persistent Protection',
    description:
      'Provenance markers are invisible to readers. They survive copy-paste into Google Docs, Slack, social media, and AI prompts, so you can trace content wherever it travels.',
  },
  {
    icon: Database,
    title: 'Zero Performance Impact',
    description:
      'Signed content is cached at the edge. Your site loads at the same speed with or without provenance enabled. No added latency for readers.',
  },
  {
    icon: Shield,
    title: 'Your Site Never Breaks',
    description:
      'If anything goes wrong, the Worker serves your original page unchanged. Provenance is additive. It never degrades your site availability or reader experience.',
  },
];

export default function CloudflarePage() {
  const [showContactModal, setShowContactModal] = useState(false);
  const [domain, setDomain] = useState('');
  const [copied, setCopied] = useState(false);

  const routePattern = domain.trim()
    ? `*${domain.trim().replace(/^https?:\/\//, '').replace(/^www\./, '').replace(/\/+$/, '')}/*`
    : '';

  const handleDeploy = useCallback(async () => {
    if (!routePattern) {
      window.open(DEPLOY_BASE_URL, '_blank');
      return;
    }
    try {
      await navigator.clipboard.writeText(routePattern);
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    } catch {
      // Clipboard not available, proceed anyway
    }
    window.open(DEPLOY_BASE_URL, '_blank');
  }, [routePattern]);

  return (
    <div className="bg-background text-foreground">
      <AISummary
        title="Encypher Edge Provenance for Cloudflare"
        whatWeDo="Cloudflare Worker that adds invisible content provenance to every article at the CDN edge. No code changes to the publisher's CMS. Provenance markers survive copy-paste, scraping, and aggregation."
        whoItsFor="Publishers running Cloudflare who want to protect and track their content without engineering effort. Compatible with WordPress, Ghost, Squarespace, Webflow, Substack, Hugo, Jekyll, news wires, and custom HTML."
        keyDifferentiator="Provenance is embedded directly in article text, not in meta tags or HTTP headers. When content is copied into AI prompts, social media, or documents, the provenance travels with it."
        primaryValue="Free for all publishers up to 1,000 articles per month. Enterprise plan adds leak source identification, C2PA compliance, granular licensing, and unlimited volume."
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
            Protect Every Article<br />at the Edge
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            Add invisible content provenance to every article on your Cloudflare site.
            Track where your content goes when it is copied, scraped, or fed into AI models.
            No CMS changes. Free for all publishers.
          </p>

          {/* Domain input deploy flow */}
          <div className="max-w-lg mx-auto mb-8">
            <div className="flex gap-2">
              <input
                type="text"
                value={domain}
                onChange={(e) => { setDomain(e.target.value); setCopied(false); }}
                placeholder="yourdomain.com"
                className="flex-1 text-base px-4 py-3 rounded-lg border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
              <Button
                size="lg"
                className="font-semibold whitespace-nowrap"
                onClick={handleDeploy}
              >
                Deploy to Cloudflare <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
            {routePattern && (
              <p className="text-sm text-muted-foreground mt-3 flex items-center justify-center gap-2">
                {copied ? (
                  <ClipboardCheck className="h-4 w-4 text-primary" />
                ) : (
                  <Clipboard className="h-4 w-4" />
                )}
                <span>
                  {copied
                    ? `Route pattern copied: ${routePattern}`
                    : `We will copy the route pattern for you: ${routePattern}`}
                </span>
              </p>
            )}
            {!domain.trim() && (
              <p className="text-xs text-muted-foreground mt-2">
                Enter your domain and we will prepare the route pattern for Cloudflare.
                Or deploy directly and configure later.
              </p>
            )}
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild variant="outline" size="lg">
              <Link href="https://github.com/encypherai/edge-provenance-worker">
                View on GitHub <GitBranch className="ml-2 h-4 w-4" />
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
              Works With Your CMS
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              The Worker detects and protects article content automatically across every
              major publishing platform. No per-CMS configuration needed.
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
              Full content provenance is free for every publisher. Enterprise adds leak
              detection, C2PA compliance, granular licensing, and unlimited volume.
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

      {/* Why Publishers Trust It */}
      <section className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Built for Publisher Sites
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Designed for reliability at CDN scale. No performance impact on your site,
              no risk to availability.
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
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Protect Every Article at the Edge
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            Deploy in minutes. Know where your content goes when it is copied, scraped,
            or ingested by AI. Free for all publishers. Enterprise features when you need them.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold">
              <Link href="https://deploy.workers.cloudflare.com/?url=https://github.com/encypherai/edge-provenance-worker">
                Deploy to Cloudflare <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              onClick={() => setShowContactModal(true)}
              size="lg"
              variant="outline"
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
