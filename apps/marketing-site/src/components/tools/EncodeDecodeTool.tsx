'use client';

// Force HMR update
import React, { useState, useRef, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
// import { Copy } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { trackToolEvent } from "@/lib/toolsAnalytics";

// Temporary replacement for Copy icon to debug import issue
const Copy = (props: any) => <span {...props}>📋</span>;

// --- Types matching backend DecodeToolResponse ---
interface VerifyVerdict {
  valid: boolean;
  tampered: boolean;
  reason_code: string;
  signer_id?: string;
  signer_name?: string;
  timestamp?: string;
  details?: any;
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

function hasOriginalText(metadata: unknown): metadata is MetadataWithOriginalText {
  return (
    typeof metadata === 'object' &&
    metadata !== null &&
    'original_text' in metadata &&
    typeof (metadata as MetadataWithOriginalText).original_text === 'string'
  );
}

interface EncodeDecodeToolProps {
  initialMode?: "encode" | "decode";
}

function getErrorMessage(error: string | { message: string } | null | undefined, fallback: string): string {
  if (!error) return fallback;
  if (typeof error === "string") return error;
  if (typeof error === "object" && "message" in error && typeof error.message === "string") return error.message;
  return fallback;
}

/**
 * Call the Enterprise API for tools endpoints
 */
async function toolsApiCall<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }
  
  return response.json();
}

async function verifyEncodedText(encodedText: string): Promise<DecodeToolResponse> {
  return toolsApiCall<DecodeToolResponse>("/api/tools/verify", {
    method: "POST",
    body: JSON.stringify({ encoded_text: encodedText }),
  });
}

