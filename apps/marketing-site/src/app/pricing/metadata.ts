import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Pricing | Free to Sign, Paid to Enforce | Encypher',
  description: 'Free tier for C2PA signing and watermarking. Enterprise plans for publisher coalition access, attribution analytics, and enforcement pipelines. AI labs get one integration for the entire publisher ecosystem.',
  alternates: {
    canonical: 'https://encypher.com/pricing',
  },
  openGraph: {
    title: 'Encypher Pricing: Free to Sign, Paid to Enforce',
    description: 'Publishers sign content for free. AI companies access the full publisher coalition and compliance tooling. Enterprise pricing aligned with your outcomes.',
    url: 'https://encypher.com/pricing',
    images: ['/og-image.png'],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Encypher Pricing | Free to Sign, Paid to Enforce',
    description: 'Free C2PA signing. Enterprise plans for coalition access and attribution analytics. Success-based models aligned with your outcomes.',
  },
};
