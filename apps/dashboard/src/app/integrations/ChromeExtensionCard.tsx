'use client';

import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@encypher/design-system';
import { CopyButton } from './CopyButton';

type ViewState = 'overview' | 'setup';

export function ChromeExtensionCard() {
  const [viewState, setViewState] = useState<ViewState>('overview');

  const chromeStoreUrl = 'https://chromewebstore.google.com/detail/encypher-c2pa-verifier/EXTENSION_ID_HERE';
  const dashboardApiKeysUrl = '/api-keys';

  if (viewState === 'setup') {
    return (
      <Card variant="bordered" className="border-blue-ncs/50 col-span-full lg:col-span-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ChromeIcon />
              <CardTitle className="text-lg">Chrome Extension Setup</CardTitle>
            </div>
            <button
              onClick={() => setViewState('overview')}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Step 1 */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-6 h-6 rounded-full bg-blue-ncs text-white flex items-center justify-center text-xs font-bold">
                1
              </div>
              <h3 className="text-sm font-semibold text-delft-blue dark:text-white">
                Install the extension
              </h3>
            </div>
            <p className="text-xs text-muted-foreground ml-8 mb-3">
              Install the Encypher C2PA Verifier from the Chrome Web Store. It works on Chrome, Edge, Brave, and any Chromium-based browser.
            </p>
            <div className="ml-8">
              <a
                href={chromeStoreUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-blue-ncs text-white rounded-md hover:bg-blue-ncs/90 transition-colors"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
                </svg>
                Chrome Web Store
              </a>
            </div>
          </div>

          {/* Step 2 */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-6 h-6 rounded-full bg-blue-ncs text-white flex items-center justify-center text-xs font-bold">
                2
              </div>
              <h3 className="text-sm font-semibold text-delft-blue dark:text-white">
                Get your API key
              </h3>
            </div>
            <p className="text-xs text-muted-foreground ml-8 mb-3">
              Verification works without an API key. To <strong>sign content</strong>, you need an API key from your dashboard.
            </p>
            <div className="ml-8">
              <a
                href={dashboardApiKeysUrl}
                className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-ncs hover:underline"
              >
                Go to API Keys
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>
          </div>

          {/* Step 3 */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-6 h-6 rounded-full bg-blue-ncs text-white flex items-center justify-center text-xs font-bold">
                3
              </div>
              <h3 className="text-sm font-semibold text-delft-blue dark:text-white">
                Configure the extension
              </h3>
            </div>
            <p className="text-xs text-muted-foreground ml-8 mb-3">
              Click the Encypher icon in your browser toolbar, then open <strong>Settings</strong>. Paste your API key and save.
            </p>
          </div>

          {/* Step 4 */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-6 h-6 rounded-full bg-blue-ncs text-white flex items-center justify-center text-xs font-bold">
                4
              </div>
              <h3 className="text-sm font-semibold text-delft-blue dark:text-white">
                Start verifying and signing
              </h3>
            </div>
            <div className="ml-8 space-y-2">
              <p className="text-xs text-muted-foreground">
                The extension automatically scans pages for C2PA-signed content and shows verification badges inline.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <FeatureItem
                  title="Auto-detect"
                  description="Scans pages for signed content"
                />
                <FeatureItem
                  title="Inline badges"
                  description="Color-coded verification status"
                />
                <FeatureItem
                  title="Sign from browser"
                  description="Sign text in the popup or editors"
                />
                <FeatureItem
                  title="Right-click verify"
                  description="Verify any selected text"
                />
              </div>
            </div>
          </div>

          {/* Usage limits */}
          <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 mb-4">
            <h4 className="text-xs font-semibold text-delft-blue dark:text-white mb-1">
              Usage Limits
            </h4>
            <div className="text-xs text-muted-foreground space-y-1">
              <p><strong>Free tier:</strong> Unlimited verification, 1,000 signings/month</p>
              <p><strong>Enterprise:</strong> Unlimited verification and signing, Merkle tree, attribution tracking</p>
            </div>
          </div>

          {/* API Base URL */}
          <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
            <h4 className="text-xs font-semibold text-delft-blue dark:text-white mb-1">
              API Base URL
            </h4>
            <p className="text-xs text-muted-foreground mb-2">
              The extension connects to the Encypher API by default. You can change this in the extension settings.
            </p>
            <div className="flex items-center gap-2">
              <code className="text-xs flex-1 font-mono text-delft-blue dark:text-slate-200 bg-white dark:bg-slate-900 px-2 py-1 rounded border border-slate-200 dark:border-slate-700">
                https://api.encypherai.com
              </code>
              <CopyButton text="https://api.encypherai.com" />
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // ── Overview state ──
  return (
    <Card variant="bordered" className="hover:border-blue-ncs/50 transition-all duration-200">
      <CardHeader>
        <div className="flex items-start gap-4">
          <ChromeIcon />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <CardTitle className="text-lg">Chrome Extension</CardTitle>
              <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full">
                Available
              </span>
            </div>
            <CardDescription className="mt-1">
              Verify and sign C2PA content on any webpage. Auto-detects signed content and shows inline trust badges.
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2">
          <button
            onClick={() => setViewState('setup')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-blue-ncs text-white rounded-md hover:bg-blue-ncs/90 transition-colors"
          >
            Setup Guide
          </button>
          <a
            href={chromeStoreUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-md hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
            </svg>
            Install
          </a>
        </div>
      </CardContent>
    </Card>
  );
}

function ChromeIcon() {
  return (
    <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-gradient-to-br from-[#1B2F50] to-[#2A87C4] flex items-center justify-center">
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="white" strokeWidth="1.5" fill="none" />
        <path d="M7.5 12.5l3 3 6-7" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      </svg>
    </div>
  );
}

function FeatureItem({ title, description }: { title: string; description: string }) {
  return (
    <div className="p-2 bg-slate-50 dark:bg-slate-800 rounded-md border border-slate-100 dark:border-slate-700">
      <p className="text-xs font-medium text-delft-blue dark:text-white">{title}</p>
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  );
}
