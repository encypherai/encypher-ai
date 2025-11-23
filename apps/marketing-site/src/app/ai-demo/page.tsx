import { Metadata } from 'next';
import AIDemo from './components/AIDemo';
import AISummary from '@/components/seo/AISummary';

export const metadata: Metadata = {
  title: 'AI Performance Analytics | Encypher AI Demo',
  description: 'Stop flying blind. Track which model parameters drive viral performance. Google Analytics for AI with regulatory compliance built in.',
  keywords: 'AI analytics, model performance, C2PA, AI compliance, EU AI Act, model optimization, R&D intelligence',
  openGraph: {
    title: 'Google Analytics for AI - Encypher',
    description: 'Track real-world performance of AI models. Optimize R&D with sentence-level analytics.',
    images: ['/og-ai-demo.png'],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Google Analytics for AI - Encypher',
    description: 'Turn $2.7B R&D into measurable insights. Real-world AI model performance analytics.',
    images: ['/og-ai-demo.png'],
  },
};

export default function AIDemoPage() {
  return (
    <>
      <AISummary
        title="AI Lab Demo | Encypher"
        whatWeDo="Interactive demonstration of sentence-level performance intelligence and compliance for AI labs."
        whoItsFor="AI product and research teams needing real-world performance analytics and regulatory compliance."
        keyDifferentiator="Cryptographic provenance with 100% accuracy vs statistical detection—trace outputs back to parameters."
        primaryValue="Optimize models with data-driven insights while ensuring ecosystem compliance."
      />
      <AIDemo />
    </>
  );
}
