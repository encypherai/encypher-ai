import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@encypher/design-system';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'Image Content Provenance: 13 Formats | C2PA | Encypher',
  'Image provenance with C2PA JUMBF manifests across 13 formats: JPEG, PNG, WebP, TIFF, AVIF, HEIC, DNG, GIF, SVG, and more. EXIF strips but provenance survives.',
  '/content-provenance/images',
  undefined,
  undefined,
  'C2PA provenance for 13 image formats. EXIF strips; provenance survives.'
);

const imageFormats = [
  { slug: 'jpeg', name: 'JPEG', container: 'JUMBF appended after EOI marker', use: 'News photography, editorial images, stock photography' },
  { slug: 'png', name: 'PNG', container: 'JUMBF in custom PNG chunk', use: 'Infographics, screenshots, logos, data visualizations' },
  { slug: 'webp', name: 'WebP', container: 'JUMBF in RIFF-based WebP container chunk', use: 'Web publishing, CDN-served images, CMS content' },
  { slug: 'tiff', name: 'TIFF', container: 'JUMBF box in TIFF IFD structure', use: 'Professional photography, print publishing, archival' },
  { slug: 'avif', name: 'AVIF', container: 'JUMBF box in ISO BMFF container', use: 'Next-gen web images, high-quality web delivery' },
  { slug: 'heic', name: 'HEIC', container: 'JUMBF box in ISO BMFF/HEIF container', use: 'iPhone/iPad photos, mobile photography' },
  { slug: 'heif', name: 'HEIF', container: 'JUMBF box in ISO BMFF/HEIF container', use: 'Cross-platform high-efficiency images, camera manufacturers' },
  { slug: 'heic-sequence', name: 'HEIC Sequence', container: 'JUMBF box in ISO BMFF/HEIF sequence container', use: 'Burst photography, live photos, image sequences' },
  { slug: 'heif-sequence', name: 'HEIF Sequence', container: 'JUMBF box in ISO BMFF/HEIF sequence container', use: 'Animated and sequential image content' },
  { slug: 'svg', name: 'SVG', container: 'JUMBF data in SVG metadata element', use: 'Logos, icons, illustrations, data visualizations' },
  { slug: 'dng', name: 'DNG', container: 'JUMBF box in TIFF/EP IFD structure', use: 'RAW photography, professional photo workflows' },
  { slug: 'gif', name: 'GIF', container: 'JUMBF data in GIF application extension block', use: 'Animated content, memes, simple web graphics' },
  { slug: 'jxl', name: 'JPEG XL', container: 'Custom JUMBF/COSE embedding', use: 'Next-gen web delivery, photography archives' },
];

