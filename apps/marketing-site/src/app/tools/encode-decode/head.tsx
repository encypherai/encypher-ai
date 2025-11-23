// Next.js app directory head.tsx for /tools/encode-decode
// Moves all meta/link/script tags from the old <head> in page.tsx

export default function Head() {
  const jsonLdSoftware = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Encypher Encode/Decode Tool",
    "applicationCategory": "Utility",
    "operatingSystem": "All",
    "url": "https://encypherai.com/tools/encode-decode",
    "description": "Embed or extract secure metadata in your text using Encypher's Unicode-powered tool. Free, secure, and privacy-preserving.",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    }
  };
  const jsonLdBreadcrumb = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": "https://encypherai.com/"
      },
      {
        "@type": "ListItem",
        "position": 2,
        "name": "Tools",
        "item": "https://encypherai.com/tools"
      },
      {
        "@type": "ListItem",
        "position": 3,
        "name": "Encode/Decode",
        "item": "https://encypherai.com/tools/encode-decode"
      }
    ]
  };
  const jsonLdFAQ = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What does the Encypher Encode/Decode Tool do?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "It allows you to embed (encode) or extract (decode) secure metadata in text using Unicode variation selectors, supporting digital provenance and authenticity."
        }
      },
      {
        "@type": "Question",
        "name": "Is my data secure and private?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Yes, the tool processes data securely and does not store or share your input. All encoding/decoding is privacy-preserving."
        }
      },
      {
        "@type": "Question",
        "name": "What types of metadata can I embed?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "You can embed model info, timestamps, AI source, and custom key-value pairs for digital provenance and verification."
        }
      }
    ]
  };
  return (
    <>
      <link rel="canonical" href="https://encypherai.com/tools/encode-decode" />
      <meta property="og:title" content="Encypher Encode/Decode Tool" />
      <meta property="og:description" content="Embed or extract secure metadata in your text using Encypher's Unicode-powered tool. Free, secure, and privacy-preserving." />
      <meta property="og:url" content="https://encypherai.com/tools/encode-decode" />
      <meta property="og:type" content="website" />
      <meta property="og:site_name" content="Encypher" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Encypher Encode/Decode Tool" />
      <meta name="twitter:description" content="Embed or extract secure metadata in your text using Encypher's Unicode-powered tool. Free, secure, and privacy-preserving." />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdSoftware) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdBreadcrumb) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdFAQ) }} />
    </>
  );
}
