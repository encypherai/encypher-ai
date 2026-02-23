"use client";

import React, { useState, useEffect } from "react";
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import Image from 'next/image';
import { AnimatePresence } from 'framer-motion';
import { ArrowRight, FileText, Zap, Shield, TrendingUp, Users, CheckCircle2, DollarSign } from 'lucide-react';
import MetadataBackground from '@/components/hero/MetadataBackground';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import AISummary from '@/components/seo/AISummary';
import SalesContactModal from '@/components/forms/SalesContactModal';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://api.encypherai.com';

export default function HomePage() {
  const [showContactModal, setShowContactModal] = useState(false);
  const [coalitionStats, setCoalitionStats] = useState<{
    coalition_members: number;
    total_signed_documents: number;
  } | null>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/coalition/public/stats`)
      .then((r) => r.ok ? r.json() : null)
      .then((data) => { if (data) setCoalitionStats(data); })
      .catch(() => {});
  }, []);

  return (
    <>
      <AISummary
        title="Encypher – Content Intelligence Infrastructure"
        whatWeDo="Encypher authored C2PA Section A.7 (Embedding Manifests into Unstructured Text). We provide API and SDKs in Python, TypeScript, Go, and Rust for patent-pending granular content attribution and licensing infrastructure. Standard published January 8, 2026."
        whoItsFor="Publishers needing content licensing infrastructure and provable ownership. AI labs needing performance intelligence and compliance. Enterprises requiring EU AI Act and China watermarking mandate compliance."
        keyDifferentiator="Patent-pending cryptographic watermarking with tamper-evident verification. Merkle tree authentication provides documentation designed for legal proceedings. Survives copy-paste, B2B distribution, and scraping."
        primaryValue="Provide technical infrastructure for content licensing across the AI ecosystem. Encypher serves as Co-Chair of the C2PA Text Provenance Task Force, with technology reviewed by C2PA members including Google, OpenAI, Adobe, and Microsoft."
        pagePath="/"
        faq={[
          {
            question: "What is Encypher?",
            answer: "Encypher authored C2PA Section A.7 (Embedding Manifests into Unstructured Text) and serves as Co-Chair of the C2PA Text Provenance Task Force. We provide API and SDKs for patent-pending granular content attribution that enables content licensing infrastructure. Standard published January 8, 2026. Technology reviewed by C2PA members including Google, OpenAI, Adobe, and Microsoft."
          },
          {
            question: "What is the C2PA text standard?",
            answer: "The C2PA text standard (Section A.7) defines how text content is cryptographically authenticated using Unicode variation selectors. Encypher authored this section of the specification. It enables verification of content origin with mathematical certainty. Published January 8, 2026."
          },
          {
            question: "How is Encypher different from AI detection tools?",
            answer: "AI detection tools provide statistical guessing with variable accuracy. Encypher provides cryptographic verification at sentence-level. Our watermarking survives copy-paste and distribution, enabling content licensing infrastructure and attribution across the AI ecosystem."
          },
          {
            question: "Who uses Encypher?",
            answer: "Publishers seeking content licensing revenue and provable ownership. AI labs needing publisher ecosystem compatibility, quote integrity verification, and performance intelligence. Enterprises requiring EU AI Act and China watermarking compliance."
          },
          {
            question: "Does Encypher have an API and SDKs?",
            answer: "Yes. Encypher provides a REST API and SDKs in Python, TypeScript, Go, and Rust. Publishers can integrate sentence-level tracking in 30 days. AI labs get one integration for the entire publisher ecosystem. Sign up at encypherai.com to access the API, documentation, and dashboard."
          }
        ]}
      />
      
      {/* Hero Section */}
      <section className="relative w-full min-h-screen flex items-center justify-center overflow-hidden" style={{ minHeight: '100vh' }}>
        <MetadataBackground />
        
        <div className="container mx-auto px-3 sm:px-4 py-12 sm:py-16 md:py-20 lg:py-28 relative z-10">
          <div className="max-w-4xl mx-auto text-center space-y-4 sm:space-y-6">
            <h1 className="text-2xl xs:text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-3 sm:mb-4 md:mb-6 text-shadow-md leading-tight px-2" style={{ minHeight: '3rem' }}>
              The Licensing Infrastructure for AI Content
            </h1>
            <p className="text-sm xs:text-base sm:text-lg md:text-xl mb-4 sm:mb-6 md:mb-8 text-shadow-md max-w-3xl mx-auto leading-relaxed px-2" style={{ minHeight: '4rem' }}>
              Publishers need to get paid when AI companies use their content.<br />
              AI companies need proof they licensed it properly.<br />
              Encypher connects both sides -- built on the C2PA standard we authored.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-4 justify-center items-center px-2">
              <Button asChild size="lg" className="w-full sm:w-auto font-semibold py-2.5 sm:py-3 px-4 sm:px-6 rounded-lg shadow-lg text-sm sm:text-base bg-white text-delft-blue hover:bg-columbia-blue transition-colors">
                <Link href="/auth/register">
                  <span className="flex items-center justify-center">
                    Get Started Free <ArrowRight className="ml-1.5 sm:ml-2 h-3.5 w-3.5 sm:h-4 sm:w-4" />
                  </span>
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="w-full sm:w-auto font-semibold py-2.5 sm:py-3 px-4 sm:px-6 rounded-lg shadow-lg text-sm sm:text-base">
                <Link href="/try">
                  <span className="flex items-center justify-center">
                    Try It Live <ArrowRight className="ml-1.5 sm:ml-2 h-3.5 w-3.5 sm:h-4 sm:w-4" />
                  </span>
                </Link>
              </Button>
            </div>
            
            {/* Standards Authority */}
            <div className="mt-8 sm:mt-12 md:mt-16 text-center">
              <h3 className="text-xs sm:text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 sm:mb-6 text-shadow-sm px-2">
                From the Authors of the C2PA Text Standard
              </h3>
              <div className="flex justify-center items-center gap-6 sm:gap-8 md:gap-12 flex-wrap">
                <div className="relative h-8 w-28 sm:h-10 sm:w-32 md:h-12 md:w-36 flex-shrink-0">
                  <Image
                    src="/c2pa-hero.svg"
                    alt="C2PA Logo"
                    fill
                    sizes="(max-width: 640px) 112px, (max-width: 768px) 128px, 144px"
                    style={{objectFit: "contain"}}
                    className="dark:invert dark:brightness-200"
                    priority
                  />
                </div>
                <div className="relative h-8 w-28 sm:h-10 sm:w-32 md:h-12 md:w-36 flex-shrink-0">
                  <Image
                    src="/CAI_Lockup_RGB_Black.svg"
                    alt="Content Authenticity Initiative Logo"
                    fill
                    sizes="(max-width: 640px) 112px, (max-width: 768px) 128px, 144px"
                    style={{objectFit: "contain"}}
                    className="dark:invert dark:brightness-200"
                    priority
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Credentials Bar */}
      <section className="py-12 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto text-center">
            <div>
              <p className="text-2xl md:text-3xl font-bold text-primary">C2PA 2.3</p>
              <p className="text-sm text-muted-foreground mt-1">Standard Authors</p>
            </div>
            <div>
              <p className="text-2xl md:text-3xl font-bold text-primary">Jan 2026</p>
              <p className="text-sm text-muted-foreground mt-1">Standard Published</p>
            </div>
            <div>
              <p className="text-2xl md:text-3xl font-bold text-primary">1,000</p>
              <p className="text-sm text-muted-foreground mt-1">Free Signs / Month</p>
            </div>
            <div>
              <p className="text-2xl md:text-3xl font-bold text-primary">99.95%</p>
              <p className="text-sm text-muted-foreground mt-1">Uptime SLA</p>
            </div>
          </div>
        </div>
      </section>

      {/* Infrastructure for Two Markets */}
      <section id="value-prop" className="py-20 w-full bg-muted/40 border-y border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Infrastructure for the AI Content Economy
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Two markets. One infrastructure. Sentence-level tracking enables both litigation evidence and performance intelligence.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8 lg:gap-12 max-w-5xl mx-auto">
            {/* For Publishers */}
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border">
              <div className="flex items-center gap-4 mb-4">
                <FileText className="h-8 w-8 text-primary" />
                <h3 className="text-2xl font-semibold">For Publishers</h3>
              </div>
              <h4 className="text-xl font-bold mb-3">Transform Unmarked Content Into Provably Owned Assets</h4>
              <p className="text-muted-foreground mb-4">
                Cryptographic watermarking that survives copy-paste and scraping. Serve formal notice to AI companies with mathematical proof of ownership.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Cryptographic proof survives copy-paste and scraping</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Formal notice capability with sentence-level tracking</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Success-based model: we only win when you win</span>
                </li>
              </ul>
              <Button asChild className="w-full mt-6 shadow-lg btn-blue-hover" size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                <Link href="/publisher-demo">
                  See Publisher Demo <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>

            {/* For AI Companies */}
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border">
              <div className="flex items-center gap-4 mb-4">
                <Zap className="h-8 w-8 text-primary" />
                <h3 className="text-2xl font-semibold">For AI Labs</h3>
              </div>
              <h4 className="text-xl font-bold mb-3">License Content at Scale. Prove You Did It Right.</h4>
              <p className="text-muted-foreground mb-4">
                One integration to access licensed publisher content, satisfy regulators, and show your users you take provenance seriously. Built collaboratively through C2PA -- OpenAI, Google, Adobe, and Microsoft are members.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Access the publisher coalition with a single integration</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">EU AI Act + China mandate compliant out of the box</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Signal responsible AI with the Licensed Content mark</span>
                </li>
              </ul>
              <Button asChild className="w-full mt-6 shadow-lg btn-blue-hover" size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                <Link href="/ai-demo">
                  See AI Lab Demo <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">How It Works</h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-2xl mx-auto">
              Three steps from unprotected content to licensed revenue.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-2xl font-bold mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold mb-3">Sign Your Content</h3>
              <p className="text-muted-foreground text-sm">
                Invisible C2PA watermarks embed into every article at publication. Archive signing covers existing content in bulk. Zero visible changes to readers.
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-2xl font-bold mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold mb-3">Track Where It Goes</h3>
              <p className="text-muted-foreground text-sm">
                Provenance verification events accumulate in your free dashboard. See which AI systems are using your content. Evidence package builds automatically.
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-2xl font-bold mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold mb-3">License and Get Paid</h3>
              <p className="text-muted-foreground text-sm">
                When evidence reaches threshold, send formal notice. Encypher handles licensing through the coalition -- you approve every deal, you control the terms.
              </p>
            </div>
          </div>

          <div className="text-center mt-10">
            <Button asChild variant="outline" size="lg">
              <Link href="/try">
                Try It Live -- 30 Seconds <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Why Encypher - Replaces "Key Features" */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">Why Encypher</h2>
          <p className="text-lg text-center text-muted-foreground mb-12 max-w-3xl mx-auto">
            We wrote the standard. We built the infrastructure. Publishers and AI companies both win.
          </p>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <Shield className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">We Wrote the Standard</h3>
              <p className="text-muted-foreground">
                Encypher authored C2PA Section A.7 -- the global standard for text content authentication, published January 2026. When the industry needed a solution, we wrote it.
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <TrendingUp className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Proof That Holds Up</h3>
              <p className="text-muted-foreground">
                Invisible cryptographic signatures embedded sentence by sentence. They survive copy-paste, scraping, and distribution -- providing a tamper-evident record of what was published and when.
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <Users className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Neutral Infrastructure</h3>
              <p className="text-muted-foreground">
                Like Visa connecting banks, Encypher connects publishers and AI companies. Neither side is the adversary. Both sides need the network to function.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Standards & Compliance Section */}
      <StandardsCompliance />

      {/* Final CTA */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            The AI content economy is being built right now.
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            Publishers who protect their content today are building the evidence package and the coalition that determines how licensing works tomorrow. Start free.
          </p>
          {coalitionStats && (
            <div className="inline-flex items-center gap-6 mb-8 px-6 py-3 bg-muted/40 border border-border rounded-full text-sm">
              <span className="font-semibold text-primary">
                {coalitionStats.coalition_members.toLocaleString()} publishers
              </span>
              <span className="text-muted-foreground">in the coalition</span>
              <span className="w-px h-4 bg-border" />
              <span className="font-semibold text-primary">
                {coalitionStats.total_signed_documents.toLocaleString()} articles
              </span>
              <span className="text-muted-foreground">protected</span>
            </div>
          )}
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center">
            <Button asChild size="lg" className="w-full sm:w-auto shadow-lg font-semibold" style={{ backgroundColor: '#1a365d', color: '#ffffff' }}>
              <Link href="/auth/register">
                Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="w-full sm:w-auto font-semibold"
              onClick={() => setShowContactModal(true)}
            >
              Talk to Sales <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
          
          {/* Developer CTA - Secondary */}
          <div className="mt-8 pt-8 border-t border-border/50">
            <p className="text-sm text-muted-foreground mb-3">
              Developers: Try our open-source implementation
            </p>
            <Button asChild variant="ghost" size="sm">
              <a
                href="https://github.com/encypherai/encypher-ai"
                target="_blank"
                rel="noopener noreferrer"
              >
                View on GitHub <ArrowRight className="inline ml-2 h-3.5 w-3.5" />
              </a>
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
    </>
  );
}