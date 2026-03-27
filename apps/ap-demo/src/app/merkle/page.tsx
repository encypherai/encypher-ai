"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import {
  TreeDeciduous,
  FileText,
  Search,
  Shield,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  Hash,
  Layers,
  Clock,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  ArrowLeft
} from "lucide-react";
import { cn } from "@/lib/utils";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.encypher.com';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

// Sample article for encoding
const SAMPLE_ARTICLE = {
  title: "Climate Summit Reaches Historic Agreement",
  paragraphs: [
    "World leaders gathered at the Global Climate Summit have reached a landmark agreement to reduce carbon emissions by 50% by 2035.",
    "The agreement, signed by 195 nations, represents the most ambitious climate action plan in history. It includes binding commitments for both developed and developing nations.",
    "\"This is a turning point for our planet,\" said the UN Secretary-General. \"Future generations will look back at this moment as the day we chose to act.\"",
    "Key provisions include a $100 billion annual fund for climate adaptation, mandatory emissions reporting, and accelerated timelines for phasing out coal power.",
    "Environmental groups have praised the agreement while noting that implementation will be the true test. Industry leaders expressed cautious optimism about the transition timeline."
  ]
};

interface MerkleRoot {
  root_id: string;
  document_id: string;
  root_hash: string;
  tree_depth: number;
  total_leaves: number;
  segmentation_level: string;
  created_at: string;
}

interface EncodeResponse {
  success: boolean;
  message: string;
  document_id: string;
  organization_id: string;
  roots: Record<string, MerkleRoot>;
  total_segments: Record<string, number>;
  processing_time_ms: number;
}

interface SourceMatch {
  document_id: string;
  organization_id: string;
  root_hash: string;
  segmentation_level: string;
  matched_hash: string;
  confidence: number;
}

interface AttributionResponse {
  success: boolean;
  query_hash: string;
  matches_found: number;
  sources: SourceMatch[];
  processing_time_ms: number;
}

