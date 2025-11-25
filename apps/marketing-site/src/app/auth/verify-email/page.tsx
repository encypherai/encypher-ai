"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { signIn } from "next-auth/react";
import { fetchApi } from "../../../lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import Image from 'next/image';
import { BackendTokenExchangeResponse, UserSessionData } from "../../../types/auth-responses"; // Added

// Loading component to show while the main component is loading
function VerifyEmailLoading() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl text-center">Verifying Email</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col items-center space-y-4">
          <p className="text-center">Please wait while we verify your email...</p>
        </CardContent>
      </Card>
    </div>
  );
}

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string>("Verifying your email...");
  const [called, setCalled] = useState(false);

  useEffect(() => {
    if (!token) {
      setError("Verification token is missing.");
      setIsLoading(false);
      return;
    }
    if (called) return; // Prevent double call
    setCalled(true);

    const verifyAndLogin = async () => {
      setIsLoading(true);
      setError(null);
      try {
        console.log("[VerifyEmail] Starting verification with token:", token);
        setMessage("Verifying email...");
        // Use the new BackendTokenExchangeResponse type
        const verifyRes = await fetchApi<BackendTokenExchangeResponse>(`/api/v1/auth/verify-email?token=${token}`, {
          method: "GET",
        });

        if (!verifyRes.success || !verifyRes.data) { // Ensure data object exists
          console.error("[VerifyEmail] Verification failed or data missing:", verifyRes.error);
          setError(verifyRes.error?.message || "Email verification failed. Please try the link again or contact support.");
          setIsLoading(false);
          return;
        }

        const { access_token: backendToken, session_data: userSessionData, message: backendMessage } = verifyRes.data;

        if (!backendToken || !userSessionData) {
          setError("Verification succeeded, but critical session data (token or user details) was not returned. Please try signing in manually.");
          setIsLoading(false);
          return;
        }

        if (backendMessage?.toLowerCase().includes("already verified")) {
          setMessage("Your email was already verified. Logging you in...");
        } else {
          setMessage("Email verified successfully. Logging you in...");
        }
        
        console.log("[VerifyEmail] Attempting sign in with backend token and session data (redirect: false)...");
        
        // Pass the backendToken and userSessionData to NextAuth.
        // The 'credentials' provider's authorize callback will need to be adapted
        // to handle these parameters instead of traditional email/password.
        const signInResult = await signIn("credentials", {
          redirect: false,
          // It's common to pass a specific flag or use a different provider type
          // if the 'credentials' provider is strictly for email/password.
          // For now, we assume 'credentials' can be adapted.
          isVerifiedTokenFlow: true, // Custom flag to indicate this flow
          backendToken: backendToken,
          email: userSessionData.email,
          name: userSessionData.name,
          user_uuid: userSessionData.user_uuid,
          org_uuid: userSessionData.org_uuid,
          org_name: userSessionData.org_name,
          roles: JSON.stringify(userSessionData.roles), // Stringify arrays/objects if needed by authorize
          first_name: userSessionData.first_name,
          last_name: userSessionData.last_name,
          is_verified: userSessionData.is_verified
          // ... include other necessary fields from userSessionData
        });

        console.log("[VerifyEmail] signIn Result:", signInResult);

        if (signInResult?.ok) {
          setMessage("Login successful! Redirecting to your dashboard...");
          router.replace("/dashboard"); 
        } else {
          setError(signInResult?.error || "Login failed after verification. Please try signing in manually or contact support.");
          setIsLoading(false);
        }
      } catch (err: unknown) {
        console.error("[VerifyEmail] Error during verification/login process:", err);
        const errorMessage = err instanceof Error ? err.message : "An unexpected error occurred.";
        setError(errorMessage);
        setIsLoading(false);
      }
    };

    verifyAndLogin();
  }, [router, searchParams, token, called]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-primary to-primary/70 p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="items-center">
          <div className="flex items-center justify-center">
            <Image src="/encypher_full_nobg.png" alt="Encypher Corporation Logo" width={120} height={60} />
          </div>
          <CardTitle className="text-center text-2xl">Verifying Your Account</CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-4">
          {isLoading && (
            <div>
              {/* TODO: Replace with ShadCN Spinner/Progress Bar */}
              <p className="text-lg animate-pulse">{message}</p>
            </div>
          )}
          {error && (
            <div className="text-destructive space-y-2">
              <p><b>Verification Error</b></p>
              <p>{error}</p>
              <Button asChild variant="outline">
                <Link href="/auth/signin">Go to Sign In</Link>
              </Button>
            </div>
          )}
          {!isLoading && !error && (
            // This state should ideally not be reached if successful login navigates away
            <p>Verification process completed. If you are not redirected, please click below.</p>
          )}
          <div className="mt-4">
            <Button asChild variant="link">
              <Link href="/auth/signin">Back to Sign In</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Wrap the component with Suspense to handle useSearchParams
export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<VerifyEmailLoading />}>
      <VerifyEmailContent />
    </Suspense>
  );
}
