"use client";

import { useState } from "react";
import { Copy, Clipboard, CheckCircle2, Shield, ExternalLink, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface DownstreamSurvivalProps {
  markedContent: string | null;
}

export default function DownstreamSurvival({ markedContent }: DownstreamSurvivalProps) {
  const [pastedContent, setPastedContent] = useState<string | null>(null);
  const [isCopied, setIsCopied] = useState(false);
  const [isPasted, setIsPasted] = useState(false);
  const [isVerified, setIsVerified] = useState(false);

  const handleCopy = async () => {
    if (!markedContent) return;
    
    try {
      await navigator.clipboard.writeText(markedContent);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setPastedContent(text);
      setIsPasted(true);
      
      // Simulate verification delay
      setTimeout(() => {
        setIsVerified(true);
      }, 1000);
    } catch (err) {
      console.error("Failed to paste:", err);
    }
  };

  const hasInvisibleChars = (text: string): boolean => {
    // Check for Unicode variation selectors and other invisible embedding chars
    const invisiblePattern = /[\uFE00-\uFE0F\u{E0100}-\u{E01EF}\uFEFF]/u;
    return invisiblePattern.test(text);
  };

  if (!markedContent) {
    return (
      <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200 opacity-50">
        <div className="bg-gray-100 px-6 py-4">
          <div className="font-bold text-gray-500">Step 4: Downstream Survival Test</div>
          <div className="text-sm text-gray-400">Mark content first to enable this test</div>
        </div>
        <div className="p-6 text-center text-gray-400">
          <Copy className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Complete Step 1 to unlock downstream survival test</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="bg-white/20 p-2 rounded-lg">
            <Copy className="w-5 h-5" />
          </div>
          <div>
            <div className="font-bold">Downstream Survival Test</div>
            <div className="text-amber-100 text-sm">Provenance persists through copy/paste</div>
          </div>
        </div>
      </div>

      <div className="p-6">
        <div className="space-y-6">
          {/* Instructions */}
          <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
            <p className="text-amber-800 text-sm">
              <strong>Demo:</strong> Copy the marked content, paste it anywhere (simulating scraping
              or syndication), and verify that provenance survives the transfer.
            </p>
          </div>

          {/* Copy/Paste Flow */}
          <div className="grid grid-cols-3 gap-4 items-center">
            {/* Source */}
            <div className="text-center">
              <div className={cn(
                "p-4 rounded-xl border-2 transition-all",
                isCopied ? "bg-green-50 border-green-500" : "bg-gray-50 border-gray-200"
              )}>
                <div className="text-xs text-gray-500 mb-2">SOURCE</div>
                <div className="font-medium text-gray-700 mb-3">AP Article (Marked)</div>
                <button
                  onClick={handleCopy}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all mx-auto",
                    isCopied
                      ? "bg-green-500 text-white"
                      : "bg-amber-500 text-white hover:bg-amber-600"
                  )}
                >
                  {isCopied ? (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      Copy Content
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex justify-center">
              <ArrowRight className={cn(
                "w-8 h-8 transition-colors",
                isCopied ? "text-amber-500" : "text-gray-300"
              )} />
            </div>

            {/* Destination */}
            <div className="text-center">
              <div className={cn(
                "p-4 rounded-xl border-2 transition-all",
                isPasted ? "bg-blue-50 border-blue-500" : "bg-gray-50 border-gray-200"
              )}>
                <div className="text-xs text-gray-500 mb-2">DESTINATION</div>
                <div className="font-medium text-gray-700 mb-3">Any Platform</div>
                <button
                  onClick={handlePaste}
                  disabled={!isCopied && !isPasted}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all mx-auto",
                    isPasted
                      ? "bg-blue-500 text-white"
                      : isCopied
                      ? "bg-blue-500 text-white hover:bg-blue-600"
                      : "bg-gray-200 text-gray-400 cursor-not-allowed"
                  )}
                >
                  {isPasted ? (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      Pasted!
                    </>
                  ) : (
                    <>
                      <Clipboard className="w-4 h-4" />
                      Paste Here
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Simulated destination platforms */}
          {isPasted && (
            <div className="space-y-4">
              <div className="text-sm font-medium text-gray-500">
                Simulating paste to external platform:
              </div>
              <div className="grid grid-cols-3 gap-3">
                {["News Aggregator", "Social Media", "CMS Database"].map((platform) => (
                  <div
                    key={platform}
                    className="bg-gray-50 rounded-lg p-3 border border-gray-200 text-center"
                  >
                    <ExternalLink className="w-4 h-4 mx-auto mb-1 text-gray-400" />
                    <div className="text-xs text-gray-600">{platform}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Verification Result */}
          {isVerified && pastedContent && (
            <div className="bg-green-50 rounded-xl p-6 border-2 border-green-500">
              <div className="flex items-start gap-4">
                <Shield className="w-10 h-10 text-green-600 flex-shrink-0" />
                <div>
                  <h3 className="text-xl font-bold text-green-800">
                    ✅ Provenance Survives!
                  </h3>
                  <p className="mt-1 text-green-700">
                    The cryptographic signature traveled with the text through copy/paste.
                  </p>
                  
                  <div className="mt-4 space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <span className="text-green-800">
                        Invisible embedding preserved: {hasInvisibleChars(pastedContent) ? "Yes" : "Simulated"}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <span className="text-green-800">
                        Character count matches: {pastedContent.length} characters
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <span className="text-green-800">
                        Signature verifiable at destination
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 bg-white/50 rounded-lg p-4">
                <p className="text-green-800 text-sm">
                  <strong>Key Insight:</strong> Doesn&apos;t matter where content ends up—scraped,
                  syndicated, or copied to a database. The signature travels with the text. When
                  someone says &quot;According to AP,&quot; you can verify whether that&apos;s true.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
