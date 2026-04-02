import AISummary from '@/components/seo/AISummary';
import { Breadcrumbs } from '@/components/seo/Breadcrumbs';
import Script from 'next/script';
import Link from 'next/link';
import { getCompareMetadata, getTechArticleSchema, getBreadcrumbSchema, siteConfig } from '@/lib/seo';
import type { Metadata } from 'next';
import { ArrowRight, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypher.com';

export const metadata: Metadata = getCompareMetadata(
  'content-provenance-vs-content-detection',
  'Content Provenance vs Content Detection: Proof of Origin vs Identification After the Fact',
  "Content provenance is cryptographic proof of who created content, established at the moment of creation. Content detection is statistical inference applied after the fact. These answer different questions and have fundamentally different legal and technical properties."
);

const PAGE_URL = `${siteConfig.url}/compare/content-provenance-vs-content-detection`;
const DATE = '2026-03-31';

const techArticleSchema = getTechArticleSchema({
  headline: 'Content Provenance vs Content Detection: Proof of Origin vs Identification After the Fact',
  description: "The category-defining comparison. Content provenance establishes cryptographic proof at creation. Content detection applies statistical inference afterward. Different questions, different tools, different legal standing.",
  url: PAGE_URL,
  datePublished: DATE,
});

const breadcrumbSchema = getBreadcrumbSchema([
  { name: 'Home', url: siteConfig.url },
  { name: 'Compare', url: `${siteConfig.url}/compare` },
  { name: 'Provenance vs Detection', url: PAGE_URL },
]);

const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is content provenance?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Content provenance is a cryptographic record of a piece of content's origin and history, established at the moment of creation. A provenance record includes who created the content, when, with what tools, and what has happened to it since. The record is signed with the creator's private key, making it verifiable by anyone with the corresponding public key. Provenance answers the question: who created this, and can they prove it?"
      }
    },
    {
      "@type": "Question",
      "name": "What is content detection?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Content detection uses statistical analysis of text, image, or audio features to identify whether content was produced by an AI system. Detection tools are trained on datasets of human and AI-generated content and look for patterns associated with each. They produce a probability score: this content is X% likely to be AI-generated. Detection is applied after content has been created, examining the output rather than the creation process."
      }
    },
    {
      "@type": "Question",
      "name": "Can content provenance detect AI-generated content?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Provenance does not detect - it verifies. If an AI system embeds a C2PA manifest in its outputs identifying them as AI-generated (as required by the EU AI Act Article 52), provenance verification can confirm that claim. If content has no provenance record, that absence is informative but not deterministic - it could be AI-generated content, human content that was never signed, or content where the signature was stripped. Provenance proves origin when it is present; it cannot prove AI generation when it is absent."
      }
    },
    {
      "@type": "Question",
      "name": "Which approach is more accurate?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Provenance is 100% accurate for signed content: the signature either verifies or it does not. Detection is approximately 74-95% accurate depending on the tool and content type, with false positive rates of 5-26%. The accuracy comparison is somewhat misleading because they answer different questions - provenance accuracy for signed content is perfect, but provenance only works on content that was signed. Detection covers all content at lower accuracy."
      }
    },
    {
      "@type": "Question",
      "name": "Which approach has better legal standing?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Content provenance has significantly stronger legal standing. Cryptographic signatures are recognized under the E-SIGN Act (US) and eIDAS (EU) as authenticated documentation. A C2PA-signed document with a valid signature constitutes legal evidence of authorship and creation time. Detection scores are regularly disputed in legal contexts because of the false positive problem and the inherently probabilistic nature of the evidence. Courts have generally been reluctant to treat detection scores as conclusive evidence."
      }
    },
    {
      "@type": "Question",
      "name": "Does provenance replace detection for all use cases?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. For use cases where the question is 'was this submitted content AI-generated?' - content moderation, academic integrity, journalism verification - detection tools remain relevant because provenance may not be present. Provenance is the right tool when you need to prove ownership of content you created. Detection is the right tool when you need to screen content submitted by others. As provenance adoption grows, the need for detection in some use cases will decrease: signed human content and signed AI content can be distinguished definitively, without statistical inference."
      }
    }
  ]
};

