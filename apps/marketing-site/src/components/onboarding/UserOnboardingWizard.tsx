import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { useSession } from 'next-auth/react';
import { fetchApi } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';
import { useSearchParams } from 'next/navigation';

/**
 * UserOnboardingWizard: Accessible, modular onboarding wizard for collecting user and org info.
 * Step 1: Collects first/last name.
 * Step 2: Collects org name (and optionally role/title).
 * API: PATCH /api/v1/users/me, POST /api/v1/organization
 * Accessibility: Keyboard/focus, ARIA, error feedback.
 */
export const UserOnboardingWizard: React.FC = () => {
  const { data: session } = useSession();
  const { toast } = useToast();
  const searchParams = useSearchParams();
  const inviteToken = searchParams.get('invite') || null;
  const [step, setStep] = useState(1);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [orgName, setOrgName] = useState('');
  const [orgPreFilled, setOrgPreFilled] = useState(false);
  const [revenueTier, setRevenueTier] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Resume logic for returning users with incomplete profiles
  useEffect(() => {
    if (session?.user) {
      // Use explicit type for session.user
      const user = session.user as { first_name?: string; last_name?: string; organization?: { name?: string } };
      const { first_name, last_name, organization } = user;
      if (first_name && last_name) {
        setFirstName(first_name);
        setLastName(last_name);
        if (organization || inviteToken) {
          setStep(2); // Org step
          if (organization) {
            setOrgName(organization.name || '');
            setOrgPreFilled(true);
          }
        }
      }
    }
  }, [session, inviteToken]);

  // Step 1: Submit user info
  const handleUserInfoSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!firstName.trim() || !lastName.trim()) {
      setError('First and last name are required.');
      return;
    }
    if (!session?.accessToken) {
      setError('You must be logged in.');
      return;
    }
    try {
      setLoading(true);
      setError(null);
      await fetchApi('/api/v1/users/me', {
        method: 'PUT',
        token: session.accessToken,
        body: JSON.stringify({ first_name: firstName, last_name: lastName }),
        headers: { 'Content-Type': 'application/json' },
      });
      setStep(2);
    } catch {
      setError('Failed to save your name.');
      toast({ title: 'Error', description: 'Could not save user info.', variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Submit org info (handle invited user)
  const handleOrgInfoSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!orgName.trim() && !inviteToken) {
      setError('Organization name is required.');
      return;
    }
    if (!inviteToken && !revenueTier) {
      setError('Revenue tier is required.');
      return;
    }
    // Contact email is only required when *creating* an org, not joining or if prefilled
    if (!inviteToken && !orgPreFilled && !contactEmail.trim()) {
      setError('Main contact email is required.');
      return;
    }
    if (!session?.accessToken) {
      setError('You must be logged in.');
      return;
    }
    try {
      setLoading(true);
      setError(null);
      if (!inviteToken && !orgPreFilled) {
        // Only create org if not joining via invite and not pre-filled
        await fetchApi('/api/v1/organization', {
          method: 'POST',
          token: session.accessToken,
          body: JSON.stringify({ name: orgName, revenue_tier: revenueTier, contact_email: contactEmail || undefined }),
          headers: { 'Content-Type': 'application/json' },
        });
        toast({ title: 'Welcome!', description: `Organization "${orgName}" created.`, variant: 'success' });
        // Redirect to dashboard after successful org creation
        window.location.assign('/dashboard');
      } else {
        // If joining via invite, or org pre-filled, just proceed
        toast({ title: 'Welcome!', description: `Onboarding complete.`, variant: 'success' });
        window.location.assign('/dashboard');
      }
    } catch (err: unknown) { // Changed variable name for clarity
      // Default error message
      let specificErrorHandled = false;
      const toastTitle = 'Error'; // Changed to const
      let toastDescription = 'Could not complete organization step.';
      const toastVariant: "default" | "destructive" | "error" | "success" | "info" | null | undefined = 'error'; // Changed to const, added 'info' to type explicitly for clarity

      // Check if it's a fetchApi-style error with status and data
      if (err && typeof err === 'object' && 'status' in err && 'data' in err) {
        const apiError = err as { status: number; data?: { error?: { code?: string; message?: string } } }; // Type assertion
        if (apiError.status === 409 && apiError.data?.error?.code === 'ORGANIZATION_NAME_EXISTS') {
          specificErrorHandled = true;
          toast({
            title: 'Organization Exists',
            description: `The organization "${orgName}" already exists. Ask your admin to invite you. You can proceed to your dashboard.`,
            variant: 'info', // Changed from 'warning' to 'info'
            duration: 9000, // Longer duration
          });
          // We showed the toast, but still set local error state if needed
          setError(`Organization "${orgName}" already exists.`);
        } else if (apiError.data?.error?.message) {
           // Use backend error message if available and not handled above
          toastDescription = apiError.data.error.message;
        }
      } else if (err instanceof Error) {
          // Fallback to standard Error object message
         toastDescription = err.message;
      }

      // Show generic error toast ONLY if a specific one wasn't shown
      if (!specificErrorHandled) {
        setError(toastDescription); // Set local error state
        toast({ title: toastTitle, description: toastDescription, variant: toastVariant });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white dark:bg-zinc-900 dark:text-zinc-100 rounded shadow mt-12 transition-colors duration-300" role="main" aria-labelledby="onboarding-title">
      <span id="onboarding-status" className="sr-only" aria-live="polite">{loading ? "Loading..." : error ? error : step === 1 ? "User info step" : "Organization info step"}</span>
      {step === 1 && (
        <form onSubmit={handleUserInfoSubmit} aria-label="User Info Step" aria-describedby="onboarding-status" autoComplete="off">
          <h2 id="onboarding-title" className="text-xl font-bold mb-4">Welcome! Let&apos;s get to know you</h2>
          <div className="mb-4">
            <Label htmlFor="firstName">First Name</Label>
            <Input id="firstName" value={firstName} onChange={e => setFirstName(e.target.value)} required autoFocus aria-required="true" aria-label="First Name" />
          </div>
          <div className="mb-4">
            <Label htmlFor="lastName">Last Name</Label>
            <Input id="lastName" value={lastName} onChange={e => setLastName(e.target.value)} required aria-required="true" aria-label="Last Name" />
          </div>
          {error && <div role="alert" className="text-red-600 mb-2" aria-live="assertive">{error}</div>}
          <Button type="submit" disabled={loading} className="w-full" aria-disabled={loading} aria-busy={loading} tabIndex={0}>Next</Button>
        </form>
      )}
      {step === 2 && (
        <form onSubmit={handleOrgInfoSubmit} aria-label="Organization Info Step" aria-describedby="onboarding-status" autoComplete="off">
          <h2 className="text-xl font-bold mb-4">{inviteToken || orgPreFilled ? "Join Your Organization" : "Create Your Organization"}</h2>
          <div className="mb-4">
            <Label htmlFor="orgName">Organization Name</Label>
            <Input id="orgName" value={orgName} onChange={e => setOrgName(e.target.value)} required={!inviteToken} autoFocus aria-required={!inviteToken} aria-label="Organization Name" disabled={!!inviteToken || orgPreFilled} />
          </div>
          {!inviteToken && !orgPreFilled && (
            <div className="mb-4">
              <Label htmlFor="revenueTier">Revenue Tier</Label>
              <select
                id="revenueTier"
                value={revenueTier}
                onChange={e => setRevenueTier(e.target.value)}
                required
                aria-required="true"
                aria-label="Revenue Tier"
                className="block w-full mt-1 p-2 rounded border border-gray-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-gray-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">Select a tier...</option>
                <option value="free_agpl">Free (AGPL)</option>
                <option value="growth">Growth</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </div>
          )}
          {!inviteToken && !orgPreFilled && (
            <div className="mb-4">
              <Label htmlFor="contactEmail">Main Contact Email</Label>
              <Input
                id="contactEmail"
                type="email"
                value={contactEmail}
                onChange={e => setContactEmail(e.target.value)}
                aria-label="Main Contact Email"
                placeholder="your@email.com"
                className="dark:bg-zinc-800 dark:text-zinc-100"
                required
                aria-required="true"
              />
            </div>
          )}
          {error && <div role="alert" className="text-red-600 mb-2" aria-live="assertive">{error}</div>}
          <Button type="submit" disabled={loading} className="w-full" aria-disabled={loading} aria-busy={loading} tabIndex={0}>{inviteToken || orgPreFilled ? "Finish" : "Finish & Create Organization"}</Button>
        </form>
      )}
    </div>
  );
};
