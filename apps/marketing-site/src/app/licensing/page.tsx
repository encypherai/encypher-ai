'use client';

import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, Check, FileText, Zap, Building2, Code, ChevronDown } from 'lucide-react';
import Link from 'next/link';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import SalesContactModal from '@/components/forms/SalesContactModal';
import AISummary from '@/components/seo/AISummary';

export default function LicensingPage() {
  const [showPublisherModal, setShowPublisherModal] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [showEnterpriseModal, setShowEnterpriseModal] = useState(false);
  return (
    <div className="bg-background text-foreground">
      <AISummary
        title="Encypher Licensing & Pricing"
        whatWeDo="Provide flexible licensing options from self-service WordPress plugins to white-glove enterprise implementations."
        whoItsFor="Publishers of all sizes, AI labs, and Fortune 500 companies seeking content authentication infrastructure."
        keyDifferentiator="Success-based models aligned with outcomes. Scale from plugin to enterprise as your needs evolve."
        primaryValue="Contact us to explore licensing tailored to your specific use case and scale."
      />

      {/* Hero Section - ICP Selector */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
              Licensing for Every Scale
            </h1>
            <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-4">
              From self-service WordPress plugins to enterprise infrastructure. Success-based models aligned with your outcomes.
            </p>
            <p className="text-base text-muted-foreground">
              Choose your path below to explore options tailored to your needs.
            </p>
          </div>

          {/* ICP Selection Cards */}
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            
            {/* Publishers Card */}
            <a 
              href="#publishers" 
              className="bg-card rounded-lg border-2 border-border p-8 hover:border-primary transition-colors cursor-pointer group"
            >
              <FileText className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-2xl font-bold mb-3 text-center">Publishers</h3>
              <p className="text-sm text-muted-foreground text-center mb-6">
                Transform AI copyright challenges into licensing revenue. From WordPress to enterprise.
              </p>
              <div className="flex items-center justify-center gap-2 text-primary group-hover:gap-3 transition-all">
                <span className="font-semibold">Explore Options</span>
                <ChevronDown className="h-4 w-4" />
              </div>
            </a>

            {/* AI Labs Card */}
            <a 
              href="#ai-labs" 
              className="bg-card rounded-lg border-2 border-border p-8 hover:border-primary transition-colors cursor-pointer group"
            >
              <Zap className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-2xl font-bold mb-3 text-center">AI Labs</h3>
              <p className="text-sm text-muted-foreground text-center mb-6">
                Publisher ecosystem access + performance intelligence in one infrastructure layer.
              </p>
              <div className="flex items-center justify-center gap-2 text-primary group-hover:gap-3 transition-all">
                <span className="font-semibold">Explore Options</span>
                <ChevronDown className="h-4 w-4" />
              </div>
            </a>

            {/* Enterprises Card */}
            <a 
              href="#enterprises" 
              className="bg-card rounded-lg border-2 border-border p-8 hover:border-primary transition-colors cursor-pointer group"
            >
              <Building2 className="h-12 w-12 text-primary mb-4 mx-auto" />
              <h3 className="text-2xl font-bold mb-3 text-center">Enterprises</h3>
              <p className="text-sm text-muted-foreground text-center mb-6">
                EU AI Act compliance baseline with performance intelligence upside for scaled deployments.
              </p>
              <div className="flex items-center justify-center gap-2 text-primary group-hover:gap-3 transition-all">
                <span className="font-semibold">Explore Options</span>
                <ChevronDown className="h-4 w-4" />
              </div>
            </a>
          </div>
        </div>
      </section>

      {/* Publishers Section */}
      <section id="publishers" className="py-20 w-full bg-background scroll-mt-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <FileText className="h-12 w-12 text-primary mx-auto mb-4" />
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              For Publishers: From WordPress to Enterprise
            </h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              Scale from self-service plugins to white-glove implementations. Success-based models mean we only win when you generate licensing revenue.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            
            {/* WordPress Plugin Tier */}
            <div className="bg-card rounded-lg border border-border p-8">
              <div className="mb-6">
                <h3 className="text-2xl font-bold mb-2 flex items-center gap-2">WordPress Plugin <Badge variant="blue" className="uppercase tracking-wide text-[10px] px-2 py-1">COMING SOON</Badge></h3>
                <p className="text-sm text-muted-foreground">
                  For bloggers, small publishers, and CMS users
                </p>
              </div>

              <div className="mb-6">
                <div className="text-3xl font-bold mb-2">Free to Start</div>
                <p className="text-sm text-muted-foreground">
                  Revenue share on licensing you generate.<br />
                  No licensing? No cost.
                </p>
              </div>

              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Self-service installation (WordPress, Drupal, Joomla)</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Basic C2PA content authentication</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Document-level tracking</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Community support</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Usage dashboard</span>
                </li>
              </ul>

              <div className="mb-6 pt-6 border-t border-border">
                <p className="text-sm text-muted-foreground">
                  <strong>Best for:</strong> Independent publishers, bloggers, small news sites, niche publications
                </p>
              </div>

              <Button asChild className="w-full" variant="outline">
                {/* <Link href="/wordpress-plugin"> */}
                  <span className="flex items-center justify-center gap-2">
                    Get Plugin <Badge variant="blue" className="uppercase tracking-wide text-[10px]">COMING SOON</Badge> <ArrowRight className="ml-2 h-4 w-4" />
                  </span>
                {/* </Link> */}
              </Button>
            </div>

            {/* Professional Tier */}
            <div className="bg-card rounded-lg border-2 border-primary/50 p-8 relative">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                <Badge variant="blue" className="px-4 py-1 text-sm font-semibold">Most Popular</Badge>
              </div>
              
              <div className="mb-6">
                <h3 className="text-2xl font-bold mb-2">Professional</h3>
                <p className="text-sm text-muted-foreground">
                  For regional publishers and growing media companies
                </p>
              </div>

              <div className="mb-6">
                <div className="text-3xl font-bold mb-2">Let's Talk</div>
                <p className="text-sm text-muted-foreground">
                  Implementation + success-based revenue share.<br />
                  We'll tailor pricing to your situation.
                </p>
              </div>

              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm"><strong>Sentence-level tracking</strong> (proprietary)</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">White-glove implementation support</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Court-admissible evidence packages</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Usage intelligence dashboard</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Priority support (email + Slack)</span>
                </li>
              </ul>

              <div className="mb-6 pt-6 border-t border-border">
                <p className="text-sm text-muted-foreground">
                  <strong>Best for:</strong> Regional newspapers, digital magazines, trade publications, medium publishers
                </p>
              </div>

              <Button 
                onClick={() => setShowPublisherModal(true)}
                className="w-full btn-blue-hover" 
                style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}
              >
                Schedule Discovery Call <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>

            {/* Enterprise Tier */}
            <div className="bg-card rounded-lg border border-border p-8">
              <div className="mb-6">
                <h3 className="text-2xl font-bold mb-2">Enterprise</h3>
                <p className="text-sm text-muted-foreground">
                  For Tier 1 publishers and major media companies
                </p>
              </div>

              <div className="mb-6">
                <div className="text-3xl font-bold mb-2">Custom</div>
                <p className="text-sm text-muted-foreground">
                  White-glove everything. Success-based model aligned with your scale.
                </p>
              </div>

              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Everything in Professional, plus:</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm"><strong>Coalition founding member benefits</strong></span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Preferential revenue share terms</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Advisory board seat</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Dedicated technical account manager</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">Custom feature development</span>
                </li>
              </ul>

              <div className="mb-6 pt-6 border-t border-border">
                <p className="text-sm text-muted-foreground">
                  <strong>Best for:</strong> NYT, Universal Music, News Corp, major media conglomerates
                </p>
              </div>

              <Button 
                onClick={() => setShowPublisherModal(true)}
                className="w-full" 
                variant="outline"
              >
                Contact Sales <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Publisher Value Prop */}
          <div className="mt-16 max-w-4xl mx-auto bg-primary/5 border-2 border-primary/20 rounded-lg p-8">
            <h3 className="text-2xl font-bold mb-4 text-center">The Publisher Opportunity</h3>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <p className="text-sm text-muted-foreground mb-2">Traditional Approach:</p>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Litigation costs</span>
                    <span className="font-semibold text-destructive">Millions/year</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Licensing revenue</span>
                    <span className="font-semibold">$0</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Evidence quality</span>
                    <span className="font-semibold text-destructive">26% accurate</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-border">
                    <span className="font-bold">Net result</span>
                    <span className="font-bold text-destructive">Loss</span>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm text-muted-foreground mb-2">With Encypher:</p>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Litigation costs</span>
                    <span className="font-semibold text-primary">Eliminated</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Licensing revenue</span>
                    <span className="font-semibold text-primary">Enabled</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Evidence quality</span>
                    <span className="font-semibold text-primary">100% accurate</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-border">
                    <span className="font-bold">Net result</span>
                    <span className="font-bold text-primary">Significant gain</span>
                  </div>
                </div>
              </div>
            </div>
            <p className="text-sm text-center text-muted-foreground mt-6">
              Success-based model means you keep the majority of licensing revenue. We only win when you win.
            </p>
          </div>
        </div>
      </section>

      {/* AI Labs Section */}
      <section id="ai-labs" className="py-20 w-full bg-muted/30 border-y border-border scroll-mt-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <Zap className="h-12 w-12 text-primary mx-auto mb-4" />
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              For AI Labs: Enterprise Infrastructure
            </h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              One integration covers the entire publisher ecosystem. Compliance + performance intelligence in a single infrastructure layer.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="bg-card rounded-lg border-2 border-primary/50 p-8 md:p-12">
              <div className="grid md:grid-cols-2 gap-8 mb-8">
                <div>
                  <h3 className="text-2xl font-bold mb-4">What You Get</h3>
                  <ul className="space-y-3">
                    <li className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-sm">Publisher ecosystem access (growing coalition)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-sm">Performance intelligence on all outputs</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-sm">Enhanced C2PA compliance infrastructure</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-sm">Litigation risk resolution</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-sm">Dedicated technical team</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-sm">Sentence-level tracking infrastructure</span>
                    </li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-2xl font-bold mb-4">The Value</h3>
                  <div className="space-y-4">
                    <div className="bg-primary/5 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Litigation risk mitigation</p>
                      <p className="text-xl font-bold text-primary">Significant</p>
                    </div>
                    <div className="bg-primary/5 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">R&D optimization</p>
                      <p className="text-xl font-bold text-primary">10x+ potential</p>
                    </div>
                    <div className="bg-primary/5 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Publisher compatibility</p>
                      <p className="text-xl font-bold text-primary">Essential</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border-t border-border pt-8">
                <h4 className="font-bold mb-4 text-center">Custom Enterprise Licensing</h4>
                <p className="text-muted-foreground mb-6 text-center">
                  Annual licensing tailored to your scale, use case, and integration requirements. Let's discuss what makes sense for your specific needs.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button 
                    onClick={() => setShowAIModal(true)}
                    size="lg" 
                    className="btn-blue-hover" 
                    style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}
                  >
                    Schedule Technical Evaluation <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                  <Button asChild size="lg" variant="outline">
                    <Link href="/solutions/ai-companies">
                      Learn More <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Enterprises Section */}
      <section id="enterprises" className="py-20 w-full bg-background scroll-mt-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <Building2 className="h-12 w-12 text-primary mx-auto mb-4" />
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              For Enterprises: AI Governance Infrastructure
            </h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              EU AI Act compliance baseline with performance intelligence upside. Turn regulatory requirement into competitive advantage.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            
            {/* Starter */}
            <div className="bg-card rounded-lg border border-border p-6">
              <h3 className="text-xl font-bold mb-2">Pilot</h3>
              <p className="text-sm text-muted-foreground mb-4">Validate value with limited deployment</p>
              
              <div className="mb-6">
                <div className="text-2xl font-bold mb-1">Contact Us</div>
                <p className="text-xs text-muted-foreground">We'll discuss scope and structure pricing accordingly</p>
              </div>

              <ul className="space-y-2 text-sm mb-6">
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Basic C2PA implementation</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Compliance reporting</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Standard support</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>30-60 day evaluation period</span>
                </li>
              </ul>

              <Button 
                onClick={() => setShowEnterpriseModal(true)}
                variant="outline" 
                size="sm" 
                className="w-full"
              >
                Contact Sales
              </Button>
            </div>

            {/* Production */}
            <div className="bg-card rounded-lg border-2 border-primary/50 p-6">
              <h3 className="text-xl font-bold mb-2">Production</h3>
              <p className="text-sm text-muted-foreground mb-4">Full-scale deployment with enhanced features</p>
              
              <div className="mb-6">
                <div className="text-2xl font-bold mb-1">Let's Talk</div>
                <p className="text-xs text-muted-foreground">Pricing based on volume and feature requirements</p>
              </div>

              <ul className="space-y-2 text-sm mb-6">
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Enhanced features + sentence-level tracking</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Intelligence dashboards</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Priority support</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>API access & integrations</span>
                </li>
              </ul>

              <Button 
                onClick={() => setShowEnterpriseModal(true)}
                size="sm" 
                className="w-full btn-blue-hover" 
                style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}
              >
                Schedule Call
              </Button>
            </div>

            {/* Enterprise */}
            <div className="bg-card rounded-lg border border-border p-6">
              <h3 className="text-xl font-bold mb-2">Enterprise</h3>
              <p className="text-sm text-muted-foreground mb-4">Custom everything for global deployments</p>
              
              <div className="mb-6">
                <div className="text-2xl font-bold mb-1">Custom</div>
                <p className="text-xs text-muted-foreground">Tailored to your specific requirements and scale</p>
              </div>

              <ul className="space-y-2 text-sm mb-6">
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Full capabilities + custom development</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>White-glove support</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Custom policy engine</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>SLA guarantees & dedicated team</span>
                </li>
              </ul>

              <Button asChild variant="outline" size="sm" className="w-full">
                <Link href="/solutions/enterprise">Learn More</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Open Source Section */}
      <section className="py-20 w-full bg-muted/30 border-y border-border">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <Code className="h-12 w-12 text-primary mx-auto mb-6" />
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Open Source Foundation
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Our C2PA text reference implementation is open source (AGPL-3.0). Start with the standard, upgrade to enterprise features when ready.
            </p>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="bg-card p-6 rounded-lg border border-border text-left">
                <h3 className="font-bold mb-3">Open Source (Free)</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>• Document-level C2PA authentication</li>
                  <li>• Basic verification</li>
                  <li>• Standard metadata</li>
                  <li>• Community support</li>
                </ul>
              </div>

              <div className="bg-card p-6 rounded-lg border-2 border-primary/30 text-left">
                <h3 className="font-bold mb-3">Commercial (Licensed)</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>• <strong>Sentence-level tracking</strong> (proprietary)</li>
                  <li>• Court-admissible evidence</li>
                  <li>• Performance intelligence</li>
                  <li>• White-glove support</li>
                </ul>
              </div>
            </div>

            <Button asChild variant="outline" size="lg">
              <a href="https://github.com/encypherai/encypher-ai" target="_blank" rel="noopener noreferrer">
                View on GitHub <ArrowRight className="ml-2 h-4 w-4" />
              </a>
            </Button>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Common Questions
          </h2>

          <div className="max-w-3xl mx-auto space-y-6">
            <div className="bg-card p-6 rounded-lg border border-border">
              <h3 className="font-bold mb-2">How does success-based pricing work?</h3>
              <p className="text-sm text-muted-foreground">
                For publishers: we take a percentage of licensing revenue you generate. If you generate zero licensing revenue, you pay nothing beyond any initial setup. We're incentivized to help you succeed—not just sell you software.
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <h3 className="font-bold mb-2">Why don't you show exact pricing?</h3>
              <p className="text-sm text-muted-foreground">
                Every situation is unique. Your content type, volume, existing licensing relationships, and technical requirements all factor into the right model. We'd rather have a conversation about your specific needs than show one-size-fits-all pricing that doesn't fit anyone perfectly.
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <h3 className="font-bold mb-2">Can I start small and scale up?</h3>
              <p className="text-sm text-muted-foreground">
                Absolutely. Many publishers start with our WordPress plugin (free), validate value, then upgrade to Professional or Enterprise tiers when they need sentence-level tracking for larger licensing deals. Your licensing scales as your needs evolve.
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <h3 className="font-bold mb-2">What's the difference between document-level and sentence-level tracking?</h3>
              <p className="text-sm text-muted-foreground">
                Document-level proves a document was accessed. Sentence-level proves <strong>which specific sentences</strong> were used—critical for copyright litigation and establishing licensing terms. Sentence-level is proprietary to Encypher and only available in commercial tiers.
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <h3 className="font-bold mb-2">Do you offer pilots or trials?</h3>
              <p className="text-sm text-muted-foreground">
                Yes. WordPress plugin is free to start. For Professional/Enterprise, we offer pilot programs (typically 30-60 days) to validate value before committing to long-term agreements. Contact sales to discuss pilot options for your situation.
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <h3 className="font-bold mb-2">What if I'm not sure which tier is right for me?</h3>
              <p className="text-sm text-muted-foreground">
                That's exactly why we offer discovery calls. We'll discuss your content volume, licensing goals, technical requirements, and budget constraints to recommend the best starting point. There's no pressure—just a conversation about what makes sense for your specific situation.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Standards Compliance */}
      <StandardsCompliance />

      {/* Final CTA */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Let's Find the Right Licensing Model for You
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            Whether you're exploring WordPress plugins or enterprise infrastructure, we'll help you understand your options without pressure or scary pricing surprises.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center">
            <Button 
              onClick={() => setShowPublisherModal(true)}
              size="lg" 
              className="w-full sm:w-auto shadow-lg btn-blue-hover" 
              style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}
            >
              Schedule a Conversation <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button asChild size="lg" variant="outline" className="w-full sm:w-auto shadow-lg">
              {/* <Link href="/wordpress-plugin"> */}
                <span className="flex items-center justify-center gap-2">
                  Try WordPress Plugin <Badge variant="blue" className="uppercase tracking-wide text-[10px]">COMING SOON</Badge> <ArrowRight className="ml-2 h-4 w-4" />
                </span>
              {/* </Link> */}
            </Button>
          </div>
        </div>
      </section>

      {/* Sales Contact Modals */}
      <AnimatePresence>
        {showPublisherModal && (
          <SalesContactModal 
            onClose={() => setShowPublisherModal(false)} 
            context="publisher"
          />
        )}
      </AnimatePresence>
      
      <AnimatePresence>
        {showAIModal && (
          <SalesContactModal 
            onClose={() => setShowAIModal(false)} 
            context="ai"
          />
        )}
      </AnimatePresence>
      
      <AnimatePresence>
        {showEnterpriseModal && (
          <SalesContactModal 
            onClose={() => setShowEnterpriseModal(false)} 
            context="enterprise"
          />
        )}
      </AnimatePresence>
    </div>
  );
}