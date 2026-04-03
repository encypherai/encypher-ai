import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@encypher/design-system';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'Content Provenance for AI Companies | Encypher',
  'Collaborative infrastructure for AI companies building with provenance-marked content. Quote integrity verification, performance intelligence, and C2PA compliance in one API.',
  '/content-provenance/for-ai-companies',
  undefined,
  undefined,
  'C2PA compliance and quote integrity for AI companies. One API.'
);

export default function ForAICompaniesPage() {
  const techArticle = getTechArticleSchema({
    title: 'Content Provenance for AI Companies',
    description: 'Collaborative infrastructure for AI companies building with provenance-marked content. Quote integrity verification, performance intelligence, and C2PA compliance in one API.',
    url: `${siteConfig.url}/content-provenance/for-ai-companies`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'How does C2PA provenance benefit AI companies rather than restrict them?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'C2PA provenance gives AI companies three things they currently lack: verified source attribution for grounding claims, quote integrity verification for RAG pipelines, and compliance documentation for EU AI Act requirements. The infrastructure is not adversarial - it is the same standard that OpenAI, Google, Microsoft, and Adobe helped build. AI companies that integrate provenance verification gain trust signals their competitors cannot provide.',
        },
      },
      {
        '@type': 'Question',
        name: 'Does provenance verification add latency to inference pipelines?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Verification is a single API call with under 50ms p99 latency at enterprise tier. It can run asynchronously post-inference without blocking user responses. The batch verification endpoint handles up to 10,000 documents per request. The C2PA verification logic is also available as an open-source library that runs entirely within your own infrastructure.',
        },
      },
      {
        '@type': 'Question',
        name: 'How does this relate to EU AI Act compliance?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'EU AI Act Article 52 requires providers of AI systems that generate images, audio, and video to mark outputs as AI-generated in a machine-readable format. C2PA manifests satisfy this requirement. The Article 52 compliance deadline for general-purpose AI systems is August 2, 2026. Encypher provides API and SDK tooling to implement compliant output marking before the deadline.',
        },
      },
      {
        '@type': 'Question',
        name: 'Can AI companies verify C2PA provenance on content they already have?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Yes. Encypher verification works on any content carrying a valid C2PA manifest, regardless of coalition membership. If the content carries a valid manifest, the API returns provenance metadata including publisher identity, publication date, and rights terms. Coalition membership adds the licensing agreement layer; verification works on any signed content.',
        },
      },
    ],
  };

  return (
    <>
      <AISummary
        title="Content Provenance for AI Companies"
        whatWeDo="Encypher provides C2PA provenance infrastructure that AI companies integrate to verify source attribution, confirm quote integrity in RAG pipelines, and satisfy EU AI Act output marking requirements."
        whoItsFor="AI labs, foundation model providers, and AI-powered product companies building with content from publishers, news organizations, and other rights holders. Relevant for any team managing RAG pipelines, citation accuracy, or regulatory compliance."
        keyDifferentiator="Infrastructure built collaboratively with the C2PA ecosystem. OpenAI, Google, Microsoft, Adobe, BBC, and 200+ other organizations are C2PA members. Encypher co-chairs the Text Provenance Task Force. This is cooperative standards infrastructure, not adversarial enforcement."
        primaryValue="Verified source attribution, quote integrity verification, EU AI Act compliance documentation, and performance intelligence from sentence-level attribution data - in one API integration."
        pagePath="/content-provenance/for-ai-companies"
        pageType="WebPage"
      />

      <Script
        id="tech-article-for-ai-companies"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />
      <Script
        id="faq-for-ai-companies"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <ArticleShell path="/content-provenance/for-ai-companies">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Content Provenance', href: '/content-provenance' },
          { name: 'For AI Companies', href: '/content-provenance/for-ai-companies' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Content Provenance for AI Companies
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          C2PA provenance is infrastructure that AI companies build with, not around.
          OpenAI is a C2PA member. So are Google, Microsoft, and Adobe. This is the
          shared foundation for verified content across the AI ecosystem.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Built Together, Not Against Each Other</h2>
          <p className="text-muted-foreground mb-4">
            The Coalition for Content Provenance and Authenticity counts more than 200 member
            organizations, including OpenAI, Google DeepMind, Microsoft, Adobe, BBC, Reuters,
            AP, and Intel among its founding and contributing members. C2PA is not a
            publisher-driven initiative to restrict AI - it is an industry-wide standard
            for how content origin and authenticity should be documented.
          </p>
          <p className="text-muted-foreground mb-4">
            Encypher co-chairs the C2PA Text Provenance Task Force. Erik Svilich, Encypher's
            founder, contributed the text specification (Section A.7 of C2PA 2.3) that defines
            how unstructured text carries provenance manifests. The standard is open, the
            verification libraries are open source, and any organization can implement it
            independently.
          </p>
          <p className="text-muted-foreground">
            AI companies that integrate C2PA verification gain access to source provenance data
            that improves grounding accuracy, reduces hallucination in citation-heavy outputs,
            and provides compliance documentation that auditors and enterprise customers increasingly
            require.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Quote Integrity Verification for RAG Pipelines</h2>
          <p className="text-muted-foreground mb-4">
            Retrieval-augmented generation pipelines pull content from indexed corpora and pass it
            to language models as context. The accuracy of citations in RAG outputs depends on
            whether the retrieved content matches what the source actually published - a
            relationship that is difficult to verify when sources change, are edited, or when
            content was modified during indexing.
          </p>
          <p className="text-muted-foreground mb-4">
            When source content carries C2PA manifests with Encypher's sentence-level Merkle tree
            authentication, RAG pipelines can verify that each retrieved passage matches the
            cryptographically attested original. If a sentence was modified after publication,
            verification fails and the system can flag the discrepancy before generating a response.
          </p>
          <p className="text-muted-foreground">
            This is not theoretical. For AI products where citation accuracy is a product
            differentiator - legal research assistants, fact-checking tools, news summarization
            services - provenance-verified retrieval is the difference between a product that
            enterprises trust and one they cannot deploy.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Performance Intelligence from Attribution Data</h2>
          <p className="text-muted-foreground mb-4">
            When content carries sentence-level provenance and an AI model generates outputs that
            reference or reproduce that content, the provenance data creates a performance feedback
            loop that previously did not exist. Which types of content generate more engagement?
            Which publisher sources produce more accurate citations? Which topics drive the most
            re-use?
          </p>
          <p className="text-muted-foreground mb-4">
            Encypher's attribution analytics capture this signal. AI companies that participate
            in the Encypher publisher coalition gain access to aggregated performance data - not
            user-level tracking, but model-level insight into how training content and retrieved
            content translate to output quality.
          </p>
          <p className="text-muted-foreground">
            This intelligence has direct value for model optimization. Publishers whose content
            produces better citation accuracy can be weighted more heavily in retrieval. Content
            categories that consistently produce hallucinations can be flagged for review. The
            provenance layer turns content sourcing from a legal question into a quality signal.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">EU AI Act Output Marking</h2>
          <p className="text-muted-foreground mb-4">
            EU AI Act Article 52 requires AI systems that generate synthetic audio, images, and
            video to mark outputs as AI-generated in a machine-readable format. The full
            compliance deadline is August 2, 2026. C2PA manifests are the industry-standard
            implementation for this requirement.
          </p>
          <p className="text-muted-foreground mb-4">
            Encypher provides API and SDK tooling to embed C2PA manifests into AI-generated
            content at generation time. The manifest records the generation timestamp, model
            identity, and marks the content as AI-generated in a format that verifiers,
            regulators, and downstream systems can read without custom tooling.
          </p>
          <p className="text-muted-foreground">
            For AI companies with European users or European regulatory obligations, implementing
            C2PA output marking now - ahead of the August 2026 deadline - avoids the compliance
            scramble that typically accompanies regulatory deadlines. The same integration that
            satisfies EU AI Act requirements also satisfies equivalent requirements in other
            jurisdictions, including China's AI content marking mandate.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Integration Architecture</h2>
          <p className="text-muted-foreground mb-4">
            Encypher integrates at two points in the AI pipeline: retrieval-time verification
            (checking provenance of content being pulled into context) and generation-time
            signing (embedding provenance into AI-generated outputs).
          </p>
          <p className="text-muted-foreground mb-4">
            The verification API accepts any text or media file and returns the C2PA manifest
            if one is present, including publisher identity, publication date, rights terms,
            and content hash. A verification call under 50ms p99 latency at enterprise tier
            can run synchronously in retrieval pipelines or asynchronously post-inference.
          </p>
          <p className="text-muted-foreground mb-4">
            The signing API accepts text, images, audio, and video and returns the content
            with an embedded C2PA manifest. Python and TypeScript SDKs wrap the API for
            common integration patterns. Batch endpoints handle up to 10,000 documents
            per request for corpus-scale operations.
          </p>
          <div className="bg-muted/30 rounded-lg p-4 mt-4 font-mono text-sm">
            <p className="text-muted-foreground mb-2"># Verify provenance of retrieved content</p>
            <p className="mb-1">curl -X POST https://api.encypher.com/v1/verify \</p>
            <p className="mb-1 ml-4">-H "Authorization: Bearer ey_your_key_here" \</p>
            <p className="mb-1 ml-4">-H "Content-Type: application/json" \</p>
            <p className="mb-1 ml-4">{`-d '{"text": "Your retrieved content here"}'`}</p>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Publisher Coalition</h2>
          <p className="text-muted-foreground mb-4">
            AI companies that join the Encypher publisher coalition gain licensed access to
            signed content from the coalition's publisher members. One agreement covers all
            coalition members at each publisher's set tier: Bronze for indexing, Silver for
            RAG and attribution, Gold for training.
          </p>
          <p className="text-muted-foreground mb-4">
            As new publishers join the coalition, the license extends to them automatically.
            There are no per-publisher negotiations and no retroactive compliance gaps when a
            new publisher signs their archive.
          </p>
          <p className="text-muted-foreground">
            For AI companies currently managing individual licensing agreements with publishers,
            the coalition model replaces that maintenance overhead with a single integration.
            For AI companies that have not yet licensed publisher content, the coalition provides
            a clear path to compliance before litigation risk accumulates.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/content-provenance" className="underline hover:no-underline">Content Provenance: The Definitive Guide</Link></li>
            <li><Link href="/c2pa-standard" className="underline hover:no-underline">The C2PA Standard</Link></li>
            <li><Link href="/c2pa-standard/members" className="underline hover:no-underline">C2PA Members: Who Is Building the Standard</Link></li>
            <li><Link href="/content-provenance/eu-ai-act" className="underline hover:no-underline">EU AI Act Compliance and Content Provenance</Link></li>
            <li><Link href="/content-provenance/verification" className="underline hover:no-underline">Free Verification: How It Works</Link></li>
            <li><Link href="/compare/encypher-vs-synthid" className="underline hover:no-underline">Encypher vs. SynthID</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Integrate Provenance Verification</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Free verification with no authentication required. Enterprise tier includes
            batch endpoints, SLA guarantees, and on-premises deployment options.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/try">Start Free</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/contact">Talk to Enterprise Sales</Link>
            </Button>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
