import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@encypher/design-system';
import { getVerticalMetadata } from '@/lib/seo';
import type { Metadata } from 'next';

export const metadata: Metadata = getVerticalMetadata(
  'enterprise-ai',
  'Content Provenance for Enterprise AI Governance | Encypher',
  'EU AI Act Article 50 compliance, AI content audit trails, and enterprise governance infrastructure. Embed cryptographic provenance into AI-generated content before the August 2, 2026 enforcement deadline.',
  'EU AI Act Article 50 compliance via embedded content provenance.'
);

export default function EnterpriseAIPage() {
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'What does EU AI Act Article 50 require for AI-generated content?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'EU AI Act Article 50 requires that AI systems generating synthetic content (text, images, audio, video) mark that content in a machine-readable format detectable by humans. The requirement applies to general-purpose AI models generating large volumes of synthetic content. The August 2, 2026 enforcement deadline applies to general-purpose AI model providers. Enterprises deploying those models in their products and workflows need provenance infrastructure that satisfies the marking requirement and creates an audit trail demonstrating compliance.',
        },
      },
      {
        '@type': 'Question',
        name: 'How does Encypher help enterprises comply with EU AI Act content marking requirements?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Encypher provides an API for embedding C2PA manifests into AI-generated content at the point of generation. The manifest records that the content was AI-generated, which model produced it, the timestamp, and the enterprise organization responsible. This creates a machine-readable marking that satisfies the Article 50 technical requirement and a tamper-evident audit trail that demonstrates the marking was applied consistently.',
        },
      },
      {
        '@type': 'Question',
        name: 'What is the difference between C2PA document-level provenance and Encypher segment-level provenance for enterprise AI?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'C2PA provides document-level provenance: a manifest attached to a file that authenticates the document as a whole. This is the standard for images, audio, and video. For text, Encypher offers proprietary segment-level provenance that can attribute individual sentences or paragraphs to their source. In an enterprise context where documents contain both AI-generated and human-authored sections, segment-level provenance allows precise attribution rather than a document-level binary claim.',
        },
      },
      {
        '@type': 'Question',
        name: 'How does enterprise AI governance benefit from content provenance beyond regulatory compliance?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Provenance creates an audit trail that supports multiple governance objectives beyond regulatory compliance. When AI-generated content causes harm (reputational damage, legal exposure, misinformation), provenance records allow organizations to trace which system generated it, when, and under what authorization. This is essential for incident response, liability allocation in multi-vendor AI stacks, and internal governance accountability.',
        },
      },
    ],
  };

  return (
    <>
      <AISummary
        title="Content Provenance for Enterprise AI Governance"
        whatWeDo="Encypher provides an API for embedding cryptographic C2PA provenance into AI-generated content at the point of generation. The manifest records AI authorship, model identity, timestamp, and responsible organization. This creates both a machine-readable marking satisfying EU AI Act Article 50 and an audit trail for enterprise AI governance."
        whoItsFor="Fortune 500 enterprises deploying AI content generation systems, AI governance and compliance teams, legal departments managing EU AI Act exposure, and technology organizations building AI products that generate synthetic content for distribution."
        keyDifferentiator="C2PA document-level provenance for images, audio, and video. Proprietary segment-level provenance for text that can attribute individual sentences to their AI source within a mixed human-AI document. Enterprise tier includes dual binding, fingerprinting, and audit trail export."
        primaryValue="EU AI Act Article 50 compliance infrastructure before the August 2, 2026 enforcement deadline. Audit trails for AI content incidents. Attribution clarity in multi-vendor AI stacks. Governance accountability for AI-generated content distribution."
        pagePath="/content-provenance/enterprise-ai"
        pageType="WebPage"
      />

      <Script
        id="faq-enterprise-ai"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <ArticleShell path="/content-provenance/enterprise-ai">
        <Breadcrumbs
          items={[
            { name: 'Home', href: '/' },
            { name: 'Content Provenance', href: '/content-provenance' },
            { name: 'Enterprise AI', href: '/content-provenance/enterprise-ai' },
          ]}
        />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Content Provenance for Enterprise AI Governance
        </h1>
        <p className="text-lg text-muted-foreground mb-8">
          EU AI Act Article 50 compliance infrastructure, AI content audit trails, and enterprise
          governance for organizations generating AI content at scale.
        </p>

        {/* EU AI Act */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">EU AI Act Article 50: The August 2026 Deadline</h2>
          <p className="text-base leading-relaxed mb-4">
            The EU AI Act Article 50 requires that AI systems generating synthetic content mark that
            content in a machine-readable format. The enforcement deadline for general-purpose AI model
            providers is August 2, 2026. Enterprises deploying those models in customer-facing products
            and internal workflows need provenance infrastructure in place before that date.
          </p>
          <p className="text-base leading-relaxed mb-4">
            The requirement is not merely disclosure. It is technical marking: the content itself must
            carry machine-readable identification of its AI origin. A terms-of-service disclosure that
            your product uses AI does not satisfy Article 50. Each piece of generated content must
            carry its own marking.
          </p>
          <div className="bg-muted/30 border border-border rounded-lg p-6 mb-4">
            <h3 className="font-semibold mb-3">Article 50 technical requirements</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>- Machine-readable marking embedded in or attached to the content</li>
              <li>- Marking must be detectable by automated systems</li>
              <li>- Applies to text, images, audio, and video generated by AI</li>
              <li>- Must be robust to standard content processing</li>
              <li>- Organizations must maintain records of marking implementation</li>
            </ul>
          </div>
          <p className="text-base leading-relaxed">
            Encypher's C2PA manifest infrastructure satisfies all five requirements. For a detailed
            analysis of how Article 50 applies to specific content types and deployment scenarios,
            see the{' '}
            <Link href="/content-provenance/eu-ai-act" className="text-[#2a87c4] hover:underline">
              EU AI Act compliance overview
            </Link>
            .
          </p>
        </section>

        {/* Audit trails */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">AI Content Audit Trails</h2>
          <p className="text-base leading-relaxed mb-4">
            When AI-generated content causes a problem, the first question is: where did this come from?
            In a typical enterprise AI stack, this question has no clean answer. Content was generated
            by a model from a vendor, in a workflow built by a developer, invoked through an application
            built by a third team, distributed through a channel managed by a fourth. Which system
            is responsible for the content that caused the issue?
          </p>
          <p className="text-base leading-relaxed mb-4">
            Provenance creates the audit trail that makes this question answerable. Each piece of
            AI-generated content carries a manifest recording which system generated it, under what
            organizational authorization, at what timestamp. When an incident occurs, the manifest
            traces the content to its source.
          </p>
          <p className="text-base leading-relaxed">
            Enterprise tier customers can export audit logs from the Encypher API, including all
            signing events, content hashes, and timestamps. This creates an organizational record
            of AI content generation activity that supports both internal incident review and
            external regulatory reporting.
          </p>
        </section>

        {/* Multi-vendor AI stacks */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Attribution in Multi-Vendor AI Stacks</h2>
          <p className="text-base leading-relaxed mb-4">
            Enterprise AI deployments rarely use a single model from a single vendor. A typical
            enterprise AI workflow might use one model for drafting, another for editing, a third
            for image generation, and a retrieval-augmented generation system pulling from internal
            knowledge bases. Content that reaches customers is a composite of multiple AI systems'
            outputs.
          </p>
          <p className="text-base leading-relaxed mb-4">
            The C2PA ingredient model supports this complexity. A document can carry a manifest
            recording each AI system that contributed to it, in sequence, with timestamps. If the
            draft was generated by Model A and edited by Model B, both contributions are recorded.
            If the final output includes content from an internal knowledge base, that source is
            recorded as an ingredient.
          </p>
          <p className="text-base leading-relaxed">
            This is not just a compliance feature. It is a governance feature. Organizations with
            clear AI content lineage can make better decisions about which AI systems to deploy,
            identify which systems produced problematic content, and demonstrate to regulators
            the specific provenance of content under scrutiny.
          </p>
        </section>

        {/* Document vs segment level */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Document-Level vs. Segment-Level Provenance</h2>
          <p className="text-base leading-relaxed mb-4">
            For images, audio, and video, C2PA document-level provenance is the right tool. The manifest
            attaches to the file and authenticates it as a whole. This is the C2PA standard as defined
            in the specification, and Encypher implements it natively for all 33 supported media formats.
          </p>
          <p className="text-base leading-relaxed mb-4">
            For text, enterprise AI workflows often produce mixed-origin documents: human-written sections,
            AI-generated sections, and sections from both. Document-level provenance cannot represent
            this granularity. A document-level claim that "this document is AI-generated" is inaccurate
            for a document that is 30% AI-generated.
          </p>
          <p className="text-base leading-relaxed">
            Encypher's proprietary segment-level text provenance, which uses invisible Unicode markers
            embedded at the sentence level, can attribute individual segments to their origin. This is
            Encypher's own technology, distinct from the C2PA standard, and it is the basis for the
            text provenance work in C2PA Section A.7. For enterprise customers with mixed-origin text
            workflows, segment-level provenance is the accurate representation. See the{' '}
            <Link href="/content-provenance/for-enterprises" className="text-[#2a87c4] hover:underline">
              enterprise overview
            </Link>{' '}
            for tier comparison and feature availability.
          </p>
        </section>

        {/* Transparency requirements */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">AI Content Transparency for Stakeholders</h2>
          <p className="text-base leading-relaxed mb-4">
            Beyond regulatory compliance, enterprise boards and investors are asking governance questions
            about AI content. What AI systems does the company use to generate customer-facing content?
            What percentage of distributed content is AI-generated? What oversight exists for AI content
            before distribution? How would the company respond to an incident involving AI-generated content?
          </p>
          <p className="text-base leading-relaxed mb-4">
            Organizations with provenance infrastructure can answer these questions with data. The signing
            API records every AI content generation event. Audit log exports provide the raw data for
            governance reporting. The manifest embedded in each piece of content provides the per-asset
            evidence supporting the aggregate report.
          </p>
          <p className="text-base leading-relaxed">
            This is the difference between a governance policy and a governance program. A policy states
            what the organization intends to do. A program with provenance infrastructure demonstrates
            what the organization actually did.
          </p>
        </section>

        {/* FAQ section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-6">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">
                Does the August 2026 EU AI Act deadline apply to enterprises or only to model providers?
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                The direct obligation falls on general-purpose AI model providers. Enterprises deploying
                those models have an indirect compliance interest: if the model provider does not satisfy
                the marking requirement, and the enterprise distributes unmarked AI content, the enterprise
                faces its own exposure under downstream AI transparency requirements. Building your own
                provenance layer is a hedge against model provider non-compliance and a demonstration of
                governance due diligence.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">
                How does enterprise AI provenance interact with existing DLP and content governance systems?
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Encypher's API integrates at the content generation layer, before content reaches DLP
                systems. Signed content can be identified and tracked through existing governance workflows
                using the cryptographic hash in the manifest. For DLP systems that need to classify
                AI-generated content, the manifest provides a reliable signal that does not depend on
                statistical detection methods.
              </p>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="border-t pt-8">
          <h2 className="text-xl font-semibold mb-4">Implement Enterprise AI Governance</h2>
          <p className="text-muted-foreground mb-6">
            The August 2, 2026 enforcement deadline is fixed. Provenance infrastructure requires
            integration time. Start the compliance implementation now.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 mb-6">
            <Button asChild style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/content-provenance/for-enterprises">Enterprise Overview</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/platform">API Documentation</Link>
            </Button>
          </div>
          <div className="flex flex-col sm:flex-row gap-4 text-sm">
            <Link href="/content-provenance/eu-ai-act" className="text-[#2a87c4] hover:underline">
              EU AI Act Compliance
            </Link>
            <Link href="/c2pa-standard" className="text-[#2a87c4] hover:underline">
              The C2PA Standard
            </Link>
            <Link href="/content-provenance/for-enterprises" className="text-[#2a87c4] hover:underline">
              Enterprise Features
            </Link>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
