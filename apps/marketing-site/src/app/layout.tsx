import type { Metadata } from "next";
import { Suspense } from "react";
import { Roboto, Roboto_Mono } from "next/font/google";
import "./globals.css";
import "../styles/animations.css";
// import { Navbar } from '@/components/layout/navbar';
// import { Footer } from '@/components/layout/footer';
import { Providers } from '@/components/providers';
import { Toaster } from '@encypher/design-system';
import { GoogleTagManager } from '@next/third-parties/google';
import { defaultMetadata } from '@/lib/seo';
import { ClientProviders } from "./ClientProviders";
import { ToastProvider } from '@encypher/design-system';
import { ConditionalLayoutWrapper } from '@/components/layout/ConditionalLayoutWrapper';
import { ScriptsContainer } from '@/components/ScriptsContainer';
import WebPageSchema from '@/components/seo/WebPageSchema';
import { AnalyticsTracker } from '@/components/AnalyticsTracker';
import CookieConsentBanner from '@/components/CookieConsent';

const isProd = process.env.NEXT_PUBLIC_ENV === "production";

const roboto = Roboto({
  variable: "--font-roboto",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  display: "swap",
  preload: true,
});

const robotoMono = Roboto_Mono({
  variable: "--font-roboto-mono",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  display: "swap",
  preload: false,
});

export const metadata: Metadata = defaultMetadata;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Preconnect to critical third-party origins */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
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
      <body
        className={`${roboto.variable} ${robotoMono.variable} antialiased`}
      >
        <ClientProviders>
          <Providers>
            <ToastProvider>
              <ConditionalLayoutWrapper>{children}</ConditionalLayoutWrapper>
              <Toaster />
              <ScriptsContainer isProd={isProd} />
              <WebPageSchema />
              <CookieConsentBanner />
            </ToastProvider>
          </Providers>
        </ClientProviders>
      </body>
    </html>
  );
}
