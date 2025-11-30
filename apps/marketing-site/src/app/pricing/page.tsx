'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AnimatePresence } from 'framer-motion';
import { ArrowRight, Check, Zap, Building2 } from 'lucide-react';
import Link from 'next/link';
import SalesContactModal from '@/components/forms/SalesContactModal';
import AISummary from '@/components/seo/AISummary';
import { getAllTiers, formatPrice, formatRevShare, type TierConfig } from '@encypher/pricing-config';

// Dashboard URL for sign-up flows
const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypherai.com';

// Marketing-specific tier descriptions
const TIER_MARKETING: Record<string, { description: string; bestFor: string; cta: { text: string; variant: 'default' | 'outline' }; showPrice: boolean }> = {
  starter: {
    description: 'For bloggers and small publishers',
    bestFor: 'Independent bloggers, small sites',
    cta: { text: 'Get Started Free', variant: 'outline' },
    showPrice: true,
  },
  professional: {
    description: 'For regional publishers and growing media companies',
    bestFor: 'Regional newspapers, digital magazines, trade publications',
    cta: { text: 'Start Free Trial', variant: 'default' },
    showPrice: true,
  },
  business: {
    description: 'For major digital publishers needing enterprise features',
    bestFor: 'Major digital publishers, news networks',
    cta: { text: 'Start Free Trial', variant: 'outline' },
    showPrice: true,
  },
  enterprise: {
    description: 'For Tier 1 publishers and major media companies',
    bestFor: 'NYT, Universal Music, News Corp, major media conglomerates',
    cta: { text: 'Contact Sales', variant: 'outline' },
    showPrice: false,
  },
};

