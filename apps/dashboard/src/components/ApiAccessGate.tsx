'use client';

/**
 * API Access Gate Component
 * 
 * TEAM_006: Gates API key generation behind approval workflow.
 * Shows different UI based on user's API access status:
 * - not_requested: Show request form
 * - pending: Show pending status
 * - approved: Show children (API keys page)
 * - denied: Show denial reason with option to reapply
 */

import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { toast } from 'sonner';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@encypher/design-system';
import { Textarea } from './ui/textarea';
import apiClient, { ApiAccessStatusType } from '../lib/api';

interface ApiAccessGateProps {
  children: React.ReactNode;
}

export function ApiAccessGate({ children }: ApiAccessGateProps) {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();
  
  const [useCase, setUseCase] = useState('');
  const [showRequestForm, setShowRequestForm] = useState(false);

  // Fetch current API access status
  const statusQuery = useQuery({
    queryKey: ['api-access-status'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getApiAccessStatus(accessToken);
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
    retry: 1,
  });

  // Request API access mutation
  const requestMutation = useMutation({
    mutationFn: async (useCaseText: string) => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.requestApiAccess(accessToken, useCaseText);
    },
    onSuccess: () => {
      toast.success('API access request submitted! We\'ll review it shortly.');
      setUseCase('');
      setShowRequestForm(false);
      queryClient.invalidateQueries({ queryKey: ['api-access-status'] });
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to submit request');
    },
  });

  const handleSubmitRequest = (e: React.FormEvent) => {
    e.preventDefault();
    if (useCase.trim().length < 20) {
      toast.error('Please provide a more detailed use case (at least 20 characters)');
      return;
    }
    requestMutation.mutate(useCase.trim());
  };

  // Loading state
  if (statusQuery.isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-ncs"></div>
      </div>
    );
  }

  // Error state - treat as not_requested for graceful degradation
  const status: ApiAccessStatusType = statusQuery.data?.status || 'not_requested';

  // If approved, show the children (API keys page)
  if (status === 'approved') {
    return <>{children}</>;
  }

  // Not requested - show request form
  if (status === 'not_requested' || (status === 'denied' && showRequestForm)) {
    return (
      <div className="max-w-2xl mx-auto py-8">
        <Card className="border-2 border-blue-ncs/20">
          <CardHeader className="text-center pb-2">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-ncs/10 flex items-center justify-center">
              <svg className="w-8 h-8 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
            </div>
            <CardTitle className="text-2xl">Request API Access</CardTitle>
            <CardDescription className="text-base mt-2">
              {status === 'denied' 
                ? 'Your previous request was denied. Please provide more details about your use case.'
                : 'To generate API keys, please tell us how you plan to use the Encypher API.'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmitRequest} className="space-y-6">
              <div>
                <label htmlFor="use-case" className="block text-sm font-medium text-foreground mb-2">
                  How will you use the API?
                </label>
                <Textarea
                  id="use-case"
                  placeholder="Describe your use case... (e.g., 'I'm building a content verification tool for my news publication to authenticate articles with cryptographic proof.')"
                  value={useCase}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setUseCase(e.target.value)}
                  rows={5}
                  className="w-full"
                  disabled={requestMutation.isPending}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Minimum 20 characters. Be specific about your project and how you'll use content provenance.
                </p>
              </div>
              
              <div className="flex gap-3">
                {status === 'denied' && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowRequestForm(false)}
                    disabled={requestMutation.isPending}
                  >
                    Cancel
                  </Button>
                )}
                <Button
                  type="submit"
                  variant="primary"
                  className="flex-1"
                  disabled={useCase.trim().length < 20 || requestMutation.isPending}
                >
                  {requestMutation.isPending ? 'Submitting...' : 'Submit Request'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Pending - show waiting status
  if (status === 'pending') {
    return (
      <div className="max-w-2xl mx-auto py-8">
        <Card className="border-2 border-amber-500/20 bg-amber-50/50 dark:bg-amber-950/20">
          <CardHeader className="text-center pb-2">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-500/10 flex items-center justify-center">
              <svg className="w-8 h-8 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <CardTitle className="text-2xl text-amber-800 dark:text-amber-200">
              Request Pending Review
            </CardTitle>
            <CardDescription className="text-base mt-2 text-amber-700 dark:text-amber-300">
              Your API access request is being reviewed. We'll notify you once it's approved.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            {statusQuery.data?.use_case && (
              <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-left mb-4">
                <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Your submitted use case:</p>
                <p className="text-sm text-foreground">{statusQuery.data.use_case}</p>
              </div>
            )}
            <p className="text-sm text-muted-foreground">
              This usually takes less than 24 hours. Check back soon!
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Denied - show denial reason with option to reapply
  if (status === 'denied') {
    return (
      <div className="max-w-2xl mx-auto py-8">
        <Card className="border-2 border-destructive/20 bg-destructive/5">
          <CardHeader className="text-center pb-2">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-destructive/10 flex items-center justify-center">
              <svg className="w-8 h-8 text-destructive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <CardTitle className="text-2xl text-destructive">
              Request Not Approved
            </CardTitle>
            <CardDescription className="text-base mt-2">
              Unfortunately, your API access request was not approved at this time.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            {statusQuery.data?.denial_reason && (
              <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-left">
                <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Reason:</p>
                <p className="text-sm text-foreground">{statusQuery.data.denial_reason}</p>
              </div>
            )}
            <p className="text-sm text-muted-foreground">
              You can submit a new request with more details about your use case.
            </p>
            <Button
              variant="primary"
              onClick={() => setShowRequestForm(true)}
            >
              Submit New Request
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Fallback
  return <>{children}</>;
}

export default ApiAccessGate;
