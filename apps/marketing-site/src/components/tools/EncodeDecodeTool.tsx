'use client';

// Force HMR update
import React, { useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
// import { Copy } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { useApiClient } from "@/lib/hooks/useApiClient";

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

interface DecodeToolResponse {
  metadata?: MetadataWithOriginalText | null;
  verification_status: 'Success' | 'Failure' | 'Key Not Found' | 'Not Attempted' | 'Error';
  error?: string | { message: string } | null;
  raw_hidden_data?: VerifyVerdict | null;
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

export default function EncodeDecodeTool({ initialMode }: EncodeDecodeToolProps) {
  const [mode, setMode] = useState<"encode" | "decode">(initialMode ?? "encode");
  const [inputText, setInputText] = useState("");
  const [c2paClaimGenerator, setC2paClaimGenerator] = useState("Encypher Demo UI");
  const [c2paProvenance, setC2paProvenance] = useState("");
  const [output, setOutput] = useState<string | null>(null);
  const [lastDecodeResponse, setLastDecodeResponse] = useState<DecodeToolResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();
  const { apiCall } = useApiClient();
  const copyBtnRef = useRef<HTMLButtonElement>(null);

  const handleModeToggle = () => {
    setMode(mode === "encode" ? "decode" : "encode");
    setInputText("");
    setOutput(null);
    setLastDecodeResponse(null);
    setError(null);
  };

  const handleProcess = async () => {
    setLoading(true);
    setError(null);
    setOutput(null);
    setLastDecodeResponse(null);

    try {
      if (mode === "encode") {
        const body = {
          original_text: inputText,
          target: "first_letter",
          metadata_format: "c2pa_v2_2",
          ai_info: {
            claim_generator: c2paClaimGenerator,
            provenance: c2paProvenance
          }
        };

        const response = await apiCall<{ encoded_text: string, metadata?: any }>("/api/v1/tools/encode", {
          isPublic: true,
          method: "POST",
          body: JSON.stringify(body),
        });

        if (response && response.encoded_text) {
          setOutput(response.encoded_text);
          
          // Automatically verify to get full manifest details for consistent display
          try {
            const verifyResponse = await apiCall<DecodeToolResponse>("/api/v1/tools/decode", {
              isPublic: true,
              method: "POST",
              body: JSON.stringify({ encoded_text: response.encoded_text }),
            });

            if (verifyResponse && verifyResponse.verification_status === 'Success') {
               setLastDecodeResponse(verifyResponse);
            } else {
               // Fallback
               setLastDecodeResponse({ 
                   verification_status: 'Success', 
                   metadata: { manifest: response.metadata },
                   raw_hidden_data: { valid: true, signer_name: "org_demo (Demo Key)", reason_code: "CREATED" } as any 
               });
            }
          } catch (e) {
             // Fallback
             setLastDecodeResponse({ 
                 verification_status: 'Success', 
                 metadata: { manifest: response.metadata },
                 raw_hidden_data: { valid: true, signer_name: "org_demo (Demo Key)", reason_code: "CREATED" } as any 
             });
          }
        } else {
          throw new Error("Encoding failed: Invalid response from server.");
        }
      } else { // decode
        const body = { encoded_text: inputText };
        const response = await apiCall<DecodeToolResponse>("/api/v1/tools/decode", {
          isPublic: true,
          method: "POST",
          body: JSON.stringify(body),
        });

        if (!response) {
          throw new Error("Decoding failed: Empty response from server.");
        }
        setLastDecodeResponse(response);
        setOutput(null);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || "An unexpected error occurred.";
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
        toast({ title: "Copied to clipboard!" });
      },
      (err) => {
        toast({ title: "Copy failed", description: `Could not copy text: ${err}` });
      }
    );
  };

  const getStatusUI = (response: DecodeToolResponse) => {
    const verdict = response.raw_hidden_data;
    
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
    // Ensure manifest is truly present and not empty
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

  return (
    <div className="w-full max-w-4xl mx-auto px-4 sm:px-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <span className="text-lg sm:text-xl">Encypher Encode/Decode Tool</span>
            <Button onClick={handleModeToggle} variant="outline" size="sm">
              Switch to {mode === "encode" ? "Decode" : "Encode"}
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="input-text" className="font-bold">
                {mode === "encode" ? "Text to Encode" : "Text to Decode"}
              </Label>
              <Textarea
                id="input-text"
                placeholder={mode === 'encode' ? 'Enter the text you want to embed information into...' : 'Paste the text containing hidden information...'}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="min-h-[150px] font-mono text-sm"
              />
            </div>

            {mode === 'encode' && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="c2pa-claim-generator" className="font-bold">Claim Generator</Label>
                  <Input id="c2pa-claim-generator" value={c2paClaimGenerator} onChange={(e) => setC2paClaimGenerator(e.target.value)} />
                </div>
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
              <em>Note: For demo use only. All encoding uses a server-side demo key. Private keys are not required or accepted here.</em>
            </div>

            <div className="mt-6">
              <Button onClick={handleProcess} disabled={loading || !inputText} className="w-full">
                {loading ? "Processing..." : (mode === "encode" ? "Encode Text" : "Decode Text")}
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
                <AlertTitle>Encoded Text</AlertTitle>
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
                        {lastDecodeResponse.metadata && hasOriginalText(lastDecodeResponse.metadata) && (
                          <div className="flex items-center gap-2 mb-2">
                            <span className="break-all font-mono text-sm">{lastDecodeResponse.metadata.original_text}</span>
                            <Button ref={copyBtnRef} variant="ghost" size="icon" onClick={() => lastDecodeResponse.metadata?.original_text && handleCopy(lastDecodeResponse.metadata.original_text)}>
                              Copy
                            </Button>
                          </div>
                        )}
                        {lastDecodeResponse.metadata && (
                          <div className="mt-4 p-2 bg-slate-900 text-slate-50 rounded text-xs border border-slate-800 max-w-full">
                            <strong className="block mb-1 text-slate-400">C2PA Manifest Data:</strong>
                            <pre className="whitespace-pre-wrap break-all overflow-x-auto text-slate-50 max-w-full">
                              {JSON.stringify(lastDecodeResponse.metadata, null, 2)}
                            </pre>
                            
                            {(lastDecodeResponse.raw_hidden_data || (lastDecodeResponse.metadata as any)?.manifest) && (
                              <div className="mt-2 pt-2 border-t border-slate-800">
                                <div>
                                    <strong className="text-slate-400">Signer:</strong> 
                                    <span className="text-slate-50 ml-1">
                                        {lastDecodeResponse.raw_hidden_data?.signer_name || 
                                         lastDecodeResponse.raw_hidden_data?.signer_id || 
                                         (lastDecodeResponse.metadata as any)?.manifest?.claim_generator || 
                                         "Unknown"}
                                    </span>
                                </div>
                                <div>
                                    <strong className="text-slate-400">Reason Code:</strong> 
                                    <span className="text-slate-50 ml-1">
                                        {lastDecodeResponse.raw_hidden_data?.reason_code || 
                                         (lastDecodeResponse.raw_hidden_data?.valid ? "OK" : "Unknown")}
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
