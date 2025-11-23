import React from "react";
import EncodeDecodeTool from "@/components/tools/EncodeDecodeTool";
import { Metadata } from "next";
import { getSiteUrl } from "@/lib/env";

export const metadata: Metadata = {
  title: "Decode Metadata from Text | Encypher Tool",
  description: "Extract and verify embedded metadata from text using Encypher's Unicode-powered decoder. Free, secure, and privacy-preserving.",
  keywords: [
    "decode text",
    "extract metadata",
    "unicode metadata",
    "Encypher",
    "digital provenance",
    "content authenticity",
    "secure decoding tool"
  ],
  openGraph: {
    title: "Decode Metadata from Text | Encypher Tool",
    description: "Extract and verify embedded metadata from text using Encypher's Unicode-powered decoder. Free, secure, and privacy-preserving.",
    url: "https://encypherai.com/tools/decode",
    siteName: "Encypher",
    type: "website"
  },
  twitter: {
    card: "summary_large_image",
    title: "Decode Metadata from Text | Encypher Tool",
    description: "Extract and verify embedded metadata from text using Encypher's Unicode-powered decoder. Free, secure, and privacy-preserving."
  },
  metadataBase: new URL(getSiteUrl()),
};

export default function DecodePage() {
  return (
    <main className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6">Decode Metadata from Text</h1>
      <EncodeDecodeTool initialMode="decode" />
    </main>
  );
}
