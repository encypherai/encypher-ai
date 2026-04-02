'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ChromeInstallButton } from '@/components/ui/ChromeInstallButton';
import {
  ArrowRight,
  CheckCircle2,
  Copy,
  Loader2,
  Shield,
  AlertTriangle,
  RotateCcw,
} from 'lucide-react';
import { EncypherMark, EncypherLoader } from '@encypher/icons';
import {
  VerificationSequence,
  SIGN_STEPS,
  VERIFY_TEXT_STEPS,
  withMinDuration,
  getStepsDuration,
} from '@/components/ui/VerificationSequence';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type Stage =
  | 'input'
  | 'signing'
  | 'signed'
  | 'verifying'
  | 'verified'
  | 'tampered'
  | 'unsigned'
  | 'error';

interface VerifyResult {
  verification_status: string;
  raw_hidden_data?: {
    valid?: boolean;
    tampered?: boolean;
    signer_name?: string;
    signer_id?: string;
    timestamp?: string;
    reason_code?: string;
  } | null;
  embeddings_found?: number;
}

// ---------------------------------------------------------------------------
// Sample content
// ---------------------------------------------------------------------------

const SAMPLE_TEXT =
  'Researchers at Stanford University have developed a new method for ' +
  'detecting AI-generated content in academic papers, according to a study ' +
  'published Tuesday in Nature. The technique relies on subtle statistical ' +
  'patterns in how humans and AI systems structure sentences, achieving 94 ' +
  'percent accuracy in blind tests. The findings come amid growing concerns ' +
  'about academic integrity as large language models become more widely ' +
  'accessible to students and researchers worldwide.';

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

async function apiSign(text: string): Promise<string> {
  const res = await fetch('/api/tools/sign', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      original_text: text,
      metadata_format: 'c2pa_v2_2',
      ai_info: { provenance: '' },
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail || `Sign failed (${res.status})`);
  }
  const data = await res.json() as { encoded_text: string };
  return data.encoded_text;
}

async function apiVerify(text: string): Promise<VerifyResult> {
  const res = await fetch('/api/tools/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ encoded_text: text }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail || `Verify failed (${res.status})`);
  }
  return res.json() as Promise<VerifyResult>;
}

// ---------------------------------------------------------------------------
// Step badge
// ---------------------------------------------------------------------------

