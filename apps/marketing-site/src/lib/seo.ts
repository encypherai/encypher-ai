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
  tagline: "Machine-Readable Rights for Your Content",
  description: "Encypher authored the C2PA text authentication standard. Patent-pending granular content attribution with Merkle tree authentication for tamper-evident documentation.",
  
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
    "tamper-evident documentation",
    "content licensing infrastructure",
    "AI content usage tracking",
    "publisher AI licensing",
    "copyright enforcement",
    "AI copyright infringement",
    "AI art copyright",
    "publisher licensing",
    "AI training data copyright",
    "content provenance verification",
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
    default: "Encypher | Machine-Readable Rights for Your Content",
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
    title: "Encypher | Machine-Readable Rights for Your Content",
    description: siteConfig.description,
    siteName: siteConfig.name,
    images: [
      {
        url: siteConfig.images.default,
        width: 1200,
        height: 630,
        alt: "Encypher - Machine-Readable Rights for Your Content",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Encypher | Machine-Readable Rights for Your Content",
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
    description: "Transform unmarked content into provably owned assets. Cryptographic watermarking that survives copy-paste. Formal notice capability for AI licensing.",
    keywords: [...keywords.core, ...keywords.publishers],
    openGraph: {
      title: "Transform Your Archive Into Revenue | Encypher",
      description: "Cryptographic watermarking that survives copy-paste. Formal notice capability. Join publishers defining AI licensing terms.",
      images: [
        {
          url: siteConfig.images.publishers,
          width: 1200,
          height: 630,
          alt: "Encypher for Publishers - Transform Your Archive Into Revenue",
        }
      ],
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: "Transform Your Archive Into Revenue | Encypher",
      description: "Cryptographic watermarking that survives copy-paste. Formal notice capability. Join publishers defining AI licensing terms.",
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
    title: "AI Content Licensing & C2PA Compliance | Encypher",
    description: "One API for publisher coalition access, C2PA compliance proof, and EU AI Act transparency watermarking. No per-publisher negotiations. Built with OpenAI, Google, Adobe, and Microsoft.",
    keywords: [...keywords.core, ...keywords.aiLabs],
    openGraph: {
      title: "License Publisher Content at Scale | Encypher",
      description: "One agreement covers the entire publisher coalition. Cryptographic proof of C2PA compliance, EU AI Act Article 52 transparency, and real-world performance intelligence.",
      images: [
        {
          url: siteConfig.images.ai,
          width: 1200,
          height: 630,
          alt: "Encypher for AI Companies - Publisher Content Licensing and C2PA Compliance",
        }
      ],
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: "License Publisher Content at Scale | Encypher",
      description: "One API for publisher coalition licensing, C2PA compliance proof, and EU AI Act transparency. Built with OpenAI, Google, Adobe, Microsoft.",
      images: [siteConfig.images.ai],
    },
    alternates: {
      canonical: `${siteConfig.url}/solutions/ai-companies`,
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
          "description": "Sentence-level tracking and tamper-evident documentation for content licensing"
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
    "Cryptographic verification",
    "Tamper-evident documentation",
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
        "text": "Encypher authored the C2PA text authentication standard and provides sentence-level content tracking infrastructure for publishers and AI labs. We provide technical infrastructure for content licensing through cryptographic verification."
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
        "text": "AI detection tools provide statistical guessing with variable accuracy and high false positive rates. Encypher provides cryptographic verification with sentence-level granularity. Our tamper-evident documentation is designed for legal proceedings and eliminates false positives through mathematical certainty, not statistical inference."
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
        "text": "Encypher serves two primary markets: (1) Publishers seeking tamper-evident documentation for content licensing infrastructure, and (2) AI labs requiring publisher ecosystem integration, model performance intelligence, and compliance infrastructure. Our infrastructure provides technical foundation for content licensing and performance intelligence on how your models are performing across the internet."
      }
    }
  ]
};

/**
 * Page-specific FAQ schema for /solutions/publishers
 * Must match the visible FAQ accordion content on that page.
 */
