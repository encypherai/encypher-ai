'use client';

import { useState, useEffect } from 'react';
import { EncypherLoader } from '@encypher/icons';

/**
 * Dev-only preview page for the branded loading screen.
 * Visit /loading-preview to see both light and dark variants
 * side by side, plus a live full-screen demo toggle.
 */
export default function LoadingPreviewPage() {
  const [showFullScreen, setShowFullScreen] = useState(false);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains('dark'));
  }, []);

  const toggleTheme = () => {
    const next = !isDark;
    setIsDark(next);
    document.documentElement.classList.toggle('dark', next);
    localStorage.setItem('encypher_theme', next ? 'dark' : 'light');
  };

  return (
    <>
      {/* Full-screen demo overlay */}
      {showFullScreen && (
        <div className="branded-loading-screen" role="status" aria-label="Loading">
          <div className="branded-loading-mark">
            <EncypherLoader size="xl" color="navy" className="!h-14 !w-14 block dark:hidden" />
            <EncypherLoader size="xl" color="white" className="!h-14 !w-14 hidden dark:block" />
          </div>
          <div className="branded-loading-track">
            <div className="branded-loading-bar" />
          </div>
          <p className="branded-loading-message">Checking your session...</p>
          <button
            onClick={() => setShowFullScreen(false)}
            className="absolute bottom-8 text-sm text-muted-foreground underline hover:text-foreground transition-colors"
          >
            Close full-screen demo
          </button>
        </div>
      )}

      <div className="min-h-screen bg-background p-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">Loading Screen Preview</h1>
              <p className="text-sm text-muted-foreground mt-1">
                Branded loading screen with Tron-style bouncing progress bar
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={toggleTheme}
                className="px-4 py-2 text-sm font-medium rounded-lg border border-border bg-card text-foreground hover:bg-muted transition-colors"
              >
                {isDark ? 'Light mode' : 'Dark mode'}
              </button>
              <button
                onClick={() => setShowFullScreen(true)}
                className="px-4 py-2 text-sm font-medium rounded-lg bg-blue-ncs text-white hover:bg-blue-ncs/90 transition-colors"
              >
                Full-screen demo
              </button>
            </div>
          </div>

          {/* Side-by-side previews */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Light mode preview */}
            <div className="rounded-xl overflow-hidden border border-border shadow-sm">
              <div className="px-4 py-2 bg-card border-b border-border">
                <span className="text-xs font-medium text-muted-foreground">Light mode</span>
              </div>
              <div
                className="relative flex flex-col items-center justify-center gap-8 py-20"
                style={{ backgroundColor: 'hsl(216 18% 94%)' }}
              >
                <div className="branded-loading-mark">
                  <EncypherLoader size="xl" color="navy" className="!h-14 !w-14" />
                </div>
                <div
                  className="branded-loading-track"
                  style={{ backgroundColor: 'rgba(42, 135, 196, 0.15)' }}
                >
                  <div className="branded-loading-bar" />
                </div>
                <p className="text-[0.8125rem]" style={{ color: 'hsl(215 16% 47%)' }}>
                  Checking your session...
                </p>
              </div>
            </div>

            {/* Dark mode preview */}
            <div className="rounded-xl overflow-hidden border border-border shadow-sm">
              <div className="px-4 py-2 bg-card border-b border-border">
                <span className="text-xs font-medium text-muted-foreground">Dark mode</span>
              </div>
              <div
                className="relative flex flex-col items-center justify-center gap-8 py-20"
                style={{ backgroundColor: 'hsl(213 49% 21%)' }}
              >
                <div className="branded-loading-mark">
                  <EncypherLoader size="xl" color="white" className="!h-14 !w-14" />
                </div>
                <div
                  className="branded-loading-track"
                  style={{ backgroundColor: 'rgba(183, 213, 237, 0.12)' }}
                >
                  <div className="branded-loading-bar" />
                </div>
                <p className="text-[0.8125rem]" style={{ color: 'hsl(215 20% 65%)' }}>
                  Checking your session...
                </p>
              </div>
            </div>
          </div>

          {/* Variants */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-foreground">Variants</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* No message */}
              <div className="rounded-xl overflow-hidden border border-border shadow-sm">
                <div className="px-4 py-2 bg-card border-b border-border">
                  <span className="text-xs font-medium text-muted-foreground">No message</span>
                </div>
                <div className="flex flex-col items-center justify-center gap-8 py-16 bg-background">
                  <div className="branded-loading-mark">
                    <EncypherLoader size="xl" color="navy" className="!h-14 !w-14 block dark:hidden" />
                    <EncypherLoader size="xl" color="white" className="!h-14 !w-14 hidden dark:block" />
                  </div>
                  <div className="branded-loading-track">
                    <div className="branded-loading-bar" />
                  </div>
                </div>
              </div>

              {/* With message */}
              <div className="rounded-xl overflow-hidden border border-border shadow-sm">
                <div className="px-4 py-2 bg-card border-b border-border">
                  <span className="text-xs font-medium text-muted-foreground">With message</span>
                </div>
                <div className="flex flex-col items-center justify-center gap-8 py-16 bg-background">
                  <div className="branded-loading-mark">
                    <EncypherLoader size="xl" color="navy" className="!h-14 !w-14 block dark:hidden" />
                    <EncypherLoader size="xl" color="white" className="!h-14 !w-14 hidden dark:block" />
                  </div>
                  <div className="branded-loading-track">
                    <div className="branded-loading-bar" />
                  </div>
                  <p className="branded-loading-message">Loading invitation...</p>
                </div>
              </div>

              {/* Custom message */}
              <div className="rounded-xl overflow-hidden border border-border shadow-sm">
                <div className="px-4 py-2 bg-card border-b border-border">
                  <span className="text-xs font-medium text-muted-foreground">Signing in</span>
                </div>
                <div className="flex flex-col items-center justify-center gap-8 py-16 bg-background">
                  <div className="branded-loading-mark">
                    <EncypherLoader size="xl" color="navy" className="!h-14 !w-14 block dark:hidden" />
                    <EncypherLoader size="xl" color="white" className="!h-14 !w-14 hidden dark:block" />
                  </div>
                  <div className="branded-loading-track">
                    <div className="branded-loading-bar" />
                  </div>
                  <p className="branded-loading-message">Checking your session...</p>
                </div>
              </div>
            </div>
          </div>

          {/* Animation details */}
          <div className="rounded-xl border border-border bg-card p-6 space-y-3">
            <h2 className="text-lg font-semibold text-foreground">Animation details</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-muted-foreground">Bar animation</div>
                <div className="font-medium text-foreground">1.4s cubic-bezier</div>
              </div>
              <div>
                <div className="text-muted-foreground">Bar width</div>
                <div className="font-medium text-foreground">40% of track</div>
              </div>
              <div>
                <div className="text-muted-foreground">Gradient</div>
                <div className="font-medium text-foreground">blue-ncs -&gt; cyber-teal</div>
              </div>
              <div>
                <div className="text-muted-foreground">Fade-in</div>
                <div className="font-medium text-foreground">0.4s staggered</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
