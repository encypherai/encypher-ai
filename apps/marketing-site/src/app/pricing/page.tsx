'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
// Tabs import removed - using custom styled buttons for better active state visibility
import { AnimatePresence } from 'framer-motion';
import { ArrowRight, Check, Newspaper, BarChart3, Shield, Award } from 'lucide-react';
import Link from 'next/link';
import SalesContactModal from '@/components/forms/SalesContactModal';
import AISummary from '@/components/seo/AISummary';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import Image from 'next/image';
import {
  FREE_TIER,
  ENTERPRISE_TIER,
} from '@/lib/pricing-config';
import {
  COALITION_VALUE_PROP,
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
                <Badge className="mb-3 bg-primary">Free Tier</Badge>
                <h2 className="text-3xl font-bold mb-2">Full Signing Infrastructure — $0</h2>
                <p className="text-muted-foreground max-w-2xl mx-auto">
                  {COALITION_VALUE_PROP.subheadline}
                </p>
              </div>

              {/* Business-value bullets — what it does for you, not what it is */}
              <ul className="grid sm:grid-cols-2 gap-x-8 gap-y-3 max-w-2xl mx-auto mb-6">
                {[
                  'Prove ownership of every piece of content you publish',
                  'Detect when your content is copied, scraped, or modified',
                  'Invisible signatures that survive copy-paste and redistribution',
                  'Anyone can verify your content is authentic — no login required',
                  'Join a coalition that licenses your content to AI companies — bringing you revenue',
                  'WordPress integration — protect content the moment you hit publish',
                ].map((f) => (
                  <li key={f} className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{f}</span>
                  </li>
                ))}
              </ul>

              {/* Collapsible full feature list for those who want details */}
              <details className="group mb-6">
                <summary className="flex items-center justify-center gap-2 cursor-pointer text-sm font-medium text-muted-foreground hover:text-foreground transition-colors select-none">
                  <span>See all free features</span>
                  <ArrowRight className="h-3.5 w-3.5 transition-transform group-open:rotate-90" />
                </summary>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mt-6 pt-6 border-t border-border">
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
                    <h4 className="font-bold text-sm uppercase text-muted-foreground mb-3">AI Crawler Analytics</h4>
                    <ul className="space-y-2">
                      {FREE_TIER.analyticsFeatures.map((f: string) => (
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
              </details>

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

          {/* ===== ATTRIBUTION ANALYTICS ADD-ON CALLOUT ===== */}
          <div className="max-w-4xl mx-auto mb-16">
            <div className="bg-blue-ncs/5 border border-blue-ncs/20 rounded-xl p-6">
              <div className="flex items-start gap-4">
                <div className="p-2 bg-blue-ncs/10 rounded-lg flex-shrink-0">
                  <BarChart3 className="h-5 w-5 text-blue-ncs" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold">Attribution Analytics</h3>
                    <span className="text-xs bg-blue-ncs/10 text-blue-ncs border border-blue-ncs/20 rounded-full px-2 py-0.5 font-medium">Coming Soon</span>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">
                    See exactly where your signed content is spreading across the internet --
                    which domains are hosting it, which AI companies are using it, and how frequently.
                    Included free for all coalition members when it launches.
                  </p>
                  <div className="grid sm:grid-cols-2 gap-x-6 gap-y-1.5">
                    {[
                      'External domain detections -- where your content appears outside your site',
                      'AI company usage patterns -- training, RAG, direct reproduction',
                      'Content spread timeline -- track velocity over time',
                      'Export targeting lists for formal notice campaigns',
                    ].map((f) => (
                      <div key={f} className="flex items-start gap-2">
                        <Check className="h-3.5 w-3.5 text-blue-ncs mt-0.5 flex-shrink-0" />
                        <span className="text-xs text-muted-foreground">{f}</span>
                      </div>
                    ))}
                  </div>
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

              {/* Business-value bullets — why enterprise matters to a decision-maker */}
              <ul className="grid sm:grid-cols-2 gap-x-8 gap-y-3 max-w-2xl mx-auto mb-6">
                {[
                  'Unlimited signing — no caps on content volume or API calls',
                  'Real-time AI output monitoring — see exactly where your content appears',
                  'Enforcement tools — formal notices and court-ready evidence packages',
                  'Sign as your brand — custom identity and white-label verification',
                  'Streaming LLM signing — protect AI-generated content in real time',
                  'Dedicated SLA, SSO, and a named account manager',
                ].map((f) => (
                  <li key={f} className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{f}</span>
                  </li>
                ))}
              </ul>

              {/* Collapsible full feature list for those who want details */}
              <details className="group mb-8">
                <summary className="flex items-center justify-center gap-2 cursor-pointer text-sm font-medium text-muted-foreground hover:text-foreground transition-colors select-none">
                  <span>See all enterprise features</span>
                  <ArrowRight className="h-3.5 w-3.5 transition-transform group-open:rotate-90" />
                </summary>
                <div className="grid md:grid-cols-2 gap-6 mt-6 pt-6 border-t border-border">
                  <div>
                    <h4 className="font-bold text-sm uppercase text-muted-foreground mb-3">Everything Unlimited</h4>
                    <ul className="space-y-2">
                      {ENTERPRISE_TIER.features.map((feature: string) => (
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
                      {ENTERPRISE_TIER.exclusiveCapabilities.map((cap: string) => (
                        <li key={cap} className="flex items-start gap-2">
                          <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                          <span className="text-sm">{cap}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </details>

              <div className="bg-primary/5 rounded-lg p-4 mb-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Any resulting licensing revenue is shared between the coalition and the publisher, with the majority going to the content creator. We only win when you win.
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