export const publishersFaqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Will my content look different to readers?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. The cryptographic watermark is completely invisible. It is embedded using zero-width Unicode characters between words -- characters that are present in the text but invisible to the human eye. Your readers, your fonts, and your layout are not affected in any way."
      }
    },
    {
      "@type": "Question",
      "name": "Will this slow down my website?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. Signing happens server-side at publish time, not on page load. Once an article is signed, there is no additional overhead for readers or for your site. The signed content is stored exactly as you published it."
      }
    },
    {
      "@type": "Question",
      "name": "Who gets the licensing revenue?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The majority goes to you, the publisher. When an AI company licenses your content through the Encypher Coalition, the split strongly favors publishers -- the same split regardless of whether you are on a free or paid plan. Encypher takes a small platform fee."
      }
    },
    {
      "@type": "Question",
      "name": "Do I need a lawyer to issue a formal notice?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. Encypher generates the formal notice package automatically from your evidence -- a cryptographically-backed letter that you can send directly or forward to counsel. Many publishers find that receiving a notice is enough to open licensing talks. If it escalates, your lawyer will have a complete evidence chain, tamper-evident delivery confirmation, and documentation in standard litigation support formats."
      }
    },
    {
      "@type": "Question",
      "name": "What if AI companies just ignore the rights terms?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Ignoring machine-readable rights terms that are embedded in every document is what converts innocent infringement into willful infringement under US copyright law. Willful infringement carries statutory damages up to $150,000 per work vs. $30,000 for innocent infringement. EU AI Act compliance (effective August 2026) also requires AI providers to respect machine-readable rights reservations."
      }
    },
    {
      "@type": "Question",
      "name": "Can I sign content from years ago?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. You can backfill your entire archive using the Encypher API or our SDK batch tools. The Python and TypeScript SDKs let you sign thousands of articles in a single overnight job. The free tier covers 1,000 documents per month; volume pricing is available for large archives."
      }
    },
    {
      "@type": "Question",
      "name": "What happens if I stop using Encypher?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "All content you signed remains signed -- permanently. The cryptographic signatures are embedded in the text itself and do not depend on Encypher servers to remain valid. The free tier will always exist at $0. If you stop a paid plan, you keep the signing infrastructure and your signed archive, and lose access to paid analytics and enforcement tools until you re-subscribe."
      }
    },
    {
      "@type": "Question",
      "name": "Is my content stored on Encypher servers?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. Encypher signs your content at the moment of publication and returns it to your CMS. We store metadata and cryptographic hashes for verification purposes -- not the full text of your articles. Your content stays on your servers. We can verify a piece of text is yours using the hash without needing a copy of the original."
      }
    }
  ]
};

/**
 * Page-specific FAQ schema for /solutions/ai-companies
 * Must match the visible FAQ accordion content on that page.
 */
export const aiCompaniesFaqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Do we need to negotiate with each publisher separately?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. The Encypher publisher coalition operates as a network license -- one agreement with Encypher covers access to all coalition members at the tiers each publisher has set (Bronze for indexing, Silver for RAG and attribution, Gold for training). You never negotiate directly with individual publishers. As new publishers join the coalition, your license extends to them automatically."
      }
    },
    {
      "@type": "Question",
      "name": "We received a formal notice with an Encypher evidence package. What does that mean?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The evidence package contains cryptographic proof that is independently verifiable -- it does not depend on trusting Encypher's servers. The signature is embedded in the content itself, verified against the publisher's own key. Your legal team should treat it as valid documentation of when content was published, who authored it, and what licensing tier it was marked for. The practical path forward is to join the coalition; AI companies that resolve notices this way typically complete the process within 60 days."
      }
    },
    {
      "@type": "Question",
      "name": "Does provenance verification add latency to our inference pipeline?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Verification is a single API call with under 50ms p99 latency at enterprise tier. It can run asynchronously post-inference without blocking the user response. The batch verification endpoint handles up to 10,000 documents per request. The C2PA verification logic is also available as an open-source library that runs entirely within your own infrastructure for zero-latency isolation."
      }
    },
    {
      "@type": "Question",
      "name": "We may have fair use or training exemptions under US law. Why license?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The legal landscape is unsettled with active litigation ongoing. Licensing is defensible regardless of how copyright law evolves -- it removes the question entirely. Enterprise customers are now asking about content provenance in security questionnaires, and AI companies that can prove they license content close deals that competitors cannot. The legal exemption argument only addresses the legal risk; licensing addresses both the legal risk and the competitive advantage."
      }
    },
    {
      "@type": "Question",
      "name": "How does this relate to robots.txt and noai directives?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "robots.txt and noai directives apply at crawl time, on the publisher's server. C2PA provenance is embedded in the content itself -- it travels with the text wherever it goes, including content already in your training corpus before any crawl directive existed. A publisher who signs their archive retroactively attaches licensing terms to every copy of that content, on any server. Encypher is not an enforcement mechanism -- it is infrastructure that makes licensing terms machine-readable and verifiable."
      }
    },
    {
      "@type": "Question",
      "name": "What data do you see from our inference calls?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "For verification calls: we receive the text submitted for verification and return provenance metadata. We do not train on your data, do not retain content beyond the verification transaction, and offer a standard data processing agreement at enterprise tier. For performance intelligence: we record that a provenance check occurred, the result, and the timestamp -- not the full content of your AI-generated outputs unless you opt into spread analytics via explicit configuration."
      }
    },
    {
      "@type": "Question",
      "name": "Is this sufficient for EU AI Act compliance?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Encypher's output watermarking is designed to satisfy Article 52(1) transparency obligations -- the requirement that AI-generated content be detectable as such. The C2PA manifest embedded in each output identifies it as AI-generated, records the generation timestamp, and links to the source model. The China watermarking mandate is covered by the same integration under a separate configuration flag. Confirm with your counsel that our implementation satisfies your specific obligations in the jurisdictions where you operate."
      }
    },
    {
      "@type": "Question",
      "name": "How does performance intelligence work if a publisher is not in the coalition yet?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "You can still verify content from publishers who have signed their content independently -- C2PA is an open standard and any publisher can embed provenance metadata. If the content carries a valid C2PA manifest, Encypher can verify it and attribute it to the source, regardless of coalition membership. Coalition membership adds the licensing agreement layer; the provenance verification layer works on any signed content."
      }
    }
  ]
};

