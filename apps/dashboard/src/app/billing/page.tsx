'use client';

import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent } from '@encypher/design-system';
import { useState } from 'react';
import Link from 'next/link';

export default function BillingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

  // Mock data - replace with actual API calls
  const currentPlan = {
    name: 'Professional',
    price: 99,
    period: 'month',
    features: [
      '50,000 signatures/month',
      'Unlimited verifications',
      'Priority support',
      'Advanced analytics',
      'Custom branding',
    ],
  };

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      period: 'month',
      features: [
        '1,000 signatures/month',
        'Unlimited verifications',
        'Email support',
        'Basic analytics',
      ],
      popular: false,
    },
    {
      id: 'professional',
      name: 'Professional',
      price: billingCycle === 'monthly' ? 99 : 950,
      period: billingCycle === 'monthly' ? 'month' : 'year',
      features: [
        '50,000 signatures/month',
        'Unlimited verifications',
        'Priority support',
        'Advanced analytics',
        'Custom branding',
        'API access',
      ],
      popular: true,
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: billingCycle === 'monthly' ? 499 : 4790,
      period: billingCycle === 'monthly' ? 'month' : 'year',
      features: [
        'Unlimited signatures',
        'Unlimited verifications',
        '24/7 phone support',
        'Advanced analytics',
        'Custom branding',
        'API access',
        'Dedicated account manager',
        'SLA guarantee',
        'Custom integrations',
      ],
      popular: false,
    },
  ];

  const invoices = [
    { id: 'INV-2025-001', date: '2025-01-01', amount: 99, status: 'paid', downloadUrl: '#' },
    { id: 'INV-2024-012', date: '2024-12-01', amount: 99, status: 'paid', downloadUrl: '#' },
    { id: 'INV-2024-011', date: '2024-11-01', amount: 99, status: 'paid', downloadUrl: '#' },
    { id: 'INV-2024-010', date: '2024-10-01', amount: 99, status: 'paid', downloadUrl: '#' },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-white sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/">
                <div className="w-8 h-8 bg-gradient-to-br from-delft-blue to-blue-ncs rounded-lg cursor-pointer" />
              </Link>
              <h1 className="text-xl font-bold text-delft-blue">Encypher Dashboard</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link href="/">
                <Button variant="ghost" size="sm">Dashboard</Button>
              </Link>
              <Link href="/api-keys">
                <Button variant="ghost" size="sm">API Keys</Button>
              </Link>
              <Link href="/analytics">
                <Button variant="ghost" size="sm">Analytics</Button>
              </Link>
              <Link href="/settings">
                <Button variant="ghost" size="sm">Settings</Button>
              </Link>
              <div className="w-8 h-8 bg-columbia-blue rounded-full flex items-center justify-center text-white font-semibold">
                U
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-delft-blue mb-2">Billing & Subscription</h2>
          <p className="text-muted-foreground">
            Manage your subscription, payment methods, and billing history
          </p>
        </div>

        {/* Current Plan */}
        <Card className="mb-8 border-columbia-blue">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Current Plan: {currentPlan.name}</CardTitle>
                <CardDescription>
                  ${currentPlan.price}/{currentPlan.period} • Renews on February 1, 2025
                </CardDescription>
              </div>
              <Button variant="outline">Change Plan</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-3">Plan Features</h4>
                <ul className="space-y-2">
                  {currentPlan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center space-x-2 text-sm">
                      <svg className="w-4 h-4 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Usage This Month</h4>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Signatures</span>
                      <span className="font-medium">3,421 / 50,000</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div className="bg-columbia-blue h-2 rounded-full" style={{ width: '6.8%' }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Verifications</span>
                      <span className="font-medium">8,192 / Unlimited</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div className="bg-blue-ncs h-2 rounded-full" style={{ width: '100%' }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Available Plans */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-delft-blue">Available Plans</h3>
            <div className="flex items-center space-x-2 bg-muted rounded-lg p-1">
              <button
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  billingCycle === 'monthly'
                    ? 'bg-white text-delft-blue shadow'
                    : 'text-muted-foreground'
                }`}
                onClick={() => setBillingCycle('monthly')}
              >
                Monthly
              </button>
              <button
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  billingCycle === 'annual'
                    ? 'bg-white text-delft-blue shadow'
                    : 'text-muted-foreground'
                }`}
                onClick={() => setBillingCycle('annual')}
              >
                Annual
                <span className="ml-2 text-xs text-success">Save 20%</span>
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {plans.map((plan) => (
              <Card key={plan.id} className={plan.popular ? 'border-columbia-blue shadow-lg' : ''}>
                {plan.popular && (
                  <div className="bg-columbia-blue text-white text-center py-2 text-sm font-semibold rounded-t-lg">
                    Most Popular
                  </div>
                )}
                <CardHeader>
                  <CardTitle>{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-delft-blue">${plan.price}</span>
                    <span className="text-muted-foreground">/{plan.period}</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start space-x-2 text-sm">
                        <svg className="w-4 h-4 text-success mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button 
                    variant={plan.popular ? 'primary' : 'outline'} 
                    fullWidth
                  >
                    {plan.id === 'professional' ? 'Current Plan' : 'Upgrade'}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Payment Method */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Payment Method</CardTitle>
                <CardDescription>Manage your payment information</CardDescription>
              </div>
              <Button variant="outline">Update</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4 p-4 border border-border rounded-lg">
              <div className="w-12 h-8 bg-gradient-to-r from-blue-600 to-blue-400 rounded flex items-center justify-center">
                <svg className="w-8 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M0 4v16h24V4H0zm22 14H2V8h20v10z"/>
                </svg>
              </div>
              <div className="flex-1">
                <div className="font-medium">Visa ending in 4242</div>
                <div className="text-sm text-muted-foreground">Expires 12/2025</div>
              </div>
              <span className="px-2 py-1 bg-success/10 text-success text-xs rounded-full">Default</span>
            </div>
          </CardContent>
        </Card>

        {/* Billing History */}
        <Card>
          <CardHeader>
            <CardTitle>Billing History</CardTitle>
            <CardDescription>View and download your past invoices</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {invoices.map((invoice) => (
                <div key={invoice.id} className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-medium">{invoice.id}</div>
                      <div className="text-sm text-muted-foreground">{invoice.date}</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="font-semibold">${invoice.amount}</div>
                      <span className="px-2 py-1 bg-success/10 text-success text-xs rounded-full">
                        {invoice.status}
                      </span>
                    </div>
                    <Button variant="ghost" size="sm">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
