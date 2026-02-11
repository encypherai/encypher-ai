'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
// Tabs import removed - using custom styled buttons for better active state visibility
import { AnimatePresence } from 'framer-motion';
import { ArrowRight, Check, Newspaper, BarChart3, Shield, FileText, Award } from 'lucide-react';
import Link from 'next/link';
import SalesContactModal from '@/components/forms/SalesContactModal';
import AISummary from '@/components/seo/AISummary';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import Image from 'next/image';
import {
  FREE_TIER,
  ADD_ONS,
  BUNDLES,
  ENTERPRISE_TIER,
  formatAddOnPrice,
  formatBundlePrice,
  type AddOnConfig,
} from '@/lib/pricing-config';
import {
  COALITION_VALUE_PROP,
  LICENSING_TRACKS,
} from '@/lib/pricing-config/coalition';

// Dashboard URL for sign-up flows
const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypherai.com';

type ICP = 'publishers' | 'ai-labs' | 'enterprises';

// ICP-specific value propositions aligned with demos
const ICP_VALUE_PROPS: Record<ICP, { headline: string; subheadline: string; icon: typeof Newspaper }> = {
  publishers: {
    headline: 'Free to Sign. Paid to Enforce.',
    subheadline: 'Full signing infrastructure at no cost. Pay only for enforcement tools when you\'re ready to license.',
    icon: Newspaper,
  },
  'ai-labs': {
    headline: '"Google Analytics" for AI',
    subheadline: 'Performance intelligence + regulatory compliance. Building standards WITH you through C2PA. Meta, Google, and OpenAI are already members.',
    icon: BarChart3,
  },
  enterprises: {
    headline: 'AI Governance Infrastructure',
    subheadline: 'EU AI Act & China watermarking compliance with C2PA.',
    icon: Shield,
  },
};


