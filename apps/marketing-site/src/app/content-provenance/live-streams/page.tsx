import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { ArticleShell } from '@/components/content/ArticleShell';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'Live Stream Content Provenance | C2PA 2.3 Section 19 | Encypher',
  'Real-time provenance for live video streams. C2PA 2.3 Section 19 per-segment manifests with backwards-linked chains. Tamper-evident records for news broadcasts, live events, and government proceedings.',
  '/content-provenance/live-streams',
  undefined,
  undefined,
  'C2PA 2.3 per-segment manifests for live video. Tamper-evident, broadcast-ready.'
);

export default function LiveStreamsPage() {
  const techArticle = getTechArticleSchema({
    title: 'Live Stream Content Provenance',
    description: 'Real-time provenance for live video streams using C2PA 2.3 Section 19. Per-segment manifests with backwards-linked chains create tamper-evident records for broadcast content.',
    url: `${siteConfig.url}/content-provenance/live-streams`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  return (
    <>
      <AISummary
        title="Live Stream Content Provenance"
        whatWeDo="Encypher implements C2PA 2.3 Section 19 live stream provenance, embedding per-segment signed manifests into live video streams as they broadcast. Each segment's manifest links to the previous segment, creating a backwards-linked tamper-evident chain."
        whoItsFor="News broadcasters, live event producers, government and legislative bodies, and sports rights holders who need cryptographic documentation of live content as it is produced."
        keyDifferentiator="Per-segment manifests linked in a backwards chain. Tampering with any segment breaks the chain from that point forward. Real-time signing occurs at broadcast, not post-production. The provenance record is as live as the content."
        primaryValue="Tamper-evident documentation of live broadcasts. Authentic footage identification. Chain of custody for news and government proceedings. Compliance documentation for live AI-generated content."
        pagePath="/content-provenance/live-streams"
        pageType="WebPage"
      />

      <Script
        id="tech-article-live-streams"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />

      <ArticleShell path="/content-provenance/live-streams">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Content Provenance', href: '/content-provenance' },
          { name: 'Live Streams', href: '/content-provenance/live-streams' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Live Stream Content Provenance
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          C2PA 2.3 Section 19 defines provenance for live video streams. Per-segment manifests
          signed in real time, linked in a backwards chain. The provenance record is as
          live as the broadcast.
        </p>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Why Live Streams Need Provenance</h2>
          <p className="text-muted-foreground mb-4">
            Recorded video can be signed at the completion of production. The file exists,
            it can be hashed, and the hash can be signed. Live video presents a different
            challenge: the content does not exist as a complete file until the broadcast ends.
            Waiting until the end to sign means the entire broadcast period is undocumented.
          </p>
          <p className="text-muted-foreground mb-4">
            Live news broadcasts are particularly sensitive to this gap. A breaking news
            broadcast with manipulated footage could be presented as authentic because no
            provenance record exists during the live period. The same applies to government
            proceedings, live court testimony, sports events with rights restrictions, and
            live music performances.
          </p>
          <p className="text-muted-foreground">
            C2PA 2.3 Section 19 addresses this by defining a provenance model for streaming
            content where signing happens continuously during the broadcast, not just at the end.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Per-Segment Manifests and Backwards Linking</h2>
          <p className="text-muted-foreground mb-4">
            Streaming video is divided into segments - short chunks of video data typically
            2-10 seconds long in HLS (HTTP Live Streaming) and DASH (Dynamic Adaptive
            Streaming over HTTP) formats. Each segment is a self-contained piece of video
            data that can be independently decoded.
          </p>
          <p className="text-muted-foreground mb-4">
            C2PA 2.3 Section 19 assigns a signed manifest to each segment. The manifest for
            segment N includes:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>The segment's own content hash</li>
            <li>The signing timestamp for this segment</li>
            <li>The broadcaster's identity (verified certificate)</li>
            <li>A hash of the previous segment's manifest (backwards link)</li>
          </ul>
          <p className="text-muted-foreground mb-4">
            The backwards link is the chain's integrity mechanism. Each segment's manifest
            includes a cryptographic commitment to the previous segment's manifest. This means
            any manipulation of an earlier segment also breaks the chain for all subsequent
            segments. A verifier examining the complete chain can identify the exact segment
            where the chain breaks, localizing any tampering to a specific time range in the broadcast.
          </p>
          <p className="text-muted-foreground">
            The first segment in a stream (the genesis segment) has no backwards link - it
            begins the chain. All subsequent segments extend it. After the broadcast ends,
            the complete chain provides a tamper-evident record of the entire broadcast.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Real-Time Signing at Broadcast</h2>
          <p className="text-muted-foreground mb-4">
            Live stream signing operates with millisecond latency requirements. A signing
            operation that adds multiple seconds to segment delivery is not compatible with
            live streaming. The Encypher live stream signing service is designed for
            sub-100ms signing latency, compatible with typical segment delivery timelines.
          </p>
          <p className="text-muted-foreground mb-4">
            Integration with existing broadcast infrastructure occurs at the segment packaging
            stage - after the segment is encoded but before it is delivered to the CDN or
            streaming origin. The signing service receives the encoded segment, computes the
            hash, assembles the manifest with the backwards link to the previous segment,
            signs it, and returns the segment with the embedded manifest.
          </p>
          <p className="text-muted-foreground">
            For news broadcasters using standard broadcast infrastructure, integration
            typically occurs at the stream packager. For direct-to-consumer streaming
            operations, integration occurs at the streaming origin server. The Encypher
            SDK provides client libraries for common broadcast software.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Use Cases</h2>
          <div className="space-y-4">
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">News Broadcasts</h3>
              <p className="text-muted-foreground text-sm">
                A live news broadcast with C2PA provenance creates a tamper-evident record
                of every minute of coverage. Questions about whether footage was authentic
                or manipulated can be resolved by verifying the chain. Newsroom archives
                of live broadcasts carry the same cryptographic documentation as filed
                photographic evidence.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Government and Legislative Proceedings</h3>
              <p className="text-muted-foreground text-sm">
                Legislative sessions, court proceedings, and official government briefings
                streamed with C2PA provenance create an official authenticated record.
                Disputes about what was said or shown in an official proceeding can be
                resolved by reference to the signed stream. Parliamentary archives with
                live stream provenance are legally defensible primary sources.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Live Events and Sports</h3>
              <p className="text-muted-foreground text-sm">
                Sports rights holders face unauthorized redistribution of live broadcast
                content in real time. Signed streams create a technical basis for
                distinguishing authorized broadcast copies from unauthorized redistributions.
                Each segment's manifest identifies the authorized broadcast source.
              </p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold mb-1">Live AI-Generated Content</h3>
              <p className="text-muted-foreground text-sm">
                AI-generated live content (synthetic presenters, real-time deepfake detection
                scenarios) needs the same EU AI Act Article 52 compliance documentation as
                recorded AI-generated content. Live stream signing with an AI-generation
                action in the manifest satisfies the machine-readable marking requirement
                for live AI content.
              </p>
            </div>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Verification After Broadcast</h2>
          <p className="text-muted-foreground mb-4">
            After a broadcast ends, the complete segment chain can be archived as a
            provenance record. The archive contains each segment with its manifest,
            forming a complete cryptographic history of the broadcast.
          </p>
          <p className="text-muted-foreground mb-4">
            Verification of a specific time range requires the segments for that range
            and the preceding chain back to the genesis segment. The Encypher API supports
            range verification: submit a time range and receive a verification report
            covering all segments in that range, including the chain integrity status.
          </p>
          <p className="text-muted-foreground">
            For news organizations preserving broadcast archives, this means every archived
            broadcast can include a tamper-evident provenance chain alongside the video files.
            The chain is separate from the video and lightweight - it is a sequence of
            manifest signatures, not a copy of the video itself.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/content-provenance/audio-video" className="underline hover:no-underline">Audio and Video Provenance: 10 Formats</Link></li>
            <li><Link href="/content-provenance" className="underline hover:no-underline">Content Provenance: The Definitive Guide</Link></li>
            <li><Link href="/c2pa-standard" className="underline hover:no-underline">The C2PA Standard</Link></li>
            <li><Link href="/content-provenance/eu-ai-act" className="underline hover:no-underline">EU AI Act Compliance</Link></li>
            <li><Link href="/content-provenance/verification" className="underline hover:no-underline">Free Verification</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Live Stream Provenance Infrastructure</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Live stream signing is available at enterprise tier. Integration with HLS and DASH
            packaging infrastructure. Sub-100ms signing latency for real-time broadcast.
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
