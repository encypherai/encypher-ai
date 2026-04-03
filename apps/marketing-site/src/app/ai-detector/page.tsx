'use client';

import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { Button } from '@encypher/design-system';
import Image from 'next/image';
import { ArrowRight, Search, Shield, Zap, CheckCircle2, XCircle, TrendingDown } from 'lucide-react';
import MetadataBackground from '@/components/hero/MetadataBackground';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import AISummary from '@/components/seo/AISummary';
import SalesContactModal from '@/components/forms/SalesContactModal';

export default function AIDetectorPage() {
  const [showContactModal, setShowContactModal] = useState(false);

  return (
    <>
      <AISummary
        title="Better Than AI Detectors"
        whatWeDo="Co-Chair of C2PA Text Provenance Task Force. API and SDKs for cryptographic authentication with 100% accuracy. Standard publishes January 8, 2026."
        whoItsFor="Publishers needing provable content ownership. AI labs needing quote integrity verification. Enterprises requiring EU AI Act compliance."
        keyDifferentiator="Cryptographic watermarking survives copy-paste and distribution. Zero false positives. Enables content attribution and licensing."
        primaryValue="Building standards with NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others through C2PA (c2pa.org). Court-admissible proof, not statistical guessing."
      />

      {/* Hero Section */}
      <section className="relative w-full min-h-screen flex items-center justify-center overflow-hidden">
        <MetadataBackground />

        <div className="container mx-auto px-3 sm:px-4 py-12 sm:py-16 md:py-20 lg:py-28 relative z-10">
          <div className="max-w-4xl mx-auto text-center space-y-4 sm:space-y-6">
            <h1 className="text-2xl xs:text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-3 sm:mb-4 md:mb-6 text-shadow-md leading-tight px-2">
              Better Than AI Detectors: Cryptographic Proof
            </h1>
            <p className="text-sm xs:text-base sm:text-lg md:text-xl mb-4 sm:mb-6 md:mb-8 text-shadow-md max-w-3xl mx-auto leading-relaxed px-2">
              Stop guessing with 26% accurate AI detectors.<br />
              Start proving with 100% accurate cryptographic authentication via <Link href="/content-provenance" className="text-primary underline underline-offset-2 hover:no-underline">content provenance</Link>.<br />
              <strong>The difference? Detection guesses. Proof knows.</strong>
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
                <Link href="/solutions">
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

      {/* Why AI Detectors Fail */}
      <section className="py-20 w-full bg-muted/40 border-y border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Why AI Detectors Can't Be Trusted
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Statistical AI detection has fundamental flaws that cryptographic proof eliminates.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="bg-card p-6 rounded-lg border border-border">
              <TrendingDown className="h-10 w-10 text-destructive mb-4" />
              <h3 className="text-xl font-bold mb-3">26% Accuracy</h3>
              <p className="text-muted-foreground text-sm">
                Independent testing shows AI detectors correctly identify AI-generated content only <strong>26% of the time</strong>. That's worse than a coin flip. Would you trust your reputation on these odds?
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <XCircle className="h-10 w-10 text-destructive mb-4" />
              <h3 className="text-xl font-bold mb-3">False Positive Crisis</h3>
              <p className="text-muted-foreground text-sm">
                AI detectors flag <strong>authentic human-written content</strong> as AI-generated at alarming rates. Students get falsely accused. Writers lose jobs. Reputations suffer. One false positive is too many.
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <Search className="h-10 w-10 text-destructive mb-4" />
              <h3 className="text-xl font-bold mb-3">The Arms Race Problem</h3>
              <p className="text-muted-foreground text-sm">
                As AI generation improves, detection becomes impossible. It's pattern matching vs. pattern creation—detection will always lose. You need a fundamentally different approach.
              </p>
            </div>
          </div>

          {/* Real-World Impact */}
          <div className="mt-12 max-w-4xl mx-auto bg-destructive/5 border-2 border-destructive/20 rounded-lg p-8">
            <h3 className="text-2xl font-bold mb-4 text-center">Real-World Consequences</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <p className="font-semibold mb-2">For Publishers:</p>
                <p className="text-sm text-muted-foreground">
                  Can't enforce copyright. Litigation fails due to unreliable evidence. Revenue lost to AI companies using content without proof.
                </p>
              </div>
              <div>
                <p className="font-semibold mb-2">For Enterprises:</p>
                <p className="text-sm text-muted-foreground">
                  False positives damage employee trust. Legal exposure from wrongful accusations. Compliance requirements unmet.
                </p>
              </div>
              <div>
                <p className="font-semibold mb-2">For Platforms:</p>
                <p className="text-sm text-muted-foreground">
                  User complaints about false flags. Moderation chaos. Brand reputation risk from unreliable tools.
                </p>
              </div>
              <div>
                <p className="font-semibold mb-2">For Educators:</p>
                <p className="text-sm text-muted-foreground">
                  Students falsely accused. Appeals processes overwhelmed. Academic integrity policies undermined.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* The Better Approach */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Cryptographic Proof: The Superior Alternative
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Instead of analyzing content after creation, embed proof during creation.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 lg:gap-12 max-w-5xl mx-auto">
            {/* The Encypher Approach */}
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border">
              <h3 className="text-2xl font-bold mb-4">How Encypher Works Differently</h3>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">1</div>
                  <div>
                    <p className="font-semibold mb-1">Authentication at Creation</p>
                    <p className="text-sm text-muted-foreground">Cryptographic signatures embedded when content is generated—not analyzed after</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">2</div>
                  <div>
                    <p className="font-semibold mb-1">Mathematical Certainty</p>
                    <p className="text-sm text-muted-foreground">Proof based on cryptography, not statistical patterns. 100% accuracy, always.</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">3</div>
                  <div>
                    <p className="font-semibold mb-1">Zero False Positives</p>
                    <p className="text-sm text-muted-foreground">Authentic content never flagged incorrectly. Trust restored.</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">4</div>
                  <div>
                    <p className="font-semibold mb-1">Complete Audit Trail</p>
                    <p className="text-sm text-muted-foreground">Know exactly who created what, when, and what changed</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Benefits */}
            <div className="bg-primary/5 p-6 md:p-8 rounded-lg border-2 border-primary/20">
              <h3 className="text-2xl font-bold mb-4">What This Means for You</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">100% Accuracy Guaranteed</p>
                    <p className="text-sm text-muted-foreground">Mathematical proof eliminates guesswork</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">Zero False Positives</p>
                    <p className="text-sm text-muted-foreground">Never wrongly flag authentic content</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">Court-Admissible Evidence</p>
                    <p className="text-sm text-muted-foreground">Proof that stands up in legal proceedings</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">Future-Proof Solution</p>
                    <p className="text-sm text-muted-foreground">Cryptography doesn't degrade as AI improves</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">Complete Transparency</p>
                    <p className="text-sm text-muted-foreground">Full audit trail of content lifecycle</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Direct Comparison */}
      <section className="py-20 w-full bg-muted/40 border-y border-border">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            AI Detectors vs. Cryptographic Proof: Side-by-Side
          </h2>

          <div className="max-w-4xl mx-auto overflow-x-auto">
            <table className="w-full bg-card rounded-lg border border-border">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-4 font-semibold">Feature</th>
                  <th className="text-center p-4 font-semibold">AI Detectors</th>
                  <th className="text-center p-4 font-semibold bg-primary/5">Encypher</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-border">
                  <td className="p-4">Accuracy</td>
                  <td className="text-center p-4 text-destructive font-bold">26%</td>
                  <td className="text-center p-4 text-primary font-bold bg-primary/5">100%</td>
                </tr>
                <tr className="border-b border-border">
                  <td className="p-4">False Positives</td>
                  <td className="text-center p-4 text-destructive">High</td>
                  <td className="text-center p-4 text-primary font-semibold bg-primary/5">Zero</td>
                </tr>
                <tr className="border-b border-border">
                  <td className="p-4">Method</td>
                  <td className="text-center p-4">Statistical patterns</td>
                  <td className="text-center p-4 bg-primary/5">Cryptographic proof</td>
                </tr>
                <tr className="border-b border-border">
                  <td className="p-4">When Applied</td>
                  <td className="text-center p-4">After creation</td>
                  <td className="text-center p-4 font-semibold bg-primary/5">During creation</td>
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
                  <td className="text-center p-4">❌</td>
                  <td className="text-center p-4 bg-primary/5">✅</td>
                </tr>
                <tr>
                  <td className="p-4">Gets Better Over Time</td>
                  <td className="text-center p-4 text-destructive">❌ (Gets worse)</td>
                  <td className="text-center p-4 text-primary bg-primary/5">✅ (Math is constant)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Who Needs This */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Who Needs Better Than AI Detection
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            <div className="bg-card p-6 rounded-lg border border-border text-center">
              <h3 className="font-bold mb-2">Publishers</h3>
              <p className="text-sm text-muted-foreground">
                Prove copyright infringement with court-admissible evidence
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border text-center">
              <h3 className="font-bold mb-2">Enterprises</h3>
              <p className="text-sm text-muted-foreground">
                EU AI Act compliance without false positives
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border text-center">
              <h3 className="font-bold mb-2">Platforms</h3>
              <p className="text-sm text-muted-foreground">
                Content moderation with zero wrongful accusations
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border text-center">
              <h3 className="font-bold mb-2">AI Companies</h3>
              <p className="text-sm text-muted-foreground">
                Publisher compatibility and performance tracking
              </p>
            </div>
          </div>

          <div className="mt-12 text-center">
            <Button asChild size="lg" className="shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/solutions">
                Explore Solutions by Industry <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Standards Compliance */}
      <StandardsCompliance />

      {/* Final CTA */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Stop Guessing. Start Proving.
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            See how cryptographic authentication provides 100% accuracy with zero false positives - the certainty AI detectors can&apos;t deliver. Compare <Link href="/compare/encypher-vs-detection-tools" className="text-primary underline underline-offset-2 hover:no-underline">Encypher vs. detection tools</Link> directly.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center">
            <Button asChild size="lg" className="w-full sm:w-auto shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/demo">
                See Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              onClick={() => setShowContactModal(true)}
              size="lg"
              className="w-full sm:w-auto shadow-lg btn-blue-hover"
              style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}
            >
              Contact Sales <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>

      {/* Sales Contact Modal */}
      <AnimatePresence>
        {showContactModal && (
          <SalesContactModal
            onClose={() => setShowContactModal(false)}
            context="ai"
          />
        )}
      </AnimatePresence>
    </>
  );
}
