'use client';

import { useState } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
// Tabs import removed - using custom styled buttons for better active state visibility
import { AnimatePresence } from 'framer-motion';
import { ArrowRight, Check, Newspaper, BarChart3, Shield, FileText, Award, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import Link from 'next/link';
import SalesContactModal from '@/components/forms/SalesContactModal';
import AISummary from '@/components/seo/AISummary';
import FeatureComparisonTable from '@/components/pricing/FeatureComparisonTable';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import Image from 'next/image';
import { useLicense } from '@/lib/hooks/useLicense';
import { getAllTiers, formatPrice, formatRevShare, type TierConfig } from '@/lib/pricing-config';

// Dashboard URL for sign-up flows
const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypherai.com';

type ICP = 'publishers' | 'ai-labs' | 'enterprises';

// ICP-specific value propositions aligned with demos
const ICP_VALUE_PROPS: Record<ICP, { headline: string; subheadline: string; icon: typeof Newspaper }> = {
  publishers: {
    headline: 'Turn Your Archive Into Revenue',
    subheadline: 'Cryptographic watermarking that survives copy-paste. Formal notice capability for AI licensing.',
    icon: Newspaper,
  },
  'ai-labs': {
    headline: '"Google Analytics" for AI',
    subheadline: 'Performance intelligence + regulatory compliance. Building standards WITH you through C2PA. Meta, Google, and OpenAI are already members.',
    icon: BarChart3,
  },
  enterprises: {
    headline: 'AI Governance Infrastructure',
    subheadline: 'EU AI Act & China watermarking compliance with C2PA.',
    icon: Shield,
  },
};

// Marketing-specific tier descriptions for publishers
const TIER_MARKETING: Record<string, { description: string; bestFor: string; cta: { text: string; variant: 'default' | 'outline' }; showPrice: boolean; highlight?: string }> = {
  starter: {
    description: 'Get paid when AI uses your content',
    bestFor: 'Independent bloggers, local news, small sites, WordPress users',
    cta: { text: 'Get Started Free', variant: 'default' },
    showPrice: true,
    highlight: 'WordPress plugin installs in 5 minutes',
  },
  professional: {
    description: 'For regional publishers and growing media companies',
    bestFor: 'Regional newspapers, digital magazines, trade publications',
    cta: { text: 'Start Free Trial', variant: 'default' },
    showPrice: true,
    highlight: 'Invisible embeddings + enhanced revenue share',
  },
  business: {
    description: 'For major digital publishers needing enterprise features',
    bestFor: 'Major digital publishers, news networks',
    cta: { text: 'Start Free Trial', variant: 'default' },
    showPrice: true,
    highlight: 'Similarity detection + source attribution',
  },
  enterprise: {
    description: 'White-glove implementation',
    bestFor: 'NYT, Guardian, News Corp, major media conglomerates',
    cta: { text: 'Contact Sales', variant: 'default' },
    showPrice: false,
    highlight: 'Shape industry licensing standards',
  },
};

// Map license tier to TierId for feature comparison
type TierId = 'starter' | 'professional' | 'business' | 'enterprise';

function normalizeTier(tier: string | undefined): TierId | null {
  if (!tier) return null;
  const normalized = tier.toLowerCase();
  if (['starter', 'free', 'basic'].includes(normalized)) return 'starter';
  if (['professional', 'pro'].includes(normalized)) return 'professional';
  if (['business', 'team'].includes(normalized)) return 'business';
  if (['enterprise', 'custom'].includes(normalized)) return 'enterprise';
  return null;
}

export default function PricingPage() {
  const [activeICP, setActiveICP] = useState<ICP>('publishers');
  const [showPublisherModal, setShowPublisherModal] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [showEnterpriseModal, setShowEnterpriseModal] = useState(false);
  const [showFullFeatureTable, setShowFullFeatureTable] = useState(false);
  
  const router = useRouter();
  const { data: session } = useSession();
  const { license } = useLicense();
  
  // Get user's current plan for feature table highlighting
  const currentPlan = normalizeTier(license?.tier);
  const isLoggedIn = !!session;
  
  // Handle upgrade from feature table
  const handleUpgrade = (tier: TierId) => {
    if (tier === 'enterprise') {
      setShowPublisherModal(true);
    } else {
      router.push(`${DASHBOARD_URL}/billing?upgrade=${tier}`);
    }
  };
  
  const tiers = getAllTiers();

  return (
    <div className="bg-background text-foreground">
      {/* SEO: AI Summary with all ICP information for crawlers */}
      <AISummary
        title="Encypher Pricing & Licensing"
        whatWeDo="Encypher serves as Co-Chair of C2PA Text Provenance Task Force (c2pa.org). API and SDKs in Python, TypeScript, Go, and Rust for content authentication. Standard published January 8, 2026. Technology reviewed by C2PA members including Google, OpenAI, Adobe, and Microsoft."
        whoItsFor="Publishers seeking content licensing infrastructure and provable ownership. AI labs needing performance intelligence and quote integrity verification. Enterprises requiring EU AI Act and China watermarking compliance."
        keyDifferentiator="Cryptographic watermarking survives copy-paste and distribution. Provides technical infrastructure for content attribution and licensing. One API integration for entire publisher ecosystem."
        primaryValue="Start free, scale as you grow. Enterprise partners help shape industry-standard licensing frameworks for AI content usage."
      />

      {/* Hero Section with ICP Selector */}
      <section className="relative w-full py-12 md:py-16 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          {/* ICP Tab Selector - Vertical on mobile, horizontal on desktop */}
          <div className="flex justify-center mb-6 px-4">
            {/* Mobile: Vertical stack */}
            <div className="flex flex-col sm:hidden gap-2 w-full max-w-xs">
              {(['publishers', 'ai-labs', 'enterprises'] as const).map((icp) => {
                const isActive = activeICP === icp;
                const config = {
                  publishers: { icon: Newspaper, label: 'Publishers' },
                  'ai-labs': { icon: BarChart3, label: 'AI Labs' },
                  enterprises: { icon: Shield, label: 'Enterprises' },
                }[icp];
                const IconComponent = config.icon;
                return (
                  <button
                    key={icp}
                    onClick={() => setActiveICP(icp)}
                    className="flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium transition-all text-sm"
                    style={isActive ? {
                      backgroundColor: '#2a87c4',
                      color: '#ffffff',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    } : {
                      backgroundColor: '#e2e8f0',
                      color: '#64748b'
                    }}
                  >
                    <IconComponent className="h-4 w-4" />
                    <span>{config.label}</span>
                  </button>
                );
              })}
            </div>
            {/* Desktop: Horizontal tabs */}
            <div className="hidden sm:inline-flex rounded-lg p-1.5 gap-1" style={{ backgroundColor: '#e2e8f0' }}>
              {(['publishers', 'ai-labs', 'enterprises'] as const).map((icp) => {
                const isActive = activeICP === icp;
                const config = {
                  publishers: { icon: Newspaper, label: 'Publishers' },
                  'ai-labs': { icon: BarChart3, label: 'AI Labs' },
                  enterprises: { icon: Shield, label: 'Enterprises' },
                }[icp];
                const IconComponent = config.icon;
                return (
                  <button
                    key={icp}
                    onClick={() => setActiveICP(icp)}
                    className="flex items-center justify-center gap-2 py-3 px-6 rounded-md font-medium transition-all text-sm"
                    style={isActive ? {
                      backgroundColor: '#2a87c4',
                      color: '#ffffff',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    } : {
                      color: '#64748b'
                    }}
                  >
                    <IconComponent className="h-4 w-4" />
                    <span>{config.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Dynamic Value Prop based on active ICP */}
          <div className="text-center">
            {(() => {
              const props = ICP_VALUE_PROPS[activeICP];
              const IconComponent = props.icon;
              return (
                <>
                  <div className="flex justify-center mb-4">
                    <div className="p-3 bg-primary/10 rounded-full">
                      <IconComponent className="h-8 w-8 text-primary" />
                    </div>
                  </div>
                  <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight mb-4">
                    {props.headline}
                  </h1>
                  <p className="text-lg md:text-xl max-w-2xl mx-auto text-muted-foreground">
                    {props.subheadline}
                  </p>
                </>
              );
            })()}
          </div>

          {/* C2PA Co-Chair Authority Badge - Single source of standards authority */}
          <div className="flex justify-center mt-8 px-4">
            <div className="inline-flex items-center gap-2 px-3 md:px-4 py-2 bg-primary/10 border border-primary/20 rounded-full">
              <Award className="h-4 w-4 text-primary flex-shrink-0" />
              <span className="text-xs md:text-sm font-medium text-center">
                <span className="hidden md:inline">C2PA Text Provenance Co-Chair — Building standards with Google, BBC, OpenAI, Adobe & Microsoft</span>
                <span className="md:hidden">C2PA Co-Chair with Google, BBC, OpenAI, Adobe</span>
              </span>
            </div>
          </div>

          {/* C2PA & CAI Logos - Standards Authority */}
          <div className="mt-4 flex justify-center items-center gap-6 md:gap-10">
            <div className="relative h-8 w-24 md:h-10 md:w-32">
              <Image
                src="/c2pa-hero.svg"
                alt="C2PA Logo"
                fill
                style={{objectFit: 'contain'}}
              />
            </div>
            <div className="relative h-8 w-24 md:h-10 md:w-32">
              <Image
                src="/CAI_Lockup_RGB_Black.svg"
                alt="Content Authenticity Initiative Logo"
                fill
                style={{objectFit: 'contain'}}
              />
            </div>
          </div>

        </div>
      </section>

      {/* 
        SEO NOTE: All three sections are rendered in the DOM but only one is visible.
        This ensures crawlers index all content while users see a clean tabbed interface.
        Using CSS visibility/display instead of conditional rendering.
      */}

      {/* ==================== PUBLISHERS SECTION ==================== */}
      <section 
        id="publishers" 
        className={`py-12 w-full ${activeICP === 'publishers' ? 'block' : 'hidden'}`}
        aria-hidden={activeICP !== 'publishers'}
      >
        <div className="container mx-auto px-4">

          {/* Publisher Pricing Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto mb-16">
            {tiers.map((tier: TierConfig) => {
              const marketing = TIER_MARKETING[tier.id];
              const isPopular = tier.popular;
              
              return (
                <div 
                  key={tier.id}
                  className={`bg-card rounded-lg p-6 relative flex flex-col ${
                    isPopular 
                      ? 'border-2 border-primary/50 shadow-lg' 
                      : 'border border-border'
                  }`}
                >
                  {isPopular && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                      <span 
                        className="inline-block px-4 py-1.5 text-sm font-semibold rounded-full shadow-md"
                        style={{ backgroundColor: '#2a87c4', color: '#ffffff' }}
                      >
                        Recommended
                      </span>
                    </div>
                  )}
                  
                  {/* Tier Name & Description - Fixed height */}
                  <div className="h-[72px] mb-4">
                    <h3 className="text-xl font-bold mb-2">{tier.name}</h3>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {marketing.description}
                    </p>
                  </div>

                  {/* Price Section - Fixed height with centered content */}
                  <div className="h-[72px] mb-4 flex flex-col justify-center items-center text-center">
                    <div className="text-3xl font-bold">
                      {marketing.showPrice ? formatPrice(tier) : 'Custom'}
                    </div>
                    {marketing.showPrice && tier.price.monthly > 0 && (
                      <p className="text-sm text-muted-foreground">/month</p>
                    )}
                    {marketing.showPrice && tier.price.monthly === 0 && (
                      <p className="text-sm text-muted-foreground">Forever free</p>
                    )}
                    {!marketing.showPrice && (
                      <p className="text-sm text-muted-foreground">White-glove implementation</p>
                    )}
                  </div>

                  {/* Coalition Rev Share Badge - Fixed height */}
                  <div className="h-[60px] bg-primary/10 rounded-lg p-3 mb-4 flex flex-col justify-center items-center text-center">
                    <p className="text-xs text-muted-foreground">Coalition Revenue</p>
                    <p className="text-sm font-semibold text-primary">
                      {tier.enterprise ? 'Best terms available' : 
                       tier.id === 'business' ? 'Premium revenue share' :
                       tier.id === 'professional' ? 'Enhanced revenue share' :
                       'Standard revenue share'}
                    </p>
                  </div>

                  {/* Features List - Fixed height */}
                  <ul className="h-[180px] space-y-2 mb-4">
                    {tier.features.slice(0, 6).map((feature) => (
                      <li key={feature} className="flex items-start gap-2">
                        <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* Highlight callout - Fixed height */}
                  <div className="h-[48px] mb-4 flex items-center justify-center">
                    {marketing.highlight && (
                      <div className="py-2 px-3 bg-muted/50 rounded text-xs text-center font-medium w-full">
                        {marketing.highlight}
                      </div>
                    )}
                  </div>

                  {/* Best for section - Fixed height */}
                  <div className="h-[56px] mb-4 pt-4 border-t border-border">
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      <strong>Best for:</strong> {marketing.bestFor}
                    </p>
                  </div>

                  {/* CTA Button - Auto pushed to bottom */}
                  <div className="mt-auto">
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
                        <Link href={`/auth/signin?mode=signup&source=pricing-${tier.id}`}>
                          {marketing.cta.text} <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Key Differentiators - Quick Overview */}
          <div className="max-w-5xl mx-auto mb-12">
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-card border border-border rounded-lg p-6 text-center">
                <div className="p-3 bg-primary/10 rounded-full w-fit mx-auto mb-4">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <h4 className="font-bold mb-2">Survives Copy-Paste</h4>
                <p className="text-sm text-muted-foreground">
                  Cryptographic watermarking embedded in text travels with your content across the web.
                </p>
              </div>
              <div className="bg-card border border-border rounded-lg p-6 text-center">
                <div className="p-3 bg-primary/10 rounded-full w-fit mx-auto mb-4">
                  <FileText className="h-6 w-6 text-primary" />
                </div>
                <h4 className="font-bold mb-2">Formal Notice Capability</h4>
                <p className="text-sm text-muted-foreground">
                  Sentence-level tracking enables legal notice to AI companies with mathematical proof.
                </p>
              </div>
              <div className="bg-card border border-border rounded-lg p-6 text-center">
                <div className="p-3 bg-primary/10 rounded-full w-fit mx-auto mb-4">
                  <Clock className="h-6 w-6 text-primary" />
                </div>
                <h4 className="font-bold mb-2">30-Day Implementation</h4>
                <p className="text-sm text-muted-foreground">
                  Enterprise: $30k implementation in 30 days. WordPress plugin: install in 5 minutes.
                </p>
              </div>
            </div>
          </div>

          {/* Publisher Value Prop */}
          <div className="max-w-4xl mx-auto bg-primary/5 border-2 border-primary/20 rounded-lg p-8 mb-12">
            <h3 className="text-2xl font-bold mb-4 text-center">The Publisher Opportunity</h3>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <p className="text-sm text-muted-foreground mb-2">Without Content Provenance:</p>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">AI training attribution</span>
                    <span className="font-semibold text-destructive">None</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Licensing revenue</span>
                    <span className="font-semibold">$0</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Formal notice capability</span>
                    <span className="font-semibold text-destructive">Impossible</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Content after copy-paste</span>
                    <span className="font-semibold text-destructive">Untraceable</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-border">
                    <span className="font-bold">Net result</span>
                    <span className="font-bold text-destructive">Lost opportunity</span>
                  </div>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-2">With Encypher:</p>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">AI training attribution</span>
                    <span className="font-semibold text-primary">C2PA verified</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Licensing revenue</span>
                    <span className="font-semibold text-primary">$1M+</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Formal notice capability</span>
                    <span className="font-semibold text-primary">Enabled</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Content after copy-paste</span>
                    <span className="font-semibold text-primary">Still provable</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-border">
                    <span className="font-bold">Net result</span>
                    <span className="font-bold text-primary">New revenue stream</span>
                  </div>
                </div>
              </div>
            </div>
            <p className="text-sm text-center text-muted-foreground mt-6">
              Success-based model means you keep the majority of licensing revenue. We only win when you win.
            </p>
          </div>

          {/* Enterprise Engagement - Shape Industry Standards */}
          <div className="max-w-3xl mx-auto bg-muted/50 border border-border rounded-lg p-6 mb-12 text-center">
            <Badge variant="outline" className="mb-3">Enterprise</Badge>
            <h4 className="font-bold text-lg mb-2">Shape Industry Licensing Standards</h4>
            <p className="text-sm text-muted-foreground mb-4">
              Enterprise partners work with Encypher to establish industry-standard licensing frameworks for AI content usage. The organizations engaged today are setting the standards others will follow.
            </p>
            <Button onClick={() => setShowPublisherModal(true)} variant="outline" size="sm">
              Discuss Enterprise Engagement <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>

          {/* Quick Comparison Table */}
          <div className="max-w-5xl mx-auto mb-12">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b-2 border-border">
                    <th className="text-left py-3 px-2 md:px-4 font-semibold whitespace-nowrap">Feature</th>
                    <th className="text-center py-3 px-2 md:px-4 font-semibold whitespace-nowrap">Starter<br/><span className="text-xs font-normal text-muted-foreground">Free</span></th>
                    <th className="text-center py-3 px-2 md:px-4 font-semibold whitespace-nowrap bg-primary/5">Pro<br/><span className="text-xs font-normal text-muted-foreground">$99/mo</span></th>
                    <th className="text-center py-3 px-2 md:px-4 font-semibold whitespace-nowrap">Business<br/><span className="text-xs font-normal text-muted-foreground">$499/mo</span></th>
                    <th className="text-center py-3 px-2 md:px-4 font-semibold whitespace-nowrap">Enterprise<br/><span className="text-xs font-normal text-muted-foreground">Custom</span></th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-border/50">
                    <td className="py-3 px-2 md:px-4 font-medium whitespace-nowrap">C2PA Signing</td>
                    <td className="text-center py-3 px-2 md:px-4">10K/mo</td>
                    <td className="text-center py-3 px-2 md:px-4 bg-primary/5">Unlimited</td>
                    <td className="text-center py-3 px-2 md:px-4">Unlimited</td>
                    <td className="text-center py-3 px-2 md:px-4">Unlimited</td>
                  </tr>
                  <tr className="border-b border-border/50">
                    <td className="py-3 px-2 md:px-4 font-medium whitespace-nowrap">Embeddings</td>
                    <td className="text-center py-3 px-2 md:px-4 text-muted-foreground">—</td>
                    <td className="text-center py-3 px-2 md:px-4 bg-primary/5"><Check className="h-4 w-4 text-primary mx-auto" /></td>
                    <td className="text-center py-3 px-2 md:px-4"><Check className="h-4 w-4 text-primary mx-auto" /></td>
                    <td className="text-center py-3 px-2 md:px-4"><Check className="h-4 w-4 text-primary mx-auto" /></td>
                  </tr>
                  <tr className="border-b border-border/50">
                    <td className="py-3 px-2 md:px-4 font-medium whitespace-nowrap">Tracking</td>
                    <td className="text-center py-3 px-2 md:px-4 text-muted-foreground">—</td>
                    <td className="text-center py-3 px-2 md:px-4 bg-primary/5">50K/mo</td>
                    <td className="text-center py-3 px-2 md:px-4">500K/mo</td>
                    <td className="text-center py-3 px-2 md:px-4">Unlimited</td>
                  </tr>
                  <tr className="border-b border-border/50">
                    <td className="py-3 px-2 md:px-4 font-medium whitespace-nowrap">WordPress</td>
                    <td className="text-center py-3 px-2 md:px-4">Basic</td>
                    <td className="text-center py-3 px-2 md:px-4 bg-primary/5">Pro</td>
                    <td className="text-center py-3 px-2 md:px-4">Pro</td>
                    <td className="text-center py-3 px-2 md:px-4">White-label</td>
                  </tr>
                  <tr className="border-b border-border/50 bg-muted/30">
                    <td className="py-3 px-2 md:px-4 font-bold whitespace-nowrap">Revenue Share</td>
                    <td className="text-center py-3 px-2 md:px-4 font-medium text-sm">Standard</td>
                    <td className="text-center py-3 px-2 md:px-4 bg-primary/5 font-medium text-primary text-sm">Enhanced</td>
                    <td className="text-center py-3 px-2 md:px-4 font-medium text-sm">Premium</td>
                    <td className="text-center py-3 px-2 md:px-4 font-medium text-sm">Best</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="text-xs text-muted-foreground mt-3 text-center max-w-3xl mx-auto">
              Coalition revenue is paid when AI companies license the corpus. Your share increases with higher tiers. Specific terms discussed during consultation.
            </p>
          </div>

          {/* Collapsible Full Feature Table */}
          <div className="max-w-6xl mx-auto">
            <button
              onClick={() => setShowFullFeatureTable(!showFullFeatureTable)}
              className="w-full flex items-center justify-center gap-2 py-3 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              {showFullFeatureTable ? (
                <>Hide full feature comparison <ChevronUp className="h-4 w-4" /></>
              ) : (
                <>Show all 28 features <ChevronDown className="h-4 w-4" /></>
              )}
            </button>
            
            {showFullFeatureTable && (
              <div className="mt-4">
                <p className="text-center text-muted-foreground mb-6 text-sm">
                  Every feature maps directly to our Enterprise API. See{' '}
                  <Link href="https://api.encypherai.com/docs" className="text-primary hover:underline">API documentation</Link> for details.
                </p>
                <FeatureComparisonTable 
                  currentPlan={currentPlan}
                  showUpsell={isLoggedIn}
                  onUpgrade={handleUpgrade}
                />
              </div>
            )}
          </div>

          {/* What is Content Provenance - Beginner Explainer */}
          <div className="max-w-3xl mx-auto mt-16 p-6 bg-muted/30 rounded-lg">
            <h4 className="font-bold text-lg mb-3">New to content provenance?</h4>
            <p className="text-sm text-muted-foreground mb-4">
              <strong>Content provenance</strong> is cryptographic proof that you created your content. 
              When AI companies scrape the web for training data, they currently can't tell who owns what. 
              Our technology embeds invisible, tamper-proof signatures directly into your text that:
            </p>
            <ul className="text-sm text-muted-foreground space-y-2 mb-4">
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span><strong>Survive copy-paste</strong> — Your proof travels with your content</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span><strong>Enable licensing</strong> — AI companies can identify and pay you</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span><strong>Are invisible</strong> — Readers see nothing different</span>
              </li>
            </ul>
            <p className="text-sm text-muted-foreground">
              Built on <strong>C2PA</strong>, the same standard used by NYT, BBC, Adobe, and Google. 
              We co-authored the text specification.
            </p>
          </div>
        </div>
      </section>

      {/* ==================== AI LABS SECTION ==================== */}
      <section 
        id="ai-labs" 
        className={`py-12 w-full ${activeICP === 'ai-labs' ? 'block' : 'hidden'}`}
        aria-hidden={activeICP !== 'ai-labs'}
      >
        <div className="container mx-auto px-4">
          {/* The Problem - aligned with AI Demo Section 1 */}
          <div className="max-w-4xl mx-auto mb-12 text-center">
            <p className="text-lg text-muted-foreground mb-2">The Problem</p>
            <h2 className="text-2xl md:text-3xl font-bold mb-4">
              You spend <span className="text-primary">$2.7B per model</span> with zero performance analytics.
            </h2>
            <p className="text-muted-foreground">
              No visibility into which training data drives real-world performance. No way to optimize R&D spend.
            </p>
          </div>

          <div className="max-w-5xl mx-auto">
            <div className="grid md:grid-cols-2 gap-8 mb-12">
              {/* Performance Intelligence */}
              <div className="bg-card rounded-lg border border-border p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <BarChart3 className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-bold">Performance Intelligence</h3>
                </div>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">Sentence-level analytics on all outputs</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">Track which parameters drive viral performance</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">Real-world feedback loop for R&D optimization</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">Publisher ecosystem performance data</span>
                  </li>
                </ul>
              </div>

              {/* Regulatory Compliance */}
              <div className="bg-card rounded-lg border border-border p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Shield className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-bold">Regulatory Compliance</h3>
                </div>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">EU AI Act compliant infrastructure</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">China watermarking mandate ready</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">C2PA standard (Adobe, Microsoft, Google)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">Publisher coalition licensing access</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* CTA Card */}
            <div className="bg-primary/5 border-2 border-primary/20 rounded-lg p-8 text-center">
              <h3 className="text-2xl font-bold mb-2">Custom Enterprise Licensing</h3>
              <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
                Annual licensing tailored to your scale. One integration covers the entire publisher ecosystem.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button 
                  onClick={() => setShowAIModal(true)}
                  size="lg"
                >
                  Schedule Technical Evaluation <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link href="/ai-demo">
                    See Interactive Demo <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </div>
          </div>

          {/* Standards Footer */}
          <div className="max-w-3xl mx-auto mt-12">
            <p className="text-sm text-muted-foreground mb-4 text-center">Built on global standards</p>
            <div className="flex flex-wrap justify-center gap-8">
              <div className="flex items-center gap-2">
                <span className="font-bold text-primary">C2PA</span>
                <span className="text-sm text-muted-foreground">Standard</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-primary">EU AI Act</span>
                <span className="text-sm text-muted-foreground">Compliant</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-primary">China</span>
                <span className="text-sm text-muted-foreground">Watermarking Ready</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ==================== ENTERPRISES SECTION ==================== */}
      <section 
        id="enterprises" 
        className={`py-12 w-full ${activeICP === 'enterprises' ? 'block' : 'hidden'}`}
        aria-hidden={activeICP !== 'enterprises'}
      >
        <div className="container mx-auto px-4">
          {/* Regulatory Context */}
          <div className="max-w-4xl mx-auto mb-12 text-center">
            <p className="text-lg text-muted-foreground mb-2">The Regulatory Reality</p>
            <h2 className="text-2xl md:text-3xl font-bold mb-4">
              EU AI Act & China watermarking mandates are here.
            </h2>
            <p className="text-muted-foreground">
              Turn compliance requirements into competitive advantage with C2PA infrastructure.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-12">
            {/* Pilot */}
            <div className="bg-card rounded-lg border border-border p-6">
              <h3 className="text-xl font-bold mb-2">Pilot</h3>
              <p className="text-sm text-muted-foreground mb-4">Validate value with limited deployment</p>
              
              <div className="mb-6">
                <div className="text-2xl font-bold mb-1">Contact Us</div>
                <p className="text-xs text-muted-foreground">30-60 day evaluation period</p>
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
                  <span>Success metrics defined</span>
                </li>
              </ul>

              <Button 
                onClick={() => setShowEnterpriseModal(true)}
                className="w-full"
              >
                Start Pilot
              </Button>
            </div>

            {/* Production */}
            <div className="bg-card rounded-lg border-2 border-primary/50 p-6">
              <Badge className="mb-4 bg-primary">Recommended</Badge>
              <h3 className="text-xl font-bold mb-2">Production</h3>
              <p className="text-sm text-muted-foreground mb-4">Full-scale deployment with enhanced features</p>
              
              <div className="mb-6">
                <div className="text-2xl font-bold mb-1">Custom Pricing</div>
                <p className="text-xs text-muted-foreground">Based on volume and requirements</p>
              </div>

              <ul className="space-y-2 text-sm mb-6">
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Everything in Pilot</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Sentence-level tracking</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Intelligence dashboards</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Priority support (24hr SLA)</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Quarterly business reviews</span>
                </li>
              </ul>

              <Button 
                onClick={() => setShowEnterpriseModal(true)}
                className="w-full"
              >
                Contact Sales <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>

            {/* Strategic */}
            <div className="bg-card rounded-lg border border-border p-6">
              <h3 className="text-xl font-bold mb-2">Strategic</h3>
              <p className="text-sm text-muted-foreground mb-4">Partnership-level engagement</p>
              
              <div className="mb-6">
                <div className="text-2xl font-bold mb-1">Custom</div>
                <p className="text-xs text-muted-foreground">Multi-year strategic partnership</p>
              </div>

              <ul className="space-y-2 text-sm mb-6">
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Everything in Production</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Dedicated account team</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Custom feature development</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>On-premise deployment option</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Advisory board participation</span>
                </li>
              </ul>

              <Button 
                onClick={() => setShowEnterpriseModal(true)}
                className="w-full"
              >
                Discuss Partnership
              </Button>
            </div>
          </div>

          {/* Enterprise Value Prop */}
          <div className="max-w-4xl mx-auto bg-muted/30 rounded-lg p-8">
            <h3 className="text-2xl font-bold mb-6 text-center">EU AI Act Compliance + Competitive Advantage</h3>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h4 className="font-bold mb-3">Compliance Baseline</h4>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5" />
                    <span>C2PA-compliant content provenance</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5" />
                    <span>Audit trails for AI-generated content</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5" />
                    <span>Regulatory reporting dashboards</span>
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="font-bold mb-3">Competitive Advantage</h4>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5" />
                    <span>Performance intelligence on AI outputs</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5" />
                    <span>Content attribution and licensing</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5" />
                    <span>Publisher ecosystem compatibility</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
          <div className="max-w-3xl mx-auto mt-8 text-center text-sm text-muted-foreground">
            <p>
              Building on Encypher? Enterprise SaaS and non-publisher platforms can start with a free Starter account to test the API today.
              OEM and non-publisher licensing is handled through custom Enterprise agreements — contact our team to discuss terms.
            </p>
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

      {/* C2PA Member Company Logo Scroller */}
      <StandardsCompliance />
    </div>
  );
}
