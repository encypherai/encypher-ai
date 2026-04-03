import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@encypher/design-system';
import { getVerticalMetadata } from '@/lib/seo';
import type { Metadata } from 'next';

export const metadata: Metadata = getVerticalMetadata(
  'government',
  'Content Provenance for Government Agencies | Encypher',
  'Public records authentication, FOIA documentation integrity, regulatory filing provenance, and official document authentication for government agencies using C2PA cryptographic signing.',
  'Cryptographic provenance for public records and official documents.'
);

export default function GovernmentPage() {
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'How does C2PA provenance apply to government public records?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Government agencies publish documents that citizens, journalists, and businesses rely on as authoritative. C2PA manifests embedded in official documents create cryptographic proof that a document was issued by the named agency at a specific time and has not been altered since. Recipients can verify authenticity without contacting the agency. This is particularly valuable for documents that circulate widely or are used in legal and regulatory contexts where authenticity is essential.',
        },
      },
      {
        '@type': 'Question',
        name: 'How does content provenance support FOIA compliance?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'FOIA responses involve producing documents whose authenticity may be challenged. Agencies that sign documents at creation create a record that the document existed in its signed state at a specific time. When a FOIA requestor receives a document with a valid C2PA signature, they have cryptographic evidence that the document is authentic and unaltered. Agencies can also use provenance to demonstrate that redactions were applied to a specific version of a document, documenting the redaction as a provenance event.',
        },
      },
      {
        '@type': 'Question',
        name: 'Can government agencies use Encypher to authenticate official communications against deepfakes?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Yes. Video and audio statements from government officials can be signed with C2PA manifests at the time of recording or publication. The manifest records the agency identity, timestamp, and cryptographic hash of the content. Any subsequent alteration breaks the signature. Citizens and journalists can verify the authenticity of official communications by checking the manifest against the agency certificate. This is a defense against deepfake impersonation of officials and manipulation of official statements.',
        },
      },
      {
        '@type': 'Question',
        name: 'How does document provenance integrate with government PKI infrastructure?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'C2PA signing uses X.509 certificates, the same infrastructure used in government PKI (PIV cards, CAC cards, federal PKI bridge). Encypher supports integration with existing government certificate authorities, allowing agencies to sign content using their own PKI infrastructure rather than Encypher-issued certificates. This means the chain of trust runs through the agency\'s own certificate authority, which is verifiable by anyone who trusts the government PKI.',
        },
      },
    ],
  };

  return (
    <>
      <AISummary
        title="Content Provenance for Government Agencies"
        whatWeDo="Encypher provides C2PA cryptographic provenance for government documents, public records, official communications, and regulatory filings. Agencies embed tamper-evident manifests at publication, creating machine-verifiable proof of authenticity that citizens, journalists, and oversight bodies can check without contacting the agency."
        whoItsFor="Federal agencies, state and local government departments, regulatory bodies, and government technology teams. Specifically suited to agencies with high-volume public records disclosure obligations, official communications that are targets for manipulation, and regulatory filings requiring document integrity documentation."
        keyDifferentiator="Integration with government PKI infrastructure (PIV, CAC, federal PKI bridge) using existing agency certificate authorities. C2PA manifests that are verifiable by any party without contacting the agency. Document-level provenance for PDFs and office documents plus image, audio, and video authentication for official communications."
        primaryValue="Public records authentication that is verifiable without agency involvement. FOIA response integrity documentation. Defense against deepfake manipulation of official communications. Regulatory filing provenance for audit trails."
        pagePath="/content-provenance/government"
        pageType="WebPage"
      />

      <Script
        id="faq-government"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <ArticleShell path="/content-provenance/government">
        <Breadcrumbs
          items={[
            { name: 'Home', href: '/' },
            { name: 'Content Provenance', href: '/content-provenance' },
            { name: 'Government', href: '/content-provenance/government' },
          ]}
        />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Content Provenance for Government Agencies
        </h1>
        <p className="text-lg text-muted-foreground mb-8">
          Public records authentication, official document integrity, and agency communication
          verification using C2PA cryptographic signing integrated with government PKI.
        </p>

        {/* Public records */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Authenticating Public Records</h2>
          <p className="text-base leading-relaxed mb-4">
            Government agencies publish documents that form the basis of public trust in institutional
            decisions. Regulations, guidance documents, meeting minutes, official statistics, and
            policy announcements circulate widely online. They are cited in news coverage, legal
            filings, and academic research. Their authenticity is assumed.
          </p>
          <p className="text-base leading-relaxed mb-4">
            That assumption is increasingly exploited. Manipulated government documents circulate
            as genuine. Altered screenshots of agency websites spread on social media. AI-generated
            content is published under official agency branding. Distinguishing authentic government
            documents from fabrications is harder than it should be.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Content provenance makes authenticity machine-verifiable. An official document signed
            with a C2PA manifest at publication carries cryptographic proof of its origin. Any
            party can verify the document against the agency's published certificate, without
            contacting the agency and without specialized software. If the document has been altered,
            the signature fails. If it carries a valid signature from the issuing agency, the
            authenticity claim is verified.
          </p>
          <p className="text-base leading-relaxed">
            For citizens, journalists, and oversight bodies, this changes the verification question
            from "is this document from that agency?" (which currently requires judgment) to
            "does this document have a valid signature from that agency?" (which is a cryptographic
            check with a binary answer).
          </p>
        </section>

        {/* FOIA */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">FOIA Compliance and Document Integrity</h2>
          <p className="text-base leading-relaxed mb-4">
            FOIA responses are routinely challenged. Requestors dispute whether they received
            complete records. Agencies dispute whether produced documents were altered in transit.
            Redaction decisions are challenged on the grounds that the redacted version does not
            accurately represent the original. These disputes are expensive and time-consuming
            to resolve without a reliable authenticity record.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Provenance addresses this by creating a chain of custody for FOIA-responsive documents.
            When an agency produces documents in response to a FOIA request, it can sign each document
            at the time of production. The manifest records the production timestamp, the agency identity,
            and whether any redactions were applied. The requestor receives documents with cryptographic
            proof of their state at production.
          </p>
          <div className="bg-muted/30 border border-border rounded-lg p-6 mb-4">
            <h3 className="font-semibold mb-3">FOIA provenance chain</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>- Original document signed at creation (agency signing key)</li>
              <li>- Redacted version signed at FOIA production (references original as ingredient)</li>
              <li>- Redaction recorded as a provenance action with timestamp</li>
              <li>- Requestor receives document with full provenance chain</li>
              <li>- Chain is verifiable without further agency involvement</li>
            </ul>
          </div>
          <p className="text-base leading-relaxed">
            This is not just a compliance feature. It is a dispute-prevention feature. When the
            provenance chain is clear and verifiable, the factual disputes that consume FOIA
            litigation resources are resolved before they become disputes.
          </p>
        </section>

        {/* Official communications */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Official Communications and Deepfake Defense</h2>
          <p className="text-base leading-relaxed mb-4">
            Deepfake technology can produce realistic video and audio of government officials
            saying things they did not say. The threat is not hypothetical - manipulated videos
            of officials have circulated during elections and crises. The current defense relies
            on human judgment and post-hoc investigation, which is slow and often ineffective.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Official video and audio statements signed at recording or publication carry C2PA manifests
            that bind the agency identity to the specific content. Any alteration breaks the signature.
            Journalists and citizens can verify an official statement by checking its manifest.
            The verification is fast (seconds), requires no specialized knowledge, and gives a
            reliable answer.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Agencies that sign their official communications create a positive authentication baseline.
            Authentic communications are verifiable. Manipulated content, which lacks a valid agency
            signature, is distinguishable from the authentic record. This does not eliminate all
            deepfake risk - unsigned video can still circulate - but it gives the public a reliable
            mechanism to verify the official record.
          </p>
          <p className="text-base leading-relaxed">
            See the{' '}
            <Link href="/content-provenance/verification" className="text-[#2a87c4] hover:underline">
              verification documentation
            </Link>{' '}
            for how the public verification endpoint works. Verification requires no authentication
            and is available to any party.
          </p>
        </section>

        {/* Regulatory filings */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Regulatory Filing Provenance</h2>
          <p className="text-base leading-relaxed mb-4">
            Regulated entities submit filings to government agencies: financial disclosures, environmental
            reports, safety certifications, license applications. The authenticity and integrity of these
            filings matters for the regulatory process. Agencies need to know that the filing they received
            is the filing the entity submitted, unaltered.
          </p>
          <p className="text-base leading-relaxed mb-4">
            When regulated entities sign their filings before submission using Encypher, the agency
            receives a document with a cryptographic hash bound to its content. Any alteration in
            transit is detectable. The signing timestamp from an RFC 3161 trusted timestamping
            authority proves when the document was created, which matters for compliance deadlines.
          </p>
          <p className="text-base leading-relaxed">
            For agencies implementing e-filing systems, Encypher's API supports integration at the
            submission layer. Filings can be validated against their manifests at receipt, with
            broken signatures flagged for follow-up. This provides a systematic integrity check
            that does not depend on manual review.
          </p>
        </section>

        {/* Government PKI integration */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Integration with Government PKI</h2>
          <p className="text-base leading-relaxed mb-4">
            Government agencies operate within established PKI frameworks: PIV cards for individual
            identity, CAC cards for military personnel, the Federal PKI Bridge for cross-agency trust.
            Content provenance built on top of these existing certificate infrastructures inherits
            their trust properties.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Encypher supports custom certificate authority integration. Agencies can sign content
            using certificates issued by their own certificate authority, which is itself trusted
            through the Federal PKI bridge. The C2PA manifest carries the full certificate chain,
            so any party that trusts the government PKI can verify the signature without trusting
            Encypher's infrastructure independently.
          </p>
          <div className="bg-muted/30 border border-border rounded-lg p-6 mb-4">
            <h3 className="font-semibold mb-3">Government PKI integration options</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>- Bring your own certificate authority (BYOCA)</li>
              <li>- PIV/CAC card signing for individual official statements</li>
              <li>- Federal PKI bridge integration for cross-agency trust</li>
              <li>- Agency root CA integration for departmental signing</li>
              <li>- HSM-based signing for high-assurance environments</li>
            </ul>
          </div>
          <p className="text-base leading-relaxed">
            For technical integration requirements and FedRAMP authorization status, contact us
            directly. See the{' '}
            <Link href="/c2pa-standard" className="text-[#2a87c4] hover:underline">
              C2PA standard overview
            </Link>{' '}
            for the certificate and signing requirements at the specification level.
          </p>
        </section>

        {/* FAQ section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-6">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">
                Is Encypher FedRAMP authorized?
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                FedRAMP authorization status varies by deployment tier and data classification requirements.
                Contact us directly for current authorization status and available deployment options
                for government environments, including air-gapped and on-premises configurations.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">
                Can state and local governments use the same infrastructure as federal agencies?
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Yes. State and local governments can use Encypher with their own certificate authorities
                or with Encypher-issued certificates. The verification infrastructure is public and does
                not require federal PKI integration. State governments with their own PKI can integrate
                their certificate authorities for agency-branded signing.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">
                How does this interact with existing e-signature requirements for government documents?
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                C2PA content provenance is distinct from electronic signatures under ESIGN, UETA, or
                eIDAS. It is not a legal signature on a document but a provenance record attached to
                the document. For documents requiring legally binding electronic signatures, those
                requirements still apply. Provenance and legal signatures can coexist in the same
                document: the legal signature satisfies the legal requirement, and the C2PA manifest
                provides integrity documentation.
              </p>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="border-t pt-8">
          <h2 className="text-xl font-semibold mb-4">Implement Government Document Provenance</h2>
          <p className="text-muted-foreground mb-6">
            Authentic government records need provenance before the documents are challenged.
            Sign at publication, not in response to a dispute.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 mb-6">
            <Button asChild style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/platform">API Documentation</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/content-provenance/verification">Verification API</Link>
            </Button>
          </div>
          <div className="flex flex-col sm:flex-row gap-4 text-sm">
            <Link href="/content-provenance" className="text-[#2a87c4] hover:underline">
              What Is Content Provenance?
            </Link>
            <Link href="/c2pa-standard" className="text-[#2a87c4] hover:underline">
              The C2PA Standard
            </Link>
            <Link href="/content-provenance/verification" className="text-[#2a87c4] hover:underline">
              Verification Documentation
            </Link>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
