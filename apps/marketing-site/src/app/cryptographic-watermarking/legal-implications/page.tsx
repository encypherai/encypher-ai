import type { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import { Button } from '@/components/ui/button';
import { generateMetadata as seoMetadata, getTechArticleSchema, siteConfig } from '@/lib/seo';

export const metadata: Metadata = seoMetadata(
  'Legal Implications of Cryptographic Watermarking | Willful Infringement | Encypher',
  'How cryptographic watermarking shifts copyright disputes from innocent to willful infringement. Statutory damages, formal notice mechanism, and the evidentiary weight of cryptographic proof.',
  '/cryptographic-watermarking/legal-implications'
);

export default function LegalImplicationsPage() {
  const techArticle = getTechArticleSchema({
    title: 'Legal Implications of Cryptographic Watermarking',
    description: 'Willful infringement, formal notice, statutory damages, and the evidentiary weight of cryptographic proof in AI copyright disputes.',
    url: `${siteConfig.url}/cryptographic-watermarking/legal-implications`,
    author: 'Erik Svilich',
    datePublished: '2026-03-31',
  });

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'What is the legal difference between innocent and willful copyright infringement?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Under 17 U.S.C. 504, a copyright owner can elect to recover statutory damages instead of actual damages and profits. For innocent infringement - where the infringer did not know and had no reason to believe that their acts constituted infringement - statutory damages are reduced to a minimum of $200 per work. For ordinary infringement, statutory damages range from $750 to $30,000 per work. For willful infringement - where the infringer knew or had reason to know their acts were infringing - statutory damages increase to up to $150,000 per work. Embedded provenance with rights terms creates the formal notice that makes ignorance difficult to claim.',
        },
      },
      {
        '@type': 'Question',
        name: 'How does embedded provenance create formal notice?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Formal notice in copyright law can be constructive (publicly available information that a party should have known) as well as actual (direct communication). When content carries embedded machine-readable rights terms, any party that ingests the content receives notice of the rights terms with the content. Courts have increasingly recognized that machine-readable rights terms constitute constructive notice. This is why EU AI Act Article 4(3) specifically recognizes machine-readable rights reservations as legally operative.',
        },
      },
      {
        '@type': 'Question',
        name: 'Can cryptographic proof be challenged in court?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Cryptographic proof can be challenged in court, but the challenges are narrow. Opposing counsel can argue that the private key was compromised, that the certificate chain is untrusted, or that the timestamp is inaccurate. They cannot argue that the signature itself is wrong if the verification algorithm is correct - that would require breaking SHA-256 or the signing algorithm, which is computationally infeasible. The practical effect is that cryptographic proof shifts the burden to the opposing party to demonstrate a specific technical failure, rather than merely arguing that the evidence is probabilistic.',
        },
      },
    ],
  };

  return (
    <>
      <AISummary
        title="Legal Implications of Cryptographic Watermarking"
        whatWeDo="Encypher's cryptographic watermarking creates formal notice of copyright ownership and rights terms embedded in every copy of signed content. This formal notice is the mechanism that shifts AI copyright disputes from innocent infringement claims to willful infringement claims."
        whoItsFor="Publishers, legal counsel, and enterprises evaluating the legal significance of content provenance infrastructure. Anyone building an AI copyright enforcement strategy."
        keyDifferentiator="Embedded rights terms create formal notice without any action by the rights holder after publication. Every copy of signed content carries the notice automatically. This shifts the legal default from 'publisher must prove notice' to 'infringer must prove they lacked notice.'"
        primaryValue="Understanding how willful infringement differs from innocent infringement, the statutory damage implications, and the evidentiary weight of cryptographic proof."
        pagePath="/cryptographic-watermarking/legal-implications"
        pageType="WebPage"
      />

      <Script
        id="tech-article-legal-implications"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticle) }}
      />
      <Script
        id="faq-legal-implications"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Cryptographic Watermarking', href: '/cryptographic-watermarking' },
          { name: 'Legal Implications', href: '/cryptographic-watermarking/legal-implications' },
        ]} />

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Legal Implications of Cryptographic Watermarking
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          Embedded provenance changes the legal posture of copyright disputes. The mechanism
          is formal notice: every copy of signed content carries the rights terms, and any
          party that receives the content has received that notice.
        </p>

        <div className="p-4 bg-muted/30 rounded-lg border border-border mb-12 text-sm text-muted-foreground">
          <strong>Disclaimer:</strong> This page describes legal concepts relevant to content provenance.
          It is not legal advice. Consult qualified copyright counsel for advice specific to your situation.
        </div>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Innocent vs. Willful Infringement</h2>
          <p className="text-muted-foreground mb-4">
            US copyright law distinguishes between innocent infringement and willful infringement.
            The distinction matters enormously for statutory damages.
          </p>
          <p className="text-muted-foreground mb-4">
            Under 17 U.S.C. 504, copyright owners who have registered their works can elect
            statutory damages in lieu of actual damages. The ranges are:
          </p>
          <ul className="space-y-3 mb-4">
            <li className="flex gap-3 items-start p-3 bg-muted/30 rounded-lg">
              <div className="text-sm font-mono bg-muted px-2 py-1 rounded h-fit">Innocent</div>
              <div>
                <p className="text-sm font-semibold">$200 minimum per work</p>
                <p className="text-muted-foreground text-sm">Infringer did not know and had no reason to believe their acts constituted infringement</p>
              </div>
            </li>
            <li className="flex gap-3 items-start p-3 bg-muted/30 rounded-lg">
              <div className="text-sm font-mono bg-muted px-2 py-1 rounded h-fit">Standard</div>
              <div>
                <p className="text-sm font-semibold">$750 to $30,000 per work</p>
                <p className="text-muted-foreground text-sm">Ordinary infringement, court determines amount</p>
              </div>
            </li>
            <li className="flex gap-3 items-start p-3 bg-muted/30 rounded-lg">
              <div className="text-sm font-mono bg-muted px-2 py-1 rounded h-fit">Willful</div>
              <div>
                <p className="text-sm font-semibold">Up to $150,000 per work</p>
                <p className="text-muted-foreground text-sm">Infringer knew or had reason to know their acts were infringing</p>
              </div>
            </li>
          </ul>
          <p className="text-muted-foreground">
            For a publisher with 10,000 articles in an AI training corpus, the difference
            between innocent and willful infringement is the difference between $2 million
            (innocent minimum) and $1.5 billion (willful maximum). Even at more moderate
            assessments, the difference is material.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">How Embedded Provenance Creates Formal Notice</h2>
          <p className="text-muted-foreground mb-4">
            For infringement to be "innocent," the infringer must demonstrate that they had
            no reason to know the content was protected. When content carries embedded rights
            terms, that defense becomes difficult to sustain.
          </p>
          <p className="text-muted-foreground mb-4">
            A C2PA manifest embedded in a text article includes, among other things, a rights
            assertion: a machine-readable statement of what licensing tier applies (Bronze for
            indexing, Silver for RAG, Gold for training). When an AI company's scraper ingests
            that article, the manifest is present in the scraped text.
          </p>
          <p className="text-muted-foreground mb-4">
            The argument "we did not know the content was owned" fails when the content
            contained explicit ownership metadata. The manifest is not a metadata field
            that requires technical knowledge to interpret - it is structured data in a
            published open standard (C2PA) that any engineer can read with open-source tools.
          </p>
          <p className="text-muted-foreground">
            Courts examining AI copyright disputes will need to address the notice question.
            Content that carries embedded, machine-readable rights terms presents a materially
            different notice argument than content that merely carries a byline and copyright
            notice in HTML headers.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">EU AI Act and Machine-Readable Rights Reservations</h2>
          <p className="text-muted-foreground mb-4">
            The EU AI Act Article 4(3) specifically addresses machine-readable rights reservations.
            It requires providers of general-purpose AI models to implement policies that
            respect rights reservations made by content owners using machine-readable formats
            defined in the DSA (Digital Services Act) and its implementing regulations.
          </p>
          <p className="text-muted-foreground mb-4">
            C2PA rights assertions are a machine-readable format. An AI company that ingests
            content with C2PA rights assertions and does not honor the licensing tier restrictions
            is potentially in violation of EU AI Act Article 4(3), in addition to any copyright
            claims.
          </p>
          <p className="text-muted-foreground">
            The EU AI Act compliance angle provides a separate enforcement pathway from
            copyright law, and one with different remedies. Both pathways benefit from
            embedded provenance that documents what rights terms were present in the content
            at the time of ingestion.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Evidentiary Weight of Cryptographic Proof</h2>
          <p className="text-muted-foreground mb-4">
            Evidence in copyright litigation typically involves documentation that can be
            challenged on authenticity grounds. A spreadsheet of publication dates can be
            questioned. A screenshot can be questioned. A log file can be questioned.
            These are not inherently fraudulent, but they depend on trusting the party
            that produced them.
          </p>
          <p className="text-muted-foreground mb-4">
            A valid cryptographic signature is different in kind. Challenging a COSE signature
            requires demonstrating that the private key was compromised, the certificate chain
            is fraudulent, or the signature algorithm was broken. These are narrow and
            technically specific challenges that require expert evidence, not general skepticism
            about the producing party's motives.
          </p>
          <p className="text-muted-foreground mb-4">
            Digital signatures have been accepted as evidence in courts globally. Electronic
            signature laws (ESIGN in the US, eIDAS in the EU) establish legal frameworks
            for digital signature admissibility. C2PA manifests are signed with standard
            cryptographic tools that satisfy these frameworks.
          </p>
          <p className="text-muted-foreground">
            In practice, this means that a publisher presenting a C2PA evidence package has
            documentation that opposing counsel cannot dismiss as mere assertion. The verification
            is public, the algorithm is published, and anyone can reproduce the verification
            independently.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Formal Notice Package</h2>
          <p className="text-muted-foreground mb-4">
            When a publisher discovers their signed content in an AI company's outputs, Encypher
            generates a formal notice package that documents:
          </p>
          <ul className="list-disc list-inside text-muted-foreground mb-4 space-y-2 ml-4">
            <li>The original signed content with verified manifest (dated proof of ownership)</li>
            <li>The content found in the AI output (the allegedly infringing reproduction)</li>
            <li>The verification result (confirming the signed content is the source)</li>
            <li>The rights assertion in the manifest (documenting what licensing terms applied)</li>
            <li>The sentence-level attribution (specific sentences verified as matching)</li>
          </ul>
          <p className="text-muted-foreground mb-4">
            This package is independently verifiable. The AI company's legal team can verify
            every claim in the package using open-source tools, without trusting Encypher.
            The verification is based on the C2PA open standard, not on proprietary assertions.
          </p>
          <p className="text-muted-foreground">
            Publishers who use Encypher's notice feature report that many AI companies respond
            to notices by opening licensing discussions rather than litigating. The independently
            verifiable evidence package changes the economics of the dispute: litigation against
            cryptographic proof is expensive, while licensing is straightforward.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Registered vs. Unregistered Works</h2>
          <p className="text-muted-foreground mb-4">
            Statutory damages and attorney's fees under US copyright law are available only
            for registered works. Content provenance does not replace copyright registration -
            it is a different tool that strengthens the evidentiary record.
          </p>
          <p className="text-muted-foreground mb-4">
            Publishers who want access to the full range of copyright remedies, including
            statutory damages, should register their works with the US Copyright Office.
            Provenance then provides the documentation that supports the willful infringement
            argument once the registration is in place.
          </p>
          <p className="text-muted-foreground">
            For unregistered works, provenance still has value: it supports actual damages
            claims, licensing negotiations, and the willful infringement argument under the
            enhanced actual damages doctrine. It also applies in EU jurisdictions where
            copyright protection does not require registration.
          </p>
        </section>

        <section className="mb-12 p-6 bg-muted/30 rounded-lg border border-border">
          <h2 className="text-xl font-bold mb-3">Related Resources</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li><Link href="/content-provenance/for-publishers" className="underline hover:no-underline">Content Provenance for Publishers</Link></li>
            <li><Link href="/content-provenance/vs-content-detection" className="underline hover:no-underline">Provenance vs. Detection: The Legal Difference</Link></li>
            <li><Link href="/content-provenance/eu-ai-act" className="underline hover:no-underline">EU AI Act Compliance</Link></li>
            <li><Link href="/cryptographic-watermarking/how-it-works" className="underline hover:no-underline">How Cryptographic Watermarking Works</Link></li>
            <li><Link href="/cryptographic-watermarking/survives-distribution" className="underline hover:no-underline">How Provenance Survives Distribution</Link></li>
          </ul>
        </section>

        <section className="text-center py-8">
          <h2 className="text-2xl font-bold mb-4">Build Your Copyright Documentation Infrastructure</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Provenance that creates formal notice and supports willful infringement arguments.
            Free tier for up to 1,000 documents per month.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
              <Link href="/try">Start Free</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/contact">Talk to Sales</Link>
            </Button>
          </div>
        </section>
      </div>
    </>
  );
}
