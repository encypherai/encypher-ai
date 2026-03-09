'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { useState } from 'react';
import { toast } from 'sonner';
import apiClient, {
  type AccountType,
  type DashboardLayoutPreference,
  type PublisherPlatform,
  type WorkflowCategory,
} from '../../lib/api';

type WizardStep = 'workflow' | 'layout' | 'account_type' | 'display_name' | 'publisher_platform';

const publisherPlatformOptions: Array<{
  value: PublisherPlatform;
  label: string;
  description: string;
}> = [
  {
    value: 'wordpress',
    label: 'WordPress',
    description: 'Use the WordPress plugin and publisher setup guide.',
  },
  {
    value: 'ghost',
    label: 'Ghost',
    description: 'Connect your Ghost site and start auto-signing posts.',
  },
  {
    value: 'substack',
    label: 'Substack',
    description: 'Track newsletter provenance and prepare for future automation.',
  },
  {
    value: 'medium',
    label: 'Medium',
    description: 'Use Encypher with syndicated and hosted article workflows.',
  },
  {
    value: 'custom',
    label: 'Custom CMS',
    description: 'We will route you to the API and integration docs.',
  },
];

export function SetupWizard() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();

  const [step, setStep] = useState<WizardStep>('workflow');
  const [workflowCategory, setWorkflowCategory] = useState<WorkflowCategory | null>(null);
  const [accountType, setAccountType] = useState<AccountType | null>(null);
  const [dashboardLayout, setDashboardLayout] = useState<DashboardLayoutPreference>('publisher');
  const [displayName, setDisplayName] = useState(
    session?.user?.name || ''
  );
  const [publisherPlatform, setPublisherPlatform] = useState<PublisherPlatform>('wordpress');
  const [publisherPlatformCustom, setPublisherPlatformCustom] = useState('');

  const progressSteps = workflowCategory === 'media_publishing'
    ? ['workflow', 'account_type', 'display_name', 'publisher_platform']
    : workflowCategory
      ? ['workflow', 'layout', 'account_type', 'display_name']
      : ['workflow', 'layout', 'account_type', 'display_name'];

  const completeMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken || !accountType || !workflowCategory) throw new Error('Missing data');
      return apiClient.completeSetup(accessToken, {
        account_type: accountType,
        display_name: displayName.trim(),
        workflow_category: workflowCategory,
        dashboard_layout: dashboardLayout,
        publisher_platform: dashboardLayout === 'publisher' ? publisherPlatform : undefined,
        publisher_platform_custom:
          dashboardLayout === 'publisher' && publisherPlatform === 'custom'
            ? publisherPlatformCustom.trim()
            : undefined,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['setup-status'] });
      queryClient.invalidateQueries({ queryKey: ['onboarding-status'] });
      toast.success('Setup complete. Your dashboard has been tailored to your workflow.');
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
    if (workflowCategory === 'media_publishing') {
      setStep('publisher_platform');
      return;
    }
    completeMutation.mutate();
  };

  const handleSubmitPublisherPlatform = () => {
    if (publisherPlatform === 'custom' && !publisherPlatformCustom.trim()) {
      toast.error('Please tell us which publishing platform you use.');
      return;
    }
    completeMutation.mutate();
  };

  return (
    <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
        {/* Progress indicator */}
        <div className="flex gap-1 px-6 pt-6">
          {progressSteps.map((s, i) => (
            <div
              key={s}
              className={`h-1 flex-1 rounded-full transition-colors ${
                i <= progressSteps.indexOf(step)
                  ? 'bg-gradient-to-r from-blue-ncs to-delft-blue'
                  : 'bg-slate-200 dark:bg-slate-700'
              }`}
            />
          ))}
        </div>

        <div className="p-6">
          {step === 'workflow' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-delft-blue dark:text-white">
                  What are you trying to get up and running?
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  We&apos;ll tailor the dashboard, language, and next steps to your workflow. Publishers are the fastest path, but we also support enterprise integrity and AI governance use cases.
                </p>
              </div>

              <div className="space-y-3">
                <button
                  onClick={() => {
                    setWorkflowCategory('media_publishing');
                    setDashboardLayout('publisher');
                    setStep('account_type');
                  }}
                  className="w-full flex items-start gap-4 p-4 rounded-xl border-2 border-blue-ncs bg-blue-50/60 dark:bg-blue-900/10 hover:border-blue-ncs transition-colors text-left group"
                >
                  <div className="w-10 h-10 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex items-center justify-center text-blue-ncs flex-shrink-0 mt-0.5">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h14a2 2 0 012 2v14a2 2 0 01-2 2zM7 8h10M7 12h10M7 16h6" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-semibold text-delft-blue dark:text-white group-hover:text-blue-ncs transition-colors">
                      Yes — I publish media or content
                    </p>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      Best for publishers, journalists, newsrooms, blogs, and CMS-driven teams. We&apos;ll route you to WordPress, Ghost, or API-based publishing setup.
                    </p>
                  </div>
                </button>

                <button
                  onClick={() => {
                    setStep('layout');
                  }}
                  className="w-full flex items-start gap-4 p-4 rounded-xl border-2 border-border hover:border-blue-ncs transition-colors text-left group"
                >
                  <div className="w-10 h-10 bg-purple-50 dark:bg-purple-900/20 rounded-lg flex items-center justify-center text-purple-600 flex-shrink-0 mt-0.5">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7h18M6 11h12M9 15h6M4 21h16a1 1 0 001-1V4a1 1 0 00-1-1H4a1 1 0 00-1 1v16a1 1 0 001 1z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-semibold text-delft-blue dark:text-white group-hover:text-blue-ncs transition-colors">
                      No — take me to enterprise or AI governance
                    </p>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      Best for enterprise integrity, attested document workflows, AI provenance, and governance-led rollouts.
                    </p>
                  </div>
                </button>
              </div>
            </div>
          )}

          {step === 'layout' && (
            <div className="space-y-6">
              <div>
                <button
                  onClick={() => setStep('workflow')}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors mb-3 flex items-center gap-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back
                </button>
                <h2 className="text-xl font-bold text-delft-blue dark:text-white">
                  Which non-publisher workflow best matches your needs?
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  We&apos;ll prioritize the language, guidance, and actions that get your team live fastest.
                </p>
              </div>

              <div className="space-y-3">
                <button
                  onClick={() => {
                    setWorkflowCategory('enterprise');
                    setDashboardLayout('enterprise');
                    setStep('account_type');
                  }}
                  className={`w-full flex items-start gap-4 p-4 rounded-xl border-2 transition-colors text-left group ${
                    workflowCategory === 'enterprise' ? 'border-blue-ncs bg-blue-50/50 dark:bg-blue-900/10' : 'border-border hover:border-blue-ncs'
                  }`}
                >
                  <div className="w-10 h-10 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex items-center justify-center text-blue-ncs flex-shrink-0 mt-0.5">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7h18M6 11h12M9 15h6M4 21h16a1 1 0 001-1V4a1 1 0 00-1-1H4a1 1 0 00-1 1v16a1 1 0 001 1z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-semibold text-delft-blue dark:text-white group-hover:text-blue-ncs transition-colors">
                      Enterprise integrity workflow
                    </p>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      Best for teams who need API keys, implementation guides, and controlled rollout across business systems.
                    </p>
                  </div>
                </button>

                <button
                  onClick={() => {
                    setDashboardLayout('enterprise');
                    setWorkflowCategory('ai_provenance_governance');
                    setStep('account_type');
                  }}
                  className={`w-full flex items-start gap-4 p-4 rounded-xl border-2 transition-colors text-left group ${
                    workflowCategory === 'ai_provenance_governance' ? 'border-blue-ncs bg-blue-50/50 dark:bg-blue-900/10' : 'border-border hover:border-blue-ncs'
                  }`}
                >
                  <div className="w-10 h-10 bg-purple-50 dark:bg-purple-900/20 rounded-lg flex items-center justify-center text-purple-600 flex-shrink-0 mt-0.5">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-semibold text-delft-blue dark:text-white group-hover:text-blue-ncs transition-colors">
                      AI / LLM provenance & governance
                    </p>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      Best for regulated or high-stakes AI workflows that need attestation, governance controls, and evidence-ready records.
                    </p>
                  </div>
                </button>
              </div>
            </div>
          )}

          {step === 'account_type' && (
            <div className="space-y-6">
              <div>
                <button
                  onClick={() => setStep(workflowCategory === 'media_publishing' ? 'workflow' : 'layout')}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors mb-3 flex items-center gap-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back
                </button>
                <h2 className="text-xl font-bold text-delft-blue dark:text-white">
                  Who is this setup for?
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  This helps us tailor language, identity defaults, and recommended next actions.
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
                      Individual
                    </p>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      A single operator, creator, consultant, or practitioner getting set up personally.
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
                      Organization or team
                    </p>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      A newsroom, company, legal team, product group, or cross-functional rollout.
                    </p>
                  </div>
                </button>
              </div>
            </div>
          )}

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
                  {workflowCategory === 'media_publishing'
                    ? accountType === 'individual'
                      ? 'What name should appear on your signed content?'
                      : "What's your publication or organization name?"
                    : accountType === 'individual'
                      ? 'What name should we use for your workspace?'
                      : 'What is your team or organization called?'}
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  {workflowCategory === 'media_publishing'
                    ? accountType === 'individual'
                      ? 'This is what readers see when they verify your content.'
                      : 'This appears on published content signed by your team.'
                    : 'We use this to personalize your workspace, rollout guidance, and integration path.'}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  {accountType === 'individual' ? 'Your name' : 'Organization name'}
                </label>
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder={accountType === 'individual' ? 'e.g. Sarah Chen' : workflowCategory === 'media_publishing' ? 'e.g. The Ency Times' : 'e.g. Acme Legal Ops'}
                  className="w-full px-4 py-2.5 rounded-lg border border-border bg-white dark:bg-slate-800 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-blue-ncs focus:border-transparent"
                  autoFocus
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSubmitIdentity();
                  }}
                />
                <p className="text-xs text-muted-foreground mt-2">
                  {workflowCategory === 'media_publishing'
                    ? accountType === 'individual'
                      ? 'Signed content will show: "Signed by [your name] · Powered by Encypher"'
                      : 'Signed content will show: "Signed by [your name] at [org name] · Powered by Encypher"'
                    : 'This helps us keep your setup clear and aligned with your rollout stage.'}
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

          {step === 'publisher_platform' && (
            <div className="space-y-6">
              <div>
                <button
                  onClick={() => setStep('display_name')}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors mb-3 flex items-center gap-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back
                </button>
                <h2 className="text-xl font-bold text-delft-blue dark:text-white">
                  What platform do you publish with?
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  We use this to route you to the right guides and track publisher adoption internally.
                </p>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  Publishing platform
                </label>
                <select
                  value={publisherPlatform}
                  onChange={(e) => setPublisherPlatform(e.target.value as PublisherPlatform)}
                  className="w-full px-4 py-2.5 rounded-lg border border-border bg-white dark:bg-slate-800 text-foreground focus:outline-none focus:ring-2 focus:ring-blue-ncs focus:border-transparent"
                >
                  {publisherPlatformOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-muted-foreground">
                  {publisherPlatformOptions.find((option) => option.value === publisherPlatform)?.description}
                </p>
              </div>

              {publisherPlatform === 'custom' && (
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    Platform name
                  </label>
                  <input
                    type="text"
                    value={publisherPlatformCustom}
                    onChange={(e) => setPublisherPlatformCustom(e.target.value)}
                    placeholder="e.g. Arc XP"
                    className="w-full px-4 py-2.5 rounded-lg border border-border bg-white dark:bg-slate-800 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-blue-ncs focus:border-transparent"
                    autoFocus
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleSubmitPublisherPlatform();
                    }}
                  />
                </div>
              )}

              <button
                onClick={handleSubmitPublisherPlatform}
                disabled={completeMutation.isPending || (publisherPlatform === 'custom' && !publisherPlatformCustom.trim())}
                className="w-full py-2.5 bg-gradient-to-r from-blue-ncs to-delft-blue text-white font-medium rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {completeMutation.isPending ? 'Saving...' : 'Finish setup'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
