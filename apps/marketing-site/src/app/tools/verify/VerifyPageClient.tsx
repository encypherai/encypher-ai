'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { FileText, Upload } from 'lucide-react';

// Dynamic imports with ssr:false - pdfjs-dist uses Promise.withResolvers (ES2024)
// which is unavailable in Node, and EncodeDecodeTool uses browser APIs
const EncodeDecodeTool = dynamic(
  () => import('@/components/tools/EncodeDecodeTool'),
  { ssr: false, loading: () => <div className="min-h-[400px]" /> },
);

const FileInspectorTool = dynamic(
  () => import('@/components/tools/FileInspectorTool'),
  { ssr: false, loading: () => <div className="min-h-[500px]" /> },
);

type Tab = 'text' | 'file';

export default function VerifyPageClient() {
  const [activeTab, setActiveTab] = useState<Tab>('text');

  return (
    <div>
      {/* Tab bar */}
      <div className="flex gap-1 mb-8 border-b border-border">
        <button
          onClick={() => setActiveTab('text')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'text'
              ? 'border-[#2a87c4] text-foreground'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <FileText className="h-4 w-4" />
          Text
        </button>
        <button
          onClick={() => setActiveTab('file')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'file'
              ? 'border-[#2a87c4] text-foreground'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Upload className="h-4 w-4" />
          File Upload
        </button>
      </div>

      {/* Tab content */}
      {activeTab === 'text' ? (
        <div className="max-w-2xl mx-auto">
          <EncodeDecodeTool initialMode="decode" />
        </div>
      ) : (
        <FileInspectorTool />
      )}
    </div>
  );
}
