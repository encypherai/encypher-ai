import React from "react";
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import Image from 'next/image';
import { ArrowRight, FileText, Scale, AlertTriangle, CheckCircle2, DollarSign, Shield } from 'lucide-react';
import MetadataBackground from '@/components/hero/MetadataBackground';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import AISummary from '@/components/seo/AISummary';
import type { Metadata } from 'next';
import { generateMetadata as buildMetadata } from '@/lib/seo';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypher.com';

export const metadata: Metadata = buildMetadata(
  'AI Copyright Infringement: Court-Admissible Proof | Encypher',
  'Stop guessing with 26% accurate AI detectors. Encypher provides cryptographic proof of AI copyright infringement with 100% accuracy. Transform litigation costs into licensing revenue.',
  '/ai-copyright-infringement',
  '/og-image-publishers.png',
  ['AI copyright infringement', 'AI copyright lawsuit', 'AI art copyright', 'prove AI copyright', 'AI training data copyright'],
  'Cryptographic proof of AI copyright infringement. 100% accuracy.'
);

export default function AICopyrightInfringementPage() {
  return (
    <>
      <AISummary
        title="AI Copyright Infringement Solution"
        whatWeDo="Authors of C2PA Section A.7. Patent-pending API and SDKs for granular content attribution with Merkle tree authentication. Court-admissible evidence generation with 83 claims filed. Standard published January 8, 2026."
        whoItsFor="Publishers facing AI content usage challenges who need provable ownership and licensing infrastructure. Legal teams seeking court-admissible evidence."
        keyDifferentiator="Patent-pending Merkle tree authentication generates court-admissible evidence. Cryptographic watermarking survives copy-paste and B2B distribution. 83 claims covering granular content attribution."
        primaryValue="Transform litigation costs into licensing revenue. Building standards with NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others through C2PA (c2pa.org)."
      />

      {/* Hero Section */}
      <section className="relative w-full min-h-screen flex items-center justify-center overflow-hidden">
        <MetadataBackground />

        <div className="container mx-auto px-3 sm:px-4 py-12 sm:py-16 md:py-20 lg:py-28 relative z-10">
          <div className="max-w-4xl mx-auto text-center space-y-4 sm:space-y-6">
            <h1 className="text-2xl xs:text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-3 sm:mb-4 md:mb-6 text-shadow-md leading-tight px-2">
              From AI Copyright Infringement to Licensing Revenue
            </h1>
            <p className="text-sm xs:text-base sm:text-lg md:text-xl mb-4 sm:mb-6 md:mb-8 text-shadow-md max-w-3xl mx-auto leading-relaxed px-2">
              AI companies train on your content without permission. You know it&apos;s happening but can&apos;t prove it in court. AI detectors fail with 26% accuracy.<br />
              <strong>Encypher provides <Link href="/cryptographic-watermarking" className="text-primary underline underline-offset-2 hover:no-underline">cryptographic watermarking</Link> proof with 100% accuracy.</strong>
            </p>

            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 md:gap-4 justify-center items-center px-2">
              <Button asChild size="lg" className="w-full sm:w-auto font-semibold py-2.5 sm:py-3 px-4 sm:px-6 rounded-lg shadow-lg text-sm sm:text-base btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                <Link href="/publisher-demo">
                  <span className="flex items-center justify-center">
                    See How It Works <ArrowRight className="ml-1.5 sm:ml-2 h-3.5 w-3.5 sm:h-4 sm:w-4" />
                  </span>
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="w-full sm:w-auto font-semibold py-2.5 sm:py-3 px-4 sm:px-6 rounded-lg shadow-lg text-sm sm:text-base">
                <Link href={`${DASHBOARD_URL}/auth/signin?mode=signup&source=ai-copyright`}>
                  <span className="flex items-center justify-center">
                    Get Started Free <ArrowRight className="ml-1.5 sm:ml-2 h-3.5 w-3.5 sm:h-4 sm:w-4" />
                  </span>
                </Link>
              </Button>
              <Button asChild size="lg" variant="ghost" className="w-full sm:w-auto font-semibold py-2.5 sm:py-3 px-4 sm:px-6 text-sm sm:text-base">
                <Link href="/solutions/publishers">
                  <span className="flex items-center justify-center">
                    For Publishers <ArrowRight className="ml-1.5 sm:ml-2 h-3.5 w-3.5 sm:h-4 sm:w-4" />
                  </span>
                </Link>
              </Button>
            </div>

            {/* Standards Authority */}
            <div className="mt-8 sm:mt-12 md:mt-16 text-center">
              <h3 className="text-xs sm:text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 sm:mb-6 text-shadow-sm px-2">
                Authors of C2PA Section A.7 (Text Provenance)
              </h3>
              <div className="flex justify-center items-center gap-6 sm:gap-8 md:gap-12 flex-wrap">
                <div className="relative h-8 w-28 sm:h-10 sm:w-32 md:h-12 md:w-36 flex-shrink-0">
                  <Image src="/c2pa-hero.svg" alt="C2PA Logo" fill sizes="(max-width: 640px) 112px, (max-width: 768px) 128px, 144px" style={{objectFit: "contain"}} />
                </div>
                <div className="relative h-8 w-28 sm:h-10 sm:w-32 md:h-12 md:w-36 flex-shrink-0">
                  <Image src="/CAI_Lockup_RGB_Black.svg" alt="Content Authenticity Initiative Logo" fill sizes="(max-width: 640px) 112px, (max-width: 768px) 128px, 144px" style={{objectFit: "contain"}} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* The Problem Section */}
      <section className="py-20 w-full bg-muted/40 border-y border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              The AI Copyright Infringement Challenge
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Publishers face a $250M annual legal battle against AI companies using their content without permission.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="bg-card p-6 rounded-lg border border-border">
              <AlertTriangle className="h-10 w-10 text-destructive mb-4" />
              <h3 className="text-xl font-bold mb-3">The Evidence Gap</h3>
              <p className="text-muted-foreground text-sm">
                You know AI companies are training on your content. But proving <strong>which specific content</strong> was used, <strong>where it appeared</strong>, and <strong>how it was modified</strong> is nearly impossible with current tools.
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <Scale className="h-10 w-10 text-destructive mb-4" />
              <h3 className="text-xl font-bold mb-3">Detection Tools Fail</h3>
              <p className="text-muted-foreground text-sm">
                Statistical AI detectors provide only <strong>26% accuracy</strong>—useless for court. High false positive rates mean legitimate claims get dismissed. You're spending millions on litigation with no proof.
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <DollarSign className="h-10 w-10 text-destructive mb-4" />
              <h3 className="text-xl font-bold mb-3">Revenue Lost</h3>
              <p className="text-muted-foreground text-sm">
                Without proof, you can't establish licensing terms. Every day AI companies profit from your content while you bear legal costs. The problem isn't going away—it's accelerating.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* The Solution Section */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Cryptographic Proof, Not Statistical Guessing
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Encypher provides the evidence needed to win AI copyright infringement cases and enable licensing.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 lg:gap-12 max-w-5xl mx-auto">
            {/* What You Get */}
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border">
              <h3 className="text-2xl font-bold mb-4">What You Get</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">Sentence-Level Tracking</p>
                    <p className="text-sm text-muted-foreground">Prove exactly which sentences were used—not just that a document was accessed</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">100% Accuracy</p>
                    <p className="text-sm text-muted-foreground">Mathematical certainty through cryptographic proof—zero false positives</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">Court-Admissible Evidence</p>
                    <p className="text-sm text-muted-foreground">Evidence packages designed for litigation with forensic-grade documentation</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">Usage Intelligence</p>
                    <p className="text-sm text-muted-foreground">See where your content appears, how it's modified, and by whom</p>
                  </div>
                </li>
              </ul>
            </div>

            {/* The Transformation */}
            <div className="bg-primary/5 p-6 md:p-8 rounded-lg border-2 border-primary/20">
              <h3 className="text-2xl font-bold mb-4">The Transformation</h3>
              <div className="space-y-6">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">From:</p>
                  <p className="font-semibold text-lg">$14M in annual legal costs</p>
                  <p className="text-sm text-muted-foreground">Fighting unwinnable cases with unreliable evidence</p>
                </div>
                <div className="border-t border-border pt-6">
                  <p className="text-sm text-muted-foreground mb-1">To:</p>
                  <p className="font-semibold text-lg text-primary">$20M+ in licensing revenue</p>
                  <p className="text-sm text-muted-foreground">Enforceable agreements backed by provable usage</p>
                </div>
                <div className="bg-card p-4 rounded-lg mt-4">
                  <p className="text-sm font-semibold mb-2">Our Model:</p>
                  <p className="text-sm text-muted-foreground">
                    We only succeed when you succeed. Success-aligned pricing means no licensing revenue = no payment. <a href="/contact" className="text-primary underline">Contact us for details</a>.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-20 w-full bg-muted/40 border-y border-border">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            AI Detection vs. Cryptographic Proof
          </h2>

          <div className="max-w-4xl mx-auto overflow-x-auto">
            <table className="w-full bg-card rounded-lg border border-border">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-4 font-semibold">Capability</th>
                  <th className="text-center p-4 font-semibold">AI Detectors</th>
                  <th className="text-center p-4 font-semibold bg-primary/5">Encypher</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-border">
                  <td className="p-4">Accuracy</td>
                  <td className="text-center p-4 text-destructive">26%</td>
                  <td className="text-center p-4 text-primary font-semibold bg-primary/5">100%</td>
                </tr>
                <tr className="border-b border-border">
                  <td className="p-4">Sentence-Level Tracking</td>
                  <td className="text-center p-4">❌</td>
                  <td className="text-center p-4 bg-primary/5">✅</td>
                </tr>
                <tr className="border-b border-border">
                  <td className="p-4">Court-Admissible</td>
                  <td className="text-center p-4">❌</td>
                  <td className="text-center p-4 bg-primary/5">✅</td>
                </tr>
                <tr className="border-b border-border">
                  <td className="p-4">False Positives</td>
                  <td className="text-center p-4 text-destructive">High</td>
                  <td className="text-center p-4 text-primary font-semibold bg-primary/5">Zero</td>
                </tr>
                <tr className="border-b border-border">
                  <td className="p-4">Tamper Detection</td>
                  <td className="text-center p-4">❌</td>
                  <td className="text-center p-4 bg-primary/5">✅</td>
                </tr>
                <tr>
                  <td className="p-4">Licensing Infrastructure</td>
                  <td className="text-center p-4">❌</td>
                  <td className="text-center p-4 bg-primary/5">✅</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Why Encypher */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            Why Publishers Choose Encypher
          </h2>
          <p className="text-lg text-center text-muted-foreground mb-12 max-w-3xl mx-auto">
            We authored Section A.7 of the <Link href="/c2pa-standard" className="text-primary underline underline-offset-2 hover:no-underline">C2PA</Link> 2.3 specification. We built the proof infrastructure. We enable the licensing economy.
          </p>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <Shield className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Standards Authority</h3>
              <p className="text-muted-foreground">
                Authored Section A.7 of the C2PA 2.3 specification (text provenance). Co-Chair of the C2PA Text Provenance Task Force.
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <FileText className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Proprietary Tracking</h3>
              <p className="text-muted-foreground">
                Sentence-level tracking is exclusive to Encypher. 18+ months of development created capabilities AI detection companies can't replicate.
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <DollarSign className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Success-Based Model</h3>
              <p className="text-muted-foreground">
                We only win when you win. 25-30% of licensing revenue we enable. If you don't generate revenue, we don't get paid beyond setup.
              </p>
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
            Ready to Transform AI Copyright Infringement Into Revenue?
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            See how cryptographic proof with sentence-level tracking provides the evidence you need to win cases and establish licensing terms. Understand the <Link href="/cryptographic-watermarking/legal-implications" className="text-primary underline underline-offset-2 hover:no-underline">legal implications of cryptographic watermarking</Link> and the full <Link href="/content-provenance" className="text-primary underline underline-offset-2 hover:no-underline">content provenance</Link> picture.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center">
            <Button asChild size="lg" className="w-full sm:w-auto shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/publisher-demo">
                See Publisher Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" className="w-full sm:w-auto shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/solutions/publishers">
                Learn More <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </>
  );
}
