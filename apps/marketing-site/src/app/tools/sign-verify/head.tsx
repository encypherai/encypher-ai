// SEO head for /tools/sign-verify
// Canonical domain: https://encypher.com
export default function Head() {
  const jsonLdSoftware = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Encypher Sign/Verify Tool",
    "applicationCategory": "Utility",
    "operatingSystem": "All",
    "url": "https://encypher.com/tools/sign-verify",
    "description": "Sign or verify secure metadata in your text using Encypher's provenance tool. Free, secure, and privacy-preserving.",
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
        "item": "https://encypher.com/"
      },
      {
        "@type": "ListItem",
        "position": 2,
        "name": "Tools",
        "item": "https://encypher.com/tools"
      },
      {
        "@type": "ListItem",
        "position": 3,
        "name": "Sign/Verify",
        "item": "https://encypher.com/tools/sign-verify"
      }
    ]
  };
  const jsonLdFAQ = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What does the Encypher Sign/Verify Tool do?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "It allows you to sign text with secure metadata or verify authenticity using Unicode variation selectors, supporting digital provenance and authenticity."
        }
      },
      {
        "@type": "Question",
        "name": "Is my data secure and private?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Yes, the tool processes data securely and does not store or share your input. All signing and verification is privacy-preserving."
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
      <link rel="canonical" href="https://encypher.com/tools/sign-verify" />
      <meta property="og:title" content="Encypher Sign/Verify Tool" />
      <meta property="og:description" content="Sign or verify secure metadata in your text using Encypher's provenance tool. Free, secure, and privacy-preserving." />
      <meta property="og:url" content="https://encypher.com/tools/sign-verify" />
      <meta property="og:type" content="website" />
      <meta property="og:site_name" content="Encypher" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Encypher Sign/Verify Tool" />
      <meta name="twitter:description" content="Sign or verify secure metadata in your text using Encypher's provenance tool. Free, secure, and privacy-preserving." />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdSoftware) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdBreadcrumb) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdFAQ) }} />
    </>
  );
}
