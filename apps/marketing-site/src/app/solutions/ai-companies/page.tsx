'use client';

import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import {
  ArrowRight,
  BarChart2,
  Zap,
  Shield,
  Award,
  BookOpen,
  TrendingUp,
  FileText,
  Network,
  ChevronDown,
} from 'lucide-react';
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
      <Script
        id="schema-faq-ai"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      {/* ------------------------------------------------------------------ */}
      {/* Hero                                                                */}
      {/* ------------------------------------------------------------------ */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            License Content at Scale. Prove You Did It Right.
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            AI companies that license publisher content through Encypher get three things at once:
            access to a growing publisher coalition, cryptographic proof of compliance for
            regulators, and performance intelligence that shows which content actually moves
            your product metrics. Built collaboratively through C2PA -- OpenAI, Google, Adobe,
            and Microsoft are members.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              asChild
              size="lg"
              className="font-semibold py-3 px-6 rounded-lg shadow-lg btn-blue-hover"
              style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}
            >
              <Link href="/ai-demo">
                Get Your Performance Intelligence Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              asChild
              size="lg"
              variant="outline"
              className="font-semibold py-3 px-6 rounded-lg shadow-lg"
            >
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

      {/* ------------------------------------------------------------------ */}
      {/* Value props (4 cards)                                               */}
      {/* ------------------------------------------------------------------ */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              One Integration. Four Compounding Benefits.
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Each benefit is valuable alone. Together they turn a compliance cost into
              a competitive moat.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 max-w-6xl mx-auto">
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border">
              <BarChart2 className="h-10 w-10 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-3">Performance Intelligence</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Track which outputs spread, which training sources correlate with better
                downstream engagement, and where your model performs vs. hallucinates.
                Data no competitor has.
              </p>
            </div>
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border">
              <Network className="h-10 w-10 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-3">Coalition Access</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                One agreement covers the entire publisher network. No bilateral negotiations
                per publisher. As the coalition grows, your licensed corpus grows with it
                automatically.
              </p>
            </div>
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border">
              <Shield className="h-10 w-10 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-3">Regulatory Compliance</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                EU AI Act Article 52(1) output disclosure, China watermarking mandate, and
                C2PA provenance -- all from the same API call. Stay compliant across
                jurisdictions as regulations evolve.
              </p>
            </div>
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border">
              <Award className="h-10 w-10 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-3">Licensed Content Mark</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Signal responsible content use to enterprise customers who ask about
                provenance in security questionnaires. Early adopters get a window
                to differentiate before this becomes table stakes.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* Analytics deep-dive                                                 */}
      {/* ------------------------------------------------------------------ */}
      <section className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              What the Data Actually Tells You
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Performance intelligence is not a dashboard you check once. It feeds back
              into training data selection, RAG corpus curation, and product decisions.
            </p>
          </div>
          <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-8">

            <div className="bg-card rounded-xl border border-border p-6 space-y-4">
              <div className="flex items-center gap-3">
                <TrendingUp className="h-7 w-7 text-primary flex-shrink-0" />
                <h3 className="text-lg font-semibold">Output Spread Analytics</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Every AI output you sign carries a C2PA manifest. When that output is
                copy-pasted, quoted in a blog post, or cited in a downstream document,
                Encypher records the provenance check. You see exactly which outputs
                spread and how far -- the real-world reach your internal evals cannot measure.
              </p>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Which response types get cited vs. corrected downstream
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Provenance check frequency by content category
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Spread velocity: how quickly outputs circulate after generation
                </li>
              </ul>
            </div>

            <div className="bg-card rounded-xl border border-border p-6 space-y-4">
              <div className="flex items-center gap-3">
                <BookOpen className="h-7 w-7 text-primary flex-shrink-0" />
                <h3 className="text-lg font-semibold">Training Source Performance</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Coalition publishers have signed content with C2PA metadata. When your
                RAG pipeline cites from that corpus, Encypher tracks which publishers
                contribute to outputs that get the strongest downstream engagement vs.
                those that generate correction signals. Use this to curate your corpus
                by verified signal, not gut feel.
              </p>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Per-publisher citation performance in your product
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Content category breakdown: news vs. analysis vs. research
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Data to drive coalition licensing renewal negotiations
                </li>
              </ul>
            </div>

            <div className="bg-card rounded-xl border border-border p-6 space-y-4">
              <div className="flex items-center gap-3">
                <FileText className="h-7 w-7 text-primary flex-shrink-0" />
                <h3 className="text-lg font-semibold">Quote Integrity Verification</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                When your model generates "According to Reuters..." Encypher can verify
                whether that citation matches a signed Reuters document. Catch hallucinated
                citations before they ship -- and create an audit log proving you made
                the check. This matters when enterprise customers demand citation accuracy
                guarantees in their SLAs.
              </p>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Automated pre-publish hallucination check on citations
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Similarity score vs. signed source document
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Audit log exportable for enterprise customer SLA reporting
                </li>
              </ul>
            </div>

            <div className="bg-card rounded-xl border border-border p-6 space-y-4">
              <div className="flex items-center gap-3">
                <Zap className="h-7 w-7 text-primary flex-shrink-0" />
                <h3 className="text-lg font-semibold">Compliance Audit Trail</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Every provenance verification creates a cryptographic log entry. When a
                regulator or enterprise customer asks "show me which content you licensed and
                when you verified it," you export a tamper-evident evidence package -- not
                a spreadsheet from your own servers. The proof is embedded in the content itself.
              </p>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Merkle-proof audit trail independent of Encypher infrastructure
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  EU AI Act Article 52(1) documentation built-in
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Exportable evidence packages for legal and security reviews
                </li>
              </ul>
            </div>

          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* Interactive Demo                                                    */}
      {/* ------------------------------------------------------------------ */}
      <section className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-8">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              See It In Action
            </h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto mb-4">
              Experience how performance intelligence transforms R&amp;D guesswork into
              data-driven optimization. This is a live, interactive demo.
            </p>
          </div>
          <div
            className="max-w-6xl mx-auto border-2 border-border rounded-xl shadow-2xl bg-card"
            style={{ maxHeight: '80vh', overflow: 'hidden', position: 'relative' }}
          >
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

      {/* ------------------------------------------------------------------ */}
      {/* How It Works                                                        */}
      {/* ------------------------------------------------------------------ */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              One Integration. Three Outcomes.
            </h2>
            <p className="text-lg md:text-xl mt-4 max-w-3xl mx-auto text-muted-foreground">
              License content legitimately, satisfy regulators, and show your users you
              take provenance seriously.
            </p>
          </div>
          <div className="max-w-3xl mx-auto">
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="item-1">
                <AccordionTrigger>Step 1: Connect to the Publisher Coalition</AccordionTrigger>
                <AccordionContent>
                  A single API integration connects you to Encypher&apos;s growing publisher
                  coalition. Licensing terms are established at the network level -- no
                  bilateral negotiations per publisher. Publishers set Bronze (indexing),
                  Silver (RAG / attribution), and Gold (training) tier terms. You access
                  the full catalog under one agreement. As the coalition grows, your
                  licensed corpus grows automatically.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-2">
                <AccordionTrigger>Step 2: Verify Provenance at Inference</AccordionTrigger>
                <AccordionContent>
                  When your model cites or uses publisher content, a single API call
                  verifies the C2PA watermark and records the provenance check. Latency
                  is under 50ms p99 at enterprise tier and can run async without blocking
                  your user response. This creates an auditable, cryptographic log of
                  licensed content use -- the documentation regulators, licensing agreements,
                  and enterprise security questionnaires require.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-3">
                <AccordionTrigger>Step 3: Compliance + Performance Intelligence</AccordionTrigger>
                <AccordionContent>
                  From the same integration: EU AI Act and China watermarking mandate
                  compliance for your AI-generated outputs, real-world spread analytics
                  showing which outputs get cited and which get corrected, and per-publisher
                  performance data to drive corpus curation decisions. Sign your AI outputs
                  at generation time -- even streaming responses -- and the C2PA manifest
                  travels with the content wherever it goes.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* Enterprise pricing                                                  */}
      {/* ------------------------------------------------------------------ */}
      <section className="py-16 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-4">
              Custom Enterprise Licensing
            </h2>
            <p className="text-lg text-muted-foreground mb-6">
              Annual licensing tailored to your scale. One integration covers the entire
              publisher ecosystem.
            </p>
            <div className="bg-card p-6 md:p-8 rounded-lg shadow-md border border-border mb-6">
              <ul className="space-y-3 text-left max-w-md mx-auto">
                <li className="flex items-center gap-3">
                  <BarChart2 className="h-5 w-5 text-primary flex-shrink-0" />
                  <span>Real-world performance analytics on all outputs</span>
                </li>
                <li className="flex items-center gap-3">
                  <Shield className="h-5 w-5 text-primary flex-shrink-0" />
                  <span>EU AI Act + China mandate compliant output watermarking</span>
                </li>
                <li className="flex items-center gap-3">
                  <Network className="h-5 w-5 text-primary flex-shrink-0" />
                  <span>Publisher coalition licensing -- one agreement, full network</span>
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

      {/* ------------------------------------------------------------------ */}
      {/* Standards                                                           */}
      {/* ------------------------------------------------------------------ */}
      <StandardsCompliance />

      {/* ------------------------------------------------------------------ */}
      {/* FAQ                                                                 */}
      {/* ------------------------------------------------------------------ */}
      <section className="py-20 w-full bg-muted/30 border-t border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Questions we hear from legal, engineering, and product teams at AI companies
              evaluating Encypher.
            </p>
          </div>
          <div className="max-w-3xl mx-auto">
            <Accordion type="single" collapsible className="w-full space-y-2">

              <AccordionItem value="faq-1" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  Do we need to negotiate with each publisher separately?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  No. The Encypher publisher coalition operates as a network license -- one
                  agreement with Encypher covers access to all coalition members at the tiers
                  each publisher has set (Bronze, Silver, Gold). You never negotiate directly
                  with individual publishers unless you want a custom bilateral arrangement
                  on top of the network agreement. As new publishers join the coalition,
                  your license extends to them automatically.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-2" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  We received a formal notice with an Encypher evidence package. What does that mean?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  The evidence package contains cryptographic proof that is independently
                  verifiable -- meaning it does not depend on trusting Encypher&apos;s
                  servers. The signature is embedded in the content itself, verified against
                  the publisher&apos;s own key. Your legal team should treat it as valid
                  documentation of when content was published, who authored it, and what
                  licensing tier it was marked for.
                  <br /><br />
                  The practical path forward is to join the coalition. The formal notice is
                  resolved as part of the licensing agreement -- the same publisher who sent
                  the notice becomes a licensed source. AI companies that resolve notices
                  this way typically complete the process within 60 days.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-3" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  Does provenance verification add latency to our inference pipeline?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  Verification is a single API call with under 50ms p99 latency at enterprise
                  tier. It can run asynchronously post-inference without blocking the user
                  response -- you fire the check, return the response, and record the result.
                  For highest throughput, the batch verification endpoint handles up to 10,000
                  documents per request. If you need zero-latency isolation, the C2PA
                  verification logic is available as an open-source library that runs entirely
                  within your own infrastructure.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-4" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  We may have fair use or training exemptions under US law. Why license?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  The legal landscape is unsettled and active litigation is ongoing. Licensing
                  is defensible regardless of how copyright law evolves -- it removes the
                  question entirely. More practically: enterprise customers are now asking
                  about content provenance in security questionnaires. AI companies that can
                  prove they license their content close deals that competitors cannot. The
                  "Verified Sources" product differentiator is already generating measurable
                  ARR for early adopters. Legal protection and competitive advantage are
                  both real; the legal exemption argument only addresses the first.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-5" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  How does this relate to robots.txt and noai directives?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  robots.txt and noai directives apply at crawl time, on the publisher&apos;s
                  server. C2PA provenance is embedded in the content itself -- it travels with
                  the text wherever it goes, including content that was already in your training
                  corpus before any crawl directive existed. A publisher who signs their archive
                  retroactively attaches licensing terms to every copy of that content, on any
                  server.
                  <br /><br />
                  Encypher is not an enforcement mechanism -- it is infrastructure that makes
                  licensing terms machine-readable and verifiable. robots.txt is the crawl
                  signal; C2PA is the content-level signal. Both have a role, but only C2PA
                  works after the content has already left the publisher&apos;s server.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-6" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  What data do you see from our inference calls?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  For verification calls: we receive the text submitted for verification
                  and return provenance metadata. We do not train on your data, do not retain
                  content beyond the verification transaction, and offer a standard data
                  processing agreement at enterprise tier.
                  <br /><br />
                  For performance intelligence: we record that a provenance check occurred,
                  the result (verified / not found), and the timestamp. We do not store the
                  full content of your AI-generated outputs unless you opt into spread
                  analytics, which requires explicit configuration.
                  <br /><br />
                  For highest isolation: C2PA verification is an open standard and the
                  verification logic can run entirely within your infrastructure using the
                  open-source C2PA libraries.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-7" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  Is this sufficient for EU AI Act compliance?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  Encypher&apos;s output watermarking is designed to satisfy Article 52(1)
                  transparency obligations -- the requirement that AI-generated content be
                  detectable as such. The C2PA manifest embedded in each output identifies
                  it as AI-generated, records the generation timestamp, and links to the
                  source model. This is the technical requirement as written.
                  <br /><br />
                  We are not a legal firm and regulations are still being interpreted.
                  You should confirm with your counsel that our implementation satisfies
                  your specific obligations in the jurisdictions where you operate. We can
                  provide technical documentation to support that review. The China
                  watermarking mandate is covered by the same integration under a separate
                  configuration flag.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-8" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  How does performance intelligence work if a publisher is not in the coalition yet?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  You can still verify content from publishers who have signed their content
                  independently -- C2PA is an open standard and any publisher can embed
                  provenance metadata using it. If the content carries a valid C2PA manifest,
                  Encypher can verify it and attribute it to the source, regardless of coalition
                  membership.
                  <br /><br />
                  For content without any C2PA watermark, verification returns "unsigned" --
                  which is itself a signal. Coalition membership adds the licensing agreement
                  layer; the provenance verification layer works on any signed content.
                </AccordionContent>
              </AccordionItem>

            </Accordion>
          </div>

          <div className="text-center mt-12">
            <p className="text-muted-foreground mb-4">Have a question not covered here?</p>
            <Button
              onClick={() => setShowContactModal(true)}
              variant="outline"
              size="lg"
              className="font-semibold"
            >
              Talk to the Team <ArrowRight className="ml-2 h-4 w-4" />
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
    </div>
  );
}