export default function PricingPage() {
  const [activeICP, setActiveICP] = useState<ICP>('publishers');
  const [showPublisherModal, setShowPublisherModal] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [showEnterpriseModal, setShowEnterpriseModal] = useState(false);
  // Categorize add-ons for display
  const enforcementAddOns = ADD_ONS.filter(a => a.category === 'enforcement');
  const infrastructureAddOns = ADD_ONS.filter(a => a.category === 'infrastructure');
  const operationsAddOns = ADD_ONS.filter(a => a.category === 'operations');

  return (
    <div className="bg-background text-foreground">
      {/* SEO: AI Summary with all ICP information for crawlers */}
      <AISummary
        title="Encypher Pricing & Licensing"
        whatWeDo="Encypher serves as Co-Chair of C2PA Text Provenance Task Force (c2pa.org). API and SDKs in Python, TypeScript, Go, and Rust for content authentication. Standard published January 8, 2026. Technology reviewed by C2PA members including Google, OpenAI, Adobe, and Microsoft."
        whoItsFor="Publishers seeking content licensing infrastructure and provable ownership. AI labs needing performance intelligence and quote integrity verification. Enterprises requiring EU AI Act and China watermarking compliance."
        keyDifferentiator="Cryptographic watermarking survives copy-paste and distribution. Provides technical infrastructure for content attribution and licensing. One API integration for entire publisher ecosystem."
        primaryValue="Start free, scale as you grow. Enterprise partners help shape industry-standard licensing frameworks for AI content usage."
      />

      {/* Hero Section with ICP Selector */}
      <section className="relative w-full py-12 md:py-16 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          {/* ICP Tab Selector - Vertical on mobile, horizontal on desktop */}
          <div className="flex justify-center mb-6 px-4">
            {/* Mobile: Vertical stack */}
            <div className="flex flex-col sm:hidden gap-2 w-full max-w-xs">
              {(['publishers', 'ai-labs', 'enterprises'] as const).map((icp) => {
                const isActive = activeICP === icp;
                const config = {
                  publishers: { icon: Newspaper, label: 'Publishers' },
                  'ai-labs': { icon: BarChart3, label: 'AI Labs' },
                  enterprises: { icon: Shield, label: 'Enterprises' },
                }[icp];
                const IconComponent = config.icon;
                return (
                  <button
                    key={icp}
                    onClick={() => setActiveICP(icp)}
                    className={`flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium transition-all text-sm ${
                      isActive
                        ? 'bg-blue-ncs text-white shadow-md'
                        : 'bg-secondary text-muted-foreground'
                    }`}
                  >
                    <IconComponent className="h-4 w-4" />
                    <span>{config.label}</span>
                  </button>
                );
              })}
            </div>
            {/* Desktop: Horizontal tabs */}
            <div className="hidden sm:inline-flex rounded-lg p-1.5 gap-1 bg-secondary">
              {(['publishers', 'ai-labs', 'enterprises'] as const).map((icp) => {
                const isActive = activeICP === icp;
                const config = {
                  publishers: { icon: Newspaper, label: 'Publishers' },
                  'ai-labs': { icon: BarChart3, label: 'AI Labs' },
                  enterprises: { icon: Shield, label: 'Enterprises' },
                }[icp];
                const IconComponent = config.icon;
                return (
                  <button
                    key={icp}
                    onClick={() => setActiveICP(icp)}
                    className={`flex items-center justify-center gap-2 py-3 px-6 rounded-md font-medium transition-all text-sm ${
                      isActive
                        ? 'bg-blue-ncs text-white shadow-md'
                        : 'text-muted-foreground'
                    }`}
                  >
                    <IconComponent className="h-4 w-4" />
                    <span>{config.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Dynamic Value Prop based on active ICP */}
          <div className="text-center">
            {(() => {
              const props = ICP_VALUE_PROPS[activeICP];
              const IconComponent = props.icon;
              return (
                <>
                  <div className="flex justify-center mb-4">
                    <div className="p-3 bg-primary/10 rounded-full">
                      <IconComponent className="h-8 w-8 text-primary" />
                    </div>
                  </div>
                  <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight mb-4">
                    {props.headline}
                  </h1>
                  <p className="text-lg md:text-xl max-w-2xl mx-auto text-muted-foreground">
                    {props.subheadline}
                  </p>
                </>
              );
            })()}
          </div>

          {/* C2PA Co-Chair Authority Badge - Single source of standards authority */}
          <div className="flex justify-center mt-8 px-4">
            <div className="inline-flex items-center gap-2 px-3 md:px-4 py-2 bg-primary/10 border border-primary/20 rounded-full">
              <Award className="h-4 w-4 text-primary flex-shrink-0" />
              <span className="text-xs md:text-sm font-medium text-center">
                <span className="hidden md:inline">C2PA Text Provenance Co-Chair — Building standards with Google, BBC, OpenAI, Adobe & Microsoft</span>
                <span className="md:hidden">C2PA Co-Chair with Google, BBC, OpenAI, Adobe</span>
              </span>
            </div>
          </div>

          {/* C2PA & CAI Logos - Standards Authority */}
          <div className="mt-4 flex justify-center items-center gap-6 md:gap-10">
            <div className="relative h-8 w-24 md:h-10 md:w-32">
              <Image
                src="/c2pa-hero.svg"
                alt="C2PA Logo"
                fill
                style={{objectFit: 'contain'}}
                className="dark:invert"
              />
            </div>
            <div className="relative h-8 w-24 md:h-10 md:w-32">
              <Image
                src="/CAI_Lockup_RGB_Black.svg"
                alt="Content Authenticity Initiative Logo"
                fill
                style={{objectFit: 'contain'}}
                className="dark:invert"
              />
            </div>
          </div>

        </div>
      </section>

      {/* 
        SEO NOTE: All three sections are rendered in the DOM but only one is visible.
        This ensures crawlers index all content while users see a clean tabbed interface.
        Using CSS visibility/display instead of conditional rendering.
      */}

      {/* ==================== PUBLISHERS SECTION ==================== */}
      <section 
        id="publishers" 
        className={`py-12 w-full ${activeICP === 'publishers' ? 'block' : 'hidden'}`}
        aria-hidden={activeICP !== 'publishers'}
      >
        <div className="container mx-auto px-4">

          {/* ===== FREE TIER HERO CARD ===== */}
          <div className="max-w-4xl mx-auto mb-16">
            <div className="bg-card border-2 border-primary/30 rounded-xl p-8 shadow-lg">
              <div className="text-center mb-6">
                <Badge className="mb-3 bg-primary">Free Forever</Badge>
                <h2 className="text-3xl font-bold mb-2">Full Signing Infrastructure — $0</h2>
                <p className="text-muted-foreground max-w-2xl mx-auto">
                  {COALITION_VALUE_PROP.subheadline}
                </p>
              </div>

              <div className="grid md:grid-cols-3 gap-6 mb-8">
                <div>
                  <h4 className="font-bold text-sm uppercase text-muted-foreground mb-3">Signing & Provenance</h4>
                  <ul className="space-y-2">
                    {FREE_TIER.signingFeatures.map((f: string) => (
                      <li key={f} className="flex items-start gap-2">
                        <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold text-sm uppercase text-muted-foreground mb-3">Distribution & Tools</h4>
                  <ul className="space-y-2">
                    {FREE_TIER.distributionFeatures.map((f: string) => (
                      <li key={f} className="flex items-start gap-2">
                        <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold text-sm uppercase text-muted-foreground mb-3">Coalition Membership</h4>
                  <ul className="space-y-2">
                    {FREE_TIER.coalitionFeatures.map((f: string) => (
                      <li key={f} className="flex items-start gap-2">
                        <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="bg-muted/50 rounded-lg p-4 mb-6 text-center">
                <p className="text-sm">
                  <strong>{FREE_TIER.limits.documentsPerMonth.toLocaleString()} documents/month</strong> included.
                  Overage: ${FREE_TIER.limits.overagePerDoc}/doc. Unlimited verification & API lookups.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button asChild size="lg" className="font-semibold shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                  <Link href={`/auth/signin?mode=signup&source=pricing-free`}>
                    Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link href="/publisher-demo">
                    See Publisher Demo <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </div>
          </div>

          {/* ===== TWO-TRACK LICENSING MODEL ===== */}
          <div className="max-w-5xl mx-auto mb-16">
            <h3 className="text-2xl font-bold text-center mb-2">Two-Track Licensing Revenue</h3>
            <p className="text-center text-muted-foreground mb-8 max-w-2xl mx-auto">
              Same splits whether you&apos;re on Free or Enterprise. We only win when you win.
            </p>
            <div className="grid md:grid-cols-2 gap-6">
              {Object.entries(LICENSING_TRACKS).map(([key, track]) => (
                <div key={key} className="bg-card border border-border rounded-lg p-6">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="text-2xl font-bold text-primary">{track.split}</div>
                    <div>
                      <h4 className="font-bold">{track.name}</h4>
                      <p className="text-xs text-muted-foreground">Publisher / Encypher</p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">{track.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* ===== ENFORCEMENT ADD-ONS ===== */}
          <div className="max-w-6xl mx-auto mb-16">
            <h3 className="text-2xl font-bold text-center mb-2">Enforcement Tools</h3>
            <p className="text-center text-muted-foreground mb-8">
              Self-service. No sales call required. Add when you&apos;re ready to license.
            </p>

            {/* Enforcement Pipeline Visualization */}
            <div className="flex flex-wrap justify-center items-center gap-2 mb-8 text-sm">
              {['Sign', 'Detect', 'Notify', 'Prove', 'License'].map((step, i) => (
                <div key={step} className="flex items-center gap-2">
                  <span className={`px-3 py-1.5 rounded-full font-medium ${i === 0 ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'}`}>
                    {step}
                  </span>
                  {i < 4 && <ArrowRight className="h-4 w-4 text-muted-foreground" />}
                </div>
              ))}
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-8">
              {enforcementAddOns.map((addOn: AddOnConfig) => (
                <div key={addOn.id} className={`bg-card border border-border rounded-lg p-6 ${addOn.comingSoon ? 'opacity-80' : ''}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-bold text-lg">{addOn.name}</h4>
                    {addOn.comingSoon && <Badge variant="outline" className="text-xs">Coming Soon</Badge>}
                  </div>
                  {!addOn.comingSoon && (
                    <div className="text-2xl font-bold text-primary mb-2">{formatAddOnPrice(addOn)}</div>
                  )}
                  <p className="text-sm text-muted-foreground mb-4">{addOn.description}</p>
                  {addOn.includes && (
                    <ul className="space-y-1.5 mb-4">
                      {addOn.includes.slice(0, 4).map((item: string) => (
                        <li key={item} className="flex items-start gap-2">
                          <Check className="h-3.5 w-3.5 text-primary mt-0.5 flex-shrink-0" />
                          <span className="text-xs">{item}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                  {addOn.replaces && (
                    <p className="text-xs text-muted-foreground italic border-t border-border pt-2">
                      Replaces: {addOn.replaces}
                    </p>
                  )}
                  {!addOn.comingSoon && addOn.volumePricing && addOn.volumePricing.length > 1 && (
                    <div className="mt-3 pt-3 border-t border-border">
                      <p className="text-xs font-medium mb-1">Volume pricing:</p>
                      {addOn.volumePricing.slice(1).map((vp) => (
                        <p key={String(vp.quantity)} className="text-xs text-muted-foreground">
                          {vp.quantity}: ${vp.priceEach}{addOn.unitLabel} {vp.savings && <span className="text-primary font-medium">({vp.savings})</span>}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* ===== BUNDLES ===== */}
          <div className="max-w-5xl mx-auto mb-16">
            <h3 className="text-2xl font-bold text-center mb-2">Bundles — Save Up to 57%</h3>
            <p className="text-center text-muted-foreground mb-8">
              Pre-packaged combinations for common workflows.
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              {BUNDLES.map((bundle) => (
                <div key={bundle.id} className={`bg-card rounded-lg p-6 ${bundle.comingSoon ? 'opacity-80 border border-border' : bundle.id === 'enforcement-bundle' ? 'border-2 border-primary/50 shadow-lg relative' : 'border border-border'}`}>
                  {!bundle.comingSoon && bundle.id === 'enforcement-bundle' && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <Badge className="bg-primary">Most Popular</Badge>
                    </div>
                  )}
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-bold text-lg">{bundle.name}</h4>
                    {bundle.comingSoon && <Badge variant="outline" className="text-xs">Coming Soon</Badge>}
                  </div>
                  {!bundle.comingSoon ? (
                    <div className="flex items-baseline gap-2 mb-2">
                      <span className="text-2xl font-bold text-primary">{formatBundlePrice(bundle)}</span>
                      <Badge variant="outline" className="text-xs">Save {bundle.savings}</Badge>
                    </div>
                  ) : (
                    <div className="mb-2" />
                  )}
                  <p className="text-sm text-muted-foreground mb-4">{bundle.description}</p>
                  <ul className="space-y-2">
                    {bundle.includes.map((item: string) => (
                      <li key={item} className="flex items-start gap-2">
                        <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>

          {/* ===== INFRASTRUCTURE & OPERATIONS ADD-ONS ===== */}
          <div className="max-w-5xl mx-auto mb-16">
            <h3 className="text-2xl font-bold text-center mb-8">Infrastructure & Operations</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-bold text-sm uppercase text-muted-foreground mb-4">Infrastructure</h4>
                <div className="space-y-3">
                  {infrastructureAddOns.map((addOn: AddOnConfig) => (
                    <div key={addOn.id} className={`bg-card border border-border rounded-lg p-4 flex justify-between items-start ${addOn.comingSoon ? 'opacity-80' : ''}`}>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h5 className="font-medium text-sm">{addOn.name}</h5>
                          {addOn.comingSoon && <Badge variant="outline" className="text-[10px] px-1.5 py-0">Coming Soon</Badge>}
                        </div>
                        <p className="text-xs text-muted-foreground">{addOn.description}</p>
                      </div>
                      {!addOn.comingSoon && (
                        <span className="text-sm font-bold text-primary ml-4 whitespace-nowrap">{formatAddOnPrice(addOn)}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-bold text-sm uppercase text-muted-foreground mb-4">Operations</h4>
                <div className="space-y-3">
                  {operationsAddOns.map((addOn: AddOnConfig) => (
                    <div key={addOn.id} className={`bg-card border border-border rounded-lg p-4 flex justify-between items-start ${addOn.comingSoon ? 'opacity-80' : ''}`}>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h5 className="font-medium text-sm">{addOn.name}</h5>
                          {addOn.comingSoon && <Badge variant="outline" className="text-[10px] px-1.5 py-0">Coming Soon</Badge>}
                        </div>
                        <p className="text-xs text-muted-foreground">{addOn.description}</p>
                      </div>
                      {!addOn.comingSoon && (
                        <span className="text-sm font-bold text-primary ml-4 whitespace-nowrap">{formatAddOnPrice(addOn)}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* ===== ENTERPRISE TIER ===== */}
          <div className="max-w-4xl mx-auto mb-16">
            <div className="bg-muted/30 border-2 border-border rounded-xl p-8">
              <div className="text-center mb-6">
                <Badge variant="outline" className="mb-3">Enterprise</Badge>
                <h3 className="text-2xl font-bold mb-2">Enterprise — Unlimited Everything</h3>
                <p className="text-muted-foreground">
                  All add-ons included. Exclusive capabilities. Dedicated support. Custom pricing tailored to your organization.
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-6 mb-8">
                <div>
                  <h4 className="font-bold text-sm uppercase text-muted-foreground mb-3">Everything Unlimited</h4>
                  <ul className="space-y-2">
                    {ENTERPRISE_TIER.features.slice(0, 7).map((feature: string) => (
                      <li key={feature} className="flex items-start gap-2">
                        <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold text-sm uppercase text-muted-foreground mb-3">Exclusive Capabilities</h4>
                  <ul className="space-y-2">
                    {ENTERPRISE_TIER.exclusiveCapabilities.slice(0, 7).map((cap: string) => (
                      <li key={cap} className="flex items-start gap-2">
                        <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{cap}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="bg-primary/5 rounded-lg p-4 mb-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Same <strong>60/40</strong> coalition and <strong>80/20</strong> self-service licensing splits. We only win when you win.
                </p>
              </div>

              <div className="text-center">
                <Button onClick={() => setShowPublisherModal(true)} size="lg">
                  Contact for Pricing <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* ===== CONTENT PROVENANCE EXPLAINER ===== */}
          <div className="max-w-3xl mx-auto p-6 bg-muted/30 rounded-lg">
            <h4 className="font-bold text-lg mb-3">New to content provenance?</h4>
            <p className="text-sm text-muted-foreground mb-4">
              <strong>Content provenance</strong> is cryptographic proof that you created your content. 
              When AI companies scrape the web for training data, they currently can&apos;t tell who owns what. 
              Our technology embeds invisible, tamper-proof signatures directly into your text that:
            </p>
            <ul className="text-sm text-muted-foreground space-y-2 mb-4">
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span><strong>Survive copy-paste</strong> — Your proof travels with your content</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span><strong>Enable licensing</strong> — AI companies can identify and pay you</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span><strong>Are invisible</strong> — Readers see nothing different</span>
              </li>
            </ul>
            <p className="text-sm text-muted-foreground">
              Built on <strong>C2PA</strong>, the same standard used by NYT, BBC, Adobe, and Google. 
              We co-authored the text specification.
            </p>
          </div>
        </div>
      </section>

      {/* ==================== AI LABS SECTION ==================== */}
      <section 
        id="ai-labs" 
        className={`py-12 w-full ${activeICP === 'ai-labs' ? 'block' : 'hidden'}`}
        aria-hidden={activeICP !== 'ai-labs'}
      >
        <div className="container mx-auto px-4">
          {/* The Problem - aligned with AI Demo Section 1 */}
          <div className="max-w-4xl mx-auto mb-12 text-center">
            <p className="text-lg text-muted-foreground mb-2">The Problem</p>
            <h2 className="text-2xl md:text-3xl font-bold mb-4">
              You spend <span className="text-primary">$2.7B per model</span> with zero performance analytics.
            </h2>
            <p className="text-muted-foreground">
              No visibility into which training data drives real-world performance. No way to optimize R&D spend.
            </p>
          </div>

          <div className="max-w-5xl mx-auto">
            <div className="grid md:grid-cols-2 gap-8 mb-12">
              {/* Performance Intelligence */}
              <div className="bg-card rounded-lg border border-border p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <BarChart3 className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-bold">Performance Intelligence</h3>
                </div>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">Sentence-level analytics on all outputs</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">Track which parameters drive viral performance</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">Real-world feedback loop for R&D optimization</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">Publisher ecosystem performance data</span>
                  </li>
                </ul>
              </div>

              {/* Regulatory Compliance */}
              <div className="bg-card rounded-lg border border-border p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Shield className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-bold">Regulatory Compliance</h3>
                </div>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">EU AI Act compliant infrastructure</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">China watermarking mandate ready</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">C2PA standard (Adobe, Microsoft, Google)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">Publisher coalition licensing access</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* CTA Card */}
            <div className="bg-primary/5 border-2 border-primary/20 rounded-lg p-8 text-center">
              <h3 className="text-2xl font-bold mb-2">Custom Enterprise Licensing</h3>
              <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
                Annual licensing tailored to your scale. One integration covers the entire publisher ecosystem.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button 
                  onClick={() => setShowAIModal(true)}
                  size="lg"
                >
                  Schedule Technical Evaluation <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link href="/ai-demo">
                    See Interactive Demo <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </div>
          </div>

          {/* Standards Footer */}
          <div className="max-w-3xl mx-auto mt-12">
            <p className="text-sm text-muted-foreground mb-4 text-center">Built on global standards</p>
            <div className="flex flex-wrap justify-center gap-8">
              <div className="flex items-center gap-2">
                <span className="font-bold text-primary">C2PA</span>
                <span className="text-sm text-muted-foreground">Standard</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-primary">EU AI Act</span>
                <span className="text-sm text-muted-foreground">Compliant</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-primary">China</span>
                <span className="text-sm text-muted-foreground">Watermarking Ready</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ==================== ENTERPRISES SECTION ==================== */}
      <section 
        id="enterprises" 
        className={`py-12 w-full ${activeICP === 'enterprises' ? 'block' : 'hidden'}`}
        aria-hidden={activeICP !== 'enterprises'}
      >
        <div className="container mx-auto px-4">
          {/* Regulatory Context */}
          <div className="max-w-4xl mx-auto mb-12 text-center">
            <p className="text-lg text-muted-foreground mb-2">The Regulatory Reality</p>
            <h2 className="text-2xl md:text-3xl font-bold mb-4">
              EU AI Act & China watermarking mandates are here.
            </h2>
            <p className="text-muted-foreground">
              Turn compliance requirements into competitive advantage with C2PA infrastructure.
            </p>
          </div>

          <div className="max-w-4xl mx-auto mb-12">
            <div className="bg-card border-2 border-primary/30 rounded-xl p-8">
              <div className="text-center mb-6">
                <Badge variant="outline" className="mb-3">Enterprise</Badge>
                <h3 className="text-2xl font-bold mb-2">Custom Implementation for Your Organization</h3>
                <p className="text-muted-foreground max-w-2xl mx-auto">
                  Full C2PA infrastructure tailored to your compliance requirements and scale. Custom pricing based on your needs.
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-6 mb-8">
                <div>
                  <h4 className="font-bold text-sm uppercase text-muted-foreground mb-3">Infrastructure</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>C2PA-compliant content provenance</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>Sentence-level tracking & intelligence dashboards</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>Audit trails for AI-generated content</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>On-premise deployment available</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold text-sm uppercase text-muted-foreground mb-3">Support & Services</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>Dedicated account team</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>Priority support with SLA</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>Custom feature development</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>SSO integration (SAML, OAuth)</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="text-center">
                <Button 
                  onClick={() => setShowEnterpriseModal(true)}
                  size="lg"
                >
                  Contact for Pricing <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Enterprise Value Prop */}
          <div className="max-w-4xl mx-auto bg-muted/30 rounded-lg p-8">
            <h3 className="text-2xl font-bold mb-6 text-center">EU AI Act Compliance + Competitive Advantage</h3>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h4 className="font-bold mb-3">Compliance Baseline</h4>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5" />
                    <span>C2PA-compliant content provenance</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5" />
                    <span>Audit trails for AI-generated content</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5" />
                    <span>Regulatory reporting dashboards</span>
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="font-bold mb-3">Competitive Advantage</h4>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5" />
                    <span>Performance intelligence on AI outputs</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5" />
                    <span>Content attribution and licensing</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5" />
                    <span>Publisher ecosystem compatibility</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
          <div className="max-w-3xl mx-auto mt-8 text-center text-sm text-muted-foreground">
            <p>
              Building on Encypher? Enterprise SaaS and non-publisher platforms can start with a free Starter account to test the API today.
              OEM and non-publisher licensing is handled through custom Enterprise agreements — contact our team to discuss terms.
            </p>
          </div>
        </div>
      </section>

      {/* Sales Modals */}
      <AnimatePresence>
        {showPublisherModal && (
          <SalesContactModal
            onClose={() => setShowPublisherModal(false)}
            context="publisher"
            title="Publisher Inquiry"
            subtitle="Tell us about your publication and we'll help you find the right plan."
          />
        )}
      </AnimatePresence>
      <AnimatePresence>
        {showAIModal && (
          <SalesContactModal
            onClose={() => setShowAIModal(false)}
            context="ai"
            title="AI Lab Technical Evaluation"
            subtitle="Schedule a technical evaluation to explore our infrastructure."
          />
        )}
      </AnimatePresence>
      <AnimatePresence>
        {showEnterpriseModal && (
          <SalesContactModal
            onClose={() => setShowEnterpriseModal(false)}
            context="enterprise"
            title="Enterprise Inquiry"
            subtitle="Let's discuss your compliance and infrastructure needs."
          />
        )}
      </AnimatePresence>

      {/* C2PA Member Company Logo Scroller */}
      <StandardsCompliance />
    </div>
  );
}
