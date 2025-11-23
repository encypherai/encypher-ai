'use client';

// This page is a client component because it uses the useSearchParams hook from next/navigation.
import React, { Suspense } from "react";
import EncodeDecodeTool from "@/components/tools/EncodeDecodeTool";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

// Create a client component that uses useSearchParams
function EncodeDecodeContent() {
  // Read ?mode=encode or ?mode=decode from URL
  const searchParams = useSearchParams();
  let initialMode: "encode" | "decode" = "encode";
  const modeParam = searchParams?.get("mode");
  if (modeParam === "decode") initialMode = "decode";

  return (
    <>
      <h1 className="text-3xl font-bold mb-6">Encypher Encode/Decode Tool</h1>
      <EncodeDecodeTool initialMode={initialMode} />
    </>
  );
}

// Main page component with Suspense boundary
export default function EncodeDecodePage() {
  return (
    <>
      {/* Visible breadcrumbs for accessibility/UX */}
      <main className="max-w-2xl mx-auto py-12 px-4">
        <Suspense fallback={<div>Loading...</div>}>
          <EncodeDecodeContent />
        </Suspense>
      </main>
      <div className="mt-6 text-xs text-muted-foreground text-center">
        <Link href="/tools">← All Tools</Link>
      </div>
    </>
  );
}
