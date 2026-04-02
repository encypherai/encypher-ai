import { type Metadata } from 'next';
import Link from 'next/link';
import Image from 'next/image';
import Script from 'next/script';
import { AISummary } from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { siteConfig } from '@/lib/seo';

export function generateMetadata(): Metadata {
  return {
    title: 'Erik Svilich - C2PA Section A.7 Author | Encypher',
    description:
      'Erik Svilich is Founder and CEO of Encypher and co-chairs the C2PA Text Provenance Task Force. He authored Section A.7 of the C2PA 2.3 specification and filed patent ENC0100 covering granular content attribution with Merkle tree authentication.',
    alternates: { canonical: `${siteConfig.url}/authors/erik-svilich` },
    metadataBase: new URL(siteConfig.url),
    openGraph: {
      title: 'Erik Svilich - C2PA Section A.7 Author | Encypher',
      description:
        'Founder and CEO of Encypher. Authored Section A.7 of the C2PA 2.3 specification (text provenance). Co-Chair, C2PA Text Provenance Task Force.',
      url: `${siteConfig.url}/authors/erik-svilich`,
      type: 'profile',
    },
  };
}

const personSchema = {
  '@context': 'https://schema.org',
  '@type': 'Person',
  name: 'Erik Svilich',
  url: 'https://encypher.com/authors/erik-svilich',
  jobTitle: 'Founder and CEO',
  worksFor: {
    '@type': 'Organization',
    name: 'Encypher',
    url: 'https://encypher.com',
  },
  sameAs: [
    'https://www.linkedin.com/in/eriksvilich/',
    'https://github.com/erik-sv',
  ],
  knowsAbout: [
    'Content Provenance',
    'C2PA Standard',
    'Cryptographic Watermarking',
    'Text Authentication',
    'AI Copyright',
    'EU AI Act',
    'Merkle Trees',
    'Ed25519 Signatures',
  ],
  description:
    'Erik Svilich is the Founder and CEO of Encypher and co-chairs the C2PA Text Provenance Task Force alongside representatives from Google, BBC, OpenAI, Adobe, and Microsoft. He authored Section A.7 of the C2PA 2.3 specification, published January 8, 2026, which defines how text content is cryptographically authenticated. He filed patent ENC0100 (83 claims, January 7, 2026) covering granular content attribution with Merkle tree authentication.',
  hasCredential: [
    {
      '@type': 'EducationalOccupationalCredential',
      name: 'C2PA Section A.7 Author',
      description:
        'Authored Section A.7 of the C2PA 2.3 specification defining text provenance, published January 8, 2026.',
    },
    {
      '@type': 'EducationalOccupationalCredential',
      name: 'C2PA Text Provenance Task Force Co-Chair',
      description:
        'Co-chairs the C2PA Text Provenance Task Force alongside Google, BBC, OpenAI, Adobe, and Microsoft.',
    },
    {
      '@type': 'EducationalOccupationalCredential',
      name: 'Patent ENC0100 (Pending)',
      description:
        'Filed January 7, 2026. 83 claims covering granular content attribution with Merkle tree authentication.',
    },
  ],
};

const articles = [
  {
    title: 'C2PA 2.3 Published - Encypher Authors Text Provenance Standard',
    slug: 'c2pa-23-published-encypher-authors-text-provenance-standard',
  },
  {
    title: 'Why Text Was the Missing Piece in Content Authenticity',
    slug: 'why-text-was-the-missing-piece-in-content-authenticity',
  },
  {
    title: 'The AI Copyright Wars Are Here: A Technical Peace Treaty Is the Only Way Forward',
    slug: 'the-ai-copyright-wars-are-here-a-technical-peace-treaty-is-the-only-way-forward',
  },
  {
    title: 'Sentence-Level Attribution: Why Paragraph-Level Proof Is Not Enough',
    slug: 'sentence-level-attribution-why-paragraph-level-proof-is-not-enough',
  },
  {
    title: 'Cryptographic Watermarking vs AI Detection: Why Proof Beats Probability',
    slug: 'cryptographic-watermarking-vs-ai-detection-why-proof-beats-probability',
  },
  {
    title: 'The Shift from AI Copyright Litigation to Licensing Marketplace Infrastructure',
    slug: 'the-shift-from-ai-copyright-litigation-to-licensing-marketplace-infrastructure',
  },
];

