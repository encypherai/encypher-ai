import { Button } from '@encypher/design-system';
import Image from 'next/image';
import Link from 'next/link';
import { Linkedin, Github, FileText, Video, Calendar, ExternalLink } from 'lucide-react';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'You Just Met Erik Svilich | C2PA Text Co-Chair & Encypher CEO',
  description: 'Erik Svilich co-chairs the C2PA Text Task Force and leads Encypher in building infrastructure for AI content licensing through sentence-level authentication.',
  robots: {
    index: false,
    follow: false,
  },
};

export default function ErikPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12 md:py-20 max-w-4xl">
        {/* Header Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-3">
            You Just Met Erik Svilich
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-8">
            C2PA Text Co-Chair & Encypher CEO
          </p>

          {/* Headshot */}
          <div className="flex justify-center mb-8">
            <div className="relative w-48 h-48 md:w-64 md:h-64">
              <Image
                src="/images/headshots/Erik_Svilich_Headshot.png"
                alt="Erik Svilich - Professional Headshot"
                fill
                className="rounded-full object-cover shadow-xl border-4 border-border"
                priority
              />
            </div>
          </div>

          {/* Value Proposition */}
          <div className="bg-card border border-border rounded-xl p-6 md:p-8 shadow-lg mb-8">
            <p className="text-lg md:text-xl leading-relaxed">
              We're building the infrastructure for<br />
              AI content licensing through sentence-level<br />
              authentication and cryptographic proof.
            </p>
          </div>

          {/* Primary CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Button asChild size="lg" className="bg-primary hover:bg-primary/90 text-white font-semibold">
              <Link href="/demo">
                <Video className="mr-2 h-5 w-5" />
                View Demo
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <a href="https://book.encypher.com/#/encypherai" target="_blank" rel="noopener noreferrer">
                <Calendar className="mr-2 h-5 w-5" />
                Schedule a Call
              </a>
            </Button>
            <Button asChild size="lg" variant="outline">
              <a href="https://www.linkedin.com/in/eriksvilich/" target="_blank" rel="noopener noreferrer">
                <Linkedin className="mr-2 h-5 w-5" />
                LinkedIn
              </a>
            </Button>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-border my-12"></div>

        {/* What We Do Section */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold mb-8 text-center">What We Do</h2>

          <div className="grid md:grid-cols-2 gap-6">
            {/* For Publishers */}
            <div className="bg-card border border-border rounded-lg p-6 shadow-md">
              <h3 className="text-xl font-semibold mb-3 text-primary">FOR PUBLISHERS</h3>
              <p className="text-muted-foreground leading-relaxed">
                Transform litigation costs into licensing revenue through sentence-level usage proof
                and court-admissible evidence.
              </p>
            </div>

            {/* For AI Companies */}
            <div className="bg-card border border-border rounded-lg p-6 shadow-md">
              <h3 className="text-xl font-semibold mb-3 text-primary">FOR AI COMPANIES</h3>
              <p className="text-muted-foreground leading-relaxed">
                Access the publisher ecosystem while gaining performance intelligence and reducing legal
                exposure.
              </p>
            </div>
          </div>
        </section>

        {/* Divider */}
        <div className="border-t border-border my-12"></div>

        {/* About Erik Section */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold mb-6 text-center">About Erik</h2>

          <div className="bg-muted/30 rounded-lg p-6 md:p-8 space-y-4">
            <p className="text-muted-foreground leading-relaxed">
              Erik Svilich co-chairs the C2PA Text Task Force, leading the development of global
              standards for AI content authentication.
            </p>

            <p className="text-muted-foreground leading-relaxed">
              As Founder & CEO of Encypher, Erik is building the production-ready implementation
              of the C2PA text standard with proprietary sentence-level tracking capabilities.
            </p>

            <p className="text-muted-foreground leading-relaxed">
              Prior to Encypher, Erik led a $5M company's digital transformation and brings extensive
              experience in AI SaaS, enterprise software, and successful business turnarounds.
            </p>
          </div>

          {/* Contact Links */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mt-6">
            <Button asChild variant="outline" size="lg">
              <a href="https://www.linkedin.com/in/eriksvilich/" target="_blank" rel="noopener noreferrer">
                <Linkedin className="mr-2 h-5 w-5" />
                LinkedIn
              </a>
            </Button>
            <Button asChild variant="outline" size="lg">
              <a href="https://github.com/erik-sv" target="_blank" rel="noopener noreferrer">
                <Github className="mr-2 h-5 w-5" />
                GitHub
              </a>
            </Button>
          </div>
        </section>

        {/* Divider */}
        <div className="border-t border-border my-12"></div>

        {/* How It Works Section */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold mb-6 text-center">How It Works</h2>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {/* For Publishers */}
            <div className="bg-card border border-border rounded-lg p-6 shadow-md">
              <h3 className="text-xl font-semibold mb-4 text-primary">FOR PUBLISHERS</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">
                    1
                  </div>
                  <p className="text-muted-foreground pt-1">
                    Implement C2PA text signing (30-day integration)
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">
                    2
                  </div>
                  <p className="text-muted-foreground pt-1">
                    Monitor usage across platforms automatically
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">
                    3
                  </div>
                  <p className="text-muted-foreground pt-1">
                    Generate evidence packages or licensing agreements
                  </p>
                </div>
              </div>
            </div>

            {/* For AI Companies */}
            <div className="bg-card border border-border rounded-lg p-6 shadow-md">
              <h3 className="text-xl font-semibold mb-4 text-primary">FOR AI COMPANIES</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">
                    1
                  </div>
                  <p className="text-muted-foreground pt-1">
                    Integrate C2PA authentication into training pipelines
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">
                    2
                  </div>
                  <p className="text-muted-foreground pt-1">
                    Access publisher content through licensing framework
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">
                    3
                  </div>
                  <p className="text-muted-foreground pt-1">
                    Gain performance intelligence on model behavior
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Documentation Links */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild variant="outline">
              <a href="https://docs.encypher.com" target="_blank" rel="noopener noreferrer">
                <FileText className="mr-2 h-4 w-4" />
                Technical Documentation
              </a>
            </Button>
            <Button asChild variant="outline">
              <a href="https://docs.encypher.com/integration" target="_blank" rel="noopener noreferrer">
                <ExternalLink className="mr-2 h-4 w-4" />
                Integration Guide
              </a>
            </Button>
          </div>
        </section>

        {/* Divider */}
        <div className="border-t border-border my-12"></div>

        {/* Final CTA Section */}
        <section className="text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Transform Your Approach?
          </h2>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="bg-primary hover:bg-primary/90 text-white font-semibold">
              <a href="https://book.encypher.com/#/encypherai" target="_blank" rel="noopener noreferrer">
                <Video className="mr-2 h-5 w-5" />
                Schedule Technical Demo
              </a>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/solutions">
                <FileText className="mr-2 h-5 w-5" />
                Explore Solutions
              </Link>
            </Button>
          </div>
        </section>
      </div>
    </div>
  );
}
