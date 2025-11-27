/**
 * SEO configuration for Encypher website
 * Centralizes metadata for consistent implementation across pages
 * Updated: October 2024 - Standards Authority Positioning
 */

import type { Metadata } from "next";
import { getSiteUrl } from './env';

// ============================================================================
// SITE CONFIGURATION
// ============================================================================

export const siteConfig = {
  name: "Encypher",
  url: "https://encypherai.com",
  tagline: "From the Authors of the C2PA Text Standard",
  description: "Authors of the C2PA text authentication standard. Building infrastructure for AI content authentication and licensing through sentence-level tracking.",
  
  // OG Images by audience
  images: {
    default: "https://encypherai.com/og-image.png",
    publishers: "https://encypherai.com/og-image-publishers.png",
    ai: "https://encypherai.com/og-image-ai.png",
  },
  
  // Social profiles
  social: {
    twitter: "@encypherai",
    linkedin: "company/encypherai",
    github: "encypherai",
  },
  
  // Standards & partnerships
  standards: {
    c2pa: "https://c2pa.org",
    cai: "https://contentauthenticity.org",
  }
};

// ============================================================================
// KEYWORDS BY CATEGORY
// ============================================================================

export const keywords = {
  // Core technology keywords
  core: [
    "C2PA text standard",
    "sentence-level tracking",
    "content authentication",
    "cryptographic proof",
    "content provenance",
    "AI content licensing",
  ],
  
  // Publisher-focused keywords
  publishers: [
    "publisher content protection",
    "AI copyright litigation",
    "court-admissible evidence",
    "content licensing revenue",
    "AI content usage tracking",
    "publisher AI licensing",
    "copyright enforcement",
    "AI copyright infringement",
    "AI art copyright",
    "publisher licensing",
    "AI training data copyright",
    "prove AI copyright infringement",
  ],
  
  // AI Lab-focused keywords
  aiLabs: [
    "AI model optimization",
    "AI performance intelligence",
    "model parameter tracking",
    "publisher integration",
    "AI compliance",
    "C2PA compliance",
    "AI content analytics",
    "C2PA",
    "AI watermarking",
    "content authenticity",
    "AI detector",
  ],
  
  // Enterprise-focused keywords
  enterprises: [
    "EU AI Act",
    "enterprise AI governance",
    "AI compliance",
    "AI audit trail",
    "AI privacy protection",
  ],
  
  // Technical keywords
  technical: [
    "Unicode metadata",
    "cryptographic signatures",
    "content authentication standard",
    "zero-knowledge proofs",
    "tamper detection",
    "blockchain verification",
  ],
  
  // Market/industry keywords
  market: [
    "AI content economy",
    "content authenticity infrastructure",
    "AI licensing framework",
    "publisher coalition",
    "content provenance standard",
  ]
};

// Combined keyword array for general use
export const allKeywords = [
  ...keywords.core,
  ...keywords.publishers,
  ...keywords.aiLabs,
  ...keywords.enterprises,
  ...keywords.technical,
  ...keywords.market,
];

// ============================================================================
// DEFAULT METADATA
// ============================================================================

