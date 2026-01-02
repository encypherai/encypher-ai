import React from 'react';
import Script from 'next/script';

export interface FAQItem {
  question: string;
  answer: string;
}

export interface AISummaryProps {
  title: string;
  whatWeDo: string;
  whoItsFor: string;
  keyDifferentiator: string;
  primaryValue: string;
  /** Optional page-specific FAQ items for schema.org FAQPage */
  faq?: FAQItem[];
  /** Optional page path for canonical reference */
  pagePath?: string;
  /** Optional page type for schema.org (default: WebPage) */
  pageType?: 'WebPage' | 'AboutPage' | 'ContactPage' | 'FAQPage' | 'ProductPage' | 'CollectionPage';
}

/**
 * AI-optimized summary component for search engines and AI crawlers.
 * Renders hidden semantic content + JSON-LD structured data.
 * 
 * Best practices implemented:
 * - Hidden div with data-ai-summary for crawler extraction
 * - JSON-LD WebPage schema with mainEntity
 * - Optional FAQ schema for rich snippets
 * - Semantic HTML structure
 */
export function AISummary({ 
  title, 
  whatWeDo, 
  whoItsFor, 
  keyDifferentiator, 
  primaryValue,
  faq,
  pagePath,
  pageType = 'WebPage'
}: AISummaryProps) {
  const baseUrl = 'https://encypherai.com';
  const pageUrl = pagePath ? `${baseUrl}${pagePath}` : baseUrl;

  // WebPage schema with AI-friendly properties
  const webPageSchema = {
    "@context": "https://schema.org",
    "@type": pageType,
    "name": title,
    "description": whatWeDo,
    "url": pageUrl,
    "provider": {
      "@type": "Organization",
      "name": "Encypher",
      "url": baseUrl
    },
    "mainEntity": {
      "@type": "Thing",
      "name": "Encypher",
      "description": whatWeDo,
      "additionalProperty": [
        {
          "@type": "PropertyValue",
          "name": "Target Audience",
          "value": whoItsFor
        },
        {
          "@type": "PropertyValue",
          "name": "Key Differentiator",
          "value": keyDifferentiator
        },
        {
          "@type": "PropertyValue",
          "name": "Primary Value",
          "value": primaryValue
        }
      ]
    }
  };

  // FAQ schema if FAQ items provided
  const faqSchema = faq && faq.length > 0 ? {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faq.map(item => ({
      "@type": "Question",
      "name": item.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": item.answer
      }
    }))
  } : null;

  return (
    <>
      {/* Hidden semantic content for AI crawlers */}
      <div 
        style={{ display: 'none' }} 
        data-ai-summary="true"
        aria-hidden="true"
        itemScope
        itemType={`https://schema.org/${pageType}`}
      >
        <h1 itemProp="name">{title}</h1>
        <meta itemProp="url" content={pageUrl} />
        <div itemProp="description">
          <p><strong>What Encypher does:</strong> {whatWeDo}</p>
          <p><strong>Who it's for:</strong> {whoItsFor}</p>
          <p><strong>Key differentiator:</strong> {keyDifferentiator}</p>
          <p><strong>Primary value:</strong> {primaryValue}</p>
        </div>
        {faq && faq.length > 0 && (
          <div data-ai-faq="true">
            <h2>Frequently Asked Questions</h2>
            {faq.map((item, index) => (
              <div key={index} itemScope itemType="https://schema.org/Question">
                <h3 itemProp="name">{item.question}</h3>
                <div itemScope itemType="https://schema.org/Answer" itemProp="acceptedAnswer">
                  <p itemProp="text">{item.answer}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* JSON-LD structured data */}
      <Script
        id={`ai-summary-schema-${title.replace(/\s+/g, '-').toLowerCase()}`}
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(webPageSchema) }}
      />
      {faqSchema && (
        <Script
          id={`ai-faq-schema-${title.replace(/\s+/g, '-').toLowerCase()}`}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
        />
      )}
    </>
  );
}

export default AISummary;
