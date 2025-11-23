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
        whatWeDo="Interactive walk-through of sentence-level content authentication and licensing for publishers."
        whoItsFor="Publishing executives and legal teams evaluating AI-era licensing and enforcement."
        keyDifferentiator="Court-admissible, cryptographic proof at sentence-level, authored by C2PA text standard leaders."
        primaryValue="Shift from litigation costs to predictable licensing revenue with mathematical certainty."
      />
      <PublisherDemo />
    </>
  );
}
