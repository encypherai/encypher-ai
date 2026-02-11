'use client';

// TEAM_152: Drag-and-drop file inspector for text file verification
import React, { useState, useRef, useCallback } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useToast } from "@/components/ui/use-toast";
import { trackToolEvent } from "@/lib/toolsAnalytics";
import {
  SUPPORTED_EXTENSIONS,
  SUPPORTED_FORMATS_DISPLAY,
  MAX_FILE_SIZE_BYTES,
  isTextFile,
  isPdfFile,
  formatFileSize,
  validateFile,
} from "@/lib/fileInspector";

// --- Types matching backend DecodeToolResponse (shared with EncodeDecodeTool) ---
interface VerifyVerdict {
  valid: boolean;
  tampered: boolean;
  reason_code: string;
  signer_id?: string;
  signer_name?: string;
  timestamp?: string;
  details?: unknown;
}

interface MetadataWithOriginalText {
  original_text?: string;
  [key: string]: unknown;
}

interface SegmentLocation {
  paragraph_index: number;
  sentence_in_paragraph: number;
}

interface SegmentEmbeddingDetail {
  segment_uuid: string;
  leaf_index?: number | null;
  segment_location?: SegmentLocation | null;
  manifest_mode?: string | null;
}

interface C2PAInfo {
  validated: boolean;
  validation_type?: string | null;
  manifest_hash?: string | null;
  assertions?: Array<Record<string, unknown>> | null;
}

interface EmbeddingResult {
  index: number;
  metadata?: MetadataWithOriginalText | null;
  verification_status: 'Success' | 'Failure' | 'Key Not Found' | 'Not Attempted' | 'Error';
  error?: string | null;
  verdict?: VerifyVerdict | null;
  text_span?: [number, number] | null;
  clean_text?: string | null;
}

interface DecodeToolResponse {
  metadata?: MetadataWithOriginalText | null;
  verification_status: 'Success' | 'Failure' | 'Key Not Found' | 'Not Attempted' | 'Error';
  error?: string | { message: string } | null;
  raw_hidden_data?: VerifyVerdict | null;
  embeddings_found?: number;
  all_embeddings?: EmbeddingResult[] | null;
  segment_embeddings?: SegmentEmbeddingDetail[] | null;
  total_segments_in_document?: number | null;
  c2pa?: C2PAInfo | null;
}

function getErrorMessage(error: string | { message: string } | null | undefined, fallback: string): string {
  if (!error) return fallback;
  if (typeof error === "string") return error;
  if (typeof error === "object" && "message" in error && typeof error.message === "string") return error.message;
  return fallback;
}

