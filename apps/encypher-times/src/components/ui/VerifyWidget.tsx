"use client";

import { useState } from "react";
import { AlertTriangle, Loader2, Minus } from "lucide-react";
import { verifyContent, type VerifyResult } from "@/lib/api";
import { EncypherMark } from "@/components/ui/EncypherMark";

export function VerifyWidget() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VerifyResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleVerify() {
    if (!text.trim()) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await verifyContent(text);
      setResult(res);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Verification request failed"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label
          htmlFor="verify-text"
          className="block font-[family-name:var(--font-ui)] text-sm font-medium text-ink mb-2"
        >
          Paste text to verify
        </label>
        <textarea
          id="verify-text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={6}
          placeholder="Paste any text from this site. If it carries an Encypher signature, you'll see proof of who published it and whether it's been altered."
          className="w-full p-3 border border-rule-light rounded font-[family-name:var(--font-body)] text-sm text-ink bg-white placeholder:text-ink-faint/60 focus:outline-none focus:ring-2 focus:ring-blue-ncs/30 focus:border-blue-ncs resize-y"
        />
      </div>

      <button
        onClick={handleVerify}
        disabled={loading || !text.trim()}
        className="inline-flex items-center gap-2 px-4 py-2 bg-delft-blue text-white font-[family-name:var(--font-ui)] text-sm font-medium rounded hover:bg-delft-blue/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <EncypherMark className="w-4 h-4" color="white" />
        )}
        {loading ? "Verifying..." : "Verify"}
      </button>

      {/* Verified Result */}
      {result && result.valid && !result.tampered && (
        <div className="p-4 rounded border bg-[#B7D5ED]/20 border-[#00CED1]/40">
          <div className="flex items-center gap-2 mb-3">
            <EncypherMark className="w-5 h-5" color="teal" />
            <span className="font-[family-name:var(--font-ui)] text-sm font-bold text-delft-blue">
              Signature Verified
            </span>
          </div>
          <dl className="font-[family-name:var(--font-ui)] text-xs space-y-1.5">
            {result.signerName && result.signerName !== "Unknown" && (
              <div className="flex gap-2">
                <dt className="text-ink-faint w-28 shrink-0">Publisher:</dt>
                <dd className="text-ink font-medium">{result.signerName}</dd>
              </div>
            )}
            {result.signedAt && (
              <div className="flex gap-2">
                <dt className="text-ink-faint w-28 shrink-0">Signed:</dt>
                <dd className="text-ink">{result.signedAt}</dd>
              </div>
            )}
            <div className="flex gap-2">
              <dt className="text-ink-faint w-28 shrink-0">Status:</dt>
              <dd className="text-ink">
                Original -- no modifications detected
              </dd>
            </div>
          </dl>
          <p className="font-[family-name:var(--font-ui)] text-xs text-ink-muted mt-3 leading-relaxed">
            This text carries a valid Encypher signature confirming it was
            published by {result.signerName || "the original publisher"} and has
            not been altered since signing.
          </p>
        </div>
      )}

      {/* Content Modified Result */}
      {result && result.tampered && (
        <div className="p-4 rounded border bg-amber-50/60 border-amber-300/60">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <span className="font-[family-name:var(--font-ui)] text-sm font-bold text-amber-800">
              Content Modified
            </span>
          </div>
          <dl className="font-[family-name:var(--font-ui)] text-xs space-y-1.5">
            {result.signerName && result.signerName !== "Unknown" && (
              <div className="flex gap-2">
                <dt className="text-ink-faint w-28 shrink-0">Publisher:</dt>
                <dd className="text-ink font-medium">{result.signerName}</dd>
              </div>
            )}
            <div className="flex gap-2">
              <dt className="text-ink-faint w-28 shrink-0">Signature:</dt>
              <dd className="text-teal-700 font-medium">
                Valid -- original signer confirmed
              </dd>
            </div>
            <div className="flex gap-2">
              <dt className="text-ink-faint w-28 shrink-0">Integrity:</dt>
              <dd className="text-amber-800 font-medium">
                Modified -- text has been altered since signing
              </dd>
            </div>
          </dl>
          <p className="font-[family-name:var(--font-ui)] text-xs text-ink-muted mt-3 leading-relaxed">
            This text carries a valid Encypher signature from{" "}
            {result.signerName || "the original publisher"}, but the visible
            content has been changed since it was signed. The original
            cryptographic hash no longer matches.
          </p>
        </div>
      )}

      {/* No Signature / Invalid Result */}
      {result && !result.valid && !result.tampered && (
        <div className="p-4 rounded border bg-neutral-50 border-neutral-200">
          <div className="flex items-center gap-2 mb-3">
            <Minus className="w-5 h-5 text-[#A7AFBC]" />
            <span className="font-[family-name:var(--font-ui)] text-sm font-bold text-ink-muted">
              No Signature Detected
            </span>
          </div>
          <p className="font-[family-name:var(--font-ui)] text-xs text-ink-muted leading-relaxed">
            This text does not contain an Encypher signature. It may be unsigned
            content, or the signature may have been stripped during processing.
          </p>
        </div>
      )}

      {/* Network Error */}
      {error && (
        <div className="p-4 rounded border bg-amber-50 border-amber-200">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-700" />
            <span className="font-[family-name:var(--font-ui)] text-sm text-amber-800">
              {error}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
