'use client';

import { EncypherLoader } from '@encypher/icons';

interface BrandedLoadingScreenProps {
  /** Optional message shown below the progress bar */
  message?: string;
}

/**
 * Full-screen branded loading screen with the Encypher mark
 * and a Tron-style bouncing progress bar.
 *
 * Responds to light/dark mode via the .dark class on <html>.
 * Uses brand colors: blue-ncs (#2a87c4) and columbia-blue (#b7d5ed).
 */
export function BrandedLoadingScreen({ message }: BrandedLoadingScreenProps) {
  return (
    <div className="branded-loading-screen" role="status" aria-label={message || 'Loading'}>
      {/* Animated logo - navy in light mode, white in dark mode */}
      <div className="branded-loading-mark">
        <EncypherLoader size="xl" color="navy" className="!h-14 !w-14 block dark:hidden" />
        <EncypherLoader size="xl" color="white" className="!h-14 !w-14 hidden dark:block" />
      </div>

      {/* Progress bar track */}
      <div className="branded-loading-track">
        <div className="branded-loading-bar" />
      </div>

      {/* Optional message */}
      {message && (
        <p className="branded-loading-message">{message}</p>
      )}
    </div>
  );
}
