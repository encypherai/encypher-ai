'use client';

import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@encypher/design-system';
import {
  ArrowRight,
  Shield,
  FileCheck,
  AlertTriangle,
  CheckCircle2,
  Key,
  Scale,
  FileText,
  Search,
  Lock,
} from 'lucide-react';
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
import { enterprisesFaqSchema } from '@/lib/seo';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypher.com';

export default function EnterprisePage() {
  const [showContactModal, setShowContactModal] = useState(false);

  return (
    <div className="bg-background text-foreground">
      <Script
        id="schema-faq-enterprises"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(enterprisesFaqSchema) }}
      />
      <AISummary
        title="Encypher for Enterprise Governance"
        whatWeDo="Authors of C2PA Section A.7. Patent-pending API and SDKs for sentence-level document provenance. Cryptographic proof of which passages were AI-generated, AI-assisted, or human-written - exportable as tamper-evident evidence packages."
        whoItsFor="Law firms, consulting firms, financial services, and regulated enterprises that produce documents where AI provenance is legally or professionally significant."
        keyDifferentiator="Sentence-level Merkle tree authentication. Prove exactly which paragraph was AI-generated on which date by which model - independently verifiable without trusting Encypher."
        primaryValue="Turn AI governance from a policy document into cryptographic proof. Court-ready evidence packages. BYOK for attorney-client privilege."
      />

      {/* ------------------------------------------------------------------ */}
      {/* Hero                                                                */}
      {/* ------------------------------------------------------------------ */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            Know Exactly What AI Wrote.<br />Prove It.
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            Law firms, consulting firms, and regulated enterprises face a new question on
            every document: which sentences came from AI, which came from humans, and
            which were AI-drafted then edited? An AI policy does not answer that question.
            <Link href="/content-provenance" className="text-primary underline underline-offset-2 hover:no-underline">Cryptographic content provenance</Link> does.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              onClick={() => setShowContactModal(true)}
              size="lg"
              className="font-semibold"
            >
              Schedule Architecture Review <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href={`${DASHBOARD_URL}/auth/signin?mode=signup&source=enterprises`}>
                Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="ghost" size="lg">
              <Link href="/try">
                See It Live <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* The gap between policy and proof                                    */}
      {/* ------------------------------------------------------------------ */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              The Gap Between Policy and Proof
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Most organizations have an AI use policy. Almost none can prove
              what that policy produced on a specific document.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="bg-destructive/5 border-2 border-destructive/20 p-8 rounded-lg">
              <AlertTriangle className="h-10 w-10 text-destructive mb-4" />
              <h3 className="text-xl font-bold mb-4">What "We Have a Policy" Cannot Do</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-destructive rounded-full mt-2 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-sm">Answer a court order</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Federal courts are requiring attorneys to certify AI use. A policy
                      memo does not satisfy a signed certification requirement.
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-destructive rounded-full mt-2 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-sm">Identify which paragraph was hallucinated</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      If opposing counsel or a regulator challenges a specific citation,
                      you need sentence-level proof, not an attestation that "AI may have
                      been used."
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-destructive rounded-full mt-2 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-sm">Prove retroactively</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Without provenance embedded at creation time, any claim about
                      a document's origin is unverifiable - and therefore contestable.
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-destructive rounded-full mt-2 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-sm">Protect against internal dispute</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      When a client asks "did your team use AI on this engagement," a
                      policy cannot tell you what actually happened on a specific deliverable.
                    </p>
                  </div>
                </li>
              </ul>
            </div>

            <div className="bg-primary/5 border-2 border-primary/20 p-8 rounded-lg">
              <Shield className="h-10 w-10 text-primary mb-4" />
              <h3 className="text-xl font-bold mb-4">What Cryptographic Provenance Does</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-sm">Marks provenance at creation</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Every AI-generated or AI-assisted passage is signed with model
                      metadata, timestamp, and author at the moment it is produced --
                      not reconstructed later.
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-sm">Sentence-level Merkle tree</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Each sentence has independent cryptographic proof. You can show
                      that paragraph 4 was AI-generated while paragraphs 1-3 and 5
                      were human-authored.
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-sm">Tamper-evident export</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Evidence packages are independently verifiable - the proof is
                      embedded in the document itself, not on Encypher's servers.
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-sm">Detects post-signing modification</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Any change to a signed passage is cryptographically recorded.
                      You can prove a section was edited after signing, and by whom.
                    </p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* Use cases                                                           */}
      {/* ------------------------------------------------------------------ */}
      <section className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              Where Provenance Proof Is Required
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              The question is no longer hypothetical. Courts, regulators, and clients
              are asking for documentation that standard AI governance frameworks
              cannot produce.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">

            <div className="bg-card rounded-xl border border-border p-6 space-y-4">
              <div className="flex items-center gap-3">
                <Scale className="h-7 w-7 text-primary flex-shrink-0" />
                <h3 className="text-lg font-semibold">Law Firms</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Federal and state courts are issuing standing orders requiring attorneys
                to certify AI use in filings. Bar associations are publishing ethics guidance
                on disclosure obligations. Attorneys using AI assistants (Harvey, Westlaw AI,
                Copilot) need to certify not just "AI may have been used" but which specific
                passages - and that those passages were reviewed.
              </p>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Court filing certification: paragraph-level AI attribution
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Malpractice defense: prove which citations were AI-generated vs. attorney-verified
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Sanctions defense: evidence that AI output was reviewed before filing
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Client billing documentation: distinguish AI-assisted from attorney work
                </li>
              </ul>
            </div>

            <div className="bg-card rounded-xl border border-border p-6 space-y-4">
              <div className="flex items-center gap-3">
                <FileText className="h-7 w-7 text-primary flex-shrink-0" />
                <h3 className="text-lg font-semibold">Consulting and Advisory Firms</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Enterprise clients - especially in regulated industries - are adding AI
                disclosure requirements to engagement terms. A strategy memo or due diligence
                report that contains AI-synthesized sections without disclosure creates
                professional liability. Firms need to demonstrate exactly what was
                AI-produced and what was partner-level analysis.
              </p>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Client deliverable provenance on request
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  M&A due diligence: which synthesis was AI, which was analyst judgment
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Engagement audit trail for regulatory review
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Professional standards compliance (AICPA, CFA, etc.)
                </li>
              </ul>
            </div>

            <div className="bg-card rounded-xl border border-border p-6 space-y-4">
              <div className="flex items-center gap-3">
                <Search className="h-7 w-7 text-primary flex-shrink-0" />
                <h3 className="text-lg font-semibold">Financial Services</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                SEC guidance requires disclosure of AI use in filings. Research reports,
                prospectuses, and regulatory submissions that use AI-generated content
                without provenance documentation create material risk. Financial firms
                need an audit trail that satisfies both internal compliance and external
                regulatory review.
              </p>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  SEC filing AI disclosure documentation
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Research report provenance for analyst certification
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Internal audit trail for AI governance frameworks (SR 11-7 equivalent)
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  <Link href="/content-provenance/eu-ai-act" className="text-primary underline underline-offset-2 hover:no-underline">EU AI Act</Link> compliance for customer-facing AI outputs
                </li>
              </ul>
            </div>

            <div className="bg-card rounded-xl border border-border p-6 space-y-4">
              <div className="flex items-center gap-3">
                <FileCheck className="h-7 w-7 text-primary flex-shrink-0" />
                <h3 className="text-lg font-semibold">Enterprise Legal and Compliance</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                General counsel and compliance teams at large enterprises face a
                discovery problem: when litigation or regulatory investigation touches
                internal documents, they need to produce provenance information that
                currently does not exist. Signing documents at creation builds that
                record before it is needed.
              </p>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  e-Discovery: identify AI-generated content in document review
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Contract lifecycle: prove which clauses were AI-drafted vs. negotiated
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  Board reporting: accurate AI usage disclosure in governance reports
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">+</span>
                  HR and policy documents: provenance audit for internal investigations
                </li>
              </ul>
            </div>

          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* How it works                                                        */}
      {/* ------------------------------------------------------------------ */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              How Sentence-Level Provenance Works
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Provenance is embedded at creation time, not reconstructed later.
              The proof travels with the document wherever it goes.
            </p>
          </div>
          <div className="max-w-3xl mx-auto">
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="step-1">
                <AccordionTrigger>Step 1: Sign at Creation</AccordionTrigger>
                <AccordionContent>
                  When your AI assistant generates a passage - or when an attorney
                  or analyst writes one - the document is signed via the Encypher API.
                  The <Link href="/c2pa-standard/implementation-guide" className="text-primary underline underline-offset-2 hover:no-underline">C2PA</Link> manifest records: who signed, at what time, whether the
                  content was AI-generated or human-authored, and which model produced it
                  (if AI). This happens at the moment of production, not retroactively.
                  <br /><br />
                  Encypher embeds the provenance metadata as invisible Unicode characters
                  woven between the text. The document looks identical to readers.
                  The metadata is machine-readable and cryptographically bound to
                  the specific content.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="step-2">
                <AccordionTrigger>Step 2: Sentence-Level Merkle Tree</AccordionTrigger>
                <AccordionContent>
                  Unlike document-level signing (which only tells you the whole document
                  was signed at some point), Encypher builds a Merkle tree at the
                  sentence level. Each sentence is an independent node.
                  <br /><br />
                  This means you can prove: "Paragraph 4, sentences 2 and 3 were
                  generated by GPT-4o on March 15, 2026 at 14:32 UTC. Sentences 1
                  and 4 were written by J. Smith on March 16, 2026. All sentences
                  are unmodified since signing." Each claim is independently verifiable
                  without checking the others.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="step-3">
                <AccordionTrigger>Step 3: Export a Tamper-Evident Evidence Package</AccordionTrigger>
                <AccordionContent>
                  When provenance needs to be produced - for a court certification,
                  regulatory inquiry, client request, or internal audit - Encypher
                  exports a tamper-evident evidence package containing:
                  <br /><br />
                  - SHA-256 hash of each signed passage<br />
                  - Merkle proof linking each passage to the root manifest<br />
                  - Timestamp chain (when each passage was created and by whom)<br />
                  - Model metadata for AI-generated passages<br />
                  - Modification log (any edits made after signing)
                  <br /><br />
                  The proof is independently verifiable using the C2PA open standard --
                  it does not depend on Encypher's infrastructure being trusted.
                  The signature is against your organization's own key.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* BYOK section                                                        */}
      {/* ------------------------------------------------------------------ */}
      <section className="py-16 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-start gap-4 mb-8">
              <Key className="h-8 w-8 text-primary flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-2">
                  BYOK: Your Keys. Your Infrastructure.
                </h2>
                <p className="text-muted-foreground leading-relaxed">
                  For law firms and regulated enterprises, attorney-client privilege and
                  data residency requirements mean you cannot send document content to
                  a third party's signing service. Encypher's BYOK model addresses this:
                  your organization registers its own Ed25519 public key, and all signing
                  uses your key. Encypher provides the infrastructure; your key material
                  never leaves your environment.
                </p>
              </div>
            </div>
            <div className="grid md:grid-cols-3 gap-6 mb-6">
              <div className="bg-card p-5 rounded-lg border border-border text-center">
                <Lock className="h-6 w-6 text-primary mx-auto mb-2" />
                <p className="text-sm font-semibold mb-1">Key custody stays with you</p>
                <p className="text-xs text-muted-foreground">
                  Encypher never stores, transmits, or accesses your key material.
                  HSM, AWS KMS, Azure Key Vault supported.
                </p>
              </div>
              <div className="bg-card p-5 rounded-lg border border-border text-center">
                <Shield className="h-6 w-6 text-primary mx-auto mb-2" />
                <p className="text-sm font-semibold mb-1">Independently verifiable</p>
                <p className="text-xs text-muted-foreground">
                  C2PA assertions embed your certificate. Anyone can verify
                  the signature against your public key without trusting Encypher.
                </p>
              </div>
              <div className="bg-card p-5 rounded-lg border border-border text-center">
                <FileCheck className="h-6 w-6 text-primary mx-auto mb-2" />
                <p className="text-sm font-semibold mb-1">Data residency compatible</p>
                <p className="text-xs text-muted-foreground">
                  Signing can run within your infrastructure. Document content
                  does not need to leave your environment.
                </p>
              </div>
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
              Questions from legal, compliance, and IT teams at law firms and
              regulated enterprises evaluating Encypher.
            </p>
          </div>

          <div className="max-w-3xl mx-auto">
            <Accordion type="single" collapsible className="w-full space-y-2">

              <AccordionItem value="faq-1" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  Does Encypher satisfy court AI disclosure requirements?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  Court AI disclosure orders vary significantly by jurisdiction and judge.
                  Most require attorneys to certify that AI-generated content was reviewed
                  and that citations were verified - they do not specify the technical
                  mechanism. Encypher provides the provenance record that supports such
                  a certification: which passages were AI-generated, when, by which model,
                  and that the document is unmodified since signing.
                  <br /><br />
                  We are not a law firm and this is not legal advice. You should confirm
                  with ethics counsel that your implementation satisfies the specific orders
                  in your jurisdictions. We can provide technical documentation describing
                  what the provenance record contains and how it can be exported.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-2" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  How does paragraph-level signing work in a real drafting workflow?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  The typical integration is through your AI drafting tool or document
                  management system. When an AI assistant generates a passage, the
                  output is signed via the Encypher API before it is inserted into the
                  document - the manifest records the model, timestamp, and generation
                  context. When an attorney writes a passage, it can be signed as
                  human-authored with the attorney&apos;s credentials.
                  <br /><br />
                  For existing workflows, Encypher also supports batch signing of
                  completed documents - though this produces a document-level signature
                  rather than sentence-level provenance. The strongest provenance comes
                  from signing at the point of generation, not retroactively.
                  <br /><br />
                  Integration points: REST API, Python and TypeScript SDKs, Word/Google
                  Docs add-in (available on request), and webhook-based CMS integrations.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-3" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  If an attorney edits an AI-generated paragraph, what does the record show?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  The record shows both events. The original AI-generated passage has its
                  own signed manifest (model, timestamp, generation context). When the
                  attorney edits and re-signs, the updated passage carries the attorney&apos;s
                  credentials and a new timestamp - with the prior AI-generation manifest
                  preserved in the chain.
                  <br /><br />
                  This gives you a precise answer to "was this passage AI-generated?":
                  yes, originally, and here is the original AI output; and yes, it was
                  subsequently reviewed and edited by J. Smith on this date, and here is
                  what changed. The modification log is tamper-evident.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-4" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  Can opposing counsel or regulators independently verify the provenance claims?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  Yes - and this is a deliberate design property. The C2PA standard is
                  open and the verification libraries are open source. Any party with
                  the signed document and your organization&apos;s public key can
                  independently verify every provenance claim without Encypher&apos;s
                  involvement.
                  <br /><br />
                  With BYOK, the signature is against your own certificate. Encypher
                  is not in the verification chain - you are. This matters in adversarial
                  contexts where a party might argue the provenance record is
                  self-serving or could have been manufactured. An independently
                  verifiable cryptographic signature from your own key is much harder
                  to contest than a declaration from a vendor.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-5" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  Does Encypher see the content of our documents?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  In the standard API integration, document content passes through
                  Encypher&apos;s signing service to have provenance metadata embedded.
                  We do not store, train on, or use document content beyond the signing
                  transaction. Enterprise customers receive a standard data processing
                  agreement.
                  <br /><br />
                  For the highest isolation - appropriate for matters with strict
                  attorney-client privilege or data residency requirements - Encypher
                  supports on-premises deployment and BYOK configurations where signing
                  runs entirely within your infrastructure. In this configuration,
                  document content never leaves your environment. Contact us to discuss
                  the architecture for your requirements.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-6" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  How does this integrate with Word, Google Docs, or our DMS?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  Encypher provides a REST API and SDKs (Python, TypeScript) that can
                  be integrated into any document workflow. For common document
                  management systems (iManage, NetDocuments, SharePoint), integration
                  is typically built at the document save or export event - when a
                  document is finalized, it is signed and the evidence package is
                  stored alongside the document.
                  <br /><br />
                  For real-time sentence-level provenance, the integration is at the
                  AI drafting tool level - connecting the AI output to the signing
                  API before it enters the document. Word and Google Docs add-ins
                  that support this workflow are available for enterprise customers.
                  Contact us to discuss your specific DMS and AI tooling environment.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="faq-7" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-left font-medium">
                  What happens if we need to prove provenance for documents created before we integrated Encypher?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  Retroactive signing is possible but produces a different - and weaker --
                  type of proof. A document signed today carries a timestamp of today,
                  regardless of when it was created. This proves the document&apos;s
                  current state is unchanged since today&apos;s signing, not that
                  it was created on a prior date.
                  <br /><br />
                  For documents that already exist, the realistic options are: (1) sign
                  them now to establish a baseline of their current state, or (2) rely
                  on other evidence (email chains, version history, system logs) to
                  establish prior provenance. Encypher does not help with retroactive claims.
                  <br /><br />
                  This is why signing at creation is the correct approach - the value
                  of provenance proof is built prospectively, before it is needed.
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

      {/* ------------------------------------------------------------------ */}
      {/* Final CTA                                                           */}
      {/* ------------------------------------------------------------------ */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Build the Record Before You Need It
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            The time to establish document provenance is at creation, not during
            litigation or regulatory review. Schedule a technical architecture
            review to see how Encypher fits your document workflow and governance
            requirements.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              onClick={() => setShowContactModal(true)}
              size="lg"
              className="font-semibold"
            >
              Schedule Architecture Review <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/try">
                See It Live in 30 Seconds <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Sales Contact Modal */}
      <AnimatePresence>
        {showContactModal && (
          <SalesContactModal
            onClose={() => setShowContactModal(false)}
            context="enterprise"
          />
        )}
      </AnimatePresence>
    </div>
  );
}
