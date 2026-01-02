import { NextPage } from 'next';
import AISummary from '@/components/seo/AISummary';

const PlatformPage: NextPage = () => {
  return (
    <div className="container mx-auto py-12">
      <AISummary
        title="Encypher Platform"
        whatWeDo="Co-Chair of C2PA Text Provenance Task Force. Enterprise API and SDKs in Python, TypeScript, Go, and Rust for content authentication infrastructure. Standard publishes January 8, 2026."
        whoItsFor="Publishers needing provable content ownership. AI labs needing performance intelligence and quote integrity verification. Enterprises requiring EU AI Act and China watermarking compliance."
        keyDifferentiator="Cryptographic watermarking survives copy-paste, B2B distribution, and scraping. One API for entire publisher ecosystem."
        primaryValue="Building standards with NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others through C2PA (c2pa.org). Working with industry leaders to define content licensing frameworks."
      />
      <h1 className="text-4xl font-bold">Platform</h1>
      <p className="mt-4 text-lg">Information about the Encypher platform will be available here soon.</p>
    </div>
  );
};

export default PlatformPage;
