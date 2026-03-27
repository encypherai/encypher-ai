import React from "react";
import EncodeDecodeTool from "@/components/tools/EncodeDecodeTool";
import { Metadata } from "next";
import { getSiteUrl } from "@/lib/env";
import Link from "next/link";
import { ChromeInstallButton } from "@/components/ui/ChromeInstallButton";

export const metadata: Metadata = {
  title: "Verify Signed Text | Encypher Tool",
  description: "Verify signed text and inspect embedded metadata with Encypher's provenance tool. Free, secure, and privacy-preserving.",
  keywords: [
    "verify text",
    "verify metadata",
    "unicode metadata",
    "Encypher",
    "digital provenance",
    "content authenticity",
    "secure verification tool",
  ],
  openGraph: {
    title: "Verify Signed Text | Encypher Tool",
    description: "Verify signed text and inspect embedded metadata with Encypher's provenance tool. Free, secure, and privacy-preserving.",
    url: "https://encypher.com/tools/verify",
    siteName: "Encypher",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Verify Signed Text | Encypher Tool",
    description: "Verify signed text and inspect embedded metadata with Encypher's provenance tool. Free, secure, and privacy-preserving.",
  },
  metadataBase: new URL(getSiteUrl()),
};

export default function VerifyPage() {
  return (
    <main className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6">Verify Signed Text</h1>
      <EncodeDecodeTool initialMode="decode" />
      <div className="mt-8 p-4 rounded-lg border border-border bg-muted/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium">Verify on any webpage</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            The Encypher Verify Chrome extension detects C2PA watermarks
            automatically as you browse. Free, no account required.
          </p>
        </div>
        <ChromeInstallButton size="sm" installLabel="Add to Chrome" />
      </div>
      <div className="mt-3 text-xs text-muted-foreground text-center">
        <Link href="/tools">Back to all tools</Link>
      </div>
    </main>
  );
}