function StepBadge({ n, done, active }: { n: number; done: boolean; active: boolean }) {
  const base =
    'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 transition-colors';
  if (done)
    return (
      <div className={`${base} bg-primary text-primary-foreground`}>
        <EncypherMark color="white" className="w-4 h-4" />
      </div>
    );
  if (active)
    return <div className={`${base} bg-primary text-primary-foreground`}>{n}</div>;
  return (
    <div className={`${base} bg-muted text-muted-foreground border border-border`}>{n}</div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

interface TryItPageProps {
  embedded?: boolean;
}

export default function TryItPage({ embedded = false }: TryItPageProps) {
  const [stage, setStage] = useState<Stage>('input');
  const [inputText, setInputText] = useState(SAMPLE_TEXT);
  const [signedText, setSignedText] = useState('');
  const [verifyInput, setVerifyInput] = useState('');
  const [verifyResult, setVerifyResult] = useState<VerifyResult | null>(null);
  const [copied, setCopied] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const invisibleChars = signedText ? signedText.length - inputText.length : 0;
  const step1Done = stage !== 'input' && stage !== 'signing';
  const step2Done =
    stage === 'verifying' ||
    stage === 'verified' ||
    stage === 'tampered' ||
    stage === 'unsigned' ||
    stage === 'error';
  const showStep2 = step1Done;
  const showStep3 = step1Done;
  const showResult =
    stage === 'verified' ||
    stage === 'tampered' ||
    stage === 'unsigned' ||
    stage === 'error';

  const handleSign = async () => {
    if (!inputText.trim()) return;
    setStage('signing');
    setErrorMsg(null);
    try {
      const signed = await withMinDuration(apiSign(inputText), getStepsDuration(SIGN_STEPS));
      setSignedText(signed);
      setVerifyInput(signed);
      setStage('signed');
    } catch (e: unknown) {
      setErrorMsg(e instanceof Error ? e.message : 'Signing failed');
      setStage('input');
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(signedText).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleVerify = async () => {
    if (!verifyInput.trim()) return;
    setStage('verifying');
    setErrorMsg(null);
    try {
      const result = await withMinDuration(apiVerify(verifyInput), getStepsDuration(VERIFY_TEXT_STEPS));
      setVerifyResult(result);
      const valid = result.raw_hidden_data?.valid === true;
      const tamperedByApi = result.raw_hidden_data?.tampered === true;
      const found = (result.embeddings_found ?? 0) > 0;
      // Watermark found but invalid = content was modified after signing
      const effectivelyTampered = !valid && found;
      if (valid) setStage('verified');
      else if (tamperedByApi || effectivelyTampered) setStage('tampered');
      else if (!found) setStage('unsigned');
      else setStage('error');
    } catch (e: unknown) {
      setErrorMsg(e instanceof Error ? e.message : 'Verification failed');
      setStage('error');
    }
  };

  const handleReset = () => {
    setStage('input');
    setInputText(SAMPLE_TEXT);
    setSignedText('');
    setVerifyInput('');
    setVerifyResult(null);
    setErrorMsg(null);
    setCopied(false);
  };

  const signerName =
    verifyResult?.raw_hidden_data?.signer_name ||
    verifyResult?.raw_hidden_data?.signer_id ||
    'Encypher Demo Signer';
  const signedAt = verifyResult?.raw_hidden_data?.timestamp
    ? new Date(verifyResult.raw_hidden_data.timestamp).toLocaleString()
    : 'just now';

  return (
    <div className={embedded ? 'bg-background' : 'bg-background min-h-screen'}>
      {!embedded && (
        <section className="py-16 border-b border-border bg-muted/30">
          <div className="container mx-auto px-4 text-center">
            <h1 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">
              See It Work in 30 Seconds
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Sign any text with an invisible C2PA watermark. Copy it anywhere.
              Verify it came back unchanged. No account required.
            </p>
          </div>
        </section>
      )}

      {/* Steps */}
      <section className="py-12">
        <div className="container mx-auto px-4 max-w-2xl space-y-10">

          {/* ----------------------------------------------------------------
              STEP 1 - Input
          ---------------------------------------------------------------- */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <StepBadge n={1} done={step1Done} active={stage === 'input' || stage === 'signing'} />
              <h2 className="text-xl font-semibold">Paste your content</h2>
              {step1Done && (
                <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
                  Signed
                </span>
              )}
            </div>

            {stage === 'input' && (
              <div className="space-y-3">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  className="w-full min-h-[140px] p-4 rounded-lg border border-border bg-card text-sm leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-primary/40"
                />
                <div className="flex items-center justify-between flex-wrap gap-3">
                  <p className="text-xs text-muted-foreground">
                    Sample article pre-filled. Edit it or paste your own.
                  </p>
                  <Button
                    onClick={handleSign}
                    size="lg"
                    className="font-semibold"
                    disabled={!inputText.trim()}
                  >
                    Sign This Text <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </div>
                {errorMsg && <p className="text-sm text-destructive">{errorMsg}</p>}
              </div>
            )}

            {stage === 'signing' && (
              <div className="p-5 rounded-lg border border-border bg-card">
                <VerificationSequence steps={SIGN_STEPS} />
              </div>
            )}

            {step1Done && (
              <div className="p-4 rounded-lg border border-border bg-muted/40">
                <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
                  {inputText.slice(0, 140)}...
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  {inputText.length} readable characters
                </p>
              </div>
            )}
          </div>

          {/* ----------------------------------------------------------------
              STEP 2 - Signed output
          ---------------------------------------------------------------- */}
          {showStep2 && (
            <div>
              <div className="flex items-center gap-3 mb-4">
                <StepBadge n={2} done={step2Done} active={stage === 'signed'} />
                <h2 className="text-xl font-semibold">
                  Identical to readers. Verifiable forever.
                </h2>
              </div>

              <div className="rounded-lg border border-primary/30 bg-card overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3 bg-primary/5 border-b border-primary/20 gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <Shield className="w-4 h-4 text-primary flex-shrink-0" />
                    <span className="text-sm font-medium">Signed text</span>
                    {invisibleChars > 0 && (
                      <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full whitespace-nowrap">
                        +{invisibleChars} invisible chars
                      </span>
                    )}
                  </div>
                  <Button variant="outline" size="sm" onClick={handleCopy} className="flex-shrink-0">
                    {copied ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 text-green-500" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 mr-1.5" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>

                <div className="p-4">
                  <p className="text-sm leading-relaxed text-foreground">
                    {signedText.slice(0, 340)}
                    {signedText.length > 340 ? '...' : ''}
                  </p>
                </div>

                <div className="px-4 py-3 bg-muted/30 border-t border-border">
                  <p className="text-xs text-muted-foreground">
                    Visually identical to what you pasted. The watermark is
                    embedded invisibly within the text - undetectable by
                    readers, machine-readable on verification.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* ----------------------------------------------------------------
              STEP 3 - Verify
          ---------------------------------------------------------------- */}
          {showStep3 && (
            <div>
              <div className="flex items-center gap-3 mb-4">
                <StepBadge
                  n={3}
                  done={showResult}
                  active={stage === 'signed' || stage === 'verifying'}
                />
                <h2 className="text-xl font-semibold">Verify the watermark survived</h2>
              </div>

              <div className="p-4 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-sm mb-4 dark:bg-amber-950/20 dark:border-amber-800 dark:text-amber-100">
                <strong>Skeptic test:</strong> Copy the signed text above, paste
                it into a Google Doc, email, or Slack message - then copy it
                back below and verify. Or just click Verify to see it work
                in-page.
              </div>

              {!showResult && (
                <div className="space-y-3">
                  <textarea
                    value={verifyInput}
                    onChange={(e) => setVerifyInput(e.target.value)}
                    className="w-full min-h-[120px] p-4 rounded-lg border border-border bg-card text-sm leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-primary/40"
                    placeholder="Paste signed text here..."
                  />
                  <div className="flex items-center justify-between flex-wrap gap-3">
                    <p className="text-xs text-muted-foreground">
                      Pre-filled with the signed text. Edit a word to test
                      tamper detection.
                    </p>
                    <Button
                      onClick={handleVerify}
                      size="lg"
                      disabled={stage === 'verifying' || !verifyInput.trim()}
                    >
                      {stage === 'verifying' ? (
                        <>
                          <EncypherLoader size="sm" color="current" className="!mx-0 mr-2" />
                          Verifying...
                        </>
                      ) : (
                        <>
                          Verify Provenance <ArrowRight className="ml-2 h-4 w-4" />
                        </>
                      )}
                    </Button>
                  </div>
                  {stage === 'verifying' && (
                    <div className="mt-4 p-4 rounded-lg border border-border bg-card">
                      <VerificationSequence steps={VERIFY_TEXT_STEPS} />
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* ----------------------------------------------------------------
              RESULT - Verified
          ---------------------------------------------------------------- */}
          {stage === 'verified' && (
            <div className="space-y-6">
              <div className="rounded-lg border-2 border-green-500 bg-green-50 dark:bg-green-950/20 overflow-hidden">
                <div className="flex items-center gap-3 px-6 py-4 bg-green-500 text-white">
                  <EncypherMark color="white" className="w-6 h-6 flex-shrink-0" />
                  <div>
                    <p className="font-bold text-lg">Verified Authentic</p>
                    <p className="text-green-100 text-sm">
                      Watermark survived. Provenance confirmed.
                    </p>
                  </div>
                </div>
                <div className="p-6 space-y-3">
                  {(
                    [
                      ['Signed by', signerName],
                      ['Signed at', signedAt],
                      ['Standard', 'C2PA 2.3 (Section A.7 - authored by Encypher)'],
                      ['Content integrity', 'Unmodified since signing'],
                    ] as [string, string][]
                  ).map(([label, value]) => (
                    <div key={label} className="flex justify-between text-sm gap-4">
                      <span className="text-muted-foreground flex-shrink-0">{label}</span>
                      <span
                        className={`font-medium text-right ${
                          label === 'Content integrity'
                            ? 'text-green-600 dark:text-green-400'
                            : ''
                        }`}
                      >
                        {value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-5 bg-muted/50 rounded-lg border border-border text-sm text-muted-foreground leading-relaxed">
                That watermark survives copy-paste, email, Slack, Google Docs,
                and web scraping. When an AI system scrapes your content,
                the provenance markers persist in their training databases - which
                means{' '}
                <strong className="text-foreground">
                  they cannot claim they did not know it was licensed
                </strong>
                .
              </div>

              <div className="text-center pt-2">
                <p className="text-lg font-semibold mb-1">
                  This runs on every article you publish.
                </p>
                <p className="text-muted-foreground text-sm mb-6">
                  Sign your archive in one batch job. New content signs at
                  publication. Free to start.
                </p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <Button asChild size="lg" className="font-semibold">
                    <Link href="/auth/register">
                      Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                  <Button asChild variant="outline" size="lg">
                    <Link href="/solutions/publishers">
                      See the Full Publisher Story <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </div>
                <button
                  onClick={handleReset}
                  className="mt-5 text-sm text-muted-foreground hover:text-foreground underline flex items-center gap-1.5 mx-auto"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Run it again
                </button>
              </div>
            </div>
          )}

          {/* ----------------------------------------------------------------
              RESULT - Tampered
          ---------------------------------------------------------------- */}
          {stage === 'tampered' && (
            <div className="space-y-4">
              <div className="rounded-lg border-2 border-amber-500 bg-amber-50 dark:bg-amber-950/20 overflow-hidden">
                <div className="flex items-center gap-3 px-6 py-4 bg-amber-500 text-white">
                  <AlertTriangle className="w-6 h-6 flex-shrink-0" />
                  <div>
                    <p className="font-bold text-lg">Tampered Content Detected</p>
                    <p className="text-amber-100 text-sm">
                      The C2PA manifest was found but the text has been
                      modified since signing.
                    </p>
                  </div>
                </div>
                <div className="p-6 text-sm text-muted-foreground space-y-3">
                  <p>
                    The manifest is still present - proving the original
                    content existed and was owned. The modification is now
                    provably documented.
                  </p>
                  <p>
                    In a real enforcement scenario this is evidence of
                    unauthorized modification - stronger than simple use.
                  </p>
                </div>
              </div>
              <div className="text-center">
                <button
                  onClick={handleReset}
                  className="text-sm text-muted-foreground hover:text-foreground underline flex items-center gap-1.5 mx-auto"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Run it again
                </button>
              </div>
            </div>
          )}

          {/* ----------------------------------------------------------------
              RESULT - Unsigned
          ---------------------------------------------------------------- */}
          {stage === 'unsigned' && (
            <div className="space-y-4">
              <div className="p-5 rounded-lg border border-border bg-muted/30 text-sm space-y-2">
                <p className="font-medium">No watermark found in this text.</p>
                <p className="text-muted-foreground">
                  This is what an AI company sees when content has no
                  provenance - no proof of ownership, no licensing terms, no
                  evidence of willful infringement. Unsigned content has no
                  leverage.
                </p>
              </div>
              <div className="text-center">
                <button
                  onClick={handleReset}
                  className="text-sm text-muted-foreground hover:text-foreground underline flex items-center gap-1.5 mx-auto"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Try again with signed text
                </button>
              </div>
            </div>
          )}

          {/* ----------------------------------------------------------------
              RESULT - Error
          ---------------------------------------------------------------- */}
          {stage === 'error' && (
            <div className="space-y-4">
              <div className="p-5 rounded-lg border border-destructive/50 bg-destructive/5 text-sm space-y-2">
                <p className="font-medium text-destructive">
                  {errorMsg || 'Verification failed.'}
                </p>
                <p className="text-muted-foreground">Please try again.</p>
              </div>
              <div className="text-center">
                <button
                  onClick={handleReset}
                  className="text-sm text-muted-foreground hover:text-foreground underline flex items-center gap-1.5 mx-auto"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Try again
                </button>
              </div>
            </div>
          )}

        </div>
      </section>

      {/* Context strip - shown only on input stage */}
      {stage === 'input' && (
        <section className="py-12 border-t border-border bg-muted/20">
          <div className="container mx-auto px-4 max-w-2xl">
            <div className="grid sm:grid-cols-3 gap-6 text-center text-sm">
              <div>
                <p className="font-semibold mb-1">No account required</p>
                <p className="text-muted-foreground">
                  This demo uses a shared signing key. Your own content uses a
                  key tied to your organization.
                </p>
              </div>
              <div>
                <p className="font-semibold mb-1">Invisible to readers</p>
                <p className="text-muted-foreground">
                  Watermarks are zero-width Unicode characters. CMS systems,
                  search engines, and human readers never see them.
                </p>
              </div>
              <div>
                <p className="font-semibold mb-1">C2PA 2.3 compliant</p>
                <p className="text-muted-foreground">
                  Encypher authored Section A.7 of the C2PA standard. This demo
                  produces standard-compliant manifests.
                </p>
              </div>
            </div>
          </div>
        </section>
      )}

      {!embedded && (
        <section className="border-t border-border py-8 bg-background">
          <div className="container mx-auto px-4 max-w-2xl">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-lg border border-border bg-muted/30">
              <div>
                <p className="font-semibold text-sm">Verify on any webpage</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Install the free Encypher Verify Chrome extension to detect C2PA
                  watermarks automatically as you browse. No account required for
                  verification.
                </p>
              </div>
              <ChromeInstallButton installLabel="Add to Chrome" />
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
