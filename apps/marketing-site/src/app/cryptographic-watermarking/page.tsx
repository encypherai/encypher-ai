import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { Shield, CheckCircle2, ArrowRight, Lock, AlertTriangle, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { getPillarMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = getPillarMetadata('cryptographic-watermarking');

const techArticleSchema = getTechArticleSchema({
  title: 'Cryptographic Watermarking: Proof Embedded in Content',
  description: 'Cryptographic watermarking embeds deterministic proof of origin into text, images, audio, and video. Survives copy-paste, B2B distribution, and scraping. Not statistical guessing.',
  url: `${siteConfig.url}/cryptographic-watermarking`,
  author: 'Erik Svilich',
  datePublished: '2026-01-08',
  dateModified: '2026-03-31',
});

const faqItems = [
  {
    question: 'What is cryptographic watermarking?',
    answer: 'Cryptographic watermarking embeds a cryptographically signed proof of origin directly into content - text, images, audio, or video. Unlike statistical watermarking, the embedded data is deterministic: verification either succeeds or fails with certainty. There are no false positives. The proof includes who created the content, when, and what rights apply.',
  },
  {
    question: 'How is cryptographic watermarking different from statistical watermarking?',
    answer: 'Statistical watermarking - like Google DeepMind\'s SynthID - embeds imperceptible patterns and detects them using a trained model. The result is a probability score. A piece of content might be "87% likely" to be AI-generated. Cryptographic watermarking produces a binary result: the signature is valid or it is not. This matters for legal proceedings, where probabilistic evidence has a very different standing than cryptographic proof.',
  },
  {
    question: 'Does cryptographic watermarking survive copy-paste?',
    answer: 'For text using Encypher\'s variation selector encoding, yes. Unicode variation selectors are preserved through copy-paste in browsers, email clients, Slack, and most text editors. They are stripped by some aggressive text normalization pipelines - this is a known limitation and an active area of technical development. For images, C2PA manifests are stored in the file container and survive most distribution pathways, but aggressive JPEG recompression can sometimes strip the manifest.',
  },
  {
    question: 'What is the difference between cryptographic watermarking and C2PA?',
    answer: 'C2PA is a standard - it defines how provenance manifests are structured and verified. Cryptographic watermarking is a technique - the method of embedding proof. Encypher uses cryptographic watermarking to implement C2PA for images, audio, and video (JUMBF container embedding) and a proprietary extension for text (variation selector encoding). The two concepts are complementary, not competing.',
  },
  {
    question: 'Can cryptographic watermarks be removed?',
    answer: 'Removal is technically possible but consequential. For text, stripping variation selector markers changes the byte sequence of the content, which breaks any hash-based verification against the original. For images, stripping a JUMBF container requires rewriting the file format. The act of removal is itself evidence of tampering in a legal context - a signed content item that loses its manifest has been intentionally altered.',
  },
  {
    question: 'How does cryptographic watermarking establish willful infringement?',
    answer: 'US copyright law permits higher statutory damages - up to $150,000 per work - when infringement is willful. Willfulness requires that the infringer had notice of the copyright. A cryptographic watermark with embedded rights terms is formal notice: every party who handles the content encounters the machine-readable rights terms. An infringer who claims ignorance of rights terms embedded in every copy of a document faces a difficult argument.',
  },
  {
    question: 'What media types support cryptographic watermarking?',
    answer: 'Text: Encypher\'s proprietary variation selector encoding, compatible with C2PA Section A.7. Images: JUMBF container embedding for 13 MIME types including JPEG, PNG, WebP, HEIC, and AVIF. Audio: C2PA manifest embedding for WAV, MP3, AAC, FLAC, AIFF, and M4A. Video: C2PA manifest embedding for MP4, MOV, M4V, and MKV.',
  },
];

export default function CryptographicWatermarkingPage() {
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
        title="Cryptographic Watermarking: Proof Embedded in Content"
        whatWeDo="Cryptographic watermarking embeds a cryptographically signed record of content origin directly into the content file. Verification is deterministic - it succeeds or fails with certainty, with no false positives. Encypher implements cryptographic watermarking for text (via proprietary variation selector encoding), images, audio, and video (via C2PA JUMBF manifests)."
        whoItsFor="Publishers who need proof of ownership that travels with content, AI companies satisfying EU AI Act Article 52 marking requirements, enterprises building tamper-evident audit trails, and anyone who needs to prove origin without relying on probabilistic detection."
        keyDifferentiator="Deterministic proof versus probabilistic detection. A cryptographic watermark does not produce a probability score - it produces a verified signature or a failed verification. This is the distinction that makes it suitable for legal proceedings, regulatory compliance, and licensing enforcement."
        primaryValue="Content provenance proof that survives distribution, establishes formal notice for copyright purposes, satisfies EU AI Act Article 52 machine-readable marking, and enables sentence-level attribution at a granularity no other implementation offers."
        pagePath="/cryptographic-watermarking"
        pageType="WebPage"
        faq={faqItems}
      />
      <Script
        id="schema-tech-article-watermarking"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticleSchema) }}
      />
      <Script
        id="schema-faq-watermarking"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <div className="bg-background text-foreground">
        {/* Breadcrumbs */}
        <div className="container mx-auto px-4 pt-6">
          <Breadcrumbs items={[
            { name: 'Home', href: '/' },
            { name: 'Cryptographic Watermarking', href: '/cryptographic-watermarking' },
          ]} />
        </div>

        {/* Hero */}
        <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center">
              <div className="inline-flex items-center gap-2 bg-background border border-border rounded-full px-4 py-1.5 text-sm text-muted-foreground mb-6">
                <Lock className="h-4 w-4" style={{ color: '#2a87c4' }} />
                <span>Deterministic proof, not probabilistic detection</span>
              </div>
              <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
                Cryptographic Watermarking
              </h1>
              <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-4">
                Cryptographic watermarking embeds a signed, verifiable record of content origin directly into the file. Unlike statistical watermarking, it produces proof - not probabilities.
              </p>
              <p className="text-base max-w-3xl mx-auto text-muted-foreground mb-10">
                Encypher implements cryptographic watermarking for text using proprietary variation selector encoding and for images, audio, and video using <Link href="/c2pa-standard" className="underline hover:text-foreground transition-colors">C2PA manifests</Link>. The proof travels with the content wherever it goes.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button asChild size="lg" className="font-semibold py-3 px-6 rounded-lg shadow-lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                  <Link href="/auth/signin?mode=signup&source=cryptographic-watermarking">
                    Start Watermarking Content <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline" className="font-semibold py-3 px-6 rounded-lg">
                  <Link href="/content-provenance">
                    What Is Content Provenance? <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* What Cryptographic Watermarking Is */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">What Cryptographic Watermarking Is</h2>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                A cryptographic watermark is a data payload - signed with a private key, verified with a public key - embedded in content using a method that makes it survive normal distribution. The payload contains information about who created the content, when, what tools produced it, and what rights apply.
              </p>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                Cryptographic means the signature is mathematically bound to the content. Any change to the content changes its hash, which no longer matches the signed value. Watermarking means the payload is embedded in the content itself - not in a separate database or an external reference that can be lost.
              </p>
              <p className="text-muted-foreground mb-8 text-base leading-relaxed">
                The combination produces a self-contained proof: the content carries its own verification data. No lookup to an external registry. No dependency on a third party. Anyone with the public key can verify independently.
              </p>

              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircle2 className="h-5 w-5 flex-shrink-0" style={{ color: '#2a87c4' }} />
                    <h3 className="font-semibold">Cryptographic Watermarking</h3>
                  </div>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex items-start gap-2"><span style={{ color: '#2a87c4' }}>+</span> Deterministic: verification passes or fails</li>
                    <li className="flex items-start gap-2"><span style={{ color: '#2a87c4' }}>+</span> Zero false positives</li>
                    <li className="flex items-start gap-2"><span style={{ color: '#2a87c4' }}>+</span> Tamper-evident: any change breaks the signature</li>
                    <li className="flex items-start gap-2"><span style={{ color: '#2a87c4' }}>+</span> Self-contained: no external database required</li>
                    <li className="flex items-start gap-2"><span style={{ color: '#2a87c4' }}>+</span> Suitable for legal proceedings</li>
                    <li className="flex items-start gap-2"><span style={{ color: '#2a87c4' }}>+</span> Machine-readable rights terms</li>
                  </ul>
                </div>
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
                    <h3 className="font-semibold">Statistical Watermarking (e.g. SynthID)</h3>
                  </div>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex items-start gap-2"><span>-</span> Probabilistic: returns a confidence score</li>
                    <li className="flex items-start gap-2"><span>-</span> False positives affect human-created content</li>
                    <li className="flex items-start gap-2"><span>-</span> Pattern can be reduced by editing or paraphrasing</li>
                    <li className="flex items-start gap-2"><span>-</span> Requires access to the detection model</li>
                    <li className="flex items-start gap-2"><span>-</span> Not accepted as legal proof</li>
                    <li className="flex items-start gap-2"><span>-</span> Cannot encode rights terms</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Proof vs Probability */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">Proof vs. Probability: Why the Distinction Matters</h2>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                Detection tools identify content by detecting patterns. They answer: "does this look like AI-generated content?" The answer is statistical. Even the best systems misclassify human writing as AI-generated and vice versa.
              </p>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                Cryptographic watermarking answers a different question: "was this content signed by this private key at this time?" That question has a binary answer. The signature either matches or it does not.
              </p>

              <div className="bg-background border border-border rounded-lg p-6 mb-6">
                <h3 className="font-semibold mb-4">In Practice</h3>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-muted-foreground">Detection approach</h4>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      A news organization uses an AI detector on a submitted article. Result: "72% likely AI-generated." The organization must decide whether to reject the article based on a probabilistic score. False positives harm legitimate contributors. The score can be gamed by rewriting.
                    </p>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-muted-foreground">Cryptographic proof approach</h4>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      An AI company embeds a C2PA manifest in every generated article, marking it as AI-produced with the generation timestamp. The news organization verifies the manifest. Result: either "signed as AI-generated by model X on date Y" or "no valid provenance manifest found." No ambiguity.
                    </p>
                  </div>
                </div>
              </div>

              <p className="text-muted-foreground text-base leading-relaxed">
                The same logic applies in legal contexts. A court considering copyright infringement cannot act on a probability score. A valid cryptographic signature is documentation. The distinction between what can be proven and what can only be estimated determines the legal outcome.
              </p>
            </div>
          </div>
        </section>

        {/* Cryptographic Watermarking for Text */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-4">Cryptographic Watermarking for Text</h2>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                Text watermarking presents a harder problem than image or video watermarking. Plain text has no binary container. Adding visible characters changes the content. Steganographic approaches must work within the character encoding itself.
              </p>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                Encypher's proprietary approach uses Unicode variation selectors - control characters in the Unicode standard designed to modify the visual rendering of the preceding character. In practice, standard variation selectors are invisible between words. Encypher uses 256 variation selectors (VS1-VS256) to encode binary data, embedding the manifest payload across word boundaries in the text.
              </p>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                The result: a signed text document that carries its C2PA manifest invisibly, survives copy-paste, and can be verified by anyone with the publisher's public key. Readers see no difference. The byte sequence differs from a plain-text version of the same content, which is how verification works.
              </p>

              <div className="bg-muted/30 p-6 rounded-lg border border-border mb-6">
                <h3 className="font-semibold mb-3">Sentence-Level Merkle Tree Attribution</h3>
                <p className="text-sm text-muted-foreground leading-relaxed mb-3">
                  Encypher's proprietary sentence-level technology builds a Merkle tree over the sentences of a document. Each leaf node is the hash of one sentence. The tree root is signed. This structure makes it possible to prove that a specific sentence - not just a document - came from a specific source, and that the sentence has not been altered.
                </p>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  C2PA authenticates documents as a whole. Sentence-level attribution is Encypher's proprietary layer on top of C2PA. It is the technology that turns "this document was used" into "sentence 47 from this article was used." That granularity is what makes licensing and enforcement practical at scale.
                </p>
              </div>

              <Link href="/content-provenance/text" className="text-sm underline hover:opacity-80" style={{ color: '#2a87c4' }}>
                Text provenance technical guide &rarr;
              </Link>
            </div>
          </div>
        </section>

        {/* Media Watermarking */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">Cryptographic Watermarking for Images, Audio, and Video</h2>
              <p className="text-muted-foreground mb-8 text-base leading-relaxed">
                For binary media types, Encypher uses C2PA JUMBF container embedding - the standard approach for images, audio, and video. The manifest travels with the file.
              </p>

              <div className="grid md:grid-cols-3 gap-4 mb-8">
                <div className="bg-background p-5 rounded-lg border border-border">
                  <h3 className="font-semibold text-sm mb-2">Images</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed mb-2">
                    C2PA JUMBF manifest embedded in 13 formats: JPEG, PNG, WebP, TIFF, HEIC, HEIF, AVIF, GIF, SVG, BMP, DNG, JPEG 2000, JPEG XL.
                  </p>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Manifests survive most distribution pathways. Aggressive JPEG recompression may strip the container - an active area of C2PA technical work.
                  </p>
                </div>
                <div className="bg-background p-5 rounded-lg border border-border">
                  <h3 className="font-semibold text-sm mb-2">Audio</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed mb-2">
                    C2PA manifest embedding for WAV, MP3, AAC, FLAC, AIFF, M4A. Critical for synthetic voice attribution: AI-generated audio carries its generation metadata.
                  </p>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    EU AI Act Article 52 applies to AI-generated audio. C2PA manifests with the appropriate digital source type field satisfy the marking requirement.
                  </p>
                </div>
                <div className="bg-background p-5 rounded-lg border border-border">
                  <h3 className="font-semibold text-sm mb-2">Video</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed mb-2">
                    C2PA manifest embedding for MP4, MOV, M4V, MKV. Ingredient chains trace AI-generated video back to source images or models.
                  </p>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Live stream provenance is an emerging C2PA use case. Deepfake detection is strengthened when legitimate source video carries provenance that a deepfake version lacks.
                  </p>
                </div>
              </div>

              <Link href="/content-provenance/audio-video" className="text-sm underline hover:opacity-80" style={{ color: '#2a87c4' }}>
                Audio and video provenance guide &rarr;
              </Link>
            </div>
          </div>
        </section>

        {/* Why It Survives Distribution */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">Why Cryptographic Watermarking Survives and Detection Does Not</h2>
              <p className="text-muted-foreground mb-8 text-base leading-relaxed">
                The content lifecycle for publisher material looks like this: original publication, aggregation by news wire services, embedding in newsletters, scraping by AI training pipelines, use in RAG systems, and redistribution in AI-generated summaries that cite the source. Detection tools are applied at a single point in this chain. Watermarks travel through all of it.
              </p>

              <div className="space-y-4 mb-8">
                {[
                  {
                    scenario: 'Copy-paste across platforms',
                    detection: 'Loss of context. Most detectors require the full text. Partial text produces unreliable scores.',
                    watermark: 'Variation selector markers copy with the text. A 500-word excerpt carries the same manifest as the full article.',
                  },
                  {
                    scenario: 'B2B data licensing',
                    detection: 'Licensee strips headers and footers. Detector sees no attribution. No way to trace origin.',
                    watermark: 'Manifest is embedded in the content body. No header or footer required. Origin traces to the original publisher.',
                  },
                  {
                    scenario: 'AI training corpus',
                    detection: 'Training pipelines apply normalization that removes detection-relevant patterns. Content in a training corpus is undetectable.',
                    watermark: 'Unicode variation selectors survive standard normalization. The manifest persists in the training data.',
                  },
                  {
                    scenario: 'Paraphrasing and summarization',
                    detection: 'Statistical patterns are reset by paraphrasing. Detectors cannot identify AI-summarized content as derived from a specific source.',
                    watermark: 'Sentence-level Merkle attribution identifies source sentences even in a summarized form. The relationship between summary and source is traceable.',
                  },
                ].map(item => (
                  <div key={item.scenario} className="bg-muted/30 p-5 rounded-lg border border-border">
                    <h3 className="font-semibold text-sm mb-3">{item.scenario}</h3>
                    <div className="grid md:grid-cols-2 gap-3">
                      <div>
                        <p className="text-xs text-muted-foreground font-medium mb-1">Detection</p>
                        <p className="text-xs text-muted-foreground leading-relaxed">{item.detection}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium mb-1" style={{ color: '#2a87c4' }}>Cryptographic Watermark</p>
                        <p className="text-xs text-muted-foreground leading-relaxed">{item.watermark}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Legal Implications */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">Legal Implications of Cryptographic Watermarking</h2>

              <div className="space-y-6">
                <div>
                  <h3 className="font-semibold mb-3">Formal Notice and Willful Infringement</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed mb-3">
                    US copyright law (17 U.S.C. sections 504(c)) provides for statutory damages of $750 to $30,000 per infringed work, and up to $150,000 per work when infringement is willful. The distinction between innocent and willful infringement turns on whether the infringer had notice.
                  </p>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    A cryptographic watermark with embedded rights terms - embedded in every copy of the content, surviving distribution - constitutes formal notice. An AI training pipeline that processes signed content and proceeds without a license cannot credibly claim it had no notice of the rights terms. The burden shifts.
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">Evidence in Legal Proceedings</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    A valid cryptographic signature is a form of documentary evidence. It can establish: who signed the content, when the signing occurred (timestamp in the manifest), that the content has not been altered since signing (any modification breaks the signature), and what rights terms were attached. This is substantially stronger than a declaration from a publisher or a statistical detection result. Courts in multiple jurisdictions have admitted cryptographic evidence in copyright proceedings.
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">EU AI Act Compliance</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    EU AI Act Article 52 requires machine-readable marking of AI-generated content. C2PA manifests with the appropriate digital source type field satisfy this requirement. Non-compliance carries fines of up to 3% of global annual turnover. The August 2, 2026 deadline applies to providers of covered AI systems operating in the EU market.
                  </p>
                </div>
              </div>

              <div className="mt-6">
                <Link href="/cryptographic-watermarking/legal-implications" className="text-sm underline hover:opacity-80" style={{ color: '#2a87c4' }}>
                  Full guide: Legal implications of cryptographic watermarking &rarr;
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Implementation */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">Implementation</h2>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                Encypher provides two layers of implementation. C2PA-standard document-level signing works for images, audio, video, and documents. Encypher's proprietary sentence-level layer adds granular attribution on top of C2PA for text content.
              </p>

              <div className="grid md:grid-cols-2 gap-6 mb-8">
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-3">C2PA Document-Level</h3>
                  <p className="text-sm text-muted-foreground mb-4 leading-relaxed">
                    Standard for any file type. Submit via REST API, Python SDK, TypeScript SDK, Go SDK, or Rust SDK. Returns the signed file with embedded manifest. Free to verify using open-source C2PA libraries.
                  </p>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 flex-shrink-0" style={{ color: '#2a87c4' }} /> 31 MIME types</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 flex-shrink-0" style={{ color: '#2a87c4' }} /> Open-source verification</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 flex-shrink-0" style={{ color: '#2a87c4' }} /> EU AI Act Article 52 compatible</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 flex-shrink-0" style={{ color: '#2a87c4' }} /> BYOK for enterprise</li>
                  </ul>
                </div>
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-3">Sentence-Level Attribution</h3>
                  <p className="text-sm text-muted-foreground mb-4 leading-relaxed">
                    Encypher's proprietary layer for text. Builds a Merkle tree over sentences. Proves which specific sentences were used in a derivative work. Identifies quote-level reuse across AI training and RAG pipelines.
                  </p>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 flex-shrink-0" style={{ color: '#2a87c4' }} /> Sentence-granularity proof</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 flex-shrink-0" style={{ color: '#2a87c4' }} /> Survives copy-paste</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 flex-shrink-0" style={{ color: '#2a87c4' }} /> Patent-pending</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 flex-shrink-0" style={{ color: '#2a87c4' }} /> Enterprise tier</li>
                  </ul>
                </div>
              </div>

              <div className="flex gap-4">
                <Button asChild size="sm" className="font-semibold" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                  <Link href="/auth/signin?mode=signup&source=crypto-watermark">
                    Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild size="sm" variant="outline" className="font-semibold">
                  <a href="https://api.encypher.com/docs" target="_blank" rel="noopener noreferrer">
                    API Documentation <FileText className="ml-2 h-4 w-4" />
                  </a>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Cross-pillar links */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold tracking-tight mb-6">Related Topics</h2>
              <div className="grid sm:grid-cols-2 gap-4">
                <Link href="/content-provenance" className="block bg-background p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">What Is Content Provenance?</h3>
                  <p className="text-sm text-muted-foreground">The broader context for cryptographic watermarking: how provenance works across all media types.</p>
                </Link>
                <Link href="/c2pa-standard" className="block bg-background p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">The C2PA Standard</h3>
                  <p className="text-sm text-muted-foreground">The open standard that defines how cryptographic watermarks are structured and verified for binary media types.</p>
                </Link>
                <Link href="/glossary#cryptographic-watermarking" className="block bg-background p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">Glossary: Watermarking Terms</h3>
                  <p className="text-sm text-muted-foreground">Definitions for cryptographic watermarking, statistical watermarking, variation selector markers, and related terms.</p>
                </Link>
                <Link href="/cryptographic-watermarking/legal-implications" className="block bg-background p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">Legal Implications</h3>
                  <p className="text-sm text-muted-foreground">How cryptographic watermarks establish formal notice, support willful infringement claims, and satisfy regulatory requirements.</p>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-16 w-full bg-background border-b border-border">
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
        <section className="py-20 w-full bg-muted/30">
          <div className="container mx-auto px-4 text-center">
            <div className="max-w-2xl mx-auto">
              <Shield className="h-8 w-8 mx-auto mb-4" style={{ color: '#2a87c4' }} />
              <h2 className="text-3xl font-bold tracking-tight mb-4">Embed Proof in Your Content</h2>
              <p className="text-muted-foreground mb-8">
                Cryptographic watermarking that survives copy-paste, B2B distribution, and AI training pipelines. Free tier for up to 1,000 documents per month.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button asChild size="lg" className="font-semibold" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                  <Link href="/auth/signin?mode=signup&source=crypto-watermark-cta">
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
