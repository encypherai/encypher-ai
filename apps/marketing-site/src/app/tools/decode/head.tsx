// SEO head for /tools/decode
// Canonical domain: https://encypherai.com
export default function Head() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Encypher Verify Tool",
    "applicationCategory": "Utility",
    "operatingSystem": "All",
    "url": "https://encypherai.com/tools/verify",
    "description": "Verify signed text and inspect embedded metadata with Encypher's provenance tool. Free, secure, and privacy-preserving.",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    }
  };
  return (
    <>
      <link rel="canonical" href="https://encypherai.com/tools/verify" />
      <meta property="og:title" content="Verify Signed Text | Encypher Tool" />
      <meta property="og:description" content="Verify signed text and inspect embedded metadata with Encypher's provenance tool. Free, secure, and privacy-preserving." />
      <meta property="og:url" content="https://encypherai.com/tools/verify" />
      <meta property="og:type" content="website" />
      <meta property="og:site_name" content="Encypher" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Verify Signed Text | Encypher Tool" />
      <meta name="twitter:description" content="Verify signed text and inspect embedded metadata with Encypher's provenance tool. Free, secure, and privacy-preserving." />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
    </>
  );
}