export const defaultMetadata: Metadata = {
  metadataBase: new URL(getSiteUrl()),
  title: {
    default: "Encypher | Content Intelligence Infrastructure",
    template: "%s | Encypher"
  },
  description: siteConfig.description,
  keywords: allKeywords,
  authors: [{ name: "Encypher" }],
  creator: "Encypher",
  publisher: "Encypher",
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
  openGraph: {
    type: "website",
    locale: "en_US",
    url: siteConfig.url,
    title: "Encypher | Content Intelligence Infrastructure",
    description: siteConfig.description,
    siteName: siteConfig.name,
    images: [
      {
        url: siteConfig.images.default,
        width: 1200,
        height: 630,
        alt: "Encypher - Content Intelligence Infrastructure",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Encypher | Content Intelligence Infrastructure",
    description: siteConfig.description,
    images: [siteConfig.images.default],
    creator: siteConfig.social.twitter,
  },
  icons: {
    icon: "/encypher_icon_nobg_color.ico",
    shortcut: "/encypher_icon_nobg_color.ico",
    apple: "/encypher_icon_nobg_color.png",
  },
  alternates: {
    canonical: siteConfig.url,
  },
};

// ============================================================================
// AUDIENCE-SPECIFIC METADATA GENERATORS
// ============================================================================

/**
 * Publisher-specific metadata
 */
export function getPublisherMetadata(): Metadata {
  return {
    title: "Publisher Content Protection & Licensing | Encypher",
    description: "From litigation costs to licensing revenue. Court-admissible evidence with 100% accuracy. Track which sentences were used, where, and when.",
    keywords: [...keywords.core, ...keywords.publishers],
    openGraph: {
      title: "From Litigation Costs to Licensing Revenue | Encypher",
      description: "Court-admissible evidence. 100% accuracy. Track which sentences were used, where, and when. Join publishers defining AI licensing terms.",
      images: [
        {
          url: siteConfig.images.publishers,
          width: 1200,
          height: 630,
          alt: "Encypher for Publishers - From Litigation Costs to Licensing Revenue",
        }
      ],
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: "From Litigation Costs to Licensing Revenue | Encypher",
      description: "Court-admissible evidence. Track which sentences were used, where, and when. Join publishers defining AI licensing terms.",
      images: [siteConfig.images.publishers],
    },
    alternates: {
      canonical: `${siteConfig.url}/publishers`,
    },
  };
}

/**
 * Enterprise-specific metadata
 */
export function getEnterpriseMetadata(): Metadata {
  return generateMetadata(
    "Enterprise AI Governance & Compliance | Encypher",
    "Implement EU AI Act-ready governance with sentence-level audit trails, compliance reporting, and privacy-safe content intelligence.",
    "/solutions/enterprises",
    siteConfig.images.default,
    keywords.enterprises
  );
}

/**
 * AI Lab-specific metadata
 */
export function getAILabMetadata(): Metadata {
  return {
    title: "AI Performance Intelligence | Encypher",
    description: "See which parameters drive viral content. Track every output at sentence-level. One integration covers the entire publisher ecosystem.",
    keywords: [...keywords.core, ...keywords.aiLabs],
    openGraph: {
      title: "See Which Parameters Drive Viral Content | Encypher",
      description: "Track every output. Optimize your models. One integration covers the entire publisher ecosystem.",
      images: [
        {
          url: siteConfig.images.ai,
          width: 1200,
          height: 630,
          alt: "Encypher for AI Labs - See Which Parameters Drive Viral Content",
        }
      ],
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: "See Which Parameters Drive Viral Content | Encypher",
      description: "Track every output. Optimize your models. Performance intelligence + compliance infrastructure.",
      images: [siteConfig.images.ai],
    },
    alternates: {
      canonical: `${siteConfig.url}/ai`,
    },
  };
}

/**
 * Basic WebPage schema generator
 */
export function getWebPageSchema(
  title: string,
  description: string,
  path: string
) {
  const pageUrl = `${siteConfig.url}${path}`;
  return {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": title,
    "description": description,
    "url": pageUrl,
  };
}

// ============================================================================
// STRUCTURED DATA SCHEMAS
// ============================================================================

/**
 * Organization schema with standards authority positioning
 */
export const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Encypher",
  "alternateName": "EncypherAI",
  "legalName": "Encypher Corporation",
  "url": siteConfig.url,
  "logo": `${siteConfig.url}/encypher_full_nobg.png`,
  "description": siteConfig.description,
  "foundingDate": "2025",
  "founders": [
    {
      "@type": "Person",
      "name": "Erik Svilich"
    }
  ],
  "knowsAbout": [
    "C2PA text standard",
    "Content authentication",
    "AI content licensing",
    "Sentence-level tracking",
    "Cryptographic proof",
    "Publisher licensing infrastructure"
  ],
  "memberOf": [
    {
      "@type": "Organization",
      "name": "Coalition for Content Provenance and Authenticity",
      "url": siteConfig.standards.c2pa
    },
    {
      "@type": "Organization",
      "name": "Content Authenticity Initiative",
      "url": siteConfig.standards.cai
    }
  ],
  "sameAs": [
    `https://github.com/${siteConfig.social.github}`,
    `https://twitter.com/${siteConfig.social.twitter}`,
    `https://linkedin.com/${siteConfig.social.linkedin}`
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "Sales",
    "email": "sales@encypherai.com",
    "availableLanguage": ["en"]
  },
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Encypher Infrastructure Services",
    "itemListElement": [
      {
        "@type": "Offer",
        "itemOffered": {
          "@type": "Service",
          "name": "Publisher Content Authentication",
          "description": "Sentence-level tracking and court-admissible evidence for content licensing"
        }
      },
      {
        "@type": "Offer",
        "itemOffered": {
          "@type": "Service",
          "name": "AI Lab Performance Intelligence",
          "description": "Model optimization and publisher ecosystem integration infrastructure"
        }
      }
    ]
  }
};

