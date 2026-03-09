'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import Link from 'next/link';
import { useEffect } from 'react';
import apiClient from '../../lib/api';

interface OnboardingLaunchpadProps {
  className?: string;
  hasApiKeys: boolean;
  documentsSigned: number;
  verifications: number;
}

type LaunchpadStep = {
  title: string;
  description: string;
  href: string;
  completed: boolean;
};

function getPublisherPlatformLabel(platform: string | null | undefined, customLabel?: string | null) {
  if (platform === 'wordpress') return 'WordPress';
  if (platform === 'ghost') return 'Ghost';
  if (platform === 'substack') return 'Substack';
  if (platform === 'medium') return 'Medium';
  if (platform === 'custom' || platform === 'custom_cms') return customLabel || 'your custom CMS';
  return 'your publishing stack';
}

export function OnboardingLaunchpad({
  className = '',
  hasApiKeys,
  documentsSigned,
  verifications,
}: OnboardingLaunchpadProps) {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();

  const setupQuery = useQuery({
    queryKey: ['setup-status'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getSetupStatus(accessToken);
    },
    enabled: Boolean(accessToken),
    staleTime: 60_000,
    refetchOnWindowFocus: false,
  });

  const onboardingStatusQuery = useQuery({
    queryKey: ['onboarding-status'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getOnboardingStatus(accessToken);
    },
    enabled: Boolean(accessToken),
    staleTime: 30_000,
    refetchOnWindowFocus: false,
  });

  const completeStepMutation = useMutation({
    mutationFn: async (stepId: string) => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.completeOnboardingStep(accessToken, stepId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['onboarding-status'] });
    },
  });

  const setup = setupQuery.data;
  const onboardingStatus = onboardingStatusQuery.data;
  const workflow = setup?.workflow_category ?? (setup?.dashboard_layout === 'enterprise' ? 'enterprise' : 'media_publishing');
  const platform = setup?.publisher_platform;
  const isPublisher = workflow === 'media_publishing';
  const isAiGovernance = workflow === 'ai_provenance_governance';
  const integrationStarted = hasApiKeys || documentsSigned > 0 || verifications > 0;

  useEffect(() => {
    if (!setup?.setup_completed || !onboardingStatus || completeStepMutation.isPending) {
      return;
    }

    const stepMap = new Map(onboardingStatus.steps.map((step) => [step.step_id, step.completed]));

    if (hasApiKeys && !stepMap.get('first_api_key')) {
      completeStepMutation.mutate('first_api_key');
      return;
    }

    if (documentsSigned > 0 && !stepMap.get('first_document_signed')) {
      completeStepMutation.mutate('first_document_signed');
      return;
    }

    if (verifications > 0 && !stepMap.get('first_verification')) {
      completeStepMutation.mutate('first_verification');
    }
  }, [
    completeStepMutation,
    documentsSigned,
    hasApiKeys,
    onboardingStatus,
    setup?.setup_completed,
    verifications,
  ]);

  if (setupQuery.isLoading || setupQuery.isError || !setup?.setup_completed) {
    return null;
  }

  let eyebrow = 'Recommended next steps';
  let title = 'Get your team live with Encypher';
  let description = 'We tailored this workspace to the workflow you selected. Follow the guided steps below to reach first value quickly.';
  let primaryHref = '/docs';
  let primaryLabel = 'Open implementation guide';
  let secondaryHref = '/api-keys';
  let secondaryLabel = 'Generate an API key';
  let steps: LaunchpadStep[] = [];

  if (isPublisher) {
    const platformLabel = getPublisherPlatformLabel(platform, setup.publisher_platform_custom);
    eyebrow = 'Publisher quick start';
    title = `Get ${platformLabel} publishing with proof of origin`;
    description = 'Start with the fastest path for publishers: connect your CMS, sign your first piece of content, then verify that proof travels with it.';

    if (!integrationStarted) {
      primaryHref = '/integrations';
      primaryLabel = platform === 'wordpress' ? 'Set up the WordPress plugin' : 'Open publisher integrations';
      secondaryHref = '/docs';
      secondaryLabel = 'View publisher docs';
    } else if (documentsSigned === 0) {
      primaryHref = '/playground';
      primaryLabel = 'Sign your first document';
      secondaryHref = '/integrations';
      secondaryLabel = 'Continue CMS setup';
    } else if (verifications === 0) {
      primaryHref = '/playground';
      primaryLabel = 'Verify signed content';
      secondaryHref = '/analytics';
      secondaryLabel = 'View content performance';
    } else {
      primaryHref = '/analytics';
      primaryLabel = 'View protected content';
      secondaryHref = '/integrations';
      secondaryLabel = 'Expand your publishing setup';
    }

    steps = [
      {
        title: platform === 'wordpress' ? 'Install the WordPress plugin' : `Connect ${platformLabel}`,
        description: 'Use the guided integration path built for your publishing workflow.',
        href: '/integrations',
        completed: integrationStarted,
      },
      {
        title: 'Sign your first article or document',
        description: 'Create cryptographic proof of origin that survives downstream distribution.',
        href: '/playground',
        completed: documentsSigned > 0,
      },
      {
        title: 'Verify how proof appears publicly',
        description: 'Confirm readers and partners can validate authenticity with confidence.',
        href: '/playground',
        completed: verifications > 0,
      },
    ];
  } else if (isAiGovernance) {
    eyebrow = 'AI provenance & governance';
    title = 'Stand up attested AI workflow infrastructure';
    description = 'We will guide you through the fastest path to governance-ready provenance: credentials, first signed payload, and verification-ready evidence.';

    if (!hasApiKeys) {
      primaryHref = '/api-keys';
      primaryLabel = 'Generate your first API key';
      secondaryHref = '/docs';
      secondaryLabel = 'Open governance docs';
    } else if (documentsSigned === 0) {
      primaryHref = '/playground';
      primaryLabel = 'Create your first attested record';
      secondaryHref = '/docs';
      secondaryLabel = 'Review AI governance docs';
    } else if (verifications === 0) {
      primaryHref = '/playground';
      primaryLabel = 'Verify your attested output';
      secondaryHref = '/docs';
      secondaryLabel = 'Review governance docs';
    } else {
      primaryHref = '/docs';
      primaryLabel = 'Continue implementation';
      secondaryHref = '/settings';
      secondaryLabel = 'Review workspace settings';
    }

    steps = [
      {
        title: 'Create secure credentials',
        description: 'Provision the credentials your team needs for governed integrations.',
        href: '/api-keys',
        completed: hasApiKeys,
      },
      {
        title: 'Sign your first governed payload',
        description: 'Generate an attested output your team can validate and operationalize.',
        href: '/playground',
        completed: documentsSigned > 0,
      },
      {
        title: 'Verify and document evidence',
        description: 'Confirm the workflow is verification-ready before broader rollout.',
        href: '/playground',
        completed: verifications > 0,
      },
    ];
  } else {
    eyebrow = 'Enterprise rollout';
    title = 'Launch provenance infrastructure for your team';
    description = 'We tailored the dashboard for implementation teams. Start with credentials, validate a first workflow, then expand the rollout with confidence.';

    if (!hasApiKeys) {
      primaryHref = '/api-keys';
      primaryLabel = 'Generate your first API key';
      secondaryHref = '/docs';
      secondaryLabel = 'Open implementation docs';
    } else if (documentsSigned === 0) {
      primaryHref = '/playground';
      primaryLabel = 'Run your first signing workflow';
      secondaryHref = '/docs';
      secondaryLabel = 'Review implementation steps';
    } else if (verifications === 0) {
      primaryHref = '/playground';
      primaryLabel = 'Verify signed output';
      secondaryHref = '/settings';
      secondaryLabel = 'Review workspace settings';
    } else {
      primaryHref = '/settings';
      primaryLabel = 'Prepare team rollout';
      secondaryHref = '/docs';
      secondaryLabel = 'Continue implementation';
    }

    steps = [
      {
        title: 'Create credentials for your implementation',
        description: 'Generate a key and align the integration path with your technical team.',
        href: '/api-keys',
        completed: hasApiKeys,
      },
      {
        title: 'Run a first signing workflow',
        description: 'Validate the happy path before broadening the rollout.',
        href: '/playground',
        completed: documentsSigned > 0,
      },
      {
        title: 'Verify output and prepare rollout',
        description: 'Confirm trust signals and move toward broader team adoption.',
        href: '/playground',
        completed: verifications > 0,
      },
    ];
  }

  return (
    <div className={`bg-white dark:bg-slate-800 rounded-2xl border border-border overflow-hidden ${className}`}>
      <div className="p-6 lg:p-7 bg-gradient-to-r from-delft-blue/5 via-blue-ncs/5 to-columbia-blue/10 border-b border-border">
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-5">
          <div className="max-w-3xl">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-ncs mb-2">{eyebrow}</p>
            <h2 className="text-2xl font-bold text-delft-blue dark:text-white mb-2">{title}</h2>
            <p className="text-sm text-muted-foreground leading-6">{description}</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3 lg:flex-col xl:flex-row lg:min-w-[260px]">
            <Link href={primaryHref}>
              <button className="w-full inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-ncs to-delft-blue text-white font-medium rounded-lg hover:opacity-90 transition-opacity">
                {primaryLabel}
              </button>
            </Link>
            <Link href={secondaryHref}>
              <button className="w-full inline-flex items-center justify-center gap-2 px-5 py-2.5 border border-blue-ncs/30 text-blue-ncs font-medium rounded-lg hover:bg-blue-ncs/5 transition-colors">
                {secondaryLabel}
              </button>
            </Link>
          </div>
        </div>
      </div>

      <div className="p-6 lg:p-7 grid md:grid-cols-3 gap-4">
        {steps.map((step, index) => (
          <Link key={step.title} href={step.href} className="group rounded-xl border border-border p-4 hover:border-blue-ncs/40 hover:bg-muted/40 transition-colors">
            <div className="flex items-start gap-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-semibold ${
                step.completed
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                  : 'bg-blue-ncs/10 text-blue-ncs'
              }`}>
                {step.completed ? '✓' : index + 1}
              </div>
              <div>
                <p className="text-sm font-semibold text-delft-blue dark:text-white group-hover:text-blue-ncs transition-colors">
                  {step.title}
                </p>
                <p className="text-xs text-muted-foreground mt-1 leading-5">
                  {step.description}
                </p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
