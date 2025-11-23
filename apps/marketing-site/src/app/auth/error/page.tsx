"use client";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

const errorMessages: Record<string, string> = {
  OAuthSignin: "Error in constructing an authorization URL.",
  OAuthCallback: "Error in handling the response from the OAuth provider.",
  OAuthCreateAccount: "Could not create OAuth account.",
  EmailCreateAccount: "Could not create email account.",
  Callback: "Error in the callback handler.",
  OAuthAccountNotLinked: "To confirm your identity, sign in with the same account you used originally.",
  EmailSignin: "Error sending the email.",
  CredentialsSignin: "Sign in failed. Check the details you provided are correct.",
  default: "Unable to sign in. Please try again."
};

// Loading component to show while the main component is loading
function AuthErrorLoading() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
      <h1 className="text-3xl font-bold mb-6">Loading...</h1>
      <p className="mb-4">Please wait while we process your request.</p>
    </main>
  );
}

// Main component that uses client-side hooks
function AuthErrorContent() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error") ?? "default";
  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
      <h1 className="text-3xl font-bold mb-6">Authentication Error</h1>
      <p className="mb-4">{errorMessages[error] || errorMessages.default}</p>
      <a href="/auth/signin" className="text-blue-400 underline">Back to sign in</a>
    </main>
  );
}

// Wrap the component with Suspense to handle useSearchParams
export default function AuthErrorPage() {
  return (
    <Suspense fallback={<AuthErrorLoading />}>
      <AuthErrorContent />
    </Suspense>
  );
}
