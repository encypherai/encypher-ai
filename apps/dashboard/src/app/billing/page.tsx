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
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { useMemo, useState } from 'react';
import { toast } from 'sonner';
import apiClient from '../../lib/api';
import { DashboardLayout } from '../../components/layout/DashboardLayout';

type PaymentMethod = {
  brand?: string;
  last4?: string;
  expMonth?: string | number;
  expYear?: string | number;
};

type Invoice = {
  id: string;
  date: string;
  amount: number;
  status: string;
  url?: string;
};

type BillingInfo = {
  planId: string;
  planName: string;
  price: number;
  period: 'month' | 'year';
  features: string[];
  renewalDate?: string;
  paymentMethod?: PaymentMethod;
};

const planCatalog = (billingCycle: 'monthly' | 'annual') => [
  {
    id: 'starter',
    name: 'Starter',
    price: 0,
    period: 'month',
    features: [
      'Unlimited C2PA signing',
      'Unlimited verifications',
      '2 API keys',
      'Community support',
      '7-day analytics',
      'Licensing coalition (65/35 rev share)',
    ],
    coalition: '65% you / 35% Encypher',
  },
  {
    id: billingCycle === 'monthly' ? 'pro-monthly' : 'pro-annual',
    name: 'Professional',
    price: billingCycle === 'monthly' ? 99 : 950,
    period: billingCycle === 'monthly' ? 'month' : 'year',
    features: [
      'Everything in Starter',
      'Sentence-level tracking (50K/mo)',
      'Invisible embeddings',
      '10 API keys',
      'Email support (48hr SLA)',
      '90-day analytics',
      'BYOK encryption',
      'WordPress Pro (no branding)',
      'Licensing coalition (70/30 rev share)',
    ],
    popular: true,
    coalition: '70% you / 30% Encypher',
  },
  {
    id: billingCycle === 'monthly' ? 'business-monthly' : 'business-annual',
    name: 'Business',
    price: billingCycle === 'monthly' ? 499 : 4790,
    period: billingCycle === 'monthly' ? 'month' : 'year',
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
      'Licensing coalition (75/25 rev share)',
    ],
    coalition: '75% you / 25% Encypher',
  },
];

const normalizeBillingInfo = (raw: any): BillingInfo => ({
  planId: raw?.plan_id ?? raw?.planId ?? 'free',
  planName: raw?.plan_name ?? raw?.planName ?? 'Free',
  price: raw?.price ?? 0,
  period: (raw?.period ?? 'month') as 'month' | 'year',
  features:
    raw?.features ??
    [
      '1,000 signatures/month',
      'Unlimited verifications',
      'Email support',
    ],
  renewalDate: raw?.renewal_date ?? raw?.renews_on ?? '',
  paymentMethod: raw?.payment_method ?? raw?.paymentMethod,
});

const normalizeInvoices = (raw: any): Invoice[] => {
  const rows = raw?.data ?? raw?.invoices ?? raw ?? [];
  return (Array.isArray(rows) ? rows : []).map((invoice: any, idx: number) => ({
    id: invoice.id ?? invoice.invoice_id ?? `INV-${idx}`,
    date: invoice.date ?? invoice.created_at ?? invoice.period_start ?? '',
    amount: invoice.amount ?? invoice.total ?? 0,
    status: invoice.status ?? invoice.state ?? 'paid',
    url: invoice.download_url ?? invoice.url,
  }));
};

