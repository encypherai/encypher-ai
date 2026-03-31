import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { Shield, CheckCircle2, ArrowRight, Users, BookOpen, Globe, Code } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { getPillarMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = getPillarMetadata('c2pa-standard');

const techArticleSchema = getTechArticleSchema({
  title: 'The C2PA Standard: How Content Provenance Works',
  description: 'C2PA is the open standard for content provenance, backed by Adobe, Microsoft, Google, BBC, and OpenAI. Encypher authored Section A.7 (text provenance) and co-chairs the task force.',
  url: `${siteConfig.url}/c2pa-standard`,
  author: 'Erik Svilich',
  datePublished: '2026-01-08',
  dateModified: '2026-03-31',
});

const faqItems = [
  {
    question: 'What does C2PA stand for?',
    answer: 'C2PA stands for Coalition for Content Provenance and Authenticity. It is the standards body - not a product or platform - that defines how content provenance manifests are structured, embedded, and verified. The coalition has over 200 member organizations.',
  },
  {
    question: 'Who founded C2PA?',
    answer: 'C2PA was founded in 2021 by Adobe, Arm, Intel, Microsoft, Qualcomm, and Twitter (now X). The Content Authenticity Initiative (CAI), operated by Adobe, provides a public-facing interface and verification tools. The two organizations work in parallel: CAI raises awareness, C2PA defines the standard.',
  },
  {
    question: 'What is a C2PA manifest?',
    answer: 'A C2PA manifest is a structured record embedded in a content file that contains: who created the content, when it was created, what tools were used, any edits or transformations made, and a cryptographic signature proving the record has not been altered. For images and video, the manifest is stored in a JUMBF container. For text, it is embedded using a protocol defined in Section A.7.',
  },
  {
    question: 'What is Section A.7 of the C2PA specification?',
    answer: 'Section A.7 of the C2PA 2.3 specification defines how provenance manifests are embedded into unstructured text - articles, social posts, and any text-based content. It defines encoding methods, integrity verification, and the claim structure for text content. Encypher authored this section. The specification was published on January 8, 2026.',
  },
  {
    question: 'Is C2PA free to implement?',
    answer: 'Yes. The C2PA specification is free to read and implement. Open-source verification libraries are available in multiple languages. The standard is governed as a community specification under the Joint Development Foundation.',
  },
  {
    question: 'Does C2PA work across the internet?',
    answer: 'C2PA manifests are embedded in content files and travel with the content. Any party with the signed content and access to the publisher\'s public key can verify provenance independently, without network access to a central registry. The certificate chain within the manifest provides the verification path.',
  },
  {
    question: 'What is the difference between C2PA and the Content Authenticity Initiative (CAI)?',
    answer: 'C2PA is the technical standards organization that publishes the specification. The Content Authenticity Initiative (CAI), run by Adobe, is a broader coalition that promotes adoption and provides consumer-facing tools like the Content Credentials browser plugin. CAI implements C2PA; it does not replace it.',
  },
  {
    question: 'How does C2PA handle AI-generated content?',
    answer: 'C2PA defines a "digital source type" field in the claim that identifies how content was produced. AI-generated content is marked with c2pa.digitalSourceType of trainedAlgorithmicMedia or compositeWithTrainedAlgorithmicMedia. This machine-readable flag satisfies EU AI Act Article 52 marking requirements for AI-generated images, audio, and video.',
  },
];

export default function C2PAStandardPage() {
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
        title="The C2PA Standard: How Content Provenance Works"
        whatWeDo="C2PA (Coalition for Content Provenance and Authenticity) is the open standard for embedding cryptographic provenance into digital content. Over 200 member organizations including Adobe, Microsoft, Google, BBC, and OpenAI. C2PA 2.3 published January 8, 2026. Encypher authored Section A.7 (text provenance). Erik Svilich co-chairs the C2PA Text Provenance Task Force."
        whoItsFor="Developers implementing content provenance, publishers protecting content rights, AI companies achieving EU AI Act compliance, media organizations verifying authenticity, and any organization that needs to prove the origin of digital content."
        keyDifferentiator="Encypher authored Section A.7 of the C2PA 2.3 specification - the text provenance framework. This is the standard that defines how articles, social posts, and unstructured text carry cryptographic provenance. No other commercial implementation has this level of standards authority."
        primaryValue="Open standard supported by the entire industry. Free to implement. Verification requires no account or third-party dependency. Machine-readable rights terms that travel with content. EU AI Act Article 52 compliance via C2PA digital source type fields."
        pagePath="/c2pa-standard"
        pageType="WebPage"
        faq={faqItems}
      />
      <Script
        id="schema-tech-article-c2pa"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticleSchema) }}
      />
      <Script
        id="schema-faq-c2pa"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <div className="bg-background text-foreground">
        {/* Breadcrumbs */}
        <div className="container mx-auto px-4 pt-6">
          <Breadcrumbs items={[
            { name: 'Home', href: '/' },
            { name: 'C2PA Standard', href: '/c2pa-standard' },
          ]} />
        </div>

        {/* Hero */}
        <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center">
              <div className="inline-flex items-center gap-2 bg-background border border-border rounded-full px-4 py-1.5 text-sm text-muted-foreground mb-6">
                <Shield className="h-4 w-4" style={{ color: '#2a87c4' }} />
                <span>Encypher co-chairs the C2PA Text Provenance Task Force</span>
              </div>
              <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
                The C2PA Standard
              </h1>
              <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-4">
                The Coalition for Content Provenance and Authenticity defines how cryptographic provenance is embedded in digital content. Over 200 member organizations. C2PA 2.3 published January 8, 2026.
              </p>
              <p className="text-base max-w-3xl mx-auto text-muted-foreground mb-10">
                Encypher authored Section A.7 of the C2PA 2.3 specification, which defines text provenance - the framework for embedding and verifying provenance in articles, posts, and unstructured text.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button asChild size="lg" className="font-semibold py-3 px-6 rounded-lg shadow-lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                  <Link href="/auth/signin?mode=signup&source=c2pa-standard">
                    Implement C2PA Now <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline" className="font-semibold py-3 px-6 rounded-lg">
                  <a href="https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html" target="_blank" rel="noopener noreferrer">
                    Read the Specification <BookOpen className="ml-2 h-4 w-4" />
                  </a>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* What C2PA Is */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">What Is C2PA?</h2>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                The Coalition for Content Provenance and Authenticity (C2PA) is a standards body that publishes open technical specifications for digital content provenance. It is not a product, not a platform, and not a certification body. It defines how content provenance manifests are structured, embedded, and verified.
              </p>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                C2PA operates under the Joint Development Foundation, an affiliate of the Linux Foundation. The specification is free to implement. Governance is community-driven, with working groups for specific media types and use cases.
              </p>

              <div className="grid md:grid-cols-3 gap-6 mb-8">
                <div className="bg-muted/30 p-5 rounded-lg border border-border text-center">
                  <div className="text-3xl font-bold mb-1" style={{ color: '#2a87c4' }}>200+</div>
                  <div className="text-sm text-muted-foreground">Member organizations</div>
                </div>
                <div className="bg-muted/30 p-5 rounded-lg border border-border text-center">
                  <div className="text-3xl font-bold mb-1" style={{ color: '#2a87c4' }}>2021</div>
                  <div className="text-sm text-muted-foreground">Year founded</div>
                </div>
                <div className="bg-muted/30 p-5 rounded-lg border border-border text-center">
                  <div className="text-3xl font-bold mb-1" style={{ color: '#2a87c4' }}>2.3</div>
                  <div className="text-sm text-muted-foreground">Latest specification (Jan 8, 2026)</div>
                </div>
              </div>

              <p className="text-muted-foreground text-base leading-relaxed">
                The major members include Adobe (who operates the Content Authenticity Initiative), Microsoft, Google, BBC, Reuters, OpenAI, Qualcomm, Intel, Arm, NVIDIA, Sony, and Truepic. Encypher is a member and co-chairs the Text Provenance Task Force.
              </p>
            </div>
          </div>
        </section>

        {/* History */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">C2PA History and Versions</h2>
              <div className="space-y-4">
                {[
                  { date: '2021', event: 'C2PA founded by Adobe, Arm, Intel, Microsoft, Qualcomm, and Twitter. Content Authenticity Initiative (CAI) launched to promote adoption.' },
                  { date: '2022', event: 'C2PA 1.0 published. First specification defining the JUMBF manifest structure, COSE signing, and claim format for images and video.' },
                  { date: '2023', event: 'C2PA 1.3 published. Added support for audio, live streams, and expanded ingredient chain capabilities. Adoption grows in camera hardware (Leica, Nikon) and social platforms (LinkedIn, TikTok).' },
                  { date: '2024', event: 'C2PA 2.0 published. Significant revision to the manifest structure, improved cross-platform compatibility. EU AI Act Article 50 takes effect (August 2024). Google, OpenAI join as major members.' },
                  { date: 'Jan 8, 2026', event: 'C2PA 2.3 published. Section A.7 (text provenance) included - authored by Encypher. Full framework for embedding and verifying provenance in unstructured text. EU AI Act Article 52 deadline approaches (August 2, 2026).' },
                ].map(item => (
                  <div key={item.date} className="flex gap-4">
                    <div className="flex-shrink-0 text-sm font-semibold w-24 pt-0.5" style={{ color: '#2a87c4' }}>{item.date}</div>
                    <div className="text-sm text-muted-foreground leading-relaxed">{item.event}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* How C2PA Manifests Work */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">How C2PA Manifests Work</h2>
              <p className="text-muted-foreground mb-8 text-base leading-relaxed">
                A C2PA manifest contains four main components. You do not need to understand the technical details to use C2PA - the Encypher API handles all of this automatically - but understanding the structure helps in evaluating the standard.
              </p>

              <div className="space-y-6 mb-8">
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-2">JUMBF Container</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    For images and media files, the manifest is stored in a JUMBF (JPEG Universal Metadata Box Format) container embedded in the file's binary. JUMBF is a standardized format for metadata boxes that supports nesting - a manifest can contain multiple claims, each with its own signature. The container is part of the file but ignored by applications that do not implement C2PA.
                  </p>
                </div>
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-2">Claim Structure</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    A claim is the core data unit in a C2PA manifest. It records: who created or modified the content (the assertion), what actions were taken (the actions list, such as "created," "edited," "transcoded"), the content hash at signing time, and any ingredients (source files used to produce this file, with their own manifests). Claims are structured as CBOR (Concise Binary Object Representation) for compact encoding.
                  </p>
                </div>
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-2">COSE Signature</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    COSE (CBOR Object Signing and Encryption) is the signing standard used for C2PA claims. It is the same cryptographic foundation as JOSE (JSON Object Signing and Encryption) but uses CBOR encoding for compactness. The COSE signature covers the claim hash. If the claim is altered after signing, the signature verification fails. The signer's public key certificate is included in the manifest for independent verification.
                  </p>
                </div>
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-2">Certificate Chain</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    The manifest includes the signer's X.509 certificate chain, which allows any verifier to validate the signature without a central registry. Publishers use their own certificates (BYOK - bring your own key) or Encypher-managed certificates depending on their compliance requirements. The chain anchors to a trusted root certificate authority, the same infrastructure used for TLS and code signing.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section A.7: Text Provenance */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-4">C2PA for Text: Section A.7</h2>
              <div className="bg-background border border-border rounded-lg p-6 mb-6">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded flex items-center justify-center" style={{ backgroundColor: '#2a87c420' }}>
                    <BookOpen className="h-4 w-4" style={{ color: '#2a87c4' }} />
                  </div>
                  <div>
                    <p className="font-semibold text-sm mb-1">Standards Authority</p>
                    <p className="text-sm text-muted-foreground">
                      Encypher authored Section A.7 of the C2PA 2.3 specification. Erik Svilich co-chairs the C2PA Text Provenance Task Force. This is the definitive standard for embedding provenance in unstructured text content.
                    </p>
                  </div>
                </div>
              </div>
              <p className="text-muted-foreground mb-6 text-base leading-relaxed">
                Text presents unique challenges for content provenance. Unlike image or video files, plain text has no binary container to embed a JUMBF manifest. Section A.7 defines three encoding approaches:
              </p>

              <div className="space-y-4 mb-8">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-2 h-2 rounded-full mt-2" style={{ backgroundColor: '#2a87c4' }}></div>
                  <div>
                    <h3 className="font-semibold text-sm mb-1">Unicode Variation Selector Encoding</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      Unicode variation selectors (VS1-VS256) are control characters that modify the visual appearance of the preceding character. In text provenance, they are used to encode binary data - the manifest payload - between visible words. The characters are invisible to readers and survive copy-paste across most applications. This is Encypher's primary text encoding method.
                    </p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-2 h-2 rounded-full mt-2" style={{ backgroundColor: '#2a87c4' }}></div>
                  <div>
                    <h3 className="font-semibold text-sm mb-1">Sidecar Manifest</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      A separate manifest file accompanying the text content. Useful for content management systems where modifying the text itself is not appropriate. The manifest references the text content by hash.
                    </p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-2 h-2 rounded-full mt-2" style={{ backgroundColor: '#2a87c4' }}></div>
                  <div>
                    <h3 className="font-semibold text-sm mb-1">Remote Reference</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      The text includes a reference (URL or cryptographic identifier) to a manifest stored externally. Provides a path for very long documents where inline embedding would be impractical.
                    </p>
                  </div>
                </div>
              </div>

              <p className="text-muted-foreground text-sm mb-6">
                C2PA authenticates text at the document level. Sentence-level Merkle tree attribution - which identifies exactly which sentences were used or modified - is Encypher's proprietary technology, built on top of the C2PA framework.
              </p>

              <Button asChild variant="outline" size="sm">
                <a href="https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#embedding_manifests_into_unstructured_text" target="_blank" rel="noopener noreferrer">
                  Read Section A.7 in the C2PA Specification <ArrowRight className="ml-2 h-3 w-3" />
                </a>
              </Button>
            </div>
          </div>
        </section>

        {/* C2PA vs Other Approaches */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">C2PA vs. Other Approaches</h2>

              <div className="space-y-6">
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-2">C2PA vs. SynthID (Google DeepMind)</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    SynthID is a statistical watermarking system that embeds imperceptible patterns in AI-generated images and audio. It identifies AI-generated content by detecting these patterns - a probabilistic approach. C2PA is cryptographic: verification succeeds or fails with certainty. SynthID cannot prove who created content or when; C2PA can. SynthID is fragile under aggressive compression; C2PA manifests are stored in a dedicated container. SynthID is proprietary to Google; C2PA is open.
                  </p>
                </div>
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-2">C2PA vs. Blockchain Provenance</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Blockchain systems record content hashes on a distributed ledger. The provenance record lives on the chain, not in the content. When content is copied or redistributed without the chain reference, provenance is lost. C2PA manifests are embedded in the file and travel with it. Blockchain also introduces transaction costs and latency; C2PA verification is free and offline. See the <Link href="/compare/c2pa-vs-blockchain" className="underline hover:opacity-80" style={{ color: '#2a87c4' }}>full comparison</Link>.
                  </p>
                </div>
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-2">C2PA vs. Fingerprinting</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Perceptual hashing (pHash) and content fingerprinting identify content by its visual or acoustic characteristics. These are lookup systems: you compare a fingerprint against a database to find a match. C2PA is a signing system: the manifest contains all necessary verification data. Fingerprinting requires a populated database and cannot prove creation date or rights terms. C2PA is self-contained.
                  </p>
                </div>
                <div className="bg-muted/30 p-6 rounded-lg border border-border">
                  <h3 className="font-semibold mb-2">C2PA vs. AI Detection</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    AI detection tools classify content as human-written or AI-generated using machine learning models. They produce probabilities, not proof. False positive rates are significant - human-written content is frequently misclassified, with serious consequences in academic and professional contexts. C2PA does not detect; it proves. A C2PA manifest on AI-generated content proves it was AI-generated. A C2PA manifest on human-authored content proves that too.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Who Uses C2PA */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">Who Implements C2PA</h2>
              <p className="text-muted-foreground mb-8 text-base leading-relaxed">
                C2PA adoption spans hardware manufacturers, software platforms, AI companies, and news organizations.
              </p>

              <div className="grid sm:grid-cols-2 gap-4 mb-8">
                {[
                  { category: 'Camera Manufacturers', examples: 'Leica, Nikon, Sony - embedding C2PA manifests at capture for photojournalism authenticity.' },
                  { category: 'AI Image Generators', examples: 'Adobe Firefly, DALL-E (OpenAI), Midjourney - marking AI-generated images with C2PA digital source type fields.' },
                  { category: 'Social Platforms', examples: 'LinkedIn, TikTok - displaying Content Credentials badges on supported content.' },
                  { category: 'News Organizations', examples: 'BBC, Reuters, Associated Press - signing news photography for distribution authenticity.' },
                  { category: 'Tech Platforms', examples: 'Adobe (Photoshop, Lightroom, Premiere), Microsoft (Bing Image Creator, Designer).' },
                  { category: 'Text Provenance', examples: 'Encypher - Section A.7 authors, co-chairs of the Text Provenance Task Force. The only commercial implementation of C2PA text provenance.' },
                ].map(item => (
                  <div key={item.category} className="bg-background p-5 rounded-lg border border-border">
                    <h3 className="font-semibold text-sm mb-2">{item.category}</h3>
                    <p className="text-xs text-muted-foreground leading-relaxed">{item.examples}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* C2PA and Regulation */}
        <section className="py-16 w-full bg-background border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">C2PA and Regulation</h2>

              <div className="space-y-6">
                <div>
                  <h3 className="font-semibold mb-3">EU AI Act</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed mb-3">
                    Article 52(1) of the EU AI Act requires providers of AI systems that generate images, audio, and video to ensure outputs are marked as AI-generated in a machine-readable format. Article 50 (effective August 2024) covers general-purpose AI systems used in consumer-facing applications. The August 2, 2026 deadline triggers fines for non-compliance.
                  </p>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    C2PA manifests with the appropriate digital source type field satisfy the machine-readable marking requirement. The EU AI Act does not mandate C2PA specifically, but C2PA is the dominant open standard aligned with the requirement. Confirm with your legal counsel that your specific implementation satisfies the obligations in your jurisdiction.
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold mb-3">US Copyright Law</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    US copyright law distinguishes between innocent infringement (where the infringer had no notice of the copyright) and willful infringement (where notice existed). C2PA manifests with embedded rights terms constitute formal notice to any party who encounters the content. This distinction matters for statutory damages: up to $30,000 per work for innocent infringement, up to $150,000 per work for willful infringement. C2PA does not create a legal right - that is governed by copyright law - but it does establish the notice that converts one damage category to the other.
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold mb-3">Potential US Framework</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    Multiple pieces of US legislation have referenced C2PA or similar standards as a basis for AI content marking requirements. The DEFIANCE Act (2024) and proposed NO FAKES Act both address synthetic media. While no US federal AI marking mandate exists as of March 2026, several states have enacted requirements for AI-generated political content, most referencing machine-readable marking standards.
                  </p>
                </div>
              </div>

              <div className="mt-6">
                <Link href="/content-provenance/eu-ai-act" className="text-sm underline hover:opacity-80" style={{ color: '#2a87c4' }}>
                  Full guide: C2PA and EU AI Act compliance &rarr;
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Implementation Quickstart */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-6">Implementing C2PA with Encypher</h2>
              <p className="text-muted-foreground mb-8 text-base leading-relaxed">
                Encypher provides the only commercial API that implements C2PA across all 31 supported MIME types, including the Section A.7 text provenance specification. Three lines of code sign a document.
              </p>

              <div className="bg-muted border border-border rounded-lg p-6 mb-6 font-mono text-sm overflow-x-auto">
                <div className="text-muted-foreground mb-1"># Sign text with C2PA manifest</div>
                <div>curl -X POST https://api.encypher.com/v1/sign \</div>
                <div className="pl-4">-H &quot;Authorization: Bearer YOUR_API_KEY&quot; \</div>
                <div className="pl-4">-H &quot;Content-Type: application/json&quot; \</div>
                <div className="pl-4">-d &apos;&#123;&quot;text&quot;: &quot;Your content here&quot;, &quot;metadata&quot;: &#123;&quot;author&quot;: &quot;Jane Smith&quot;&#125;&#125;&apos;</div>
              </div>

              <div className="flex gap-4">
                <Button asChild size="sm" className="font-semibold" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                  <a href="https://api.encypher.com/docs" target="_blank" rel="noopener noreferrer">
                    Full API Documentation <Code className="ml-2 h-4 w-4" />
                  </a>
                </Button>
                <Button asChild size="sm" variant="outline" className="font-semibold">
                  <Link href="/auth/signin?mode=signup&source=c2pa-quickstart">
                    Get API Key <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
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
                <Link href="/content-provenance" className="block bg-muted/30 p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">What Is Content Provenance?</h3>
                  <p className="text-sm text-muted-foreground">The definitive guide to content provenance: why it matters, how it works, and how it applies across 31 media types.</p>
                </Link>
                <Link href="/cryptographic-watermarking" className="block bg-muted/30 p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">Cryptographic Watermarking</h3>
                  <p className="text-sm text-muted-foreground">How deterministic proof of origin is embedded in content and why it is fundamentally different from statistical watermarking.</p>
                </Link>
                <Link href="/glossary#c2pa" className="block bg-muted/30 p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">C2PA Terminology</h3>
                  <p className="text-sm text-muted-foreground">Definitions for JUMBF, COSE, claim structure, ingredient chain, digital source type, and other C2PA terms.</p>
                </Link>
                <Link href="/content-provenance/eu-ai-act" className="block bg-muted/30 p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">C2PA and EU AI Act</h3>
                  <p className="text-sm text-muted-foreground">How C2PA satisfies Article 52 machine-readable marking requirements before the August 2, 2026 deadline.</p>
                </Link>
                <Link href="/c2pa-standard/conformance" className="block bg-muted/30 p-5 rounded-lg border border-border hover:border-primary/50 transition-colors group">
                  <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">Conformance Explorer</h3>
                  <p className="text-sm text-muted-foreground">Browse all products that have passed C2PA conformance testing. Search by company, product type, or media format.</p>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-16 w-full bg-muted/30 border-b border-border">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-8">Frequently Asked Questions About C2PA</h2>
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
              <div className="flex justify-center mb-4">
                <Users className="h-8 w-8" style={{ color: '#2a87c4' }} />
              </div>
              <h2 className="text-3xl font-bold tracking-tight mb-4">Implement C2PA Today</h2>
              <p className="text-muted-foreground mb-8">
                The only commercial API that covers all 31 C2PA MIME types, including Section A.7 text provenance. Free tier available.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button asChild size="lg" className="font-semibold" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                  <Link href="/auth/signin?mode=signup&source=c2pa-cta">
                    Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline" className="font-semibold">
                  <Link href="/contact">
                    Talk to an Expert <Globe className="ml-2 h-4 w-4" />
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
