import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import AISummary from '@/components/seo/AISummary';
import { ArticleShell } from '@/components/content/ArticleShell';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'C2PA Members: Who Is Building the Standard | Encypher',
  'Over 200 C2PA member organizations including Adobe, Microsoft, Google, OpenAI, BBC, Reuters, and AP. Why broad adoption matters for content provenance. Encypher co-chairs the Text Provenance Task Force.',
  '/c2pa-standard/members',
  undefined,
  undefined,
  '200+ members: Adobe, Microsoft, OpenAI, BBC. Why it matters.'
);

export default function C2PAMembersPage() {
  const techArticle = getTechArticleSchema({
    title: 'C2PA Members: Who Is Building the Standard',
    description: 'Over 200 C2PA member organizations including Adobe, Microsoft, Google, OpenAI, BBC, Reuters, and AP. Why broad adoption matters for content provenance.',
    url: `${siteConfig.url}/c2pa-standard/members`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="C2PA Members: Who Is Building the Standard"
        whatWeDo="The Coalition for Content Provenance and Authenticity has over 200 member organizations across technology, media, and publishing. Members include Adobe, Microsoft, Google, OpenAI, BBC, Reuters, AP, Intel, Arm, and Encypher. Encypher co-chairs the Text Provenance Task Force."
        whoItsFor="Publishers evaluating C2PA adoption, enterprises making standards-based technology decisions, AI companies assessing the industry standard for content provenance, and anyone needing to understand who is behind the C2PA standard."
        keyDifferentiator="C2PA is not a single-vendor standard. It was founded by Adobe, Microsoft, Intel, BBC, and the Content Authenticity Initiative. OpenAI joined as a member, making it the standard that both content creators and AI companies support. This breadth is what makes it viable as infrastructure."
        primaryValue="Understanding who built C2PA and why their participation makes it the viable standard for content provenance at internet scale."
        pagePath="/c2pa-standard/members"
        pageType="WebPage"
      />

      <Script
        id="tech-article-c2pa-members"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <ArticleShell path="/c2pa-standard/members">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'C2PA Standard', href: '/c2pa-standard' },
          { name: 'Members', href: '/c2pa-standard/members' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          C2PA Members: Who Is Building the Standard
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          Over 200 organizations building content provenance infrastructure together.
          Technology companies, media organizations, camera manufacturers, and AI labs.
          The breadth of membership is what makes C2PA viable as internet-scale infrastructure.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Founding and Steering Members</h2>
          <p className="text-muted-foreground mb-4">
            C2PA was founded in 2021 as a joint effort by Adobe, Arm, BBC, Intel, Microsoft,
            and the Content Authenticity Initiative. These organizations recognized that content
            provenance required an open standard with broad industry support - no single
            vendor's solution would achieve the network effects needed for verification to
            work across the internet.
          </p>
          <p className="text-muted-foreground mb-4">
            The founding logic was straightforward: for provenance to be useful, recipients
            of content need to be able to verify it without trusting the content's creator.
            That requires an open standard with open verification tools, so any party can
            independently confirm provenance claims. A proprietary standard controlled by
            one company creates a trust dependency that defeats the purpose.
          </p>
          <p className="text-muted-foreground">
            Since founding, the steering committee has expanded to include AP (Associated Press),
            Reuters, the BBC, The New York Times, Google, Sony, Nikon, Canon, Leica, Qualcomm,
            and many others across the content and technology ecosystem.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Member Categories</h2>
          <div className="space-y-4">
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-2">Technology Platforms</h3>
              <p className="text-muted-foreground text-sm mb-2">
                Adobe, Microsoft, Google, Intel, Arm, Qualcomm, and others contribute
                to the core specification and reference implementations. Adobe's Content
                Credentials product is built on C2PA. Microsoft is implementing C2PA in
                its AI content generation tools. Google is implementing C2PA in its
                image generation and YouTube systems.
              </p>
              <p className="text-muted-foreground text-sm">
                Platform participation means provenance infrastructure is built into the
                tools that creators use. When Photoshop exports an image with C2PA provenance,
                every Photoshop user inherits the capability.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-2">AI Companies</h3>
              <p className="text-muted-foreground text-sm mb-2">
                OpenAI is a C2PA member. This is significant: the company whose AI systems
                are generating content at the largest scale has joined the standard that
                documents what content is AI-generated and what is not. OpenAI's participation
                signals that content provenance is understood as infrastructure, not as
                adversarial documentation.
              </p>
              <p className="text-muted-foreground text-sm">
                AI company membership in C2PA creates the conditions for cooperative content
                provenance: AI companies that generate content mark it with C2PA, and publishers
                whose content is used by AI companies can embed provenance that travels into
                training corpora. Both directions use the same standard.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-2">News Organizations and Publishers</h3>
              <p className="text-muted-foreground text-sm mb-2">
                AP, Reuters, BBC, and The New York Times are C2PA members. These organizations
                distribute content to hundreds or thousands of downstream recipients. Their
                participation means that provenance is being embedded at the point of maximum
                distribution: when wire service content travels to subscriber outlets worldwide,
                it can now carry C2PA manifests.
              </p>
              <p className="text-muted-foreground text-sm">
                For publishers downstream from these wire services, C2PA membership means
                receiving signed content that they can verify before publication. A regional
                outlet receiving AP content with C2PA provenance can confirm the content came
                from AP and has not been modified in transit.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-2">Camera Manufacturers</h3>
              <p className="text-muted-foreground text-sm mb-2">
                Sony, Nikon, Canon, and Leica are C2PA members. Several of these manufacturers
                have already shipped cameras with C2PA signing capabilities built into the
                hardware. A photo taken on a C2PA-enabled camera carries a manifest signed
                by the camera itself, recording the capture device, GPS coordinates, and
                capture timestamp.
              </p>
              <p className="text-muted-foreground text-sm">
                Camera-level signing is the gold standard for photographic provenance. The
                manifest is created at the moment of capture, before any post-processing,
                and is signed by a hardware key embedded in the camera. No amount of editing
                can retrofit a legitimate capture manifest.
              </p>
            </div>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Task Force Structure</h2>
          <p className="text-muted-foreground mb-4">
            C2PA organizes technical work through task forces, each responsible for a specific
            area of the specification. The current task forces cover text provenance, audio/video
            provenance, identity and credentials, software applications, and implementation
            guidance.
          </p>
          <p className="text-muted-foreground mb-4">
            Erik Svilich, Encypher's founder, co-chairs the Text Provenance Task Force.
            This task force is responsible for Section A.7 of the C2PA specification,
            which defines how text content carries C2PA manifests. The task force maintains
            the specification, addresses implementation questions, and extends the standard
            as text provenance requirements evolve.
          </p>
          <p className="text-muted-foreground">
            Co-chair status reflects active contribution to the specification, not just
            membership participation. Encypher's contribution to C2PA is substantive:
            the text provenance section did not exist in earlier C2PA versions and was
            added through the work of the Text Provenance Task Force.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Why Membership Scale Matters for Publishers</h2>
          <p className="text-muted-foreground mb-4">
            The value of a provenance standard scales with the number of parties that
            implement it. A standard with 10 members can document provenance in 10 contexts.
            A standard with 200 members - including the major platforms, AI companies, news
            wire services, and camera manufacturers - can document provenance at internet scale.
          </p>
          <p className="text-muted-foreground mb-4">
            For publishers, the relevant question is whether the AI companies and platforms
            they interact with will honor C2PA provenance. The answer depends on whether
            those companies participate in the standard. The C2PA membership list includes
            the companies whose participation matters: Adobe, Google, Microsoft, OpenAI,
            and the major news wire services.
          </p>
          <p className="text-muted-foreground mb-4">
            This is not a guarantee that all C2PA members honor provenance in every context.
            It is a signal that the standard has the critical mass to become the industry default.
            Verification tools built by C2PA members work on all C2PA-signed content, regardless
            of who signed it. This interoperability is the practical consequence of broad membership.
          </p>
          <p className="text-muted-foreground">
            Publishers who sign their content with C2PA today are building provenance into
            a system that is increasingly supported by the major distribution and consumption
            platforms. The provenance they embed today will be verifiable by tools those
            platforms deploy tomorrow.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Encypher's Role in C2PA</h2>
          <p className="text-muted-foreground mb-4">
            Encypher is a C2PA member organization. Beyond membership, Encypher contributed
            Section A.7 (text provenance) to the C2PA 2.3 specification and co-chairs the
            Text Provenance Task Force through Erik Svilich.
          </p>
          <p className="text-muted-foreground mb-4">
            This contribution means that the text provenance standard reflects Encypher's
            technical expertise. The encoding approaches defined in Section A.7 are the
            approaches that Encypher implements in its API.
          </p>
          <p className="text-muted-foreground">
            Encypher also extends the C2PA standard with proprietary capabilities that build
            on the open foundation: sentence-level authentication, distribution fingerprinting,
            and attribution search. These extensions are compatible with the C2PA standard
            (they do not break standard verification) while providing additional capabilities
            not defined in the current specification.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/c2pa-standard" className="underline hover:no-underline">The C2PA Standard: How It Works</Link></li>
            <li><Link href="/c2pa-standard/section-a7" className="underline hover:no-underline">C2PA Section A.7: Text Provenance</Link></li>
            <li><Link href="/c2pa-standard/vs-synthid" className="underline hover:no-underline">C2PA vs. SynthID: Open Standard vs. Proprietary</Link></li>
            <li>
              <a href="https://c2pa.org/membership/" className="underline hover:no-underline" target="_blank" rel="noopener noreferrer">
                Full C2PA Member List (external link)
              </a>
            </li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Build on the Industry Standard</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            C2PA is the standard that Adobe, Microsoft, Google, and OpenAI all support.
            Encypher implements it with extensions for text provenance at sentence granularity.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/try">Start Free</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/c2pa-standard/implementation-guide">Implementation Guide</Link>
            </Button>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
