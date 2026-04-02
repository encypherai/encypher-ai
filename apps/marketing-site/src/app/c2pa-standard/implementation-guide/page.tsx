import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import AISummary from '@/components/seo/AISummary';
import { ArticleShell } from '@/components/content/ArticleShell';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'C2PA Implementation Guide for Developers | Encypher API | Encypher',
  'Developer guide for C2PA implementation via the Encypher API. Quickstart with curl, Python SDK, TypeScript SDK, and free verification. Sign text, images, audio, and video.',
  '/c2pa-standard/implementation-guide'
);

export default function ImplementationGuidePage() {
  const techArticle = getTechArticleSchema({
    title: 'C2PA Implementation Guide for Developers',
    description: 'Developer guide for C2PA implementation via the Encypher API. Quickstart with curl, Python SDK, TypeScript SDK, and free verification.',
    url: `${siteConfig.url}/c2pa-standard/implementation-guide`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="C2PA Implementation Guide for Developers"
        whatWeDo="Encypher provides a REST API, Python SDK, and TypeScript SDK for implementing C2PA content provenance. Sign text, images, audio, and video. Verify any C2PA-signed content for free."
        whoItsFor="Developers integrating content provenance into CMS platforms, AI pipelines, media publishing systems, and document management tools. Engineers building C2PA compliance into AI output systems."
        keyDifferentiator="One API covers all 31 supported MIME types. Sentence-level Merkle tree authentication for text (not available from other providers). Free verification endpoint requires no authentication. Python and TypeScript SDKs with batch processing support."
        primaryValue="API quickstart in under 5 minutes. Free tier covers 1,000 documents per month. Verification is free with no account required. Open-source SDK implementations available."
        pagePath="/c2pa-standard/implementation-guide"
        pageType="WebPage"
      />

      <Script
        id="tech-article-implementation-guide"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <ArticleShell path="/c2pa-standard/implementation-guide">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'C2PA Standard', href: '/c2pa-standard' },
          { name: 'Implementation Guide', href: '/c2pa-standard/implementation-guide' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          C2PA Implementation Guide
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          From zero to signed content in five minutes. REST API, Python SDK, and TypeScript SDK.
          Free verification for any C2PA-signed content, no account required.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">API Quickstart</h2>
          <p className="text-muted-foreground mb-4">
            Sign text content with a single API call. Get your API key at{' '}
            <Link href="/try" className="underline hover:no-underline">encypher.com/try</Link> (free tier, no credit card).
          </p>

          <h3 className="text-lg font-semibold mb-3">Sign Text</h3>
          <div className="bg-muted/30 rounded-lg p-4 font-mono text-sm mb-6">
            <p className="text-muted-foreground mb-2"># Sign a text document</p>
            <p className="mb-1">curl -X POST https://api.encypher.com/v1/sign \</p>
            <p className="mb-1 ml-4">-H "Authorization: Bearer ey_your_key_here" \</p>
            <p className="mb-1 ml-4">-H "Content-Type: application/json" \</p>
            <p className="ml-4">{`-d '{"text": "Your article content here.", "metadata": {"author": "Jane Smith", "rights": "bronze"}}'`}</p>
          </div>

          <h3 className="text-lg font-semibold mb-3">Sign an Image</h3>
          <div className="bg-muted/30 rounded-lg p-4 font-mono text-sm mb-6">
            <p className="text-muted-foreground mb-2"># Sign an image file</p>
            <p className="mb-1">curl -X POST https://api.encypher.com/v1/sign/media \</p>
            <p className="mb-1 ml-4">-H "Authorization: Bearer ey_your_key_here" \</p>
            <p className="ml-4">-F "file=@photo.jpg"</p>
          </div>

          <h3 className="text-lg font-semibold mb-3">Verify (no auth required)</h3>
          <div className="bg-muted/30 rounded-lg p-4 font-mono text-sm mb-6">
            <p className="text-muted-foreground mb-2"># Verify any C2PA-signed content</p>
            <p className="mb-1">curl -X POST https://api.encypher.com/v1/verify \</p>
            <p className="mb-1 ml-4">-H "Content-Type: application/json" \</p>
            <p className="ml-4">{`-d '{"text": "Content to verify here."}'`}</p>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Python SDK</h2>
          <div className="bg-muted/30 rounded-lg p-4 font-mono text-sm mb-4">
            <p className="text-muted-foreground mb-2"># Install</p>
            <p className="mb-4">pip install encypher</p>
            <p className="text-muted-foreground mb-2"># Sign text with sentence-level provenance</p>
            <p className="mb-1">from encypher import EncypherClient</p>
            <p className="mb-4">{``}</p>
            <p className="mb-1">client = EncypherClient(api_key="ey_your_key_here")</p>
            <p className="mb-4">{``}</p>
            <p className="mb-1">result = client.sign_text(</p>
            <p className="mb-1 ml-4">text="Your article content here.",</p>
            <p className="mb-1 ml-4">author="Jane Smith",</p>
            <p className="mb-1 ml-4">rights="bronze"</p>
            <p className="mb-4">)</p>
            <p className="mb-4">signed_text = result.text  # Contains invisible provenance markers</p>
            <p className="text-muted-foreground mb-2"># Verify</p>
            <p className="mb-1">verification = client.verify_text(signed_text)</p>
            <p>print(verification.signer, verification.timestamp)</p>
          </div>
          <p className="text-muted-foreground mb-4">
            The Python SDK wraps the REST API with typed interfaces for all signing and
            verification operations. Batch utilities allow processing thousands of documents:
          </p>
          <div className="bg-muted/30 rounded-lg p-4 font-mono text-sm">
            <p className="text-muted-foreground mb-2"># Batch sign articles from CMS</p>
            <p className="mb-1">articles = cms.get_all_articles()  # Your CMS client</p>
            <p className="mb-1">results = client.sign_batch(</p>
            <p className="mb-1 ml-4">items=[{`{"text": a.body, "id": a.id}`} for a in articles],</p>
            <p className="mb-1 ml-4">concurrency=20</p>
            <p>)</p>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">TypeScript SDK</h2>
          <div className="bg-muted/30 rounded-lg p-4 font-mono text-sm mb-4">
            <p className="text-muted-foreground mb-2">// Install</p>
            <p className="mb-4">npm install @encypher/sdk</p>
            <p className="text-muted-foreground mb-2">// Sign text content</p>
            <p className="mb-1">import {`{ EncypherClient }`} from '@encypher/sdk';</p>
            <p className="mb-4">{``}</p>
            <p className="mb-1">const client = new EncypherClient({`{ key: 'ey_your_key_here' }`});</p>
            <p className="mb-4">{``}</p>
            <p className="mb-1">const result = await client.signText({`{`}</p>
            <p className="mb-1 ml-4">text: 'Your article content here.',</p>
            <p className="mb-1 ml-4">author: 'Jane Smith',</p>
            <p className="mb-1 ml-4">rights: 'bronze',</p>
            <p className="mb-4">{`});`}</p>
            <p className="text-muted-foreground mb-2">// Verify (no API key needed)</p>
            <p className="mb-1">const verification = await client.verifyText(result.text);</p>
            <p>console.log(verification.signer, verification.timestamp);</p>
          </div>
          <p className="text-muted-foreground">
            The TypeScript SDK provides full type definitions for all API responses.
            Compatible with Node.js and browser environments. The verification function
            works without an API key using the public verification endpoint.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">CMS Integration Patterns</h2>
          <p className="text-muted-foreground mb-4">
            The most common integration pattern is signing at publish time via a CMS webhook.
            When an article is published, the CMS fires a webhook to your signing service,
            which calls the Encypher API and updates the stored article with the signed version.
          </p>
          <div className="space-y-4">
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">WordPress</h3>
              <p className="text-muted-foreground text-sm">Hook into the publish_post action. Call the Encypher signing API with the post content. Update the post with the signed content before the response is sent.</p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Contentful / Headless CMS</h3>
              <p className="text-muted-foreground text-sm">Subscribe to the ContentPublished webhook. In the handler, retrieve the content, sign it, and update the entry via the Management API. The signed version is served to readers.</p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Next.js / Static Generation</h3>
              <p className="text-muted-foreground text-sm">Sign content in getStaticProps or at build time. The signed content is baked into the static output. No runtime signing required for static sites.</p>
            </div>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Signing Options Reference</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 pr-4 font-semibold">Parameter</th>
                  <th className="text-left py-3 pr-4 font-semibold">Type</th>
                  <th className="text-left py-3 font-semibold">Description</th>
                </tr>
              </thead>
              <tbody className="text-muted-foreground">
                <tr className="border-b border-border/50">
                  <td className="py-3 pr-4 font-mono text-xs">text / file</td>
                  <td className="py-3 pr-4 font-mono text-xs">string / file</td>
                  <td className="py-3 text-xs">Content to sign. Text for articles; multipart file for media.</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 pr-4 font-mono text-xs">author</td>
                  <td className="py-3 pr-4 font-mono text-xs">string</td>
                  <td className="py-3 text-xs">Author name or identifier. Included in manifest assertion.</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 pr-4 font-mono text-xs">rights</td>
                  <td className="py-3 pr-4 font-mono text-xs">bronze | silver | gold</td>
                  <td className="py-3 text-xs">Machine-readable rights tier for AI licensing.</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 pr-4 font-mono text-xs">encoding</td>
                  <td className="py-3 pr-4 font-mono text-xs">vs | zwc</td>
                  <td className="py-3 text-xs">VS markers (default) or ZWC markers (Word-safe). Text only.</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 pr-4 font-mono text-xs">sentence_level</td>
                  <td className="py-3 pr-4 font-mono text-xs">boolean</td>
                  <td className="py-3 text-xs">Enable Merkle tree per-sentence authentication. Default true.</td>
                </tr>
                <tr>
                  <td className="py-3 pr-4 font-mono text-xs">fingerprint</td>
                  <td className="py-3 pr-4 font-mono text-xs">string</td>
                  <td className="py-3 text-xs">Recipient ID for distribution fingerprinting. Enterprise tier only.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Free Tier and Limits</h2>
          <p className="text-muted-foreground mb-4">
            The free tier provides 1,000 signing operations per month. Verification is
            unlimited and free at all tiers including without any account. The free tier
            includes full API access, both SDK libraries, and sentence-level Merkle
            tree authentication.
          </p>
          <p className="text-muted-foreground">
            Paid tiers unlock higher volume limits, multi-media signing, fingerprinting,
            batch endpoints, and enterprise features including BYOK and on-premises deployment.
            See <Link href="/pricing" className="underline hover:no-underline">pricing</Link> for tier details.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/c2pa-standard" className="underline hover:no-underline">The C2PA Standard</Link></li>
            <li><Link href="/c2pa-standard/section-a7" className="underline hover:no-underline">C2PA Section A.7: Text Provenance</Link></li>
            <li><Link href="/c2pa-standard/manifest-structure" className="underline hover:no-underline">C2PA Manifest Structure</Link></li>
            <li><Link href="/content-provenance/verification" className="underline hover:no-underline">Verification: How It Works</Link></li>
            <li><Link href="/c2pa-standard/media-types" className="underline hover:no-underline">All 31 Supported Media Types</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Start Building</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Free API key, no credit card, up to 1,000 documents per month.
            Verification is always free.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/try">Get Your API Key</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/tools/verify">Try Verification</Link>
            </Button>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
