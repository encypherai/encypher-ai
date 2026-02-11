'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Check } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import {
  FREE_TIER,
  ENTERPRISE_TIER,
  BUNDLES,
  formatBundlePrice,
} from '@/lib/pricing-config';

export function PricingTable() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
          <div className="mt-3 p-2 bg-muted/50 rounded-lg text-center">
            <p className="text-xs text-muted-foreground">Licensing Revenue</p>
            <p className="text-sm font-semibold">60/40 coalition · 80/20 self-service</p>
          </div>
          <CardDescription className="mt-3">
            Full signing infrastructure. {FREE_TIER.limits.documentsPerMonth.toLocaleString()} docs/month.
            Join the coalition and earn when AI companies license your content.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-1">
          <ul className="space-y-2">
            {FREE_TIER.signingFeatures.slice(0, 4).map((feature: string) => (
              <li key={feature} className="flex items-start gap-2">
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-sm">{feature}</span>
              </li>
            ))}
            {FREE_TIER.coalitionFeatures.slice(0, 2).map((feature: string) => (
              <li key={feature} className="flex items-start gap-2">
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-sm">{feature}</span>
              </li>
            ))}
          </ul>
        </CardContent>
        <CardFooter>
          <Button asChild className="w-full">
            <a href="/auth/signin?mode=signup&source=pricing-free">Get Started Free</a>
          </Button>
        </CardFooter>
      </Card>

      {/* Bundles */}
      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle>Add-Ons & Bundles</CardTitle>
          <div className="mt-2">
            <span className="text-3xl font-bold">From $29</span>
            <span className="text-muted-foreground">/month</span>
          </div>
          <div className="mt-3 p-2 bg-muted/50 rounded-lg text-center">
            <p className="text-xs text-muted-foreground">Self-Service</p>
            <p className="text-sm font-semibold">No sales call required</p>
          </div>
          <CardDescription className="mt-3">
            Enforcement tools, infrastructure upgrades, and operational add-ons.
            Bundle and save up to 57%.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-1">
          <ul className="space-y-2">
            {BUNDLES.map((bundle) => (
              <li key={bundle.id} className={`flex items-start gap-2 ${bundle.comingSoon ? 'opacity-70' : ''}`}>
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-sm">
                  <strong>{bundle.name}</strong>{!bundle.comingSoon ? (<> — {formatBundlePrice(bundle)}
                  <Badge variant="outline" className="ml-1 text-[10px] py-0">Save {bundle.savings}</Badge></>) : (
                  <Badge variant="outline" className="ml-1 text-[10px] py-0">Coming Soon</Badge>)}
                </span>
              </li>
            ))}
            <li className="flex items-start gap-2 opacity-70">
              <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span className="text-sm">Attribution Analytics <Badge variant="outline" className="ml-1 text-[10px] py-0">Coming Soon</Badge></span>
            </li>
            <li className="flex items-start gap-2 opacity-70">
              <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span className="text-sm">Formal Notice <Badge variant="outline" className="ml-1 text-[10px] py-0">Coming Soon</Badge></span>
            </li>
            <li className="flex items-start gap-2 opacity-70">
              <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span className="text-sm">Evidence Package <Badge variant="outline" className="ml-1 text-[10px] py-0">Coming Soon</Badge></span>
            </li>
          </ul>
        </CardContent>
        <CardFooter>
          <Button asChild className="w-full" variant="outline">
            <a href="/pricing">View All Add-Ons</a>
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
            {ENTERPRISE_TIER.features.slice(0, 5).map((feature: string) => (
              <li key={feature} className="flex items-start gap-2">
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-sm">{feature}</span>
              </li>
            ))}
            <li className="flex items-start gap-2">
              <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <span className="text-sm">+ {ENTERPRISE_TIER.exclusiveCapabilities.length} exclusive capabilities</span>
            </li>
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