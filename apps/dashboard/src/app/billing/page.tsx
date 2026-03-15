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
import { useEffect, useRef, Suspense } from 'react';
import { toast } from 'sonner';
import { useSearchParams } from 'next/navigation';
import apiClient, {
  type BillingUsageStats,
  type CoalitionSummary,
  Invoice,
  type SubscriptionInfo,
} from '../../lib/api';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { useOrganization } from '../../contexts/OrganizationContext';
import {
  FREE_TIER,
  ENTERPRISE_TIER,
  ADD_ONS,
  BUNDLES,
  formatAddOnPrice,
  formatBundlePrice,
  type AddOnConfig,
} from '@/lib/pricing-config';
import { LICENSING_TRACKS } from '@/lib/pricing-config/coalition';


function BillingPageContent() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const { activeOrganization, refetch: refetchOrganization } = useOrganization();
  const searchParams = useSearchParams();
  const hasRefetchedAfterCheckout = useRef(false);
  const requestedAddOn = searchParams.get('addon');
  const requestedQuantity = Number(searchParams.get('quantity') || '0');
  const archiveQuantity = Number.isFinite(requestedQuantity) && requestedQuantity > 0 ? requestedQuantity : 0;
  const isArchiveBackfillRequested = requestedAddOn === 'bulk-archive-backfill';
  const archiveEstimatedTotal = archiveQuantity * 0.01;

  // Fetch subscription, invoices, usage, and coalition data
  const billingQuery = useQuery<{
    subscription: SubscriptionInfo | null;
    invoices: Invoice[];
    usage: BillingUsageStats | null;
    coalition: CoalitionSummary | null;
  }>({
    queryKey: ['billing', accessToken],
    queryFn: async () => {
      if (!accessToken) return { subscription: null, invoices: [], usage: null, coalition: null };
      const [invoices, usage, coalition] = await Promise.all([
        apiClient.getInvoices(accessToken).catch(() => []),
        apiClient.getBillingUsage(accessToken).catch(() => null),
        apiClient.getCoalitionEarnings(accessToken).catch(() => null),
      ]);
      const subscription = null;
      return { subscription, invoices, usage, coalition };
    },
    enabled: Boolean(accessToken),
  });

  useEffect(() => {
    if (!accessToken) return;
    const success = searchParams.get('success');
    const upgrade = searchParams.get('upgrade');
    const isCheckoutSuccess = success === 'true' || upgrade === 'success';
    if (isCheckoutSuccess && !hasRefetchedAfterCheckout.current) {
      billingQuery.refetch();
      refetchOrganization();
      hasRefetchedAfterCheckout.current = true;
    }
    if (!isCheckoutSuccess) {
      hasRefetchedAfterCheckout.current = false;
    }
  }, [accessToken, billingQuery, refetchOrganization, searchParams]);

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

  const addOnCheckoutMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      if (!archiveQuantity) throw new Error('No archive quantity selected.');
      return apiClient.createAddOnCheckout(accessToken, {
        add_on: 'bulk-archive-backfill',
        quantity: archiveQuantity,
      });
    },
    onSuccess: (response) => {
      window.location.href = response.checkout_url;
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Failed to start archive checkout.');
    },
  });

  const addOnSubscriptionMutation = useMutation({
    mutationFn: async (addOnId: string) => {
      if (!accessToken) throw new Error('You must be signed in.');
      return apiClient.createAddOnSubscriptionCheckout(accessToken, {
        add_on: addOnId,
      });
    },
    onSuccess: (response) => {
      window.location.href = response.checkout_url;
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Failed to start add-on checkout.');
    },
  });

  const subscription = billingQuery.data?.subscription;
  const invoices = billingQuery.data?.invoices || [];
  const usage = billingQuery.data?.usage;
  const coalition = billingQuery.data?.coalition;
  const organizationTier = activeOrganization?.tier;
  const subscriptionTier = subscription?.tier && subscription.tier !== 'unknown' ? subscription.tier : undefined;
  // TEAM_160: Map old tier names to new model
  const rawTier = subscriptionTier || organizationTier || 'free';
  const currentTier = ['starter', 'free', 'basic'].includes(rawTier) ? 'free' : rawTier;
  const currentTierLabel = currentTier === 'enterprise' ? 'Enterprise' : 'Free';
  // Get subscription price info
  const currentPrice = subscription?.amount && subscription.amount > 0
    ? subscription.amount
    : 0;
  const currentBillingCycle = subscription?.billing_cycle || 'monthly';
  const isDowngradeScheduled = Boolean(subscription?.cancel_at_period_end);
  const downgradeEffectiveDate = subscription?.current_period_end;
  const downgradeTargetLabel = 'Free';
  const currentPriceLabel = currentPrice > 0
    ? `$${currentPrice}/${currentBillingCycle === 'annual' ? 'year' : 'month'}`
    : currentTier === 'enterprise'
      ? 'Custom'
      : 'Free';
  // TEAM_061: Enterprise pricing terms (rev share) should not be displayed in the dashboard UI.
  const isEnterpriseTier = currentTier === 'enterprise';
  const isLoading = status === 'loading' || billingQuery.isLoading;

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
          <h1 className="text-2xl font-bold text-delft-blue dark:text-white">Billing &amp; Subscription</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage your plan, payment methods, and download invoices.
          </p>
        </div>

        {/* Free Tier Welcome Banner */}
        {!isLoading && currentTier === 'free' && !isEnterpriseTier && (
          <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-columbia-blue/20 via-blue-ncs/10 to-columbia-blue/20 border border-columbia-blue/30 p-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-ncs text-white">
                    Free Plan
                  </span>
                  <span className="text-xs text-muted-foreground">1,000 docs/month included</span>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  Full C2PA signing, Merkle tree auth, unlimited verification, and coalition membership — all at $0. Add enforcement tools when you&apos;re ready.
                </p>
              </div>
              <a href="#addons-bundles" className="inline-flex items-center gap-2 px-4 py-2 bg-blue-ncs text-white text-sm font-medium rounded-lg hover:bg-blue-ncs/90 transition-colors whitespace-nowrap flex-shrink-0">
                Explore Add-Ons
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
              </a>
            </div>
          </div>
        )}

        {/* Current Plan Card */}
        <Card className="border-columbia-blue">
          <CardHeader>
            <CardTitle>{isDowngradeScheduled ? 'Current Plan (Downgrade Scheduled)' : 'Current Plan'}</CardTitle>
            <CardDescription>
              {isLoading ? 'Loading plan information…' : currentTierLabel}
            </CardDescription>
          </CardHeader>
          <CardContent className={isEnterpriseTier ? 'grid md:grid-cols-3 gap-6' : 'grid md:grid-cols-4 gap-6'}>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Plan</p>
              <p className="text-2xl font-bold text-delft-blue dark:text-white">
                {currentTierLabel}
              </p>
              <span className={`mt-1 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                currentTier === 'enterprise'
                  ? 'bg-blue-ncs/10 text-blue-ncs'
                  : 'bg-muted text-muted-foreground'
              }`}>
                {currentPriceLabel}
              </span>
              {isDowngradeScheduled && downgradeEffectiveDate && (
                <p className="mt-2 text-xs text-amber-600">
                  Access ends {formatDate(downgradeEffectiveDate)}
                </p>
              )}
            </div>
            {isDowngradeScheduled && (
              <div>
                <p className="text-sm text-muted-foreground mb-1">Next Plan</p>
                <p className="text-2xl font-bold text-delft-blue dark:text-white">
                  {downgradeTargetLabel}
                </p>
                <p className="text-muted-foreground">Free</p>
              </div>
            )}
            <div>
              <p className="text-sm text-muted-foreground mb-1">Status</p>
              <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                isDowngradeScheduled
                  ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-200'
                  : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200'
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${isDowngradeScheduled ? 'bg-amber-500' : 'bg-emerald-500'}`} />
                {isDowngradeScheduled ? 'Downgrade scheduled' : subscription?.status || 'Active'}
              </span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">
                {isDowngradeScheduled ? 'Ends' : 'Renews'}
              </p>
              <p className="text-foreground">
                {subscription?.current_period_end ? formatDate(subscription.current_period_end) : '—'}
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
                  'Coalition earnings summary'
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

        {/* Licensing Revenue Tracks */}
        <Card>
          <CardHeader>
            <CardTitle>Licensing Revenue</CardTitle>
            <CardDescription>Same splits for all publishers — Free or Enterprise</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              {Object.entries(LICENSING_TRACKS).map(([key, track]) => (
                <div key={key} className="bg-muted/30 rounded-lg p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl font-bold text-blue-ncs">{track.split}</span>
                    <div>
                      <p className="font-semibold text-sm">{track.name}</p>
                      <p className="text-xs text-muted-foreground">Publisher / Encypher</p>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">{track.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Bulk Archive Backfill callout — shown when no documents have been signed yet */}
        {!isLoading && (usage?.metrics?.['documents_signed']?.used ?? 0) === 0 && (
          <div className="rounded-xl border border-blue-ncs/40 bg-blue-ncs/5 p-5">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <p className="font-semibold text-sm text-delft-blue dark:text-white">
                  You have 0 signed documents.
                </p>
                <p className="text-sm text-muted-foreground mt-0.5">
                  Sign your existing archive at $0.01/doc -- one batch operation covers years of content.
                </p>
              </div>
              <a
                href="#addons-bundles"
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-ncs text-white text-sm font-medium rounded-lg hover:bg-blue-ncs/90 transition-colors whitespace-nowrap flex-shrink-0"
              >
                Learn More
              </a>
            </div>
          </div>
        )}

        {/* Add-Ons & Bundles Section */}
        <section id="addons-bundles" className="space-y-4 scroll-mt-8">
          <div>
            <h3 className="text-2xl font-semibold text-delft-blue dark:text-white">Add-Ons & Bundles</h3>
            <p className="text-muted-foreground">Self-service enforcement tools. Add when you&apos;re ready to license.</p>
          </div>

          {isArchiveBackfillRequested && archiveQuantity > 0 && (
            <Card className="border-blue-ncs bg-blue-ncs/5">
              <CardHeader>
                <CardTitle>Archive Backfill Requested</CardTitle>
                <CardDescription>
                  Finish the one-time archive purchase started from the WordPress plugin.
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Archive documents</p>
                  <p className="text-2xl font-bold text-delft-blue dark:text-white">{archiveQuantity.toLocaleString()}</p>
                  <p className="text-sm text-muted-foreground">Estimated one-time total: ${archiveEstimatedTotal.toFixed(2)}</p>
                </div>
                <div className="flex flex-col gap-2 sm:flex-row">
                  <Button
                    onClick={() => addOnCheckoutMutation.mutate()}
                    disabled={addOnCheckoutMutation.isPending || isEnterpriseTier}
                  >
                    {isEnterpriseTier ? 'Included in Enterprise' : addOnCheckoutMutation.isPending ? 'Opening Checkout…' : 'Buy Archive Backfill'}
                  </Button>
                  <a
                    href="#addons-bundles"
                    className="inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground"
                  >
                    Review Add-On Details
                  </a>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Bundles */}
          <div className="grid md:grid-cols-3 gap-4">
            {BUNDLES.map((bundle) => (
              <Card key={bundle.id} className={`${bundle.comingSoon ? 'opacity-80' : bundle.id === 'enforcement-bundle' ? 'border-blue-ncs' : ''}`}>
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-lg">{bundle.name}</CardTitle>
                    {bundle.comingSoon && <span className="text-[10px] font-medium border rounded px-1.5 py-0.5 text-muted-foreground">Coming Soon</span>}
                  </div>
                  <CardDescription>{bundle.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  {!bundle.comingSoon ? (
                    <div className="flex items-baseline gap-2 mb-3">
                      <span className="text-2xl font-bold text-blue-ncs">{formatBundlePrice(bundle)}</span>
                      <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">Save {bundle.savings}</span>
                    </div>
                  ) : (
                    <div className="mb-3" />
                  )}
                  <ul className="space-y-1.5 text-sm">
                    {bundle.includes.map((item: string) => (
                      <li key={item} className="flex items-start gap-2">
                        <svg className="w-4 h-4 text-blue-ncs mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-muted-foreground">{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Individual Add-Ons */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Individual Add-Ons</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-3">
                {ADD_ONS.map((addOn: AddOnConfig) => {
                  const orgAddOns = (activeOrganization?.add_ons || {}) as Record<string, { active?: boolean }>;
                  const addOnState = orgAddOns[addOn.id];
                  const isActive = Boolean(addOnState && addOnState.active);
                  const isSubscriptionAddOn = ['custom-signing-identity', 'white-label-verification', 'custom-verification-domain', 'byok', 'priority-support'].includes(addOn.id);
                  const canPurchase = isSubscriptionAddOn && !addOn.comingSoon && !isActive && !isEnterpriseTier;

                  return (
                    <div key={addOn.id} className={`flex justify-between items-start p-3 bg-muted/30 rounded-lg ${addOn.comingSoon ? 'opacity-80' : ''} ${isActive ? 'border border-emerald-500 bg-emerald-500/5' : ''} ${isArchiveBackfillRequested && addOn.id === 'bulk-archive-backfill' ? 'border border-blue-ncs bg-blue-ncs/5' : ''}`}>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-sm">{addOn.name}</p>
                          {isActive && (
                            <span className="text-[10px] font-semibold rounded px-1.5 py-0.5 bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200">Active</span>
                          )}
                          {addOn.comingSoon && <span className="text-[10px] font-medium border rounded px-1.5 py-0.5 text-muted-foreground">Coming Soon</span>}
                          {isArchiveBackfillRequested && addOn.id === 'bulk-archive-backfill' && (
                            <span className="text-[10px] font-medium rounded px-1.5 py-0.5 bg-blue-ncs text-white">Selected from WordPress</span>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground">{addOn.description}</p>
                        {isArchiveBackfillRequested && addOn.id === 'bulk-archive-backfill' && archiveQuantity > 0 && (
                          <p className="text-xs text-delft-blue mt-2">
                            {archiveQuantity.toLocaleString()} documents selected · ${archiveEstimatedTotal.toFixed(2)} one-time
                          </p>
                        )}
                      </div>
                      <div className="ml-3 flex flex-col items-end gap-2">
                        {!addOn.comingSoon && (
                          <span className="text-sm font-bold text-blue-ncs whitespace-nowrap">{formatAddOnPrice(addOn)}</span>
                        )}
                        {canPurchase && (
                          <Button
                            size="sm"
                            onClick={() => addOnSubscriptionMutation.mutate(addOn.id)}
                            disabled={addOnSubscriptionMutation.isPending}
                          >
                            {addOnSubscriptionMutation.isPending ? 'Opening...' : 'Subscribe'}
                          </Button>
                        )}
                        {isEnterpriseTier && !addOn.comingSoon && isSubscriptionAddOn && (
                          <span className="text-[10px] font-medium text-muted-foreground">Included</span>
                        )}
                        {isArchiveBackfillRequested && addOn.id === 'bulk-archive-backfill' && (
                          <Button
                            size="sm"
                            onClick={() => addOnCheckoutMutation.mutate()}
                            disabled={addOnCheckoutMutation.isPending || isEnterpriseTier}
                          >
                            {isEnterpriseTier ? 'Included' : addOnCheckoutMutation.isPending ? 'Opening...' : 'Checkout'}
                          </Button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Enterprise Section */}
        <section className="space-y-4">
          <Card className={isEnterpriseTier ? 'border-2 border-green-500 ring-2 ring-green-500/20' : 'border-blue-ncs/30'}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Enterprise</CardTitle>
                  <CardDescription>Unlimited everything. All add-ons included. Exclusive capabilities.</CardDescription>
                </div>
                {isEnterpriseTier && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-full bg-green-500 text-white">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Current plan
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm font-medium mb-2">All add-ons included:</p>
                  <ul className="space-y-1.5 text-sm">
                    {ENTERPRISE_TIER.features.slice(0, 6).map((feature: string) => (
                      <li key={feature} className="flex items-start gap-2">
                        <svg className="w-4 h-4 text-blue-ncs mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-muted-foreground">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="text-sm font-medium mb-2">Exclusive capabilities:</p>
                  <ul className="space-y-1.5 text-sm">
                    {ENTERPRISE_TIER.exclusiveCapabilities.slice(0, 6).map((cap: string) => (
                      <li key={cap} className="flex items-start gap-2">
                        <svg className="w-4 h-4 text-blue-ncs mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-muted-foreground">{cap}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              {!isEnterpriseTier && (
                <Button
                  variant="outline"
                  onClick={() => {
                    window.location.href = 'mailto:sales@encypherai.com?subject=Enterprise%20Inquiry';
                  }}
                >
                  Contact Sales
                </Button>
              )}
            </CardContent>
          </Card>
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

export default function BillingPage() {
  return (
    <Suspense fallback={
      <DashboardLayout>
        <div className="space-y-8">
          <div>
            <h1 className="text-2xl font-bold text-delft-blue dark:text-white">Billing &amp; Subscription</h1>
            <p className="text-sm text-muted-foreground mt-1">Loading billing information...</p>
          </div>
          <Card className="border-columbia-blue">
            <CardHeader>
              <CardTitle>Current Plan</CardTitle>
              <CardDescription>Loading...</CardDescription>
            </CardHeader>
            <CardContent className="grid md:grid-cols-4 gap-6">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-4 w-20 bg-muted rounded mb-2" />
                  <div className="h-8 w-32 bg-muted rounded" />
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    }>
      <BillingPageContent />
    </Suspense>
  );
}
