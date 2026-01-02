import { Metadata } from 'next';
import PublisherDemo from './components/PublisherDemo';
import AISummary from '@/components/seo/AISummary';

export const metadata: Metadata = {
  title: 'Publisher Demo | Encypher',
  description: 'Experience how Encypher shifts the burden of proof from publishers to AI companies with cryptographic certainty. An interactive demonstration for publishing strategists.',
  openGraph: {
    title: 'Publisher Demo - Encypher',
    description: 'See how cryptographic provenance changes the legal landscape for content licensing in the AI era.',
    images: ['/og-publisher-demo.png'],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Publisher Demo - Encypher',
    description: 'Interactive demo: How publishers regain control in the AI economy',
    images: ['/og-publisher-demo.png'],
  },
};

export default function PublisherDemoPage() {
  return (
    <>
      <AISummary
        title="Publisher Demo | Encypher"
        whatWeDo="Co-Chair of C2PA Text Provenance Task Force. Interactive demo of cryptographic watermarking that survives copy-paste and B2B distribution. API and SDKs available. Standard publishes January 8, 2026."
        whoItsFor="Publishing executives and legal teams seeking provable content ownership and licensing revenue."
        keyDifferentiator="Cryptographic proof enables content attribution and licensing. Sentence-level tracking proves exactly which content was used."
        primaryValue="Transform litigation costs into licensing revenue. Building standards with NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others through C2PA (c2pa.org)."
      />
      <PublisherDemo />
    </>
  );
}
