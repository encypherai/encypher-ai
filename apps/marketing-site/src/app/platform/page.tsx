'use client';

import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@encypher/design-system';
import { Badge } from '@encypher/design-system';
import {
  ArrowRight,
  CheckCircle2,
  Shield,
  Fingerprint,
  FileSearch,
  Scale,
  Code2,
  Layers,
  Globe,
  Terminal,
  BookOpen,
  Server,
} from 'lucide-react';
import Link from 'next/link';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import AISummary from '@/components/seo/AISummary';
import SalesContactModal from '@/components/forms/SalesContactModal';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypher.com';

const CORE_CAPABILITIES = [
  {
    icon: Shield,
    title: 'Sign Every Format You Publish',
    description:
      'Articles, photos, podcasts, video, PDFs, websites, live streams. One API handles all of them. Composite signing bundles an entire article package into a single provenance unit, so the hero image, podcast clip, and written piece share one verifiable chain of custody.',
  },
  {
    icon: Fingerprint,
    title: 'Watermarks That Survive Everything',
    description:
      'Invisible text embeddings survive copy-paste, scraping, and CMS rendering. Audio and video watermarks survive transcoding, compression, and format conversion. Image watermarks survive cropping and resizing. Together they satisfy the EU AI Act proposed multilayered marking requirements.',
  },
  {
    icon: FileSearch,
    title: 'Free Verification for Anyone',
    description:
      'Any journalist, court, compliance team, or AI company can verify any signed asset at no cost through the public API. Quote integrity verification checks whether AI-generated citations match your original signed content.',
  },
  {
    icon: Scale,
    title: 'From Detection to Licensing',
    description:
      'Attribution analytics show where your content appears across the web. Formal notices establish willful infringement. Evidence packages hold up in court. The pipeline works across articles, images, audio, and video.',
  },
  {
    icon: Layers,
    title: 'Rights at Every Level',
    description:
      'Publisher rights profiles, licensing terms, and usage policies travel with content. Per-segment rights let you license one section of an article under Creative Commons while keeping another exclusive. AI companies resolve rights programmatically before ingestion.',
  },
  {
    icon: Globe,
    title: 'Coalition Licensing',
    description:
      'Auto-enrolled in the Encypher Coalition. Every format you sign is indexed for licensing deals. Publishers keep the majority of revenue on every deal.',
  },
];

const INFRASTRUCTURE_STACK = [
  { layer: 'Signing', detail: 'C2PA manifests for articles, images, audio, video, PDFs, fonts, and live streams' },
  { layer: 'Watermarking', detail: 'Audio, video, and image watermarks plus invisible text embeddings' },
  { layer: 'Verification', detail: 'Free public API, tamper detection, quote integrity, watermark extraction' },
  { layer: 'Enforcement', detail: 'Attribution analytics, formal notices, court-ready evidence packages' },
  { layer: 'Rights', detail: 'Per-segment licensing, rights resolution API, publisher profiles' },
  { layer: 'Distribution', detail: 'WordPress, Prebid ad-tech, CDN edge, REST API, CLI, browser extension' },
];

const COMPETITIVE_POSITIONING = [
  {
    us: 'Articles, photos, audio, video, websites, ads, live streams',
    them: 'Text-only or image-only tools',
  },
  {
    us: 'Watermarks survive transcoding, compression, and format conversion',
    them: 'Fragile metadata stripped by platforms',
  },
  {
    us: 'Co-authored the C2PA standard we implement',
    them: 'Third-party implementations of standards others wrote',
  },
  {
    us: 'Composite signing: one provenance unit per article package',
    them: 'Separate, unlinked signing per file',
  },
  {
    us: 'Court-ready evidence packages with cryptographic chain of custody',
    them: 'Basic detection reports',
  },
  {
    us: 'Free signing for every publisher, paid enforcement add-ons',
    them: 'Per-document fees from day one',
  },
];

const ECOSYSTEM_LAYERS = [
  {
    layer: 'Layer 1',
    title: 'Access Control',
    tools: ['robots.txt', 'TollBit', 'Cloudflare'],
    description:
      'Tell AI crawlers not to scrape. These tools work at the server level, but only when AI companies respect your directives.',
    strengthened:
      'When crawlers ignore these signals, content-level provenance provides the evidence that your terms were attached and violated.',
    highlight: false,
  },
  {
    layer: 'Layer 2',
    title: 'Content Provenance',
    tools: ['Encypher'],
    description:
      'Proof of ownership embedded in the content itself. Articles, photos, audio, video, websites. Works whether AI companies cooperate or not.',
    strengthened: '',
    highlight: true,
  },
  {
    layer: 'Layer 3',
    title: 'Attribution & Monetization',
    tools: ['ProRata', 'Dappier', 'Microsoft PCM'],
    description:
      'Estimate which sources contributed to AI outputs and route revenue to publishers. These tools work inside opted-in ecosystems.',
    strengthened:
      'Cryptographic proof of origin makes attribution claims verifiable, not just statistical estimates.',
    highlight: false,
  },
];

