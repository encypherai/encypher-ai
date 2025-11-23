'use client';

import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, BarChart, Zap, Shield } from 'lucide-react';
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
        whatWeDo="We provide sentence-level performance intelligence for AI outputs, authored by the creators of the C2PA text standard."
        whoItsFor="AI labs needing model performance insights and compliance across the publisher ecosystem."
        keyDifferentiator="Trace viral content back to exact parameters with cryptographic proof—no probabilistic guessing."
        primaryValue="Turn R&D guesswork into data-driven optimization with court-grade provenance."
      />
      <Script id="schema-faq-ai" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />
      {/* Hero Section */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            See Which Parameters Drive Viral Content
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            Track every output to optimize your models. One integration covers the entire publisher ecosystem. Performance intelligence + compliance infrastructure.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold py-3 px-6 rounded-lg shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/ai-demo">
                Get Your Performance Intelligence Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button 
              onClick={() => setShowContactModal(true)}
              size="lg" 
              variant="outline"
              className="font-semibold py-3 px-6 rounded-lg shadow-lg"
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

      {/* Value Props Section */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 lg:gap-12 max-w-6xl mx-auto">
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border text-center">
              <BarChart className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-2xl font-semibold mb-3">Performance Intelligence</h3>
              <p className="text-muted-foreground">
                Unlock powerful model performance insights by tracing viral content and understanding what truly drives engagement.
              </p>
            </div>
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border text-center">
              <Zap className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-2xl font-semibold mb-3">Protagonist Positioning</h3>
              <p className="text-muted-foreground">
                Shift from a defensive, reactive posture to a proactive, offensive strategy by taking control of industry standards.
              </p>
            </div>
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border text-center">
              <Shield className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-2xl font-semibold mb-3">Technical Safe Harbor</h3>
              <p className="text-muted-foreground">
                Mitigate legal risks with court-admissible, cryptographic proof of content origin and usage. Comply with industry standards and regulations.
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
              From Guesswork to Certainty
            </h2>
            <p className="text-lg md:text-xl mt-4 max-w-3xl mx-auto text-muted-foreground">
              Our technology provides verifiable proof of your content's journey, transforming AI development from an art to a science.
            </p>
          </div>
          <div className="max-w-3xl mx-auto">
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="item-1">
                <AccordionTrigger>Step 1: Cryptographic Watermarking at Source</AccordionTrigger>
                <AccordionContent>
                  We embed invisible, cryptographically signed metadata directly into your content as it's generated. This 'digital birthmark' is tamper-proof and serves as unforgeable proof of origin for every output from your models.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-2">
                <AccordionTrigger>Step 2: Trace and Analyze Content Performance</AccordionTrigger>
                <AccordionContent>
                  When your content goes viral or achieves high engagement, our system traces it back to its source. We identify the exact training data, model settings, and prompts that led to that success, providing a clear map of what works.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-3">
                <AccordionTrigger>Step 3: Actionable Intelligence for Optimization</AccordionTrigger>
                <AccordionContent>
                  You receive detailed reports that enable you to systematically replicate high-performing outputs. Our infrastructure provides a technical safe harbor and unlocks powerful insights to optimize your models, training data, and overall strategy.
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
