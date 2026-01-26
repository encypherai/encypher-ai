import React from "react";
import EncodeDecodeTool from "@/components/tools/EncodeDecodeTool";
import { Metadata } from "next";
import { getSiteUrl } from "@/lib/env";

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
    "secure signing tool"
  ],
  openGraph: {
    title: "Sign Text with Metadata | Encypher Tool",
    description: "Sign text with secure metadata using Encypher's provenance tool. Try Encypher's free online signing tool for digital authenticity.",
    url: "https://encypherai.com/tools/sign",
    siteName: "Encypher",
    type: "website"
  },
  twitter: {
    card: "summary_large_image",
    title: "Sign Text with Metadata | Encypher Tool",
    description: "Sign text with secure metadata using Encypher's provenance tool. Try Encypher's free online signing tool for digital authenticity."
  },
  metadataBase: new URL(getSiteUrl()),
};

export default function EncodePage() {
  return (
    <main className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6">Sign Text with Metadata</h1>
      <EncodeDecodeTool initialMode="encode" />
    </main>
  );
}
