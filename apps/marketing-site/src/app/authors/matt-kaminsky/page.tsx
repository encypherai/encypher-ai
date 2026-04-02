import { type Metadata } from 'next';
import Link from 'next/link';
import Image from 'next/image';
import Script from 'next/script';
import { AISummary } from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { siteConfig } from '@/lib/seo';

export function generateMetadata(): Metadata {
  return {
    title: 'Matt Kaminsky - Chief Commercial Officer | Encypher',
    description:
      'Matt Kaminsky is Chief Commercial Officer at Encypher. He brings 13+ years in digital media and ad-tech revenue leadership, with prior roles at Mediavine, Enthusiast Gaming, Space Cow Media, and Digimarc.',
    alternates: { canonical: `${siteConfig.url}/authors/matt-kaminsky` },
    metadataBase: new URL(siteConfig.url),
    openGraph: {
      title: 'Matt Kaminsky - Chief Commercial Officer | Encypher',
      description:
        'CCO at Encypher. 13+ years in digital media and ad-tech revenue leadership. Expert in content licensing and publisher monetization.',
      url: `${siteConfig.url}/authors/matt-kaminsky`,
      type: 'profile',
    },
  };
}

const personSchema = {
  '@context': 'https://schema.org',
  '@type': 'Person',
  name: 'Matt Kaminsky',
  url: 'https://encypher.com/authors/matt-kaminsky',
  jobTitle: 'Chief Commercial Officer',
  worksFor: {
    '@type': 'Organization',
    name: 'Encypher',
    url: 'https://encypher.com',
  },
  description:
    'Matt Kaminsky is Chief Commercial Officer at Encypher. He brings 13+ years in digital media and ad-tech revenue leadership, with prior roles at Mediavine, Enthusiast Gaming, Space Cow Media, and Digimarc/Via Licensing in IP licensing frameworks.',
  knowsAbout: [
    'Content Licensing',
    'Publisher Monetization',
    'Ad Tech',
    'Digital Media',
    'IP Licensing',
    'Revenue Leadership',
    'AI Content Economy',
  ],
};

const articles = [
  {
    title: 'The Publishers Guide to AI Content Licensing in 2026',
    slug: 'the-publishers-guide-to-ai-content-licensing-in-2026',
  },
  {
    title: 'Content Licensing in 2026: What Publishers and AI Companies Should Expect',
    slug: 'content-licensing-in-2026-what-publishers-and-ai-companies-should-expect',
  },
  {
    title: 'The We Didnt Know Defense: How AI Companies Avoid Copyright Liability',
    slug: 'the-we-didnt-know-defense-how-ai-companies-avoid-copyright-liability',
  },
  {
    title: 'How Robots.txt Fails Publishers: The Case for In-Content Rights Signals',
    slug: 'how-robots-txt-fails-publishers-the-case-for-in-content-rights-signals',
  },
  {
    title: 'Quote Integrity Verification: Protecting Your Brand from AI Hallucinations',
    slug: 'quote-integrity-verification-protecting-your-brand-from-ai-hallucinations',
  },
];

export default function MattKaminskyPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12 md:py-20 max-w-4xl">
        <AISummary
          title="Matt Kaminsky - Chief Commercial Officer | Encypher"
          whatWeDo="Matt Kaminsky is Chief Commercial Officer at Encypher, leading commercial strategy for content provenance infrastructure. He brings 13+ years in digital media, ad-tech, and IP licensing."
          whoItsFor="Publishers, media executives, and commercial partners exploring content licensing and provenance infrastructure."
          keyDifferentiator="13+ years in digital media and ad-tech revenue leadership. Experience in IP licensing frameworks through Digimarc and Via Licensing."
          primaryValue="Translates content provenance infrastructure into commercial frameworks for publishers and AI companies."
          pagePath="/authors/matt-kaminsky"
          pageType="WebPage"
        />

        <Script
          id="person-schema-matt-kaminsky"
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(personSchema) }}
        />

        <Breadcrumbs
          items={[
            { name: 'Home', href: '/' },
            { name: 'Authors', href: '/authors' },
            { name: 'Matt Kaminsky', href: '/authors/matt-kaminsky' },
          ]}
        />

        {/* Header */}
        <div className="mb-10 flex items-start gap-6">
          <Image
            src="/images/headshots/Matt_Kaminsky_Headshot.png"
            alt="Matt Kaminsky"
            width={96}
            height={96}
            className="h-24 w-24 rounded-full object-cover flex-shrink-0"
            priority
          />
          <div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-3 text-foreground">
              Matt Kaminsky
            </h1>
            <p className="text-xl text-muted-foreground">
              Chief Commercial Officer, Encypher
            </p>
          </div>
        </div>

        {/* Bio */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 text-foreground">About</h2>
          <div className="space-y-4 text-muted-foreground leading-relaxed">
            <p>
              Matt Kaminsky serves as Chief Commercial Officer at Encypher, where he leads
              commercial strategy, partnerships, and revenue operations. He joined Encypher
              to build the commercial side of content provenance infrastructure as the market
              for AI content licensing matures.
            </p>
            <p>
              Matt brings 13+ years of digital media and ad-tech revenue leadership. He held
              senior roles at Mediavine, one of the largest ad management platforms for
              independent publishers, Enthusiast Gaming, and Space Cow Media. His time at
              Digimarc and Via Licensing gave him direct experience in IP licensing frameworks,
              the structures through which content rights are packaged, priced, and transacted
              at scale.
            </p>
            <p>
              At Encypher, Matt translates the technical capabilities of C2PA text provenance
              and multi-media signing into commercial frameworks. He works directly with
              publishers on licensing agreements and AI companies on compatible infrastructure
              arrangements, drawing on his ad-tech background to position provenance as the
              foundational layer for the AI content economy.
            </p>
          </div>
        </section>

        {/* Background */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 text-foreground">Background</h2>
          <div className="space-y-4">
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-1 text-foreground">Encypher</h3>
              <p className="text-xs text-muted-foreground mb-2 uppercase tracking-wide">
                Chief Commercial Officer
              </p>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Commercial strategy and revenue operations for content provenance infrastructure.
                Publisher and AI company partnerships. Licensing framework development.
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-1 text-foreground">Mediavine</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Revenue leadership at one of the largest independent publisher ad management
                platforms, working directly with thousands of publishers on monetization strategy.
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-1 text-foreground">
                Digimarc / Via Licensing
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                IP licensing frameworks and digital rights management. Experience structuring
                licensing arrangements for content rights at scale.
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-1 text-foreground">
                Enthusiast Gaming / Space Cow Media
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Digital media revenue leadership across gaming and entertainment publisher
                networks.
              </p>
            </div>
          </div>
        </section>

        {/* Articles */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 text-foreground">Articles by Matt Kaminsky</h2>
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
              href="mailto:sales@encypher.com"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-md border border-border text-sm font-medium hover:bg-accent transition-colors"
            >
              Contact Sales
            </a>
          </div>
        </section>
      </div>
    </div>
  );
}
