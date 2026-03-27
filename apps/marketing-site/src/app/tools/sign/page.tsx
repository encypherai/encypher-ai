import React from "react";
import EncodeDecodeTool from "@/components/tools/EncodeDecodeTool";
import { Metadata } from "next";
import { getSiteUrl } from "@/lib/env";
import Link from "next/link";
import { ChromeInstallButton } from "@/components/ui/ChromeInstallButton";

export const metadata: Metadata = {
  title: "Sign Text with Metadata | Encypher Tool",
  description: "Sign text with secure metadata using Encypher's provenance tool. Try Encypher's free online signing tool for digital authenticity.",
  keywords: [
    "sign text",
    "metadata signing",
    "unicode metadata",
    "Encypher",
    "digital provenance",
    "content authenticity",
    "secure signing tool",
  ],
  openGraph: {
    title: "Sign Text with Metadata | Encypher Tool",
    description: "Sign text with secure metadata using Encypher's provenance tool. Try Encypher's free online signing tool for digital authenticity.",
    url: "https://encypher.com/tools/sign",
    siteName: "Encypher",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Sign Text with Metadata | Encypher Tool",
    description: "Sign text with secure metadata using Encypher's provenance tool. Try Encypher's free online signing tool for digital authenticity.",
  },
  metadataBase: new URL(getSiteUrl()),
};

export default function SignPage() {
  return (
    <main className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6">Sign Text with Metadata</h1>
      <EncodeDecodeTool initialMode="encode" />
      <div className="mt-8 p-4 rounded-lg border border-border bg-muted/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium">Sign and verify from your browser</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            The Encypher Verify Chrome extension lets you sign selected text on
            any page and verify C2PA watermarks as you browse. Verification is
            free with no account.
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
