'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Check } from 'lucide-react';
import {
  FREE_TIER,
  ENTERPRISE_TIER,
} from '@/lib/pricing-config';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypher.com';

export function PricingTable() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
      {/* Free Tier */}
      <Card className="flex flex-col border-primary shadow-lg ring-2 ring-primary/20">
        <div className="bg-primary text-primary-foreground text-center text-sm font-medium py-1 rounded-t-lg">
          Start Here
        </div>
        <CardHeader>
          <CardTitle>{FREE_TIER.name}</CardTitle>
          <div className="mt-2">
            <span className="text-3xl font-bold">$0</span>
            <span className="text-muted-foreground">/month</span>
          </div>
          <CardDescription className="mt-3">
            Full signing infrastructure. {FREE_TIER.limits.documentsPerMonth.toLocaleString()} docs/month.
            Join the coalition and earn when AI companies license your content.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-1">
          <ul className="space-y-2">
            {[
              'Prove ownership of every piece of content you publish',
              'Detect when your content is copied, scraped, or modified',
              'Invisible signatures that survive copy-paste and redistribution',
              'Anyone can verify your content is authentic — no login required',
              'Join a coalition that licenses your content to AI companies — bringing you revenue',
              'WordPress integration — protect content the moment you hit publish',
            ].map((feature: string) => (
              <li key={feature} className="flex items-start gap-2">
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-sm">{feature}</span>
              </li>
            ))}
          </ul>
        </CardContent>
        <CardFooter>
          <Button asChild className="w-full">
            <a href={`${DASHBOARD_URL}/auth/signin?mode=signup&source=pricing-free`}>Get Started Free</a>
          </Button>
        </CardFooter>
      </Card>

      {/* Enterprise */}
      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle>{ENTERPRISE_TIER.name}</CardTitle>
          <div className="mt-2">
            <span className="text-3xl font-bold">Custom</span>
          </div>
          <CardDescription className="mt-3">
            Unlimited everything. All add-ons included. Exclusive capabilities.
            Dedicated support. Custom pricing tailored to your organization.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-1">
          <ul className="space-y-2">
            {[
              'Unlimited signing — no caps on volume or API calls',
              'Real-time AI output monitoring for your content',
              'Enforcement tools — formal notices and evidence packages',
              'Sign as your brand with white-label verification',
              'Streaming LLM signing for AI-generated content',
              'Dedicated SLA, SSO, and named account manager',
            ].map((feature: string) => (
              <li key={feature} className="flex items-start gap-2">
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-sm">{feature}</span>
              </li>
            ))}
          </ul>
        </CardContent>
        <CardFooter>
          <Button asChild className="w-full" variant="outline">
            <a href="/contact">Contact Sales</a>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
