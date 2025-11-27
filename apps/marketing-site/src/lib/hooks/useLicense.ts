import { useQuery } from '@tanstack/react-query';
import { fetchApi } from "../api";
import { useSession } from "next-auth/react";

/**
 * Interface representing a license object.
 *
 * @property {string} uuid - Unique identifier for the license.
 * @property {string} license_key - License key.
 * @property {string} tier - Tier of the license.
 * @property {string} status - Status of the license.
 * @property {string} issued_at - Timestamp when the license was issued.
 * @property {string} expires_at - Timestamp when the license expires.
 * @property {string} organization_uuid - Unique identifier for the organization.
 * @property {boolean} is_trial - Indicates if the license is a trial.
 */
export interface License {
  uuid: string;
  license_key: string;
  tier: string;
  status: string;
  issued_at: string;
  expires_at: string;
  organization_uuid: string;
  is_trial: boolean;
};

/**
 * React hook to fetch the authenticated user's license from the backend.
 *
 * - Requires a valid JWT accessToken from the next-auth session.
 * - Only queries if session is authenticated and token is present.
 * - Returns license data, error, and loading state.
 * - Ensures Authorization header is set for protected endpoint.
 * - If the session is missing or the token is invalid, returns a clear error for the UI.
 *
 * @returns { license, error, isLoading }
 */
export function useLicense() {
  // Get the current session and its status
  const { data: session, status: sessionStatus } = useSession();
  // Extract the access token from the session
  const token = session?.accessToken;

  // Enhanced: If session is not authenticated or token is missing, return explicit error
  const isEnabled = sessionStatus === 'authenticated' && !!token;

  const {
    data,
    error,
    isLoading,
  } = useQuery<License>({
    queryKey: ["license"],
    queryFn: async () => {
      if (!token) {
        throw new Error("No access token found. Please sign in again.");
      }
      // Secure: pass JWT for Authorization
      return fetchApi("/api/v1/license/me", {
        token,
      });
    },
    enabled: isEnabled,
    // Optional: Add retry logic or stale time if needed
    // retry: 1,
    // staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // If not enabled, return a clear error for the UI
  return {
    license: isEnabled ? data : undefined,
    error: !isEnabled ? new Error("Not authenticated or missing access token.") : error,
    isLoading,
  };
}
