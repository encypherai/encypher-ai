'use client';

// TEAM_152: Client-only wrapper for FileInspectorTool.
// Uses next/dynamic with ssr:false to prevent pdfjs-dist from loading during SSR.
// pdfjs-dist v4 uses Promise.withResolvers (ES2024) which is unavailable in Node.

import dynamic from "next/dynamic";

const FileInspectorTool = dynamic(
  () => import("@/components/tools/FileInspectorTool"),
  { ssr: false, loading: () => <div className="min-h-[500px]" /> },
);

export default function FileInspectorClientWrapper() {
  return <FileInspectorTool />;
}
