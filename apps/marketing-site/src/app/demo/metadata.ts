import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Request a Demo | Encypher',
  description: 'See Encypher in action. Request a personalized demo of C2PA signing, invisible watermarking, attribution analytics, and publisher coalition licensing. For publishers, AI labs, and enterprises.',
  alternates: {
    canonical: 'https://encypherai.com/demo',
  },
  openGraph: {
    title: 'Request an Encypher Demo',
    description: 'Live demo of content authentication, coalition licensing, and attribution analytics. Built on the C2PA text standard.',
    url: 'https://encypherai.com/demo',
    images: ['/og-image.png'],
    type: 'website',
  },
};