export default function ImagesProvenancePage() {
  const techArticle = getTechArticleSchema({
    title: 'Image Content Provenance: 13 Formats',
    description: 'Image provenance with C2PA JUMBF manifests across 13 formats. EXIF strips but provenance survives. pHash attribution search for derivatives.',
    url: `${siteConfig.url}/content-provenance/images`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="Image Content Provenance"
        whatWeDo="Encypher embeds C2PA JUMBF manifests into image files across 13 supported formats. Provenance is stored in the file container, not in EXIF fields that get stripped by social platforms. Verification is free and works on any C2PA-signed image."
        whoItsFor="Photographers, news organizations, stock photo agencies, and visual publishers whose images are distributed across web platforms, social media, and AI image generation training sets. Any organization needing cryptographic proof of image origin."
        keyDifferentiator="C2PA manifests are embedded in the file container, not in EXIF data. EXIF is stripped by every major social platform and many CDNs. C2PA manifests survive download and re-upload. The ownership record stays in the file."
        primaryValue="Thirteen image formats covered with format-specific JUMBF embedding. pHash attribution search for finding derivative works and compressed copies. Free verification for any recipient."
        pagePath="/content-provenance/images"
        pageType="WebPage"
      />

      <Script
        id="tech-article-images-provenance"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <ArticleShell path="/content-provenance/images">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Content Provenance', href: '/content-provenance' },
          { name: 'Images', href: '/content-provenance/images' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Image Content Provenance
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          C2PA manifests embedded in 13 image formats. Stored in the file container,
          not in EXIF fields. The ownership record survives download, re-upload, and
          redistribution.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The EXIF Problem</h2>
          <p className="text-muted-foreground mb-4">
            Every major social platform strips EXIF metadata from uploaded images.
            Instagram, Twitter/X, Facebook, and LinkedIn all remove EXIF data - including
            photographer name, copyright notice, and creation date - when images are uploaded.
            CDN optimization pipelines often do the same. The industry standard for
            image ownership metadata is systematically stripped by the infrastructure
            through which images are distributed.
          </p>
          <p className="text-muted-foreground mb-4">
            This is a known problem and the C2PA specification addresses it directly. C2PA
            manifests are not stored in EXIF fields. They are stored in format-specific
            container structures: JUMBF boxes appended to JPEG files, PNG chunks, RIFF
            chunks, ISO BMFF uuid boxes, and other format-native embedding locations. These
            structures are part of the file format itself and survive the processes that
            strip EXIF.
          </p>
          <p className="text-muted-foreground">
            Social platforms do sometimes strip C2PA manifests during upload processing.
            This is an evolving area - platforms like LinkedIn and some major news distribution
            services are implementing C2PA support. For B2B distribution, syndication feeds,
            and API-based distribution, C2PA manifests typically survive intact. For consumer
            social platforms, the landscape is improving as platform adoption of C2PA grows.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">JUMBF: The Container Standard</h2>
          <p className="text-muted-foreground mb-4">
            JUMBF (JPEG Universal Metadata Box Format) is an ISO standard (ISO 19566-5) for
            embedding structured metadata into image and media files. C2PA uses JUMBF as
            the container format for manifests across all supported media types.
          </p>
          <p className="text-muted-foreground mb-4">
            The JUMBF box contains the complete C2PA manifest: the claim (what is being
            asserted about the content), assertions (specific claims like authorship,
            creation timestamp, and rights terms), the content hash, and the COSE signature
            (the cryptographic proof that authenticates the manifest).
          </p>
          <p className="text-muted-foreground">
            Each image format has a format-specific location for the JUMBF box. The C2PA
            specification defines these locations precisely. JPEG files have the box appended
            after the EOI (End of Image) marker. PNG files use a custom PNG chunk. WebP
            files use a RIFF chunk. ISO BMFF containers (AVIF, HEIC, HEIF, M4V) use a
            uuid box. The embedding location is format-native to ensure compatibility with
            existing image processing tools.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Supported Image Formats</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 pr-4 font-semibold">Format</th>
                  <th className="text-left py-3 pr-4 font-semibold">Container</th>
                  <th className="text-left py-3 font-semibold">Primary Use Cases</th>
                </tr>
              </thead>
              <tbody className="text-muted-foreground">
                {imageFormats.map((fmt, i) => (
                  <tr key={fmt.slug} className={i < imageFormats.length - 1 ? 'border-b border-border/50' : ''}>
                    <td className="py-3 pr-4">
                      <Link href={`/content-provenance/${fmt.slug}`} className="font-medium text-foreground underline hover:no-underline">
                        {fmt.name}
                      </Link>
                    </td>
                    <td className="py-3 pr-4 text-xs">{fmt.container}</td>
                    <td className="py-3 text-xs">{fmt.use}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">pHash Attribution Search</h2>
          <p className="text-muted-foreground mb-4">
            Perceptual hashing (pHash) generates a compact fingerprint of an image based
            on its visual content rather than its exact pixel values. Two images that look
            similar to a human eye produce similar pHash values, even if they differ in
            resolution, compression, or minor visual modifications.
          </p>
          <p className="text-muted-foreground mb-4">
            Encypher's attribution search uses pHash to find derivative works: versions of
            a signed image that have been resized, compressed, color-adjusted, or lightly
            edited. When a photographer publishes a signed original, attribution search can
            identify compressed social media versions, thumbnail derivatives, and editorial
            crops of the same image as related to the original.
          </p>
          <p className="text-muted-foreground">
            This is particularly useful for photojournalism. A news organization's signed
            original photo may be redistributed as compressed versions across dozens of
            outlets. pHash attribution search identifies those derivatives and links them
            back to the original provenance record, extending the ownership documentation
            to derivative works that do not themselves carry the original manifest.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">What the Image Manifest Records</h2>
          <p className="text-muted-foreground mb-4">
            The C2PA manifest embedded in a signed image includes:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>Publisher/photographer identity (verified certificate)</li>
            <li>Creation and publication timestamps</li>
            <li>Content hash (SHA-256 of the image pixel data)</li>
            <li>Rights assertions (machine-readable licensing terms)</li>
            <li>Ingredient list (for images that incorporate other signed assets)</li>
            <li>Actions (creation, editing, publishing - each as a separate assertion)</li>
            <li>Location data (optional, for photojournalism with geographic context)</li>
          </ul>
          <p className="text-muted-foreground">
            The full manifest is accessible through any C2PA-compatible verification tool.
            Verification does not require Encypher access - the open-source c2pa-python
            and c2pa-js libraries verify manifests directly from the image file.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">AI Image Generation and Provenance</h2>
          <p className="text-muted-foreground mb-4">
            AI image generation training sets contain billions of images scraped from the
            web. Many of those images were created by photographers and visual artists who
            did not license them for AI training. The provenance problem for images is
            both a publisher protection issue and an AI compliance issue.
          </p>
          <p className="text-muted-foreground mb-4">
            Photographers and visual publishers who sign their archives with C2PA provenance
            create a documented ownership record for every image. When those images appear
            in AI training data, the manifest records that they were used without a license
            if no license was obtained. EU AI Act Article 52 compliance for image-generating
            AI systems requires C2PA manifest embedding for AI-generated outputs.
          </p>
          <p className="text-muted-foreground">
            C2PA has explicit support for documenting AI-generated images: the manifest can
            record that an image was generated by a specific AI model, the generation prompt
            (optionally), and the generating organization's identity. This creates a
            provenance record for AI-generated images that is as strong as the provenance
            record for human-created images.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Format-Specific Pages</h2>
          <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
            {imageFormats.map(fmt => (
              <Link
                key={fmt.slug}
                href={`/content-provenance/${fmt.slug}`}
                className="p-2 text-sm text-center bg-muted rounded hover:bg-muted/70 transition-colors"
              >
                {fmt.name}
              </Link>
            ))}
          </div>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/content-provenance" className="underline hover:no-underline">Content Provenance: The Definitive Guide</Link></li>
            <li><Link href="/c2pa-standard/manifest-structure" className="underline hover:no-underline">C2PA Manifest Structure</Link></li>
            <li><Link href="/c2pa-standard/media-types" className="underline hover:no-underline">All 31 Supported Media Types</Link></li>
            <li><Link href="/content-provenance/audio-video" className="underline hover:no-underline">Audio and Video Provenance</Link></li>
            <li><Link href="/content-provenance/verification" className="underline hover:no-underline">Free Verification</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Sign Your Image Archive</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            API and SDK support for all 13 image formats. Batch signing available.
            Free verification for any recipient, no account required.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/try">Start Free</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/tools/verify">Verify an Image</Link>
            </Button>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
