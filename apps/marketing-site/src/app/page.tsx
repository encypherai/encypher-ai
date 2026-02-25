"use client";

import React, { useState, useEffect } from "react";
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import Image from 'next/image';
import { AnimatePresence } from 'framer-motion';
import { ArrowRight, FileText, CheckCircle2, Bot, Building2 } from 'lucide-react';
import MetadataBackground from '@/components/hero/MetadataBackground';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import AISummary from '@/components/seo/AISummary';
import SalesContactModal from '@/components/forms/SalesContactModal';
import { CHROME_STORE_URL } from '@/components/ui/ChromeInstallButton';
import Script from 'next/script';
import { organizationSchema } from '@/lib/seo';

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
      <Script
        id="schema-organization"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
      />
      <AISummary
        title="Encypher – Machine-Readable Rights for Your Content"
        whatWeDo="Encypher authored C2PA Section A.7 (Embedding Manifests into Unstructured Text). We embed invisible cryptographic proof directly into text so ownership and licensing terms travel with content through copy-paste, syndication, scraping, and AI training."
        whoItsFor="Publishers who need enforceable machine-readable rights, competitor scraping visibility, and provable ownership evidence."
        keyDifferentiator="Not AI detection and not front-door-only controls. Encypher embeds cryptographic proof into the content itself, so provenance survives distribution and can be independently verified."
        primaryValue="Protect content at publish time, track where it appears, and enforce your licensing terms with cryptographic evidence. Encypher co-chairs the C2PA Text Provenance Task Force."
        pagePath="/"
      />
      
      {/* Hero Section */}
      <section className="relative w-full min-h-screen flex items-center justify-center overflow-hidden" style={{ minHeight: '100vh' }}>
        <MetadataBackground />
        
        <div className="container mx-auto px-3 sm:px-4 py-12 sm:py-16 md:py-20 lg:py-28 relative z-10">
          <div className="max-w-4xl mx-auto text-center space-y-4 sm:space-y-6">
            <h1 className="text-2xl xs:text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-3 sm:mb-4 md:mb-6 text-shadow-md leading-tight px-2" style={{ minHeight: '3rem' }}>
              Your Content Carries Its Own Proof of Ownership.<br />Everywhere It Goes.
            </h1>
            <p className="text-sm xs:text-base sm:text-lg md:text-xl mb-4 sm:mb-6 md:mb-8 text-shadow-md max-w-3xl mx-auto leading-relaxed px-2" style={{ minHeight: '4rem' }}>
              Invisible cryptographic signatures embed directly into your text content, surviving copy-paste, scraping, syndication, and AI training.<br />
              When someone uses your content, you can prove it&apos;s yours.<br />
              When they ignore your rights, you can prove that too.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-4 justify-center items-center px-2">
              <Button asChild size="lg" className="w-full sm:w-auto font-semibold py-2.5 sm:py-3 px-4 sm:px-6 rounded-lg shadow-lg text-sm sm:text-base bg-white text-delft-blue hover:bg-columbia-blue transition-colors">
                <Link href="/try">
                  <span className="flex items-center justify-center">
                    See It Work <ArrowRight className="ml-1.5 sm:ml-2 h-3.5 w-3.5 sm:h-4 sm:w-4" />
                  </span>
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="w-full sm:w-auto font-semibold py-2.5 sm:py-3 px-4 sm:px-6 rounded-lg shadow-lg text-sm sm:text-base">
                <Link href="#differentiation">
                  <span className="flex items-center justify-center">
                    How It&apos;s Different <ArrowRight className="ml-1.5 sm:ml-2 h-3.5 w-3.5 sm:h-4 sm:w-4" />
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
              <p className="text-2xl md:text-3xl font-bold text-primary">Section A.7</p>
              <p className="text-sm text-muted-foreground mt-1">Authored in C2PA</p>
            </div>
            <div>
              <p className="text-2xl md:text-3xl font-bold text-primary">Jan 8, 2026</p>
              <p className="text-sm text-muted-foreground mt-1">Standard Published</p>
            </div>
            <div>
              <p className="text-2xl md:text-3xl font-bold text-primary">Co-Chair</p>
              <p className="text-sm text-muted-foreground mt-1">Text Task Force</p>
            </div>
            <div>
              <p className="text-2xl md:text-3xl font-bold text-primary">Free</p>
              <p className="text-sm text-muted-foreground mt-1">1,000 signs / month</p>
            </div>
          </div>
        </div>
      </section>

      {/* Publisher-first Value Section */}
      <section id="value-prop" className="py-20 w-full bg-muted/40 border-y border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Infrastructure for Content Rights. Built on the C2PA Standard.
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Publisher-first infrastructure that protects content ownership across syndication, competitor copying, and AI usage.
            </p>
          </div>

          <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-10 gap-5">
            <article className="lg:col-span-4 bg-card p-6 md:p-8 rounded-lg shadow-lg border-2 border-primary/20">
              <div className="flex items-center gap-4 mb-4">
                <FileText className="h-8 w-8 text-primary" />
                <h3 className="text-2xl font-semibold">For Publishers</h3>
              </div>
              <h4 className="text-xl font-bold mb-3">Protect Ownership Across Every Channel</h4>
              <p className="text-muted-foreground mb-4">
                Other solutions put a lock on your front door. Encypher locks every piece of content you own with invisible proof that survives redistribution.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Cryptographic proof survives copy-paste, scraping, and syndication</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Detect competitor and aggregator reuse with cryptographic certainty</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Set machine-readable licensing terms: your content, your rules</span>
                </li>
              </ul>
              <div className="mt-6 flex flex-col sm:flex-row gap-3">
                <Button asChild className="shadow-lg btn-blue-hover" size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                  <Link href="/solutions/publishers">
                    See Publisher Demo <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </article>

            <article className="lg:col-span-3 bg-card p-6 rounded-lg border border-border shadow-sm">
              <div className="flex items-center gap-3 mb-3">
                <Bot className="h-6 w-6 text-primary" />
                <h3 className="text-xl font-semibold">For AI Labs</h3>
              </div>
              <h4 className="text-lg font-bold mb-3">Compatible Infrastructure for Marked Content</h4>
              <p className="text-sm text-muted-foreground mb-4">
                The publisher ecosystem is implementing cryptographic provenance at scale. Your training pipeline needs compatible infrastructure - built collaboratively through C2PA with OpenAI, Google, Adobe, and Microsoft as members.
              </p>
              <ul className="space-y-2 mb-5">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">One integration for the entire publisher ecosystem</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Quote integrity verification - prove &quot;According to [Source]&quot; is accurate</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Standards-based - we co-authored the spec</span>
                </li>
              </ul>
              <Button asChild variant="outline" className="w-full">
                <Link href="/solutions/ai-companies">
                  See AI Lab Demo <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </article>

            <article className="lg:col-span-3 bg-card p-6 rounded-lg border border-border shadow-sm">
              <div className="flex items-center gap-3 mb-3">
                <Building2 className="h-5 w-5 text-primary" />
                <h3 className="text-xl font-semibold">For Enterprises</h3>
              </div>
              <h4 className="text-lg font-bold mb-3">AI Content Governance at Scale</h4>
              <p className="text-sm text-muted-foreground mb-4">
                When your organization generates or ingests AI content, you need provenance infrastructure that meets regulatory requirements - EU AI Act, China watermarking mandates, and emerging US frameworks.
              </p>
              <ul className="space-y-2 mb-5">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">C2PA 2.3 compliant - standard published January 8, 2026</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Sentence-level authentication for audit trails</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">On-premise or cloud deployment with SSO and custom SLAs</span>
                </li>
              </ul>
              <Button asChild variant="outline" className="w-full">
                <Link href="/solutions/enterprises">
                  Learn More <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </article>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">Three Steps. Your Content Is Protected Everywhere.</h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-2xl mx-auto">
              Capability first: mark it, track it, own it.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-2xl font-bold mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold mb-3">Mark It</h3>
              <p className="text-muted-foreground text-sm">
                Free, invisible cryptographic proof embeds directly into your text. Survives copy-paste, scraping, syndication, and AI training with zero visible changes.
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-2xl font-bold mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold mb-3">Track It</h3>
              <p className="text-muted-foreground text-sm">
                Detect marked content on competitor sites, aggregators, social posts, and AI outputs. Evidence trails build automatically in your dashboard.
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-2xl font-bold mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold mb-3">Own It</h3>
              <p className="text-muted-foreground text-sm">
                Set machine-readable licensing terms, enforce against unauthorized use, and license through coalition pathways or direct negotiation.
              </p>
            </div>
          </div>

          <div className="text-center mt-10">
            <Button asChild variant="outline" size="lg">
              <Link href="/try">
                Try It Live - 30 Seconds <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Content Theft Detection */}
      <section className="py-20 w-full bg-muted/40 border-y border-border">
        <div className="container mx-auto px-4 max-w-5xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Know When Someone Takes Your Content. With Certainty.</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-3xl mx-auto">
            Our Chrome extension and analytics detect when marked articles appear on competitor sites, aggregators, social platforms, or AI outputs.
            Not statistical guessing - cryptographic proof that this specific text came from your publication.
          </p>
          <Button asChild size="lg" className="shadow-lg font-semibold" style={{ backgroundColor: '#1a365d', color: '#ffffff' }}>
            <a href={CHROME_STORE_URL} target="_blank" rel="noopener noreferrer">
              Install Chrome Extension <ArrowRight className="ml-2 h-4 w-4" />
            </a>
          </Button>
        </div>
      </section>

      {/* Lock Analogy + Comparison */}
      <section id="differentiation" className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">Not a Lock on Your Front Door. A Lock on Everything Inside.</h2>
          <p className="text-lg text-center text-muted-foreground mb-12 max-w-3xl mx-auto">
            Other tools protect your website. Encypher protects your content wherever it goes.
          </p>

          <div className="overflow-x-auto max-w-5xl mx-auto">
            <table className="w-full border border-border rounded-lg text-sm">
              <thead className="bg-muted/40">
                <tr>
                  <th className="text-left p-4 font-semibold">Capability</th>
                  <th className="text-left p-4 font-semibold">Front-Door Solutions</th>
                  <th className="text-left p-4 font-semibold">Encypher</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-t border-border">
                  <td className="p-4">Protects content on your site</td>
                  <td className="p-4">Yes</td>
                  <td className="p-4">Yes</td>
                </tr>
                <tr className="border-t border-border">
                  <td className="p-4">Protects copied content</td>
                  <td className="p-4">No</td>
                  <td className="p-4">Yes</td>
                </tr>
                <tr className="border-t border-border">
                  <td className="p-4">Protects through syndication</td>
                  <td className="p-4">No</td>
                  <td className="p-4">Yes</td>
                </tr>
                <tr className="border-t border-border">
                  <td className="p-4">Protects in AI training sets</td>
                  <td className="p-4">No</td>
                  <td className="p-4">Yes</td>
                </tr>
                <tr className="border-t border-border">
                  <td className="p-4">Cryptographic proof of ownership</td>
                  <td className="p-4">No</td>
                  <td className="p-4">Yes</td>
                </tr>
                <tr className="border-t border-border">
                  <td className="p-4">Embeds machine-readable terms</td>
                  <td className="p-4">Per-page</td>
                  <td className="p-4">Per-sentence</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Standards & Compliance Section */}
      <StandardsCompliance />

      {/* Final CTA */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Machine-Readable Rights for Your Content.
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            Start free. Mark your content today, track where it goes, and build enforceable evidence before disputes begin.
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