import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Github, Linkedin, Code, Mail, MessageSquare } from 'lucide-react';
import { siteConfig } from "@/config/site";
import { getSiteUrl } from "@/lib/env";
import Image from 'next/image';
import { Metadata } from 'next';
import Script from 'next/script';
import { faqSchema, getAISearchSummary } from '@/lib/seo';
import AISummary from '@/components/seo/AISummary';

export const metadata: Metadata = {
  title: 'Company | Encypher',
  description: 'Meet the Encypher team and advisors. Leaders in AI content provenance, trust, and enterprise adoption. Learn about our mission and the visionaries behind the open standard for AI content authenticity.',
  alternates: { canonical: 'https://encypherai.com/company' },
  metadataBase: new URL('https://encypherai.com'),
};

export default function CompanyPage() {
  return (
    <div className="container py-12 md:py-20">
      <AISummary
        title="About Encypher"
        whatWeDo="Co-Chair of C2PA Text Provenance Task Force (c2pa.org) with NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others. API and SDKs in Python, TypeScript, Go, and Rust. Standard publishes January 8, 2026."
        whoItsFor="Publishers seeking content licensing and provable ownership. AI labs needing quote integrity verification and performance intelligence. Enterprises requiring EU AI Act compliance."
        keyDifferentiator="Cryptographic watermarking survives copy-paste, B2B distribution, and scraping. Enables content attribution and licensing."
        primaryValue="Building collaborative infrastructure for the AI content economy. Working with industry leaders to define content licensing frameworks."
      />
      <Script id="schema-faq" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />
      <Script
        id="schema-ai-summary"
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            getAISearchSummary({
              whatWeDo: 'Sentence-level content authentication and licensing infrastructure authored by the C2PA text standard creators.',
              whoItsFor: 'Publishers seeking licensing revenue and AI labs optimizing performance and compliance.',
              keyDifferentiator: 'Cryptographic proof with 100% accuracy at sentence-level vs probabilistic detection.',
              primaryValue: 'Transforms litigation into licensing with court-admissible evidence and ecosystem integration.'
            })
          ),
        }}
      />
      <div className="max-w-3xl mx-auto">
        <div className="space-y-4 mb-12">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight">About Encypher</h1>
          <p className="text-xl text-muted-foreground">
            Building Trust Infrastructure for the AI Economy
          </p>

          {/* Mission Statement */}
          <div className="bg-primary/5 border border-primary/20 rounded-lg p-6 mt-8">
            <p className="text-lg font-medium text-center">
              We believe AI and creators can thrive together. Our mission is to build the infrastructure that makes this possible—open standards that enable attribution, licensing, and trust at scale.
            </p>
          </div>

          <div className="text-center pt-8">
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-8">
              Co-Authors of the C2PA Text Standard
            </h3>
            <div className="flex justify-center items-center gap-12 md:gap-16 flex-wrap">
              <div className="relative h-12 w-48">
                <Image
                  src="/c2pa-hero.svg"
                  alt="C2PA Logo"
                  fill
                  style={{objectFit: "contain"}}
                />
              </div>
              <div className="relative h-12 w-48">
                <Image
                  src="/CAI_Lockup_RGB_Black.svg"
                  alt="Content Authenticity Initiative Logo"
                  fill
                  style={{objectFit: "contain"}}
                />
              </div>
            </div>
          </div>
        </div>
        <div className="space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-4">Our Story</h2>
            <p className="text-muted-foreground mb-4">
              When the industry needed a standard for AI content authenticity, we wrote it. As co-authors of the C2PA text specification, we work alongside Adobe, Microsoft, Google, OpenAI, and the BBC to define how digital content is authenticated.
            </p>
            <p className="text-muted-foreground mb-4">
              But standards alone don't solve problems—infrastructure does. Publishers need provable ownership. AI labs need performance intelligence and compliance infrastructure. The ecosystem needs interoperability.
            </p>
            <p className="text-muted-foreground mb-4">
              So we built it. Sentence-level tracking with cryptographic certainty. Open-source foundations with commercial capabilities. Infrastructure that serves both creators and AI companies—because the future isn't adversarial, it's collaborative.
            </p>
            <ul className="space-y-2 mb-4">
              <li className="text-muted-foreground"><strong>For Publishers:</strong> Transform unmarked content into provably owned assets with licensing capability.</li>
              <li className="text-muted-foreground"><strong>For AI Labs:</strong> Performance intelligence on your models + regulatory compliance infrastructure.</li>
              <li className="text-muted-foreground"><strong>For Developers:</strong> Open-source SDK implementing the standard we co-authored.</li>
            </ul>
            <p className="text-muted-foreground">
              The coalition is growing. The infrastructure is ready. We're building the trust layer for the AI economy.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Core Team & Advisors</h2>
            <div className="flex flex-col items-center">
              {/* Row 1: CEO (Centered on md+) */}
              {/* Container takes 1/2 width on md+ and centers the card within it */}
              <div className="w-full md:w-1/2 mb-6 flex justify-center">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex flex-col items-center text-center">
                      <Image src="/images/headshots/Erik_Svilich_Headshot.png" alt="Erik Svilich headshot" width={96} height={96} className="h-24 w-24 rounded-full object-cover mb-4" priority />
                      <h3 className="text-xl font-semibold">Erik Svilich</h3>
                      <p className="text-sm text-muted-foreground mb-2">Founder & CEO</p>
                      <p className="text-sm text-muted-foreground mb-4">
                        Co-author of the C2PA text standard and co-chair of the C2PA Text Task Force. Working with Adobe, Microsoft, Google, and OpenAI to define content authenticity standards. Background in AI SaaS and enterprise software.
                      </p>
                      <div className="flex gap-2">
                        <a 
                          href="https://github.com/erik-sv" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-muted-foreground hover:text-foreground"
                        >
                          <Github className="h-5 w-5" />
                          <span className="sr-only">GitHub</span>
                        </a>
                        <a 
                          href="https://www.linkedin.com/in/eriksvilich/" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-muted-foreground hover:text-foreground"
                        >
                          <Linkedin className="h-5 w-5" />
                          <span className="sr-only">Erik Svilich LinkedIn Profile</span>
                        </a>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              {/* Row 2: CRO & Advisors (2-col grid on md+) */}
              <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex flex-col items-center text-center">
                      <Image src="/images/headshots/Nate_Alvord_Headshot.png" alt="Nate Alvord headshot" width={96} height={96} className="h-24 w-24 rounded-full object-cover mb-4" />
                      <h3 className="text-xl font-semibold">Nate Alvord</h3>
                      <p className="text-sm text-muted-foreground mb-2">Chief Revenue Officer</p>
                      <p className="text-sm text-muted-foreground mb-4">
                        25+ years in enterprise sales and IP monetization. Former sales leader at Digimarc, Intellectual Ventures, and Dolby. Drives commercial strategy and enterprise partnerships.
                      </p>
                      <div className="flex gap-2">
                        <a 
                          href="https://www.linkedin.com/in/nate-alvord/" 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          aria-label="Nate Alvord LinkedIn Profile"
                          className="text-muted-foreground hover:text-foreground"
                        >
                          <Linkedin className="h-5 w-5" />
                          <span className="sr-only">Nate Alvord LinkedIn Profile</span>
                        </a>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-6">
                    <div className="flex flex-col items-center text-center">
                      <Image src="/images/headshots/Hiep_Dang_Headshot.png" alt="Hiep Dang headshot" width={96} height={96} className="h-24 w-24 rounded-full object-cover mb-4" />
                      <h3 className="text-xl font-semibold">Hiep Dang</h3>
                      <p className="text-sm text-muted-foreground mb-2">Strategic Advisor</p>
                      <p className="text-sm text-muted-foreground mb-4">
                        20+ years in AI/ML and security GTM strategy. Developed GTM at Cylance (acquired by BlackBerry for $1.4B). Advises on product strategy and enterprise partnerships.
                      </p>
                      <div className="flex gap-2">
                        <a 
                          href="https://www.linkedin.com/in/hiepdang/" 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          aria-label="Hiep Dang LinkedIn Profile"
                          className="text-muted-foreground hover:text-foreground"
                        >
                          <Linkedin className="h-5 w-5" />
                          <span className="sr-only">Hiep Dang LinkedIn Profile</span>
                        </a>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                {/* New Advisor: Allen Guthier */}
                <Card>
                  <CardContent className="p-6">
                    <div className="flex flex-col items-center text-center">
                      <Image src="/images/headshots/Allen_Guthier_Headshot.png" alt="Allen Guthier headshot" width={96} height={96} className="h-24 w-24 rounded-full object-cover mb-4" />
                      <h3 className="text-xl font-semibold">Allen Guthier</h3>
                      <p className="text-sm text-muted-foreground mb-2">Strategic Advisor</p>
                      <p className="text-sm text-muted-foreground mb-4">
                        Venture Partner at Oregon Venture Fund. Key role at CloudHealth through $535M acquisition by VMware. Advises on scaling, fundraising, and product-market fit.
                      </p>
                      <div className="flex gap-2">
                        <a 
                          href="https://www.linkedin.com/in/allenguthier/" 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          aria-label="Allen Guthier LinkedIn Profile"
                          className="text-muted-foreground hover:text-foreground"
                        >
                          <Linkedin className="h-5 w-5" />
                          <span className="sr-only">Allen Guthier LinkedIn Profile</span>
                        </a>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                {/* New Advisor: Adarsh Bhatt */}
                <Card>
                  <CardContent className="p-6">
                    <div className="flex flex-col items-center text-center">
                      <Image src="/images/headshots/Adarsh_Bhatt_Headshot.png" alt="Adarsh Bhatt headshot" width={96} height={96} className="h-24 w-24 rounded-full object-cover mb-4" />
                      <h3 className="text-xl font-semibold">Adarsh Bhatt</h3>
                      <p className="text-sm text-muted-foreground mb-2">Strategic Advisor</p>
                      <p className="text-sm text-muted-foreground mb-4">
                        Co-Founder & GP at Comma Capital. First BD hire at multiple tech startups. Advises on fundraising, partnerships, and go-to-market strategy.
                      </p>
                      <div className="flex gap-2">
                        <a 
                          href="https://www.linkedin.com/in/adbhatt/" 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          aria-label="Adarsh Bhatt LinkedIn Profile"
                          className="text-muted-foreground hover:text-foreground"
                        >
                          <Linkedin className="h-5 w-5" />
                          <span className="sr-only">Adarsh Bhatt LinkedIn Profile</span>
                        </a>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </section>



          <section className="bg-muted py-12 md:py-16">
            <div className="container max-w-3xl text-center">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">Join Our Open Community</h2>
              <p className="text-lg text-muted-foreground mb-8">
                Help shape the future of AI content provenance!  Encypher is open-source (AGPL-3.0) and built collaboratively. Find out how you can contribute.
              </p>
              <div className="flex flex-col sm:flex-row justify-center gap-4"> 
                <Button asChild className="shadow-lg btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                  {/* Link to contribution guide or relevant section */}
                  <a href={`${siteConfig.links.github}/blob/main/CONTRIBUTING.md`} target="_blank" rel="noopener noreferrer">
                    <Code className="mr-2 h-4 w-4" />
                    Contribute
                  </a>
                </Button>
                <Button asChild>
                  {/* Link to main repository */}
                  <a href={siteConfig.links.github} target="_blank" rel="noopener noreferrer">
                    <Github className="mr-2 h-4 w-4" />
                    Repository
                  </a>
                </Button>
              </div>
            </div>
          </section>

          <section id="contact" className="pt-8">
            <h2 className="text-2xl font-semibold mb-4">Get in Touch</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex flex-col items-center text-center">
                    <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                      <Github className="h-6 w-6 text-primary" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">GitHub</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      Report issues, contribute code, or explore the project on GitHub.
                    </p>
                    <Button asChild size="sm" className="shadow-md btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                      <a 
                        href="https://github.com/encypherai/encypher-ai" 
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        Visit Repository
                      </a>
                    </Button>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6">
                  <div className="flex flex-col items-center text-center">
                    <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                      <Mail className="h-6 w-6 text-primary" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">Email</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      For commercial licensing, enterprise solutions, or sales inquiries.
                    </p>
                    <Button asChild size="sm" className="shadow-md btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                      <a href="mailto:licensing@encypherai.com">
                        licensing@encypherai.com
                      </a>
                    </Button>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6">
                  <div className="flex flex-col items-center text-center">
                    <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                      <MessageSquare className="h-6 w-6 text-primary" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">Community</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      Join our community discussions, ask questions, and share your experiences.
                    </p>
                    <Button asChild size="sm" className="shadow-md btn-blue-hover" style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}>
                      <a 
                        href="https://github.com/encypherai/encypher-ai/discussions" 
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        Join Discussions
                      </a>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
