import { NextPage } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';
import AISummary from '@/components/seo/AISummary';

const SolutionsPage: NextPage = () => {
  return (
    <div className="container mx-auto py-12">
      <AISummary
        title="Encypher Solutions"
        whatWeDo="Provide sentence-level content authentication, licensing, and performance intelligence."
        whoItsFor="Publishers, AI labs, and enterprises needing provenance, licensing, and optimization."
        keyDifferentiator="Cryptographic proof with 100% accuracy authored by C2PA text standard leaders."
        primaryValue="Turn litigation into licensing and R&D into data-driven market advantage."
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
