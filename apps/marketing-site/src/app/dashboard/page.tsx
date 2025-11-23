/**
 * DashboardClient Component
 *
 * - Handles authenticated dashboard view for users.
 * - Fetches organization and license data using secure hooks.
 * - Provides robust error handling and user feedback for session/data issues.
 * - Ensures session is fully loaded before rendering dashboard content.
 * - Logs error details for debugging in development.
 *
 * UX: Shows loading spinners, actionable error messages, and clear data state.
 */
"use client";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { OrganizationPanel } from "@/components/dashboard/OrganizationPanel";
import { InvitationsPanel } from "@/components/dashboard/InvitationsPanel";
import { KeysPanel } from "@/components/dashboard/KeysPanel";
import { SettingsPanel } from "@/components/dashboard/SettingsPanel";
import EnterpriseToolsPanel from "@/components/dashboard/EnterpriseToolsPanel";
import { useSession, signOut } from "next-auth/react";
import { useEffect, useState, useCallback } from "react";
import { UserOnboardingWizard } from "@/components/onboarding/UserOnboardingWizard";
import { fetchApi, AuthError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { AlertCircle, RefreshCw } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

export default function DashboardPage() {
  const { data: session, status, update: updateSession } = useSession();
  const [userProfile, setUserProfile] = useState<{ first_name?: string; last_name?: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const { toast } = useToast();

  const handleSignOut = useCallback(async () => {
    await signOut({ redirect: true, callbackUrl: '/' });
  }, []);

  const fetchUserProfile = useCallback(async () => {
    if (!session?.accessToken) return;
    try {
      setLoading(true);
      setError(null);
      setErrorCode(null);
      
      // Debug: Log the token being used
      console.log('[Dashboard] Using accessToken from session:', 
        session.accessToken ? `${session.accessToken.substring(0, 20)}...` : 'undefined');
      
      const res = await fetchApi("/api/v1/users/me", {
        method: "GET",
        token: session.accessToken
      });
      console.log('[Dashboard][userProfile]', res); // Debug: log actual profile
      setUserProfile(res as { first_name?: string; last_name?: string } | null);
    } catch (err) {
      console.error('[Dashboard] Error fetching user profile:', err);
      
      // Handle specific authentication errors
      if (err instanceof AuthError) {
        if (err.code === 'TOKEN_EXPIRED') {
          setError("Your session has expired. Please sign in again.");
          setErrorCode('TOKEN_EXPIRED');
          toast({
            title: "Session Expired",
            description: "Your session has expired. Please sign in again.",
            variant: "error",
          });
        } else if (err.code === 'USER_NOT_FOUND') {
          setError("User account not found. You may need to complete the registration process.");
          setErrorCode('USER_NOT_FOUND');
          toast({
            title: "User Not Found",
            description: "Your user account was not found. You may need to complete the registration process.",
            variant: "error",
          });
        } else if (err.code === 'INVALID_UUID_FORMAT') {
          setError("Invalid user identifier. Please sign out and sign in again.");
          setErrorCode('INVALID_UUID_FORMAT');
          toast({
            title: "Authentication Error",
            description: "Invalid user identifier. Please sign out and sign in again.",
            variant: "error",
          });
        } else {
          setError(`Authentication error: ${err.message}`);
          setErrorCode('AUTH_ERROR');
        }
      } else if (err && typeof err === 'object' && 'error' in err && err.error) {
        // Handle structured error responses
        const errorObj = err.error as { code?: string; message?: string };
        if (errorObj.code === 'USER_NOT_FOUND') {
          setError("User account not found. You may need to complete the registration process.");
          setErrorCode('USER_NOT_FOUND');
        } else {
          setError(errorObj.message || "Failed to load user profile");
          setErrorCode(errorObj.code || 'UNKNOWN_ERROR');
        }
      } else {
        setError("Failed to load user profile");
        setErrorCode('UNKNOWN_ERROR');
      }
    } finally {
      setLoading(false);
    }
  }, [session?.accessToken, toast]);

  const refreshSession = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      setErrorCode(null);
      await updateSession();
      console.log('[Dashboard] Session refreshed');
      fetchUserProfile();
    } catch (err) {
      console.error('[Dashboard] Error refreshing session:', err);
      setError("Failed to refresh session");
      setLoading(false);
    }
  }, [updateSession, fetchUserProfile]);

  useEffect(() => {
    if (session?.accessToken) {
      console.log('[Dashboard] Session loaded, fetching user profile');
      fetchUserProfile();
    } else {
      console.log('[Dashboard] No accessToken in session');
      setLoading(false);
    }
  }, [session?.accessToken, fetchUserProfile]);

  // Show loading until session and user profile are loaded
  if (status === "loading" || loading) {
    return (
      <div className="flex flex-col justify-center items-center h-screen">
        <div className="animate-spin mb-4">
          <RefreshCw className="h-8 w-8 text-primary" />
        </div>
        <p className="text-lg">Loading your dashboard...</p>
      </div>
    );
  }

  // Handle authentication errors with appropriate actions
  if (error) {
    return (
      <div className="flex flex-col justify-center items-center h-screen p-4">
        <div className="bg-destructive/10 border border-destructive rounded-lg p-6 max-w-md w-full">
          <div className="flex items-center mb-4">
            <AlertCircle className="h-6 w-6 text-destructive mr-2" />
            <h2 className="text-xl font-semibold text-destructive">Authentication Error</h2>
          </div>
          <p className="mb-6">{error}</p>
          <div className="flex flex-col sm:flex-row gap-3">
            {errorCode === 'TOKEN_EXPIRED' ? (
              <>
                <Button variant="default" onClick={handleSignOut} className="flex-1">
                  Sign In Again
                </Button>
                <Button variant="outline" onClick={refreshSession} className="flex-1">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh Session
                </Button>
              </>
            ) : errorCode === 'USER_NOT_FOUND' ? (
              <>
                <Button variant="default" onClick={handleSignOut} className="flex-1">
                  Sign In Again
                </Button>
                <Button variant="outline" onClick={() => window.location.href = '/auth/register'} className="flex-1">
                  Register
                </Button>
              </>
            ) : (
              <>
                <Button variant="default" onClick={refreshSession} className="flex-1">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
                <Button variant="outline" onClick={handleSignOut} className="flex-1">
                  Sign Out
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Robust onboarding completion check (snake_case only, matches backend)
  if (!userProfile?.first_name || !userProfile?.last_name) {
    return <UserOnboardingWizard />;
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Organization Dashboard</h1>
      <DashboardLayout
        orgPanel={<OrganizationPanel />}
        invitationsPanel={<InvitationsPanel />}
        keysPanel={<KeysPanel />}
        settingsPanel={<SettingsPanel />}
        enterprisePanel={<EnterpriseToolsPanel />}
      />
    </div>
  );
}
