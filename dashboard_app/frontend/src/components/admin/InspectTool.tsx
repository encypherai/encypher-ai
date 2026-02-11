'use client';

import React, { useState, useCallback, useRef } from 'react';
import {
  detectMarkers,
  segmentText,
  summarizeMarkers,
  type DetectedMarker,
  type TextSegment,
  type MarkerSummary,
} from '@/lib/marker-detector';

// ---------------------------------------------------------------------------
// Marker Icon (inline SVG — Encypher shield)
// ---------------------------------------------------------------------------

function EncypherIcon({ status }: { status: 'detected' | 'verified' | 'failed' | 'tampered' }) {
  const colors = {
    detected: { fill: '#6366f1', ring: '#818cf8' },   // indigo — not yet verified
    verified: { fill: '#22c55e', ring: '#4ade80' },    // green — signature valid
    failed: { fill: '#ef4444', ring: '#f87171' },      // red — verification failed
    tampered: { fill: '#f59e0b', ring: '#fbbf24' },    // amber — content modified
  };
  const c = colors[status];

  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="inline-block mx-0.5 cursor-pointer align-text-bottom"
    >
      <path
        d="M8 1L2 4v4c0 3.5 2.5 6.4 6 7 3.5-.6 6-3.5 6-7V4L8 1z"
        fill={c.fill}
        stroke={c.ring}
        strokeWidth="0.8"
      />
      <text
        x="8"
        y="10.5"
        textAnchor="middle"
        fill="white"
        fontSize="7"
        fontWeight="bold"
        fontFamily="system-ui"
      >
        E
      </text>
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Marker Popover
// ---------------------------------------------------------------------------

interface MarkerPopoverProps {
  marker: DetectedMarker;
  verificationResult?: VerificationDetail | null;
  onClose: () => void;
  position: { top: number; left: number };
}

interface VerificationDetail {
  valid: boolean;
  tampered: boolean;
  signerIdentity?: {
    organization_id?: string;
    organization_name?: string;
    trust_level?: string;
    ca_backed?: boolean;
  } | null;
  leafHash?: string;
  computedHash?: string;
  contentHashValid?: boolean;
  error?: string;
}

function MarkerPopover({ marker, verificationResult, onClose, position }: MarkerPopoverProps) {
  const typeLabels: Record<string, string> = {
    micro: 'Micro (36-char, 128-bit HMAC)',
    micro_ecc: 'Micro ECC (44-char, 128-bit HMAC + Reed-Solomon)',
    basic: 'Basic Format (JSON payload)',
    c2pa: 'C2PA Manifest (COSE_Sign1)',
    unknown: 'Unknown Format',
  };

  const getStatusBadge = () => {
    if (!verificationResult) {
      return <span className="badge badge-info">Detected — Not Verified</span>;
    }
    if (verificationResult.tampered) {
      return <span className="badge badge-warning">Content Modified</span>;
    }
    if (verificationResult.valid) {
      return <span className="badge badge-success">Verified</span>;
    }
    return <span className="badge badge-danger">Verification Failed</span>;
  };

  return (
    <div
      className="fixed z-50 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 p-4 w-96 max-h-96 overflow-y-auto animate-fadeIn"
      style={{ top: position.top, left: position.left }}
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
          Embedding #{marker.index + 1}
        </h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="space-y-2 text-xs">
        <div className="flex items-center gap-2">
          <span className="text-gray-500 dark:text-gray-400 font-medium w-16">Status</span>
          {getStatusBadge()}
        </div>

        <div className="flex items-start gap-2">
          <span className="text-gray-500 dark:text-gray-400 font-medium w-16 shrink-0">Type</span>
          <span className="text-gray-900 dark:text-white">{typeLabels[marker.type] || marker.type}</span>
        </div>

        <div className="flex items-start gap-2">
          <span className="text-gray-500 dark:text-gray-400 font-medium w-16 shrink-0">Size</span>
          <span className="text-gray-900 dark:text-white">{marker.charCount} invisible chars</span>
        </div>

        {marker.uuid && (
          <div className="flex items-start gap-2">
            <span className="text-gray-500 dark:text-gray-400 font-medium w-16 shrink-0">UUID</span>
            <code className="text-[10px] bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded font-mono break-all">
              {marker.uuid}
            </code>
          </div>
        )}

        {marker.hmac && (
          <div className="flex items-start gap-2">
            <span className="text-gray-500 dark:text-gray-400 font-medium w-16 shrink-0">HMAC</span>
            <code className="text-[10px] bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded font-mono break-all">
              {marker.hmac}
            </code>
          </div>
        )}

        {marker.rsParity && (
          <div className="flex items-start gap-2">
            <span className="text-gray-500 dark:text-gray-400 font-medium w-16 shrink-0">RS ECC</span>
            <code className="text-[10px] bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded font-mono break-all">
              {marker.rsParity}
            </code>
          </div>
        )}

        {verificationResult?.signerIdentity && (
          <>
            <hr className="border-gray-200 dark:border-gray-700 my-2" />
            <div className="flex items-start gap-2">
              <span className="text-gray-500 dark:text-gray-400 font-medium w-16 shrink-0">Signer</span>
              <span className="text-gray-900 dark:text-white">
                {verificationResult.signerIdentity.organization_name || verificationResult.signerIdentity.organization_id}
              </span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-gray-500 dark:text-gray-400 font-medium w-16 shrink-0">Trust</span>
              <span className={`text-xs font-medium ${
                verificationResult.signerIdentity.trust_level === 'ca_verified'
                  ? 'text-green-600 dark:text-green-400'
                  : verificationResult.signerIdentity.trust_level === 'self_signed'
                  ? 'text-blue-600 dark:text-blue-400'
                  : 'text-gray-500'
              }`}>
                {verificationResult.signerIdentity.trust_level === 'ca_verified'
                  ? 'CA Verified'
                  : verificationResult.signerIdentity.trust_level === 'self_signed'
                  ? 'Self-Signed (Encypher-managed)'
                  : 'No Certificate'}
              </span>
            </div>
          </>
        )}

        {verificationResult?.contentHashValid === false && (
          <>
            <hr className="border-gray-200 dark:border-gray-700 my-2" />
            <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded p-2">
              <p className="text-amber-800 dark:text-amber-200 text-[10px] font-medium">
                Content has been modified since signing.
              </p>
              {verificationResult.leafHash && (
                <p className="text-amber-600 dark:text-amber-400 text-[10px] mt-1">
                  Expected: {verificationResult.leafHash.slice(0, 16)}...
                </p>
              )}
              {verificationResult.computedHash && (
                <p className="text-amber-600 dark:text-amber-400 text-[10px]">
                  Computed: {verificationResult.computedHash.slice(0, 16)}...
                </p>
              )}
            </div>
          </>
        )}

        {verificationResult?.error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded p-2">
            <p className="text-red-600 dark:text-red-400 text-[10px]">{verificationResult.error}</p>
          </div>
        )}

        <div className="flex items-start gap-2">
          <span className="text-gray-500 dark:text-gray-400 font-medium w-16 shrink-0">Position</span>
          <span className="text-gray-900 dark:text-white">
            chars {marker.startIndex}–{marker.endIndex}
          </span>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Summary Bar
// ---------------------------------------------------------------------------

function SummaryBar({ summary, verified }: { summary: MarkerSummary; verified: boolean }) {
  return (
    <div className="flex flex-wrap gap-3 text-xs">
      <div className="flex items-center gap-1.5">
        <div className="w-2 h-2 rounded-full bg-indigo-500" />
        <span className="text-gray-600 dark:text-gray-400">
          <strong className="text-gray-900 dark:text-white">{summary.total}</strong> embeddings found
        </span>
      </div>
      {summary.micro > 0 && (
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-blue-500" />
          <span className="text-gray-600 dark:text-gray-400">{summary.micro} micro</span>
        </div>
      )}
      {summary.microEcc > 0 && (
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-cyan-500" />
          <span className="text-gray-600 dark:text-gray-400">{summary.microEcc} micro_ecc</span>
        </div>
      )}
      {summary.basic > 0 && (
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-purple-500" />
          <span className="text-gray-600 dark:text-gray-400">{summary.basic} basic</span>
        </div>
      )}
      {summary.c2pa > 0 && (
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-gray-600 dark:text-gray-400">{summary.c2pa} C2PA</span>
        </div>
      )}
      {verified && (
        <div className="flex items-center gap-1.5 ml-auto">
          <svg className="w-3.5 h-3.5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span className="text-green-600 dark:text-green-400 font-medium">Server-verified</span>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main InspectTool Component
// ---------------------------------------------------------------------------

export default function InspectTool() {
  const [inputText, setInputText] = useState('');
  const [segments, setSegments] = useState<TextSegment[]>([]);
  const [markers, setMarkers] = useState<DetectedMarker[]>([]);
  const [summary, setSummary] = useState<MarkerSummary | null>(null);
  const [activePopover, setActivePopover] = useState<{
    marker: DetectedMarker;
    position: { top: number; left: number };
  } | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationResults, setVerificationResults] = useState<Map<number, VerificationDetail>>(new Map());
  const [hasVerified, setHasVerified] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  const handleInspect = useCallback(() => {
    if (!inputText.trim()) return;

    const detected = detectMarkers(inputText);
    const segs = segmentText(inputText);
    const sum = summarizeMarkers(detected);

    setMarkers(detected);
    setSegments(segs);
    setSummary(sum);
    setActivePopover(null);
    setVerificationResults(new Map());
    setHasVerified(false);
  }, [inputText]);

  const handleVerify = useCallback(async () => {
    if (!inputText.trim() || markers.length === 0) return;

    setIsVerifying(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/verify/advanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          text: inputText,
          include_attribution: false,
          detect_plagiarism: false,
          segmentation_level: 'sentence',
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const results = new Map<number, VerificationDetail>();

        // Map verification results back to detected markers
        const verdict = data.data || {};
        const tamperDetection = data.tamper_detection || {};
        const tamperLocalization = data.tamper_localization || {};

        // For each marker, create a verification detail
        for (const marker of markers) {
          const detail: VerificationDetail = {
            valid: verdict.signature_valid || false,
            tampered: false,
            signerIdentity: verdict.signer_identity || null,
          };

          // Check tamper localization for this marker's sentence
          if (tamperDetection.root_match === false && tamperLocalization.events) {
            const events = tamperLocalization.events as Array<{
              type: string;
              stored_range: number[];
              request_range: number[];
            }>;
            for (const event of events) {
              if (
                marker.index >= event.request_range[0] &&
                marker.index < event.request_range[1]
              ) {
                detail.tampered = true;
                detail.contentHashValid = false;
                break;
              }
            }
          }

          if (tamperDetection.root_match === true) {
            detail.contentHashValid = true;
          }

          results.set(marker.index, detail);
        }

        setVerificationResults(results);
        setHasVerified(true);
      }
    } catch (err) {
      console.error('Verification failed:', err);
    } finally {
      setIsVerifying(false);
    }
  }, [inputText, markers]);

  const handleMarkerClick = (marker: DetectedMarker, event: React.MouseEvent) => {
    const rect = (event.target as HTMLElement).getBoundingClientRect();
    setActivePopover({
      marker,
      position: {
        top: rect.bottom + 8,
        left: Math.min(rect.left, window.innerWidth - 400),
      },
    });
  };

  const getMarkerStatus = (marker: DetectedMarker): 'detected' | 'verified' | 'failed' | 'tampered' => {
    const result = verificationResults.get(marker.index);
    if (!result) return 'detected';
    if (result.tampered) return 'tampered';
    if (result.valid) return 'verified';
    return 'failed';
  };

  const handleClear = () => {
    setInputText('');
    setSegments([]);
    setMarkers([]);
    setSummary(null);
    setActivePopover(null);
    setVerificationResults(new Map());
    setHasVerified(false);
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setInputText(text);
    } catch {
      // Clipboard API not available — user can paste manually
    }
  };

  return (
    <div className="space-y-6">
      {/* Input Area */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Content Inspector
          </h2>
          <div className="flex gap-2">
            <button onClick={handlePaste} className="btn-secondary text-xs px-3 py-1.5 rounded-md">
              Paste from Clipboard
            </button>
            {inputText && (
              <button onClick={handleClear} className="text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 px-2">
                Clear
              </button>
            )}
          </div>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
          Paste signed content below to inspect embedded Encypher markers. Invisible signatures will be detected and displayed as shield icons.
        </p>
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste content with Encypher embeddings here..."
          className="input-field w-full h-40 resize-y font-mono text-sm"
          data-testid="inspect-input"
        />
        <div className="flex gap-3 mt-3">
          <button
            onClick={handleInspect}
            disabled={!inputText.trim()}
            className="btn-primary text-sm px-4 py-2 rounded-md disabled:opacity-50"
            data-testid="inspect-button"
          >
            Inspect Markers
          </button>
          {markers.length > 0 && (
            <button
              onClick={handleVerify}
              disabled={isVerifying}
              className="bg-green-600 text-white hover:bg-green-700 text-sm px-4 py-2 rounded-md disabled:opacity-50 flex items-center gap-2"
              data-testid="verify-button"
            >
              {isVerifying && (
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              )}
              {isVerifying ? 'Verifying...' : 'Verify All'}
            </button>
          )}
        </div>
      </div>

      {/* Results */}
      {summary && summary.total > 0 && (
        <div className="card" data-testid="inspect-results">
          <div className="mb-4">
            <SummaryBar summary={summary} verified={hasVerified} />
          </div>

          <hr className="border-gray-200 dark:border-gray-700 mb-4" />

          {/* Formatted text with marker icons */}
          <div
            ref={contentRef}
            className="prose prose-sm dark:prose-invert max-w-none leading-relaxed"
            data-testid="formatted-content"
          >
            {segments.map((seg, i) => {
              if (seg.type === 'text') {
                // Check if this text segment has a verified marker after it
                const nextSeg = segments[i + 1];
                const hasMarkerAfter = nextSeg?.type === 'marker';
                const markerResult = hasMarkerAfter && nextSeg.marker
                  ? verificationResults.get(nextSeg.marker.index)
                  : null;

                // Highlight background based on verification status
                let bgClass = '';
                if (hasMarkerAfter && hasVerified && markerResult) {
                  if (markerResult.tampered) {
                    bgClass = 'bg-amber-50 dark:bg-amber-900/10 rounded px-1';
                  } else if (markerResult.valid) {
                    bgClass = 'bg-green-50 dark:bg-green-900/10 rounded px-1';
                  } else {
                    bgClass = 'bg-red-50 dark:bg-red-900/10 rounded px-1';
                  }
                } else if (hasMarkerAfter && !hasVerified) {
                  bgClass = 'bg-indigo-50 dark:bg-indigo-900/10 rounded px-1';
                }

                return (
                  <span key={i} className={bgClass}>
                    {seg.content}
                  </span>
                );
              }

              // Marker icon
              if (seg.marker) {
                const status = getMarkerStatus(seg.marker);
                return (
                  <span
                    key={i}
                    onClick={(e) => handleMarkerClick(seg.marker!, e)}
                    title={`Embedding #${seg.marker.index + 1} (${seg.marker.type})`}
                    data-testid={`marker-icon-${seg.marker.index}`}
                  >
                    <EncypherIcon status={status} />
                  </span>
                );
              }

              return null;
            })}
          </div>
        </div>
      )}

      {/* No markers found */}
      {summary && summary.total === 0 && (
        <div className="card" data-testid="no-markers">
          <div className="text-center py-8">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No Embeddings Found</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              The pasted content does not contain any detectable Encypher markers.
            </p>
          </div>
        </div>
      )}

      {/* Popover */}
      {activePopover && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setActivePopover(null)}
          />
          <MarkerPopover
            marker={activePopover.marker}
            verificationResult={verificationResults.get(activePopover.marker.index) || null}
            onClose={() => setActivePopover(null)}
            position={activePopover.position}
          />
        </>
      )}
    </div>
  );
}
