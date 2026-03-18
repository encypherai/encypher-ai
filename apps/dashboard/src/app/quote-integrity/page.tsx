'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Badge,
  Input,
} from '@encypher/design-system';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import apiClient, { type QuoteIntegrityResponse, type QuoteVerdict, type QuoteConfidence } from '../../lib/api';

type Verdict = QuoteVerdict;
type Confidence = QuoteConfidence;
type QuoteIntegrityResult = QuoteIntegrityResponse;

const VERDICT_STYLES: Record<Verdict, { label: string; className: string }> = {
  accurate: { label: 'Accurate', className: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' },
  approximate: { label: 'Approximate', className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' },
  hallucinated: { label: 'Hallucinated', className: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' },
  unverifiable: { label: 'Unverifiable', className: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300' },
};

export default function QuoteIntegrityPage() {
  const [quote, setQuote] = useState('');
  const [attribution, setAttribution] = useState('');
  const [orgId, setOrgId] = useState('');
  const [docId, setDocId] = useState('');
  const [fuzzyThreshold, setFuzzyThreshold] = useState(0.85);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [merkleOpen, setMerkleOpen] = useState(false);

  const mutation = useMutation<QuoteIntegrityResult, Error, void>({
    mutationFn: async () => {
      const params: Parameters<typeof apiClient.verifyQuoteIntegrity>[0] = {
        quote,
        attribution,
      };
      if (orgId.trim()) params.org_id = orgId.trim();
      if (docId.trim()) params.doc_id = docId.trim();
      if (fuzzyThreshold !== 0.85) params.fuzzy_threshold = fuzzyThreshold;
      return apiClient.verifyQuoteIntegrity(params);
    },
    onError: (err) => {
      toast.error(err.message || 'Quote integrity check failed');
    },
  });

  const result = mutation.data ?? null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!quote.trim() || !attribution.trim()) {
      toast.error('Both quote and attribution are required');
      return;
    }
    mutation.mutate();
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Quote Integrity</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Verify whether a quoted passage matches a signed document.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left column - Form */}
          <Card>
            <CardHeader>
              <CardTitle>Check a Quote</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label
                    htmlFor="qi-quote"
                    className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
                  >
                    Quote
                  </label>
                  <textarea
                    id="qi-quote"
                    data-testid="qi-quote"
                    className="w-full rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[120px] resize-y"
                    placeholder="Paste the quoted text here..."
                    value={quote}
                    onChange={(e) => setQuote(e.target.value)}
                  />
                </div>

                <div>
                  <label
                    htmlFor="qi-attribution"
                    className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
                  >
                    Attribution
                  </label>
                  <Input
                    id="qi-attribution"
                    data-testid="qi-attribution"
                    placeholder="e.g., According to Reuters..."
                    value={attribution}
                    onChange={(e) => setAttribution(e.target.value)}
                  />
                </div>

                {/* Advanced Options */}
                <div className="border border-slate-200 dark:border-slate-700 rounded-md">
                  <button
                    type="button"
                    className="w-full flex items-center justify-between px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-md"
                    onClick={() => setAdvancedOpen(!advancedOpen)}
                    data-testid="qi-advanced-toggle"
                  >
                    <span>Advanced Options</span>
                    <svg
                      className={`w-4 h-4 transition-transform ${advancedOpen ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {advancedOpen && (
                    <div className="px-3 pb-3 space-y-3 border-t border-slate-200 dark:border-slate-700 pt-3">
                      <div>
                        <label
                          htmlFor="qi-org-id"
                          className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1"
                        >
                          Organization ID
                        </label>
                        <Input
                          id="qi-org-id"
                          data-testid="qi-org-id"
                          placeholder="Optional org ID"
                          value={orgId}
                          onChange={(e) => setOrgId(e.target.value)}
                        />
                      </div>
                      <div>
                        <label
                          htmlFor="qi-doc-id"
                          className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1"
                        >
                          Document ID
                        </label>
                        <Input
                          id="qi-doc-id"
                          data-testid="qi-doc-id"
                          placeholder="Optional document ID"
                          value={docId}
                          onChange={(e) => setDocId(e.target.value)}
                        />
                      </div>
                      <div>
                        <label
                          htmlFor="qi-threshold"
                          className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1"
                        >
                          Fuzzy Threshold: {fuzzyThreshold.toFixed(2)}
                        </label>
                        <input
                          id="qi-threshold"
                          data-testid="qi-threshold"
                          type="range"
                          min="0"
                          max="1"
                          step="0.01"
                          value={fuzzyThreshold}
                          onChange={(e) => setFuzzyThreshold(parseFloat(e.target.value))}
                          className="w-full accent-blue-600"
                        />
                        <div className="flex justify-between text-xs text-slate-400 mt-0.5">
                          <span>0.0</span>
                          <span>1.0</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <Button
                  type="submit"
                  disabled={mutation.isPending}
                  className="w-full"
                  data-testid="qi-submit"
                >
                  {mutation.isPending ? 'Verifying...' : 'Verify Quote'}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Right column - Results */}
          <Card>
            <CardHeader>
              <CardTitle>Result</CardTitle>
            </CardHeader>
            <CardContent>
              {!result && !mutation.isPending && (
                <p className="text-sm text-slate-500 dark:text-slate-400" data-testid="qi-placeholder">
                  Enter a quote and click Verify to check its integrity
                </p>
              )}

              {mutation.isPending && (
                <div className="flex items-center justify-center py-8">
                  <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate-300 border-t-blue-600" />
                </div>
              )}

              {result && !mutation.isPending && (
                <div className="space-y-4" data-testid="qi-result">
                  {/* Verdict badge */}
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Verdict:</span>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${VERDICT_STYLES[result.verdict].className}`}
                      data-testid="qi-verdict"
                    >
                      {VERDICT_STYLES[result.verdict].label}
                    </span>
                  </div>

                  {/* Similarity score */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                        Similarity Score
                      </span>
                      <span className="text-sm text-slate-600 dark:text-slate-400" data-testid="qi-score">
                        {Math.round(result.similarity_score * 100)}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${Math.round(result.similarity_score * 100)}%` }}
                      />
                    </div>
                  </div>

                  {/* Confidence */}
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Confidence:</span>
                    <Badge variant="outline" data-testid="qi-confidence">
                      {result.confidence}
                    </Badge>
                  </div>

                  {/* Matched excerpt */}
                  {result.matched_excerpt && (
                    <div>
                      <span className="text-sm font-medium text-slate-700 dark:text-slate-300 block mb-1">
                        Matched Excerpt
                      </span>
                      <blockquote
                        className="border-l-4 border-blue-500 pl-3 py-2 text-sm text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-800 rounded-r-md italic"
                        data-testid="qi-excerpt"
                      >
                        {result.matched_excerpt}
                      </blockquote>
                    </div>
                  )}

                  {/* Explanation */}
                  <div>
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300 block mb-1">
                      Explanation
                    </span>
                    <p className="text-sm text-slate-600 dark:text-slate-400" data-testid="qi-explanation">
                      {result.explanation}
                    </p>
                  </div>

                  {/* Merkle proof collapsible */}
                  {result.merkle_proof && (
                    <div className="border border-slate-200 dark:border-slate-700 rounded-md">
                      <button
                        type="button"
                        className="w-full flex items-center justify-between px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-md"
                        onClick={() => setMerkleOpen(!merkleOpen)}
                        data-testid="qi-merkle-toggle"
                      >
                        <span>Merkle Proof</span>
                        <svg
                          className={`w-4 h-4 transition-transform ${merkleOpen ? 'rotate-180' : ''}`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      {merkleOpen && (
                        <div className="px-3 pb-3 border-t border-slate-200 dark:border-slate-700 pt-3">
                          <pre
                            className="text-xs bg-slate-100 dark:bg-slate-900 p-3 rounded-md overflow-auto max-h-64 text-slate-700 dark:text-slate-300"
                            data-testid="qi-merkle-json"
                          >
                            {JSON.stringify(result.merkle_proof, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