export default function PricingPage() {
  const [showPublisherModal, setShowPublisherModal] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [showEnterpriseModal, setShowEnterpriseModal] = useState(false);
  
  const tiers = getAllTiers();

  return (
    <div className="bg-background text-foreground">
      <AISummary
        title="Encypher Pricing"
        whatWeDo="Provide flexible pricing from free self-service to white-glove enterprise implementations."
        whoItsFor="Publishers of all sizes seeking content authentication and AI licensing revenue."
        keyDifferentiator="Success-based models aligned with outcomes. Earn when AI companies use your content."
        primaryValue="Start free, scale as you grow. Coalition revenue share improves with each tier."
      />

      {/* Hero Section */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
              For Publishers: From WordPress to Enterprise
            </h1>
            <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-4">
              Scale from self-service plugins to white-glove implementations. Success-based models mean we only win when you generate licensing revenue.
            </p>
          </div>

          {/* Pricing Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
            {tiers.map((tier: TierConfig) => {
              const marketing = TIER_MARKETING[tier.id];
              const isPopular = tier.popular;
              
              return (
                <div 
                  key={tier.id}
                  className={`bg-card rounded-lg p-6 relative ${
                    isPopular 
                      ? 'border-2 border-primary/50 shadow-lg' 
                      : 'border border-border'
                  }`}
                >
                  {isPopular && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                      <Badge variant="default" className="px-4 py-1 text-sm font-semibold bg-primary">
                        Most Popular
                      </Badge>
                    </div>
                  )}
                  
                  <div className="mb-4">
                    <h3 className="text-xl font-bold mb-2">{tier.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {marketing.description}
                    </p>
                  </div>

                  <div className="mb-4">
                    <div className="text-3xl font-bold mb-1">
                      {marketing.showPrice ? formatPrice(tier) : 'Custom'}
                    </div>
                    {marketing.showPrice && tier.price.monthly > 0 && (
                      <p className="text-sm text-muted-foreground">/month</p>
                    )}
                    {marketing.showPrice && tier.price.monthly === 0 && (
                      <p className="text-sm text-muted-foreground">Forever free for basic usage</p>
                    )}
                    {!marketing.showPrice && (
                      <p className="text-sm text-muted-foreground">White-glove everything. Success-based model.</p>
                    )}
                  </div>

                  {/* Coalition Rev Share Badge */}
                  <div className="bg-primary/10 rounded-lg p-3 mb-4 text-center">
                    <p className="text-xs text-muted-foreground">Coalition Revenue</p>
                    <p className="text-sm font-semibold text-primary">{formatRevShare(tier)}</p>
                  </div>

                  <ul className="space-y-2 mb-6">
                    {tier.features.slice(0, 6).map((feature) => (
                      <li key={feature} className="flex items-start gap-2">
                        <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <div className="mb-4 pt-4 border-t border-border">
                    <p className="text-xs text-muted-foreground">
                      <strong>Best for:</strong> {marketing.bestFor}
                    </p>
                  </div>

                  {tier.enterprise ? (
                    <Button 
                      onClick={() => setShowPublisherModal(true)}
                      className="w-full" 
                      variant={marketing.cta.variant}
                    >
                      {marketing.cta.text} <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  ) : (
                    <Button asChild className="w-full" variant={marketing.cta.variant}>
                      <Link href={tier.price.monthly === 0 ? `${DASHBOARD_URL}/signup` : `${DASHBOARD_URL}/signup?plan=${tier.id}`}>
                        {marketing.cta.text} <ArrowRight className="ml-2 h-4 w-4" />
                      </Link>
                    </Button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Publisher Value Prop */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto bg-primary/5 border-2 border-primary/20 rounded-lg p-8">
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

      {/* Feature Comparison Table */}
      <section className="py-20 w-full bg-muted/30">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            Feature Comparison
          </h2>
          <p className="text-lg text-muted-foreground text-center mb-12 max-w-2xl mx-auto">
            Compare features across our publisher tiers to find the right fit for your needs.
          </p>

          <div className="max-w-5xl mx-auto overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-4 px-4 font-semibold">Feature</th>
                  <th className="text-center py-4 px-4 font-semibold">Starter<br/><span className="text-xs font-normal text-muted-foreground">Free</span></th>
                  <th className="text-center py-4 px-4 font-semibold bg-primary/5 border-x border-primary/20">Professional<br/><span className="text-xs font-normal text-muted-foreground">$99/mo</span></th>
                  <th className="text-center py-4 px-4 font-semibold">Business<br/><span className="text-xs font-normal text-muted-foreground">$499/mo</span></th>
                  <th className="text-center py-4 px-4 font-semibold">Enterprise<br/><span className="text-xs font-normal text-muted-foreground">Custom</span></th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {/* C2PA Signing */}
                <tr className="border-b border-border/50">
                  <td className="py-3 px-4 font-medium">C2PA Document Signing</td>
                  <td className="text-center py-3 px-4">10K/mo</td>
                  <td className="text-center py-3 px-4 bg-primary/5 border-x border-primary/20">Unlimited</td>
                  <td className="text-center py-3 px-4">Unlimited</td>
                  <td className="text-center py-3 px-4">Unlimited</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 px-4 font-medium">Sentence-Level Tracking</td>
                  <td className="text-center py-3 px-4 text-muted-foreground">—</td>
                  <td className="text-center py-3 px-4 bg-primary/5 border-x border-primary/20">50K/mo</td>
                  <td className="text-center py-3 px-4">500K/mo</td>
                  <td className="text-center py-3 px-4">Unlimited</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 px-4 font-medium">Batch Operations</td>
                  <td className="text-center py-3 px-4 text-muted-foreground">—</td>
                  <td className="text-center py-3 px-4 bg-primary/5 border-x border-primary/20 text-muted-foreground">—</td>
                  <td className="text-center py-3 px-4"><Check className="h-4 w-4 text-primary mx-auto" /></td>
                  <td className="text-center py-3 px-4"><Check className="h-4 w-4 text-primary mx-auto" /></td>
                </tr>
                {/* Team & Management */}
                <tr className="border-b border-border/50 bg-muted/30">
                  <td className="py-3 px-4 font-medium" colSpan={5}>Team & Management</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 px-4 font-medium">API Keys</td>
                  <td className="text-center py-3 px-4">2</td>
                  <td className="text-center py-3 px-4 bg-primary/5 border-x border-primary/20">10</td>
                  <td className="text-center py-3 px-4">50</td>
                  <td className="text-center py-3 px-4">Unlimited</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 px-4 font-medium">Team Members</td>
                  <td className="text-center py-3 px-4">1</td>
                  <td className="text-center py-3 px-4 bg-primary/5 border-x border-primary/20">5</td>
                  <td className="text-center py-3 px-4">10</td>
                  <td className="text-center py-3 px-4">Unlimited</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 px-4 font-medium">Audit Logs</td>
                  <td className="text-center py-3 px-4 text-muted-foreground">—</td>
                  <td className="text-center py-3 px-4 bg-primary/5 border-x border-primary/20 text-muted-foreground">—</td>
                  <td className="text-center py-3 px-4"><Check className="h-4 w-4 text-primary mx-auto" /></td>
                  <td className="text-center py-3 px-4"><Check className="h-4 w-4 text-primary mx-auto" /></td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 px-4 font-medium">SSO / SCIM</td>
                  <td className="text-center py-3 px-4 text-muted-foreground">—</td>
                  <td className="text-center py-3 px-4 bg-primary/5 border-x border-primary/20 text-muted-foreground">—</td>
                  <td className="text-center py-3 px-4 text-muted-foreground">—</td>
                  <td className="text-center py-3 px-4"><Check className="h-4 w-4 text-primary mx-auto" /></td>
                </tr>
                {/* Coalition */}
                <tr className="border-b border-border/50 bg-muted/30">
                  <td className="py-3 px-4 font-medium" colSpan={5}>Coalition Revenue Share</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 px-4 font-medium">Your Share</td>
                  <td className="text-center py-3 px-4">65%</td>
                  <td className="text-center py-3 px-4 bg-primary/5 border-x border-primary/20 font-semibold text-primary">70%</td>
                  <td className="text-center py-3 px-4">75%</td>
                  <td className="text-center py-3 px-4">80%</td>
                </tr>
                {/* Support */}
                <tr className="border-b border-border/50 bg-muted/30">
                  <td className="py-3 px-4 font-medium" colSpan={5}>Support</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 px-4 font-medium">Support Level</td>
                  <td className="text-center py-3 px-4">Community</td>
                  <td className="text-center py-3 px-4 bg-primary/5 border-x border-primary/20">Email (48hr)</td>
                  <td className="text-center py-3 px-4">Priority (24hr)</td>
                  <td className="text-center py-3 px-4">Dedicated TAM</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 px-4 font-medium">Analytics Retention</td>
                  <td className="text-center py-3 px-4">7 days</td>
                  <td className="text-center py-3 px-4 bg-primary/5 border-x border-primary/20">90 days</td>
                  <td className="text-center py-3 px-4">1 year</td>
                  <td className="text-center py-3 px-4">Unlimited</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ICP Selection - Other Audiences */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            Not a Publisher?
          </h2>
          <p className="text-lg text-muted-foreground text-center mb-12 max-w-2xl mx-auto">
            We also work with AI labs and enterprises. Choose your path below.
          </p>

          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {/* AI Labs Card */}
            <div className="bg-card rounded-lg border-2 border-border p-8 hover:border-primary transition-colors">
              <Zap className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-2xl font-bold mb-3">AI Labs</h3>
              <p className="text-sm text-muted-foreground mb-6">
                Publisher ecosystem access + performance intelligence in one infrastructure layer.
              </p>
              <Button 
                onClick={() => setShowAIModal(true)}
                className="w-full"
                variant="outline"
              >
                Schedule Technical Evaluation <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>

            {/* Enterprises Card */}
            <div className="bg-card rounded-lg border-2 border-border p-8 hover:border-primary transition-colors">
              <Building2 className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-2xl font-bold mb-3">Enterprises</h3>
              <p className="text-sm text-muted-foreground mb-6">
                EU AI Act compliance baseline with performance intelligence upside for scaled deployments.
              </p>
              <Button 
                onClick={() => setShowEnterpriseModal(true)}
                className="w-full"
                variant="outline"
              >
                Contact Enterprise Sales <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Sales Modals */}
      <AnimatePresence>
        {showPublisherModal && (
          <SalesContactModal
            onClose={() => setShowPublisherModal(false)}
            context="publisher"
            title="Publisher Inquiry"
            subtitle="Tell us about your publication and we'll help you find the right plan."
          />
        )}
      </AnimatePresence>
      <AnimatePresence>
        {showAIModal && (
          <SalesContactModal
            onClose={() => setShowAIModal(false)}
            context="ai"
            title="AI Lab Technical Evaluation"
            subtitle="Schedule a technical evaluation to explore our infrastructure."
          />
        )}
      </AnimatePresence>
      <AnimatePresence>
        {showEnterpriseModal && (
          <SalesContactModal
            onClose={() => setShowEnterpriseModal(false)}
            context="enterprise"
            title="Enterprise Inquiry"
            subtitle="Let's discuss your compliance and infrastructure needs."
          />
        )}
      </AnimatePresence>
    </div>
  );
}
