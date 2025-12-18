"use client";

import { useState, useEffect } from "react";
import { Shield, ShieldCheck, ShieldX, Loader2, AlertTriangle, FileCheck, Scale, BarChart3, ChevronDown, ChevronUp, Code } from "lucide-react";
import { cn } from "@/lib/utils";
import { verifyContent, VerifyResponse } from "@/lib/api";
import { AI_CHAT_SCENARIOS, LICENSING_DATA } from "@/lib/demo-data";

interface VerificationDecoderProps {
  textToVerify: string | null;
  isAccurate: boolean | null;
  markedContent: string | null;
  onReset: () => void;
  onVerificationComplete?: (verifiedSentence: string | null) => void;
}

interface DiffHighlight {
  original: string;
  modified: string;
}

export default function VerificationDecoder({
  textToVerify,
  isAccurate,
  markedContent,
  onReset,
  onVerificationComplete,
}: VerificationDecoderProps) {
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<VerifyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showDiff, setShowDiff] = useState(false);
  const [showManifest, setShowManifest] = useState(false);
  const [displayQuote, setDisplayQuote] = useState<string>("");

  // Auto-verify when text is provided
  useEffect(() => {
    if (textToVerify && markedContent) {
      performVerification();
    }
  }, [textToVerify]);

  // Strip invisible Unicode characters for display
  const getVisibleText = (text: string): string => {
    return text.replace(/[\uFE00-\uFE0F\u{E0100}-\u{E01EF}\u200B-\u200D\uFEFF]/gu, "");
  };

  const performVerification = async () => {
    if (!textToVerify || !markedContent) return;

    setIsVerifying(true);
    setError(null);
    setVerificationResult(null);
    setShowDiff(false);

    // Simulate verification delay for dramatic effect
    await new Promise((resolve) => setTimeout(resolve, 1500));

    try {
      // Check if the quote matches the original content (strip invisible chars for comparison)
      const originalText = getVisibleText(markedContent);
      const quoteVisible = getVisibleText(textToVerify);
      const quoteExistsInOriginal = originalText.includes(quoteVisible);

      // Store the quote for display
      setDisplayQuote(quoteVisible);

      // For accurate quotes that exist in original, verify the FULL markedContent
      // The full document has the C2PA wrapper with signer_id
      const textToSend = (isAccurate && quoteExistsInOriginal) ? markedContent : textToVerify;
      const result = await verifyContent(textToSend);
      setVerificationResult(result);

      if (result.valid && quoteExistsInOriginal) {
        // Notify parent of successful verification for highlighting
        onVerificationComplete?.(quoteVisible);
      } else if (!isAccurate) {
        setShowDiff(true);
      }
    } catch (err) {
      console.error("Verification error:", err);
      // Set error state with required fields
      setVerificationResult({
        valid: false,
        tampered: true,
        reason_code: "VERIFICATION_ERROR",
        error: err instanceof Error ? err.message : "Verification failed",
      });
      if (!isAccurate) {
        setShowDiff(true);
      }
    } finally {
      setIsVerifying(false);
    }
  };

  const getDiffHighlights = (): DiffHighlight[] => {
    if (isAccurate) return [];
    return AI_CHAT_SCENARIOS.modified.modifications;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-delft-blue to-blue-ncs text-white px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="bg-white/20 p-2 rounded-lg">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <div className="font-bold">Encypher Verification Decoder</div>
            <div className="text-columbia-blue text-sm">Cryptographic provenance verification</div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {!textToVerify ? (
          // Empty state
          <div className="text-center py-12 text-gray-400">
            <Shield className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium mb-2">Paste text to verify</p>
            <p className="text-sm">Use the AI chat above to select a quote, then verify it here</p>
          </div>
        ) : isVerifying ? (
          // Loading state
          <div className="text-center py-12">
            <Loader2 className="w-12 h-12 mx-auto mb-4 animate-spin text-blue-ncs" />
            <p className="text-lg font-medium text-gray-700">Verifying provenance...</p>
            <p className="text-sm text-gray-500 mt-2">Checking cryptographic signature</p>
          </div>
        ) : verificationResult ? (
          // Result state
          <div className="space-y-6">
            {/* Result Banner */}
            <div
              className={cn(
                "rounded-xl p-6 border-2",
                verificationResult.valid
                  ? "bg-green-50 border-green-500 pulse-green"
                  : "bg-red-50 border-red-500 pulse-red"
              )}
            >
              <div className="flex items-start gap-4">
                {verificationResult.valid ? (
                  <ShieldCheck className="w-10 h-10 text-green-600 flex-shrink-0" />
                ) : (
                  <ShieldX className="w-10 h-10 text-red-600 flex-shrink-0" />
                )}
                <div>
                  <h3
                    className={cn(
                      "text-xl font-bold",
                      verificationResult.valid ? "text-green-800" : "text-red-800"
                    )}
                  >
                    {verificationResult.valid
                      ? "✅ Provenance Verified"
                      : "❌ Provenance Mismatch"}
                  </h3>
                  <p
                    className={cn(
                      "mt-1",
                      verificationResult.valid ? "text-green-700" : "text-red-700"
                    )}
                  >
                    {verificationResult.valid
                      ? "This text matches AP's original publication exactly. Hash confirmed."
                      : "This text has been modified from the original."}
                  </p>
                </div>
              </div>
            </div>

            {/* Quote being verified */}
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="text-sm font-medium text-gray-500 mb-2">Quote Being Verified:</div>
              <p className="text-gray-800 italic">&ldquo;{displayQuote.slice(0, 300)}{displayQuote.length > 300 ? '...' : ''}&rdquo;</p>
            </div>

            {/* Success details */}
            {verificationResult.valid && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div className="flex items-center gap-2 text-sm font-medium text-gray-500 mb-2">
                      <FileCheck className="w-4 h-4" />
                      Signer Information
                    </div>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-gray-500">Signer ID:</span>{" "}
                        <span className="font-semibold text-gray-800">
                          {verificationResult.signer_id || "Unknown"}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Signer Name:</span>{" "}
                        <span className="text-gray-800">{verificationResult.signer_name || "N/A"}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Reason Code:</span>{" "}
                        <span className="text-green-600 font-semibold">{verificationResult.reason_code}</span>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div className="flex items-center gap-2 text-sm font-medium text-gray-500 mb-2">
                      <Shield className="w-4 h-4" />
                      Verification Status
                    </div>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-gray-500">Valid:</span>{" "}
                        <span className="text-green-600 font-semibold">✓ TRUE</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Tampered:</span>{" "}
                        <span className="text-green-600 font-semibold">✗ FALSE</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Format:</span>{" "}
                        <span className="text-gray-800">C2PA Text Manifest</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* C2PA Manifest Dropdown */}
                {verificationResult.manifest && (
                  <div className="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
                    <button
                      onClick={() => setShowManifest(!showManifest)}
                      className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                        <Code className="w-4 h-4" />
                        C2PA Manifest Data
                      </div>
                      {showManifest ? (
                        <ChevronUp className="w-4 h-4 text-gray-500" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-gray-500" />
                      )}
                    </button>
                    {showManifest && (
                      <div className="px-4 pb-4">
                        <pre className="bg-gray-900 text-green-400 p-4 rounded-lg text-xs overflow-x-auto max-h-64 overflow-y-auto">
                          {JSON.stringify(verificationResult.manifest, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}

                {/* Rights/Licensing Metadata Card */}
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <div className="flex items-center gap-2 text-sm font-medium text-gray-500 mb-2">
                    <Scale className="w-4 h-4" />
                    Embedded Rights
                  </div>
                  <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                    <div>
                      <span className="text-gray-500">License Type:</span>{" "}
                      <span className="text-gray-800">{LICENSING_DATA.licenseType}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Permitted Uses:</span>{" "}
                      <span className="text-gray-800">{LICENSING_DATA.permittedUses}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Restrictions:</span>{" "}
                      <span className="text-gray-800">{LICENSING_DATA.restrictions}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Contact:</span>{" "}
                      <span className="text-blue-600">{LICENSING_DATA.contact}</span>
                    </div>
                  </div>
                </div>

                {/* Usage Counter - Simulated */}
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2 text-sm font-medium text-blue-800">
                        <BarChart3 className="w-4 h-4" />
                        Content Retrieval Analytics
                      </div>
                      <div className="text-xs text-blue-600 mt-1">This sentence has been retrieved for AI grounding</div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-700">47</div>
                      <div className="text-xs text-blue-500">times this month</div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Failure details - show diff */}
            {!verificationResult.valid && showDiff && (
              <div className="bg-red-50/50 rounded-lg p-4 border border-red-200">
                <div className="flex items-center gap-2 text-sm font-medium text-red-700 mb-3">
                  <AlertTriangle className="w-4 h-4" />
                  Modifications Detected
                </div>
                <div className="space-y-3">
                  {getDiffHighlights().map((diff, index) => (
                    <div key={index} className="flex items-center gap-4 text-sm">
                      {diff.original && (
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded line-through">
                          {diff.original}
                        </span>
                      )}
                      <span className="text-gray-400">→</span>
                      <span className="bg-red-100 text-red-800 px-2 py-1 rounded">
                        {diff.modified}
                      </span>
                    </div>
                  ))}
                </div>
                <p className="mt-4 text-sm text-red-700">
                  The AI claimed this text was from AP, but these modifications prove it was altered
                  from the original published content.
                </p>
              </div>
            )}

            {/* Key insight */}
            <div className="bg-gradient-to-r from-columbia-blue/20 to-blue-ncs/10 rounded-lg p-4 border border-columbia-blue">
              <p className="text-delft-blue text-sm">
                {verificationResult.valid ? (
                  <strong>
                    This is the difference between &quot;the AI says it&apos;s from AP&quot; and
                    &quot;we can mathematically prove it&apos;s from AP—and prove it wasn&apos;t
                    altered.&quot;
                  </strong>
                ) : (
                  <strong>
                    Without provenance verification, this misattribution would have gone undetected.
                    AI hallucinations can damage publisher credibility.
                  </strong>
                )}
              </p>
            </div>

            {/* Reset button */}
            <button
              onClick={onReset}
              className="w-full py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors"
            >
              Verify Another Quote
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
