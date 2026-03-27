"use client";

import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { EncypherMark } from "@encypher/icons";

const DISMISSED_KEY = "encypher-ext-banner-dismissed";

export function ExtensionBanner() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Show after a short delay so the user sees content first
    const dismissed = sessionStorage.getItem(DISMISSED_KEY);
    if (!dismissed) {
      const timer = setTimeout(() => setVisible(true), 3000);
      return () => clearTimeout(timer);
    }
  }, []);

  function dismiss() {
    setVisible(false);
    sessionStorage.setItem(DISMISSED_KEY, "1");
  }

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 animate-slide-up">
      <div className="relative bg-delft-blue text-white px-4 py-3 shadow-[0_-2px_12px_rgba(0,0,0,0.15)]">
        <div className="max-w-[900px] mx-auto">
          {/* Dismiss button -- top-right on mobile, inline on desktop */}
          <button
            onClick={dismiss}
            className="absolute top-3 right-3 sm:hidden p-1 text-white/60 hover:text-white transition-colors"
            aria-label="Dismiss"
          >
            <X className="w-4 h-4" />
          </button>

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex items-start sm:items-center gap-3 min-w-0 pr-6 sm:pr-0">
              <EncypherMark className="w-5 h-5 shrink-0 mt-0.5 sm:mt-0" color="teal" />
              <p className="font-[family-name:var(--font-ui)] text-sm leading-snug">
                <span className="font-bold">See provenance badges on every article.</span>{" "}
                <span className="text-white/80 hidden sm:inline">
                  Install Encypher Verify for Chrome for real-time signature verification as you browse.
                </span>
              </p>
            </div>
            <div className="flex items-center gap-3 shrink-0 pl-8 sm:pl-0">
              <a
                href="https://encypher.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-[#00CED1] text-delft-blue font-[family-name:var(--font-ui)] text-xs font-bold rounded hover:bg-[#00DFD2] transition-colors whitespace-nowrap"
              >
                <EncypherMark className="w-3.5 h-3.5" color="navy" />
                Install Extension
              </a>
              <button
                onClick={dismiss}
                className="hidden sm:block p-1 text-white/60 hover:text-white transition-colors"
                aria-label="Dismiss"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