/**
 * Infrastructure software schema (not "app")
 */
export const softwareSchema = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Encypher",
  "applicationCategory": "AI Infrastructure",
  "operatingSystem": "Cross-platform",
  "description": siteConfig.description,
  "softwareVersion": "2.0",
  "author": {
    "@type": "Organization",
    "name": "Encypher",
    "url": siteConfig.url
  },
  "keywords": allKeywords.join(", "),
  "offers": {
    "@type": "Offer",
    "description": "Enterprise AI content authentication infrastructure",
    "priceSpecification": {
      "@type": "PriceSpecification",
      "description": "Value-based pricing with revenue share model"
    }
  },
  "featureList": [
    "C2PA text standard implementation",
    "Sentence-level content tracking",
    "Cryptographic proof generation",
    "Court-admissible evidence packages",
    "Performance intelligence analytics"
  ]
};

/**
 * FAQ schema for homepage (AI search optimization)
 */
export const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is Encypher?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Encypher authored the C2PA text authentication standard and provides sentence-level content tracking infrastructure for publishers and AI labs. We enable litigation evidence and content licensing through cryptographic proof with 100% accuracy."
      }
    },
    {
      "@type": "Question",
      "name": "What is the C2PA text standard?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The C2PA (Coalition for Content Provenance and Authenticity) text standard, authored by Encypher, defines how text content is cryptographically authenticated. It enables verification of content origin, modifications, and usage with mathematical certainty."
      }
    },
    {
      "@type": "Question",
      "name": "How is Encypher different from AI detection tools?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "AI detection tools provide statistical guessing with 26% accuracy and high false positive rates. Encypher provides cryptographic proof with 100% accuracy and sentence-level granularity. Our evidence is court-admissible and eliminates false positives through mathematical certainty, not statistical inference."
      }
    },
    {
      "@type": "Question",
      "name": "What is sentence-level tracking?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Sentence-level tracking is Encypher's proprietary technology that identifies and authenticates content at individual sentence granularity. Instead of proving 'a document was accessed,' we prove 'sentences 47, 103, and 289 from this specific article were used.' This granularity is critical for litigation evidence and content licensing."
      }
    },
    {
      "@type": "Question",
      "name": "Who uses Encypher?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Encypher serves two primary markets: (1) Publishers seeking court-admissible evidence for AI copyright litigation and content licensing revenue, and (2) AI labs requiring publisher ecosystem integration, model performance intelligence, and compliance infrastructure. Our infrastructure enables both litigation resolution and key competitive intelligence on how your models are performing across the internet."
      }
    }
  ]
};

/**
 * Blog post schema generator
 */
