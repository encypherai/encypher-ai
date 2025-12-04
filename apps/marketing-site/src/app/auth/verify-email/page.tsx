"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { signIn } from "next-auth/react";
import { fetchApi } from "../../../lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import Image from 'next/image';
import { CheckCircle2, XCircle, Loader2, Mail } from "lucide-react";

// API response type for verify-email endpoint
interface VerifyEmailResponse {
  success: boolean;
  data?: {
    message: string;
    access_token: string;
    refresh_token: string;
    token_type: string;
    user: {
      id: string;
      email: string;
      name?: string;
      email_verified: boolean;
    };
  };
  error?: {
    code?: string;
    message: string;
  };
}

// Loading component
function VerifyEmailLoading() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-primary/10 to-primary/5 p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="items-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <CardTitle className="text-center text-xl mt-4">Verifying Email</CardTitle>
        </CardHeader>
        <CardContent className="text-center">
          <p className="text-muted-foreground">Please wait...</p>
        </CardContent>
      </Card>
    </div>
  );
}

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("Verifying your email...");
  const [called, setCalled] = useState(false);

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Verification token is missing. Please check your email for the correct link.");
      return;
    }
    
    if (called) return;
    setCalled(true);

    const verifyEmail = async () => {
      try {
        const response = await fetchApi<VerifyEmailResponse>("/auth/verify-email", {
          method: "POST",
          body: JSON.stringify({ token }),
        });

        if (response.success && response.data) {
          setStatus("success");
          setMessage(response.data.message || "Your email has been verified successfully!");
          
          // Auto-sign in with the tokens from verification
          if (response.data.access_token) {
            const signInResult = await signIn("credentials", {
              redirect: false,
              backendToken: response.data.access_token,
              isVerifiedTokenFlow: "true",
            });
            
            if (signInResult?.ok) {
              // Redirect to dashboard after successful auto-login
              setTimeout(() => {
                router.push(process.env.NEXT_PUBLIC_DASHBOARD_URL || "/dashboard");
              }, 1500);
            }
          }
        } else {
          setStatus("error");
          setMessage(response.error?.message || "Email verification failed. The link may have expired.");
        }
      } catch (err) {
        console.error("[VerifyEmail] Error:", err);
        setStatus("error");
        setMessage(err instanceof Error ? err.message : "An unexpected error occurred.");
      }
    };

    verifyEmail();
  }, [token, called, router]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-primary/10 to-primary/5 p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="items-center space-y-4">
          <div className="flex items-center justify-center">
            <Image src="/encypher_full_nobg.png" alt="Encypher" width={140} height={70} />
          </div>
          
          {status === "loading" && (
            <Loader2 className="h-16 w-16 animate-spin text-primary" />
          )}
          {status === "success" && (
            <CheckCircle2 className="h-16 w-16 text-green-500" />
          )}
          {status === "error" && (
            <XCircle className="h-16 w-16 text-destructive" />
          )}
          
          <CardTitle className="text-center text-2xl">
            {status === "loading" && "Verifying..."}
            {status === "success" && "Email Verified!"}
            {status === "error" && "Verification Failed"}
          </CardTitle>
        </CardHeader>
        
        <CardContent className="text-center space-y-6">
          <p className={`text-lg ${status === "error" ? "text-destructive" : "text-muted-foreground"}`}>
            {message}
          </p>
          
          {status === "success" && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Your account is now active. Redirecting you to the dashboard...
              </p>
              <div className="flex items-center justify-center">
                <Loader2 className="h-5 w-5 animate-spin text-primary mr-2" />
                <span className="text-sm text-muted-foreground">Signing you in...</span>
              </div>
              <Button asChild className="w-full" size="lg" variant="outline">
                <Link href={process.env.NEXT_PUBLIC_DASHBOARD_URL || "/dashboard"}>
                  Go to Dashboard Now
                </Link>
              </Button>
            </div>
          )}
          
          {status === "error" && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                The verification link may have expired or already been used.
              </p>
              <div className="flex flex-col gap-2">
                <Button asChild variant="outline" className="w-full">
                  <Link href="/auth/signin">
                    <Mail className="mr-2 h-4 w-4" />
                    Request New Verification Email
                  </Link>
                </Button>
                <Button asChild variant="ghost" className="w-full">
                  <Link href="/auth/signin">Back to Sign In</Link>
                </Button>
              </div>
            </div>
          )}
          
          {status === "loading" && (
            <p className="text-sm text-muted-foreground animate-pulse">
              This should only take a moment...
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<VerifyEmailLoading />}>
      <VerifyEmailContent />
    </Suspense>
  );
}
