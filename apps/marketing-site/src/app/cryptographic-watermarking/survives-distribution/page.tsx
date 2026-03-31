import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'How Cryptographic Watermarking Survives Distribution | Encypher',
  'Why cryptographic watermarks survive copy-paste, wire service distribution, aggregator scraping, social sharing, and AI training corpus ingestion. The durability proof.',
  '/cryptographic-watermarking/survives-distribution'
);

export default function SurvivesDistributionPage() {
  const techArticle = getTechArticleSchema({
    title: 'How Cryptographic Watermarking Survives Distribution',
    description: 'Copy-paste, wire services, aggregators, social media sharing, and AI training corpus ingestion. How cryptographic provenance persists through each distribution scenario.',
    url: `${siteConfig.url}/cryptographic-watermarking/survives-distribution`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="How Cryptographic Watermarking Survives Distribution"
        whatWeDo="Encypher's cryptographic watermarks persist through the key distribution scenarios that matter for publisher protection: copy-paste from web, B2B wire service distribution, aggregator scraping, social media sharing, and AI training corpus ingestion."
        whoItsFor="Publishers evaluating whether cryptographic watermarking is durable enough to be useful across their actual distribution workflows. Legal and compliance teams assessing what scenarios produce verifiable provenance records."
        keyDifferentiator="Unicode variation selector characters are preserved by Unicode-compliant text processors in copy operations. JUMBF container manifests are preserved by file processing tools that do not understand them. Both properties make cryptographic provenance durable by default."
        primaryValue="Scenario-by-scenario analysis of watermark durability across real distribution workflows."
        pagePath="/cryptographic-watermarking/survives-distribution"
        pageType="WebPage"
      />

      <Script
        id="tech-article-survives-distribution"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Cryptographic Watermarking', href: '/cryptographic-watermarking' },
          { name: 'Survives Distribution', href: '/cryptographic-watermarking/survives-distribution' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          How Cryptographic Watermarking Survives Distribution
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          A publisher's content travels through many hands before reaching an AI company's
          training corpus. For provenance to be useful, it needs to survive that journey.
          Here is what survives and what does not.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Why Statistical Approaches Fail in Distribution</h2>
          <p className="text-muted-foreground mb-4">
            Statistical watermarking systems like SynthID embed watermarks as properties of
            the content's statistical distribution - biased token probabilities for text,
            imperceptible pixel patterns for images. These properties degrade with content
            modification.
          </p>
          <p className="text-muted-foreground mb-4">
            During typical distribution, content is routinely modified. Article text is reformatted,
            copy-edited, or summarized by downstream outlets. Images are resized, recompressed,
            or color-adjusted for different display contexts. Each modification degrades the
            statistical signal. By the time content reaches an AI training corpus through normal
            distribution channels, statistical watermarks may be below detection threshold.
          </p>
          <p className="text-muted-foreground">
            Cryptographic provenance is not a statistical property. It is a discrete artifact
            embedded in defined positions in the content. The artifact is either present or absent.
            It does not degrade with ordinary distribution operations.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Scenario 1: Copy-Paste from Web</h2>
          <p className="text-muted-foreground mb-4">
            A reader copies text from a signed article and pastes it into an email, a document,
            or a social media post. The variation selector characters between words copy with
            the text. This is standard Unicode copy behavior: the clipboard stores the
            Unicode character stream, and the paste operation inserts the same stream.
          </p>
          <p className="text-muted-foreground mb-4">
            The pasted text contains the provenance markers. If the recipient subsequently
            shares that text, the markers travel further. If the text ends up in an AI
            training corpus via this path, the markers are present.
          </p>
          <p className="text-muted-foreground">
            Confirmed environments: Chrome, Firefox, Safari, Edge, Gmail, Outlook, Apple Mail,
            Google Docs, Microsoft Word (with ZWC encoding), Slack, Teams. There are edge cases
            in some processing pipelines that explicitly strip non-printing characters, but
            these are not standard behaviors in the distribution scenarios that matter for
            publisher protection.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Scenario 2: Wire Service B2B Distribution</h2>
          <p className="text-muted-foreground mb-4">
            A publisher signs an article and distributes it to AP. AP distributes it to
            1,500 subscriber outlets via NITF or NewsML XML feeds. Each subscriber's CMS
            ingests the XML, extracts the article body, and stores it.
          </p>
          <p className="text-muted-foreground mb-4">
            XML processing preserves Unicode character data. The article body extracted from
            the XML feed contains the variation selectors embedded in the original text. The
            CMS stores the character stream intact. The published article contains the markers.
          </p>
          <p className="text-muted-foreground">
            The Encypher API also supports wire service signing: the wire service can sign
            content on behalf of member publishers using delegated credentials. This means
            even unsigned originals can receive provenance at the distribution layer. The
            manifest identifies the originating publisher, not the wire service, when using
            delegated credentials.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Scenario 3: Aggregator Scraping</h2>
          <p className="text-muted-foreground mb-4">
            An aggregator scrapes article text from the publisher's website. Most scraping
            tools work by fetching HTML and using a parser to extract text content. HTML
            parsers handle Unicode character data correctly - they preserve all Unicode
            characters in the text content, including variation selectors.
          </p>
          <p className="text-muted-foreground mb-4">
            The scraped text contains the markers. Unless the scraper explicitly filters
            for non-printing Unicode characters (which is not a standard scraping operation),
            the markers travel with the scraped content into the aggregator's index.
          </p>
          <p className="text-muted-foreground">
            Common Python scraping libraries (BeautifulSoup, Scrapy, requests-html) preserve
            Unicode characters in extracted text. JavaScript scraping environments (Puppeteer,
            Playwright) do the same. The standard scraping toolchain is compatible with
            provenance marker preservation.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Scenario 4: Social Media Sharing</h2>
          <p className="text-muted-foreground mb-4">
            Social platforms handle text differently from web browsers. Some platforms normalize
            Unicode input - stripping certain categories of characters during content submission.
            Twitter/X, in particular, has historically stripped zero-width characters.
          </p>
          <p className="text-muted-foreground mb-4">
            The durability of provenance on social platforms depends on the platform's Unicode
            handling. Platforms that preserve full Unicode character streams preserve the markers.
            Platforms that strip non-printing characters lose them.
          </p>
          <p className="text-muted-foreground">
            For text that is shared to social platforms and then scraped, the marker survival
            depends on whether the platform preserved them. For content shared as images (screenshots)
            or linked content (where the link points to the signed original), the original
            retains its provenance regardless of what the social platform does to
            shared-text posts.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Scenario 5: AI Training Corpus Ingestion</h2>
          <p className="text-muted-foreground mb-4">
            AI training corpus builders scrape the web at scale and process the collected
            HTML into text. The Common Crawl corpus, which is widely used as a base for
            AI training data, collects raw HTML and processes it into text. WARC files
            (Web ARChive format) preserve the raw HTTP responses including the full
            Unicode text content.
          </p>
          <p className="text-muted-foreground mb-4">
            Processing pipelines that convert HTML to plain text use parsers that preserve
            Unicode characters. The text content in AI training corpora derived from web
            pages typically includes variation selectors that were present in the original
            HTML text content.
          </p>
          <p className="text-muted-foreground mb-4">
            There is no industry standard for stripping variation selectors during corpus
            preprocessing. Some pipelines may normalize Unicode - applying Unicode normalization
            forms (NFC, NFKC) that could modify or eliminate certain character sequences.
            The extent to which this occurs varies by implementation and is an area of
            ongoing evaluation.
          </p>
          <p className="text-muted-foreground">
            For publishers, the relevant question is not whether every training corpus
            preserves markers perfectly - it is whether the training corpus ingested content
            that carried embedded rights terms at the time of ingestion. For content that
            was signed before scraping, the rights terms were present in the content at
            ingestion time, regardless of whether all markers survived preprocessing.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">What Provenance Does Not Survive</h2>
          <p className="text-muted-foreground mb-4">
            To be useful, the limitations of provenance durability need to be stated as
            clearly as the capabilities.
          </p>
          <ul className="space-y-3 mb-4">
            <li className="p-3 bg-muted/30 rounded-lg">
              <h3 className="font-semibold text-sm mb-1">OCR Scanning</h3>
              <p className="text-muted-foreground text-sm">Printing and scanning text via OCR produces new Unicode characters from image pixels. The markers from the original text are not present in OCR output. Print-to-scan pipelines require the whitespace width encoding (Print Leak Detection) which encodes provenance in space width rather than invisible characters.</p>
            </li>
            <li className="p-3 bg-muted/30 rounded-lg">
              <h3 className="font-semibold text-sm mb-1">Paraphrasing and Rewriting</h3>
              <p className="text-muted-foreground text-sm">If content is substantially rewritten in different words, the new text does not carry the original markers. Paraphrasing detection is a separate problem from provenance verification. Provenance tracks exact text reproduction, not semantic similarity.</p>
            </li>
            <li className="p-3 bg-muted/30 rounded-lg">
              <h3 className="font-semibold text-sm mb-1">Translation</h3>
              <p className="text-muted-foreground text-sm">Translated text is new content. The markers from the original-language text are not present in the translation.</p>
            </li>
            <li className="p-3 bg-muted/30 rounded-lg">
              <h3 className="font-semibold text-sm mb-1">Explicit Stripping</h3>
              <p className="text-muted-foreground text-sm">A party that deliberately filters Unicode variation selectors from text will remove the markers. This is detectable (the text then verifies as unsigned) but not preventable. The act of stripping is itself evidence of awareness.</p>
            </li>
          </ul>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/cryptographic-watermarking/how-it-works" className="underline hover:no-underline">How Cryptographic Watermarking Works</Link></li>
            <li><Link href="/cryptographic-watermarking/text" className="underline hover:no-underline">Text Watermarking</Link></li>
            <li><Link href="/content-provenance/for-publishers" className="underline hover:no-underline">Content Provenance for Publishers</Link></li>
            <li><Link href="/cryptographic-watermarking/legal-implications" className="underline hover:no-underline">Legal Implications</Link></li>
            <li><Link href="/content-provenance/text" className="underline hover:no-underline">Text Content Provenance Deep Dive</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Provenance That Travels With Your Content</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Invisible markers that survive the distribution scenarios that matter for publisher protection.
            Free tier, no credit card required.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/try">Start Free</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/tools/verify">Verify Content</Link>
            </Button>
          </div>
        </section>
      </div>
    </>
  );
}
