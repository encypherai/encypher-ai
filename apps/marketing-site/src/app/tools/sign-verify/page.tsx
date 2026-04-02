'use client';

// This page is a client component because it uses the useSearchParams hook from next/navigation.
import React, { Suspense } from "react";
import EncodeDecodeTool from "@/components/tools/EncodeDecodeTool";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

// Create a client component that uses useSearchParams
function SignVerifyContent() {
  // Read ?mode=sign or ?mode=verify from URL
  const searchParams = useSearchParams();
  let initialMode: "encode" | "decode" = "encode";
  const modeParam = searchParams?.get("mode");
  if (modeParam === "decode" || modeParam === "verify") initialMode = "decode";

  return (
    <>
      <h1 className="text-3xl font-bold mb-6">Encypher Sign/Verify Tool</h1>
      <EncodeDecodeTool initialMode={initialMode} />
    </>
  );
}

// Main page component with Suspense boundary
export default function SignVerifyPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Visible breadcrumbs for accessibility/UX */}
      <main className="max-w-4xl mx-auto py-12 px-4">
        <Suspense fallback={<div className="text-center py-8">Loading...</div>}>
          <SignVerifyContent />
        </Suspense>
        {/* Related glossary terms */}
        <div className="mt-8 flex flex-wrap items-center gap-2">
          <span className="text-xs text-muted-foreground">Related glossary terms:</span>
          <Link href="/glossary#content-provenance" className="inline-block rounded-full bg-muted px-3 py-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
            Content Provenance
          </Link>
          <Link href="/glossary#c2pa" className="inline-block rounded-full bg-muted px-3 py-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
            C2PA
          </Link>
          <Link href="/glossary#cryptographic-watermarking" className="inline-block rounded-full bg-muted px-3 py-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
            Cryptographic Watermarking
          </Link>
        </div>
        <div className="mt-6 text-xs text-muted-foreground text-center">
          <Link href="/tools">← All Tools</Link>
        </div>
      </main>
    </div>
  );
}
