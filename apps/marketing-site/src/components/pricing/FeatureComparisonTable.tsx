'use client';

import React from 'react';
import { Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { cn } from '@/lib/utils';

// Feature value type
type FeatureValue = string | boolean;

interface Feature {
  name: string;
  description: string;
  starter: FeatureValue;
  professional: FeatureValue;
  business: FeatureValue;
  enterprise: FeatureValue;
  highlight?: boolean;
}

interface FeatureCategory {
  name: string;
  features: Feature[];
}

// Feature definitions aligned with enterprise_api README.md
// Each feature maps to actual API functionality
const FEATURE_CATEGORIES: FeatureCategory[] = [
  {
    name: 'Core API',
    features: [
      {
        name: 'C2PA Document Signing',
        description: 'POST /api/v1/sign - Sign content with C2PA manifest (features gated by tier via options)',
        starter: '1K/mo',
        professional: 'Unlimited',
        business: 'Unlimited',
        enterprise: 'Unlimited',
      },
      {
        name: 'Advanced Signing Options',
        description: 'Sentence segmentation, attribution indexing, custom assertions via /sign options',
        starter: false,
        professional: true,
        business: true,
        enterprise: true,
      },
      {
        name: 'Content Verification',
        description: 'POST /api/v1/verify - Verify signed content (+ portal: GET /api/v1/verify/{document_id})',
        starter: 'Unlimited',
        professional: 'Unlimited',
        business: 'Unlimited',
        enterprise: 'Unlimited',
      },
      {
        name: 'Sentence Lookup',
        description: 'POST /api/v1/lookup - Lookup sentence provenance',
        starter: false,
        professional: '50K/mo',
        business: '500K/mo',
        enterprise: 'Unlimited',
      },
      {
        name: 'Usage Statistics',
        description: 'GET /api/v1/usage - API usage analytics',
        starter: '7 days',
        professional: '90 days',
        business: '1 year',
        enterprise: 'Unlimited',
      },
    ],
  },
  {
    name: 'Invisible Embeddings',
    features: [
      {
        name: 'Unicode Variation Selector Embeddings',
        description: 'Invisible cryptographic signatures in text',
        starter: true,
        professional: true,
        business: true,
        enterprise: true,
      },
      {
        name: 'Public Verification API',
        description: 'POST /api/v1/verify (no auth for basic, API key for Merkle proof)',
        starter: true,
        professional: true,
        business: true,
        enterprise: true,
      },
      {
        name: 'Batch Embedding Verification',
        description: 'POST /api/v1/public/verify/batch',
        starter: true,
        professional: true,
        business: true,
        enterprise: true,
      },
    ],
  },
  {
    name: 'Enterprise Features',
    features: [
      {
        name: 'Merkle Tree Encoding',
        description: 'POST /api/v1/enterprise/merkle/encode',
        starter: false,
        professional: '5K/mo',
        business: '10K/mo',
        enterprise: 'Unlimited',
      },
      {
        name: 'Source Attribution',
        description: 'POST /api/v1/verify/advanced (include_attribution=true)',
        starter: false,
        professional: '10K/mo',
        business: '50K/mo',
        enterprise: 'Unlimited',
      },
      {
        name: 'Similarity Detection',
        description: 'POST /api/v1/verify/advanced (detect_plagiarism=true)',
        starter: false,
        professional: false,
        business: '5K/mo',
        enterprise: 'Unlimited',
      },
      {
        name: 'Batch Operations',
        description: 'POST /api/v1/batch/sign & /api/v1/batch/verify (max 100 docs/request)',
        starter: false,
        professional: false,
        business: '1000/mo',
        enterprise: 'Unlimited',
      },
      {
        name: 'Custom C2PA Assertions',
        description: 'Define and validate custom assertion types',
        starter: false,
        professional: false,
        business: false,
        enterprise: true,
      },
      {
        name: 'C2PA Schema Registry',
        description: 'Register custom assertion schemas',
        starter: false,
        professional: false,
        business: false,
        enterprise: true,
      },
      {
        name: 'Assertion Templates',
        description: 'Pre-built templates for news, legal, academic',
        starter: false,
        professional: false,
        business: false,
        enterprise: true,
      },
    ],
  },
  {
    name: 'Streaming API',
    features: [
      {
        name: 'Streaming Signing',
        description: 'POST /api/v1/sign/stream - Stream signing progress (SSE)',
        starter: false,
        professional: true,
        business: true,
        enterprise: true,
      },
      {
        name: 'Chat Application Wrapper',
        description: 'POST /api/v1/chat/completions - OpenAI-compatible chat streaming',
        starter: false,
        professional: true,
        business: true,
        enterprise: true,
      },
      {
        name: 'Server-Sent Events',
        description: 'GET /api/v1/sign/stream/sessions/{session_id}/events - SSE endpoint',
        starter: false,
        professional: true,
        business: true,
        enterprise: true,
      },
    ],
  },
  {
    name: 'Platform & Limits',
    features: [
      {
        name: 'API Keys',
        description: 'Number of API keys per organization',
        starter: '2',
        professional: '10',
        business: '50',
        enterprise: 'Unlimited',
      },
      {
        name: 'Rate Limit',
        description: 'Requests per second',
        starter: '10/s',
        professional: '50/s',
        business: '200/s',
        enterprise: 'Unlimited',
      },
      {
        name: 'WordPress Plugin',
        description: 'Self-service WordPress integration',
        starter: 'Basic',
        professional: 'Pro (no branding)',
        business: 'Pro (no branding)',
        enterprise: 'White-label',
      },
      {
        name: 'Team Management',
        description: 'Multi-user organization access',
        starter: false,
        professional: false,
        business: '10 users',
        enterprise: 'Unlimited',
      },
      {
        name: 'Audit Logs',
        description: 'Complete audit trail for all operations',
        starter: false,
        professional: false,
        business: true,
        enterprise: true,
      },
      {
        name: 'Bring Your Own Keys (BYOK)',
        description: 'Use your own signing keys',
        starter: false,
        professional: true,
        business: true,
        enterprise: true,
      },
    ],
  },
  {
    name: 'Coalition & Revenue',
    features: [
      {
        name: 'Coalition Membership',
        description: 'Auto-join AI licensing coalition',
        starter: true,
        professional: true,
        business: true,
        enterprise: true,
      },
      {
        name: 'Your Revenue Share',
        description: 'Percentage of licensing revenue you keep',
        starter: 'Standard',
        professional: 'Enhanced',
        business: 'Premium',
        enterprise: 'Enterprise',
        highlight: true,
      },
    ],
  },
  {
    name: 'Support & SLA',
    features: [
      {
        name: 'Support Level',
        description: 'Response time and channel',
        starter: 'Community',
        professional: 'Email (48hr)',
        business: 'Priority (24hr)',
        enterprise: 'Dedicated TAM',
      },
      {
        name: 'SLA Guarantee',
        description: 'Uptime guarantee',
        starter: false,
        professional: false,
        business: '99.5%',
        enterprise: '99.9%',
      },
      {
        name: 'SSO/SCIM Integration',
        description: 'Enterprise identity management',
        starter: false,
        professional: false,
        business: false,
        enterprise: true,
      },
      {
        name: 'On-Premise Option',
        description: 'Self-hosted deployment',
        starter: false,
        professional: false,
        business: false,
        enterprise: true,
      },
    ],
  },
];

type TierId = 'starter' | 'professional' | 'business' | 'enterprise';

interface FeatureComparisonTableProps {
  currentPlan?: TierId | null;
  onUpgrade?: (tier: TierId) => void;
  showUpsell?: boolean;
}

function renderValue(value: string | boolean, isCurrentPlan: boolean, highlight?: boolean) {
  if (value === false) {
    return <X className="h-4 w-4 text-muted-foreground/50 mx-auto" />;
  }
  if (value === true) {
    return <Check className="h-4 w-4 text-primary mx-auto" />;
  }
  return (
    <span className={cn(
      'text-sm',
      highlight && 'font-bold text-primary',
      isCurrentPlan && 'font-semibold'
    )}>
      {value}
    </span>
  );
}

export default function FeatureComparisonTable({ 
  currentPlan, 
  onUpgrade,
  showUpsell = true 
}: FeatureComparisonTableProps) {
  const tiers: { id: TierId; name: string; price: string }[] = [
    { id: 'starter', name: 'Starter', price: 'Free' },
    { id: 'professional', name: 'Professional', price: '$99/mo' },
    { id: 'business', name: 'Business', price: '$499/mo' },
    { id: 'enterprise', name: 'Enterprise', price: 'Custom' },
  ];

  const tierOrder: TierId[] = ['starter', 'professional', 'business', 'enterprise'];
  const currentPlanIndex = currentPlan ? tierOrder.indexOf(currentPlan) : -1;

  const getUpsellText = (tierId: TierId): string | null => {
    if (!currentPlan || !showUpsell) return null;
    const tierIndex = tierOrder.indexOf(tierId);
    if (tierIndex <= currentPlanIndex) return null;
    if (tierIndex === currentPlanIndex + 1) return 'Upgrade';
    return null;
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse min-w-[800px]">
        <thead>
          <tr className="border-b-2 border-border">
            <th className="text-left py-4 px-4 font-semibold w-[280px]">Feature</th>
            {tiers.map((tier) => {
              const isCurrentPlan = currentPlan === tier.id;
              const upsellText = getUpsellText(tier.id);
              const isPopular = tier.id === 'professional';
              
              return (
                <th 
                  key={tier.id}
                  className={cn(
                    'text-center py-4 px-4 font-semibold relative border-l border-border',
                    isCurrentPlan && 'bg-primary/10 border-x-2 border-t-2 border-primary',
                    isPopular && !isCurrentPlan && 'bg-primary/5'
                  )}
                >
                  {isCurrentPlan && (
                    <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-xs">
                      Current Plan
                    </Badge>
                  )}
                  {isPopular && !isCurrentPlan && (
                    <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary/80 text-xs">
                      Recommended
                    </Badge>
                  )}
                  <div className="pt-2">
                    {tier.name}
                    <br />
                    <span className="text-xs font-normal text-muted-foreground">{tier.price}</span>
                  </div>
                  {upsellText && (
                    <Button 
                      size="sm" 
                      className="mt-2 text-xs h-7"
                      onClick={() => onUpgrade?.(tier.id)}
                    >
                      {upsellText}
                    </Button>
                  )}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody className="text-sm">
          {FEATURE_CATEGORIES.map((category) => (
            <React.Fragment key={category.name}>
              <tr className="bg-muted/50">
                <td className="py-3 px-4 font-bold text-foreground" colSpan={5}>
                  {category.name}
                </td>
              </tr>
              {category.features.map((feature) => (
                <tr key={feature.name} className="border-b border-border/50 hover:bg-muted/20">
                  <td className="py-3 px-4">
                    <div className="font-medium">{feature.name}</div>
                    <div className="text-xs text-muted-foreground">{feature.description}</div>
                  </td>
                  {tiers.map((tier) => {
                    const isCurrentPlan = currentPlan === tier.id;
                    const isPopular = tier.id === 'professional';
                    const value = feature[tier.id];
                    
                    return (
                      <td 
                        key={tier.id}
                        className={cn(
                          'text-center py-3 px-4 border-l border-border',
                          isCurrentPlan && 'bg-primary/10 border-x-2 border-primary',
                          isPopular && !isCurrentPlan && 'bg-primary/5'
                        )}
                      >
                        {renderValue(value, isCurrentPlan, feature.highlight)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </React.Fragment>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-t-2 border-border">
            <td className="py-4 px-4"></td>
            {tiers.map((tier) => {
              const isCurrentPlan = currentPlan === tier.id;
              const isPopular = tier.id === 'professional';
              const tierIndex = tierOrder.indexOf(tier.id);
              const isUpgrade = currentPlan && tierIndex > currentPlanIndex;
              
              return (
                <td 
                  key={tier.id}
                  className={cn(
                    'text-center py-4 px-4 border-l border-border',
                    isCurrentPlan && 'bg-primary/10 border-x-2 border-b-2 border-primary rounded-b-lg',
                    isPopular && !isCurrentPlan && 'bg-primary/5'
                  )}
                >
                  {isCurrentPlan ? (
                    <Button variant="outline" disabled className="w-full">
                      Current Plan
                    </Button>
                  ) : tier.id === 'enterprise' ? (
                    <Button variant="outline" className="w-full" asChild>
                      <Link href="/company#contact">Contact Sales</Link>
                    </Button>
                  ) : (
                    <Button 
                      variant={isUpgrade ? 'default' : 'outline'} 
                      className="w-full"
                      asChild
                    >
                      <Link href={`/signup?plan=${tier.id}`}>
                        {isUpgrade ? 'Upgrade' : 'Get Started'}
                      </Link>
                    </Button>
                  )}
                </td>
              );
            })}
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
