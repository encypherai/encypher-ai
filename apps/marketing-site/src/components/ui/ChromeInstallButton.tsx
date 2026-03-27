'use client';

/**
 * ChromeInstallButton
 *
 * Smart install button for the Encypher Verify Chrome extension.
 *
 * Behaviour:
 *   - Detects Chromium-based browsers (Chrome, Edge, Brave) via the presence of
 *     window.chrome.runtime.sendMessage.
 *   - Pings the installed extension via chrome.runtime.sendMessage (possible
 *     because encypher.com is listed in the manifest externally_connectable).
 *     If the extension responds (even with an error payload), it is installed.
 *     If chrome.runtime.lastError is set, it is not installed.
 *   - Renders appropriate state: detecting -> not-installed -> installed,
 *     or a disabled state on non-Chromium browsers.
 *
 * NOTE: True inline installation (bypassing the Chrome Web Store) is no longer
 * possible -- Google removed chrome.webstore.install() in Chrome 71 (2018).
 * The best achievable UX is: click here -> Chrome Web Store page -> "Add to Chrome".
 */

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { CheckCircle, ArrowRight } from 'lucide-react';

const EXTENSION_ID = 'pbmfpddbafkhdjemgcnegddmniflbjla';

export const CHROME_STORE_URL =
  'https://chromewebstore.google.com/detail/encypher-verify/' + EXTENSION_ID;

type InstallState = 'detecting' | 'not-chromium' | 'not-installed' | 'installed';

function detectExtension(): Promise<InstallState> {
  return new Promise((resolve) => {
    // Must be in browser and have the chrome.runtime API
    if (
      typeof window === 'undefined' ||
      typeof (window as { chrome?: { runtime?: { sendMessage?: unknown; lastError?: unknown } } }).chrome
        ?.runtime?.sendMessage !== 'function'
    ) {
      resolve('not-chromium');
      return;
    }

    let settled = false;
    const settle = (state: InstallState) => {
      if (!settled) {
        settled = true;
        resolve(state);
      }
    };

    // Timeout fallback -- sendMessage should be near-instant for a local extension
    setTimeout(() => settle('not-installed'), 1500);

    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).chrome.runtime.sendMessage(
        EXTENSION_ID,
        { type: 'PING' },
        () => {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          const lastError = (window as any).chrome.runtime.lastError;
          if (lastError) {
            // Extension not installed or not reachable
            settle('not-installed');
          } else {
            // Extension responded (even with an error payload) -- it is installed
            settle('installed');
          }
        },
      );
    } catch {
      settle('not-installed');
    }
  });
}

interface ChromeInstallButtonProps {
  size?: 'default' | 'sm' | 'lg' | 'icon';
  variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link' | 'destructive';
  className?: string;
  /** Text shown when extension is not installed. Defaults to "Add to Chrome". */
  installLabel?: string;
}

export function ChromeInstallButton({
  size = 'default',
  variant = 'default',
  className,
  installLabel = 'Add to Chrome',
}: ChromeInstallButtonProps) {
  const [state, setState] = useState<InstallState>('detecting');

  useEffect(() => {
    detectExtension().then(setState);
  }, []);

  if (state === 'installed') {
    return (
      <Button size={size} variant="outline" className={className} disabled>
        <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
        Installed
      </Button>
    );
  }

  if (state === 'not-chromium') {
    return (
      <Button
        size={size}
        variant={variant}
        className={className}
        asChild
      >
        <a href={CHROME_STORE_URL} target="_blank" rel="noopener noreferrer">
          Get on Chrome Web Store
          <ArrowRight className="ml-2 h-4 w-4" />
        </a>
      </Button>
    );
  }

  // 'detecting' and 'not-installed' both show the install button.
  // During detection the button is functionally ready -- detection is fast enough
  // that it resolves before most users can click.
  return (
    <Button size={size} variant={variant} className={className} asChild>
      <a href={CHROME_STORE_URL} target="_blank" rel="noopener noreferrer">
        {installLabel}
        <ArrowRight className="ml-2 h-4 w-4" />
      </a>
    </Button>
  );
}
