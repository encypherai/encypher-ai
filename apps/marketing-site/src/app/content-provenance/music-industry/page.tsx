import Link from 'next/link';
import Script from 'next/script';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { getVerticalMetadata } from '@/lib/seo';
import type { Metadata } from 'next';

export const metadata: Metadata = getVerticalMetadata(
  'music-industry',
  'Content Provenance for Music: Labels, Distributors, Streaming | Encypher',
  'Embed cryptographic C2PA provenance into WAV, MP3, FLAC, M4A, and AAC audio files. Protect music from unauthorized AI training, document rights ownership, and verify authenticity across streaming and distribution platforms.'
);

export default function MusicIndustryPage() {
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'How does content provenance protect music from unauthorized AI training?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Encypher embeds C2PA manifests directly into audio file containers (WAV RIFF chunks, MP3 ID3 frames, FLAC Vorbis comment blocks, M4A/AAC ISO base media file format boxes). The manifest records label identity, artist attribution, rights ownership, and licensing terms. When AI companies scrape audio for training data, those manifests travel with the files. Labels and distributors can document that AI companies received music with explicit ownership metadata, which supports licensing enforcement.',
        },
      },
      {
        '@type': 'Question',
        name: 'Which audio formats does Encypher support for provenance embedding?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Encypher supports WAV, MP3, M4A, AAC, FLAC, OGG, and AIFF audio formats. WAV uses RIFF chunk embedding. MP3 uses ID3 GEOB frame embedding. M4A and AAC use ISO base media file format box structures. FLAC uses Vorbis comment metadata blocks. All formats store a complete C2PA manifest with cryptographic signing. See the individual format pages for technical embedding details.',
        },
      },
      {
        '@type': 'Question',
        name: 'Can provenance survive audio processing and compression for streaming?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'C2PA manifests are stored in file metadata containers, not in the audio data itself. Compression and format conversion that preserves the container structure also preserves the manifest. Lossy compression of the audio stream does not affect the manifest. However, format conversion that strips container metadata (such as some normalization pipelines) will remove the manifest. Encypher recommends signing files at the final distribution format, after any processing, to ensure the manifest survives delivery.',
        },
      },
      {
        '@type': 'Question',
        name: 'How does streaming provenance work on platforms like Spotify or Apple Music?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Streaming platforms receive master files from distributors. Provenance embedded in those master files is present in the files the platform ingests. Whether the platform preserves the manifest through its own transcoding pipeline varies by platform. Encypher works with distributors and labels to sign files before distributor submission, establishing a chain of custody from studio to distributor. Platform-level preservation is a separate integration that some platforms are actively implementing.',
        },
      },
    ],
  };

  return (
    <>
      <AISummary
        title="Content Provenance for Music Industry"
        whatWeDo="Encypher embeds C2PA provenance manifests into audio files (WAV, MP3, FLAC, M4A, AAC) at the recording or distribution stage. The manifest records label identity, artist attribution, rights ownership, and licensing terms in file containers that travel with the audio through distribution, streaming, and AI ingestion."
        whoItsFor="Record labels, music distributors, streaming platforms, and rights management organizations. Specifically suited to labels and distributors managing catalogs targeted by AI training data acquisition, and platforms implementing content authentication for AI-generated music detection."
        keyDifferentiator="Audio format coverage across WAV, MP3, FLAC, M4A, AAC, OGG, and AIFF using format-native container structures. C2PA manifests in audio metadata containers, not in the audio stream, so they survive standard audio processing. Rights management documentation that is machine-readable and cryptographically signed."
        primaryValue="Protect music catalogs from unauthorized AI training. Document rights ownership in a format that travels with the audio file through every distribution channel. Enable streaming platforms to verify content authenticity and detect AI-generated music."
        pagePath="/content-provenance/music-industry"
        pageType="WebPage"
      />

      <Script
        id="faq-music-industry"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Breadcrumbs
          items={[
            { name: 'Home', href: '/' },
            { name: 'Content Provenance', href: '/content-provenance' },
            { name: 'Music Industry', href: '/content-provenance/music-industry' },
          ]}
        />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Content Provenance for Music
        </h1>
        <p className="text-lg text-muted-foreground mb-8">
          Cryptographic ownership metadata embedded in audio files. Protects catalogs from unauthorized
          AI training, documents rights ownership, and enables streaming platform authentication.
        </p>

        {/* AI training problem */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Unauthorized AI Training on Music Catalogs</h2>
          <p className="text-base leading-relaxed mb-4">
            Music catalogs are being used to train AI systems that generate music. The legal landscape
            is unsettled, but the operational reality is clear: AI companies have ingested music at scale,
            often without licenses, and the AI-generated music they produce competes directly with the
            artists and labels whose work trained it.
          </p>
          <p className="text-base leading-relaxed mb-4">
            The central weakness in the music industry's position is the same as it is for other content
            industries: the files that reached AI companies looked like unowned content. Container metadata
            is stripped by hosting platforms. ISRC codes are useful for identification but are not
            cryptographically bound to the audio. ID3 tags can be edited. The ownership claim was present
            in the industry's own databases but not in the files themselves.
          </p>
          <p className="text-base leading-relaxed">
            Encypher embeds the ownership claim in the file using cryptographic signing. The C2PA manifest
            in a WAV or MP3 file is not just metadata that can be stripped - it is a signed, timestamped
            assertion of ownership bound to the specific audio content via cryptographic hash. Any party
            that receives that file has received the ownership claim with it.
          </p>
        </section>

        {/* Audio format coverage */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Audio Format Coverage</h2>
          <p className="text-base leading-relaxed mb-4">
            Music exists in many formats across the production and distribution pipeline. Encypher
            supports provenance embedding across the full range of professional and consumer audio formats.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div className="bg-muted/30 border border-border rounded-lg p-4">
              <h3 className="font-semibold mb-2">
                <Link href="/content-provenance/wav" className="text-[#2a87c4] hover:underline">WAV</Link>
                {' '}- Studio Masters
              </h3>
              <p className="text-sm text-muted-foreground">
                RIFF chunk embedding. Primary format for studio masters and high-resolution audio.
                Manifest stored in a dedicated RIFF chunk separate from audio data.
              </p>
            </div>
            <div className="bg-muted/30 border border-border rounded-lg p-4">
              <h3 className="font-semibold mb-2">
                <Link href="/content-provenance/mp3" className="text-[#2a87c4] hover:underline">MP3</Link>
                {' '}- Distribution
              </h3>
              <p className="text-sm text-muted-foreground">
                ID3 GEOB frame embedding. Most widely distributed format. Manifest stored
                in a binary ID3 frame that travels with the file through standard distribution.
              </p>
            </div>
            <div className="bg-muted/30 border border-border rounded-lg p-4">
              <h3 className="font-semibold mb-2">
                <Link href="/content-provenance/flac" className="text-[#2a87c4] hover:underline">FLAC</Link>
                {' '}- Lossless Streaming
              </h3>
              <p className="text-sm text-muted-foreground">
                Vorbis comment block embedding. Used by high-resolution streaming platforms
                and audiophile distribution. Lossless with full provenance support.
              </p>
            </div>
            <div className="bg-muted/30 border border-border rounded-lg p-4">
              <h3 className="font-semibold mb-2">
                <Link href="/content-provenance/m4a" className="text-[#2a87c4] hover:underline">M4A</Link>
                {' '}+{' '}
                <Link href="/content-provenance/aac" className="text-[#2a87c4] hover:underline">AAC</Link>
                {' '}- Apple Ecosystem
              </h3>
              <p className="text-sm text-muted-foreground">
                ISO base media file format box embedding. Primary formats for Apple Music
                and iTunes distribution. Full C2PA manifest support.
              </p>
            </div>
          </div>
          <p className="text-base leading-relaxed">
            See the{' '}
            <Link href="/content-provenance/audio-video" className="text-[#2a87c4] hover:underline">
              audio and video provenance overview
            </Link>{' '}
            for the complete list of supported formats including OGG, AIFF, and AAC variants.
          </p>
        </section>

        {/* Rights management */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Rights Management Through Provenance</h2>
          <p className="text-base leading-relaxed mb-4">
            Music rights are complex. A single recording involves composition rights, master rights,
            performance rights, synchronization rights, and mechanical rights, each potentially
            held by different parties. The C2PA manifest structure supports this complexity through
            layered signing and ingredient relationships.
          </p>
          <div className="bg-muted/30 border border-border rounded-lg p-6 mb-4">
            <h3 className="font-semibold mb-3">Rights data recorded in the manifest</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>- Label and distributor identity</li>
              <li>- Artist attribution (primary and featured)</li>
              <li>- ISRC code (cross-referenced, cryptographically bound)</li>
              <li>- Rights holder organization with certificate chain</li>
              <li>- Licensing terms and permitted uses</li>
              <li>- Territory restrictions</li>
              <li>- Creation and release timestamps</li>
            </ul>
          </div>
          <p className="text-base leading-relaxed">
            For catalog signing, Encypher supports bulk signing operations through the API. Labels can
            sign their entire catalog in a single batch job, with each track receiving its own manifest
            containing the relevant rights metadata from your existing rights management system.
          </p>
        </section>

        {/* Streaming provenance */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Streaming Platform Integration</h2>
          <p className="text-base leading-relaxed mb-4">
            Streaming platforms receive master files from distributors. When those master files carry
            Encypher provenance, the platform ingests content with embedded ownership documentation.
            This creates a chain of custody from studio to platform that supports both label enforcement
            actions and platform-level content authentication.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Platforms implementing content authentication can use the Encypher verification API to
            check incoming tracks. Tracks with valid provenance manifests are authenticated. Tracks
            submitted without provenance, or with broken signatures, are flagged for additional review.
            This is a practical mechanism for detecting AI-generated music submitted under false
            artist attributions.
          </p>
          <p className="text-base leading-relaxed">
            Verification is free and requires no authentication. Any platform, distributor, or rights
            organization can verify a signed audio file through the public verification endpoint.
            See the{' '}
            <Link href="/content-provenance/verification" className="text-[#2a87c4] hover:underline">
              verification documentation
            </Link>{' '}
            for integration details.
          </p>
        </section>

        {/* AI-generated music */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Detecting AI-Generated Music</h2>
          <p className="text-base leading-relaxed mb-4">
            AI-generated music is entering distribution pipelines under human artist names. Streaming
            platforms are receiving submissions that claim human authorship but were produced by AI
            systems. This creates both fraud exposure for platforms and revenue displacement for
            genuine artists.
          </p>
          <p className="text-base leading-relaxed mb-4">
            Content provenance provides a positive authentication signal. A track submitted by a
            genuine label or artist through an authenticated signing workflow carries a manifest
            that verifies the claim. A track generated by an AI system and submitted without genuine
            provenance lacks that signal.
          </p>
          <p className="text-base leading-relaxed">
            This is not a foolproof detection system - a sophisticated actor could obtain legitimate
            signing credentials. But it raises the bar significantly and creates a documented record
            of the authentication state at submission time, which matters for platform liability
            and artist protection claims.
          </p>
        </section>

        {/* FAQ section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-6">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">
                Does provenance survive audio processing and streaming transcoding?
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                C2PA manifests are stored in file metadata containers, not in the audio data itself.
                Standard audio processing that preserves the container structure preserves the manifest.
                Format conversion that strips container metadata removes the manifest. Sign files
                at the final distribution format, after any processing, to ensure the manifest survives delivery.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">
                How does this work for catalog signing of existing recordings?
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Existing recordings can be signed through the Encypher bulk signing API. The manifest
                records the signing date, which will post-date the original recording. For enforcement
                purposes, this establishes that the ownership claim was present from a known date forward.
                New releases signed at distribution are stronger for enforcement because the timestamp
                predates potential future infringement.
              </p>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="border-t pt-8">
          <h2 className="text-xl font-semibold mb-4">Protect Your Music Catalog</h2>
          <p className="text-muted-foreground mb-6">
            Sign new releases at distribution. The provenance record needs to predate AI ingestion
            to be useful for enforcement.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 mb-6">
            <Button asChild style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/platform">API Documentation</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/content-provenance/audio-video">Audio Formats</Link>
            </Button>
          </div>
          <div className="flex flex-col sm:flex-row gap-4 text-sm">
            <Link href="/content-provenance" className="text-[#2a87c4] hover:underline">
              What Is Content Provenance?
            </Link>
            <Link href="/content-provenance/wav" className="text-[#2a87c4] hover:underline">
              WAV Provenance
            </Link>
            <Link href="/content-provenance/mp3" className="text-[#2a87c4] hover:underline">
              MP3 Provenance
            </Link>
            <Link href="/content-provenance/flac" className="text-[#2a87c4] hover:underline">
              FLAC Provenance
            </Link>
          </div>
        </section>
      </div>
    </>
  );
}
