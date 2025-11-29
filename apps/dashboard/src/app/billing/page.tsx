'use client';

import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@encypher/design-system';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { useState, useMemo } from 'react';
import { toast } from 'sonner';
import apiClient, { PlanInfo, Invoice, BillingUsageStats, CoalitionSummary } from '../../lib/api';
import { DashboardLayout } from '../../components/layout/DashboardLayout';

// Fallback plans when billing service is unavailable
const FALLBACK_PLANS: PlanInfo[] = [
  {
    id: 'starter',
    name: 'Starter',
    tier: 'starter',
    price_monthly: 0,
    price_annual: 0,
    features: [
      '1,000 API calls/month',
      '10 documents/month',
      'C2PA-compliant signing',
      'Basic verification',
      'Community support',
    ],
    limits: { api_calls: 1000, documents: 10 },
    coalition_rev_share: { publisher: 65, encypher: 35 },
  },
  {
    id: 'professional',
    name: 'Professional',
    tier: 'professional',
    price_monthly: 49,
    price_annual: 470,
    features: [
      '25,000 API calls/month',
      '500 documents/month',
      'C2PA-compliant signing',
      'Advanced verification',
      'Priority email support',
      'Custom metadata fields',
      'API analytics dashboard',
    ],
    limits: { api_calls: 25000, documents: 500 },
    coalition_rev_share: { publisher: 70, encypher: 30 },
    popular: true,
  },
  {
    id: 'business',
    name: 'Business',
    tier: 'business',
    price_monthly: 199,
    price_annual: 1910,
    features: [
      '100,000 API calls/month',
      '2,500 documents/month',
      'C2PA-compliant signing',
      'Team management (5 seats)',
      'Role-based permissions',
      'Dedicated support',
      'Custom branding',
      'Audit logs & compliance',
    ],
    limits: { api_calls: 100000, documents: 2500 },
    coalition_rev_share: { publisher: 75, encypher: 25 },
  },
];

