import React from "react";
import EncodeDecodeTool from "@/components/tools/EncodeDecodeTool";
import { Metadata } from "next";
import { getSiteUrl } from "@/lib/env";

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
    "secure verification tool"
  ],
  openGraph: {
    title: "Verify Signed Text | Encypher Tool",
    description: "Verify signed text and inspect embedded metadata with Encypher's provenance tool. Free, secure, and privacy-preserving.",
    url: "https://encypher.com/tools/verify",
    siteName: "Encypher",
    type: "website"
  },
  twitter: {
    card: "summary_large_image",
    title: "Verify Signed Text | Encypher Tool",
    description: "Verify signed text and inspect embedded metadata with Encypher's provenance tool. Free, secure, and privacy-preserving."
  },
  metadataBase: new URL(getSiteUrl()),
};

export default function DecodePage() {
  return (
    <main className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6">Verify Signed Text</h1>
      <EncodeDecodeTool initialMode="decode" />
    </main>
  );
}
