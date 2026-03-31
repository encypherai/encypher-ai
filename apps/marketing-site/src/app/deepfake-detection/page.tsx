import React from "react";
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import Image from 'next/image';
import { ArrowRight, Eye, Shield, Zap, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';
import MetadataBackground from '@/components/hero/MetadataBackground';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import AISummary from '@/components/seo/AISummary';
import type { Metadata } from 'next';
import { generateMetadata as buildMetadata } from '@/lib/seo';

export const metadata: Metadata = buildMetadata(
  'Beyond Deepfake Detection: Cryptographic Authentication | Encypher',
  'Deepfake detection tools guess with statistical analysis. Encypher provides cryptographic proof of content authenticity with 100% accuracy. Mathematical certainty, not pattern matching.',
  '/deepfake-detection',
  undefined,
  ['deepfake detection', 'deepfake detection tools', 'deepfake verification', 'content authenticity', 'AI content verification']
);

export default function DeepfakeDetectionPage() {
  return (
    <>
      <AISummary
        title="Beyond Deepfake Detection"
        whatWeDo="Co-Chair of C2PA Text Provenance Task Force. API and SDKs for cryptographic authentication at creation, not post-hoc analysis. Standard publishes January 8, 2026."
        whoItsFor="Publishers needing provable content ownership. AI labs needing quote integrity verification. Enterprises requiring EU AI Act compliance."
        keyDifferentiator="Cryptographic watermarking survives copy-paste and distribution. Zero false positives. Mathematical certainty vs. statistical guessing."
        primaryValue="Building standards with NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others through C2PA (c2pa.org). Court-admissible proof of content authenticity."
      />

      {/* Hero Section */}
      <section className="relative w-full min-h-screen flex items-center justify-center overflow-hidden">
        <MetadataBackground />

        <div className="container mx-auto px-3 sm:px-4 py-12 sm:py-16 md:py-20 lg:py-28 relative z-10">
          <div className="max-w-4xl mx-auto text-center space-y-4 sm:space-y-6">
            <h1 className="text-2xl xs:text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-3 sm:mb-4 md:mb-6 text-shadow-md leading-tight px-2">
              Beyond Deepfake Detection: Mathematical Proof
            </h1>
            <p className="text-sm xs:text-base sm:text-lg md:text-xl mb-4 sm:mb-6 md:mb-8 text-shadow-md max-w-3xl mx-auto leading-relaxed px-2">
              Deepfake detection analyzes patterns after content is created. Encypher embeds <Link href="/cryptographic-watermarking" className="text-primary underline underline-offset-2 hover:no-underline">cryptographic watermarking</Link> proof at creation.<br />
              <strong>The difference? Detection guesses. Authentication knows.</strong>
            </p>

            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 md:gap-4 justify-center items-center px-2">
              <Button asChild size="lg" className="w-full sm:w-auto font-semibold py-2.5 sm:py-3 px-4 sm:px-6 rounded-lg shadow-lg text-sm sm:text-base btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                <Link href="/demo">
                  <span className="flex items-center justify-center">
                    See How It Works <ArrowRight className="ml-1.5 sm:ml-2 h-3.5 w-3.5 sm:h-4 sm:w-4" />
                  </span>
                </Link>
              </Button>
              <Button asChild size="lg" className="w-full sm:w-auto font-semibold py-2.5 sm:py-3 px-4 sm:px-6 rounded-lg shadow-lg text-sm sm:text-base btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                <Link href="/solutions/publishers">
                  <span className="flex items-center justify-center">
                    Explore Solutions <ArrowRight className="ml-1.5 sm:ml-2 h-3.5 w-3.5 sm:h-4 sm:w-4" />
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

      {/* The Problem with Detection */}
      <section className="py-20 w-full bg-muted/40 border-y border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Why Deepfake Detection Isn't Enough
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Statistical pattern matching has fundamental limitations that cryptographic authentication solves.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="bg-card p-6 rounded-lg border border-border">
              <XCircle className="h-10 w-10 text-destructive mb-4" />
              <h3 className="text-xl font-bold mb-3">Post-Hoc Analysis</h3>
              <p className="text-muted-foreground text-sm">
                Deepfake detection examines content <strong>after creation</strong>, looking for statistical anomalies. As generation improves, detection becomes impossible. It's a losing arms race.
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <AlertTriangle className="h-10 w-10 text-destructive mb-4" />
              <h3 className="text-xl font-bold mb-3">False Positives</h3>
              <p className="text-muted-foreground text-sm">
                Statistical tools flag legitimate content as fake. High false positive rates erode trust and create legal exposure. One wrong call damages credibility permanently.
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <Eye className="h-10 w-10 text-destructive mb-4" />
              <h3 className="text-xl font-bold mb-3">No Proof of Origin</h3>
              <p className="text-muted-foreground text-sm">
                Detection can't prove <strong>who created content</strong> or <strong>when modifications occurred</strong>. It identifies potential fakes but provides no evidence for what's real.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* The Authentication Approach */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              The Cryptographic Authentication Advantage
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Encypher embeds proof at creation. Not analysis after—authentication during.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 lg:gap-12 max-w-5xl mx-auto">
            {/* How It Works */}
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border">
              <h3 className="text-2xl font-bold mb-4">How Cryptographic Authentication Works</h3>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">1</div>
                  <div>
                    <p className="font-semibold mb-1">Content Creation</p>
                    <p className="text-sm text-muted-foreground">Cryptographic signatures embedded at the moment of creation—invisible, tamper-proof</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">2</div>
                  <div>
                    <p className="font-semibold mb-1">Immutable Record</p>
                    <p className="text-sm text-muted-foreground">Origin, timestamp, creator identity, and modifications tracked with mathematical certainty</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">3</div>
                  <div>
                    <p className="font-semibold mb-1">Instant Verification</p>
                    <p className="text-sm text-muted-foreground">Anyone can verify authenticity with 100% accuracy—no guessing, no false positives</p>
                  </div>
                </div>
              </div>
            </div>

            {/* The Benefits */}
            <div className="bg-primary/5 p-6 md:p-8 rounded-lg border-2 border-primary/20">
              <h3 className="text-2xl font-bold mb-4">What You Get</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">100% Accuracy</p>
                    <p className="text-sm text-muted-foreground">Mathematical proof, not statistical probability</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">Zero False Positives</p>
                    <p className="text-sm text-muted-foreground">Authentic content never flagged incorrectly</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">Proof of Origin</p>
                    <p className="text-sm text-muted-foreground">Know exactly who created what and when</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">Tamper Detection</p>
                    <p className="text-sm text-muted-foreground">See exactly what changed and where</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">Court-Admissible</p>
                    <p className="text-sm text-muted-foreground">Evidence that stands up in legal proceedings</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-20 w-full bg-muted/40 border-y border-border">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Detection vs. Authentication: The Fundamental Difference
          </h2>

          <div className="max-w-4xl mx-auto overflow-x-auto">
            <table className="w-full bg-card rounded-lg border border-border">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-4 font-semibold">Capability</th>
                  <th className="text-center p-4 font-semibold">Deepfake Detection</th>
                  <th className="text-center p-4 font-semibold bg-primary/5">Cryptographic Authentication</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-border">
                  <td className="p-4">When Applied</td>
                  <td className="text-center p-4">After creation</td>
                  <td className="text-center p-4 font-semibold bg-primary/5">At creation</td>
                </tr>
                <tr className="border-b border-border">
                  <td className="p-4">Method</td>
                  <td className="text-center p-4">Statistical analysis</td>
                  <td className="text-center p-4 font-semibold bg-primary/5">Cryptographic proof</td>
                </tr>
                <tr className="border-b border-border">
                  <td className="p-4">False Positives</td>
                  <td className="text-center p-4 text-destructive">High</td>
                  <td className="text-center p-4 text-primary font-semibold bg-primary/5">Zero</td>
                </tr>
                <tr className="border-b border-border">
                  <td className="p-4">Proof of Origin</td>
                  <td className="text-center p-4">❌</td>
                  <td className="text-center p-4 bg-primary/5">✅</td>
                </tr>
                <tr className="border-b border-border">
                  <td className="p-4">Tamper Detection</td>
                  <td className="text-center p-4">❌</td>
                  <td className="text-center p-4 bg-primary/5">✅</td>
                </tr>
                <tr className="border-b border-border">
                  <td className="p-4">Court-Admissible</td>
                  <td className="text-center p-4">Rarely</td>
                  <td className="text-center p-4 font-semibold bg-primary/5">Always</td>
                </tr>
                <tr>
                  <td className="p-4">Future-Proof</td>
                  <td className="text-center p-4">❌ (AI improves)</td>
                  <td className="text-center p-4 bg-primary/5">✅ (Math doesn't change)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Who Needs Authentication Beyond Detection
          </h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="bg-card p-6 rounded-lg border border-border">
              <Shield className="h-10 w-10 text-primary mb-4" />
              <h3 className="text-xl font-bold mb-3">Publishers</h3>
              <p className="text-muted-foreground text-sm mb-4">
                Prove AI copyright infringement with court-admissible evidence. Transform litigation into licensing.
              </p>
              <Button asChild variant="outline" size="sm" className="w-full">
                <Link href="/solutions/publishers">
                  Learn More <ArrowRight className="ml-2 h-3 w-3" />
                </Link>
              </Button>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <Zap className="h-10 w-10 text-primary mb-4" />
              <h3 className="text-xl font-bold mb-3">AI Companies</h3>
              <p className="text-muted-foreground text-sm mb-4">
                Track model outputs and performance intelligence. Ensure publisher compatibility and compliance.
              </p>
              <Button asChild variant="outline" size="sm" className="w-full">
                <Link href="/solutions/ai-companies">
                  Learn More <ArrowRight className="ml-2 h-3 w-3" />
                </Link>
              </Button>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <Eye className="h-10 w-10 text-primary mb-4" />
              <h3 className="text-xl font-bold mb-3">Enterprises</h3>
              <p className="text-muted-foreground text-sm mb-4">
                EU AI Act compliance with audit trails. Content governance at scale with intelligence upside.
              </p>
              <Button asChild variant="outline" size="sm" className="w-full">
                <Link href="/solutions/enterprise">
                  Learn More <ArrowRight className="ml-2 h-3 w-3" />
                </Link>
              </Button>
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
            Move Beyond Detection to Authentication
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            See how cryptographic authentication provides the certainty deepfake detection can&apos;t deliver. Compare <Link href="/compare/content-provenance-vs-content-detection" className="text-primary underline underline-offset-2 hover:no-underline">content provenance vs. content detection</Link> in depth.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center">
            <Button asChild size="lg" className="w-full sm:w-auto shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/demo">
                See Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" className="w-full sm:w-auto shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/solutions">
                Explore Solutions <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </>
  );
}