export function getBlogPostSchema(post: {
  title: string;
  description: string;
  author: string;
  publishDate: string;
  modifiedDate?: string;
  imageUrl?: string;
  url: string;
}) {
  return {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": post.title,
    "description": post.description,
    "image": post.imageUrl || siteConfig.images.default,
    "author": {
      "@type": "Person",
      "name": post.author
    },
    "publisher": {
      "@type": "Organization",
      "name": "Encypher",
      "logo": {
        "@type": "ImageObject",
        "url": `${siteConfig.url}/encypher_full_nobg.png`
      }
    },
    "datePublished": post.publishDate,
    "dateModified": post.modifiedDate || post.publishDate,
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": post.url
    }
  };
}

// ============================================================================
// METADATA GENERATORS
// ============================================================================

/**
 * Generate page-specific metadata with proper defaults
 */
export function generateMetadata(
  title: string,
  description?: string,
  path?: string,
  imageUrl?: string,
  additionalKeywords?: string[]
): Metadata {
  const pageUrl = path ? `${siteConfig.url}${path}` : siteConfig.url;
  const pageImageUrl = imageUrl || siteConfig.images.default;
  const pageKeywords = additionalKeywords 
    ? [...allKeywords, ...additionalKeywords]
    : allKeywords;
  
  return {
    ...defaultMetadata,
    title: title,
    description: description || defaultMetadata.description,
    keywords: pageKeywords,
    alternates: {
      canonical: pageUrl,
    },
    openGraph: {
      ...defaultMetadata.openGraph,
      title: title,
      description: description || siteConfig.description,
      url: pageUrl,
      images: [
        {
          url: pageImageUrl,
          width: 1200,
          height: 630,
          alt: title,
        },
      ],
    },
    twitter: {
      ...defaultMetadata.twitter,
      title: title,
      description: description || siteConfig.description,
      images: [pageImageUrl],
    },
  };
}

/**
 * Generate metadata for demo pages
 */
export function getDemoMetadata(audience: 'publisher' | 'ai'): Metadata {
  if (audience === 'publisher') {
    return generateMetadata(
      "Publisher Demo | Encypher",
      "See how sentence-level tracking transforms litigation into licensing. 2-minute interactive demonstration.",
      "/publisher-demo",
      siteConfig.images.publishers,
      keywords.publishers
    );
  } else {
    return generateMetadata(
      "AI Lab Demo | Encypher",
      "See which parameters drive viral content. 2-minute interactive demonstration of performance intelligence.",
      "/ai-demo",
      siteConfig.images.ai,
      keywords.aiLabs
    );
  }
}

// ============================================================================
// AI SEARCH OPTIMIZATION
// ============================================================================

/**
 * Generate AI-friendly summary block (invisible to users, visible to crawlers)
 * Add this to pages using: <AISearchSummary {...data} />
 */
export interface AISearchSummaryProps {
  whatWeDo: string;
  whoItsFor: string;
  keyDifferentiator: string;
  primaryValue: string;
}

export function getAISearchSummary(props: AISearchSummaryProps) {
  return {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "mainEntity": {
      "@type": "Thing",
      "name": "Encypher",
      "description": props.whatWeDo,
      "audience": props.whoItsFor,
      "additionalProperty": [
        {
          "@type": "PropertyValue",
          "name": "Key Differentiator",
          "value": props.keyDifferentiator
        },
        {
          "@type": "PropertyValue",
          "name": "Primary Value",
          "value": props.primaryValue
        }
      ]
    }
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  siteConfig,
  keywords,
  allKeywords,
  defaultMetadata,
  organizationSchema,
  softwareSchema,
  faqSchema,
  getPublisherMetadata,
  getAILabMetadata,
  getEnterpriseMetadata,
  getDemoMetadata,
  generateMetadata,
  getBlogPostSchema,
  getWebPageSchema,
  getAISearchSummary,
};