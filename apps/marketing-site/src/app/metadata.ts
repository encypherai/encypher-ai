import { Metadata } from 'next';

export const metadata: Metadata = {
  // Page Title - Search Results & Browser Tab
  title: "Encypher | Content Intelligence Infrastructure",
  
  // Meta Description - Search Results Preview
  description: "Authors of the C2PA text authentication standard. Sentence-level tracking transforms AI litigation into licensing revenue. Mathematical proof for publishers, performance intelligence for AI labs.",
  
  // Keywords Array (not string)
  keywords: [
    // High Volume - Capture Market
    "AI copyright infringement",
    "deepfake detection", 
    "AI watermarking",
    "AI detector",
    
    // Authority - Even if Low Volume
    "C2PA",
    "C2PA text standard",
    "content authenticity",
    "EU AI Act",
    
    // Strategic - Emerging/Related
    "AI art copyright",
    "cryptographic proof",
    "publisher licensing",
    "enterprise AI governance",
    "AI training data copyright",
    
    // Problem-Focused - High Intent
    "prove AI copyright infringement",
    "AI compliance",
    "AI audit trail",
    "content provenance",
    "AI privacy",
    
    // Tools/Solutions - Breakout Queries
    "deepfake detection tools",
    "AI content verification",
  ],
  
  // Open Graph (LinkedIn, Facebook, etc.)
  openGraph: {
    title: "Turn Content Intelligence Into Market Advantage",
    description: "Authors of the C2PA text standard. Sentence-level tracking provides court-admissible evidence for publishers and performance intelligence for AI labs. Mathematical certainty, not statistical guessing.",
    images: ['/og-image.png'],
    type: 'website',
    url: 'https://encypherai.com',
    siteName: 'Encypher',
  },
  
  // Twitter/X
  twitter: {
    card: 'summary_large_image',
    title: "Content Intelligence Infrastructure | Encypher",
    description: "C2PA text standard authors. Sentence-level tracking transforms litigation into licensing. Evidence for publishers, intelligence for AI labs.",
    images: ['/og-image.png'],
    creator: '@encypherai',
  },
  
  // Favicon
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon.ico',
  },
  
  // Additional SEO
  alternates: {
    canonical: 'https://encypherai.com',
  },
  
  // Robots
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};