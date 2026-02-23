import { Metadata } from 'next';

export const metadata: Metadata = {
  // Page Title - Search Results & Browser Tab
  title: "Encypher | Content Intelligence Infrastructure",
  
  // Meta Description - Search Results Preview
  description: "Authors of C2PA Section A.7. Patent-pending granular content attribution with Merkle tree authentication. Court-admissible evidence for publishers, performance intelligence for AI companies.",
  
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
    description: "Authors of C2PA Section A.7. Patent-pending Merkle tree authentication provides court-admissible evidence for publishers and performance intelligence for AI companies.",
    images: ['/og-image.png'],
    type: 'website',
    url: 'https://encypherai.com',
    siteName: 'Encypher',
  },
  
  // Twitter/X
  twitter: {
    card: 'summary_large_image',
    title: "Content Intelligence Infrastructure | Encypher",
    description: "Authors of the C2PA text standard. Patent-pending granular attribution transforms litigation into licensing. Court-admissible evidence at sentence level.",
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