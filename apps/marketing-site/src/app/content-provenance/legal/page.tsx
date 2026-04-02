import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { getVerticalMetadata } from '@/lib/seo';
import type { Metadata } from 'next';

export const metadata: Metadata = getVerticalMetadata(
  'legal',
  'Content Provenance for Legal Practice | Encypher',
  'Cryptographic document provenance for evidence integrity, formal notice requirements, court admissibility, and AI disclosure obligations. Built for law firms and legal departments managing AI content authentication challenges.',
  'Document provenance for evidence integrity and AI disclosure.'
);

export default function LegalPage() {
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'Is a C2PA manifest admissible as evidence of document authenticity in court?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'C2PA manifests use standard cryptographic signing (COSE with X.509 certificates) and RFC 3161 timestamps from trusted timestamping authorities. This is the same infrastructure used in qualified electronic signatures in many jurisdictions. Whether a specific manifest constitutes admissible evidence of authenticity depends on the jurisdiction, the signing certificate chain, and the integrity of the verification chain. Encypher provides the technical infrastructure. Legal practitioners should evaluate admissibility for their specific jurisdiction and use case.',
        },
      },
      {
        '@type': 'Question',
        name: 'How does embedded provenance support formal notice in AI copyright disputes?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Embedded provenance functions as constructive notice. Content with a C2PA manifest carries machine-readable rights metadata identifying the owner and stating licensing terms. A party that received content with that manifest cannot credibly claim it was unaware of the ownership claim. For AI copyright disputes, this eliminates the "we did not know it was owned" defense and supports a willful infringement argument, which affects the damages calculation significantly under US copyright law.',
        },
      },
      {
        '@type': 'Question',
        name: 'Can provenance help law firms authenticate AI-generated documents in discovery?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Yes. In civil discovery, authenticating AI-generated documents and distinguishing them from human-authored documents is an emerging challenge. Content provenance provides a technical mechanism: documents signed with Encypher carry a manifest that records whether they were AI-generated, human-authored, or a combination. The manifest is cryptographically bound to the document content and cannot be altered without breaking the signature. This provides authentication evidence that is harder to fabricate than metadata alone.',
        },
      },
      {
        '@type': 'Question',
        name: 'What are the AI disclosure obligations for law firms under current professional rules?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Professional responsibility rules on AI disclosure are evolving rapidly. Several state bars have issued guidance requiring disclosure of AI use in client communications and court filings. Some courts now require explicit disclosure of AI assistance in briefs. Content provenance provides documentation infrastructure that law firms can use to demonstrate compliance: each document signed with Encypher carries a machine-readable record of its AI authorship status, creating an audit trail for professional responsibility purposes.',
        },
      },
    ],
  };

  return (
    <>
      <AISummary
        title="Content Provenance for Legal Practice"
        whatWeDo="Encypher provides cryptographic content provenance infrastructure for legal documents, evidence files, court filings, and client communications. C2PA manifests embedded in documents create tamper-evident authentication records that support evidence integrity, formal notice arguments, and AI disclosure compliance."
        whoItsFor="Law firms, corporate legal departments, e-discovery platforms, and legal technology providers. Specifically suited to practices managing AI copyright litigation, discovery involving AI-generated documents, and compliance with AI disclosure obligations in court filings and client communications."
        keyDifferentiator="Cryptographic signing using X.509 certificates and RFC 3161 timestamps, the same infrastructure used in qualified electronic signatures. Document-level provenance for PDFs and other legal document formats. Segment-level text provenance for distinguishing AI-generated from human-authored content within a document."
        primaryValue="Evidence integrity for legal documents. Formal notice documentation in AI copyright disputes. Authentication of AI-generated documents in discovery. Professional responsibility compliance infrastructure for law firms using AI in client work."
        pagePath="/content-provenance/legal"
        pageType="WebPage"
      />

      <Script
        id="faq-legal"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <ArticleShell path="/content-provenance/legal">
        <Breadcrumbs
          items={[
            { name: 'Home', href: '/' },
            { name: 'Content Provenance', href: '/content-provenance' },
            { name: 'Legal', href: '/content-provenance/legal' },
          ]}
        />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Content Provenance for Legal Practice
        </h1>
        <p className="text-lg text-muted-foreground mb-8">
          Cryptographic document authentication, evidence provenance, formal notice infrastructure,
          and AI disclosure compliance for law firms and legal departments.
        </p>

        {/* Evidence provenance */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Evidence Provenance and Document Integrity</h2>
          <p className="text-base leading-relaxed mb-4">
            Legal proceedings increasingly involve digital documents whose authenticity is disputed.
            Screenshots, emails, contracts, and communications can be fabricated or altered. The
            standard response - metadata examination, file system analysis - is insufficient when
            a sophisticated adversary has anticipated forensic review.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Content provenance adds a layer that is harder to fabricate. A document signed with
            Encypher carries a C2PA manifest that is cryptographically bound to its content via
            hash. Any alteration to the document breaks the signature. The manifest includes an
            RFC 3161 timestamp from a trusted timestamping authority, which provides evidence of
            when the document existed in its signed state.
          </p>
          <p className="text-base leading-relaxed">
            For legal practitioners who need to preserve the authenticity of evidence at collection,
            Encypher provides a mechanism to sign documents at the moment of collection, creating
            a tamper-evident record that the document was in a specific state at a specific time.
            This is particularly valuable for social media content, web pages, and other digital
            materials that can be altered or deleted.
          </p>
        </section>

        {/* Court admissibility */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Court Admissibility Considerations</h2>
          <p className="text-base leading-relaxed mb-4">
            C2PA manifests use X.509 certificates and standard cryptographic signing that courts
            have accepted in other contexts (electronic signatures, SSL certificates, PGP-signed
            communications). The RFC 3161 timestamp uses the same trusted timestamping authority
            infrastructure used in EU qualified electronic signatures and US federal PKI.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Admissibility determinations are jurisdiction-specific and fact-specific. Federal courts
            applying FRE 901(b)(9) look to whether the process used to create the evidence is
            accurate and reliable. State courts vary. International courts have their own frameworks.
            Legal practitioners should evaluate the specific signing certificate chain, timestamping
            authority, and verification process for their jurisdiction.
          </p>
          <div className="bg-muted/30 border border-border rounded-lg p-6 mb-4">
            <h3 className="font-semibold mb-3">What the manifest provides for authentication</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>- Cryptographic hash bound to document content (SHA-256)</li>
              <li>- RFC 3161 timestamp from trusted timestamping authority</li>
              <li>- X.509 certificate chain identifying the signing organization</li>
              <li>- COSE signature covering all manifest claims</li>
              <li>- Tamper detection: signature fails if document is altered post-signing</li>
            </ul>
          </div>
          <p className="text-base leading-relaxed">
            Encypher's provenance infrastructure is technical infrastructure, not legal advice.
            The legal implications of this infrastructure vary by jurisdiction and context.
            For a detailed analysis of how cryptographic provenance interacts with copyright and
            licensing law, see{' '}
            <Link href="/cryptographic-watermarking/legal-implications" className="text-[#2a87c4] hover:underline">
              Cryptographic Watermarking: Legal Implications
            </Link>
            .
          </p>
        </section>

        {/* Formal notice */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Formal Notice in AI Copyright Disputes</h2>
          <p className="text-base leading-relaxed mb-4">
            AI copyright litigation hinges on what AI companies knew or should have known about
            the ownership of content they used for training. The "we did not know" defense is
            viable when content arrived stripped of identifying information - which is what
            happened in the early years of large-scale web scraping for training data.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Embedded provenance changes this calculus for future content. Publishers and content
            owners who sign their content before distribution create a record that the ownership
            claim was present in the content at the time of any subsequent AI ingestion. The
            manifest is machine-readable, cryptographically signed, and timestamped. It is not
            a separate record that can be disclaimed.
          </p>
          <p className="text-base leading-relaxed mb-4">
            For legal practitioners representing content owners in AI copyright matters, the
            strategic question is whether your client's content carries provenance that predates
            the infringement. Content signed before the alleged training run is stronger evidence
            of notice than content signed after. Provenance infrastructure needs to be in place
            before the infringement, not as a remedial measure.
          </p>
          <p className="text-base leading-relaxed">
            The willful infringement standard under 17 U.S.C. Section 504(c)(2) allows statutory
            damages up to $150,000 per work. Demonstrating that an infringer received content
            with embedded ownership metadata supports the willful infringement argument. This is
            a meaningful damages difference in cases involving large numbers of works.
          </p>
        </section>

        {/* AI-generated documents in discovery */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">AI-Generated Documents in Discovery</h2>
          <p className="text-base leading-relaxed mb-4">
            Discovery is encountering AI-generated documents at increasing frequency. Emails drafted
            by AI, reports generated by AI systems, contracts produced through AI-assisted drafting.
            Distinguishing AI-generated from human-authored documents is now a discovery challenge.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Statistical AI detection tools are unreliable for this purpose. They produce false positives
            on human-written content and false negatives on AI-generated content that has been lightly
            edited. They are not suitable for evidentiary claims.
          </p>
          <p className="text-base leading-relaxed">
            Provenance provides a different approach: not statistical detection after the fact, but
            documented authentication at the point of creation. Documents signed with Encypher carry
            a manifest recording their authorship status. A document signed as human-authored carries
            that claim. A document signed as AI-generated carries that claim. The signature is
            cryptographically bound to the content and cannot be altered without detection.
            See the{' '}
            <Link href="/glossary" className="text-[#2a87c4] hover:underline">
              content provenance glossary
            </Link>{' '}
            for technical definitions used in legal and regulatory contexts.
          </p>
        </section>

        {/* Professional responsibility */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">AI Disclosure and Professional Responsibility</h2>
          <p className="text-base leading-relaxed mb-4">
            Bar associations and courts are issuing AI disclosure requirements faster than law firms
            are implementing compliance infrastructure. Some courts require explicit disclosure of
            AI assistance in briefs. Several state bars have issued ethics guidance on AI use in
            client work. The trend is toward more disclosure, not less.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Content provenance provides a documentation layer for compliance. Each document processed
            through Encypher carries a manifest recording its authorship status. Law firms can use
            this infrastructure to generate audit logs demonstrating which documents used AI assistance,
            at what stage, and to what extent.
          </p>
          <p className="text-base leading-relaxed">
            For firms that need to certify to courts that specific documents were not AI-generated,
            or that AI assistance was disclosed, provenance manifests provide a technical foundation
            for that certification. The manifest is created at the point of document creation, before
            any disclosure obligation arises, which is the right sequence for compliance documentation.
          </p>
        </section>

        {/* FAQ section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-6">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">
                Can Encypher sign documents I collect as evidence to preserve their state?
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Yes. The Encypher API supports signing any document at the time of collection.
                The manifest records the signing timestamp from an RFC 3161 trusted timestamping
                authority, which provides evidence that the document was in its signed state at
                that time. This is useful for preserving the authenticity of web pages, social
                media content, and other materials collected for litigation.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">
                Does the C2PA manifest contain attorney-client privileged information?
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                The manifest records organizational identity, timestamps, and document hash.
                It does not record the content of the document, attorney names, or client identifiers
                by default. Custom claim generators can add additional metadata, but the standard
                implementation does not expose privileged information in the manifest. Law firms
                can review the specific fields included in their organizational signing configuration.
              </p>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="border-t pt-8">
          <h2 className="text-xl font-semibold mb-4">Implement Legal Document Provenance</h2>
          <p className="text-muted-foreground mb-6">
            Evidence provenance and formal notice documentation need to be in place before disputes
            arise. Signing after the fact provides less evidentiary value.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 mb-6">
            <Button asChild style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/platform">API Documentation</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/cryptographic-watermarking/legal-implications">Legal Implications</Link>
            </Button>
          </div>
          <div className="flex flex-col sm:flex-row gap-4 text-sm">
            <Link href="/content-provenance" className="text-[#2a87c4] hover:underline">
              What Is Content Provenance?
            </Link>
            <Link href="/glossary" className="text-[#2a87c4] hover:underline">
              Glossary
            </Link>
            <Link href="/cryptographic-watermarking/legal-implications" className="text-[#2a87c4] hover:underline">
              Cryptographic Watermarking: Legal Implications
            </Link>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
