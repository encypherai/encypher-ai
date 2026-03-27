import type { Metadata } from "next";
import { Roboto, Playfair_Display } from "next/font/google";
import "./globals.css";
import { DemoBanner } from "@/components/layout/DemoBanner";
import { Masthead } from "@/components/layout/Masthead";
import { SectionNav } from "@/components/layout/SectionNav";
import { Footer } from "@/components/layout/Footer";
import { ExtensionBanner } from "@/components/layout/ExtensionBanner";

const roboto = Roboto({
  variable: "--font-roboto",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  display: "swap",
});

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  weight: ["700", "900"],
  style: ["normal", "italic"],
  display: "swap",
});

// UnifrakturCook loaded via Google Fonts CSS link (single weight, not in next/font)
// This avoids issues with next/font and single-weight decorative fonts

export const metadata: Metadata = {
  title: "The Encypher Times",
  description:
    "Every Word Authenticated -- Every article, image, audio clip, and video on this site is cryptographically signed by Encypher.",
  icons: {
    icon: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
      { url: '/favicon.ico', sizes: 'any' },
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=UnifrakturCook:wght@700&display=block"
          rel="stylesheet"
        />
      </head>
      <body
        className={`${roboto.variable} ${playfair.variable} antialiased`}
      >
        <DemoBanner />
        <div className="newspaper-container">
          <Masthead />
          <SectionNav />
          <main>{children}</main>
          <Footer />
        </div>
        <ExtensionBanner />
      </body>
    </html>
  );
}