function ComparisonRow({ feature, provenance, detection, provenancePositive = true, detectionPositive = false }: {
  feature: string;
  provenance: string;
  detection: string;
  provenancePositive?: boolean;
  detectionPositive?: boolean;
}) {
  return (
    <tr className="border-b border-border hover:bg-muted/20 transition-colors">
      <td className="py-3 px-4 font-medium text-sm">{feature}</td>
      <td className="py-3 px-4 text-sm">
        <span className="flex items-start gap-2">
          {provenancePositive
            ? <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
            : <AlertCircle className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
          }
          {provenance}
        </span>
      </td>
      <td className="py-3 px-4 text-sm text-muted-foreground">
        <span className="flex items-start gap-2">
          {detectionPositive
            ? <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
            : <AlertCircle className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
          }
          {detection}
        </span>
      </td>
    </tr>
  );
}

export default function ContentProvenanceVsDetectionPage() {
  return (
    <>
      <AISummary
        title="Content Provenance vs Content Detection: The Category-Defining Comparison"
        whatWeDo="This page defines and compares two distinct approaches to content authentication: provenance (cryptographic proof of origin at creation) and detection (statistical identification after the fact). They answer different questions and have different legal standing."
        whoItsFor="Publishers, legal teams, enterprises, developers, and anyone evaluating content authentication strategies."
        keyDifferentiator="Provenance is 100% accurate, deterministic, and established before any dispute. Detection is probabilistic, applied after the fact, and challenged regularly in legal contexts."
        primaryValue="Understanding this distinction is foundational to choosing the right content authentication approach. Provenance provides formal notice capability and willful infringement triggers. Detection provides screening capability."
        pagePath="/compare/content-provenance-vs-content-detection"
      />
      <Script id="tech-article-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(techArticleSchema) }} />
      <Script id="breadcrumb-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      <Script id="faq-schema" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Breadcrumbs items={[
          { name: 'Home', href: '/' },
          { name: 'Compare', href: '/compare' },
          { name: 'Provenance vs Detection', href: '/compare/content-provenance-vs-content-detection' },
        ]} />

        <div className="mb-4 text-sm text-muted-foreground bg-muted/30 border border-border rounded px-4 py-2 inline-block">
          Category-level comparison - not specific to any vendor
        </div>

        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Content Provenance vs Content Detection
        </h1>
        <p className="text-xl text-muted-foreground mb-10">
          Content provenance proves who created something, at the moment of creation, with cryptographic certainty. Content detection guesses whether something was made by an AI, after the fact, with statistical probability. These are not competing approaches to the same problem. They are solutions to different problems.
        </p>

        {/* Defining the Two Approaches */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Defining the Two Approaches</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-6">
            <div className="border rounded-lg p-6" style={{ borderColor: '#2a87c4' }}>
              <h3 className="font-semibold mb-3" style={{ color: '#2a87c4' }}>Content Provenance</h3>
              <p className="text-sm text-muted-foreground mb-3">
                A cryptographic record of content's origin and history, created at the time the content is published. The record is signed with the creator's private key and embedded in the content itself.
              </p>
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">The question it answers:</strong> Who created this content, when, and what are their claimed rights?
              </p>
            </div>
            <div className="border border-border rounded-lg p-6">
              <h3 className="font-semibold mb-3">Content Detection</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Statistical analysis of content features to identify whether the content was produced by an AI system or a human. Applied to existing content without prior knowledge of its creation process.
              </p>
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">The question it answers:</strong> Was this content likely produced by an AI?
              </p>
            </div>
          </div>
          <p className="mb-4">
            The questions are different. The answers come with different confidence levels. The legal and operational implications are different. Choosing between them requires clarity about which question you are trying to answer.
          </p>
        </section>

        {/* Prospective vs Retrospective */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Prospective vs Retrospective</h2>
          <p className="mb-4">
            One of the most consequential differences between provenance and detection is timing.
          </p>
          <p className="mb-4">
            Provenance is established prospectively - before any dispute arises, before the content is distributed, before any AI system touches it. A publisher who signs an article at publication has evidence that predates every potential claim against it. The signed timestamp is a fact established before the fact was needed.
          </p>
          <p className="mb-4">
            Detection is applied retrospectively - to content that already exists, after a concern has arisen. A publisher who discovers that an AI appears to have used their content, then runs detection tools against the AI's output, is generating analysis created after the disputed use. In a legal proceeding, after-the-fact analysis is inherently weaker than contemporaneous documentation.
          </p>
          <p className="mb-4">
            The practical consequence: provenance enables a publisher to say "I signed this on March 15, here is the cryptographic proof, it was before the alleged use." Detection enables a publisher to say "this output has characteristics consistent with AI generation, here is our analysis." The former is closer to a timestamped receipt. The latter is closer to a forensic opinion.
          </p>
        </section>

        {/* Accuracy and the False Positive Problem */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Accuracy and the False Positive Problem</h2>
          <p className="mb-4">
            For signed content, provenance is 100% accurate. A valid cryptographic signature either verifies against the claimed public key or it does not. There is no probability involved. There are no false positives in the traditional sense, because the result is a binary verification, not a classification.
          </p>
          <p className="mb-4">
            Detection tools report probabilities and carry false positive rates. Published research puts false positive rates - human content classified as AI-generated - between 5% and 26% depending on the tool, the content type, and the author's writing style.
          </p>
          <p className="mb-4">
            Who gets false-flagged disproportionately? Non-native English speakers, academic and technical writers, legal and regulatory writers, and anyone who writes in a consistent, formal style. These writers produce text with statistical profiles that overlap with AI-generated content. A journalist writing carefully researched, precisely worded articles may score higher on AI likelihood than someone writing casually and colloquially.
          </p>
          <p className="mb-4">
            The false positive rate also degrades over time as AI models improve. Better AI models generate text that more closely resembles careful human writing. Detection models trained on older AI output become less reliable as the distribution of AI writing shifts. Provenance does not have this problem: ECDSA signatures are as reliable in 2030 as they are today.
          </p>
        </section>

        {/* Durability Under Editing and Distribution */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Durability Under Editing and Distribution</h2>
          <p className="mb-4">
            Content is edited, syndicated, quoted, summarized, and transformed. Both provenance and detection approaches handle this differently.
          </p>
          <p className="mb-4">
            Provenance signatures are tied to the exact content through a cryptographic hash. If the content is modified, the hash changes, and verification fails - indicating that the content has been altered since signing. This is the tamper-evident property: modification is detectable, not invisible. A publisher can sign at publication and then detect whether their content was altered before it appeared in a downstream use.
          </p>
          <p className="mb-4">
            Detection signals degrade under editing. Paraphrasing, translation, and targeted substitution have all been demonstrated to reduce or eliminate detection accuracy. This is because the statistical signals that detection models learn are linguistic patterns in the token sequence, and those patterns change when the token sequence changes.
          </p>
          <p className="mb-4">
            The distribution consequence: a piece of signed content copied verbatim carries verifiable provenance. A piece of AI-generated content paraphrased once may evade detection. For enforcement against AI use of content - where the concern is often that content was used in some form, possibly modified - provenance provides a more durable foundation.
          </p>
        </section>

        {/* Legal Standing */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Legal Standing</h2>
          <p className="mb-4">
            The legal treatment of the two types of evidence is significantly different.
          </p>
          <p className="mb-4">
            Cryptographic signatures are recognized as authenticated documentation under the US E-SIGN Act (2000), the EU eIDAS regulation, and equivalent laws in most major jurisdictions. A document signed with a private key and verifiable against a known public key has legal weight comparable to a notarized document in many contexts. The C2PA standard is specifically designed to produce provenance records suitable for legal proceedings.
          </p>
          <p className="mb-4">
            When a publisher issues a formal copyright notice based on Encypher's embedded provenance, the notice documents that rights were embedded in the content in machine-readable form. A recipient who continues to use the content after receiving such a notice cannot plausibly claim innocent infringement. Under US copyright law, willful infringement carries statutory damages of up to $150,000 per work, compared to $30,000 for innocent infringement.
          </p>
          <p className="mb-4">
            Detection scores have been challenged in legal proceedings in academic and employment contexts. Several high-profile cases where students or employees were accused of AI use based on detection scores have shown that detection evidence is contested and often rejected as the sole basis for consequential decisions. Detection providers include disclaimers noting their output should not be the sole basis for such decisions.
          </p>
          <p className="mb-4">
            For copyright enforcement, the evidentiary strength of provenance vs detection is not marginal. It is the difference between a signed receipt and an expert opinion.
          </p>
        </section>

        {/* Comparison Table */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Comprehensive Comparison</h2>
          <div className="overflow-x-auto my-6">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  <th className="text-left py-3 px-4 font-semibold">Dimension</th>
                  <th className="text-left py-3 px-4 font-semibold" style={{ color: '#2a87c4' }}>Content Provenance</th>
                  <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Content Detection</th>
                </tr>
              </thead>
              <tbody>
                <ComparisonRow
                  feature="Question answered"
                  provenance="Who created this and can they prove it?"
                  detection="Was this likely made by an AI?"
                />
                <ComparisonRow
                  feature="Timing"
                  provenance="At creation (prospective)"
                  detection="After the fact (retrospective)"
                />
                <ComparisonRow
                  feature="Method"
                  provenance="Cryptographic signature"
                  detection="Statistical classification"
                />
                <ComparisonRow
                  feature="Result type"
                  provenance="Deterministic: verified or not"
                  detection="Probabilistic: likelihood score"
                />
                <ComparisonRow
                  feature="Accuracy (signed content)"
                  provenance="100%"
                  detection="74-95% (varies by tool)"
                />
                <ComparisonRow
                  feature="False positive rate"
                  provenance="None"
                  detection="5-26% depending on content type"
                />
                <ComparisonRow
                  feature="Degrades as AI improves"
                  provenance="No (math does not change)"
                  detection="Yes (detection trains on older AI output)"
                />
                <ComparisonRow
                  feature="Survives paraphrasing"
                  provenance="Detects modification (hash mismatch)"
                  detection="No (signal degrades)"
                />
                <ComparisonRow
                  feature="Publisher identity"
                  provenance="Embedded and verifiable"
                  detection="Not captured"
                />
                <ComparisonRow
                  feature="Licensing terms"
                  provenance="Machine-readable, embedded"
                  detection="Not applicable"
                />
                <ComparisonRow
                  feature="Legal standing"
                  provenance="Strong (E-SIGN, eIDAS, C2PA)"
                  detection="Disputed (frequently challenged)"
                />
                <ComparisonRow
                  feature="Willful infringement trigger"
                  provenance="Yes"
                  detection="No"
                />
                <ComparisonRow
                  feature="Works without prior knowledge"
                  provenance="No (content must be signed)"
                  detection="Yes (works on any content)"
                  provenancePositive={false}
                  detectionPositive={true}
                />
                <ComparisonRow
                  feature="Useful for screening submissions"
                  provenance="No"
                  detection="Yes"
                  provenancePositive={false}
                  detectionPositive={true}
                />
              </tbody>
            </table>
          </div>
        </section>

        {/* The Path Forward */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">The Path Forward: Provenance Adoption Reduces the Need for Detection</h2>
          <p className="mb-4">
            Detection exists partly because provenance does not yet cover all content. If every piece of human-authored content carried a verified C2PA provenance record, and every piece of AI-generated content carried a C2PA manifest identifying it as AI-generated, then the question "was this made by AI?" would have a definitive answer without statistical inference.
          </p>
          <p className="mb-4">
            The EU AI Act Article 52 requires AI companies to embed machine-readable markers in their outputs by August 2026. C2PA is the likely technical standard for that requirement. As AI outputs increasingly carry signed manifests identifying them as AI-generated, the problem space for detection tools narrows: detection becomes relevant primarily for content that lacks any provenance record.
          </p>
          <p className="mb-4">
            The transition is not immediate. A large proportion of existing content was created without provenance markers. Detection tools will remain relevant in the interim. But the long-term trajectory is toward provenance as the primary authentication mechanism, with detection playing a supporting role for legacy and unsigned content.
          </p>
        </section>

        {/* Use Case Fit */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Choosing the Right Tool</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border border-border rounded-lg p-6">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                Use detection when...
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>You need to screen content submitted to you for AI use</li>
                <li>Platform moderation at scale requires flagging potential AI content</li>
                <li>You are working with content that was not signed at creation</li>
                <li>A rough signal is sufficient for your use case (e.g., editorial review)</li>
              </ul>
            </div>
            <div className="border rounded-lg p-6" style={{ borderColor: '#2a87c4' }}>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                Use content provenance when...
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>You need to prove ownership of content you created</li>
                <li>Legal proceedings may require authenticated evidence</li>
                <li>You want machine-readable rights embedded at publication</li>
                <li>Deterministic accuracy is required (false positives are unacceptable)</li>
                <li>Licensing negotiations or formal enforcement are anticipated</li>
                <li>You are building an evidence chain for willful infringement claims</li>
              </ul>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions</h2>
          <div className="space-y-6">
            {faqSchema.mainEntity.map((item, i) => (
              <div key={i} className="border-b border-border pb-6 last:border-0">
                <h3 className="font-semibold mb-2">{item.name}</h3>
                <p className="text-muted-foreground text-sm">{item.acceptedAnswer.text}</p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <div className="bg-muted/30 border border-border rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold mb-3">Start with provenance, not probability</h2>
          <p className="text-muted-foreground mb-6">
            Sign your content at publication. Establish ownership proof before disputes arise, not after.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href={`${DASHBOARD_URL}/auth/signin?mode=signup`}
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-semibold text-white transition-opacity hover:opacity-90"
              style={{ backgroundColor: '#2a87c4' }}
            >
              Get Started Free <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/publisher-demo"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-semibold border border-border hover:bg-muted/30 transition-colors"
            >
              See the Demo
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
