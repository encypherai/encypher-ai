import { useQuery } from '@tanstack/react-query';
import { fetchApi } from "../api";
import { useSession } from "next-auth/react";
import type { Organization as OrganizationType } from "@/types/organization";

/**
 * React hook to fetch the authenticated user's organization from the backend.
 *
 * - Requires a valid JWT accessToken from the next-auth session.
 * - Only queries if session is authenticated and token is present.
 * - Returns org data, error, and loading state.
 * - Ensures Authorization header is set for protected endpoint.
 * - If the session is missing or the token is invalid, returns a clear error for the UI.
 * - If the backend returns a 404 or 'Organization not found for user' error, sets org to null and error to null.
 *
 * @returns { org, error, isLoading }
 */
export type Organization = OrganizationType;

export function useOrganization() {
  // Get the current session and its status from next-auth
  const { data: session, status: sessionStatus } = useSession();
  // Extract the access token from the session (if present)
  const token = session?.accessToken;

  // Enhanced: If session is not authenticated or token is missing, return explicit error
  const isEnabled = sessionStatus === 'authenticated' && !!token;

  const {
    data,
    error,
    isLoading,
  } = useQuery<OrganizationType | null, Error, OrganizationType | null, [string]>({
    queryKey: ["organization"],
    queryFn: async (): Promise<OrganizationType | null> => {
      if (!token) {
        throw new Error("No access token found. Please sign in again.");
      }
      try {
        const res = await fetchApi("/api/v1/organization/me", {
          credentials: "include",
          token,
        });
        return res as OrganizationType;
      } catch (err: unknown) {
        // Typesafe check for 404 or 'Organization not found' error
        if (
          typeof err === 'object' && err !== null &&
          (('status' in err && (err as { status: number }).status === 404) ||
           ('data' in err && typeof (err as { data?: { detail?: string } }).data?.detail === 'string' && 
            (err as { data?: { detail?: string } }).data?.detail?.includes("Organization not found")))
        ) {
          // If backend says org not found (404 or specific error), treat as null org
          console.log("[useOrganization] Organization not found, returning null");
          return null;
        }
        throw err;
      }
    },
    enabled: isEnabled,
    retry: (failureCount: number, error: Error | { status?: number }) => {
      // Check if error has a status property and it's 404
      if (typeof error === 'object' && error !== null && 'status' in error && 
          (error as { status: number }).status === 404) {
        console.log("[useOrganization] Received 404, not retrying.");
        return false;
      }
      return failureCount < 2; // Reduced from 3 to 2 retries
    },
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    refetchInterval: false, // Prevent automatic refetching
    staleTime: 10 * 60 * 1000, // 10 minutes (increased from 5)
    gcTime: 15 * 60 * 1000, // 15 minutes cache time (renamed from cacheTime to gcTime)
  });

  // If not enabled, return a clear error for the UI
  const org = isEnabled ? data : null;
  const customError = !isEnabled ? new Error("Not authenticated or missing access token.") : (org === null ? null : error);
  console.log("[useOrganization] hook called. org:", org, "error:", customError);
  return {
    org,
    error: customError,
    isLoading,
  };
}
