// SEO head for /tools/decode
// Canonical domain: https://encypherai.com
export default function Head() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Encypher Decode Tool",
    "applicationCategory": "Utility",
    "operatingSystem": "All",
    "url": "https://encypherai.com/tools/decode",
    "description": "Extract and verify embedded metadata from text using Encypher's Unicode-powered decoder. Free, secure, and privacy-preserving.",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    }
  };
  return (
    <>
      <link rel="canonical" href="https://encypherai.com/tools/decode" />
      <meta property="og:title" content="Decode Metadata from Text | Encypher Tool" />
      <meta property="og:description" content="Extract and verify embedded metadata from text using Encypher's Unicode-powered decoder. Free, secure, and privacy-preserving." />
      <meta property="og:url" content="https://encypherai.com/tools/decode" />
      <meta property="og:type" content="website" />
      <meta property="og:site_name" content="Encypher" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Decode Metadata from Text | Encypher Tool" />
      <meta name="twitter:description" content="Extract and verify embedded metadata from text using Encypher's Unicode-powered decoder. Free, secure, and privacy-preserving." />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
    </>
  );
}
