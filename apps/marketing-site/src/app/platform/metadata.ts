import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Platform | C2PA Signing, Watermarking & Rights Management | Encypher',
  description: 'API and SDKs for C2PA document signing, invisible Unicode watermarking, attribution analytics, and rights management. Python, TypeScript, Go, Rust. Built on the standard co-authored with Google, OpenAI, Adobe, and Microsoft.',
  alternates: {
    canonical: 'https://encypherai.com/platform',
  },
  openGraph: {
    title: 'Encypher Platform: C2PA Signing, Watermarking & Attribution',
    description: 'Sentence-level Merkle tree authentication. Patent-pending invisible watermarks that survive copy-paste. Publisher rights profiles travel with content. One API for the full content authentication pipeline.',
    url: 'https://encypherai.com/platform',
    images: ['/og-image.png'],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Encypher Platform: C2PA Signing & Attribution',
    description: 'API and SDKs for C2PA signing, invisible watermarking, and rights management. Co-authored the C2PA text standard with Google, OpenAI, Adobe, and Microsoft.',
  },
};
