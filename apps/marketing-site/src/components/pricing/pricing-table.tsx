'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Check } from 'lucide-react';
import { getAllTiers, formatPrice, formatRevShare, type TierConfig } from '@encypher/pricing-config';

// Dashboard URL for sign-up flows
const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypherai.com';

// Marketing-specific tier descriptions (more persuasive than generic)
const TIER_DESCRIPTIONS: Record<string, string> = {
  starter: 'Perfect for bloggers and small publishers. Sign unlimited content, join the licensing coalition, and earn when AI companies use your content.',
  professional: 'For regional news and niche publications. Track every sentence, know when your content appears in AI outputs, and earn a better revenue share.',
  business: 'For major digital publishers. Enterprise-grade content tracking, plagiarism detection, team collaboration, and the best self-serve revenue share.',
  enterprise: 'For global media giants and wire services. Full platform access, dedicated support, custom SLAs, and the best revenue share terms.',
};

// Marketing-specific CTAs
const TIER_CTAS: Record<string, { text: string; link: string }> = {
  starter: { text: 'Get Started Free', link: `${DASHBOARD_URL}/signup` },
  professional: { text: 'Start Free Trial', link: `${DASHBOARD_URL}/signup?plan=professional` },
  business: { text: 'Start Free Trial', link: `${DASHBOARD_URL}/signup?plan=business` },
  enterprise: { text: 'Contact Sales', link: '/about#contact' },
};

// Get tiers from shared config
const tiers = getAllTiers();

export function PricingTable() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {tiers.map((tier: TierConfig) => {
        const cta = TIER_CTAS[tier.id];
        const description = TIER_DESCRIPTIONS[tier.id];
        
        return (
          <Card 
            key={tier.id} 
            className={`flex flex-col ${tier.popular ? 'border-primary shadow-lg ring-2 ring-primary/20' : ''}`}
          >
            {tier.popular && (
              <div className="bg-primary text-primary-foreground text-center text-sm font-medium py-1 rounded-t-lg">
                Most Popular
              </div>
            )}
            <CardHeader>
              <CardTitle>{tier.name}</CardTitle>
              <div className="mt-2">
                <span className="text-3xl font-bold">{formatPrice(tier)}</span>
                {!tier.enterprise && tier.price.monthly > 0 && (
                  <span className="text-muted-foreground">/month</span>
                )}
              </div>
              {/* Coalition Revenue Share - Lead with this */}
              <div className="mt-3 p-2 bg-muted/50 rounded-lg text-center">
                <p className="text-xs text-muted-foreground">Coalition Revenue</p>
                <p className="text-sm font-semibold">{formatRevShare(tier)}</p>
              </div>
              <CardDescription className="mt-3">{description}</CardDescription>
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
                variant={tier.popular ? 'default' : 'outline'}
              >
                <a href={cta.link}>{cta.text}</a>
              </Button>
            </CardFooter>
          </Card>
        );
      })}
    </div>
  );
}