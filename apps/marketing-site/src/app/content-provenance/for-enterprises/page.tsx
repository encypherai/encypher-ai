import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'Content Provenance for Enterprises | EU AI Act Compliance | Encypher',
  'Enterprise AI governance with content provenance. Audit trails, compliance reporting, and EU AI Act Article 50 compliance before the August 2, 2026 deadline.',
  '/content-provenance/for-enterprises'
);

export default function ForEnterprisesPage() {
  const techArticle = getTechArticleSchema({
    title: 'Content Provenance for Enterprises',
    description: 'Enterprise AI governance with content provenance. Audit trails, compliance reporting, and EU AI Act Article 50 compliance before the August 2, 2026 deadline.',
    url: `${siteConfig.url}/content-provenance/for-enterprises`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'What does EU AI Act compliance require for enterprises using AI-generated content?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'EU AI Act Article 50 requires operators of AI systems to ensure AI-generated text intended for public communication is marked as AI-generated. Article 52 requires providers of AI systems that generate synthetic media to embed machine-readable markers. The full compliance deadline is August 2, 2026. C2PA manifests satisfy these requirements. Enterprises that deploy AI writing tools, generate marketing content, or produce AI-assisted documents for external audiences need to audit their AI content workflows against these requirements.',
        },
      },
      {
        '@type': 'Question',
        name: 'How do audit trails from content provenance support AI governance programs?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'An audit trail requires knowing what content exists, what its source is, and whether it has been modified. Content provenance creates exactly this record at the document level. Each signed document carries a tamper-evident manifest recording who created it, when, with what tool, and whether it has changed since signing. For AI governance programs, this means governance teams can verify that AI-generated content was reviewed before publication and that the reviewed version matches what was published.',
        },
      },
      {
        '@type': 'Question',
        name: 'What is multi-media signing and when do enterprises need it?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Multi-media signing allows enterprises to sign content across all 31 supported MIME types - text, images, audio, video, documents, and fonts - using a single enterprise key. This is relevant for organizations that produce or distribute mixed-media content: press releases with embedded images, video reports with transcripts, marketing campaigns with multiple asset types. Enterprise-tier signing supports delegated credentials, allowing department-level signing under a master organizational certificate.',
        },
      },
    ],
  };

  return (
    <>
      <AISummary
        title="Content Provenance for Enterprises"
        whatWeDo="Encypher provides enterprise content provenance infrastructure for AI governance, EU AI Act compliance, and audit trail generation. Multi-media signing, fingerprinting, and compliance reporting in an enterprise-grade API."
        whoItsFor="Enterprise legal, compliance, and governance teams managing AI content workflows. Organizations subject to EU AI Act obligations. Enterprises using AI writing, image generation, or synthetic media tools for external-facing content."
        keyDifferentiator="Cryptographic audit trails that satisfy regulatory requirements. Tamper-evident documentation that does not rely on log files that can be altered. C2PA manifests that are independently verifiable by regulators, auditors, and opposing counsel."
        primaryValue="EU AI Act compliance before the August 2, 2026 deadline. Audit trails that survive legal scrutiny. AI governance infrastructure that scales across multi-media content workflows."
        pagePath="/content-provenance/for-enterprises"
        pageType="WebPage"
      />

      <Script
        id="tech-article-for-enterprises"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />
      <Script
        id="faq-for-enterprises"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Content Provenance', href: '/content-provenance' },
          { name: 'For Enterprises', href: '/content-provenance/for-enterprises' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Content Provenance for Enterprises
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          EU AI Act Article 50 takes full effect August 2, 2026. Enterprises that produce
          AI-generated content for public audiences need compliant marking infrastructure
          in place before that date. Content provenance is that infrastructure.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The EU AI Act Compliance Timeline</h2>
          <p className="text-muted-foreground mb-4">
            The EU AI Act's transparency obligations have a phased rollout. Article 50 covers
            operators of AI systems interacting with natural persons - chatbots, AI writing
            assistants, customer service systems. It requires those systems to inform users
            they are interacting with AI.
          </p>
          <p className="text-muted-foreground mb-4">
            Article 52 covers providers of AI systems that generate synthetic audio, image,
            video, and text content. It requires outputs to be marked as AI-generated in a
            machine-readable format. This applies to content intended for public communication:
            marketing materials, press releases, public reports, published articles.
          </p>
          <p className="text-muted-foreground mb-4">
            The full compliance deadline for both articles is August 2, 2026. The EU AI Act
            applies to any enterprise with European customers or operations, regardless of
            where the enterprise is headquartered. Fines for non-compliance run up to 15
            million euros or 3 percent of worldwide annual turnover, whichever is higher.
          </p>
          <p className="text-muted-foreground">
            C2PA manifests satisfy the machine-readable marking requirement. An enterprise
            that signs its AI-generated content with C2PA provenance has documentation that
            each piece of content was marked at the point of generation, who generated it,
            and when. That documentation supports compliance reporting and survives regulatory
            audit.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Audit Trails for AI Governance</h2>
          <p className="text-muted-foreground mb-4">
            AI governance programs require answers to three questions: What AI-generated content
            exists in our systems? Where did it come from? Has it been modified since generation?
            Log files can answer the first two questions approximately. They cannot reliably answer
            the third, and they are alterable.
          </p>
          <p className="text-muted-foreground mb-4">
            Content provenance answers all three questions with cryptographic certainty.
            A C2PA manifest embedded in a document at generation time records the generation
            event in a tamper-evident structure. Any subsequent modification to the document
            changes its hash and breaks the manifest signature. The modification is detectable
            by anyone with the public key and the document.
          </p>
          <p className="text-muted-foreground mb-4">
            For enterprises with AI governance policies requiring human review before publication,
            provenance creates a verifiable checkpoint. The review can be recorded as a signed
            assertion in the manifest chain: human reviewer identity, review timestamp, and the
            content state at the time of review. The published version's manifest records whether
            the content changed after review.
          </p>
          <p className="text-muted-foreground">
            This audit trail is not a log that can be altered after the fact. It is embedded
            in the content itself. A regulator or auditor examining the document can verify
            the chain independently, without Encypher's involvement, using open-source
            verification libraries.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Enterprise-Tier Features</h2>
          <p className="text-muted-foreground mb-4">
            Enterprise accounts include capabilities beyond the standard API:
          </p>
          <ul className="space-y-4 mb-4">
            <li className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Multi-Media Signing</h3>
              <p className="text-muted-foreground text-sm">Sign content across all 31 supported MIME types - text, images, audio, video, documents, and fonts - under a single enterprise certificate. Mixed-media assets are signed as a unified provenance package.</p>
            </li>
            <li className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Fingerprinting</h3>
              <p className="text-muted-foreground text-sm">Enterprise-tier fingerprinting embeds unique, recipient-specific markers into distributed content using HMAC-based pseudorandom positioning. When content leaks, fingerprint analysis identifies the distribution channel. Useful for confidential documents, pre-publication content, and internal communications.</p>
            </li>
            <li className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Bring Your Own Key (BYOK)</h3>
              <p className="text-muted-foreground text-sm">Sign content against your own organizational certificate. Signatures are verifiable by any party with your public key without Encypher's involvement. Appropriate for attorney-client privilege contexts and strict data residency requirements.</p>
            </li>
            <li className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Delegated Credentials</h3>
              <p className="text-muted-foreground text-sm">Issue department-level signing credentials under the master enterprise certificate. Marketing, legal, and communications teams sign content under their own identities while maintaining a unified organizational key hierarchy.</p>
            </li>
            <li className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Compliance Reporting</h3>
              <p className="text-muted-foreground text-sm">Automated compliance reports documenting AI-generated content volumes, signing coverage rates, and manifest audit trails. Formatted for EU AI Act reporting obligations and common enterprise governance frameworks.</p>
            </li>
          </ul>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Integration with Existing Workflows</h2>
          <p className="text-muted-foreground mb-4">
            Enterprise content provenance integrates at the content creation and publication
            layer, not as a separate system. The typical integration points are:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>CMS publish webhook: sign articles at the moment of publication</li>
            <li>AI writing tool output: sign at generation, before editorial review</li>
            <li>Document management system save event: sign on document completion</li>
            <li>Media asset management export: sign images and video on delivery</li>
            <li>Email distribution: sign press releases before distribution</li>
          </ul>
          <p className="text-muted-foreground mb-4">
            REST API, Python SDK, and TypeScript SDK are available. Common document management
            system integrations for iManage, NetDocuments, and SharePoint are available for
            enterprise customers. Word and Google Docs add-ins for real-time provenance
            embedding are available at enterprise tier.
          </p>
          <p className="text-muted-foreground">
            On-premises deployment is available for enterprises with strict data residency
            requirements. In on-premises mode, document content never leaves the enterprise
            environment. The signing service runs within your infrastructure.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Content Provenance in Enterprise Legal Risk</h2>
          <p className="text-muted-foreground mb-4">
            Enterprise AI governance is increasingly a legal risk function, not just a compliance
            checkbox. Courts in multiple jurisdictions have issued AI disclosure requirements for
            attorneys. Regulatory filings in certain sectors require disclosure of AI involvement.
            Enterprise customers are asking vendors about AI content policies in security questionnaires.
          </p>
          <p className="text-muted-foreground mb-4">
            Content provenance addresses these risks directly. A document signed at generation
            with a C2PA manifest carries its own disclosure - the manifest records that it was
            AI-generated, by which system, and when. That disclosure is not a claim the enterprise
            is asserting; it is a cryptographic fact embedded in the document.
          </p>
          <p className="text-muted-foreground">
            For enterprises that produce both human-authored and AI-generated content, provenance
            creates the clear distinction that governance and legal teams need: a verifiable record
            of which content is which, with tamper-evident documentation that cannot be revised
            after the fact.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/content-provenance/eu-ai-act" className="underline hover:no-underline">EU AI Act and Content Provenance: Full Compliance Guide</Link></li>
            <li><Link href="/content-provenance" className="underline hover:no-underline">Content Provenance: The Definitive Guide</Link></li>
            <li><Link href="/c2pa-standard" className="underline hover:no-underline">The C2PA Standard</Link></li>
            <li><Link href="/cryptographic-watermarking/legal-implications" className="underline hover:no-underline">Legal Implications of Cryptographic Watermarking</Link></li>
            <li><Link href="/content-provenance/verification" className="underline hover:no-underline">Free Verification: How It Works</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Enterprise Compliance Infrastructure</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            August 2, 2026 is the EU AI Act compliance deadline. Enterprise implementation
            typically requires 60-90 days including workflow integration and testing.
            Starting now leaves adequate time.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/contact">Talk to Enterprise Sales</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/try">Start Free Trial</Link>
            </Button>
          </div>
        </section>
      </div>
    </>
  );
}
