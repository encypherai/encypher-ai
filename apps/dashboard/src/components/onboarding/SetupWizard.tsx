'use client';

/**
 * Mandatory Setup Wizard
 *
 * TEAM_191: Non-cancelable post-signup wizard that collects publisher identity
 * (individual vs organization, display name) before the user can use the dashboard.
 * After completion, shows a welcome screen with next-step links.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import Link from 'next/link';
import { useState } from 'react';
import { toast } from 'sonner';
import apiClient, { type AccountType } from '../../lib/api';

type WizardStep = 'account_type' | 'display_name' | 'welcome';

export function SetupWizard() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();

  const [step, setStep] = useState<WizardStep>('account_type');
  const [accountType, setAccountType] = useState<AccountType | null>(null);
  const [displayName, setDisplayName] = useState(
    session?.user?.name || ''
  );

  const completeMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken || !accountType) throw new Error('Missing data');
      return apiClient.completeSetup(accessToken, {
        account_type: accountType,
        display_name: displayName.trim(),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['setup-status'] });
      queryClient.invalidateQueries({ queryKey: ['onboarding-status'] });
      setStep('welcome');
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to save. Please try again.');
    },
  });

  const handleSubmitIdentity = () => {
    if (!displayName.trim()) {
      toast.error('Please enter a name.');
      return;
    }
    completeMutation.mutate();
  };

  return (
    <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
        {/* Progress indicator */}
        <div className="flex gap-1 px-6 pt-6">
          {(['account_type', 'display_name', 'welcome'] as WizardStep[]).map((s, i) => (
            <div
              key={s}
              className={`h-1 flex-1 rounded-full transition-colors ${
                i <= ['account_type', 'display_name', 'welcome'].indexOf(step)
                  ? 'bg-gradient-to-r from-blue-ncs to-delft-blue'
                  : 'bg-slate-200 dark:bg-slate-700'
              }`}
            />
          ))}
        </div>

        <div className="p-6">
          {/* Step 1: Account Type */}
          {step === 'account_type' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-delft-blue dark:text-white">
                  Welcome to Encypher
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  Let&apos;s set up your publisher identity. This determines how your name appears on signed content.
                </p>
              </div>

              <div className="space-y-3">
                <button
                  onClick={() => {
                    setAccountType('individual');
                    setStep('display_name');
                  }}
                  className="w-full flex items-start gap-4 p-4 rounded-xl border-2 border-border hover:border-blue-ncs transition-colors text-left group"
                >
                  <div className="w-10 h-10 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex items-center justify-center text-blue-ncs flex-shrink-0 mt-0.5">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-semibold text-delft-blue dark:text-white group-hover:text-blue-ncs transition-colors">
                      Independent creator
                    </p>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      Journalist, blogger, freelance writer, or individual publisher
                    </p>
                  </div>
                </button>

                <button
                  onClick={() => {
                    setAccountType('organization');
                    setDisplayName('');
                    setStep('display_name');
                  }}
                  className="w-full flex items-start gap-4 p-4 rounded-xl border-2 border-border hover:border-blue-ncs transition-colors text-left group"
                >
                  <div className="w-10 h-10 bg-purple-50 dark:bg-purple-900/20 rounded-lg flex items-center justify-center text-purple-600 flex-shrink-0 mt-0.5">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-semibold text-delft-blue dark:text-white group-hover:text-blue-ncs transition-colors">
                      Organization or company
                    </p>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      News outlet, media company, enterprise, or team
                    </p>
                  </div>
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Display Name */}
          {step === 'display_name' && (
            <div className="space-y-6">
              <div>
                <button
                  onClick={() => setStep('account_type')}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors mb-3 flex items-center gap-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back
                </button>
                <h2 className="text-xl font-bold text-delft-blue dark:text-white">
                  {accountType === 'individual'
                    ? 'What name should appear on your signed content?'
                    : "What's your organization name?"}
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  {accountType === 'individual'
                    ? 'This is what readers see when they verify your content.'
                    : 'This appears on all content signed by your team.'}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  {accountType === 'individual' ? 'Your name or pen name' : 'Organization name'}
                </label>
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder={accountType === 'individual' ? 'e.g. Sarah Chen' : 'e.g. The Verge'}
                  className="w-full px-4 py-2.5 rounded-lg border border-border bg-white dark:bg-slate-800 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-blue-ncs focus:border-transparent"
                  autoFocus
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSubmitIdentity();
                  }}
                />
                <p className="text-xs text-muted-foreground mt-2">
                  {accountType === 'individual'
                    ? 'Signed content will show: "Signed by [your name] · Powered by Encypher"'
                    : 'Signed content will show: "Signed by [your name] at [org name] · Powered by Encypher"'}
                </p>
              </div>

              <button
                onClick={handleSubmitIdentity}
                disabled={!displayName.trim() || completeMutation.isPending}
                className="w-full py-2.5 bg-gradient-to-r from-blue-ncs to-delft-blue text-white font-medium rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {completeMutation.isPending ? 'Saving...' : 'Continue'}
              </button>
            </div>
          )}

          {/* Step 3: Welcome */}
          {step === 'welcome' && (
            <div className="space-y-6">
              <div className="text-center">
                <div className="w-14 h-14 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-7 h-7 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-delft-blue dark:text-white">
                  You&apos;re all set!
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  Your publisher identity is configured. Here are some next steps to get started.
                </p>
              </div>

              <div className="space-y-2">
                <WelcomeLink
                  href="/api-keys"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                    </svg>
                  }
                  title="Generate an API key"
                  description="Create your first key to start signing content"
                />
                <WelcomeLink
                  href="/playground"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  }
                  title="Try the API playground"
                  description="Sign and verify content in your browser"
                />
                <WelcomeLink
                  href="/integrations"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                  }
                  title="Set up an integration"
                  description="WordPress, Ghost, or custom CMS"
                />
              </div>

              <Link href="/">
                <button className="w-full py-2.5 bg-gradient-to-r from-blue-ncs to-delft-blue text-white font-medium rounded-lg hover:opacity-90 transition-opacity">
                  Go to dashboard
                </button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function WelcomeLink({
  href,
  icon,
  title,
  description,
}: {
  href: string;
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted transition-colors group"
    >
      <div className="w-9 h-9 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center text-muted-foreground group-hover:text-blue-ncs transition-colors flex-shrink-0">
        {icon}
      </div>
      <div>
        <p className="text-sm font-medium text-delft-blue dark:text-white group-hover:text-blue-ncs transition-colors">
          {title}
        </p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
    </Link>
  );
}
