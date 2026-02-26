// TEAM_152: File Inspector tool page (Server Component for metadata)
import React from "react";
import { Metadata } from "next";
import { getSiteUrl } from "@/lib/env";
import Link from "next/link";
import FileInspectorClientWrapper from "./FileInspectorClientWrapper";

export const metadata: Metadata = {
  title: "Inspect File | Encypher Tool",
  description: "Drag and drop images or text files to inspect embedded C2PA and XMP provenance credentials. Verify image authenticity, view metadata, and trace provenance with Encypher's free inspection tool.",
  keywords: [
    "file inspector",
    "C2PA verification",
    "image provenance",
    "XMP metadata",
    "content authenticity",
    "Encypher",
    "digital provenance",
    "drag and drop verify",
    "inspect metadata",
    "image signing",
  ],
  openGraph: {
    title: "Inspect File | Encypher Tool",
    description: "Drag and drop images or text files to inspect embedded C2PA and XMP provenance credentials. Verify authenticity and view metadata.",
    url: "https://encypherai.com/tools/inspect",
    siteName: "Encypher",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Inspect File | Encypher Tool",
    description: "Drag and drop images or text files to inspect embedded C2PA and XMP provenance credentials. Verify authenticity and view metadata.",
  },
  metadataBase: new URL(getSiteUrl()),
};

export default function InspectPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="max-w-6xl mx-auto py-12 px-4">
        <FileInspectorClientWrapper />
        <div className="mt-6 text-xs text-muted-foreground text-center">
          <Link href="/tools">← All Tools</Link>
        </div>
      </main>
    </div>
  );
}
