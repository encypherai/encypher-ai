import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';
import { formats, categoryInfo, getFormatsByCategory } from '@/data/formats';

export const metadata: Metadata = seoMetadata(
  'C2PA Supported Media Types: All 31 MIME Types | Encypher',
  'Complete reference for all 31 MIME types supported with C2PA provenance. Images (13), Audio (6), Video (4), Documents (5), Fonts (3). Format-specific embedding details.',
  '/c2pa-standard/media-types'
);

export default function MediaTypesPage() {
  const techArticle = getTechArticleSchema({
    title: 'C2PA Supported Media Types: All 31 MIME Types',
    description: 'Complete reference for all 31 MIME types supported with C2PA provenance. Images (13), Audio (6), Video (4), Documents (5), Fonts (3).',
    url: `${siteConfig.url}/c2pa-standard/media-types`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  const imageFormats = getFormatsByCategory('image');
  const audioFormats = getFormatsByCategory('audio');
  const videoFormats = getFormatsByCategory('video');
  const documentFormats = getFormatsByCategory('document');
  const fontFormats = getFormatsByCategory('font');

  const categories = [
    { key: 'image' as const, formats: imageFormats },
    { key: 'audio' as const, formats: audioFormats },
    { key: 'video' as const, formats: videoFormats },
    { key: 'document' as const, formats: documentFormats },
    { key: 'font' as const, formats: fontFormats },
  ];

  return (
    <>
      <AISummary
        title="C2PA Supported Media Types"
        whatWeDo="Encypher supports C2PA provenance across 31 MIME types: 13 image formats, 6 audio formats, 4 video formats, 5 document formats, and 3 font formats. Each format has a specific embedding method defined by the C2PA specification."
        whoItsFor="Developers and integration engineers evaluating format coverage for content provenance. Publishers and enterprises determining whether their content types are supported."
        keyDifferentiator="31 MIME types in a single API. Format-specific embedding using container-native methods for each format type. Images use JUMBF, audio uses RIFF/ID3/ISO BMFF, video uses ISO BMFF, text uses Unicode variation selectors."
        primaryValue="Complete format coverage reference. All supported MIME types, embedding methods, and links to format-specific documentation."
        pagePath="/c2pa-standard/media-types"
        pageType="WebPage"
      />

      <Script
        id="tech-article-media-types"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'C2PA Standard', href: '/c2pa-standard' },
          { name: 'Media Types', href: '/c2pa-standard/media-types' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          C2PA Supported Media Types
        </h1>
        <p className="text-xl text-muted-foreground mb-4">
          All 31 MIME types supported with C2PA provenance embedding. One API, one key,
          all your content types.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-12">
          {Object.entries(categoryInfo).map(([key, info]) => (
            <div key={key} className="p-3 bg-muted/30 rounded-lg text-center">
              <div className="text-2xl font-bold">{info.count}</div>
              <div className="text-sm text-muted-foreground">{info.name}</div>
            </div>
          ))}
        </div>

        <section className="mb-4">
          <h2 className="text-2xl font-bold mb-2">How Embedding Differs by Format</h2>
          <p className="text-muted-foreground mb-8">
            C2PA uses container-native embedding methods for each format type. The manifest
            data is placed in the format-standard location for extension data, ensuring
            compatibility with existing tools that process each format.
          </p>
        </section>

        {categories.map(({ key, formats: catFormats }) => {
          const info = categoryInfo[key];
          return (
            <section key={key} className="mb-12">
              <h2 className="text-2xl font-bold mb-2">{info.name}</h2>
              <p className="text-muted-foreground mb-4 text-sm">{info.description}</p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 pr-4 font-semibold w-24">Format</th>
                      <th className="text-left py-3 pr-4 font-semibold">MIME Type</th>
                      <th className="text-left py-3 font-semibold">Embedding Method</th>
                    </tr>
                  </thead>
                  <tbody className="text-muted-foreground">
                    {catFormats.map((fmt, i) => (
                      <tr key={fmt.slug} className={i < catFormats.length - 1 ? 'border-b border-border/50' : ''}>
                        <td className="py-3 pr-4">
                          <Link
                            href={`/content-provenance/${fmt.slug}`}
                            className="font-medium text-foreground underline hover:no-underline"
                          >
                            {fmt.name}
                          </Link>
                        </td>
                        <td className="py-3 pr-4 font-mono text-xs">{fmt.mimeType}</td>
                        <td className="py-3 text-xs">{fmt.embeddingMethod}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          );
        })}

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Text Content</h2>
          <p className="text-muted-foreground mb-4">
            Unstructured text - articles, social posts, email, and any plain text - is covered
            by C2PA Section A.7, which Encypher contributed to the specification. Text does not
            have a file container, so provenance is embedded using invisible Unicode characters
            within the text itself.
          </p>
          <p className="text-muted-foreground">
            Text is not included in the MIME type table because it does not have a single MIME type
            - it covers text/plain, text/html content bodies, and any unstructured text context.
            See <Link href="/content-provenance/text" className="underline hover:no-underline">Text Content Provenance</Link> and <Link href="/c2pa-standard/section-a7" className="underline hover:no-underline">C2PA Section A.7</Link> for details.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Verification Pipeline</h2>
          <p className="text-muted-foreground mb-4">
            Encypher uses two verification pipelines depending on format:
          </p>
          <ul className="space-y-3 mb-4">
            <li className="flex gap-3 items-start">
              <span className="font-mono text-xs bg-muted px-2 py-1 rounded h-fit">c2pa-python-native</span>
              <p className="text-muted-foreground text-sm">Formats natively supported by the c2pa-python library: all 13 image formats, 4 of 6 audio formats (WAV, MP3, M4A, AAC, MPA), all 4 video formats. The c2pa-python library handles manifest extraction and signature verification directly.</p>
            </li>
            <li className="flex gap-3 items-start">
              <span className="font-mono text-xs bg-muted px-2 py-1 rounded h-fit">custom-jumbf-cose</span>
              <p className="text-muted-foreground text-sm">Formats requiring custom implementation: FLAC, JPEG XL, all 5 document formats, all 3 font formats. Encypher implements JUMBF embedding and COSE signing directly for these formats. Verification uses the same cryptographic primitives but with custom manifest extraction.</p>
            </li>
          </ul>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Signing via the API</h2>
          <p className="text-muted-foreground mb-4">
            All 31 MIME types are accessible through a single signing endpoint.
            Format detection is automatic based on file content, not file extension:
          </p>
          <div className="bg-muted/30 rounded-lg p-4 font-mono text-sm">
            <p className="text-muted-foreground mb-2"># Sign any media file - format auto-detected</p>
            <p className="mb-1">curl -X POST https://api.encypher.com/v1/sign/media \</p>
            <p className="mb-1 ml-4">-H "Authorization: Bearer ey_your_key_here" \</p>
            <p className="ml-4">-F "file=@content.pdf"</p>
          </div>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/content-provenance/images" className="underline hover:no-underline">Image Provenance: 13 Formats</Link></li>
            <li><Link href="/content-provenance/audio-video" className="underline hover:no-underline">Audio and Video Provenance: 10 Formats</Link></li>
            <li><Link href="/content-provenance/text" className="underline hover:no-underline">Text Provenance</Link></li>
            <li><Link href="/c2pa-standard/manifest-structure" className="underline hover:no-underline">Manifest Structure</Link></li>
            <li><Link href="/content-provenance/verification" className="underline hover:no-underline">Free Verification</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">All 31 Types in One API</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            One API key, all media types. Free tier covers 1,000 signing operations per month.
            Verification is always free.
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
      </div>
    </>
  );
}