// TEAM_156: pdfBase64 is sent alongside encoded_text so the server can
// extract text from the EncypherSignedText metadata stream (lossless).
// The server falls back to encoded_text if no EncypherSignedText found.
async function verifyText(text: string, pdfBase64?: string): Promise<DecodeToolResponse> {
  const payload: Record<string, string> = { encoded_text: text };
  if (pdfBase64) payload.pdf_base64 = pdfBase64;

  const response = await fetch("/api/tools/verify", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export default function FileInspectorTool() {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [verifyResponse, setVerifyResponse] = useState<DecodeToolResponse | null>(null);
  const [expandedEmbeddings, setExpandedEmbeddings] = useState<Set<number>>(new Set([0]));
  // TEAM_160: PDF first-page thumbnail
  const [pdfThumbnailUrl, setPdfThumbnailUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const resetState = useCallback(() => {
    setSelectedFile(null);
    setFileContent(null);
    setVerifyResponse(null);
    setError(null);
    setExpandedEmbeddings(new Set([0]));
    setPdfThumbnailUrl(null);
  }, []);

  const readAndVerifyFile = useCallback(async (file: File) => {
    resetState();
    setSelectedFile(file);

    const validation = validateFile(file.name, file.type, file.size);
    if (!validation.valid) {
      setError(validation.reason);
      return;
    }

    setLoading(true);
    setError(null);
    const startedAt = Date.now();

    trackToolEvent({
      eventName: "tools_inspect_started",
      pageUrl: window.location.href,
      pageTitle: document.title,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
      properties: {
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type || 'unknown',
      },
    });

    try {
      let text: string;
      let pdfB64: string | undefined;
      if (isPdfFile(file.name, file.type)) {
        const buffer = await file.arrayBuffer();
        // TEAM_156: Send raw PDF bytes to server for lossless extraction
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
        pdfB64 = btoa(binary);
        // Client-side extraction as fallback display text
        const { extractTextFromPdf, renderPdfThumbnail } = await import("@/lib/pdfTextExtractor");
        text = await extractTextFromPdf(buffer);
        // TEAM_160: Generate first-page thumbnail (non-blocking)
        renderPdfThumbnail(buffer).then(setPdfThumbnailUrl).catch(() => {});
      } else {
        text = await file.text();
      }
      setFileContent(text);

      if (!text.trim()) {
        setError(isPdfFile(file.name, file.type)
          ? "Could not extract readable text from this PDF."
          : "File contains no readable text content.");
        setLoading(false);
        return;
      }

      const response = await verifyText(text, pdfB64);

      trackToolEvent({
        eventName: "tools_inspect_success",
        pageUrl: window.location.href,
        pageTitle: document.title,
        referrer: document.referrer,
        userAgent: navigator.userAgent,
        properties: {
          fileName: file.name,
          fileSize: file.size,
          textLength: text.length,
          embeddingsFound: response.embeddings_found || 0,
          verificationStatus: response.verification_status,
          durationMs: Date.now() - startedAt,
        },
      });

      setVerifyResponse(response);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "An unexpected error occurred.";
      trackToolEvent({
        eventName: "tools_inspect_error",
        pageUrl: window.location.href,
        pageTitle: document.title,
        referrer: document.referrer,
        userAgent: navigator.userAgent,
        properties: {
          fileName: file.name,
          fileSize: file.size,
          errorMessage: message,
          durationMs: Date.now() - startedAt,
        },
      });
      setError(message);
      toast({ title: "Error", description: message });
    } finally {
      setLoading(false);
    }
  }, [resetState, toast]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      readAndVerifyFile(files[0]);
    }
  }, [readAndVerifyFile]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      readAndVerifyFile(files[0]);
    }
    // Reset input so the same file can be re-selected
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [readAndVerifyFile]);

  const handleBrowseClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const toggleEmbedding = useCallback((index: number) => {
    setExpandedEmbeddings(prev => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  }, []);

  const expandAllEmbeddings = useCallback(() => {
    if (verifyResponse?.all_embeddings) {
      setExpandedEmbeddings(new Set(verifyResponse.all_embeddings.map((_, i) => i)));
    }
  }, [verifyResponse]);

  const collapseAllEmbeddings = useCallback(() => {
    setExpandedEmbeddings(new Set([0]));
  }, []);

  // --- Status UI helpers (same logic as EncodeDecodeTool) ---
  const getStatusUI = (response: DecodeToolResponse) => {
    const verdict = response.raw_hidden_data;
    const embeddingsFound = response.embeddings_found || 0;
    const allEmbeddings = response.all_embeddings || [];

    if (embeddingsFound > 1 && allEmbeddings.length > 0) {
      const verifiedCount = allEmbeddings.filter(e => e.verdict?.valid).length;
      const tamperedCount = allEmbeddings.filter(e => !e.verdict?.valid && e.metadata).length;

      if (verifiedCount === embeddingsFound) {
        return {
          variant: "default" as const,
          className: "border-green-900 bg-green-800 text-white",
          title: `All ${embeddingsFound} Embeddings Verified`,
          description: `Found ${embeddingsFound} embedded manifests. All signatures are valid.`,
          icon: "✅"
        };
      } else if (verifiedCount > 0) {
        return {
          variant: "destructive" as const,
          className: "border-yellow-900 bg-yellow-700 text-white",
          title: `Partial Verification (${verifiedCount}/${embeddingsFound})`,
          description: `Found ${embeddingsFound} embeddings: ${verifiedCount} verified, ${tamperedCount} tampered or unverified.`,
          icon: "⚠️"
        };
      } else {
        return {
          variant: "destructive" as const,
          className: "border-red-900 bg-red-800 text-white",
          title: `Verification Failed (0/${embeddingsFound})`,
          description: `Found ${embeddingsFound} embeddings but none could be verified.`,
          icon: "❌"
        };
      }
    }

    if (verdict?.valid) {
      return {
        variant: "default" as const,
        className: "border-green-900 bg-green-800 text-white",
        title: "Verified Authentic",
        description: "The content is authentic and has not been modified.",
        icon: "✅"
      };
    }

    const manifest = (response.metadata as Record<string, unknown>)?.manifest;
    const hasManifest = manifest && typeof manifest === 'object' && Object.keys(manifest as object).length > 0;

    if (verdict?.tampered && hasManifest) {
      return {
        variant: "destructive" as const,
        className: "border-yellow-900 bg-yellow-700 text-white",
        title: "Tampered Content Detected (Manifest Found)",
        description: "Warning: A valid C2PA manifest was found, but the content text has been modified since signing.",
        icon: "⚠️"
      };
    }

    return {
      variant: "destructive" as const,
      className: "border-red-900 bg-red-800 text-white",
      title: "Verification Failed",
      description: verdict?.reason_code === 'SIGNER_UNKNOWN' && !hasManifest
        ? "No C2PA signature or invisible watermark found in this text."
        : (verdict?.reason_code || "No valid signature found."),
      icon: "❌"
    };
  };

  const getEmbeddingStatusIcon = (embedding: EmbeddingResult) => {
    if (embedding.verdict?.valid) return "✅";
    if (embedding.verdict?.tampered || (!embedding.verdict?.valid && embedding.metadata)) return "⚠️";
    return "❌";
  };

  const getEmbeddingStatusClass = (embedding: EmbeddingResult) => {
    if (embedding.verdict?.valid) return "border-green-700 bg-green-900/30";
    if (embedding.verdict?.tampered || (!embedding.verdict?.valid && embedding.metadata)) return "border-yellow-700 bg-yellow-900/30";
    return "border-red-700 bg-red-900/30";
  };

  return (
    <div className="w-full">
      {/* Two-column layout: sidebar + drop zone */}
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Left sidebar */}
        <div className="lg:w-64 shrink-0">
          <h1 className="text-3xl font-bold mb-4">Inspect</h1>
          <p className="text-sm text-muted-foreground mb-6">
            Drag in a file or browse to view associated Encypher provenance credentials in detail and see changes over time.
          </p>
          <div className="mb-2">
            <strong className="text-sm">Supported formats</strong>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {SUPPORTED_FORMATS_DISPLAY}
          </p>
        </div>

        {/* Main drop zone area */}
        <div className="flex-1 min-w-0">
          {!verifyResponse && !loading && (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`
                relative flex flex-col items-center justify-center
                min-h-[400px] lg:min-h-[500px]
                rounded-2xl border-2 border-dashed
                transition-all duration-200 cursor-pointer
                ${isDragOver
                  ? 'border-primary bg-primary/5 scale-[1.01]'
                  : 'border-muted-foreground/30 hover:border-muted-foreground/50 bg-card'
                }
              `}
              onClick={handleBrowseClick}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleBrowseClick(); }}
              aria-label="Drop zone for file upload"
            >
              {/* File icon */}
              <div className="mb-6">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className="opacity-60">
                  <rect x="12" y="8" width="40" height="48" rx="4" stroke="currentColor" strokeWidth="2" fill="none" />
                  <path d="M22 24h20M22 32h20M22 40h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  <circle cx="44" cy="44" r="12" fill="hsl(var(--primary))" opacity="0.15" />
                  <path d="M40 44h8M44 40v8" stroke="hsl(var(--primary))" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </div>

              <p className="text-lg font-semibold mb-1">
                {isDragOver ? 'Drop your file here' : 'Drag and drop your file'}
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                Select a file from your device
              </p>
              <Button
                variant="default"
                size="sm"
                onClick={(e) => { e.stopPropagation(); handleBrowseClick(); }}
                className="font-medium"
              >
                Browse files
              </Button>

              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept={SUPPORTED_EXTENSIONS.join(',')}
                onChange={handleFileSelect}
              />

              {error && (
                <div className="absolute bottom-6 left-6 right-6">
                  <Alert variant="destructive">
                    <AlertTitle>Error</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                </div>
              )}
            </div>
          )}

          {/* Loading state */}
          {loading && selectedFile && (
            <Card className="min-h-[400px] flex items-center justify-center">
              <CardContent className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
                <p className="text-lg font-semibold mb-1">Inspecting file...</p>
                <p className="text-sm text-muted-foreground">
                  {selectedFile.name} ({formatFileSize(selectedFile.size)})
                </p>
              </CardContent>
            </Card>
          )}

          {/* Results */}
          {verifyResponse && selectedFile && !loading && (
            <div className="space-y-4">
              {/* File info bar */}
              <div className="flex items-center justify-between p-4 rounded-lg bg-card border">
                <div className="flex items-center gap-3 min-w-0">
                  {/* TEAM_160: PDF thumbnail or file icon */}
                  {pdfThumbnailUrl ? (
                    <img
                      src={pdfThumbnailUrl}
                      alt="PDF page 1"
                      className="shrink-0 w-16 h-auto rounded border border-muted shadow-sm"
                    />
                  ) : (
                    <div className="shrink-0 w-10 h-10 rounded-lg bg-muted flex items-center justify-center text-lg">
                      {isPdfFile(selectedFile.name, selectedFile.type) ? '📕' : '📄'}
                    </div>
                  )}
                  <div className="min-w-0">
                    <p className="font-medium truncate">{selectedFile.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(selectedFile.size)}
                      {fileContent && ` · ${fileContent.length.toLocaleString()} characters`}
                    </p>
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={resetState}>
                  Inspect another file
                </Button>
              </div>

              {/* Verification status */}
              <Alert
                variant={verifyResponse.verification_status === 'Success' ? 'default' : 'destructive'}
                className={getStatusUI(verifyResponse).className}
              >
                <AlertTitle className="flex items-center gap-2">
                  <span>{getStatusUI(verifyResponse).icon}</span>
                  {getStatusUI(verifyResponse).title}
                </AlertTitle>
                <AlertDescription>
                  <div className="mb-2">{getStatusUI(verifyResponse).description}</div>

                  {verifyResponse.error ? (
                    <div className="text-xs">
                      <strong>Error Details:</strong> {getErrorMessage(verifyResponse.error, 'An unknown error occurred.')}
                    </div>
                  ) : (
                    <>
                      {/* Multi-embedding summary */}
                      {(verifyResponse.embeddings_found || 0) > 1 && verifyResponse.all_embeddings && (
                        <div className="mb-4 p-3 bg-slate-800 rounded border border-slate-700">
                          <div className="flex items-center justify-between mb-2">
                            <strong className="text-slate-200">Embeddings Summary</strong>
                            <span className="text-xs text-slate-400">
                              {verifyResponse.all_embeddings.filter(e => e.verdict?.valid).length} verified / {verifyResponse.embeddings_found} total
                            </span>
                          </div>
                          <div className="grid grid-cols-3 gap-2 text-center text-xs">
                            <div className="p-2 bg-green-900/30 rounded border border-green-700">
                              <div className="text-lg font-bold text-green-400">
                                {verifyResponse.all_embeddings.filter(e => e.verdict?.valid).length}
                              </div>
                              <div className="text-green-300">Verified</div>
                            </div>
                            <div className="p-2 bg-yellow-900/30 rounded border border-yellow-700">
                              <div className="text-lg font-bold text-yellow-400">
                                {verifyResponse.all_embeddings.filter(e => e.verdict?.tampered || (!e.verdict?.valid && e.metadata)).length}
                              </div>
                              <div className="text-yellow-300">Tampered</div>
                            </div>
                            <div className="p-2 bg-red-900/30 rounded border border-red-700">
                              <div className="text-lg font-bold text-red-400">
                                {verifyResponse.all_embeddings.filter(e => !e.verdict?.valid && !e.verdict?.tampered && !e.metadata).length}
                              </div>
                              <div className="text-red-300">Failed</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Document coverage summary — Tier 2 */}
                      {verifyResponse.total_segments_in_document && (verifyResponse.embeddings_found || 0) >= 1 && (
                        <div className="mb-4 p-3 bg-slate-800/60 rounded border border-slate-600 flex items-center gap-3">
                          <span className="text-base">📄</span>
                          <div className="text-sm text-slate-200">
                            <strong>{verifyResponse.embeddings_found}</strong> of{' '}
                            <strong>{verifyResponse.total_segments_in_document}</strong> segments verified from this document
                            {verifyResponse.segment_embeddings?.[0]?.manifest_mode && (
                              <span className="ml-2 px-1.5 py-0.5 bg-slate-700 text-slate-300 rounded text-xs font-mono">
                                {verifyResponse.segment_embeddings[0].manifest_mode}
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Individual embeddings list */}
                      {(verifyResponse.embeddings_found || 0) >= 1 && verifyResponse.all_embeddings && (
                        <div className="space-y-2 mb-4">
                          <div className="flex items-center justify-between">
                            <strong className="block text-slate-300 text-sm">
                              {verifyResponse.embeddings_found === 1 ? 'Manifest Details:' : `All Embeddings (${verifyResponse.embeddings_found}):`}
                            </strong>
                            {(verifyResponse.embeddings_found || 0) > 1 && (
                              <div className="flex gap-2">
                                <button
                                  onClick={expandAllEmbeddings}
                                  className="text-xs text-blue-400 hover:text-blue-300 underline"
                                >
                                  Expand All
                                </button>
                                <button
                                  onClick={collapseAllEmbeddings}
                                  className="text-xs text-blue-400 hover:text-blue-300 underline"
                                >
                                  Collapse All
                                </button>
                              </div>
                            )}
                          </div>
                          <div className="max-h-96 overflow-y-auto space-y-2">
                            {verifyResponse.all_embeddings.map((embedding, idx) => {
                              const isExpanded = expandedEmbeddings.has(idx);
                              const hasC2PAStructure = embedding.metadata && (
                                '@context' in embedding.metadata ||
                                'assertions' in embedding.metadata ||
                                'instance_id' in embedding.metadata
                              );
                              const isBasicFormat = embedding.metadata?.format === 'basic';
                              const isC2PAManifest = hasC2PAStructure && !isBasicFormat;
                              const manifestType = isC2PAManifest ? 'C2PA Document Manifest' : `Sentence Embedding #${embedding.index}`;
                              // TEAM_171: Look up segment location from the segment_embeddings array
                              const segDetail = verifyResponse.segment_embeddings?.[idx];
                              const segLoc = segDetail?.segment_location;

                              return (
                                <div
                                  key={idx}
                                  className={`rounded border text-xs ${getEmbeddingStatusClass(embedding)}`}
                                >
                                  <button
                                    onClick={() => toggleEmbedding(idx)}
                                    className="w-full p-2 flex items-center justify-between hover:bg-slate-700/30 transition-colors"
                                  >
                                    <div className="flex items-center gap-2 flex-wrap">
                                      <span className="text-slate-400 transition-transform" style={{ transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)' }}>
                                        ▶
                                      </span>
                                      <span className="font-medium">
                                        {getEmbeddingStatusIcon(embedding)} {manifestType}
                                      </span>
                                      {isC2PAManifest && (
                                        <span className="px-1.5 py-0.5 bg-blue-700 text-blue-100 rounded text-xs">
                                          Primary
                                        </span>
                                      )}
                                      {segLoc && !isC2PAManifest && (
                                        <span className="px-1.5 py-0.5 bg-slate-600 text-slate-200 rounded text-xs">
                                          Paragraph {segLoc.paragraph_index + 1}, Sentence {segLoc.sentence_in_paragraph + 1}
                                        </span>
                                      )}
                                    </div>
                                    <span className={`px-2 py-0.5 rounded text-xs ${
                                      embedding.verdict?.valid ? 'bg-green-700 text-green-100' :
                                      (embedding.verdict?.tampered || (!embedding.verdict?.valid && embedding.metadata)) ? 'bg-yellow-700 text-yellow-100' :
                                      'bg-red-700 text-red-100'
                                    }`}>
                                      {embedding.verdict?.valid ? 'Verified' : (embedding.verdict?.tampered || (!embedding.verdict?.valid && embedding.metadata)) ? 'Tampered' : 'Failed'}
                                    </span>
                                  </button>

                                  {isExpanded && (
                                    <div className="p-3 pt-0 border-t border-slate-700/50">
                                      {/* TEAM_160: Signer & Reason Code summary shown before manifest */}
                                      {(embedding.verdict?.signer_name || embedding.verdict?.reason_code) && (
                                        <div className="mt-2 p-2.5 bg-slate-800 rounded border border-slate-600 space-y-1">
                                          {embedding.verdict?.signer_name && (
                                            <div className="text-white">
                                              <strong>Signer:</strong> {embedding.verdict.signer_name}
                                              {embedding.verdict?.signer_id && (
                                                <span className="text-slate-300 ml-1">({embedding.verdict.signer_id})</span>
                                              )}
                                            </div>
                                          )}
                                          {embedding.verdict?.reason_code && (
                                            <div className="text-white">
                                              <strong>Reason Code:</strong>{' '}
                                              <span className={embedding.verdict.valid ? 'text-green-400' : 'text-yellow-400'}>
                                                {embedding.verdict.reason_code}
                                              </span>
                                            </div>
                                          )}
                                          {embedding.verdict?.timestamp && (
                                            <div className="text-white">
                                              <strong>Signed:</strong> {new Date(embedding.verdict.timestamp).toLocaleString()}
                                            </div>
                                          )}
                                        </div>
                                      )}
                                      {embedding.clean_text && (
                                        <div className="text-white mt-2">
                                          <strong>Text:</strong>
                                          <div className="mt-1 p-2 bg-slate-900 rounded text-slate-200 break-words">
                                            {embedding.clean_text}
                                          </div>
                                        </div>
                                      )}
                                      {embedding.metadata && (
                                        <div className="mt-2">
                                          <strong className="text-white">Full Manifest Data:</strong>
                                          <pre className="mt-1 p-2 bg-slate-900 rounded text-slate-200 whitespace-pre-wrap break-all overflow-x-auto text-xs">
                                            {JSON.stringify(embedding.metadata, null, 2)}
                                          </pre>
                                        </div>
                                      )}
                                      {embedding.error && (
                                        <div className="text-red-200 mt-2">
                                          <strong>Error:</strong> {embedding.error}
                                        </div>
                                      )}
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {/* TEAM_160: Fallback — show signer info when no all_embeddings array */}
                      {!verifyResponse.all_embeddings && verifyResponse.metadata && (() => {
                        const verdict = verifyResponse.raw_hidden_data;
                        const manifest = (verifyResponse.metadata as Record<string, unknown>)?.manifest;
                        const hasManifest = manifest && typeof manifest === 'object' && Object.keys(manifest as object).length > 0;
                        const statusClass = verdict?.valid
                          ? 'border-green-700 bg-green-900/30'
                          : (verdict?.tampered && hasManifest)
                            ? 'border-yellow-700 bg-yellow-900/30'
                            : 'border-red-700 bg-red-900/30';
                        const statusIcon = verdict?.valid ? '✅' : (verdict?.tampered && hasManifest) ? '⚠️' : '❌';
                        const statusLabel = verdict?.valid ? 'Verified' : (verdict?.tampered && hasManifest) ? 'Tampered' : 'Failed';
                        const statusBadge = verdict?.valid
                          ? 'bg-green-700 text-green-100'
                          : (verdict?.tampered && hasManifest)
                            ? 'bg-yellow-700 text-yellow-100'
                            : 'bg-red-700 text-red-100';
                        const isExpanded = expandedEmbeddings.has(0);

                        return (
                          <div className="space-y-2 mb-4">
                            <strong className="block text-slate-300 text-sm">Manifest Details:</strong>
                            <div className={`rounded border text-xs ${statusClass}`}>
                              <button
                                onClick={() => toggleEmbedding(0)}
                                className="w-full p-2 flex items-center justify-between hover:bg-slate-700/30 transition-colors"
                              >
                                <div className="flex items-center gap-2">
                                  <span className="text-slate-400 transition-transform" style={{ transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)' }}>
                                    ▶
                                  </span>
                                  <span className="font-medium">
                                    {statusIcon} C2PA Document Manifest
                                  </span>
                                  <span className="px-1.5 py-0.5 bg-blue-700 text-blue-100 rounded text-xs">
                                    Primary
                                  </span>
                                </div>
                                <span className={`px-2 py-0.5 rounded text-xs ${statusBadge}`}>
                                  {statusLabel}
                                </span>
                              </button>

                              {isExpanded && (
                                <div className="p-3 pt-0 border-t border-slate-700/50">
                                  {/* Signer & Reason Code summary */}
                                  {!!(verdict || hasManifest) && (
                                    <div className="mt-2 p-2.5 bg-slate-800 rounded border border-slate-600 space-y-1">
                                      <div className="text-white">
                                        <strong>Signer:</strong>{' '}
                                        {String(
                                          verdict?.signer_name ||
                                          verdict?.signer_id ||
                                          (typeof manifest === 'object' &&
                                           (manifest as Record<string, unknown>)?.claim_generator) ||
                                          "Unknown"
                                        )}
                                      </div>
                                      <div className="text-white">
                                        <strong>Reason Code:</strong>{' '}
                                        <span className={verdict?.valid ? 'text-green-400' : 'text-yellow-400'}>
                                          {verdict?.reason_code ||
                                           (verdict?.valid ? "VERIFIED" : "Unknown")}
                                        </span>
                                      </div>
                                      {verdict?.timestamp && (
                                        <div className="text-white">
                                          <strong>Signed:</strong> {new Date(verdict.timestamp).toLocaleString()}
                                        </div>
                                      )}
                                    </div>
                                  )}
                                  <div className="mt-2">
                                    <strong className="text-white">Full Manifest Data:</strong>
                                    <pre className="mt-1 p-2 bg-slate-900 rounded text-slate-200 whitespace-pre-wrap break-all overflow-x-auto text-xs">
                                      {JSON.stringify(verifyResponse.metadata, null, 2)}
                                    </pre>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })()}
                    </>
                  )}
                </AlertDescription>
              </Alert>

              {/* File content preview */}
              {fileContent && (
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-3">
                      <strong className="text-sm">File Content Preview</strong>
                      <span className="text-xs text-muted-foreground">
                        {fileContent.length > 2000 ? 'First 2,000 characters shown' : `${fileContent.length.toLocaleString()} characters`}
                      </span>
                    </div>
                    <pre className="p-4 bg-muted rounded-lg text-xs font-mono whitespace-pre-wrap break-words max-h-64 overflow-y-auto">
                      {fileContent.length > 2000 ? fileContent.slice(0, 2000) + '\n\n... (truncated)' : fileContent}
                    </pre>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
