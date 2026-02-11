'use client';

import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, DollarSign, Scale, TrendingUp, CheckCircle2 } from 'lucide-react';
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

// using real iframe embed (/publisher-demo/embed)
export default function PublishersPage() {
  const [showContactModal, setShowContactModal] = useState(false);
  return (
    <div className="bg-background text-foreground">
      <AISummary
        title="Encypher for Publishers"
        whatWeDo="Encypher authored C2PA Section A.7. Patent-pending API and SDKs for granular content attribution with Merkle tree authentication. Survives copy-paste, B2B distribution, and scraping. Standard published January 8, 2026."
        whoItsFor="Publishers seeking provable content ownership and licensing infrastructure. Cryptographic verification enables content attribution across the AI ecosystem."
        keyDifferentiator="Patent-pending Merkle tree authentication documents exactly which sentences were used. Tamper-evident documentation designed for legal proceedings. Quote integrity verification protects brand from AI hallucinations."
        primaryValue="Provide technical infrastructure for content licensing. Encypher serves as Co-Chair of the C2PA Text Provenance Task Force, with technology reviewed by C2PA members including Google, OpenAI, Adobe, and Microsoft."
      />
      <Script id="schema-faq-publishers" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />
      {/* Hero Section */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            Cryptographic Content Protection That Generates Revenue
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            Stop absorbing litigation costs. Start generating new licensing revenue with tamper-evident documentation of content ownership and usage.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold py-3 px-6 rounded-lg shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/publisher-demo">
                Get Your Content Protection Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="font-semibold py-3 px-6 rounded-lg shadow-lg">
              <Link href="/auth/signin?mode=signup&source=publishers">
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
              Experience how sentence-level tracking transforms litigation into licensing. This is a live, interactive demo—try it yourself.
            </p>
            <p className="text-sm text-muted-foreground flex items-center justify-center gap-2">
              <span className="animate-bounce">↓</span>
              Scroll down to explore the demo
              <span className="animate-bounce">↓</span>
            </p>
          </div>
          <div className="max-w-6xl mx-auto border-2 border-border rounded-xl shadow-2xl bg-card demo-iframe-container" style={{ maxHeight: '80vh', overflow: 'hidden', position: 'relative' }}>
            <iframe
              title="Publisher Demo"
              src="/publisher-demo/embed"
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
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-4 text-center">
              Free to Sign. Paid to Enforce.
            </h2>
            <p className="text-lg text-muted-foreground mb-8 text-center">
              Full signing infrastructure at $0. Add enforcement tools when you&apos;re ready to license. Same revenue splits for everyone.
            </p>
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              {/* Free */}
              <div className="bg-card p-6 rounded-lg shadow-md border-2 border-primary relative">
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground text-xs px-3 py-1 rounded-full">Start Here</div>
                <h3 className="text-xl font-semibold mb-2">Free</h3>
                <p className="text-3xl font-bold mb-1">$0</p>
                <p className="text-sm text-muted-foreground mb-4">1,000 docs/month · Unlimited verification</p>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    <span>C2PA signing + Merkle auth</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    <span>Coalition membership included</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    <span>Licensing revenue shared — majority to publisher</span>
                  </li>
                </ul>
              </div>
              {/* Enterprise */}
              <div className="bg-card p-6 rounded-lg shadow-md border border-border">
                <h3 className="text-xl font-semibold mb-2">Enterprise</h3>
                <p className="text-3xl font-bold mb-1">Custom</p>
                <p className="text-sm text-muted-foreground mb-4">Unlimited everything · All add-ons</p>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    <span>Exclusive capabilities included</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    <span>Founding coalition: fee waived</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    <span>Same licensing splits as all tiers</span>
                  </li>
                </ul>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="font-semibold py-3 px-6 rounded-lg shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                <Link href="/pricing">
                  View Full Pricing <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button 
                onClick={() => setShowContactModal(true)}
                size="lg" 
                variant="outline"
                className="font-semibold py-3 px-6 rounded-lg"
              >
                Contact Sales <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Value Props Section */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 lg:gap-12 max-w-6xl mx-auto">
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border text-center">
              <DollarSign className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-2xl font-semibold mb-3">Transform Litigation Costs</h3>
              <p className="text-muted-foreground">
                Turn your biggest cost center into a strategic asset. Our cryptographic verification provides tamper-evident documentation designed to support stronger legal positioning.
              </p>
            </div>
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border text-center">
              <TrendingUp className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-2xl font-semibold mb-3">Unlock New Revenue</h3>
              <p className="text-muted-foreground">
                Create new, performance-based licensing models. Verifiable data on content usage allows you to price your assets based on their actual market value.
              </p>
            </div>
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border text-center">
              <Scale className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-2xl font-semibold mb-3">Tamper-Evident Documentation</h3>
              <p className="text-muted-foreground">
                Provide cryptographic verification of provenance designed for legal proceedings, protecting your intellectual property with mathematical certainty.
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
              How It Works: Your Technical Advantage
            </h2>
            <p className="text-lg md:text-xl mt-4 max-w-3xl mx-auto text-muted-foreground">
              Our technology provides verifiable proof, not just statistical likelihood. Here’s how we deliver mathematical certainty.
            </p>
          </div>
          <div className="max-w-3xl mx-auto">
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="item-1">
                <AccordionTrigger>Step 1: Cryptographic Watermarking</AccordionTrigger>
                <AccordionContent>
                  We embed invisible, cryptographically signed metadata directly into your content at the moment of publication. This 'digital birthmark' is tamper-proof and serves as unforgeable proof of origin.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-2">
                <AccordionTrigger>Step 2: Automated Content Monitoring</AccordionTrigger>
                <AccordionContent>
                  Our systems continuously monitor the web to see how your content is being used. We identify unauthorized use and provide the data needed to enforce your IP rights or create new licensing agreements.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-3">
                <AccordionTrigger>Step 3: Revenue & Compliance Reports</AccordionTrigger>
                <AccordionContent>
                  Receive detailed, tamper-evident reports that you can use to support infringement claims or negotiate performance-based licensing deals. Turn your content archive into a revenue-generating asset.
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
            context="publisher"
          />
        )}
      </AnimatePresence>
    </div>
  );
}
