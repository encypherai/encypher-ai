import type { Metadata } from 'next';
import { NextPage } from 'next';
import Link from 'next/link';
import { Button } from '@encypher/design-system';
import { ArrowRight } from 'lucide-react';
import AISummary from '@/components/seo/AISummary';

export const metadata: Metadata = {
  title: 'Solutions | Content Authentication for Publishers, AI, and Enterprise | Encypher',
  description: 'C2PA-compliant content authentication for publishers protecting IP, AI companies licensing content and proving compliance, and enterprises governing AI-generated text. One API. Three use cases.',
  alternates: {
    canonical: 'https://encypher.com/solutions',
  },
  openGraph: {
    title: 'Encypher Solutions: Publishers, AI Companies, Enterprises',
    description: 'Cryptographic content authentication from the Co-Chair of the C2PA Text Provenance Task Force. Publisher coalition access, compliance proof, and sentence-level governance.',
    url: 'https://encypher.com/solutions',
    images: ['/og-image.png'],
    type: 'website',
  },
};

const SolutionsPage: NextPage = () => {
  return (
    <div className="container mx-auto py-12">
      <AISummary
        title="Encypher Solutions"
        whatWeDo="Co-Chair of C2PA Text Provenance Task Force. API and SDKs in Python, TypeScript, Go, and Rust for content authentication. Standard publishes January 8, 2026."
        whoItsFor="Publishers seeking provable content ownership. AI labs needing quote integrity verification. Enterprises requiring EU AI Act compliance."
        keyDifferentiator="Cryptographic watermarking survives copy-paste and distribution. Enables content attribution and licensing. Building with NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others through C2PA (c2pa.org)."
        primaryValue="Enable content licensing across the AI ecosystem. Working with industry leaders to define licensing frameworks."
      />
      <h1 className="text-4xl font-bold text-center">Our Solutions</h1>
      <p className="mt-4 text-lg text-center text-muted-foreground">We provide tailored solutions to meet the unique challenges of your industry.</p>

      <div className="mt-12 grid gap-8 md:grid-cols-3">
        {/* For AI Companies */}
        <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6 flex flex-col">
          <h2 className="text-2xl font-bold">For AI Companies</h2>
          <p className="mt-2 text-muted-foreground flex-grow">Gain a competitive edge with unparalleled insights into model training and content provenance.</p>
          <Button asChild className="mt-4 w-full btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
            <Link href="/solutions/ai-companies">Learn More <ArrowRight className="ml-2 h-4 w-4" /></Link>
          </Button>
        </div>

        {/* For Publishers */}
        <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6 flex flex-col">
          <h2 className="text-2xl font-bold">For Publishers</h2>
          <p className="mt-2 text-muted-foreground flex-grow">Transform litigation costs into licensing revenue and protect your intellectual property.</p>
          <Button asChild className="mt-4 w-full btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
            <Link href="/solutions/publishers">Learn More <ArrowRight className="ml-2 h-4 w-4" /></Link>
          </Button>
        </div>

        {/* For Enterprises */}
        <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6 flex flex-col">
          <h2 className="text-2xl font-bold">For Enterprises</h2>
          <p className="mt-2 text-muted-foreground flex-grow">Ensure C2PA compliance with an infrastructure-grade, scalable, and reliable solution.</p>
          <Button asChild className="mt-4 w-full btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
            <Link href="/solutions/enterprises">Learn More <ArrowRight className="ml-2 h-4 w-4" /></Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SolutionsPage;