export default function BillingPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

  const billingQuery = useQuery({
    queryKey: ['billing'],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in to view billing details.');
      const [infoResponse, invoiceResponse] = await Promise.all([
        apiClient.getBillingInfo(accessToken),
        apiClient.getInvoices(accessToken),
      ]);

      return {
        billing: normalizeBillingInfo((infoResponse as any)?.data ?? infoResponse),
        invoices: normalizeInvoices(invoiceResponse as any),
      };
    },
    enabled: Boolean(accessToken),
  });

  const updatePlanMutation = useMutation({
    mutationFn: async (planId: string) => {
      if (!accessToken) throw new Error('You must be signed in to update your plan.');
      await apiClient.updateSubscription(accessToken, planId);
    },
    onSuccess: () => {
      toast.success('Subscription updated.');
      billingQuery.refetch();
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to update plan.');
    },
  });

  const currentPlan = billingQuery.data?.billing;
  const invoices = billingQuery.data?.invoices ?? [];
  const plans = useMemo(() => planCatalog(billingCycle), [billingCycle]);

  const isLoading = status === 'loading' || billingQuery.isLoading;

  const paymentLabel = currentPlan?.paymentMethod
    ? `${currentPlan.paymentMethod.brand ?? 'Card'} •••• ${currentPlan.paymentMethod.last4 ?? ''}`
    : 'Add payment method';

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-delft-blue mb-2">Billing & Subscription</h2>
          <p className="text-muted-foreground">
            Manage your plan, payment methods, and download invoices for your records.
          </p>
        </div>

        <Card className="border-columbia-blue">
          <CardHeader>
            <CardTitle>Current Plan</CardTitle>
            <CardDescription>
              {isLoading ? 'Loading plan information…' : currentPlan?.planName}
            </CardDescription>
          </CardHeader>
          <CardContent className="grid md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Plan</p>
              <p className="text-2xl font-bold text-delft-blue">
                {currentPlan?.planName ?? '—'}
              </p>
              <p className="text-muted-foreground">
                {currentPlan ? `$${currentPlan.price}/${currentPlan.period}` : '—'}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Renews</p>
              <p className="text-foreground">{currentPlan?.renewalDate || '—'}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Payment method</p>
              <p className="text-foreground">{paymentLabel}</p>
            </div>
          </CardContent>
        </Card>

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

          <div className="grid md:grid-cols-3 gap-6">
            {plans.map((plan) => {
              const isCurrent = currentPlan?.planId === plan.id || currentPlan?.planName === plan.name;
              return (
                <Card key={plan.id} className={`relative ${plan.popular ? 'border-blue-ncs' : ''}`}>
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-ncs text-white text-xs font-semibold px-3 py-1 rounded-full">
                      Most popular
                    </div>
                  )}
                  <CardHeader>
                    <CardTitle>{plan.name}</CardTitle>
                    <CardDescription>
                      <span className="text-3xl font-bold text-foreground">${plan.price}</span>
                      <span className="text-muted-foreground">/{plan.period}</span>
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      {plan.features.map((feature) => (
                        <li key={feature} className="flex items-center gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-blue-ncs" /> {feature}
                        </li>
                      ))}
                    </ul>
                    <Button
                      variant={isCurrent ? 'outline' : 'primary'}
                      fullWidth
                      disabled={isCurrent || updatePlanMutation.isPending}
                      onClick={() => updatePlanMutation.mutate(plan.id)}
                    >
                      {isCurrent ? 'Current plan' : 'Switch to this plan'}
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </section>

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
                    <th className="py-3 px-4" />
                  </tr>
                </thead>
                <tbody>
                  {invoices.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-6 text-center text-muted-foreground">
                        {isLoading ? 'Loading invoices…' : 'No invoices yet.'}
                      </td>
                    </tr>
                  )}
                  {invoices.map((invoice) => (
                    <tr key={invoice.id} className="border-b border-border/60 last:border-0">
                      <td className="py-3 px-4 font-medium">{invoice.id}</td>
                      <td className="py-3 px-4">{invoice.date}</td>
                      <td className="py-3 px-4">${invoice.amount.toFixed(2)}</td>
                      <td className="py-3 px-4 capitalize">{invoice.status}</td>
                      <td className="py-3 px-4 text-right">
                        <a 
                          href={invoice.url || '#'} 
                          target="_blank" 
                          rel="noreferrer"
                          className="inline-flex items-center justify-center px-3 py-1.5 text-sm font-medium border border-border rounded-md hover:bg-muted transition-colors"
                        >
                          Download
                        </a>
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
