import type { Metadata, Viewport } from 'next';
import '@encypher/design-system/theme';
import './globals.css';
import Providers from '../components/providers';
import { GoogleTagManager } from '@next/third-parties/google';
import { ScriptsContainer } from '../components/ScriptsContainer';
import CookieConsentBanner from '../components/CookieConsent';

const isProd = process.env.NEXT_PUBLIC_ENV === 'production';

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
};

export const metadata: Metadata = {
  title: 'Dashboard - Encypher',
  description: 'Manage your Encypher API keys, usage, and content authentication',
  robots: {
    index: false, // Don't index dashboard pages
    follow: false,
  },
  icons: {
    icon: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
      { url: '/favicon.ico', sizes: 'any' },
    ],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Blocking script: sets dark class before first paint to prevent flash */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var s=localStorage.getItem('encypher_theme');var d=document.documentElement;if(s==='dark'||(s!=='light'&&window.matchMedia('(prefers-color-scheme: dark)').matches)){d.classList.add('dark');}else{d.classList.remove('dark');}}catch(e){}})();`,
          }}
        />
        {/* Preconnect to critical third-party origins */}
        {isProd && (
          <>
            <link rel="preconnect" href="https://css.zohocdn.com" />
            <link rel="preconnect" href="https://js.zohocdn.com" />
            <link rel="dns-prefetch" href="https://www.googletagmanager.com" />
            <link rel="dns-prefetch" href="https://cdn.pagesense.io" />
            <link rel="dns-prefetch" href="https://salesiq.zohopublic.com" />
          </>
        )}
      </head>
      {isProd && <GoogleTagManager gtmId="GTM-MVSGF4KH" />}
      <body className="antialiased bg-background">
        <Providers>
          {children}
          <ScriptsContainer isProd={isProd} />
          <CookieConsentBanner />
        </Providers>
      </body>
    </html>
  );
}
