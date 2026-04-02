import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'Content Provenance for Publishers | Encypher',
  'Proof of origin that travels with every article, image, and document you distribute. Eliminate the "we did not know" defense. Build licensing leverage with cryptographic evidence.',
  '/content-provenance/for-publishers'
);

export default function ForPublishersPage() {
  const techArticle = getTechArticleSchema({
    title: 'Content Provenance for Publishers',
    description: 'Proof of origin that travels with every article, image, and document you distribute. Eliminate the "we did not know" defense. Build licensing leverage with cryptographic evidence.',
    url: `${siteConfig.url}/content-provenance/for-publishers`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'How does content provenance protect publishers from unauthorized AI use?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Encypher embeds a C2PA manifest into each article and image at the moment of publication. The manifest records publisher identity, publication timestamp, and machine-readable rights terms. When an AI company ingests the content, the manifest travels with it. That creates a documented record that the company received content with explicit ownership metadata, eliminating any claim that they did not know the content was owned.',
        },
      },
      {
        '@type': 'Question',
        name: 'What is willful infringement and why does it matter for publishers?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Under US copyright law, willful infringement carries statutory damages up to $150,000 per work, compared to $30,000 for innocent infringement. "Innocent" means the infringer did not know the work was protected. When content carries embedded provenance with rights terms, any party that uses it cannot credibly claim ignorance. The embedded manifest is formal notice. This shifts every AI copyright dispute from an innocent infringement defense to a willful infringement claim.',
        },
      },
      {
        '@type': 'Question',
        name: 'Does provenance survive wire service distribution and aggregator scraping?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'For text content, yes. Encypher embeds provenance using invisible provenance markers that survive copy-paste, syndication, and re-publication. When AP or Reuters distributes your story to 1,500 subscribers, the provenance markers travel with every copy. For images, C2PA manifests are embedded in the file container and travel with downloads. Both methods give publishers a chain of custody that persists outside their own infrastructure.',
        },
      },
      {
        '@type': 'Question',
        name: 'Can publishers sign their existing archive, not just new content?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Yes. The Encypher API and SDK batch tools let you sign thousands of existing articles in a single overnight job. The Python and TypeScript SDKs provide batch signing utilities. The free tier covers 1,000 documents per month. Volume pricing is available for publishers with large archives.',
        },
      },
    ],
  };

  return (
    <>
      <AISummary
        title="Content Provenance for Publishers"
        whatWeDo="Encypher embeds cryptographic C2PA provenance into articles, images, and documents at publication, creating tamper-evident proof of origin that travels with content through wire services, aggregators, and AI ingestion pipelines."
        whoItsFor="News publishers, wire services, trade publishers, and independent media organizations that distribute content through B2B channels and whose archives are at risk of unauthorized AI training use."
        keyDifferentiator="Provenance that survives distribution. Text provenance uses invisible provenance markers at the character level. Image provenance uses C2PA manifests embedded in the file container. Both methods create chain of custody that persists outside publisher-controlled infrastructure."
        primaryValue="Eliminate the 'we did not know' defense in AI licensing disputes. Convert innocent infringement claims to willful infringement claims. Build licensing leverage before litigation is necessary."
        pagePath="/content-provenance/for-publishers"
        pageType="WebPage"
      />

      <Script
        id="tech-article-for-publishers"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />
      <Script
        id="faq-for-publishers"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <ArticleShell path="/content-provenance/for-publishers">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Content Provenance', href: '/content-provenance' },
          { name: 'For Publishers', href: '/content-provenance/for-publishers' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Content Provenance for Publishers
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          Every article and image you publish can now carry cryptographic proof of origin.
          That proof travels through wire services and aggregators.
          It cannot be stripped without breaking verification.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Problem: Distribution Without Documentation</h2>
          <p className="text-muted-foreground mb-4">
            A publisher sends a story to AP, which distributes it to 1,500 subscribers worldwide.
            Three months later, that story appears in an AI company's training corpus with no
            attribution, no license, and no payment. The AI company claims they had no way to know
            the content was owned.
          </p>
          <p className="text-muted-foreground mb-4">
            That claim is difficult to contest when the only proof of ownership is a byline in HTML
            that was stripped during ingestion. Traditional metadata, EXIF data, and even watermarks
            visible to human eyes can be removed without detection. Once the header is gone, so is
            the ownership record.
          </p>
          <p className="text-muted-foreground">
            Content provenance solves this at the infrastructure level. The ownership record is
            embedded cryptographically into the content itself - not in a field that can be deleted,
            but in the structure of the text and the file container. Removing it requires deliberately
            modifying the content, which breaks verification and creates its own evidentiary record.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">How Provenance Works for Text</h2>
          <p className="text-muted-foreground mb-4">
            Encypher uses two complementary encoding modes for text provenance. The default mode
            embeds C2PA manifest data invisibly within text content. The encoding is undetectable
            to readers and survives copy-paste across digital platforms.
          </p>
          <p className="text-muted-foreground mb-4">
            The alternative path uses Zero Width Characters for environments like Microsoft Word
            that handle certain Unicode ranges differently. Both paths produce invisible output
            that reads identically to the naked eye. Both survive copy-paste across browsers,
            email clients, and text editors.
          </p>
          <p className="text-muted-foreground mb-4">
            The manifest embedded in each article records:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>Publisher identity (verified cryptographic key)</li>
            <li>Publication timestamp (tamper-evident)</li>
            <li>Content hash (detects any modification)</li>
            <li>Rights terms (machine-readable, supports Bronze/Silver/Gold tiers)</li>
            <li>Author attribution (sentence-level granularity)</li>
          </ul>
          <p className="text-muted-foreground">
            Sentence-level granularity is Encypher's proprietary technology. It authenticates
            each sentence individually using a Merkle tree structure, so verification can confirm
            not just that a document was published but which specific sentences were used - critical
            for licensing disputes involving partial reproduction.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Wire Service Distribution</h2>
          <p className="text-muted-foreground mb-4">
            Wire services distribute content at scale to hundreds or thousands of subscribers.
            Each copy is a potential licensing event and each copy can now carry the same
            cryptographic record as the original.
          </p>
          <p className="text-muted-foreground mb-4">
            The Encypher API supports organizational signing, where a wire service signs content
            on behalf of member publishers using delegated credentials. AP can sign content for
            its member newspapers. Reuters can sign its own wire feeds. Each signed asset carries
            the originating publisher's identity, even when signing occurs at the distribution layer.
          </p>
          <p className="text-muted-foreground">
            This means the provenance chain is established at the point of widest distribution,
            not just at the original publication. Every downstream subscriber receives content
            with embedded proof of origin, machine-readable rights terms, and a verified
            publishing timestamp.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Willful Infringement Shift</h2>
          <p className="text-muted-foreground mb-4">
            US copyright law treats willful infringement differently from innocent infringement.
            Innocent infringement means the infringer did not know the work was protected.
            Willful means they knew, or should have known, and infringed anyway.
          </p>
          <p className="text-muted-foreground mb-4">
            Statutory damages under 17 U.S.C. 504 run up to $30,000 per work for innocent
            infringement and up to $150,000 per work for willful infringement. For a publisher
            with thousands of articles in an AI training corpus, that difference is the difference
            between a nuisance claim and a material liability.
          </p>
          <p className="text-muted-foreground mb-4">
            When content carries a C2PA manifest with machine-readable rights terms, any party
            that uses the content cannot credibly claim they did not know it was owned. The
            manifest is formal notice, embedded in every copy, in every downstream location.
            The "we did not know" defense is eliminated before the lawsuit is filed.
          </p>
          <p className="text-muted-foreground">
            Publishers who have signed their archives hold a fundamentally different legal
            position than those who have not. The signed archive is not just a compliance
            artifact - it is the documentation that supports a willful infringement argument
            if licensing negotiations fail.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Licensing Leverage Before Litigation</h2>
          <p className="text-muted-foreground mb-4">
            Litigation is expensive and slow. Most publishers want licensing revenue, not court
            battles. Content provenance supports licensing by making the ownership case
            self-evident before any formal dispute begins.
          </p>
          <p className="text-muted-foreground mb-4">
            When an AI company receives a formal notice with an Encypher evidence package, they
            receive cryptographic proof that is independently verifiable - it does not depend
            on trusting Encypher or the publisher's assertions. The verification libraries are
            open source. The signature was made against the publisher's own key. The AI company's
            legal team can verify every claim in the package without third-party involvement.
          </p>
          <p className="text-muted-foreground">
            This changes the negotiating dynamic. Instead of a publisher asserting ownership
            and an AI company disputing it, the dispute is over licensing terms on content
            whose provenance is already documented. That is a more tractable negotiation,
            and it typically resolves faster.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Image Provenance</h2>
          <p className="text-muted-foreground mb-4">
            Encypher supports 13 image formats including JPEG, PNG, WebP, TIFF, AVIF, HEIC,
            and DNG. C2PA manifests are embedded in the file container - a JUMBF box appended
            to the file structure in a format-specific way defined by the C2PA specification.
          </p>
          <p className="text-muted-foreground mb-4">
            EXIF metadata is routinely stripped when images are uploaded to social platforms,
            aggregators, and CDNs. C2PA manifests are not EXIF data. They are embedded in
            the file container itself and survive most distribution pathways. When an image
            is downloaded and re-uploaded, the manifest travels with the file.
          </p>
          <p className="text-muted-foreground">
            For publishers whose photojournalists' work ends up on social platforms and in
            AI image generation training sets, image provenance creates a documented ownership
            record for every frame. See <Link href="/content-provenance/images" className="underline hover:no-underline">image provenance</Link> for
            format-specific details.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Signing Your Archive</h2>
          <p className="text-muted-foreground mb-4">
            The most valuable content for AI training is often the oldest - years of reporting,
            analysis, and photography accumulated before anyone thought to protect it. The
            Encypher API supports retroactive signing of existing archives.
          </p>
          <p className="text-muted-foreground mb-4">
            Batch signing tools in the Python and TypeScript SDKs let you sign thousands of
            articles in a single job. A publisher with 500,000 articles in their CMS can
            typically complete a full archive signing over a weekend. The free tier covers
            1,000 documents per month. Volume pricing is available for publishers with
            large archives.
          </p>
          <p className="text-muted-foreground">
            Retroactive signing does not change the publication date in the manifest. The
            manifest records when signing occurred, separate from the original publication
            date. This distinction matters for licensing - the manifest documents that the
            content existed and was owned as of the signing date, which is sufficient for
            most dispute resolution purposes.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/content-provenance" className="underline hover:no-underline">Content Provenance: The Definitive Guide</Link></li>
            <li><Link href="/content-provenance/text" className="underline hover:no-underline">Text Provenance: Technical Deep Dive</Link></li>
            <li><Link href="/content-provenance/images" className="underline hover:no-underline">Image Provenance: 13 Supported Formats</Link></li>
            <li><Link href="/content-provenance/vs-content-detection" className="underline hover:no-underline">Content Provenance vs. Content Detection</Link></li>
            <li><Link href="/cryptographic-watermarking/legal-implications" className="underline hover:no-underline">Legal Implications of Cryptographic Watermarking</Link></li>
            <li><Link href="/content-provenance/news-publishers" className="underline hover:no-underline">Content Provenance for News Publishers</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Start Signing Your Content</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            The free tier covers 1,000 documents per month. No credit card required.
            Start signing today and your archive begins building its ownership record.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/try">Start Free</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/contact">Talk to Sales</Link>
            </Button>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
