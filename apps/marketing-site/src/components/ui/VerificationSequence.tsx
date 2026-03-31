'use client';

import { useEffect, useState } from 'react';
import { EncypherMark, EncypherLoader } from '@encypher/icons';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface VerificationStep {
  label: string;
  /** Milliseconds this step stays active before advancing to the next. */
  duration: number;
}

// ---------------------------------------------------------------------------
// Predefined step sequences
// ---------------------------------------------------------------------------

export const SIGN_STEPS: VerificationStep[] = [
  { label: 'Analyzing document structure...', duration: 350 },
  { label: 'Generating cryptographic signatures...', duration: 450 },
  { label: 'Embedding provenance markers...', duration: 400 },
];

export const VERIFY_TEXT_STEPS: VerificationStep[] = [
  { label: 'Scanning for provenance markers...', duration: 350 },
  { label: 'Verifying cryptographic signatures...', duration: 450 },
  { label: 'Validating certificate chain...', duration: 350 },
];

export const VERIFY_FILE_STEPS: VerificationStep[] = [
  { label: 'Reading file metadata...', duration: 350 },
  { label: 'Checking C2PA manifest...', duration: 450 },
  { label: 'Validating signatures and certificates...', duration: 400 },
];

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

/** Sum of all step durations - the minimum time the sequence takes. */
export function getStepsDuration(steps: VerificationStep[]): number {
  return steps.reduce((sum, s) => sum + s.duration, 0);
}

/**
 * Wraps a promise so the caller waits at least `minMs` milliseconds.
 * The actual operation runs immediately in parallel with the timer.
 */
export function withMinDuration<T>(
  promise: Promise<T>,
  minMs: number,
): Promise<T> {
  return Promise.all([
    promise,
    new Promise<void>((resolve) => setTimeout(resolve, minMs)),
  ]).then(([result]) => result);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Animated stepped progress indicator for sign/verify operations.
 * Auto-advances through steps on timers. Mount while loading, unmount on
 * completion - the parent controls visibility.
 */
export function VerificationSequence({
  steps,
  className = '',
}: {
  steps: VerificationStep[];
  className?: string;
}) {
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    if (activeIndex >= steps.length) return;
    const timer = setTimeout(
      () => setActiveIndex((i) => i + 1),
      steps[activeIndex].duration,
    );
    return () => clearTimeout(timer);
  }, [activeIndex, steps]);

  return (
    <div className={`space-y-2.5 ${className}`}>
      {steps.map((step, i) => (
        <div key={i} className="flex items-center gap-2.5 text-sm">
          {i < activeIndex ? (
            <EncypherMark color="azure" className="h-4 w-4 flex-shrink-0" />
          ) : i === activeIndex ? (
            <EncypherLoader size="sm" color="current" className="!mx-0 text-primary flex-shrink-0" />
          ) : (
            <div className="h-4 w-4 rounded-full border-2 border-muted-foreground/20 flex-shrink-0" />
          )}
          <span
            className={
              i < activeIndex
                ? 'text-muted-foreground'
                : i === activeIndex
                  ? 'text-foreground font-medium'
                  : 'text-muted-foreground/40'
            }
          >
            {step.label}
          </span>
        </div>
      ))}
    </div>
  );
}
