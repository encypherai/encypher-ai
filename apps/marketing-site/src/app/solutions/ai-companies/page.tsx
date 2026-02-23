'use client';

import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, BarChart, Zap, Shield, Award } from 'lucide-react';
import Link from 'next/link';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import AISummary from '@/components/seo/AISummary';
import SalesContactModal from '@/components/forms/SalesContactModal';
import Script from 'next/script';
import { faqSchema } from '@/lib/seo';

// using real iframe embed (/ai-demo/embed)

export default function AiCompaniesPage() {
  const [showContactModal, setShowContactModal] = useState(false);
  return (
    <div className="bg-background text-foreground">
      <AISummary
        title="Encypher for AI Labs"
        whatWeDo="Co-Chair of C2PA Text Provenance Task Force (c2pa.org). API and SDKs for performance intelligence and quote integrity verification. Building standards with NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others. Standard publishes January 8, 2026."
        whoItsFor="AI labs needing publisher ecosystem compatibility, performance intelligence, quote integrity verification, and EU AI Act/China watermarking compliance."
        keyDifferentiator="One API integration for entire publisher ecosystem. Quote integrity proves 'According to AP...' is accurate vs. hallucinated."
        primaryValue="Collaborative infrastructure for the AI ecosystem. Sentence-level attribution traces viral content to exact parameters."
      />
      <Script id="schema-faq-ai" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />
      {/* Hero Section */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            License Content at Scale. Prove You Did It Right.
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            AI companies that license publisher content through Encypher get three things in one: access to a growing coalition of publishers, proof of compliance for regulators, and a trust signal for users. Built collaboratively through C2PA -- OpenAI, Google, Adobe, and Microsoft are members.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold py-3 px-6 rounded-lg shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/ai-demo">
                Get Your Performance Intelligence Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="font-semibold py-3 px-6 rounded-lg shadow-lg">
              <Link href="/auth/signin?mode=signup&source=ai-companies">
                Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
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

      {/* Interactive Demo Section */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-8">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              See It In Action
            </h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto mb-4">
              Experience how performance intelligence transforms R&D guesswork into data-driven optimization. This is a live, interactive demo—try it yourself.
            </p>
            <p className="text-sm text-muted-foreground flex items-center justify-center gap-2">
              <span className="animate-bounce">↓</span>
              Scroll down to explore the demo
              <span className="animate-bounce">↓</span>
            </p>
          </div>
          <div className="max-w-6xl mx-auto border-2 border-border rounded-xl shadow-2xl bg-card demo-iframe-container" style={{ maxHeight: '80vh', overflow: 'hidden', position: 'relative' }}>
            <iframe
              title="AI Demo"
              src="/ai-demo/embed"
              loading="lazy"
              referrerPolicy="no-referrer"
              className="w-full"
              style={{ height: '80vh', border: '0', display: 'block' }}
              sandbox="allow-scripts allow-same-origin allow-pointer-lock allow-popups"
            />
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-16 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-4">
              Custom Enterprise Licensing
            </h2>
            <p className="text-lg text-muted-foreground mb-6">
              Annual licensing tailored to your scale. One integration covers the entire publisher ecosystem.
            </p>
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border mb-6">
              <ul className="space-y-3 text-left max-w-md mx-auto">
                <li className="flex items-center gap-3">
                  <BarChart className="h-5 w-5 text-primary flex-shrink-0" />
                  <span>Real-world performance analytics on all outputs</span>
                </li>
                <li className="flex items-center gap-3">
                  <Shield className="h-5 w-5 text-primary flex-shrink-0" />
                  <span>EU AI Act + China mandate compliant</span>
                </li>
                <li className="flex items-center gap-3">
                  <Zap className="h-5 w-5 text-primary flex-shrink-0" />
                  <span>Publisher coalition licensing access</span>
                </li>
              </ul>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                onClick={() => setShowContactModal(true)}
                size="lg" 
                className="font-semibold py-3 px-6 rounded-lg shadow-lg btn-blue-hover" 
                style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}
              >
                Schedule Technical Evaluation <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              <Button asChild size="lg" variant="outline" className="font-semibold py-3 px-6 rounded-lg">
                <Link href="/pricing">
                  View Full Pricing <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Value Props Section */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 max-w-6xl mx-auto">
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border text-center">
              <BarChart className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-3">Performance Intelligence</h3>
              <p className="text-muted-foreground text-sm">
                Track which outputs go viral, which training data drives engagement, and how your models perform in the real world.
              </p>
            </div>
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border text-center">
              <Zap className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-3">Regulatory Compliance</h3>
              <p className="text-muted-foreground text-sm">
                One integration covers EU AI Act, China watermarking mandate, and C2PA. Stay compliant across all jurisdictions as regulations evolve.
              </p>
            </div>
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border text-center">
              <Shield className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-3">Publisher Coalition Access</h3>
              <p className="text-muted-foreground text-sm">
                One integration to license from a growing coalition of publishers. No bilateral negotiations at scale -- access the entire network through Encypher.
              </p>
            </div>
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border text-center">
              <Award className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-3">Licensed Content Mark</h3>
              <p className="text-muted-foreground text-sm">
                AI companies that license through Encypher can signal responsible content use to their own users and customers -- a competitive differentiator for early adopters.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 w-full bg-muted/30 border-t border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              One Integration. Three Outcomes.
            </h2>
            <p className="text-lg md:text-xl mt-4 max-w-3xl mx-auto text-muted-foreground">
              License content legitimately, satisfy regulators, and show your users you take provenance seriously. Here is how the technical infrastructure delivers all three.
            </p>
          </div>
          <div className="max-w-3xl mx-auto">
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="item-1">
                <AccordionTrigger>Step 1: Connect to the Publisher Coalition</AccordionTrigger>
                <AccordionContent>
                  A single API integration connects you to Encypher&apos;s growing publisher coalition. Licensing terms are established at the network level -- no bilateral negotiations required for each publisher. As the coalition grows, your access grows with it.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-2">
                <AccordionTrigger>Step 2: Verify Provenance at Inference</AccordionTrigger>
                <AccordionContent>
                  When your model cites or uses publisher content, Encypher verifies the cryptographic watermark and records the provenance check. This creates an auditable log of licensed content use -- the documentation regulators and licensing agreements require.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-3">
                <AccordionTrigger>Step 3: Compliance + Performance Intelligence</AccordionTrigger>
                <AccordionContent>
                  From the same integration: EU AI Act and China watermarking mandate compliance, real-world performance analytics on your outputs, and the Licensed Content mark to signal responsible use to your own users. One integration, three compounding benefits.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </div>
      </section>
      <StandardsCompliance />

      {/* Sales Contact Modal */}
      <AnimatePresence>
        {showContactModal && (
          <SalesContactModal 
            onClose={() => setShowContactModal(false)} 
            context="ai"
          />
        )}
      </AnimatePresence>
    </div>
  );
}
