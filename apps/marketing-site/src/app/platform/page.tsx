import { NextPage } from 'next';
import AISummary from '@/components/seo/AISummary';

const PlatformPage: NextPage = () => {
  return (
    <div className="container mx-auto py-12">
      <AISummary
        title="Platform"
        whatWeDo="Provide infrastructure-grade, C2PA-compliant content authenticity and provenance services."
        whoItsFor="Enterprises that need scalable, standards-compliant provenance and audit trails for user content."
        keyDifferentiator="Standards-authored, API-first architecture with deterministic, cryptographic audit trails."
        primaryValue="Trust by default and regulatory-grade transparency for all content."
      />
      <h1 className="text-4xl font-bold">Platform</h1>
      <p className="mt-4 text-lg">Information about the Encypher platform will be available here soon.</p>
    </div>
  );
};

export default PlatformPage;
