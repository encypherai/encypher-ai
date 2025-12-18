"use client";

import { useState } from "react";
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
  Check
} from "lucide-react";
import { cn } from "@/lib/utils";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.encypherai.com';
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-2 rounded-lg">
                <TreeDeciduous className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Merkle Tree Demo</h1>
                <p className="text-purple-300 text-sm">Enterprise Content Attribution</p>
              </div>
            </div>
            <a 
              href="/"
              className="text-purple-300 hover:text-white text-sm transition-colors"
            >
              ← Back to C2PA Demo
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Intro */}
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 mb-8 border border-white/10">
          <h2 className="text-2xl font-bold text-white mb-3">What is Merkle Tree Encoding?</h2>
          <p className="text-purple-200 mb-4">
            Merkle trees create a cryptographic fingerprint of your content at multiple granularity levels 
            (sentence, paragraph, section). This enables:
          </p>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <Search className="w-6 h-6 text-purple-400 mb-2" />
              <h3 className="font-semibold text-white mb-1">Source Attribution</h3>
              <p className="text-purple-300 text-sm">Find the original source of any text segment instantly</p>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <Shield className="w-6 h-6 text-purple-400 mb-2" />
              <h3 className="font-semibold text-white mb-1">Plagiarism Detection</h3>
              <p className="text-purple-300 text-sm">Detect copied content with sentence-level precision</p>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <Layers className="w-6 h-6 text-purple-400 mb-2" />
              <h3 className="font-semibold text-white mb-1">Multi-Level Hashing</h3>
              <p className="text-purple-300 text-sm">Hash at word, sentence, paragraph, or section level</p>
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
                ? "bg-purple-500 text-white"
                : "bg-white/10 text-purple-300 hover:bg-white/20"
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
                ? "bg-purple-500 text-white"
                : "bg-white/10 text-purple-300 hover:bg-white/20"
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
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 overflow-hidden">
              <div className="bg-white/5 px-6 py-4 border-b border-white/10">
                <h3 className="font-bold text-white flex items-center gap-2">
                  <FileText className="w-5 h-5 text-purple-400" />
                  Source Document
                </h3>
              </div>
              <div className="p-6">
                <h4 className="text-lg font-semibold text-white mb-4">{SAMPLE_ARTICLE.title}</h4>
                <div className="space-y-3 text-purple-200 text-sm">
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
                      ? "bg-purple-500/50 text-purple-200 cursor-not-allowed"
                      : "bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600"
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
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 overflow-hidden">
              <div className="bg-white/5 px-6 py-4 border-b border-white/10">
                <h3 className="font-bold text-white flex items-center gap-2">
                  <Hash className="w-5 h-5 text-purple-400" />
                  Encoding Results
                </h3>
              </div>
              <div className="p-6">
                {!encodeResult && !encodeError && !isEncoding && (
                  <div className="text-center py-12 text-purple-400">
                    <TreeDeciduous className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Click &quot;Encode&quot; to build Merkle trees</p>
                  </div>
                )}

                {encodeError && (
                  <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-red-400 mb-2">
                      <AlertTriangle className="w-5 h-5" />
                      <span className="font-semibold">Encoding Failed</span>
                    </div>
                    <p className="text-red-300 text-sm">{encodeError}</p>
                  </div>
                )}

                {encodeResult && (
                  <div className="space-y-4">
                    <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-4">
                      <div className="flex items-center gap-2 text-green-400">
                        <CheckCircle2 className="w-5 h-5" />
                        <span className="font-semibold">Document Encoded Successfully</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-white/5 rounded-lg p-4">
                        <div className="text-purple-400 text-sm mb-1">Document ID</div>
                        <div className="text-white font-mono text-xs truncate">{encodeResult.document_id}</div>
                      </div>
                      <div className="bg-white/5 rounded-lg p-4">
                        <div className="text-purple-400 text-sm mb-1 flex items-center gap-1">
                          <Clock className="w-3 h-3" /> Processing Time
                        </div>
                        <div className="text-white font-semibold">{encodeResult.processing_time_ms.toFixed(1)} ms</div>
                      </div>
                    </div>

                    <div className="bg-white/5 rounded-lg p-4">
                      <div className="text-purple-400 text-sm mb-3">Segments Created</div>
                      <div className="flex gap-4">
                        {Object.entries(encodeResult.total_segments).map(([level, count]) => (
                          <div key={level} className="bg-purple-500/20 rounded-lg px-4 py-2">
                            <div className="text-white font-semibold">{count}</div>
                            <div className="text-purple-300 text-xs capitalize">{level}s</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Merkle Roots Dropdown */}
                    <div className="bg-white/5 rounded-lg overflow-hidden">
                      <button
                        onClick={() => setShowRootDetails(!showRootDetails)}
                        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
                      >
                        <span className="text-purple-300 font-medium">Merkle Root Hashes</span>
                        {showRootDetails ? (
                          <ChevronUp className="w-4 h-4 text-purple-400" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-purple-400" />
                        )}
                      </button>
                      {showRootDetails && (
                        <div className="px-4 pb-4 space-y-3">
                          {Object.entries(encodeResult.roots).map(([level, root]) => (
                            <div key={level} className="bg-black/30 rounded-lg p-3">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-purple-300 text-sm capitalize font-medium">{level} Level</span>
                                <span className="text-purple-400 text-xs">Depth: {root.tree_depth} | Leaves: {root.total_leaves}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <code className="text-green-400 text-xs font-mono flex-1 truncate">{root.root_hash}</code>
                                <button
                                  onClick={() => copyToClipboard(root.root_hash, root.root_id)}
                                  className="text-purple-400 hover:text-white transition-colors"
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
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 overflow-hidden">
              <div className="bg-white/5 px-6 py-4 border-b border-white/10">
                <h3 className="font-bold text-white flex items-center gap-2">
                  <Search className="w-5 h-5 text-purple-400" />
                  Find Source
                </h3>
              </div>
              <div className="p-6">
                <p className="text-purple-300 text-sm mb-4">
                  Enter a sentence to find its original source document. Try copying a sentence from the encoded document above.
                </p>
                <textarea
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  placeholder="Paste a sentence to find its source..."
                  className="w-full h-32 bg-black/30 border border-white/20 rounded-lg p-4 text-white placeholder-purple-400/50 focus:outline-none focus:border-purple-500 resize-none"
                />
                <div className="mt-4 space-y-2">
                  <p className="text-purple-400 text-xs">Try one of these sentences:</p>
                  {SAMPLE_ARTICLE.paragraphs.slice(0, 2).map((para, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSearchText(para)}
                      className="block w-full text-left text-xs text-purple-300 hover:text-white bg-white/5 rounded p-2 truncate transition-colors"
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
                      ? "bg-purple-500/50 text-purple-200 cursor-not-allowed"
                      : "bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600"
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
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 overflow-hidden">
              <div className="bg-white/5 px-6 py-4 border-b border-white/10">
                <h3 className="font-bold text-white flex items-center gap-2">
                  <Shield className="w-5 h-5 text-purple-400" />
                  Attribution Results
                </h3>
              </div>
              <div className="p-6">
                {!attributionResult && !attributionError && !isSearching && (
                  <div className="text-center py-12 text-purple-400">
                    <Search className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Enter text to search for its source</p>
                  </div>
                )}

                {attributionError && (
                  <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-red-400 mb-2">
                      <AlertTriangle className="w-5 h-5" />
                      <span className="font-semibold">Search Failed</span>
                    </div>
                    <p className="text-red-300 text-sm">{attributionError}</p>
                  </div>
                )}

                {attributionResult && (
                  <div className="space-y-4">
                    <div className={cn(
                      "rounded-lg p-4 border",
                      attributionResult.matches_found > 0
                        ? "bg-green-500/20 border-green-500/50"
                        : "bg-yellow-500/20 border-yellow-500/50"
                    )}>
                      <div className={cn(
                        "flex items-center gap-2",
                        attributionResult.matches_found > 0 ? "text-green-400" : "text-yellow-400"
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

                    <div className="bg-white/5 rounded-lg p-4">
                      <div className="text-purple-400 text-sm mb-2">Query Hash</div>
                      <code className="text-green-400 text-xs font-mono break-all">{attributionResult.query_hash}</code>
                    </div>

                    <div className="bg-white/5 rounded-lg p-4">
                      <div className="text-purple-400 text-sm mb-1 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> Processing Time
                      </div>
                      <div className="text-white font-semibold">{attributionResult.processing_time_ms.toFixed(1)} ms</div>
                    </div>

                    {attributionResult.sources.length > 0 && (
                      <div className="space-y-3">
                        <div className="text-purple-300 font-medium">Matching Sources:</div>
                        {attributionResult.sources.map((source, idx) => (
                          <div key={idx} className="bg-black/30 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-white font-medium">Document: {source.document_id}</span>
                              <span className="text-green-400 text-sm">{(source.confidence * 100).toFixed(0)}% match</span>
                            </div>
                            <div className="text-purple-400 text-xs">
                              Organization: {source.organization_id}
                            </div>
                            <div className="text-purple-400 text-xs mt-1">
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
        <div className="mt-8 text-center text-purple-400 text-sm">
          <p>
            Merkle tree encoding is an <strong className="text-purple-300">Enterprise feature</strong>. 
            Contact us to enable it for your organization.
          </p>
        </div>
      </main>
    </div>
  );
}
