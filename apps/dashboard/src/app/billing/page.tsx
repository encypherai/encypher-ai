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
import apiClient, { PlanInfo, Invoice } from '../../lib/api';
import { DashboardLayout } from '../../components/layout/DashboardLayout';

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

  // Fetch subscription and invoices
  const billingQuery = useQuery({
    queryKey: ['billing', accessToken],
    queryFn: async () => {
      if (!accessToken) return { subscription: null, invoices: [] };
      const [subscription, invoices] = await Promise.all([
        apiClient.getSubscription(accessToken).catch(() => null),
        apiClient.getInvoices(accessToken).catch(() => []),
      ]);
      return { subscription, invoices };
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

  // Filter plans based on billing cycle
  const plans = useMemo(() => {
    const allPlans = plansQuery.data || [];
    return allPlans.filter(p => !p.enterprise); // Exclude enterprise (custom pricing)
  }, [plansQuery.data]);

  const subscription = billingQuery.data?.subscription;
  const invoices = billingQuery.data?.invoices || [];
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
          <h2 className="text-3xl font-bold text-delft-blue mb-2">Billing & Subscription</h2>
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
              <p className="text-2xl font-bold text-delft-blue">
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

        {/* Change Plan Section */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-semibold text-delft-blue">Change plan</h3>
              <p className="text-muted-foreground">Scale with usage. Upgrade or downgrade any time.</p>
            </div>
            <div className="flex bg-muted rounded-full p-1">
              <button
                className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                  billingCycle === 'monthly' ? 'bg-white shadow' : 'text-muted-foreground'
                }`}
                onClick={() => setBillingCycle('monthly')}
              >
                Monthly
              </button>
              <button
                className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                  billingCycle === 'annual' ? 'bg-white shadow' : 'text-muted-foreground'
                }`}
                onClick={() => setBillingCycle('annual')}
              >
                Annual <span className="text-xs">(save 20%)</span>
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            {plans.map((plan) => {
              const isCurrent = currentTier === plan.id;
              const price = getPrice(plan);
              const revShare = plan.coalition_rev_share;
              
              return (
                <Card key={plan.id} className={`relative ${plan.popular ? 'border-blue-ncs border-2' : ''}`}>
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-ncs text-white text-xs font-semibold px-3 py-1 rounded-full">
                      Most popular
                    </div>
                  )}
                  <CardHeader>
                    <CardTitle>{plan.name}</CardTitle>
                    <CardDescription>
                      <span className="text-3xl font-bold text-foreground">
                        {price === 0 ? 'Free' : `$${price}`}
                      </span>
                      {price > 0 && <span className="text-muted-foreground">/{getPeriod()}</span>}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Coalition Rev Share Badge */}
                    <div className="bg-muted/50 rounded-lg p-2 text-center">
                      <p className="text-xs text-muted-foreground">Coalition Revenue</p>
                      <p className="text-sm font-semibold text-delft-blue">
                        {revShare.publisher}% you / {revShare.encypher}% Encypher
                      </p>
                    </div>
                    
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      {plan.features.slice(0, 6).map((feature) => (
                        <li key={feature} className="flex items-start gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-blue-ncs mt-1.5 flex-shrink-0" />
                          <span>{feature}</span>
                        </li>
                      ))}
                      {plan.features.length > 6 && (
                        <li className="text-xs text-muted-foreground">
                          +{plan.features.length - 6} more features
                        </li>
                      )}
                    </ul>
                    
                    <Button
                      variant={isCurrent ? 'outline' : 'primary'}
                      fullWidth
                      disabled={isCurrent || upgradeMutation.isPending}
                      onClick={() => {
                        if (plan.id === 'starter') {
                          toast.info('You are already on the Starter plan.');
                        } else {
                          upgradeMutation.mutate({ tier: plan.id, cycle: billingCycle });
                        }
                      }}
                    >
                      {isCurrent ? 'Current plan' : plan.id === 'starter' ? 'Downgrade' : 'Upgrade'}
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
            
            {/* Enterprise Card */}
            <Card className="relative border-dashed">
              <CardHeader>
                <CardTitle>Enterprise</CardTitle>
                <CardDescription>
                  <span className="text-xl font-bold text-foreground">Custom pricing</span>
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-muted/50 rounded-lg p-2 text-center">
                  <p className="text-xs text-muted-foreground">Coalition Revenue</p>
                  <p className="text-sm font-semibold text-delft-blue">80% you / 20% Encypher</p>
                </div>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-ncs mt-1.5" />
                    Everything in Business
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-ncs mt-1.5" />
                    Unlimited everything
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-ncs mt-1.5" />
                    SSO/SCIM integration
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-ncs mt-1.5" />
                    Dedicated support
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
          <h3 className="text-2xl font-semibold text-delft-blue">Invoices</h3>
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