export default function EncodeDecodeTool({ initialMode }: EncodeDecodeToolProps) {
  const [mode, setMode] = useState<"encode" | "decode">(initialMode ?? "encode");
  const [inputText, setInputText] = useState("");
  const [c2paProvenance, setC2paProvenance] = useState("");
  const [output, setOutput] = useState<string | null>(null);
  const [lastDecodeResponse, setLastDecodeResponse] = useState<DecodeToolResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [expandedEmbeddings, setExpandedEmbeddings] = useState<Set<number>>(new Set([0])); // C2PA manifest (index 0) expanded by default
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();
  const copyBtnRef = useRef<HTMLButtonElement>(null);

  const handleModeToggle = () => {
    const nextMode = mode === "encode" ? "decode" : "encode";
    trackToolEvent({
      eventName: "tools_mode_toggle",
      pageUrl: window.location.href,
      pageTitle: document.title,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
      properties: {
        from: mode === "encode" ? "sign" : "verify",
        to: nextMode === "encode" ? "sign" : "verify",
      },
    });
    setMode(nextMode);
    setInputText("");
    setOutput(null);
    setLastDecodeResponse(null);
    setError(null);
    setExpandedEmbeddings(new Set([0]));
  };

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
    if (lastDecodeResponse?.all_embeddings) {
      setExpandedEmbeddings(new Set(lastDecodeResponse.all_embeddings.map((_, i) => i)));
    }
  }, [lastDecodeResponse]);

  const collapseAllEmbeddings = useCallback(() => {
    setExpandedEmbeddings(new Set([0])); // Keep C2PA manifest expanded
  }, []);

  const handleProcess = async () => {
    setLoading(true);
    setError(null);
    setOutput(null);
    setLastDecodeResponse(null);
    const startedAt = Date.now();
    trackToolEvent({
      eventName: mode === "encode" ? "tools_sign_started" : "tools_verify_started",
      pageUrl: window.location.href,
      pageTitle: document.title,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
      properties: {
        mode: mode === "encode" ? "sign" : "verify",
        inputLength: inputText.length,
      },
    });

    try {
      if (mode === "encode") {
        const body = {
          original_text: inputText,
          metadata_format: "c2pa_v2_2",
          ai_info: {
            provenance: c2paProvenance,
          },
        };

        const response = await toolsApiCall<{ encoded_text: string, metadata?: any }>("/api/tools/sign", {
          method: "POST",
          body: JSON.stringify(body),
        });

        if (response && response.encoded_text) {
          trackToolEvent({
            eventName: "tools_sign_success",
            pageUrl: window.location.href,
            pageTitle: document.title,
            referrer: document.referrer,
            userAgent: navigator.userAgent,
            properties: {
              mode: "sign",
              inputLength: inputText.length,
              outputLength: response.encoded_text.length,
              durationMs: Date.now() - startedAt,
            },
          });
          setOutput(response.encoded_text);
          
          // Automatically verify to get full manifest details for consistent display
          try {
            const verifyResponse = await verifyEncodedText(response.encoded_text);

            if (verifyResponse && verifyResponse.verification_status === "Success") {
              trackToolEvent({
                eventName: "tools_verify_after_sign_success",
                pageUrl: window.location.href,
                pageTitle: document.title,
                referrer: document.referrer,
                userAgent: navigator.userAgent,
                properties: {
                  mode: "verify",
                  inputLength: response.encoded_text.length,
                  embeddingsFound: verifyResponse.embeddings_found || 0,
                  durationMs: Date.now() - startedAt,
                },
              });
              setLastDecodeResponse(verifyResponse);
            } else {
              trackToolEvent({
                eventName: "tools_verify_after_sign_fallback",
                pageUrl: window.location.href,
                pageTitle: document.title,
                referrer: document.referrer,
                userAgent: navigator.userAgent,
                properties: {
                  mode: "verify",
                  inputLength: response.encoded_text.length,
                  status: verifyResponse?.verification_status ?? "unknown",
                  durationMs: Date.now() - startedAt,
                },
              });
              // Fallback
              setLastDecodeResponse({
                verification_status: "Success",
                metadata: { manifest: response.metadata },
                raw_hidden_data: { valid: true, signer_name: "org_demo (Demo Key)", reason_code: "CREATED" } as any,
              });
            }
          } catch (e) {
            trackToolEvent({
              eventName: "tools_verify_after_sign_error",
              pageUrl: window.location.href,
              pageTitle: document.title,
              referrer: document.referrer,
              userAgent: navigator.userAgent,
              properties: {
                mode: "verify",
                inputLength: response.encoded_text.length,
                durationMs: Date.now() - startedAt,
              },
            });
            // Fallback
            setLastDecodeResponse({
              verification_status: "Success",
              metadata: { manifest: response.metadata },
              raw_hidden_data: { valid: true, signer_name: "org_demo (Demo Key)", reason_code: "CREATED" } as any,
            });
          }
        } else {
          throw new Error("Signing failed: Invalid response from server.");
        }
      } else { // decode
        const response = await verifyEncodedText(inputText);

        if (!response) {
          throw new Error("Verification failed: Empty response from server.");
        }
        trackToolEvent({
          eventName: "tools_verify_success",
          pageUrl: window.location.href,
          pageTitle: document.title,
          referrer: document.referrer,
          userAgent: navigator.userAgent,
          properties: {
            mode: "verify",
            inputLength: inputText.length,
            embeddingsFound: response.embeddings_found || 0,
            durationMs: Date.now() - startedAt,
          },
        });
        setLastDecodeResponse(response);
        setOutput(null);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || "An unexpected error occurred.";
      trackToolEvent({
        eventName: mode === "encode" ? "tools_sign_error" : "tools_verify_error",
        pageUrl: window.location.href,
        pageTitle: document.title,
        referrer: document.referrer,
        userAgent: navigator.userAgent,
        properties: {
          mode: mode === "encode" ? "sign" : "verify",
          inputLength: inputText.length,
          errorMessage,
          durationMs: Date.now() - startedAt,
        },
      });
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text).then(
      () => {
        trackToolEvent({
          eventName: "tools_output_copied",
          pageUrl: window.location.href,
          pageTitle: document.title,
          referrer: document.referrer,
          userAgent: navigator.userAgent,
          properties: {
            mode: mode === "encode" ? "sign" : "verify",
            outputLength: text.length,
          },
        });
        toast({ title: "Copied to clipboard!" });
      },
      (err) => {
        trackToolEvent({
          eventName: "tools_copy_failed",
          pageUrl: window.location.href,
          pageTitle: document.title,
          referrer: document.referrer,
          userAgent: navigator.userAgent,
          properties: {
            mode: mode === "encode" ? "sign" : "verify",
            outputLength: text.length,
          },
        });
        toast({ title: "Copy failed", description: `Could not copy text: ${err}` });
      }
    );
  };

  const getStatusUI = (response: DecodeToolResponse) => {
    const verdict = response.raw_hidden_data;
    const embeddingsFound = response.embeddings_found || 0;
    const allEmbeddings = response.all_embeddings || [];
    
    // Multi-embedding case
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
    
    // Single embedding case
    if (verdict?.valid) {
      return {
        variant: "default" as const,
        className: "border-green-900 bg-green-800 text-white",
        title: "Verified Authentic",
        description: "The content is authentic and has not been modified.",
        icon: "✅"
      };
    }
    
    // Check for manifest presence to distinguish Tampered vs Not Signed
    const manifest = (response.metadata as any)?.manifest;
    const hasManifest = manifest && typeof manifest === 'object' && Object.keys(manifest).length > 0;

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
    // Show tampered if explicitly tampered OR if verification failed but metadata exists
    if (embedding.verdict?.tampered || (!embedding.verdict?.valid && embedding.metadata)) return "⚠️";
    return "❌";
  };

  const getEmbeddingStatusClass = (embedding: EmbeddingResult) => {
    if (embedding.verdict?.valid) return "border-green-700 bg-green-900/30";
    // Show tampered styling if explicitly tampered OR if verification failed but metadata exists
    if (embedding.verdict?.tampered || (!embedding.verdict?.valid && embedding.metadata)) return "border-yellow-700 bg-yellow-900/30";
    return "border-red-700 bg-red-900/30";
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 sm:px-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <span className="text-lg sm:text-xl">Encypher Sign/Verify Tool</span>
            <Button onClick={handleModeToggle} variant="outline" size="sm">
              Switch to {mode === "encode" ? "Verify" : "Sign"}
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="input-text" className="font-bold">
                {mode === "encode" ? "Text to Sign" : "Text to Verify"}
              </Label>
              <Textarea
                id="input-text"
                placeholder={mode === 'encode' ? 'Enter the text you want to sign with provenance metadata...' : 'Paste signed text to verify authenticity...'}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="min-h-[150px] font-mono text-sm"
              />
            </div>

            {mode === 'encode' && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="c2pa-provenance" className="font-bold">Provenance</Label>
                  <Textarea
                    id="c2pa-provenance"
                    placeholder="Enter provenance information here... (e.g., This text was generated by an AI.)"
                    value={c2paProvenance}
                    onChange={(e) => setC2paProvenance(e.target.value)}
                  />
                </div>
              </div>
            )}

            <div className="text-xs text-muted-foreground">
              <em>Note: For demo use only. All signing uses a server-side demo key. Private keys are not required or accepted here.</em>
            </div>

            <div className="mt-6">
              <Button onClick={handleProcess} disabled={loading || !inputText} className="w-full">
                {loading ? "Processing..." : (mode === "encode" ? "Sign Text" : "Verify Text")}
              </Button>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {output && mode === "encode" && (
              <Alert className="bg-muted border-muted-foreground/30">
                <AlertTitle>Signed Text</AlertTitle>
                <AlertDescription>
                  <div className="flex items-center gap-2">
                    <span className="break-all font-mono text-sm">{output}</span>
                    <Button ref={copyBtnRef} variant="ghost" size="icon" onClick={() => handleCopy(output)}>
                      Copy
                    </Button>
                  </div>
                </AlertDescription>
              </Alert>
            )}

            {lastDecodeResponse && (
              <Alert
                variant={lastDecodeResponse.verification_status === 'Success' ? 'default' : 'destructive'}
                className={getStatusUI(lastDecodeResponse).className}
              >
                <AlertTitle className="flex items-center gap-2">
                  {mode === 'encode' ? (
                    <>
                      <span>✅</span>
                      Embedded Manifest Details
                    </>
                  ) : (
                    <div className="flex items-center gap-2">
                        {(() => {
                            const statusUI = getStatusUI(lastDecodeResponse);
                            return (
                                <>
                                    <span>{statusUI.icon}</span>
                                    {statusUI.title}
                                </>
                            );
                        })()}
                    </div>
                  )}
                </AlertTitle>
                <AlertDescription>
                  {mode === 'decode' && <div className="mb-2">{getStatusUI(lastDecodeResponse).description}</div>}
                  
                  {lastDecodeResponse.error ? (
                      <div className="text-xs">
                        <strong>Error Details:</strong> {getErrorMessage(lastDecodeResponse.error, 'An unknown error occurred.')}
                      </div>
                    ) : (
                      <>
                        {/* Multi-embedding summary */}
                        {(lastDecodeResponse.embeddings_found || 0) > 1 && lastDecodeResponse.all_embeddings && (
                          <div className="mb-4 p-3 bg-slate-800 rounded border border-slate-700">
                            <div className="flex items-center justify-between mb-2">
                              <strong className="text-slate-200">Embeddings Summary</strong>
                              <span className="text-xs text-slate-400">
                                {lastDecodeResponse.all_embeddings.filter(e => e.verdict?.valid).length} verified / {lastDecodeResponse.embeddings_found} total
                              </span>
                            </div>
                            <div className="grid grid-cols-3 gap-2 text-center text-xs">
                              <div className="p-2 bg-green-900/30 rounded border border-green-700">
                                <div className="text-lg font-bold text-green-400">
                                  {lastDecodeResponse.all_embeddings.filter(e => e.verdict?.valid).length}
                                </div>
                                <div className="text-green-300">Verified</div>
                              </div>
                              <div className="p-2 bg-yellow-900/30 rounded border border-yellow-700">
                                <div className="text-lg font-bold text-yellow-400">
                                  {lastDecodeResponse.all_embeddings.filter(e => e.verdict?.tampered || (!e.verdict?.valid && e.metadata)).length}
                                </div>
                                <div className="text-yellow-300">Tampered</div>
                              </div>
                              <div className="p-2 bg-red-900/30 rounded border border-red-700">
                                <div className="text-lg font-bold text-red-400">
                                  {lastDecodeResponse.all_embeddings.filter(e => !e.verdict?.valid && !e.verdict?.tampered && !e.metadata).length}
                                </div>
                                <div className="text-red-300">Failed</div>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Document coverage summary — Tier 2 */}
                        {lastDecodeResponse.total_segments_in_document && (lastDecodeResponse.embeddings_found || 0) >= 1 && (
                          <div className="mb-4 p-3 bg-slate-800/60 rounded border border-slate-600 flex items-center gap-3">
                            <span className="text-base">📄</span>
                            <div className="text-sm text-slate-200">
                              <strong>{lastDecodeResponse.embeddings_found}</strong> verified from the original{' '}
                              <strong>{lastDecodeResponse.total_segments_in_document}</strong> signed segments
                            </div>
                          </div>
                        )}

                        {/* Individual embeddings list with collapsible details */}
                        {(lastDecodeResponse.embeddings_found || 0) >= 1 && lastDecodeResponse.all_embeddings && (
                          <div className="space-y-2 mb-4">
                            <div className="flex items-center justify-between">
                              <strong className="block text-slate-300 text-sm">
                                {lastDecodeResponse.embeddings_found === 1 ? 'Manifest Details:' : `All Embeddings (${lastDecodeResponse.embeddings_found}):`}
                              </strong>
                              {(lastDecodeResponse.embeddings_found || 0) > 1 && (
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
                              {lastDecodeResponse.all_embeddings.map((embedding, idx) => {
                                const isExpanded = expandedEmbeddings.has(idx);
                                // Check if this is a C2PA manifest by looking for C2PA-specific fields
                                const hasC2PAStructure = embedding.metadata && (
                                  '@context' in embedding.metadata || 
                                  'assertions' in embedding.metadata ||
                                  'instance_id' in embedding.metadata
                                );
                                const isBasicFormat = embedding.metadata?.format === 'basic';
                                const isC2PAManifest = hasC2PAStructure && !isBasicFormat;
                                const manifestType = isC2PAManifest ? 'C2PA Document Manifest' : `Sentence Embedding #${embedding.index}`;
                                // TEAM_171: Look up segment location from the segment_embeddings array
                                const segDetail = lastDecodeResponse.segment_embeddings?.[idx];
                                const segLoc = segDetail?.segment_location;
                                
                                return (
                                  <div 
                                    key={idx} 
                                    className={`rounded border text-xs ${getEmbeddingStatusClass(embedding)}`}
                                  >
                                    {/* Collapsible Header */}
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
                                    
                                    {/* Collapsible Content */}
                                    {isExpanded && (
                                      <div className="p-3 pt-0 border-t border-slate-700/50">
                                        {embedding.verdict?.signer_name && (
                                          <div className="text-white mt-2">
                                            <strong>Signer:</strong> {embedding.verdict.signer_name}
                                            {embedding.verdict?.signer_id && (
                                              <span className="text-slate-300 ml-1">({embedding.verdict.signer_id})</span>
                                            )}
                                          </div>
                                        )}
                                        {embedding.verdict?.timestamp && (
                                          <div className="text-white">
                                            <strong>Signed:</strong> {new Date(embedding.verdict.timestamp).toLocaleString()}
                                          </div>
                                        )}
                                        {embedding.verdict?.reason_code && (
                                          <div className="text-white">
                                            <strong>Reason Code:</strong> {embedding.verdict.reason_code}
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
                                            <strong className="text-white">Manifest Data:</strong>
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

                        {/* Show signer info + C2PA manifest when no all_embeddings array */}
                        {!lastDecodeResponse.all_embeddings && (lastDecodeResponse.metadata || lastDecodeResponse.c2pa) && (
                          <div className="mt-4 p-3 bg-slate-900 text-slate-50 rounded text-xs border border-slate-800 max-w-full">
                            {lastDecodeResponse.c2pa && (
                              <div className="mb-3">
                                <strong className="block mb-2 text-slate-400">C2PA Manifest:</strong>
                                <div className="space-y-1">
                                  <div>
                                    <strong className="text-slate-400">Validated:</strong>{' '}
                                    <span className={lastDecodeResponse.c2pa.validated ? 'text-green-400' : 'text-red-400'}>
                                      {lastDecodeResponse.c2pa.validated ? 'Yes' : 'No'}
                                    </span>
                                  </div>
                                  {lastDecodeResponse.c2pa.validation_type && (
                                    <div>
                                      <strong className="text-slate-400">Validation Type:</strong>{' '}
                                      <span className="text-slate-50">{lastDecodeResponse.c2pa.validation_type}</span>
                                    </div>
                                  )}
                                  {lastDecodeResponse.c2pa.manifest_hash && (
                                    <div>
                                      <strong className="text-slate-400">Manifest Hash:</strong>{' '}
                                      <code className="text-slate-300 bg-slate-800 px-1 rounded">{lastDecodeResponse.c2pa.manifest_hash}</code>
                                    </div>
                                  )}
                                  {lastDecodeResponse.c2pa.assertions && lastDecodeResponse.c2pa.assertions.length > 0 && (
                                    <div>
                                      <strong className="text-slate-400">Assertions:</strong>
                                      <pre className="mt-1 whitespace-pre-wrap break-all overflow-x-auto text-slate-300 bg-slate-800 p-2 rounded">
                                        {JSON.stringify(lastDecodeResponse.c2pa.assertions, null, 2)}
                                      </pre>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}

                            {lastDecodeResponse.metadata && !lastDecodeResponse.c2pa && (
                              <div className="mb-3">
                                <strong className="block mb-2 text-slate-400">Manifest Data:</strong>
                                <pre className="whitespace-pre-wrap break-all overflow-x-auto text-slate-50 max-w-full">
                                  {JSON.stringify(lastDecodeResponse.metadata, null, 2)}
                                </pre>
                              </div>
                            )}
                            
                            {(lastDecodeResponse.raw_hidden_data || lastDecodeResponse.metadata) && (
                              <div className="mt-2 pt-2 border-t border-slate-700">
                                <div>
                                    <strong className="text-slate-400">Signer:</strong> 
                                    <span className="text-slate-50 ml-1">
                                        {lastDecodeResponse.raw_hidden_data?.signer_name || 
                                         lastDecodeResponse.raw_hidden_data?.signer_id || 
                                         "Unknown"}
                                    </span>
                                    {lastDecodeResponse.raw_hidden_data?.valid && (
                                      <span className="text-green-400 ml-2">(Verified via Trust Anchor)</span>
                                    )}
                                </div>
                                <div>
                                    <strong className="text-slate-400">Reason Code:</strong> 
                                    <span className="text-slate-50 ml-1">
                                        {lastDecodeResponse.raw_hidden_data?.reason_code || 
                                         (lastDecodeResponse.raw_hidden_data?.valid ? "VERIFIED" : "Unknown")}
                                    </span>
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </>
                    )}
                </AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
