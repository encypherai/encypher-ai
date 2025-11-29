'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Check } from 'lucide-react';

// Dashboard URL for sign-up flows
const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypherai.com';

const tiers = [
  {
    name: 'Starter',
    description: 'Perfect for bloggers and small publishers. Sign unlimited content, join the licensing coalition, and earn when AI companies use your content.',
    price: 'Free',
    period: '',
    revShare: '65% you / 35% Encypher',
    features: [
      'Unlimited C2PA signing',
      'Unlimited verifications',
      '2 API keys',
      'Community support',
      '7-day analytics',
      'Auto-join licensing coalition',
    ],
    cta: 'Get Started Free',
    ctaLink: `${DASHBOARD_URL}/signup`,
    highlighted: false
  },
  {
    name: 'Professional',
    description: 'For regional news and niche publications. Track every sentence, know when your content appears in AI outputs, and earn a better revenue share.',
    price: '$99',
    period: '/month',
    revShare: '70% you / 30% Encypher',
    features: [
      'Everything in Starter',
      'Sentence-level tracking (50K/mo)',
      'Invisible embeddings',
      '10 API keys',
      'Email support (48hr SLA)',
      '90-day analytics',
      'BYOK encryption',
      'WordPress Pro (no branding)',
    ],
    cta: 'Start Free Trial',
    ctaLink: `${DASHBOARD_URL}/signup?plan=professional`,
    highlighted: true
  },
  {
    name: 'Business',
    description: 'For major digital publishers. Enterprise-grade content tracking, plagiarism detection, team collaboration, and the best self-serve revenue share.',
    price: '$499',
    period: '/month',
    revShare: '75% you / 25% Encypher',
    features: [
      'Everything in Professional',
      'Merkle tree encoding',
      'Plagiarism detection',
      'Source attribution API',
      'Batch operations (100 docs)',
      '50 API keys',
      'Priority support (24hr SLA)',
      '1-year analytics',
      'Team management (10 users)',
      'Audit logs',
    ],
    cta: 'Start Free Trial',
    ctaLink: `${DASHBOARD_URL}/signup?plan=business`,
    highlighted: false
  },
  {
    name: 'Enterprise',
    description: 'For global media giants and wire services. Full platform access, dedicated support, custom SLAs, and the best revenue share terms.',
    price: 'Custom',
    period: '',
    revShare: '80% you / 20% Encypher',
    features: [
      'Everything in Business',
      'Unlimited everything',
      'Custom C2PA assertions',
      'SSO/SCIM integration',
      'Dedicated TAM + Slack',
      'Custom SLAs',
      'On-premise option',
      'White-label WordPress',
    ],
    cta: 'Contact Sales',
    ctaLink: '/about#contact',
    highlighted: false,
    enterprise: true
  }
];

export function PricingTable() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {tiers.map((tier) => (
        <Card 
          key={tier.name} 
          className={`flex flex-col ${tier.highlighted ? 'border-primary shadow-lg ring-2 ring-primary/20' : ''}`}
        >
          {tier.highlighted && (
            <div className="bg-primary text-primary-foreground text-center text-sm font-medium py-1 rounded-t-lg">
              Most Popular
            </div>
          )}
          <CardHeader>
            <CardTitle>{tier.name}</CardTitle>
            <div className="mt-2">
              <span className="text-3xl font-bold">{tier.price}</span>
              {tier.period && <span className="text-muted-foreground">{tier.period}</span>}
            </div>
            {/* Coalition Revenue Share - Lead with this */}
            <div className="mt-3 p-2 bg-muted/50 rounded-lg text-center">
              <p className="text-xs text-muted-foreground">Coalition Revenue</p>
              <p className="text-sm font-semibold">{tier.revShare}</p>
            </div>
            <CardDescription className="mt-3">{tier.description}</CardDescription>
          </CardHeader>
          <CardContent className="flex-1">
            <ul className="space-y-2">
              {tier.features.map((feature) => (
                <li key={feature} className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{feature}</span>
                </li>
              ))}
            </ul>
          </CardContent>
          <CardFooter>
            <Button 
              asChild 
              className="w-full" 
              variant={tier.highlighted ? 'default' : 'outline'}
            >
              <a href={tier.ctaLink}>{tier.cta}</a>
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}