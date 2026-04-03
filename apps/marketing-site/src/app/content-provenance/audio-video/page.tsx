import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@encypher/design-system';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'Audio and Video Content Provenance | 10 Formats | Encypher',
  'C2PA provenance for audio and video: 6 audio formats (WAV, MP3, AAC, FLAC, M4A, MPA) and 4 video formats (MP4, MOV, M4V, AVI). Container-embedded manifests that travel with files.',
  '/content-provenance/audio-video',
  undefined,
  undefined,
  'C2PA provenance for 10 audio and video formats. Embedded, not linked.'
);

export default function AudioVideoProvenancePage() {
  const techArticle = getTechArticleSchema({
    title: 'Audio and Video Content Provenance',
    description: 'C2PA provenance for audio and video across 10 formats. Container-embedded manifests using RIFF chunks, ID3 GEOB frames, and ISO BMFF uuid boxes.',
    url: `${siteConfig.url}/content-provenance/audio-video`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  const audioFormats = [
    { slug: 'wav', name: 'WAV', container: 'RIFF chunk', mime: 'audio/wav', use: 'Music production, broadcast audio, podcast masters' },
    { slug: 'mp3', name: 'MP3', container: 'ID3 GEOB frame', mime: 'audio/mpeg', use: 'Podcast distribution, music streaming, audio journalism' },
    { slug: 'm4a', name: 'M4A', container: 'ISO BMFF uuid box', mime: 'audio/mp4', use: 'Apple Music, iTunes distribution, high-quality audio' },
    { slug: 'aac', name: 'AAC', container: 'ISO BMFF uuid box', mime: 'audio/aac', use: 'Streaming platforms, mobile audio, broadcasting' },
    { slug: 'flac', name: 'FLAC', container: 'Custom JUMBF/COSE', mime: 'audio/flac', use: 'Lossless music, archival audio, hi-fi streaming' },
    { slug: 'mpa', name: 'MPA', container: 'MPEG audio frame', mime: 'audio/mpa', use: 'Broadcast audio, multimedia applications' },
  ];

  const videoFormats = [
    { slug: 'mp4', name: 'MP4', container: 'ISO BMFF uuid box', mime: 'video/mp4', use: 'Web video, streaming platforms, news video' },
    { slug: 'mov', name: 'MOV', container: 'ISO BMFF uuid box (QuickTime)', mime: 'video/quicktime', use: 'Professional video production, film, Apple ecosystem' },
    { slug: 'm4v', name: 'M4V', container: 'ISO BMFF uuid box', mime: 'video/x-m4v', use: 'Apple TV, iTunes, DRM-protected video' },
    { slug: 'avi', name: 'AVI', container: 'RIFF chunk', mime: 'video/x-msvideo', use: 'Legacy video archives, Windows ecosystem, surveillance' },
  ];

  return (
    <>
      <AISummary
        title="Audio and Video Content Provenance"
        whatWeDo="Encypher embeds C2PA provenance into audio and video files using container-native embedding methods: RIFF chunks for WAV and AVI, ID3 GEOB frames for MP3, and ISO BMFF uuid boxes for MP4, MOV, M4V, M4A, and AAC."
        whoItsFor="Broadcasters, music publishers, podcast producers, documentary filmmakers, and news organizations distributing audio and video content through streaming platforms, syndication feeds, and B2B channels."
        keyDifferentiator="Container-native embedding for each format. Manifests are stored in format-standard locations that survive file processing and distribution. Ten formats covered with format-specific implementation for each container type."
        primaryValue="Cryptographic proof of origin for audio and video that travels with files through distribution chains. Supports live stream provenance via C2PA 2.3 Section 19."
        pagePath="/content-provenance/audio-video"
        pageType="WebPage"
      />

      <Script
        id="tech-article-audio-video"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <ArticleShell path="/content-provenance/audio-video">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Content Provenance', href: '/content-provenance' },
          { name: 'Audio and Video', href: '/content-provenance/audio-video' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Audio and Video Content Provenance
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          Six audio formats and four video formats. C2PA manifests embedded in container-native
          structures that travel with files through distribution and streaming.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Container-Native Embedding</h2>
          <p className="text-muted-foreground mb-4">
            Audio and video files use container formats - structured wrappers around compressed
            media data. The container includes metadata fields, timing information, track
            definitions, and now, with C2PA, provenance manifests.
          </p>
          <p className="text-muted-foreground mb-4">
            Each audio and video format has a container type with specific mechanisms for
            storing extension data. C2PA uses these native extension mechanisms rather than
            adding new metadata fields that could be stripped by processing tools:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>RIFF containers (WAV, AVI): JUMBF data in a dedicated RIFF chunk</li>
            <li>MP3 (ID3 container): JUMBF data in an ID3v2 GEOB (General Encapsulated Object) frame</li>
            <li>ISO BMFF containers (MP4, MOV, M4V, M4A, AAC): JUMBF data in a uuid box</li>
          </ul>
          <p className="text-muted-foreground">
            These are the same extension mechanisms that other metadata uses. A uuid box in
            an MP4 file is a standard part of the ISO BMFF specification. Processing tools
            that do not understand the C2PA content leave it intact rather than stripping it.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Audio Formats</h2>
          <div className="overflow-x-auto mb-6">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 pr-4 font-semibold">Format</th>
                  <th className="text-left py-3 pr-4 font-semibold">Container</th>
                  <th className="text-left py-3 font-semibold">Primary Use Cases</th>
                </tr>
              </thead>
              <tbody className="text-muted-foreground">
                {audioFormats.map((fmt, i) => (
                  <tr key={fmt.slug} className={i < audioFormats.length - 1 ? 'border-b border-border/50' : ''}>
                    <td className="py-3 pr-4">
                      <Link href={`/content-provenance/${fmt.slug}`} className="font-medium text-foreground underline hover:no-underline">
                        {fmt.name}
                      </Link>
                      <span className="text-xs ml-2 text-muted-foreground">{fmt.mime}</span>
                    </td>
                    <td className="py-3 pr-4 text-xs">{fmt.container}</td>
                    <td className="py-3 text-xs">{fmt.use}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h3 className="text-lg font-semibold mb-3">The ID3 GEOB Frame (MP3)</h3>
          <p className="text-muted-foreground mb-4">
            MP3 files use the ID3 tagging format for metadata. ID3 supports multiple frame
            types including GEOB (General Encapsulated Object), which stores arbitrary binary
            data with a MIME type identifier. Encypher stores the C2PA JUMBF manifest data in
            a GEOB frame identified by the C2PA MIME type.
          </p>
          <p className="text-muted-foreground mb-4">
            This is the C2PA-standard embedding method for MP3. The GEOB frame is preserved
            by ID3-aware tools that process MP3 files. Most podcast distribution platforms
            and music distribution services pass ID3 tags through without stripping them,
            making the C2PA manifest durable through typical podcast and music distribution workflows.
          </p>
          <p className="text-muted-foreground">
            MP3 is particularly important for podcast provenance. A podcast episode signed
            at production carries provenance through distribution to Apple Podcasts, Spotify,
            and other platforms. The episode's authorship, production organization, and
            publication date are documented in the file itself.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Video Formats</h2>
          <div className="overflow-x-auto mb-6">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 pr-4 font-semibold">Format</th>
                  <th className="text-left py-3 pr-4 font-semibold">Container</th>
                  <th className="text-left py-3 font-semibold">Primary Use Cases</th>
                </tr>
              </thead>
              <tbody className="text-muted-foreground">
                {videoFormats.map((fmt, i) => (
                  <tr key={fmt.slug} className={i < videoFormats.length - 1 ? 'border-b border-border/50' : ''}>
                    <td className="py-3 pr-4">
                      <Link href={`/content-provenance/${fmt.slug}`} className="font-medium text-foreground underline hover:no-underline">
                        {fmt.name}
                      </Link>
                      <span className="text-xs ml-2 text-muted-foreground">{fmt.mime}</span>
                    </td>
                    <td className="py-3 pr-4 text-xs">{fmt.container}</td>
                    <td className="py-3 text-xs">{fmt.use}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h3 className="text-lg font-semibold mb-3">ISO BMFF: The Dominant Video Container</h3>
          <p className="text-muted-foreground mb-4">
            MP4, MOV, M4V, and M4A all use ISO Base Media File Format (ISO BMFF) as their
            container architecture. ISO BMFF organizes file content into "boxes" (also called
            "atoms" in Apple's QuickTime terminology). Each box has a type identifier and length,
            and boxes can contain other boxes.
          </p>
          <p className="text-muted-foreground mb-4">
            C2PA uses a "uuid" box type - a box identified by a 16-byte UUID - to store
            the JUMBF manifest in ISO BMFF files. The UUID is the C2PA-designated identifier.
            File processing tools that do not understand the uuid box type skip it during
            processing, preserving it intact.
          </p>
          <p className="text-muted-foreground">
            This makes MP4 provenance durable through common video processing workflows.
            Transcoding that does not modify the container structure preserves the manifest.
            Streaming platforms that serve MP4 files directly pass the manifest to recipients.
            The manifest survives download and local storage.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Deepfake Detection and Media Provenance</h2>
          <p className="text-muted-foreground mb-4">
            The same C2PA provenance infrastructure that authenticates human-created audio and
            video also provides the mechanism for identifying AI-generated synthetic media.
            A C2PA manifest on an AI-generated video records that it was generated by a
            specific AI system, supporting EU AI Act Article 52 compliance requirements.
          </p>
          <p className="text-muted-foreground mb-4">
            For broadcasters and news organizations, the practical value is inverse: signing
            authentic footage with C2PA provenance creates a documented record of what is
            real. When a question arises about whether footage has been manipulated, provenance
            verification either confirms the footage is unmodified (hash matches the signed
            original) or detects modification (hash does not match).
          </p>
          <p className="text-muted-foreground">
            This is a materially different capability than deepfake detection tools, which
            analyze synthetic patterns in video frames. Detection tools guess whether content
            is synthetic. Provenance verification confirms whether signed content is unmodified.
            Both capabilities are useful; they address different questions.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Live Streams</h2>
          <p className="text-muted-foreground mb-4">
            C2PA 2.3 Section 19 defines provenance for live video streams. Live stream
            provenance uses per-segment manifests linked in a backward chain, so each
            segment of the stream carries its own signed manifest and points to the
            previous segment. This creates a continuous tamper-evident record across
            a live broadcast.
          </p>
          <p className="text-muted-foreground">
            Live stream provenance is covered in detail at <Link href="/content-provenance/live-streams" className="underline hover:no-underline">Content Provenance for Live Streams</Link>.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Format-Specific Pages</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold mb-2 text-sm">Audio</h3>
              <ul className="space-y-1">
                {audioFormats.map(fmt => (
                  <li key={fmt.slug}>
                    <Link href={`/content-provenance/${fmt.slug}`} className="text-sm text-muted-foreground underline hover:no-underline">
                      {fmt.name} Provenance
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-2 text-sm">Video</h3>
              <ul className="space-y-1">
                {videoFormats.map(fmt => (
                  <li key={fmt.slug}>
                    <Link href={`/content-provenance/${fmt.slug}`} className="text-sm text-muted-foreground underline hover:no-underline">
                      {fmt.name} Provenance
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/content-provenance/live-streams" className="underline hover:no-underline">Live Stream Provenance</Link></li>
            <li><Link href="/content-provenance/images" className="underline hover:no-underline">Image Provenance: 13 Formats</Link></li>
            <li><Link href="/c2pa-standard/media-types" className="underline hover:no-underline">All 31 Supported Media Types</Link></li>
            <li><Link href="/content-provenance" className="underline hover:no-underline">Content Provenance: The Definitive Guide</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Sign Your Audio and Video Content</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            API and SDK support for all 10 audio and video formats. Batch signing for archives.
            Free verification for any recipient.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/try">Start Free</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/contact">Enterprise Pricing</Link>
            </Button>
          </div>
        </section>
      </ArticleShell>
    </>
  );
}
