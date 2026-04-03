import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@encypher/design-system';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'EU AI Act and Content Provenance | August 2026 Compliance | Encypher',
  'EU AI Act Article 50 transparency requirements for AI-generated content. C2PA manifests satisfy machine-readable marking obligations. Full compliance deadline August 2, 2026.',
  '/content-provenance/eu-ai-act',
  undefined,
  undefined,
  'Meet EU AI Act Article 50 before August 2026. C2PA-ready.'
);

export default function EuAiActPage() {
  const techArticle = getTechArticleSchema({
    title: 'EU AI Act and Content Provenance',
    description: 'EU AI Act Article 50 transparency requirements for AI-generated content. C2PA manifests satisfy machine-readable marking obligations. Full compliance deadline August 2, 2026.',
    url: `${siteConfig.url}/content-provenance/eu-ai-act`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'What does the EU AI Act require for AI-generated content?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'EU AI Act Article 50 requires providers of certain AI systems to implement technical solutions ensuring AI-generated content is marked as such in a machine-readable format. This applies to systems generating synthetic audio, video, images, and text intended for public communication. The requirement is for machine-readable marking, not just visible disclosure. C2PA manifests satisfy this requirement by embedding structured metadata identifying the generating AI system, generation timestamp, and AI-generation status.',
        },
      },
      {
        '@type': 'Question',
        name: 'Who is subject to EU AI Act Article 50?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Article 50 applies to providers of AI systems that generate synthetic content and to operators who deploy those systems for public-facing applications. Any organization providing AI writing tools, image generation, audio synthesis, or video generation to users in the EU is subject to these requirements, regardless of where the organization is headquartered. EU AI Act jurisdiction follows the location of users, not the location of the AI provider.',
        },
      },
      {
        '@type': 'Question',
        name: 'What is the EU AI Act compliance deadline?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'The full compliance deadline for EU AI Act Article 50 is August 2, 2026. Some provisions of the EU AI Act took effect earlier: prohibited AI practices were banned from February 2, 2025, and obligations for general-purpose AI model providers began applying from August 2, 2025. Article 50 transparency obligations for AI-generated content take full effect on August 2, 2026.',
        },
      },
      {
        '@type': 'Question',
        name: 'Do C2PA manifests satisfy EU AI Act marking requirements?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'C2PA manifests are the industry standard implementation for machine-readable AI content marking. A C2PA manifest embedded in AI-generated content identifies the content as AI-generated, records the generating system, and includes a generation timestamp. The C2PA standard is supported by over 200 organizations including Adobe, Microsoft, Google, and BBC. Confirm with legal counsel that your specific implementation satisfies your jurisdiction\'s requirements under the EU AI Act.',
        },
      },
    ],
  };

  return (
    <>
      <AISummary
        title="EU AI Act and Content Provenance"
        whatWeDo="Encypher provides C2PA manifest embedding for AI-generated content that satisfies EU AI Act Article 50 machine-readable marking requirements. API and SDK tooling for compliant output marking before the August 2, 2026 deadline."
        whoItsFor="AI system providers, AI product operators, and enterprises deploying AI writing, image generation, or synthetic media tools for users in the European Union. Any organization subject to EU AI Act transparency obligations."
        keyDifferentiator="C2PA manifests are the industry standard for machine-readable AI content marking. Over 200 organizations including OpenAI, Google, and Microsoft participate in C2PA. The standard is open, the verification libraries are open source, and regulators can verify compliance independently."
        primaryValue="Machine-readable AI content marking that satisfies EU AI Act Article 50 before the August 2, 2026 deadline. One integration covers text, images, audio, and video requirements."
        pagePath="/content-provenance/eu-ai-act"
        pageType="WebPage"
      />

      <Script
        id="tech-article-eu-ai-act"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />
      <Script
        id="faq-eu-ai-act"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <ArticleShell path="/content-provenance/eu-ai-act">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Content Provenance', href: '/content-provenance' },
          { name: 'EU AI Act', href: '/content-provenance/eu-ai-act' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          EU AI Act and Content Provenance
        </h1>
        <p className="text-xl text-muted-foreground mb-4">
          The EU AI Act requires machine-readable marking of AI-generated content.
          The compliance deadline is August 2, 2026. C2PA manifests are the
          industry-standard implementation.
        </p>
        <div className="p-4 bg-muted/30 rounded-lg border border-border mb-12">
          <p className="font-semibold">Key date: August 2, 2026</p>
          <p className="text-muted-foreground text-sm mt-1">
            Full EU AI Act Article 50 transparency obligations take effect. Organizations
            with EU users that generate AI content for public audiences need compliant
            marking infrastructure in place.
          </p>
        </div>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Regulatory Framework</h2>
          <p className="text-muted-foreground mb-4">
            The EU AI Act (Regulation (EU) 2024/1689) establishes a risk-based framework
            for AI regulation across the European Union. For content provenance, the
            relevant provisions are Article 50 (transparency obligations) and the
            supporting technical specifications.
          </p>
          <p className="text-muted-foreground mb-4">
            Article 50 covers two categories of obligation. First, providers of AI systems
            that interact with natural persons must ensure those systems identify themselves
            as AI - covering chatbots, virtual assistants, and AI customer service agents.
            Second, providers of AI systems that generate synthetic audio, video, images, and
            text must implement technical solutions to ensure outputs are marked as
            AI-generated in a machine-readable format.
          </p>
          <p className="text-muted-foreground mb-4">
            The text provision is specific: it applies to AI-generated text published for
            the purpose of informing the public on matters of public interest, such as news
            articles, opinion pieces, and other editorial content. This exempts narrow uses
            like authorized testing and AI-assisted human writing where the AI role is
            editing rather than generation.
          </p>
          <p className="text-muted-foreground">
            The EU AI Act applies to any organization providing or deploying AI systems
            to users in the EU, regardless of where the organization is headquartered.
            An American AI company with European users is subject to Article 50 requirements.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">What Machine-Readable Marking Requires</h2>
          <p className="text-muted-foreground mb-4">
            The EU AI Act requires marking that is machine-readable, meaning it can be
            processed by software without human interpretation. A visible label saying
            "Generated by AI" satisfies transparency for human readers but does not
            satisfy the machine-readable requirement alone.
          </p>
          <p className="text-muted-foreground mb-4">
            Machine-readable marking must be embedded in or attached to the content in a
            structured format that allows automated verification. The EU AI Act does not
            prescribe a specific technical standard, but the recitals reference interoperability
            and the importance of standards. C2PA is the industry consensus implementation.
          </p>
          <p className="text-muted-foreground mb-4">
            A C2PA manifest embedded in AI-generated content records:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>That the content is AI-generated (action: c2pa.ai.generated)</li>
            <li>The generating system identity (AI model and version)</li>
            <li>Generation timestamp (tamper-evident)</li>
            <li>Content hash (detects subsequent modification)</li>
            <li>Publisher or deployer identity (organizational certificate)</li>
          </ul>
          <p className="text-muted-foreground">
            This information is verifiable by any party - regulators, auditors, platform
            operators - using open-source C2PA libraries, without requiring access to
            proprietary systems.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Article 50 Implementation Guide</h2>
          <p className="text-muted-foreground mb-4">
            Implementing Article 50 compliance with Encypher requires integration at the
            AI content generation step. The integration pattern differs by content type:
          </p>
          <div className="space-y-4 mb-4">
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Text Content</h3>
              <p className="text-muted-foreground text-sm">
                After AI text generation, before publishing or distributing the content,
                call the Encypher signing API with the generated text. The API returns
                the text with embedded C2PA manifest markers. Publish the signed version.
                The manifest identifies the content as AI-generated and records the
                generation metadata.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Image Content</h3>
              <p className="text-muted-foreground text-sm">
                Pass the AI-generated image file to the signing API. The API returns the
                image with an embedded C2PA JUMBF manifest in the file container. Supported
                formats include JPEG, PNG, WebP, TIFF, AVIF, and HEIC. The manifest records
                the AI-generation action with generating system identity.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Audio and Video Content</h3>
              <p className="text-muted-foreground text-sm">
                Audio and video files are signed with C2PA manifests embedded in their
                container structures (ISO BMFF uuid boxes for MP4/MOV/M4A, RIFF chunks
                for WAV/AVI, ID3 GEOB frames for MP3). The manifest records the AI-generation
                event and generating system.
              </p>
            </div>
          </div>
          <p className="text-muted-foreground">
            A single Encypher API integration handles all content types. The SDK supports
            Python and TypeScript with client libraries wrapping the REST API. Batch endpoints
            handle signing at scale.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Compliance Timeline and Penalties</h2>
          <p className="text-muted-foreground mb-4">
            The EU AI Act's compliance timeline has four phases:
          </p>
          <ul className="space-y-3 mb-4">
            <li className="flex gap-3">
              <span className="font-mono text-sm bg-muted px-2 py-1 rounded h-fit whitespace-nowrap">Feb 2025</span>
              <p className="text-muted-foreground text-sm">Prohibited AI practices banned (social scoring, biometric surveillance, manipulation)</p>
            </li>
            <li className="flex gap-3">
              <span className="font-mono text-sm bg-muted px-2 py-1 rounded h-fit whitespace-nowrap">Aug 2025</span>
              <p className="text-muted-foreground text-sm">General-purpose AI model obligations begin (capability thresholds, copyright summaries, red-team testing)</p>
            </li>
            <li className="flex gap-3">
              <span className="font-mono text-sm bg-muted px-2 py-1 rounded h-fit whitespace-nowrap">Aug 2026</span>
              <p className="text-muted-foreground text-sm">Full Article 50 transparency obligations including machine-readable AI content marking</p>
            </li>
            <li className="flex gap-3">
              <span className="font-mono text-sm bg-muted px-2 py-1 rounded h-fit whitespace-nowrap">Aug 2027</span>
              <p className="text-muted-foreground text-sm">High-risk AI system obligations for certain sectors</p>
            </li>
          </ul>
          <p className="text-muted-foreground mb-4">
            Penalties for non-compliance with transparency obligations run up to 15 million
            euros or 3 percent of worldwide annual turnover, whichever is higher. For large
            AI providers, the financial exposure is material.
          </p>
          <p className="text-muted-foreground">
            Enterprise implementation of C2PA signing typically requires 60-90 days including
            API integration, workflow modification, and testing. Organizations that wait until
            close to the August 2026 deadline will face compressed implementation timelines
            during a period of peak demand for compliance services.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Content Creators' Perspective</h2>
          <p className="text-muted-foreground mb-4">
            The EU AI Act's Article 50 requirements benefit human content creators as well as
            creating obligations for AI providers. When AI-generated content is marked,
            human-authored content that is not marked becomes distinguishable from it.
          </p>
          <p className="text-muted-foreground mb-4">
            Publishers, journalists, and authors who sign their human-authored content with
            C2PA provenance create a documented distinction from AI-generated content. A
            news outlet with a signed archive of human-authored journalism can demonstrate
            the distinction between their original reporting and AI-generated summaries.
            This distinction has commercial value in an environment where readers increasingly
            want to know which content is human-authored.
          </p>
          <p className="text-muted-foreground">
            The EU AI Act does not require human-authored content to be marked. But the
            availability of C2PA infrastructure creates the practical ability to make that
            distinction, and the incentive to do so grows as AI-generated content proliferates.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/content-provenance/for-enterprises" className="underline hover:no-underline">Content Provenance for Enterprises</Link></li>
            <li><Link href="/content-provenance/for-ai-companies" className="underline hover:no-underline">Content Provenance for AI Companies</Link></li>
            <li><Link href="/c2pa-standard" className="underline hover:no-underline">The C2PA Standard</Link></li>
            <li><Link href="/c2pa-standard/members" className="underline hover:no-underline">C2PA Members</Link></li>
            <li><Link href="/content-provenance" className="underline hover:no-underline">Content Provenance: The Definitive Guide</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">EU AI Act Compliance Infrastructure</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Enterprise implementation requires 60-90 days. The August 2, 2026 deadline
            is your planning horizon. Start with the API and SDK documentation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/contact">Talk to Enterprise Sales</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/try">Start Free</Link>
            </Button>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
