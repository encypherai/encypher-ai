'use client';

import { useSession } from 'next-auth/react';
import { useQuery } from '@tanstack/react-query';
import { useState, useRef, useEffect, useCallback } from 'react';
import Image from 'next/image';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { EncypherMark, EncypherLoader, BRAND_COLORS } from '@encypher/icons';
import apiClient from '../../lib/api';

type BgMode = 'light' | 'dark';

const SVG_ASSETS = [
  { label: 'Mark - Navy (no bg)', file: 'mark-navy-nobg.svg' },
  { label: 'Mark - White (no bg)', file: 'mark-white-nobg.svg' },
  { label: 'Mark - Navy (bg)', file: 'mark-navy-bg.svg' },
  { label: 'Mark - White (bg)', file: 'mark-white-bg.svg' },
  { label: 'Wordmark - Navy (no bg)', file: 'wordmark-navy-nobg.svg' },
  { label: 'Wordmark - White (no bg)', file: 'wordmark-white-nobg.svg' },
  { label: 'Wordmark - Navy (bg)', file: 'wordmark-navy-bg.svg' },
  { label: 'Wordmark - White (bg)', file: 'wordmark-white-bg.svg' },
  { label: 'Loader - Navy', file: 'loader-navy.svg' },
  { label: 'Loader - White', file: 'loader-white.svg' },
  { label: 'Favicon (SVG)', file: 'favicon.svg' },
] as const;

const PRESET_SIZES = [32, 64, 128, 256, 512, 1024] as const;
const MARK_COLORS = ['navy', 'azure', 'white'] as const;
const LOADER_COLORS = ['navy', 'white'] as const;
const LOADER_SIZES = ['sm', 'md', 'lg', 'xl'] as const;

function svgToCanvas(svgUrl: string, width: number, height: number): Promise<HTMLCanvasElement> {
  return new Promise((resolve, reject) => {
    const img = new window.Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      if (!ctx) return reject(new Error('Canvas context unavailable'));
      ctx.drawImage(img, 0, 0, width, height);
      resolve(canvas);
    };
    img.onerror = () => reject(new Error('Failed to load SVG'));
    img.src = svgUrl;
  });
}

function downloadCanvas(canvas: HTMLCanvasElement, filename: string) {
  const a = document.createElement('a');
  a.href = canvas.toDataURL('image/png');
  a.download = filename;
  a.click();
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      className="px-2 py-1 text-xs rounded bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
    >
      {copied ? 'Copied!' : 'Copy'}
    </button>
  );
}

