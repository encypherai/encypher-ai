import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { CheckCircle2, Shield, FileText, Image, Music, Video, BookOpen, ArrowRight, Globe, Lock, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { getPillarMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = getPillarMetadata('content-provenance');

const techArticleSchema = getTechArticleSchema({
  title: 'What Is Content Provenance? The Definitive Guide',
  description: 'Content provenance embeds cryptographic proof of origin into digital content. Learn how C2PA manifests, cryptographic watermarking, and free verification work across 31 media types.',
  url: `${siteConfig.url}/content-provenance`,
  author: 'Erik Svilich',
  datePublished: '2026-01-08',
  dateModified: '2026-03-31',
});

const faqItems = [
  {
    question: 'What is content provenance?',
    answer: 'Content provenance is a cryptographic record of a piece of content\'s origin, authorship, and history. It is embedded directly into the file or text so the record travels with the content wherever it goes. Anyone can verify it for free using the C2PA standard, without trusting a third party.',
  },
  {
    question: 'How is content provenance different from metadata?',
    answer: 'Traditional metadata - like EXIF data in photos or ID3 tags in audio - is stored separately from the content and can be stripped or altered without detection. Content provenance uses cryptographic signatures so any tampering is immediately visible. If the manifest is removed or the content is edited, verification fails.',
  },
  {
    question: 'What media types support content provenance?',
    answer: 'The C2PA standard supports 31 MIME types across five categories: 13 image formats (JPEG, PNG, WebP, TIFF, HEIC, AVIF, and others), 6 audio formats (WAV, MP3, AAC, FLAC, AIFF, M4A), 4 video formats (MP4, MOV, M4V, MKV), 5 document formats (PDF, DOCX, PPTX, XLSX, and plain text), and 3 font formats. Text provenance - covering articles, social posts, and any unstructured text - is defined in Section A.7, which Encypher authored.',
  },
  {
    question: 'Who can verify content provenance?',
    answer: 'Anyone. The C2PA verification libraries are open source and the standard is free to implement. Verification does not require an account or API key. Publishers, AI companies, journalists, courts, and regulators can all verify independently.',
  },
  {
    question: 'Does content provenance work after copy-paste?',
    answer: 'For text, yes. Encypher embeds provenance markers using Unicode variation selectors that survive copy-paste across browsers, email clients, and text editors. For images and documents, C2PA manifests are embedded in the file container and survive most distribution pathways. Compression and format conversion can sometimes strip manifests from images - this is an active area of development in the C2PA community.',
  },
  {
    question: 'What does the EU AI Act require for content provenance?',
    answer: 'EU AI Act Article 52, which takes full effect August 2, 2026, requires providers of AI systems that generate images, audio, and video to mark their outputs as AI-generated in a machine-readable format. C2PA manifests satisfy this requirement. Article 50 (effective since August 2024) covers general-purpose AI systems. Encypher provides API and SDK tooling to implement compliant marking before the deadline.',
  },
  {
    question: 'How does content provenance help publishers with AI licensing?',
    answer: 'When content carries a C2PA manifest with machine-readable rights terms, AI companies that use that content without a license cannot claim innocent infringement - they had formal notice embedded in every copy. This converts a weak copyright claim into a strong willful infringement claim, increasing statutory damages from up to $30,000 per work to up to $150,000 per work under US copyright law.',
  },
  {
    question: 'Is content provenance the same as watermarking?',
    answer: 'Cryptographic watermarking and content provenance serve the same purpose - proving origin - but are implemented differently. Cryptographic watermarking embeds proof directly into the content using steganographic or structural techniques. C2PA manifests are attached as a sidecar container. Both approaches are deterministic: verification either succeeds or fails, with no false positives. This is fundamentally different from statistical watermarking (like SynthID) which produces probabilities, not proof.',
  },
  {
    question: 'What happens if someone removes the content provenance record?',
    answer: 'Removal is itself evidence. If a C2PA manifest was present when the content was signed but is absent when the content appears elsewhere, that absence documents tampering. For text embedded using Encypher\'s proprietary variation selector markers, an attempt to strip the markers changes the byte sequence and breaks any hash-based provenance check at the original source.',
  },
  {
    question: 'How do I add content provenance to my content?',
    answer: 'Three main paths: the Encypher API (REST, works with any language), the WordPress plugin (one-click activation), or the Python/TypeScript/Go/Rust SDKs for batch processing existing archives. The free tier covers 1,000 documents per month. Enterprise tiers support millions of documents with custom workflows.',
  },
];

export default function ContentProvenancePage() {
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqItems.map(item => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: { '@type': 'Answer', text: item.answer },
    })),
  };

  return (
    <>
      <AISummary
        title="What Is Content Provenance? The Definitive Guide"
        whatWeDo="Content provenance is the cryptographic record of a piece of content's origin, authorship, and modification history - embedded directly into the file so it travels with the content. Encypher authored Section A.7 of the C2PA 2.3 specification (text provenance) and provides the infrastructure to sign, embed, and verify content provenance across 31 media types."
        whoItsFor="Publishers protecting their content from uncredited AI training, AI companies needing EU AI Act compliance, enterprises requiring tamper-evident audit trails, journalists verifying source authenticity, and any organization producing digital content that must prove its origin."
        keyDifferentiator="Encypher authored the C2PA text provenance standard (Section A.7) and Erik Svilich co-chairs the C2PA Text Provenance Task Force. Sentence-level Merkle tree authentication is Encypher's proprietary technology - not part of C2PA - and provides granularity no other implementation offers."
        primaryValue="Cryptographic proof of content origin that survives distribution. Free verification by anyone. Machine-readable rights that convert innocent infringement to willful infringement. EU AI Act Article 52 compliance before the August 2026 deadline."
        pagePath="/content-provenance"
        pageType="WebPage"
        faq={faqItems}
      />
      <Script
        id="schema-tech-article-content-provenance"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticleSchema) }}
      />
      <Script
        id="schema-faq-content-provenance"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <div className="bg-background text-foreground">
        {/* Breadcrumbs */}
        <div className="container mx-auto px-4 pt-6">
          <Breadcrumbs items={[
            { name: 'Home', href: '/' },
            { name: 'Content Provenance', href: '/content-provenance' },
          ]} />
        </div>

        {/* Hero */}
        <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center">
              <div className="inline-flex items-center gap-2 bg-background border border-border rounded-full px-4 py-1.5 text-sm text-muted-foreground mb-6">
                <Shield className="h-4 w-4" style={{ color: '#2a87c4' }} />
                <span>The definitive resource on content provenance</span>
              </div>
              <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
                What Is Content Provenance?
              </h1>
              <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-4">
                Content provenance is the cryptographic record of a piece of content's origin, authorship, and modification history. It is embedded directly into the content - not stored in a separate database - so the record travels wherever the content goes.
              </p>
              <p className="text-base max-w-3xl mx-auto text-muted-foreground mb-10">
                The <Link href="/c2pa-standard" className="underline hover:text-foreground transition-colors">C2PA open standard</Link> defines how content provenance manifests are structured and verified. Encypher authored Section A.7 of the C2PA 2.3 specification, which covers text provenance - the framework for articles, social posts, and any unstructured text.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button asChild size="lg" className="font-semibold py-3 px-6 rounded-lg shadow-lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                  <Link href="/auth/signin?mode=signup&source=content-provenance">
                    Start Signing Content Free <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline" className="font-semibold py-3 px-6 rounded-lg">
                  <Link href="/tools/verify">
                    Verify Content Now <Eye className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Definition and Why It Matters */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">Why Content Provenance Matters Now</h2>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                Three forces converged in 2024 and 2025 to make content provenance a practical necessity rather than a theoretical concern.
              </p>

              <div className="grid md:grid-cols-3 gap-6 mb-10">
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-4" style={{ backgroundColor: '#2a87c420' }}>
                    <Globe className="h-5 w-5" style={{ color: '#2a87c4' }} />
                  </div>
                  <h3 className="font-semibold mb-2">EU AI Act Deadline: August 2, 2026</h3>
                  <p className="text-sm text-muted-foreground">
                    Article 52 requires AI systems that generate images, audio, and video to mark outputs as AI-generated in a machine-readable format. C2PA manifests satisfy this requirement. Providers who miss the deadline face fines of up to 3% of global annual turnover.
                  </p>
                </div>
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-4" style={{ backgroundColor: '#2a87c420' }}>
                    <Eye className="h-5 w-5" style={{ color: '#2a87c4' }} />
                  </div>
                  <h3 className="font-semibold mb-2">Synthetic Media Explosion</h3>
                  <p className="text-sm text-muted-foreground">
                    AI-generated images, audio deepfakes, and synthetic text appear across news, social media, and enterprise content pipelines. Without provenance, determining what was created by a human versus an AI system requires statistical guessing - which carries false positives. Cryptographic proof eliminates the guessing.
                  </p>
                </div>
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-4" style={{ backgroundColor: '#2a87c420' }}>
                    <Lock className="h-5 w-5" style={{ color: '#2a87c4' }} />
                  </div>
                  <h3 className="font-semibold mb-2">Publisher Rights Erosion</h3>
                  <p className="text-sm text-muted-foreground">
                    AI training and RAG systems use publisher content at scale. Without machine-readable rights embedded in the content, publishers cannot establish formal notice - a prerequisite for willful infringement claims. Content provenance converts passive copyright into active, machine-readable rights terms.
                  </p>
                </div>
              </div>

              <p className="text-muted-foreground text-base leading-relaxed">
                The C2PA standard - backed by Adobe, Microsoft, Google, BBC, and OpenAI, with over 200 member organizations - provides the open infrastructure for content provenance across media types. The standard published its 2.3 specification on January 8, 2026, including Section A.7 on text provenance, which Encypher authored.
              </p>
            </div>
          </div>
        </section>

        {/* How Content Provenance Works */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">How Content Provenance Works</h2>
              <p className="text-muted-foreground mb-8 text-base leading-relaxed">
                Content provenance works through three steps: signing at creation, embedding in the content, and verification by anyone.
              </p>

              <div className="space-y-6">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm" style={{ backgroundColor: '#2a87c4' }}>1</div>
                  <div>
                    <h3 className="font-semibold mb-2">Cryptographic Signing at Creation</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed">
                      When content is created or published, the Encypher API signs it using the publisher's private key. The signature covers the content's hash - a fixed-length fingerprint of the content - along with metadata about the creator, creation time, and any rights terms. If the content is later altered, the hash no longer matches the signature and verification fails.
                    </p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm" style={{ backgroundColor: '#2a87c4' }}>2</div>
                  <div>
                    <h3 className="font-semibold mb-2">Manifest Embedding</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed">
                      For images, audio, and video, the C2PA manifest is embedded in the file's binary container using a JUMBF (JPEG Universal Metadata Box Format) structure. For text, Encypher uses a proprietary method: Unicode variation selectors embedded between words. These characters are invisible to readers but persist through copy-paste, email, and most distribution pathways. The manifest contains the signed claim, the public key certificate chain, and any ingredient references (links to source content used to create the piece).
                    </p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm" style={{ backgroundColor: '#2a87c4' }}>3</div>
                  <div>
                    <h3 className="font-semibold mb-2">Free Verification by Anyone</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed">
                      Anyone can verify content provenance using open-source C2PA libraries or the Encypher verification tool. Verification extracts the manifest, checks the cryptographic signature against the content hash, validates the certificate chain, and returns the provenance record. No account required. No Encypher servers involved in verification - it works entirely on the content itself and the publisher's public key.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Media Types */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-4">Content Provenance Across 31 Media Types</h2>
              <p className="text-muted-foreground mb-8 text-base leading-relaxed">
                The C2PA standard supports content provenance across five media categories. Encypher implements all 31 MIME types through a single unified API.
              </p>

              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                <div className="bg-muted/30 p-5 rounded-lg border border-border">
                  <div className="flex items-center gap-2 mb-3">
                    <Image className="h-5 w-5" style={{ color: '#2a87c4' }} />
                    <h3 className="font-semibold">Images (13 formats)</h3>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    JPEG, PNG, WebP, TIFF, HEIC, HEIF, AVIF, GIF, SVG, BMP, DNG, JPEG 2000, JPEG XL
                  </p>
                  <Link href="/content-provenance/images" className="text-xs mt-2 inline-block hover:underline" style={{ color: '#2a87c4' }}>
                    Image provenance guide &rarr;
                  </Link>
                </div>
                <div className="bg-muted/30 p-5 rounded-lg border border-border">
                  <div className="flex items-center gap-2 mb-3">
                    <Music className="h-5 w-5" style={{ color: '#2a87c4' }} />
                    <h3 className="font-semibold">Audio (6 formats)</h3>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    WAV, MP3, AAC, FLAC, AIFF, M4A
                  </p>
                  <Link href="/content-provenance/audio-video" className="text-xs mt-2 inline-block hover:underline" style={{ color: '#2a87c4' }}>
                    Audio &amp; video provenance guide &rarr;
                  </Link>
                </div>
                <div className="bg-muted/30 p-5 rounded-lg border border-border">
                  <div className="flex items-center gap-2 mb-3">
                    <Video className="h-5 w-5" style={{ color: '#2a87c4' }} />
                    <h3 className="font-semibold">Video (4 formats)</h3>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    MP4, MOV, M4V, MKV
                  </p>
                  <Link href="/content-provenance/audio-video" className="text-xs mt-2 inline-block hover:underline" style={{ color: '#2a87c4' }}>
                    Audio &amp; video provenance guide &rarr;
                  </Link>
                </div>
                <div className="bg-muted/30 p-5 rounded-lg border border-border">
                  <div className="flex items-center gap-2 mb-3">
                    <FileText className="h-5 w-5" style={{ color: '#2a87c4' }} />
                    <h3 className="font-semibold">Documents (5 formats)</h3>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    PDF, DOCX, PPTX, XLSX, plain text (TXT). Section A.7 of C2PA 2.3 covers unstructured text.
                  </p>
                  <Link href="/content-provenance/text" className="text-xs mt-2 inline-block hover:underline" style={{ color: '#2a87c4' }}>
                    Text provenance guide &rarr;
                  </Link>
                </div>
                <div className="bg-muted/30 p-5 rounded-lg border border-border">
                  <div className="flex items-center gap-2 mb-3">
                    <BookOpen className="h-5 w-5" style={{ color: '#2a87c4' }} />
                    <h3 className="font-semibold">Fonts (3 formats)</h3>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    TTF, OTF, WOFF2
                  </p>
                </div>
              </div>

              <p className="text-muted-foreground text-sm">
                The Encypher API handles format detection automatically. Submit any supported file and the API identifies the MIME type, selects the appropriate embedding method, and returns the signed content.
              </p>
            </div>
          </div>
        </section>

        {/* C2PA Standard Section */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-4">The C2PA Open Standard</h2>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                The Coalition for Content Provenance and Authenticity (C2PA) is the standards body that defines how content provenance manifests are structured, embedded, and verified. With over 200 member organizations - including Adobe, Microsoft, Google, BBC, OpenAI, Qualcomm, and Intel - C2PA is the dominant open standard for digital content provenance.
              </p>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                C2PA 2.3, published January 8, 2026, introduced Section A.7: the text provenance framework. Encypher authored this section. Erik Svilich co-chairs the C2PA Text Provenance Task Force.
              </p>
              <p className="text-muted-foreground mb-8 text-base leading-relaxed">
                C2PA operates at the document level: a C2PA manifest authenticates a document as a whole. Encypher's proprietary sentence-level Merkle tree technology works within this framework to provide granular attribution at the sentence or paragraph level - a capability not defined by C2PA itself, but compatible with it.
              </p>
              <div className="flex gap-4">
                <Button asChild variant="outline" className="font-semibold">
                  <Link href="/c2pa-standard">
                    Full C2PA Standard Guide <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="ghost" className="font-semibold">
                  <a href="https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#embedding_manifests_into_unstructured_text" target="_blank" rel="noopener noreferrer">
                    Read Section A.7 <ArrowRight className="ml-2 h-4 w-4" />
                  </a>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Comparison: Provenance vs Detection */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-4">Content Provenance vs. Content Detection</h2>
              <p className="text-muted-foreground mb-8 text-base leading-relaxed">
                Content detection tools - AI detectors, deepfake detectors, and statistical watermark readers like SynthID - attempt to identify content by analyzing statistical patterns. Content provenance proves origin through cryptographic verification. The distinction matters in practice.
              </p>

              <div className="overflow-x-auto mb-8">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 font-semibold">Property</th>
                      <th className="text-left py-3 px-4 font-semibold">Content Provenance</th>
                      <th className="text-left py-3 px-4 font-semibold">Content Detection</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      ['Method', 'Cryptographic signature', 'Statistical pattern analysis'],
                      ['Accuracy', '100% - deterministic', 'Variable - probabilistic'],
                      ['False positives', 'Zero - verification either succeeds or fails', 'Significant - human text flagged as AI'],
                      ['False negatives', 'None if manifest present', 'Frequent after paraphrasing or editing'],
                      ['Tamper evidence', 'Yes - any change breaks signature', 'No - content can be edited to evade'],
                      ['Legal standing', 'Cryptographic proof suitable for litigation', 'Statistical inference not accepted as evidence'],
                      ['Works without original?', 'Yes - manifest is self-contained', 'Depends on model training data'],
                    ].map(([prop, provenance, detection]) => (
                      <tr key={prop} className="border-b border-border">
                        <td className="py-3 px-4 font-medium">{prop}</td>
                        <td className="py-3 px-4 text-muted-foreground">
                          <span className="flex items-center gap-1.5">
                            <CheckCircle2 className="h-4 w-4 flex-shrink-0" style={{ color: '#2a87c4' }} />
                            {provenance}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-muted-foreground">{detection}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <Link href="/compare/content-provenance-vs-content-detection" className="text-sm underline hover:opacity-80" style={{ color: '#2a87c4' }}>
                Full comparison: Content provenance vs. content detection &rarr;
              </Link>
            </div>
          </div>
        </section>

        {/* Content Provenance vs Blockchain */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-4">Content Provenance vs. Blockchain</h2>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                Blockchain-based provenance systems record content hashes on a distributed ledger. This approach stores proof externally - on the chain - rather than embedding it in the content. The practical consequence: if the content is separated from the chain reference (which happens with copy-paste, re-posting, and B2B data distribution), the provenance record is lost.
              </p>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                C2PA manifests are embedded in the content itself. The same piece of text or image carries its provenance record wherever it travels, with no lookup to an external ledger required. Verification works offline, with no network dependency.
              </p>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                Blockchain also introduces latency (block confirmation times), cost (transaction fees), and governance complexity (which chain, which standard). C2PA uses public key infrastructure - the same cryptographic foundation as TLS and code signing - with no per-operation cost.
              </p>
              <Link href="/compare/c2pa-vs-blockchain" className="text-sm underline hover:opacity-80" style={{ color: '#2a87c4' }}>
                Full comparison: C2PA vs. blockchain provenance &rarr;
              </Link>
            </div>
          </div>
        </section>

        {/* Implementation */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-4">Implementing Content Provenance</h2>
              <p className="text-muted-foreground mb-8 text-base leading-relaxed">
                Three integration paths cover the full range of publisher and enterprise use cases.
              </p>

              <div className="grid md:grid-cols-3 gap-6 mb-8">
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-3">API Integration</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    REST API with SDKs in Python, TypeScript, Go, and Rust. Sign a document in a single POST request. Batch endpoints for bulk archive signing. Under 50ms p99 latency.
                  </p>
                  <a href="https://api.encypher.com/docs" target="_blank" rel="noopener noreferrer" className="text-sm underline hover:opacity-80" style={{ color: '#2a87c4' }}>
                    API documentation &rarr;
                  </a>
                </div>
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-3">WordPress Plugin</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    One-click activation. Automatic signing on publish. No engineering required. Compatible with WooCommerce, Yoast, and Elementor.
                  </p>
                  <Link href="/tools/wordpress" className="text-sm underline hover:opacity-80" style={{ color: '#2a87c4' }}>
                    WordPress plugin &rarr;
                  </Link>
                </div>
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-3">Chrome Extension</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Verify content provenance on any web page. Instant visual indicators for signed content. Available in the Chrome Web Store.
                  </p>
                  <Link href="/tools/chrome-extension" className="text-sm underline hover:opacity-80" style={{ color: '#2a87c4' }}>
                    Chrome extension &rarr;
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Cluster Links */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-4">Content Provenance by Audience and Use Case</h2>
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  { title: 'For Publishers', href: '/content-provenance/for-publishers', desc: 'Machine-readable rights, licensing infrastructure, and formal notice capability.' },
                  { title: 'For AI Companies', href: '/content-provenance/for-ai-companies', desc: 'EU AI Act compliance, coalition licensing, and publisher relationship management.' },
                  { title: 'For Enterprises', href: '/content-provenance/for-enterprises', desc: 'Audit trails, AI governance, and tamper-evident documentation for regulated industries.' },
                  { title: 'EU AI Act', href: '/content-provenance/eu-ai-act', desc: 'Article 52 compliance before the August 2, 2026 deadline.' },
                  { title: 'Text Provenance', href: '/content-provenance/text', desc: 'Section A.7 implementation for articles, posts, and unstructured text.' },
                  { title: 'Image Provenance', href: '/content-provenance/images', desc: 'C2PA manifests for 13 image formats including JPEG, PNG, WebP, and HEIC.' },
                  { title: 'Audio and Video', href: '/content-provenance/audio-video', desc: 'Provenance for synthetic voice, AI-generated video, and media files.' },
                  { title: 'Verification', href: '/content-provenance/verification', desc: 'How to verify content provenance, what results mean, and what to do with them.' },
                ].map(item => (
                  <Link key={item.href} href={item.href} className="block bg-background p-4 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                    <h3 className="font-semibold text-sm mb-1.5 group-hover:text-primary transition-colors">{item.title}</h3>
                    <p className="text-xs text-muted-foreground leading-relaxed">{item.desc}</p>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Cross-pillar links */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold tracking-tight mb-6">Related Topics</h2>
              <div className="grid sm:grid-cols-2 gap-4">
                <Link href="/c2pa-standard" className="block bg-muted/30 p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">The C2PA Standard</h3>
                  <p className="text-sm text-muted-foreground">The open standard for content provenance. How JUMBF containers, COSE signatures, and manifest structure work.</p>
                </Link>
                <Link href="/cryptographic-watermarking" className="block bg-muted/30 p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">Cryptographic Watermarking</h3>
                  <p className="text-sm text-muted-foreground">How deterministic proof of origin differs from statistical watermarking and why it survives distribution.</p>
                </Link>
                <Link href="/glossary" className="block bg-muted/30 p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">Content Provenance Glossary</h3>
                  <p className="text-sm text-muted-foreground">Definitions for C2PA, JUMBF, COSE, variation selector markers, Merkle tree authentication, willful infringement, and 40+ terms.</p>
                </Link>
                <Link href="/compare/content-provenance-vs-content-detection" className="block bg-muted/30 p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">Provenance vs. Detection</h3>
                  <p className="text-sm text-muted-foreground">Why cryptographic proof differs from statistical detection and what that means for accuracy and legal standing.</p>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-8">Frequently Asked Questions</h2>
              <div className="space-y-6">
                {faqItems.map((item) => (
                  <div key={item.question} className="border-b border-border pb-6 last:border-0 last:pb-0">
                    <h3 className="font-semibold mb-3">{item.question}</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed">{item.answer}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-20 w-full bg-background">
          <div className="container mx-auto px-4 text-center">
            <div className="max-w-2xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-4">Start Protecting Your Content</h2>
              <p className="text-muted-foreground mb-8">
                The free tier covers 1,000 documents per month. No credit card required. API keys available instantly.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button asChild size="lg" className="font-semibold" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                  <Link href="/auth/signin?mode=signup&source=content-provenance-cta">
                    Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline" className="font-semibold">
                  <Link href="/contact">
                    Talk to Sales
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
