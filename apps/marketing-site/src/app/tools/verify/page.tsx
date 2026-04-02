import React from "react";
import { Metadata } from "next";
import { getSiteUrl } from "@/lib/env";
import Link from "next/link";
import { ChromeInstallButton } from "@/components/ui/ChromeInstallButton";
import VerifyPageClient from "./VerifyPageClient";

export const metadata: Metadata = {
  title: "Verify Content Provenance | Encypher Tool",
  description: "Verify text and file provenance with Encypher's free tool. Paste signed text or upload images, audio, video, and documents to inspect embedded C2PA credentials.",
  keywords: [
    "verify text",
    "verify metadata",
    "C2PA verification",
    "image provenance",
    "content authenticity",
    "Encypher",
    "digital provenance",
    "file inspector",
    "drag and drop verify",
  ],
  openGraph: {
    title: "Verify Content Provenance | Encypher Tool",
    description: "Verify text and file provenance with Encypher's free tool. Paste signed text or upload images, audio, video, and documents to inspect C2PA credentials.",
    url: "https://encypher.com/tools/verify",
    siteName: "Encypher",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Verify Content Provenance | Encypher Tool",
    description: "Verify text and file provenance with Encypher's free tool. Paste signed text or upload images, audio, video, and documents to inspect C2PA credentials.",
  },
  metadataBase: new URL(getSiteUrl()),
};

export default function VerifyPage() {
  return (
    <main className="max-w-6xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-2">Verify Content Provenance</h1>
      <p className="text-muted-foreground mb-6">
        Paste signed text or upload a file to verify embedded C2PA provenance credentials. Free, no account required.
      </p>
      <VerifyPageClient />
      <div className="max-w-2xl mx-auto mt-8 p-4 rounded-lg border border-border bg-muted/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
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
