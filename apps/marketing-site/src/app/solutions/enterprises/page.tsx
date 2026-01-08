'use client';

import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, Shield, TrendingUp, FileCheck, AlertTriangle, CheckCircle2, Building2 } from 'lucide-react';
import Link from 'next/link';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import AISummary from '@/components/seo/AISummary';
import SalesContactModal from '@/components/forms/SalesContactModal';

export default function EnterprisePage() {
  const [showContactModal, setShowContactModal] = useState(false);
  return (
    <div className="bg-background text-foreground">
      <AISummary
        title="Encypher for Enterprise"
        whatWeDo="Authors of C2PA Section A.7. Patent-pending API and SDKs with 83 claims covering granular content attribution and evidence generation. Standard published January 8, 2026."
        whoItsFor="Fortune 500 companies deploying AI at scale needing EU AI Act and China watermarking compliance plus competitive intelligence."
        keyDifferentiator="Compliance baseline + performance intelligence upside. Patent-pending Merkle tree authentication enables court-admissible evidence generation."
        primaryValue="Turn regulatory requirement into competitive advantage. Working with industry leaders to define content licensing frameworks."
      />

      {/* Hero Section */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            Compliance is the Baseline.<br />Intelligence is the Advantage.
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            From the authors of the C2PA text standard. EU AI Act compliance through content authentication. Performance intelligence through patent-pending granular attribution. One infrastructure, dual value.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              onClick={() => setShowContactModal(true)}
              size="lg" 
              className="font-semibold"
            >
              Schedule Architecture Review <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/auth/signin?mode=signup&source=enterprises">
                Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="ghost" size="lg">
              <Link href="/demo">
                See the Platform <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* The Enterprise Challenge */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              The Enterprise AI Governance Challenge
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              AI deployment at scale requires both risk mitigation and competitive positioning.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* Risk Side */}
            <div className="bg-destructive/5 border-2 border-destructive/20 p-8 rounded-lg">
              <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
              <h3 className="text-2xl font-bold mb-4">The Downside Risk</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-destructive rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-semibold">EU AI Act Fines</p>
                    <p className="text-sm text-muted-foreground">Up to 6% of global annual revenue for non-compliance</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-destructive rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-semibold">Audit Trail Requirements</p>
                    <p className="text-sm text-muted-foreground">Must prove content origin and AI involvement</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-destructive rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-semibold">Board Exposure</p>
                    <p className="text-sm text-muted-foreground">Personal liability for AI governance failures</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-destructive rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-semibold">Brand Risk</p>
                    <p className="text-sm text-muted-foreground">AI incidents create lasting reputational damage</p>
                  </div>
                </li>
              </ul>
            </div>

            {/* Opportunity Side */}
            <div className="bg-primary/5 border-2 border-primary/20 p-8 rounded-lg">
              <TrendingUp className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-2xl font-bold mb-4">The Upside Opportunity</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-semibold">Performance Intelligence</p>
                    <p className="text-sm text-muted-foreground">See which AI outputs drive business results</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-semibold">Competitive Advantage</p>
                    <p className="text-sm text-muted-foreground">Optimize AI faster than competitors</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-semibold">Board Differentiation</p>
                    <p className="text-sm text-muted-foreground">"Governance + intelligence" beats "compliance only"</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-semibold">First-Mover Positioning</p>
                    <p className="text-sm text-muted-foreground">Early adopters shape industry standards</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          {/* The Encypher Answer */}
          <div className="mt-12 max-w-4xl mx-auto text-center bg-card p-8 rounded-lg border-2 border-primary/30">
            <h3 className="text-2xl font-bold mb-4">Encypher Provides Both</h3>
            <p className="text-lg text-muted-foreground">
              Compliance baseline through the C2PA standard we authored. Competitive intelligence through sentence-level tracking only we provide. One infrastructure solves both problems.
            </p>
          </div>
        </div>
      </section>

      {/* How Encypher Solves It */}
      <section className="py-20 w-full bg-muted/30 border-y border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              The Encypher Enterprise Solution
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Layer 1: Compliance */}
            <div className="bg-card p-6 rounded-lg border border-border">
              <div className="flex items-center gap-3 mb-4">
                <Shield className="h-8 w-8 text-primary" />
                <h3 className="text-xl font-semibold">Layer 1: Compliance</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">The baseline requirement</p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>C2PA standard implementation</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>EU AI Act audit trails</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Content authenticity verification</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Cryptographic proof generation</span>
                </li>
              </ul>
              <div className="mt-4 pt-4 border-t border-border">
                <p className="text-xs text-muted-foreground">
                  <strong>Value:</strong> Risk mitigation, regulatory compliance, board protection
                </p>
              </div>
            </div>

            {/* Layer 2: Governance */}
            <div className="bg-card p-6 rounded-lg border border-border">
              <div className="flex items-center gap-3 mb-4">
                <FileCheck className="h-8 w-8 text-primary" />
                <h3 className="text-xl font-semibold">Layer 2: Governance</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">The operational framework</p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Policy enforcement automation</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Department-level controls</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Real-time monitoring dashboards</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Automated reporting for regulators</span>
                </li>
              </ul>
              <div className="mt-4 pt-4 border-t border-border">
                <p className="text-xs text-muted-foreground">
                  <strong>Value:</strong> Operational efficiency, scalable oversight, audit readiness
                </p>
              </div>
            </div>

            {/* Layer 3: Intelligence */}
            <div className="bg-card p-6 rounded-lg border border-primary/30 border-2">
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="h-8 w-8 text-primary" />
                <h3 className="text-xl font-semibold">Layer 3: Intelligence</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">The competitive advantage</p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Sentence-level performance tracking</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>AI output optimization insights</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Viral content forensics</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Model parameter analytics</span>
                </li>
              </ul>
              <div className="mt-4 pt-4 border-t border-border">
                <p className="text-xs text-muted-foreground">
                  <strong>Value:</strong> Competitive intelligence, market advantage, ROI maximization
                </p>
              </div>
            </div>
          </div>

          <div className="mt-12 text-center">
            <p className="text-lg font-semibold mb-2">
              Your competitors will have compliance. You'll have intelligence.
            </p>
            <p className="text-muted-foreground">
              Sentence-level tracking is proprietary to Encypher. They can't replicate what we perfected over 18+ months.
            </p>
          </div>
        </div>
      </section>

      {/* Why Now */}
      <section className="py-20 w-full bg-muted/30 border-y border-border">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-8 text-center">
              Why Enterprise Leaders Choose Encypher Now
            </h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div className="flex items-start gap-4">
                <Building2 className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-2">EU AI Act Deadlines Approaching</h3>
                  <p className="text-sm text-muted-foreground">
                    Implementation timelines are 18-24 months. Starting now puts you ahead of enforcement.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <Shield className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-2">Standards Authority Matters</h3>
                  <p className="text-sm text-muted-foreground">
                    We authored the C2PA text standard. When regulators reference standards, they'll reference ours.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <TrendingUp className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-2">Competitive Intelligence Window</h3>
                  <p className="text-sm text-muted-foreground">
                    First movers gain performance data competitors lack. This advantage compounds over time.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <FileCheck className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-2">Board Expects Proactive Governance</h3>
                  <p className="text-sm text-muted-foreground">
                    "Compliance + intelligence" positions you as strategic, not reactive.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Standards Compliance */}
      <StandardsCompliance />

      {/* Final CTA */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Turn Compliance Into Competitive Advantage
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            Schedule a technical architecture review to see how Encypher provides both regulatory compliance and performance intelligence for your enterprise AI deployment.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              onClick={() => setShowContactModal(true)}
              size="lg"
            >
              Schedule Architecture Review <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/demo">
                See Platform Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Sales Contact Modal */}
      <AnimatePresence>
        {showContactModal && (
          <SalesContactModal 
            onClose={() => setShowContactModal(false)} 
            context="enterprise"
          />
        )}
      </AnimatePresence>
    </div>
  );
}