const STANDARDS_COMPAT = [
  'C2PA 2.3',
  'RSL 1.0',
  'SPUR Framework',
  'EU AI Act CoP',
  'W3C ODRL',
];

export default function PlatformPage() {
  const [showContactModal, setShowContactModal] = useState(false);

  return (
    <div className="bg-background text-foreground">
      <AISummary
        title="Encypher Platform"
        whatWeDo="Content provenance infrastructure for articles, photos, podcasts, video, websites, ads, and live streams. C2PA-based cryptographic manifests plus proprietary signal-domain watermarking across 31 media formats. Co-Chair of C2PA Text Provenance Task Force. Standard published January 8, 2026."
        whoItsFor="Publishers needing provable content ownership across their full portfolio. AI labs needing performance intelligence and quote integrity verification. Enterprises requiring EU AI Act compliance with multilayered marking."
        keyDifferentiator="One platform for every format: text, images, audio, video, documents, fonts, live streams. Watermarks survive transcoding, compression, copy-paste, and scraping. Free signing, free verification."
        primaryValue="Building standards with BBC, AP, Google, OpenAI, Adobe, Microsoft and others through C2PA. Proprietary watermarking meets EU AI Act proposed multilayered marking requirements. Working with industry leaders to define content licensing frameworks."
      />

      {/* Hero Section */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4 text-center">
          <Badge variant="outline" className="mb-6 text-sm px-4 py-1.5">
            <Layers className="h-3.5 w-3.5 mr-1.5" />
            Content Provenance Platform
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            One Platform for<br />Everything You Publish
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            Articles, photos, podcasts, video, websites, ads, live streams.
            Cryptographic provenance built on the C2PA standard we co-authored, with watermarking
            designed for EU AI Act compliance. Free for every publisher.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold">
              <Link href={`${DASHBOARD_URL}/auth/signin?mode=signup&source=platform`}>
                Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/publisher-demo">
                See Live Demo <ArrowRight className="ml-2 h-4 w-4" />
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

      {/* Infrastructure Stack */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Content Provenance Stack
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Six layers from signing through licensing. Built on{' '}
              <Link href="/c2pa-standard/media-types" className="text-primary underline underline-offset-2 hover:no-underline">C2PA</Link>{' '}
              with proprietary watermarking across{' '}
              <Link href="/c2pa-standard/media-types" className="text-primary underline underline-offset-2 hover:no-underline">31 media formats</Link>.
            </p>
          </div>

          <div className="max-w-3xl mx-auto space-y-0">
            {INFRASTRUCTURE_STACK.map((item, i) => (
              <div
                key={item.layer}
                className={`flex items-center gap-6 p-5 border border-border ${
                  i === 0 ? 'rounded-t-lg' : ''
                } ${i === INFRASTRUCTURE_STACK.length - 1 ? 'rounded-b-lg' : ''} ${
                  i % 2 === 0 ? 'bg-card/50' : 'bg-background'
                }`}
              >
                <span className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center text-sm font-bold">
                  {i + 1}
                </span>
                <div>
                  <span className="font-semibold">{item.layer}</span>
                  <span className="text-muted-foreground ml-2 text-sm">
                    {item.detail}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Core Capabilities Grid (6 cards) */}
      <section className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Core Capabilities
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Protect, verify, and monetize every content format you produce.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {CORE_CAPABILITIES.map((item) => {
              const IconComponent = item.icon;
              return (
                <div
                  key={item.title}
                  className="bg-card p-6 rounded-lg border border-border hover:border-primary/30 transition-colors"
                >
                  <IconComponent className="h-10 w-10 text-primary mb-4" />
                  <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-muted-foreground">
                    {item.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Standards Compliance */}
      <StandardsCompliance />

      {/* Ecosystem Section */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Strengthens Your Existing Stack
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Content provenance is not a replacement for access control or attribution tools.
              It is the layer that makes them enforceable.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-12">
            {ECOSYSTEM_LAYERS.map((layer) => (
              <div
                key={layer.title}
                className={`p-6 rounded-lg border-2 ${
                  layer.highlight
                    ? 'border-primary bg-primary/5'
                    : 'border-border bg-card'
                }`}
              >
                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                  {layer.layer}
                </div>
                <h3 className="text-lg font-semibold mb-3">{layer.title}</h3>
                <div className="flex flex-wrap gap-2 mb-4">
                  {layer.tools.map((tool) => (
                    <span
                      key={tool}
                      className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                        layer.highlight
                          ? 'bg-primary/10 text-primary'
                          : 'bg-muted text-muted-foreground'
                      }`}
                    >
                      {tool}
                    </span>
                  ))}
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  {layer.description}
                </p>
                {layer.strengthened && (
                  <p className="text-sm font-medium text-primary border-t border-border pt-3 mt-3">
                    {layer.strengthened}
                  </p>
                )}
              </div>
            ))}
          </div>

          <div className="max-w-4xl mx-auto">
            <h3 className="text-center text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-6">
              Standards and Frameworks Compatible
            </h3>
            <div className="flex flex-wrap justify-center gap-3">
              {STANDARDS_COMPAT.map((standard) => (
                <div
                  key={standard}
                  className="flex items-center gap-2 px-4 py-2 bg-muted/50 rounded-full border border-border"
                >
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  <span className="text-sm font-medium">{standard}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Developer Section */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Built for Developers
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              One API call to sign. One API call to verify. Production-grade SLAs for every scale.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {/* API Specifications */}
            <div className="bg-card p-6 rounded-lg border border-border">
              <Server className="h-8 w-8 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-2">API Specifications</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Production-grade infrastructure with documented limits and uptime guarantees.
              </p>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-start border-b border-border pb-2">
                  <span className="text-muted-foreground">Rate limit</span>
                  <span className="font-mono font-medium text-right text-xs">1K / min (Growth)<br />10K / min (Ent.)</span>
                </div>
                <div className="flex justify-between items-start border-b border-border pb-2">
                  <span className="text-muted-foreground">Batch size</span>
                  <span className="font-mono font-medium">10K docs/req</span>
                </div>
                <div className="flex justify-between items-start border-b border-border pb-2">
                  <span className="text-muted-foreground">Uptime SLA</span>
                  <span className="font-mono font-medium">99.95%</span>
                </div>
                <div className="flex justify-between items-start">
                  <span className="text-muted-foreground">Idempotency</span>
                  <span className="font-mono font-medium text-xs">Idempotency-Key</span>
                </div>
              </div>
            </div>

            {/* REST API */}
            <div className="bg-card p-6 rounded-lg border border-border">
              <Terminal className="h-8 w-8 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-2">REST API</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Full-featured REST API with Python, TypeScript, Go, and Rust SDKs. Batch endpoints for archive workflows.
              </p>
              <div className="bg-muted rounded-md p-3 font-mono text-xs space-y-1">
                <div>
                  <span className="text-muted-foreground">POST</span>{' '}
                  <span className="text-primary">/api/v1/sign</span>
                </div>
                <div>
                  <span className="text-muted-foreground">POST</span>{' '}
                  <span className="text-primary">/api/v1/sign/media</span>
                </div>
                <div>
                  <span className="text-muted-foreground">POST</span>{' '}
                  <span className="text-primary">/api/v1/sign/rich</span>
                </div>
                <div>
                  <span className="text-muted-foreground">POST</span>{' '}
                  <span className="text-primary">/api/v1/verify/image</span>
                </div>
                <div>
                  <span className="text-muted-foreground">GET</span>{' '}
                  <span className="text-primary">/api/v1/public/rights</span>
                </div>
              </div>
            </div>

            {/* Integrations */}
            <div className="bg-card p-6 rounded-lg border border-border">
              <Code2 className="h-8 w-8 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-2">Integrations</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Drop-in plugins for existing workflows. Kafka event streaming for high-throughput pipelines.
              </p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  WordPress plugin
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  Prebid RTD module (ad-tech)
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  CDN edge integrations
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  GitHub Action + CLI
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  OpenAPI 3.1 spec included
                </li>
              </ul>
            </div>

            {/* Documentation */}
            <div className="bg-card p-6 rounded-lg border border-border">
              <BookOpen className="h-8 w-8 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-2">Documentation</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Comprehensive guides, API reference, and interactive playground for testing before you commit.
              </p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  Quick-start guide
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  Full API reference
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  Interactive playground
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  Publisher integration guide
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  Archive signing cookbook
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Competitive Positioning */}
      <section className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Why Encypher
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              The only platform covering articles, photos, audio, video, and websites under one provenance infrastructure.
            </p>
          </div>

          <div className="max-w-4xl mx-auto overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-border">
                  <th className="text-left py-4 px-4 font-semibold">Capability</th>
                  <th className="text-center py-4 px-4 font-semibold w-40 bg-primary/5 rounded-t-lg">
                    Encypher
                  </th>
                  <th className="text-center py-4 px-4 font-semibold w-40">
                    Alternatives
                  </th>
                </tr>
              </thead>
              <tbody>
                {COMPETITIVE_POSITIONING.map((row, i) => (
                  <tr key={i} className={i % 2 === 0 ? 'bg-card/50' : ''}>
                    <td className="py-3 px-4 text-sm bg-primary/5 font-medium">
                      {row.us}
                    </td>
                    <td className="py-3 px-4 text-center bg-primary/5">
                      <CheckCircle2 className="h-5 w-5 text-primary mx-auto" />
                    </td>
                    <td className="py-3 px-4 text-center text-sm text-muted-foreground">
                      {row.them}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Start Protecting Your Content Today
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            Sign articles, photos, podcasts, and video at no cost. Add enforcement tools when you are
            ready to license. Enterprise plans for unlimited volume and dedicated support.
            Read our guide to <Link href="/content-provenance/verification" className="text-primary underline underline-offset-2 hover:no-underline">content provenance verification</Link>.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold">
              <Link href={`${DASHBOARD_URL}/auth/signin?mode=signup&source=platform`}>
                Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/pricing">
                View Pricing <ArrowRight className="ml-2 h-4 w-4" />
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
