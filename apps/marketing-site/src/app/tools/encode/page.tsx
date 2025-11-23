import React from "react";
import EncodeDecodeTool from "@/components/tools/EncodeDecodeTool";
import { Metadata } from "next";
import { getSiteUrl } from "@/lib/env";

export const metadata: Metadata = {
  title: "Encode Text with Metadata | Encypher Tool",
  description: "Embed secure metadata into your text using Unicode variation selectors. Try Encypher's free online encoder tool for digital provenance and authenticity.",
  keywords: [
    "encode text",
    "metadata embedding",
    "unicode metadata",
    "Encypher",
    "digital provenance",
    "content authenticity",
    "secure encoding tool"
  ],
  openGraph: {
    title: "Encode Text with Metadata | Encypher Tool",
    description: "Embed secure metadata into your text using Unicode variation selectors. Try Encypher's free online encoder tool for digital provenance and authenticity.",
    url: "https://encypherai.com/tools/encode",
    siteName: "Encypher",
    type: "website"
  },
  twitter: {
    card: "summary_large_image",
    title: "Encode Text with Metadata | Encypher Tool",
    description: "Embed secure metadata into your text using Unicode variation selectors. Try Encypher's free online encoder tool for digital provenance and authenticity."
  },
  metadataBase: new URL(getSiteUrl()),
};

export default function EncodePage() {
  return (
    <main className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6">Encode Text with Metadata</h1>
      <EncodeDecodeTool initialMode="encode" />
    </main>
  );
}
