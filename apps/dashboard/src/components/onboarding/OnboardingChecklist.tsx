'use client';

/**
 * Server-Backed Onboarding Checklist
 *
 * TEAM_191: Replaces the old localStorage-based OnboardingModal with a
 * persistent, server-tracked checklist that measures real product milestones.
 * Displayed as a card on the dashboard home page.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import Link from 'next/link';
import { toast } from 'sonner';
import apiClient, { type OnboardingStep } from '../../lib/api';

interface OnboardingChecklistProps {
  className?: string;
}

const stepIcons: Record<string, React.ReactNode> = {
  account_created: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
    </svg>
  ),
  first_api_key: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
    </svg>
  ),
  first_api_call: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  ),
  first_document_signed: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  first_verification: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  ),
};

export function OnboardingChecklist({ className = '' }: OnboardingChecklistProps) {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();

  const statusQuery = useQuery({
    queryKey: ['onboarding-status'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getOnboardingStatus(accessToken);
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
    retry: 1,
    staleTime: 30_000,
  });

  const completeMutation = useMutation({
    mutationFn: async (stepId: string) => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.completeOnboardingStep(accessToken, stepId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['onboarding-status'] });
    },
  });

  const dismissMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.dismissOnboarding(accessToken);
    },
    onSuccess: () => {
      toast.success('Onboarding checklist dismissed.');
      queryClient.invalidateQueries({ queryKey: ['onboarding-status'] });
    },
    onError: () => {
      toast.error('Failed to dismiss checklist.');
    },
  });

  // Don't render while loading, on error, or if dismissed/completed
  if (statusQuery.isLoading || statusQuery.isError) return null;
  const data = statusQuery.data;
  if (!data || data.dismissed || data.all_completed) return null;

  const progressPercent = data.total_count > 0
    ? Math.round((data.completed_count / data.total_count) * 100)
    : 0;

  return (
    <div className={`bg-white dark:bg-slate-800 rounded-xl border border-border overflow-hidden ${className}`}>
      {/* Header */}
      <div className="p-5 pb-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-gradient-to-br from-blue-ncs to-delft-blue rounded-lg flex items-center justify-center text-white">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <div>
            <h3 className="font-bold text-delft-blue dark:text-white text-sm">Getting Started</h3>
            <p className="text-xs text-muted-foreground">
              {data.completed_count} of {data.total_count} complete
            </p>
          </div>
        </div>
        <button
          onClick={() => dismissMutation.mutate()}
          disabled={dismissMutation.isPending}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors px-2 py-1 rounded hover:bg-muted"
          title="Dismiss checklist"
        >
          Dismiss
        </button>
      </div>

      {/* Progress bar */}
      <div className="px-5 pb-4">
        <div className="h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-ncs to-delft-blue rounded-full transition-all duration-700 ease-out"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Steps */}
      <div className="px-5 pb-5 space-y-1">
        {data.steps.map((step: OnboardingStep) => {
          const icon = stepIcons[step.step_id] || stepIcons.account_created;
          const isClickable = !step.completed && step.action_url;

          const content = (
            <div
              className={`flex items-center gap-3 p-2.5 rounded-lg transition-colors ${
                step.completed
                  ? 'opacity-60'
                  : isClickable
                  ? 'hover:bg-muted cursor-pointer'
                  : ''
              }`}
            >
              {/* Completion indicator */}
              <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                step.completed
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-400 dark:text-slate-500'
              }`}>
                {step.completed ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <span className="text-xs font-medium">{icon}</span>
                )}
              </div>

              {/* Step info */}
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${
                  step.completed
                    ? 'text-muted-foreground line-through'
                    : 'text-delft-blue dark:text-white'
                }`}>
                  {step.title}
                </p>
                {!step.completed && (
                  <p className="text-xs text-muted-foreground truncate">{step.description}</p>
                )}
              </div>

              {/* Arrow for actionable steps */}
              {isClickable && (
                <svg className="w-4 h-4 text-muted-foreground flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              )}
            </div>
          );

          if (isClickable && step.action_url) {
            return (
              <Link key={step.step_id} href={step.action_url}>
                {content}
              </Link>
            );
          }

          return <div key={step.step_id}>{content}</div>;
        })}
      </div>
    </div>
  );
}
