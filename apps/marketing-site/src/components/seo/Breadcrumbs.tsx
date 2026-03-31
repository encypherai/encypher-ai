import React from 'react';
import Link from 'next/link';
import Script from 'next/script';

interface BreadcrumbItem {
  name: string;
  href: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

/**
 * Breadcrumbs component with both visible UI and BreadcrumbList JSON-LD schema.
 * Use on all hierarchical pages (pillar > cluster > format).
 */
export function Breadcrumbs({ items }: BreadcrumbsProps) {
  const baseUrl = 'https://encypher.com';

  const schema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": items.map((item, index) => ({
      "@type": "ListItem",
      "position": index + 1,
      "name": item.name,
      "item": `${baseUrl}${item.href}`,
    })),
  };

  return (
    <>
      <nav aria-label="Breadcrumb" className="text-sm text-muted-foreground mb-6">
        <ol className="flex items-center gap-1.5 flex-wrap">
          {items.map((item, index) => (
            <li key={item.href} className="flex items-center gap-1.5">
              {index > 0 && <span aria-hidden="true">/</span>}
              {index === items.length - 1 ? (
                <span className="font-medium text-foreground" aria-current="page">
                  {item.name}
                </span>
              ) : (
                <Link href={item.href} className="hover:text-foreground transition-colors">
                  {item.name}
                </Link>
              )}
            </li>
          ))}
        </ol>
      </nav>
      <Script
        id={`breadcrumbs-${items.map(i => i.name).join('-').replace(/\s+/g, '-').toLowerCase()}`}
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />
    </>
  );
}

export default Breadcrumbs;
