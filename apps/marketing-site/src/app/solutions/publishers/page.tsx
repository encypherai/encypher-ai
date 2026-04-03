'use client';

import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@encypher/design-system';
import { ArrowRight, DollarSign, Scale, TrendingUp, CheckCircle2, AlertTriangle, Shield } from 'lucide-react';
import Link from 'next/link';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@encypher/design-system';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import AISummary from '@/components/seo/AISummary';
import SalesContactModal from '@/components/forms/SalesContactModal';
import Script from 'next/script';
import { publishersFaqSchema } from '@/lib/seo';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypher.com';

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
      <Script id="schema-faq-publishers" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(publishersFaqSchema) }} />
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
              <Link href={`${DASHBOARD_URL}/auth/signin?mode=signup&source=publishers`}>
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

      {/* No Engineering Required Section */}
      <section className="py-16 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-4">
                  No Engineering Staff Required
                </h2>
                <p className="text-muted-foreground mb-6">
                  Solo newsletter writer or 800-person newsroom - setup takes under 20 minutes using any publishing platform. Copy your API key, paste it in your CMS settings. Done.
                </p>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm"><strong>WordPress:</strong> Plugin available - one-click activation</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm"><strong>Ghost:</strong> Webhook integration - automatic signing on publish</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm"><strong>Substack &amp; Medium:</strong> Coming soon</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm"><strong>Custom CMS or archive:</strong> Python/TypeScript/Go/Rust SDK - batch-sign your entire back catalog</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm"><strong>Dashboard appears immediately:</strong> See every signed article and every external verification in real time</span>
                  </li>
                </ul>
              </div>
              <div className="bg-muted/30 p-6 rounded-lg border border-border">
                <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-5 text-center">Setup in 4 steps</p>
                <div className="space-y-3">
                  {[
                    'Sign up free (no credit card)',
                    'Copy your API key from dashboard',
                    'Paste into WordPress / Ghost / CMS settings',
                    'Publish your next article - signed automatically',
                  ].map((step, i) => (
                    <div key={i} className="flex items-center gap-3 text-sm">
                      <span className="h-7 w-7 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold flex-shrink-0">{i + 1}</span>
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-5 pt-4 border-t border-border text-center">
                  <p className="text-xs text-muted-foreground">Average setup time: under 20 minutes</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Legal Reality Section */}
      <section className="py-16 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-start gap-4 mb-8">
              <AlertTriangle className="h-8 w-8 text-amber-500 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-2">
                  The Legal Landscape Has Changed
                </h2>
                <p className="text-muted-foreground">
                  US copyright law distinguishes between innocent and <Link href="/cryptographic-watermarking/legal-implications" className="text-primary underline underline-offset-2 hover:no-underline">willful infringement</Link>. Cryptographic proof of ownership - and of when your content was published - directly affects which applies.
                </p>
              </div>
            </div>
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="bg-card p-6 rounded-lg border border-amber-200 dark:border-amber-900">
                <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-2">Without cryptographic proof</p>
                <p className="text-3xl font-bold mb-1">$30,000</p>
                <p className="text-sm text-muted-foreground">per work (innocent infringement)</p>
                <p className="text-sm mt-3 text-muted-foreground">
                  Hard to prove willful use. Defendant claims they did not know the content was protected.
                </p>
              </div>
              <div className="bg-card p-6 rounded-lg border border-primary">
                <p className="text-sm font-semibold text-primary uppercase tracking-wider mb-2">With Encypher watermarking</p>
                <p className="text-3xl font-bold mb-1">$150,000</p>
                <p className="text-sm text-muted-foreground">per work (willful infringement)</p>
                <p className="text-sm mt-3 text-muted-foreground">
                  Cryptographic evidence makes willful use mathematically demonstrable. Every sentence carries a tamper-evident signature.
                </p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground text-center">
              Note: Statutory damages reflect US Copyright Act maximums. Actual outcomes depend on specific facts and legal counsel. Encypher provides technical infrastructure, not legal advice.
            </p>
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

      {/* Bridge Value Section */}
      <section className="py-16 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-10">
              <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-4">
                See Which AI Companies Are Using Your Content - Free
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Your free dashboard shows every external verification event in real time. Licensing revenue builds over months - but you get proof of value from day one.
              </p>
            </div>
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <div className="bg-card p-5 rounded-lg border border-border">
                <Shield className="h-8 w-8 text-primary mb-3" />
                <h3 className="font-semibold mb-2">Day 1: Your Free Dashboard</h3>
                <p className="text-sm text-muted-foreground">
                  Every article you sign appears in your dashboard immediately. Each time an AI company checks your content&apos;s provenance, you see it - which company, which article, which day.
                </p>
              </div>
              <div className="bg-card p-5 rounded-lg border border-border">
                <TrendingUp className="h-8 w-8 text-primary mb-3" />
                <h3 className="font-semibold mb-2">$299/mo: Attribution Analytics</h3>
                <p className="text-sm text-muted-foreground">
                  When you want the full picture: detailed breakdown by entity, date, and content category. At 500 verifications you qualify to issue Formal Notice - Analytics shows you exactly when you hit that threshold.
                </p>
              </div>
              <div className="bg-card p-5 rounded-lg border border-border">
                <DollarSign className="h-8 w-8 text-primary mb-3" />
                <h3 className="font-semibold mb-2">500+ Verifications: Enforce</h3>
                <p className="text-sm text-muted-foreground">
                  Issue Formal Notice ($499) to companies using your content without a license. After notice, any continued use becomes willful infringement. Many publishers find notice opens licensing talks.
                </p>
              </div>
            </div>
            <p className="text-sm text-center text-muted-foreground">
              You control the timeline. See evidence. Upgrade when ready. Enforce when it makes sense.
            </p>
          </div>
        </div>
      </section>

      {/* Rights + Revenue Section */}
      <section className="py-16 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-10">
              <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-4">
                Set Your Licensing Rules. You Approve Every Deal.
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Granular content licensing is not managed manually - you set rules once in your rights profile, and Encypher enforces them cryptographically. Licensing requests flow into your dashboard for review and approval.
              </p>
            </div>
            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div className="bg-card p-6 rounded-lg border border-border">
                <h3 className="font-semibold mb-4">Example Rights Profile</h3>
                <div className="bg-muted/30 p-4 rounded-lg border border-border font-mono text-xs space-y-3">
                  <div>
                    <span className="text-amber-700 dark:text-amber-500 font-semibold">Bronze (crawling):</span>
                    <p className="text-muted-foreground mt-1">Permitted - search indexing fine</p>
                  </div>
                  <div>
                    <span className="text-zinc-500 dark:text-zinc-300 font-semibold">Silver (RAG/citation):</span>
                    <p className="text-muted-foreground mt-1">Permitted - author name + canonical URL required</p>
                  </div>
                  <div>
                    <span className="text-yellow-600 dark:text-yellow-400 font-semibold">Gold (training):</span>
                    <p className="text-muted-foreground mt-1">License required - contact licensing@yourorg.com</p>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-3">
                  Set in minutes. AI companies discover your terms automatically via C2PA provenance. No manual negotiation needed for Silver-tier access.
                </p>
              </div>
              <div className="bg-card p-6 rounded-lg border border-border">
                <h3 className="font-semibold mb-4">Example: First 6 Months</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex gap-3">
                    <span className="text-muted-foreground w-20 flex-shrink-0">Month 1-2</span>
                    <span>Archive signed, monitoring begins. Dashboard shows external verifications accumulating.</span>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-muted-foreground w-20 flex-shrink-0">Month 3</span>
                    <span>First Gold-tier licensing request. AI company licenses archive access. First revenue.</span>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-muted-foreground w-20 flex-shrink-0">Month 4-6</span>
                    <span>Coalition grows. Additional licensing deals compound. Monthly recurring revenue stabilizes.</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground pt-3 border-t border-border mt-3">
                  Results vary by content volume, market value, and coalition deal flow. Majority of licensing revenue goes to publishers.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-16 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-4 text-center">
              Start Free. Upgrade When You See Results.
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
                    <span>Encypher Patent-Pending Tech + C2PA</span>
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
              Protection From Day One
            </h2>
            <p className="text-lg md:text-xl mt-4 max-w-3xl mx-auto text-muted-foreground">
              Unlike models that require opt-in licensing deals before protection begins, Encypher protects content at the moment of publication. Your rights documentation starts accumulating on day one.
            </p>
          </div>
          <div className="max-w-3xl mx-auto">
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="item-0">
                <AccordionTrigger>Step 0: Protect Your Archive (One-Time Foundation)</AccordionTrigger>
                <AccordionContent>
                  Sign your entire content library - 500 articles or 500,000 - using our bulk signing API. The Python SDK lets you sign your full archive in a single overnight job. This is a one-time investment that converts your existing content into a provably owned corpus. Every article becomes a citable asset in any licensing or enforcement conversation. Free tier covers 1,000 docs/month; overage is fractions of a cent per document.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-1">
                <AccordionTrigger>Step 1: Automatic Signing at Publication</AccordionTrigger>
                <AccordionContent>
                  All new articles are watermarked at the moment you hit publish. Integrate via the WordPress plugin, Ghost webhook, or the REST API. No manual steps for your editorial team - protection begins automatically. Each article carries an invisible, tamper-evident cryptographic signature embedded at the sentence level.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-2">
                <AccordionTrigger>Step 2: Dashboard - See Who Is Using Your Content</AccordionTrigger>
                <AccordionContent>
                  Your free dashboard shows every external verification event: which AI companies are checking your content&apos;s provenance, how often, and which articles. When you reach 500 verifications, you qualify to issue Formal Notice. Upgrade to Attribution Analytics ($299/mo) for detailed breakdown by entity, date, and content category.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-3">
                <AccordionTrigger>Step 3: Enforce and License</AccordionTrigger>
                <AccordionContent>
                  Use your evidence package to issue Formal Notice to AI companies using your content without a license. After notice, any continued use is willful infringement - a meaningfully higher legal threshold. Many publishers find that formal notice opens licensing negotiations rather than litigation. Coalition licensing deals flow in as the network grows - approved in your dashboard, paid monthly.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-4">
                <AccordionTrigger>Bonus: Quote Integrity for Editorial QA</AccordionTrigger>
                <AccordionContent>
                  If your team uses AI-assisted writing or research tools, the Quote Integrity API helps catch hallucinated citations before publication. Submit any quote and attribution - the API checks whether the cited source actually contains that language. Used by editorial teams as a standard pre-publication check for AI-assisted drafts.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </div>
      </section>
      {/* FAQ Section */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Frequently Asked Questions
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-2xl mx-auto">
              Common questions from publishers before they get started.
            </p>
          </div>
          <div className="max-w-3xl mx-auto">
            <Accordion type="single" collapsible className="space-y-2">
              {[
                {
                  q: 'Will my content look different to readers?',
                  a: 'No. The cryptographic watermark is completely invisible. It is embedded using zero-width Unicode characters between words - characters that are present in the text but invisible to the human eye. Your readers, your fonts, and your layout are not affected in any way.',
                },
                {
                  q: 'Will this slow down my website?',
                  a: 'No. Signing happens server-side at publish time, not on page load. Once an article is signed, there is no additional overhead for readers or for your site. The signed content is stored exactly as you published it.',
                },
                {
                  q: 'Who gets the licensing revenue?',
                  a: 'The majority goes to you, the publisher. When an AI company licenses your content through the Encypher Coalition, the split strongly favors publishers - the same split regardless of whether you are on a free or paid plan. We publish the revenue share terms transparently. Encypher takes a small platform fee.',
                },
                {
                  q: 'Do I need a lawyer to issue a formal notice?',
                  a: "No. Encypher generates the formal notice package automatically from your evidence - a cryptographically-backed letter that you can send directly, or forward to counsel. Many publishers find that receiving a notice is enough to open licensing talks. If it escalates, your lawyer will have everything they need: a complete evidence chain, tamper-evident delivery confirmation, and documentation in standard litigation support formats. You don't need a lawyer to start - but the package is designed to meet one's requirements when you do.",
                },
                {
                  q: 'What if AI companies just ignore the rights terms?',
                  a: 'Ignoring machine-readable rights terms that are embedded in every document is what converts innocent infringement into willful infringement under US copyright law. Willful infringement carries statutory damages up to $150,000 per work vs. $30,000 for innocent infringement. EU AI Act compliance (effective August 2026) also requires AI providers to respect machine-readable rights reservations. The terms do not need to be actively accepted - publishing them and embedding them in the content is sufficient to establish they were available.',
                },
                {
                  q: 'Can I sign content from years ago?',
                  a: 'Yes. You can backfill your entire archive using the Encypher API or our SDK batch tools. The Python and TypeScript SDKs let you sign thousands of articles in a single overnight job. The free tier covers 1,000 documents per month; volume pricing is available for large archives. We recommend starting with your most valuable evergreen content - the articles most likely to appear in AI training datasets.',
                },
                {
                  q: 'What happens if I stop using Encypher?',
                  a: 'All content you signed remains signed - permanently. The cryptographic signatures are embedded in the text itself and do not depend on Encypher servers to remain valid. The free tier will always exist at $0. If you stop a paid plan, you keep the signing infrastructure and your signed archive. You just lose access to the paid analytics and enforcement tools until you re-subscribe.',
                },
                {
                  q: 'Is my content stored on Encypher servers?',
                  a: 'No. Encypher signs your content at the moment of publication and returns it to your CMS. We store metadata and cryptographic hashes (fingerprints) for verification purposes - not the full text of your articles. Your content stays on your servers. We can verify a piece of text is yours using the hash without needing a copy of the original.',
                },
              ].map((faq, i) => (
                <AccordionItem
                  key={i}
                  value={`publisher-faq-${i}`}
                  className="bg-card border border-border rounded-lg px-6"
                >
                  <AccordionTrigger className="text-left font-medium py-5 hover:no-underline">
                    {faq.q}
                  </AccordionTrigger>
                  <AccordionContent className="text-sm text-muted-foreground pb-5 leading-relaxed">
                    {faq.a}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>
        </div>
      </section>

      <StandardsCompliance />

      {/* Final CTA */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Start Protecting Your Content Today
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            Free signing infrastructure. See which AI companies are using your content from day one.
            Enforcement tools available when you are ready. Read the full <Link href="/content-provenance/for-publishers" className="text-primary underline underline-offset-2 hover:no-underline">publisher content provenance guide</Link>.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold py-3 px-6 rounded-lg shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/publisher-demo">
                Get Your Content Protection Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="font-semibold py-3 px-6 rounded-lg">
              <Link href={`${DASHBOARD_URL}/auth/signin?mode=signup&source=publishers`}>
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
