// SEO head for /tools/encode
// Canonical domain: https://encypherai.com
export default function Head() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Encypher Encode Tool",
    "applicationCategory": "Utility",
    "operatingSystem": "All",
    "url": "https://encypherai.com/tools/encode",
    "description": "Embed secure metadata into your text using Unicode variation selectors. Try Encypher's free online encoder tool for digital provenance and authenticity.",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    }
  };
  return (
    <>
      <link rel="canonical" href="https://encypherai.com/tools/encode" />
      <meta property="og:title" content="Encode Text with Metadata | Encypher Tool" />
      <meta property="og:description" content="Embed secure metadata into your text using Unicode variation selectors. Try Encypher's free online encoder tool for digital provenance and authenticity." />
      <meta property="og:url" content="https://encypherai.com/tools/encode" />
      <meta property="og:type" content="website" />
      <meta property="og:site_name" content="Encypher" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="Encode Text with Metadata | Encypher Tool" />
      <meta name="twitter:description" content="Embed secure metadata into your text using Unicode variation selectors. Try Encypher's free online encoder tool for digital provenance and authenticity." />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
    </>
  );
}