/**
 * Page-specific FAQ schema for /solutions/enterprises
 * Must match the visible FAQ accordion content on that page.
 */
export const enterprisesFaqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Does Encypher satisfy court AI disclosure requirements?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Court AI disclosure orders vary significantly by jurisdiction. Most require attorneys to certify that AI-generated content was reviewed and citations were verified. Encypher provides the provenance record that supports such a certification: which passages were AI-generated, when, by which model, and that the document is unmodified since signing. Confirm with ethics counsel that your implementation satisfies the specific orders in your jurisdictions."
      }
    },
    {
      "@type": "Question",
      "name": "How does paragraph-level signing work in a real drafting workflow?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The typical integration is through your AI drafting tool or document management system. When an AI assistant generates a passage, the output is signed via the Encypher API before insertion into the document -- the manifest records the model, timestamp, and generation context. When an attorney writes a passage, it can be signed as human-authored with their credentials. Integration points include REST API, Python and TypeScript SDKs, Word and Google Docs add-ins, and webhook-based CMS integrations."
      }
    },
    {
      "@type": "Question",
      "name": "If an attorney edits an AI-generated paragraph, what does the record show?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The record shows both events. The original AI-generated passage has its own signed manifest with model, timestamp, and generation context. When the attorney edits and re-signs, the updated passage carries the attorney's credentials and a new timestamp -- with the prior AI-generation manifest preserved in the chain. The modification log is tamper-evident, showing precisely what changed and when."
      }
    },
    {
      "@type": "Question",
      "name": "Can opposing counsel or regulators independently verify the provenance claims?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes -- and this is a deliberate design property. The C2PA standard is open and the verification libraries are open source. Any party with the signed document and your organization's public key can independently verify every provenance claim without Encypher's involvement. With BYOK, the signature is against your own certificate, making it much harder to contest than a declaration from a vendor."
      }
    },
    {
      "@type": "Question",
      "name": "Does Encypher see the content of our documents?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "In the standard API integration, document content passes through Encypher's signing service to have provenance metadata embedded. We do not store, train on, or use document content beyond the signing transaction. Enterprise customers receive a standard data processing agreement. For the highest isolation -- appropriate for attorney-client privilege or strict data residency requirements -- Encypher supports on-premises deployment and BYOK configurations where document content never leaves your environment."
      }
    },
    {
      "@type": "Question",
      "name": "How does this integrate with Word, Google Docs, or our DMS?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Encypher provides a REST API and SDKs in Python and TypeScript that integrate into any document workflow. For common document management systems like iManage, NetDocuments, and SharePoint, integration is typically built at the document save or export event. Word and Google Docs add-ins for real-time sentence-level provenance are available for enterprise customers. Contact us to discuss your specific DMS and AI tooling environment."
      }
    },
    {
      "@type": "Question",
      "name": "What happens if we need to prove provenance for documents created before we integrated Encypher?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "For documents created before integration, Encypher supports batch signing of completed documents, which produces a document-level signature recording that the document existed and was unmodified as of the signing date. This provides a tamper-evident record but is weaker than sentence-level provenance. The strongest provenance comes from signing at the point of generation. Contact us to discuss your retroactive requirements."
      }
    }
  ]
};

/**
 * Blog index ItemList schema generator.
 * Pass the filtered post list; optionally pass a tag for tag-filtered views.
 */
export function getBlogListSchema(
  posts: Array<{ title: string; slug: string; date: string; excerpt: string; author?: string; image?: string }>,
  tag?: string
) {
  const listUrl = tag
    ? `${siteConfig.url}/blog?tag=${encodeURIComponent(tag)}`
    : `${siteConfig.url}/blog`;

  return {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": tag ? `Encypher Blog - ${tag}` : "Encypher Blog",
    "description": tag
      ? `Articles about ${tag} from the authors of the C2PA Text Standard.`
      : "From the authors of the C2PA text standard: infrastructure for AI content authentication and licensing.",
    "url": listUrl,
    "itemListElement": posts.slice(0, 10).map((post, i) => ({
      "@type": "ListItem",
      "position": i + 1,
      "item": {
        "@type": "BlogPosting",
        "@id": `${siteConfig.url}/blog/${post.slug}`,
        "headline": post.title,
        "url": `${siteConfig.url}/blog/${post.slug}`,
        "datePublished": post.date,
        "description": post.excerpt,
        ...(post.image ? { "image": post.image } : {}),
        "author": {
          "@type": "Person",
          "name": post.author || "Encypher Team"
        },
        "publisher": {
          "@type": "Organization",
          "name": "Encypher",
          "url": siteConfig.url
        }
      }
    }))
  };
}

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
  aiCompaniesFaqSchema,
  enterprisesFaqSchema,
  getPublisherMetadata,
  getAILabMetadata,
  getEnterpriseMetadata,
  getDemoMetadata,
  generateMetadata,
  getBlogPostSchema,
  getBlogListSchema,
  getWebPageSchema,
  getAISearchSummary,
};