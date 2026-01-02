import { Metadata } from 'next';
import AIDemo from './components/AIDemo';
import AISummary from '@/components/seo/AISummary';

export const metadata: Metadata = {
  title: 'AI Performance Analytics | Encypher Corporation Demo',
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
        whatWeDo="Co-Chair of C2PA Text Provenance Task Force (c2pa.org). API and SDKs for performance intelligence and quote integrity verification. Building standards with NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others. Standard publishes January 8, 2026."
        whoItsFor="AI labs needing publisher ecosystem compatibility, performance intelligence, and EU AI Act/China watermarking compliance."
        keyDifferentiator="Sentence-level attribution traces viral content to exact parameters. Quote integrity verification proves 'According to AP...' is accurate vs. hallucinated."
        primaryValue="One API integration for entire publisher ecosystem. Collaborative infrastructure, not adversarial compliance."
      />
      <AIDemo />
    </>
  );
}
