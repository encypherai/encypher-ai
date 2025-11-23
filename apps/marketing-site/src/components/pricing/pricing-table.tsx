'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Check } from 'lucide-react';

const tiers = [
  {
    name: 'Open Source (AGPLv3)',
    description: 'Ideal for individual developers, researchers, and open-source projects. Requires any modifications or derivative works (if networked) to be shared under AGPLv3. Perfect for experimentation and community collaboration.',
    price: 'Free',
    period: '',
    features: [
      'Full access to all core functions',
      'AGPLv3 license',
      'Community support via GitHub & Discord',
      'Public documentation',
      'Full source code access'
    ],
    cta: 'View on GitHub',
    ctaLink: 'https://github.com/encypherai/encypher-ai',
    highlighted: false
  },
  {
    name: 'Commercial License',
    description: 'For businesses and organizations requiring the flexibility to integrate Encypher into proprietary systems without AGPLv3\'s open-source obligations. Includes standard support.',
    price: '$5,000',
    startingAt: true,
    period: 'per year',
    features: [
      'Use in proprietary/closed-source projects',
      'Standard email support (2 business day SLA)',
      'Access to updates and maintenance releases',
      'Suitable for most commercial applications',
      'License compliance assurance'
    ],
    cta: 'Contact Sales',
    ctaLink: '/about#contact',
    highlighted: false
  },
  {
    name: 'Enterprise License',
    description: 'Tailored for large-scale deployments with specific compliance, security, and support needs. Includes dedicated support, custom integrations, and volume-based pricing.',
    price: 'Custom Pricing',
    startingAt: false,
    period: '',
    features: [
      'All Commercial License features',
      'Dedicated account manager & priority support (custom SLA)',
      'Custom integration support & consultancy hours',
      'Volume-based pricing & flexible deployment options',
      'Option for on-premise or private cloud deployment',
      'Security & compliance review assistance',
      'Influence on product roadmap'
    ],
    cta: 'Contact Sales',
    ctaLink: '/about#contact',
    highlighted: true
  }
];

export function PricingTable() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {tiers.map((tier) => (
        <Card 
          key={tier.name} 
          className={`flex flex-col ${tier.highlighted ? 'border-primary shadow-lg' : ''}`}
        >
          <CardHeader>
            <CardTitle>{tier.name}</CardTitle>
            <CardDescription>{tier.description}</CardDescription>
          </CardHeader>
          <CardContent className="flex-1">
            <div className="mb-6">
              {tier.price === 'Custom Pricing' ? (
                <a href={tier.ctaLink} className="block">
                  <Button variant="default" className="w-full text-lg py-6">{tier.cta}</Button>
                </a>
              ) : (
                <>
                  {tier.startingAt && (
                    <span className="block text-sm text-muted-foreground mb-1">Starting at</span>
                  )}
                  <span className="text-3xl font-bold">{tier.price}</span>
                  {tier.period && <span className="text-muted-foreground ml-1">{tier.period}</span>}
                </>
              )}
            </div>
            <ul className="space-y-2">
              {tier.features.map((feature) => (
                <li key={feature} className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-primary" />
                  <span className="text-sm">{feature}</span>
                </li>
              ))}
            </ul>
          </CardContent>
          <CardFooter>
            {tier.price !== 'Custom Pricing' && (
              <Button 
                asChild 
                className="w-full" 
                variant={tier.highlighted ? 'default' : 'outline'}
              >
                <a href={tier.ctaLink}>{tier.cta}</a>
              </Button>
            )}
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}