export default function MerkleDemoPage() {
  const [activeTab, setActiveTab] = useState<'encode' | 'attribute'>('encode');

  // Encode state
  const [isEncoding, setIsEncoding] = useState(false);
  const [encodeResult, setEncodeResult] = useState<EncodeResponse | null>(null);
  const [encodeError, setEncodeError] = useState<string | null>(null);
  const [showRootDetails, setShowRootDetails] = useState(false);

  // Attribution state
  const [searchText, setSearchText] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [attributionResult, setAttributionResult] = useState<AttributionResponse | null>(null);
  const [attributionError, setAttributionError] = useState<string | null>(null);

  // Copy state
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  const generateDocumentId = () => `merkle-demo-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

  const handleEncode = async () => {
    setIsEncoding(true);
    setEncodeError(null);
    setEncodeResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/enterprise/merkle/encode`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${API_KEY}`,
        },
        body: JSON.stringify({
          document_id: generateDocumentId(),
          text: SAMPLE_ARTICLE.paragraphs.join("\n\n"),
          segmentation_levels: ["sentence", "paragraph"],
          include_words: false,
          metadata: {
            title: SAMPLE_ARTICLE.title,
            source: "Climate Summit Demo",
            encoded_at: new Date().toISOString(),
          }
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail?.message || error.detail || error.message || `API error: ${response.status}`);
      }

      const data = await response.json();
      setEncodeResult(data);
    } catch (err) {
      console.error("Encode error:", err);
      setEncodeError(err instanceof Error ? err.message : "Failed to encode document");
    } finally {
      setIsEncoding(false);
    }
  };

  const handleAttribution = async () => {
    if (!searchText.trim()) return;

    setIsSearching(true);
    setAttributionError(null);
    setAttributionResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/enterprise/merkle/attribute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${API_KEY}`,
        },
        body: JSON.stringify({
          text_segment: searchText,
          segmentation_level: "sentence",
          normalize: true,
          include_proof: false,
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail?.message || error.detail || error.message || `API error: ${response.status}`);
      }

      const data = await response.json();
      setAttributionResult(data);
    } catch (err) {
      console.error("Attribution error:", err);
      setAttributionError(err instanceof Error ? err.message : "Failed to search for source");
    } finally {
      setIsSearching(false);
    }
  };

  const copyToClipboard = async (text: string, id: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedHash(id);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Image
                src="/encypher_full_logo_color.svg"
                alt="Encypher"
                width={140}
                height={40}
                priority
              />
              <div className="border-l border-gray-300 pl-3 ml-1">
                <p className="text-sm font-medium text-delft-blue">Merkle Tree Demo</p>
              </div>
            </div>
            <Link
              href="/"
              className="flex items-center gap-2 text-blue-ncs hover:text-delft-blue text-sm font-medium transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to C2PA Demo
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Intro */}
        <div className="bg-white rounded-2xl p-6 mb-8 border border-gray-200 shadow-sm">
          <h2 className="text-2xl font-bold text-delft-blue mb-3">What is Merkle Tree Encoding?</h2>
          <p className="text-gray-600 mb-4">
            Merkle trees create a cryptographic fingerprint of your content at multiple granularity levels
            (sentence, paragraph, section). This enables:
          </p>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-columbia-blue/20 rounded-lg p-4 border border-columbia-blue/30">
              <Search className="w-6 h-6 text-blue-ncs mb-2" />
              <h3 className="font-semibold text-delft-blue mb-1">Source Attribution</h3>
              <p className="text-gray-600 text-sm">Find the original source of any text segment instantly</p>
            </div>
            <div className="bg-columbia-blue/20 rounded-lg p-4 border border-columbia-blue/30">
              <Shield className="w-6 h-6 text-blue-ncs mb-2" />
              <h3 className="font-semibold text-delft-blue mb-1">Plagiarism Detection</h3>
              <p className="text-gray-600 text-sm">Detect copied content with sentence-level precision</p>
            </div>
            <div className="bg-columbia-blue/20 rounded-lg p-4 border border-columbia-blue/30">
              <Layers className="w-6 h-6 text-blue-ncs mb-2" />
              <h3 className="font-semibold text-delft-blue mb-1">Multi-Level Hashing</h3>
              <p className="text-gray-600 text-sm">Hash at word, sentence, paragraph, or section level</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('encode')}
            className={cn(
              "px-6 py-3 rounded-lg font-medium transition-all",
              activeTab === 'encode'
                ? "bg-blue-ncs text-white"
                : "bg-white text-gray-600 hover:bg-gray-50 border border-gray-200"
            )}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            Encode Document
          </button>
          <button
            onClick={() => setActiveTab('attribute')}
            className={cn(
              "px-6 py-3 rounded-lg font-medium transition-all",
              activeTab === 'attribute'
                ? "bg-blue-ncs text-white"
                : "bg-white text-gray-600 hover:bg-gray-50 border border-gray-200"
            )}
          >
            <Search className="w-4 h-4 inline mr-2" />
            Source Attribution
          </button>
        </div>

        {/* Encode Tab */}
        {activeTab === 'encode' && (
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Source Document */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="bg-columbia-blue/20 px-6 py-4 border-b border-gray-200">
                <h3 className="font-bold text-delft-blue flex items-center gap-2">
                  <FileText className="w-5 h-5 text-blue-ncs" />
                  Source Document
                </h3>
              </div>
              <div className="p-6">
                <h4 className="text-lg font-semibold text-delft-blue mb-4">{SAMPLE_ARTICLE.title}</h4>
                <div className="space-y-3 text-gray-600 text-sm">
                  {SAMPLE_ARTICLE.paragraphs.map((para, idx) => (
                    <p key={idx} className="leading-relaxed">{para}</p>
                  ))}
                </div>
                <button
                  onClick={handleEncode}
                  disabled={isEncoding}
                  className={cn(
                    "mt-6 w-full py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2",
                    isEncoding
                      ? "bg-blue-ncs/50 text-white cursor-not-allowed"
                      : "bg-blue-ncs text-white hover:bg-blue-ncs/90"
                  )}
                >
                  {isEncoding ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Building Merkle Trees...
                    </>
                  ) : (
                    <>
                      <TreeDeciduous className="w-5 h-5" />
                      Encode into Merkle Trees
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Results */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="bg-columbia-blue/20 px-6 py-4 border-b border-gray-200">
                <h3 className="font-bold text-delft-blue flex items-center gap-2">
                  <Hash className="w-5 h-5 text-blue-ncs" />
                  Encoding Results
                </h3>
              </div>
              <div className="p-6">
                {!encodeResult && !encodeError && !isEncoding && (
                  <div className="text-center py-12 text-gray-400">
                    <TreeDeciduous className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Click &quot;Encode&quot; to build Merkle trees</p>
                  </div>
                )}

                {encodeError && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-red-600 mb-2">
                      <AlertTriangle className="w-5 h-5" />
                      <span className="font-semibold">Encoding Failed</span>
                    </div>
                    <p className="text-red-500 text-sm">{encodeError}</p>
                  </div>
                )}

                {encodeResult && (
                  <div className="space-y-4">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex items-center gap-2 text-green-600">
                        <CheckCircle2 className="w-5 h-5" />
                        <span className="font-semibold">Document Encoded Successfully</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <div className="text-gray-500 text-sm mb-1">Document ID</div>
                        <div className="text-delft-blue font-mono text-xs truncate">{encodeResult.document_id}</div>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <div className="text-gray-500 text-sm mb-1 flex items-center gap-1">
                          <Clock className="w-3 h-3" /> Processing Time
                        </div>
                        <div className="text-delft-blue font-semibold">{encodeResult.processing_time_ms.toFixed(1)} ms</div>
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div className="text-gray-500 text-sm mb-3">Segments Created</div>
                      <div className="flex gap-4">
                        {Object.entries(encodeResult.total_segments).map(([level, count]) => (
                          <div key={level} className="bg-columbia-blue/30 rounded-lg px-4 py-2">
                            <div className="text-delft-blue font-semibold">{count}</div>
                            <div className="text-gray-600 text-xs capitalize">{level}s</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Merkle Roots Dropdown */}
                    <div className="bg-gray-50 rounded-lg overflow-hidden border border-gray-200">
                      <button
                        onClick={() => setShowRootDetails(!showRootDetails)}
                        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-100 transition-colors"
                      >
                        <span className="text-delft-blue font-medium">Merkle Root Hashes</span>
                        {showRootDetails ? (
                          <ChevronUp className="w-4 h-4 text-blue-ncs" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-blue-ncs" />
                        )}
                      </button>
                      {showRootDetails && (
                        <div className="px-4 pb-4 space-y-3">
                          {Object.entries(encodeResult.roots).map(([level, root]) => (
                            <div key={level} className="bg-delft-blue rounded-lg p-3">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-columbia-blue text-sm capitalize font-medium">{level} Level</span>
                                <span className="text-gray-400 text-xs">Depth: {root.tree_depth} | Leaves: {root.total_leaves}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <code className="text-cyber-teal text-xs font-mono flex-1 truncate">{root.root_hash}</code>
                                <button
                                  onClick={() => copyToClipboard(root.root_hash, root.root_id)}
                                  className="text-columbia-blue hover:text-white transition-colors"
                                >
                                  {copiedHash === root.root_id ? (
                                    <Check className="w-4 h-4 text-green-400" />
                                  ) : (
                                    <Copy className="w-4 h-4" />
                                  )}
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Attribution Tab */}
        {activeTab === 'attribute' && (
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Search Input */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="bg-columbia-blue/20 px-6 py-4 border-b border-gray-200">
                <h3 className="font-bold text-delft-blue flex items-center gap-2">
                  <Search className="w-5 h-5 text-blue-ncs" />
                  Find Source
                </h3>
              </div>
              <div className="p-6">
                <p className="text-gray-600 text-sm mb-4">
                  Enter a sentence to find its original source document. Try copying a sentence from the encoded document above.
                </p>
                <textarea
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  placeholder="Paste a sentence to find its source..."
                  className="w-full h-32 bg-gray-50 border border-gray-200 rounded-lg p-4 text-delft-blue placeholder-gray-400 focus:outline-none focus:border-blue-ncs focus:ring-1 focus:ring-blue-ncs resize-none"
                />
                <div className="mt-4 space-y-2">
                  <p className="text-gray-500 text-xs">Try one of these sentences:</p>
                  {SAMPLE_ARTICLE.paragraphs.slice(0, 2).map((para, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSearchText(para)}
                      className="block w-full text-left text-xs text-gray-600 hover:text-delft-blue bg-gray-50 hover:bg-columbia-blue/20 rounded p-2 truncate transition-colors border border-gray-200"
                    >
                      &quot;{para}&quot;
                    </button>
                  ))}
                </div>
                <button
                  onClick={handleAttribution}
                  disabled={isSearching || !searchText.trim()}
                  className={cn(
                    "mt-6 w-full py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2",
                    isSearching || !searchText.trim()
                      ? "bg-blue-ncs/50 text-white cursor-not-allowed"
                      : "bg-blue-ncs text-white hover:bg-blue-ncs/90"
                  )}
                >
                  {isSearching ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="w-5 h-5" />
                      Find Source
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Attribution Results */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="bg-columbia-blue/20 px-6 py-4 border-b border-gray-200">
                <h3 className="font-bold text-delft-blue flex items-center gap-2">
                  <Shield className="w-5 h-5 text-blue-ncs" />
                  Attribution Results
                </h3>
              </div>
              <div className="p-6">
                {!attributionResult && !attributionError && !isSearching && (
                  <div className="text-center py-12 text-gray-400">
                    <Search className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Enter text to search for its source</p>
                  </div>
                )}

                {attributionError && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-red-600 mb-2">
                      <AlertTriangle className="w-5 h-5" />
                      <span className="font-semibold">Search Failed</span>
                    </div>
                    <p className="text-red-500 text-sm">{attributionError}</p>
                  </div>
                )}

                {attributionResult && (
                  <div className="space-y-4">
                    <div className={cn(
                      "rounded-lg p-4 border",
                      attributionResult.matches_found > 0
                        ? "bg-green-50 border-green-200"
                        : "bg-yellow-50 border-yellow-200"
                    )}>
                      <div className={cn(
                        "flex items-center gap-2",
                        attributionResult.matches_found > 0 ? "text-green-600" : "text-yellow-600"
                      )}>
                        {attributionResult.matches_found > 0 ? (
                          <CheckCircle2 className="w-5 h-5" />
                        ) : (
                          <AlertTriangle className="w-5 h-5" />
                        )}
                        <span className="font-semibold">
                          {attributionResult.matches_found > 0
                            ? `Found ${attributionResult.matches_found} source(s)`
                            : "No sources found"}
                        </span>
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div className="text-gray-500 text-sm mb-2">Query Hash</div>
                      <code className="text-blue-ncs text-xs font-mono break-all">{attributionResult.query_hash}</code>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div className="text-gray-500 text-sm mb-1 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> Processing Time
                      </div>
                      <div className="text-delft-blue font-semibold">{attributionResult.processing_time_ms.toFixed(1)} ms</div>
                    </div>

                    {attributionResult.sources.length > 0 && (
                      <div className="space-y-3">
                        <div className="text-delft-blue font-medium">Matching Sources:</div>
                        {attributionResult.sources.map((source, idx) => (
                          <div key={idx} className="bg-delft-blue rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-white font-medium">Document: {source.document_id}</span>
                              <span className="text-green-400 text-sm">{(source.confidence * 100).toFixed(0)}% match</span>
                            </div>
                            <div className="text-columbia-blue text-xs">
                              Organization: {source.organization_id}
                            </div>
                            <div className="text-columbia-blue text-xs mt-1">
                              Level: {source.segmentation_level}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Footer Note */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>
            Merkle tree encoding is an <strong className="text-delft-blue">Enterprise feature</strong>.
            Contact us to enable it for your organization.
          </p>
        </div>
      </main>
    </div>
  );
}