export default function BillingPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

  // Fetch plans from API
  const plansQuery = useQuery({
    queryKey: ['plans'],
    queryFn: () => apiClient.getPlans(),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  // Fetch subscription, invoices, usage, and coalition data
  const billingQuery = useQuery({
    queryKey: ['billing', accessToken],
    queryFn: async () => {
      if (!accessToken) return { subscription: null, invoices: [], usage: null, coalition: null };
      const [subscription, invoices, usage, coalition] = await Promise.all([
        apiClient.getSubscription(accessToken).catch(() => null),
        apiClient.getInvoices(accessToken).catch(() => []),
        apiClient.getBillingUsage(accessToken).catch(() => null),
        apiClient.getCoalitionEarnings(accessToken).catch(() => null),
      ]);
      return { subscription, invoices, usage, coalition };
    },
    enabled: Boolean(accessToken),
  });

  // Upgrade mutation - redirects to Stripe Checkout
  const upgradeMutation = useMutation({
    mutationFn: async ({ tier, cycle }: { tier: string; cycle: 'monthly' | 'annual' }) => {
      if (!accessToken) throw new Error('You must be signed in to upgrade.');
      const response = await apiClient.upgradeSubscription(accessToken, tier, cycle);
      return response;
    },
    onSuccess: (response) => {
      if (response.checkout_url) {
        // Redirect to Stripe Checkout
        window.location.href = response.checkout_url;
      } else if (response.success) {
        toast.success(response.message);
        billingQuery.refetch();
      } else {
        toast.info(response.message);
      }
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Failed to upgrade plan.');
    },
  });

  // Manage billing portal
  const portalMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      return apiClient.getBillingPortal(accessToken);
    },
    onSuccess: (response) => {
      window.location.href = response.portal_url;
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Failed to open billing portal.');
    },
  });

  // Filter plans based on billing cycle, use fallback if API fails
  const plans = useMemo(() => {
    const allPlans = plansQuery.data && plansQuery.data.length > 0 
      ? plansQuery.data 
      : FALLBACK_PLANS;
    return allPlans.filter(p => !p.enterprise); // Exclude enterprise (custom pricing)
  }, [plansQuery.data]);

  const subscription = billingQuery.data?.subscription;
  const invoices = billingQuery.data?.invoices || [];
  const usage = billingQuery.data?.usage;
  const coalition = billingQuery.data?.coalition;
  const currentTier = subscription?.tier || 'starter';
  const isLoading = status === 'loading' || billingQuery.isLoading || plansQuery.isLoading;

  // Get price based on billing cycle
  const getPrice = (plan: PlanInfo) => {
    return billingCycle === 'annual' ? plan.price_annual : plan.price_monthly;
  };

  const getPeriod = () => billingCycle === 'annual' ? 'year' : 'month';

  // Format date
  const formatDate = (dateStr: string) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-delft-blue dark:text-white mb-2">Billing & Subscription</h2>
          <p className="text-muted-foreground">
            Manage your plan, payment methods, and download invoices for your records.
          </p>
        </div>

        {/* Current Plan Card */}
        <Card className="border-columbia-blue">
          <CardHeader>
            <CardTitle>Current Plan</CardTitle>
            <CardDescription>
              {isLoading ? 'Loading plan information…' : subscription?.plan_name || 'Starter (Free)'}
            </CardDescription>
          </CardHeader>
          <CardContent className="grid md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Plan</p>
              <p className="text-2xl font-bold text-delft-blue dark:text-white">
                {subscription?.plan_name || 'Starter'}
              </p>
              <p className="text-muted-foreground">
                {subscription ? `$${subscription.amount}/${subscription.billing_cycle === 'annual' ? 'year' : 'month'}` : 'Free'}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Status</p>
              <p className="text-foreground capitalize">{subscription?.status || 'Active'}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Renews</p>
              <p className="text-foreground">
                {subscription?.current_period_end ? formatDate(subscription.current_period_end) : '—'}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Coalition Rev Share</p>
              <p className="text-foreground">
                {subscription?.coalition_rev_share 
                  ? `${subscription.coalition_rev_share.publisher}% you / ${subscription.coalition_rev_share.encypher}% Encypher`
                  : '65% you / 35% Encypher'}
              </p>
            </div>
          </CardContent>
          {subscription && (
            <div className="px-6 pb-6">
              <Button
                variant="outline"
                onClick={() => portalMutation.mutate()}
                disabled={portalMutation.isPending}
              >
                {portalMutation.isPending ? 'Opening...' : 'Manage Billing'}
              </Button>
            </div>
          )}
        </Card>

        {/* Usage Statistics */}
        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Usage This Period</CardTitle>
              <CardDescription>
                {isLoading ? (
                  <span className="inline-block h-4 w-32 bg-muted animate-pulse rounded" />
                ) : usage ? (
                  `Resets ${formatDate(usage.reset_date)}`
                ) : (
                  'No billing period active'
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {isLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="space-y-2">
                      <div className="flex justify-between">
                        <span className="h-4 w-24 bg-muted animate-pulse rounded" />
                        <span className="h-4 w-16 bg-muted animate-pulse rounded" />
                      </div>
                      <div className="h-2 bg-muted rounded-full" />
                    </div>
                  ))}
                </div>
              ) : usage?.metrics ? (
                Object.entries(usage.metrics).map(([key, metric]) => (
                  <div key={key} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">{metric.name}</span>
                      <span className="font-medium">
                        {metric.used.toLocaleString()} / {metric.limit === 'unlimited' ? '∞' : metric.limit.toLocaleString()}
                      </span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full transition-all ${
                          metric.percentage_used > 90 ? 'bg-red-500' :
                          metric.percentage_used > 70 ? 'bg-yellow-500' :
                          'bg-blue-ncs'
                        }`}
                        style={{ width: `${Math.min(metric.percentage_used, 100)}%` }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex flex-col items-center py-6 text-center">
                  <div className="w-12 h-12 mb-3 rounded-full bg-muted flex items-center justify-center">
                    <svg className="w-6 h-6 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <p className="text-muted-foreground text-sm">No usage data yet</p>
                  <p className="text-muted-foreground text-xs mt-1">Start using the API to see your metrics</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Coalition Earnings</CardTitle>
              <CardDescription>
                {isLoading ? (
                  <span className="inline-block h-4 w-32 bg-muted animate-pulse rounded" />
                ) : coalition ? (
                  `${coalition.publisher_share_percent}% revenue share`
                ) : (
                  'Join the coalition to earn'
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {isLoading ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="block h-4 w-20 bg-muted animate-pulse rounded mb-2" />
                      <span className="block h-8 w-24 bg-muted animate-pulse rounded" />
                    </div>
                    <div>
                      <span className="block h-4 w-20 bg-muted animate-pulse rounded mb-2" />
                      <span className="block h-8 w-24 bg-muted animate-pulse rounded" />
                    </div>
                  </div>
                </div>
              ) : coalition ? (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Earnings</p>
                      <p className="text-2xl font-bold text-delft-blue dark:text-white">
                        ${coalition.total_earnings.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Pending</p>
                      <p className="text-2xl font-bold text-green-600">
                        ${coalition.pending_earnings.toFixed(2)}
                      </p>
                    </div>
                  </div>
                  <div className="pt-2 border-t">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Content in Coalition</span>
                      <span className="font-medium">{coalition.total_content.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm mt-1">
                      <span className="text-muted-foreground">Payout Account</span>
                      <span className={coalition.payout_account_connected ? 'text-green-600' : 'text-yellow-600'}>
                        {coalition.payout_account_connected ? 'Connected' : 'Not Connected'}
                      </span>
                    </div>
                  </div>
                  {!coalition.payout_account_connected && (
                    <Button
                      variant="outline"
                      fullWidth
                      onClick={() => {
                        // TODO: Redirect to Stripe Connect onboarding
                        toast.info('Stripe Connect onboarding coming soon');
                      }}
                    >
                      Connect Payout Account
                    </Button>
                  )}
                </>
              ) : (
                <div className="flex flex-col items-center py-6 text-center">
                  <div className="w-12 h-12 mb-3 rounded-full bg-muted flex items-center justify-center">
                    <svg className="w-6 h-6 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-muted-foreground text-sm">No earnings yet</p>
                  <p className="text-muted-foreground text-xs mt-1">Sign content to start earning</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Change Plan Section */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-semibold text-delft-blue dark:text-white">Change plan</h3>
              <p className="text-muted-foreground">Scale with usage. Upgrade or downgrade any time.</p>
            </div>
            <div className="flex bg-muted rounded-full p-1">
              <button
                className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                  billingCycle === 'monthly' ? 'bg-white dark:bg-slate-700 shadow text-foreground' : 'text-muted-foreground'
                }`}
                onClick={() => setBillingCycle('monthly')}
              >
                Monthly
              </button>
              <button
                className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                  billingCycle === 'annual' ? 'bg-white dark:bg-slate-700 shadow text-foreground' : 'text-muted-foreground'
                }`}
                onClick={() => setBillingCycle('annual')}
              >
                Annual <span className="text-xs">(save 20%)</span>
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            {plans.map((plan) => {
              const isCurrent = currentTier === plan.id || (currentTier === 'starter' && plan.id === 'starter');
              const price = getPrice(plan);
              const revShare = plan.coalition_rev_share;
              
              return (
                <Card 
                  key={plan.id} 
                  className={`relative border-2 transition-all ${
                    isCurrent 
                      ? 'border-green-500 bg-green-50/30 shadow-lg ring-2 ring-green-500/20' 
                      : plan.popular 
                        ? 'border-blue-ncs shadow-md' 
                        : 'border-border hover:border-blue-ncs/50 hover:shadow-md'
                  }`}
                >
                  {/* Current Plan Badge */}
                  {isCurrent && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-green-500 text-white text-xs font-semibold px-3 py-1 rounded-full flex items-center gap-1">
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      Current plan
                    </div>
                  )}
                  {/* Popular Badge (only show if not current) */}
                  {plan.popular && !isCurrent && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-ncs text-white text-xs font-semibold px-3 py-1 rounded-full">
                      Most popular
                    </div>
                  )}
                  <CardHeader className="text-center pb-2">
                    <CardTitle className="text-lg">{plan.name}</CardTitle>
                    <div className="pt-2">
                      <span className="text-4xl font-bold text-foreground">
                        {price === 0 ? 'Free' : `$${price}`}
                      </span>
                      {price > 0 && <span className="text-muted-foreground text-sm">/{getPeriod()}</span>}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Coalition Rev Share Badge */}
                    <div className="bg-muted/50 rounded-lg p-2 text-center">
                      <p className="text-xs text-muted-foreground">Coalition Revenue</p>
                      <p className="text-sm font-semibold text-delft-blue dark:text-white">
                        {revShare.publisher}% you / {revShare.encypher}% Encypher
                      </p>
                    </div>
                    
                    <ul className="space-y-2 text-sm text-muted-foreground min-h-[180px]">
                      {plan.features.map((feature) => (
                        <li key={feature} className="flex items-start gap-2">
                          <svg className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                    
                    <Button
                      variant={isCurrent ? 'outline' : 'primary'}
                      fullWidth
                      disabled={isCurrent || upgradeMutation.isPending}
                      className={isCurrent ? 'border-green-500 text-green-600 cursor-default' : ''}
                      onClick={() => {
                        if (isCurrent) return;
                        if (plan.id === 'starter') {
                          toast.info('Contact support to downgrade your plan.');
                        } else {
                          upgradeMutation.mutate({ tier: plan.id, cycle: billingCycle });
                        }
                      }}
                    >
                      {isCurrent ? '✓ Your Plan' : plan.id === 'starter' ? 'Downgrade' : 'Upgrade'}
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
            
            {/* Enterprise Card */}
            <Card className="relative border-2 border-border hover:border-delft-blue/50 hover:shadow-md transition-all">
              <CardHeader className="text-center pb-2">
                <CardTitle className="text-lg">Enterprise</CardTitle>
                <div className="pt-2">
                  <span className="text-4xl font-bold text-foreground">Custom</span>
                  <p className="text-muted-foreground text-sm mt-1">Contact for pricing</p>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-muted/50 rounded-lg p-2 text-center">
                  <p className="text-xs text-muted-foreground">Coalition Revenue</p>
                  <p className="text-sm font-semibold text-delft-blue dark:text-white">80% you / 20% Encypher</p>
                </div>
                <ul className="space-y-2 text-sm text-muted-foreground min-h-[180px]">
                  <li className="flex items-start gap-2">
                    <svg className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Everything in Business
                  </li>
                  <li className="flex items-start gap-2">
                    <svg className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Unlimited API calls
                  </li>
                  <li className="flex items-start gap-2">
                    <svg className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Unlimited team seats
                  </li>
                  <li className="flex items-start gap-2">
                    <svg className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    SSO/SCIM integration
                  </li>
                  <li className="flex items-start gap-2">
                    <svg className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Dedicated account manager
                  </li>
                  <li className="flex items-start gap-2">
                    <svg className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Custom SLA & contracts
                  </li>
                </ul>
                <Button
                  variant="outline"
                  fullWidth
                  onClick={() => window.location.href = 'mailto:sales@encypherai.com?subject=Enterprise%20Inquiry'}
                >
                  Contact Sales
                </Button>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Invoices Section */}
        <section className="space-y-4">
          <h3 className="text-2xl font-semibold text-delft-blue dark:text-white">Invoices</h3>
          <Card>
            <CardContent className="p-0">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground border-b border-border">
                    <th className="py-3 px-4">Invoice</th>
                    <th className="py-3 px-4">Date</th>
                    <th className="py-3 px-4">Amount</th>
                    <th className="py-3 px-4">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {invoices.length === 0 && (
                    <tr>
                      <td colSpan={4} className="py-6 text-center text-muted-foreground">
                        {isLoading ? 'Loading invoices…' : 'No invoices yet.'}
                      </td>
                    </tr>
                  )}
                  {invoices.map((invoice: Invoice) => (
                    <tr key={invoice.id} className="border-b border-border/60 last:border-0">
                      <td className="py-3 px-4 font-medium">{invoice.invoice_number}</td>
                      <td className="py-3 px-4">{formatDate(invoice.created_at)}</td>
                      <td className="py-3 px-4">${invoice.amount_paid.toFixed(2)}</td>
                      <td className="py-3 px-4">
                        <span className={`capitalize px-2 py-1 rounded text-xs font-medium ${
                          invoice.status === 'paid' ? 'bg-green-100 text-green-800' :
                          invoice.status === 'open' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {invoice.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </section>
      </div>
    </DashboardLayout>
  );
}