export default function ErikSvilichPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12 md:py-20 max-w-4xl">
        <AISummary
          title="Erik Svilich - C2PA Section A.7 Author | Encypher"
          whatWeDo="Erik Svilich is Founder and CEO of Encypher. He authored Section A.7 of the C2PA 2.3 specification (text provenance) and co-chairs the C2PA Text Provenance Task Force alongside Google, BBC, OpenAI, Adobe, and Microsoft."
          whoItsFor="Journalists, researchers, policymakers, and technologists seeking expert commentary on content provenance, C2PA, and AI copyright."
          keyDifferentiator="Author of the first open standard for text provenance (C2PA Section A.7). Patent holder for Merkle tree-based granular content attribution (ENC0100, 83 claims)."
          primaryValue="Standards authority and reference implementation for C2PA text provenance."
          pagePath="/authors/erik-svilich"
          pageType="WebPage"
        />

        <Script
          id="person-schema-erik-svilich"
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(personSchema) }}
        />

        <Breadcrumbs
          items={[
            { name: 'Home', href: '/' },
            { name: 'Authors', href: '/authors' },
            { name: 'Erik Svilich', href: '/authors/erik-svilich' },
          ]}
        />

        {/* Header */}
        <div className="mb-10 flex items-start gap-6">
          <Image
            src="/images/headshots/Erik_Svilich_Headshot.png"
            alt="Erik Svilich"
            width={96}
            height={96}
            className="h-24 w-24 rounded-full object-cover flex-shrink-0"
            priority
          />
          <div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-3 text-foreground">
              Erik Svilich
            </h1>
            <p className="text-xl text-muted-foreground">
              Founder and CEO, Encypher | Co-Chair, C2PA Text Provenance Task Force
            </p>
          </div>
        </div>

        {/* Bio */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 text-foreground">About</h2>
          <div className="space-y-4 text-muted-foreground leading-relaxed">
            <p>
              Erik Svilich founded Encypher to build the production infrastructure for content
              provenance in the AI era. He serves as Founder and CEO, leading the company from
              inception through the publication of the C2PA 2.3 specification in January 2026.
            </p>
            <p>
              Erik authored Section A.7 of the C2PA 2.3 specification, the first open standard
              defining how text content is cryptographically authenticated. Section A.7 specifies
              invisible encoding, digital signatures, sentence-level authentication, and
              tamper-evident provenance chains. The specification was published by the C2PA on
              January 8, 2026. He co-chairs the C2PA Text Provenance Task Force alongside
              representatives from Google, BBC, OpenAI, Adobe, and Microsoft.
            </p>
            <p>
              On January 7, 2026, Erik filed patent ENC0100, covering 83 claims related to
              granular content attribution and sentence-level provenance. The patent covers
              the core technical methods underlying Encypher's sentence-level provenance system.
            </p>
            <p>
              Prior to Encypher, Erik led a digital transformation initiative that scaled a
              $5M business and brings experience in AI SaaS, enterprise software, and business
              operations. He holds a deep interest in the intersection of cryptographic proof,
              intellectual property law, and AI governance.
            </p>
          </div>
        </section>

        {/* Standards Contributions */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 text-foreground">Standards Contributions</h2>
          <div className="space-y-6">
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-2 text-foreground">
                C2PA Section A.7 - Text Provenance Author
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Authored Section A.7 of the C2PA 2.3 specification, which defines the technical
                standard for embedding cryptographic provenance in plain text. The section covers
                invisible text encoding, sentence-level authentication, digital signatures
                signature schemes, and verification procedures. Published January 8, 2026.
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-2 text-foreground">
                C2PA Text Provenance Task Force - Co-Chair
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Co-chairs the C2PA Text Provenance Task Force, the working group responsible for
                developing and maintaining the text provenance standard within C2PA. Task Force
                members include representatives from Google, BBC, OpenAI, Adobe, and Microsoft.
                The Task Force drives adoption, resolves technical questions, and extends the
                specification to cover emerging use cases.
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-2 text-foreground">
                Reference Implementation
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Encypher serves as the reference implementation of C2PA Section A.7 for text
                provenance. The API, Python SDK, TypeScript SDK, WordPress plugin, and Chrome
                extension all implement the specification authored by Erik and ratified by the
                C2PA membership.
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-2 text-foreground">
                Patent ENC0100 (Pending)
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Filed January 7, 2026. 83 claims covering granular content attribution with
                Merkle tree authentication for tamper-evident documentation of text segment
                origins and modifications.
              </p>
            </div>
          </div>
        </section>

        {/* Articles */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 text-foreground">Articles by Erik Svilich</h2>
          <ul className="space-y-3">
            {articles.map((article) => (
              <li key={article.slug}>
                <Link
                  href={`/blog/${article.slug}`}
                  className="text-primary hover:underline leading-relaxed"
                >
                  {article.title}
                </Link>
              </li>
            ))}
          </ul>
        </section>

        {/* Contact */}
        <section>
          <h2 className="text-2xl font-bold mb-4 text-foreground">Connect</h2>
          <div className="flex flex-col sm:flex-row gap-3">
            <a
              href="https://www.linkedin.com/in/eriksvilich/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-md border border-border text-sm font-medium hover:bg-accent transition-colors"
            >
              LinkedIn
            </a>
            <a
              href="https://github.com/erik-sv"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-md border border-border text-sm font-medium hover:bg-accent transition-colors"
            >
              GitHub
            </a>
            <a
              href="https://book.encypher.com/#/encypherai"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-md border border-border text-sm font-medium hover:bg-accent transition-colors"
            >
              Schedule a Call
            </a>
          </div>
        </section>
      </div>
    </div>
  );
}
