'use client';

import Script from 'next/script';
import { softwareSchema, organizationSchema, siteConfig } from '@/lib/seo';

interface ScriptsContainerProps {
  isProd: boolean;
}

export function ScriptsContainer({ isProd }: ScriptsContainerProps) {
  return (
    <>
      <link rel="icon" href="/favicon.ico" sizes="any" />
      {isProd && (
        <>
          <Script id="zoho-salesiq-init" strategy="lazyOnload">
            {`window.$zoho=window.$zoho || {};$zoho.salesiq=$zoho.salesiq||{ready:function(){}}`}
          </Script>
          <Script 
            id="zoho-salesiq-widget" 
            src="https://salesiq.zohopublic.com/widget?wc=siq535fe17c163e5051498e6444d7334f27d622b058f7355fc1cf0016f641d26159" 
            strategy="lazyOnload"
          />
          {/* Zoho PageSense Analytics */}
          <Script
            id="zoho-pagesense"
            strategy="lazyOnload"
            dangerouslySetInnerHTML={{
              __html: `(function(w,s){var e=document.createElement('script');e.type='text/javascript';e.async=true;e.src='https://cdn.pagesense.io/js/886080383/e0f74fec7ff6481098f36f9daeb282bf.js';var x=document.getElementsByTagName('script')[0];x.parentNode.insertBefore(e,x);})(window,'script');`
            }}
          />
        </>
      )}
      <Script
        id="schema-software"
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(softwareSchema)
        }}
      />
      <Script
        id="schema-organization"
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(organizationSchema)
        }}
      />
      <Script
        id="schema-website"
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Encypher",
            "url": siteConfig.url,
            "potentialAction": {
              "@type": "SearchAction",
              "target": `${siteConfig.url}/search?q={query}`,
              "query-input": "required name=query"
            }
          })
        }}
      />
    </>
  );
}