function PngExportPanel({ svgUrl, basename, aspectRatio }: {
  svgUrl: string;
  basename: string;
  aspectRatio: number;
}) {
  const [open, setOpen] = useState(false);
  const [customW, setCustomW] = useState('');
  const [customH, setCustomH] = useState('');
  const [exporting, setExporting] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  const handleCustomW = (v: string) => {
    setCustomW(v);
    const n = parseInt(v, 10);
    if (n > 0) setCustomH(String(Math.round(n / aspectRatio)));
    else setCustomH('');
  };

  const handleCustomH = (v: string) => {
    setCustomH(v);
    const n = parseInt(v, 10);
    if (n > 0) setCustomW(String(Math.round(n * aspectRatio)));
    else setCustomW('');
  };

  const downloadPng = useCallback(async (w: number, h: number) => {
    setExporting(true);
    try {
      const canvas = await svgToCanvas(svgUrl, w, h);
      downloadCanvas(canvas, `${basename}-${w}x${h}.png`);
    } finally {
      setExporting(false);
    }
  }, [svgUrl, basename]);

  const downloadSvg = () => {
    const a = document.createElement('a');
    a.href = svgUrl;
    a.download = `${basename}.svg`;
    a.click();
  };

  return (
    <div ref={panelRef} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="px-2 py-1 text-xs rounded bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-800/40 transition-colors inline-flex items-center gap-1"
      >
        Download
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="absolute left-0 top-full mt-1 z-50 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg py-2 min-w-[220px]">
          {/* SVG download */}
          <button
            onClick={() => { downloadSvg(); setOpen(false); }}
            className="w-full text-left px-3 py-1.5 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 font-medium"
          >
            SVG (vector)
          </button>

          <div className="border-t border-slate-200 dark:border-slate-700 my-1" />
          <p className="px-3 py-1 text-[10px] font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider">PNG presets</p>

          {/* Preset sizes */}
          {PRESET_SIZES.map((size) => {
            const w = Math.round(size * aspectRatio);
            const h = size;
            const label = aspectRatio === 1 ? `${size}x${size}` : `${w}x${h}`;
            return (
              <button
                key={size}
                disabled={exporting}
                onClick={() => downloadPng(w, h)}
                className="w-full text-left px-3 py-1.5 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-50"
              >
                PNG {label}
              </button>
            );
          })}

          {/* Custom size */}
          <div className="border-t border-slate-200 dark:border-slate-700 my-1" />
          <p className="px-3 py-1 text-[10px] font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider">Custom size</p>
          <div className="px-3 py-1.5 flex items-center gap-2">
            <input
              type="number"
              placeholder="W"
              min={1}
              max={4096}
              value={customW}
              onChange={(e) => handleCustomW(e.target.value)}
              className="w-16 px-2 py-1 text-xs rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-200"
            />
            <span className="text-xs text-slate-400">x</span>
            <input
              type="number"
              placeholder="H"
              min={1}
              max={4096}
              value={customH}
              onChange={(e) => handleCustomH(e.target.value)}
              className="w-16 px-2 py-1 text-xs rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-200"
            />
            <button
              disabled={exporting || !customW || !customH}
              onClick={() => {
                const w = parseInt(customW, 10);
                const h = parseInt(customH, 10);
                if (w > 0 && h > 0) downloadPng(w, h);
              }}
              className="px-2 py-1 text-xs rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-40 transition-colors"
            >
              Go
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function AssetCard({ label, src, bgMode }: { label: string; src: string; bgMode: BgMode }) {
  const isDark = bgMode === 'dark';
  const isWordmark = label.toLowerCase().includes('wordmark');
  const filename = src.split('/').pop() || '';
  const basename = filename.replace('.svg', '');
  const embedUrl = `https://encypher.com/brand/${filename}`;
  const aspectRatio = isWordmark ? 134 / 24 : 1;

  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-700">
      <div
        className={`flex items-center justify-center p-6 rounded-t-xl ${
          isDark ? 'bg-slate-900' : 'bg-white'
        } ${isWordmark ? 'min-h-[80px]' : 'min-h-[120px]'}`}
      >
        <Image
          src={src}
          alt={label}
          width={isWordmark ? 200 : 64}
          height={isWordmark ? 50 : 64}
          className={isWordmark ? 'h-8 w-auto' : 'h-16 w-16'}
          unoptimized
        />
      </div>
      <div className="px-4 py-3 bg-slate-50 dark:bg-slate-800 rounded-b-xl border-t border-slate-200 dark:border-slate-700">
        <p className="text-sm font-medium text-slate-900 dark:text-white mb-2">{label}</p>
        <div className="flex items-center gap-2 flex-wrap">
          <PngExportPanel
            svgUrl={src}
            basename={basename}
            aspectRatio={aspectRatio}
          />
          <CopyButton text={embedUrl} />
        </div>
      </div>
    </div>
  );
}

function ColorSwatch({ name, hex }: { name: string; hex: string }) {
  return (
    <div className="flex items-center gap-3">
      <div
        className="w-10 h-10 rounded-lg border border-slate-200 dark:border-slate-700"
        style={{ backgroundColor: hex }}
      />
      <div>
        <p className="text-sm font-medium text-slate-900 dark:text-white capitalize">{name}</p>
        <p className="text-xs text-slate-500 dark:text-slate-400 font-mono">{hex}</p>
      </div>
    </div>
  );
}

export default function BrandAssetsPage() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const userEmail = session?.user?.email || '';

  const { data: isSuperAdmin } = useQuery({
    queryKey: ['is-super-admin'],
    queryFn: async () => {
      if (!accessToken) return false;
      return apiClient.isSuperAdmin(accessToken);
    },
    enabled: Boolean(accessToken),
    staleTime: 5 * 60 * 1000,
  });

  const isEncypherTeam =
    userEmail.endsWith('@encypher.com') || userEmail.endsWith('@encypherai.com');
  const hasAccess = isEncypherTeam || isSuperAdmin === true;

  const [bgMode, setBgMode] = useState<BgMode>('light');

  if (!hasAccess) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center min-h-[400px] text-center px-4">
          <EncypherMark color="navy" size={48} />
          <h2 className="mt-4 text-xl font-semibold text-slate-900 dark:text-white">
            Brand Assets
          </h2>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400 max-w-md">
            This page is only available to Encypher team members and administrators.
          </p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto space-y-10">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Brand Assets</h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Official Encypher brand assets. Download SVG or export as PNG at any size.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
            <button
              onClick={() => setBgMode('light')}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                bgMode === 'light'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
              }`}
            >
              Light Preview
            </button>
            <button
              onClick={() => setBgMode('dark')}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                bgMode === 'dark'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
              }`}
            >
              Dark Preview
            </button>
          </div>
        </div>

        {/* Brand Colors */}
        <section>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Brand Colors</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            {Object.entries(BRAND_COLORS).map(([name, hex]) => (
              <ColorSwatch key={name} name={name} hex={hex} />
            ))}
          </div>
        </section>

        {/* Live React Components */}
        <section>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Live Components (React)
          </h2>

          {/* Mark variants */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-3 uppercase tracking-wider">
              EncypherMark
            </h3>
            <div className="grid grid-cols-3 gap-4">
              {MARK_COLORS.map((color) => (
                <div key={color} className="space-y-3">
                  {/* Without background */}
                  <div
                    className={`flex items-center justify-center p-4 rounded-xl border border-slate-200 dark:border-slate-700 ${
                      bgMode === 'dark' ? 'bg-slate-900' : 'bg-white'
                    }`}
                  >
                    <EncypherMark color={color} size={48} />
                  </div>
                  {/* With background */}
                  <div
                    className={`flex items-center justify-center p-4 rounded-xl border border-slate-200 dark:border-slate-700 ${
                      bgMode === 'dark' ? 'bg-slate-900' : 'bg-white'
                    }`}
                  >
                    <EncypherMark color={color} size={48} withBackground />
                  </div>
                  <p className="text-xs text-center text-slate-500 dark:text-slate-400 capitalize">
                    {color}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Loader variants */}
          <div>
            <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-3 uppercase tracking-wider">
              EncypherLoader
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {LOADER_COLORS.map((color) => (
                <div
                  key={color}
                  className={`flex items-center justify-center gap-6 p-6 rounded-xl border border-slate-200 dark:border-slate-700 ${
                    color === 'white' ? 'bg-slate-900' : 'bg-white'
                  }`}
                >
                  {LOADER_SIZES.map((size) => (
                    <div key={size} className="flex flex-col items-center gap-2">
                      <EncypherLoader color={color} size={size} />
                      <span className="text-[10px] text-slate-400">{size}</span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Static SVG Assets */}
        <section>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            SVG Assets
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {SVG_ASSETS.map((asset) => (
              <AssetCard
                key={asset.file}
                label={asset.label}
                src={`/assets/${asset.file}`}
                bgMode={bgMode}
              />
            ))}
          </div>
        </section>

        {/* Embed Snippet */}
        <section>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Embed Snippet
          </h2>
          <div className="bg-slate-900 rounded-xl p-6 overflow-x-auto">
            <pre className="text-sm text-slate-300 font-mono whitespace-pre-wrap">
{`<!-- Encypher Mark -->
<img src="https://encypher.com/brand/mark-navy-nobg.svg" alt="Encypher" width="32" height="32" />

<!-- Encypher Wordmark -->
<img src="https://encypher.com/brand/wordmark-navy-nobg.svg" alt="Encypher" height="24" />`}
            </pre>
            <div className="mt-3">
              <CopyButton
                text={`<img src="https://encypher.com/brand/mark-navy-nobg.svg" alt="Encypher" width="32" height="32" />`}
              />
            </div>
          </div>
        </section>

        {/* Usage Guidelines */}
        <section className="pb-10">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Usage Guidelines
          </h2>
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 space-y-3 text-sm text-slate-600 dark:text-slate-300">
            <p>- Use the logo as-is. Do not modify colors, proportions, or add effects.</p>
            <p>- Maintain minimum clear space equal to the height of the checkmark around the mark.</p>
            <p>- On dark backgrounds, use the white variants. On light backgrounds, use navy.</p>
            <p>- The mark can be used standalone. The wordmark should not be used without the mark.</p>
            <p>- Minimum size: 16px for the mark, 80px width for the wordmark.</p>
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}
