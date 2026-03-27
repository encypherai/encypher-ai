// SEO head for /tools/encode
// Canonical domain: https://encypher.com
export default function Head() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Encypher Sign Tool",
    "applicationCategory": "Utility",
    "operatingSystem": "All",
    "url": "https://encypher.com/tools/sign",
    "description": "Sign text with secure metadata using Encypher's provenance tool. Try Encypher's free online signing tool for digital authenticity.",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    }
  };
  return (
    <>
      <link rel="canonical" href="https://encypher.com/tools/sign" />
      <meta property="og:title" content="Sign Text with Metadata | Encypher Tool" />
      <meta property="og:description" content="Sign text with secure metadata using Encypher's provenance tool. Try Encypher's free online signing tool for digital authenticity." />
      <meta property="og:url" content="https://encypher.com/tools/sign" />
      <meta property="og:type" content="website" />
      <meta property="og:site_name" content="Encypher" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Sign Text with Metadata | Encypher Tool" />
      <meta name="twitter:description" content="Sign text with secure metadata using Encypher's provenance tool. Try Encypher's free online signing tool for digital authenticity." />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
    </>
  );
}
