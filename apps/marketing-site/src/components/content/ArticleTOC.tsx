'use client';

import { useEffect, useState, useRef } from 'react';

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

interface TOCItem {
  id: string;
  text: string;
}

export function ArticleTOC() {
  const [items, setItems] = useState<TOCItem[]>([]);
  const [activeId, setActiveId] = useState<string>('');
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    // Find all h2 elements within the article content
    const headings = document.querySelectorAll('h2');
    const tocItems: TOCItem[] = [];

    headings.forEach((heading) => {
      const text = heading.textContent?.trim();
      if (!text) return;

      // Add id if missing
      if (!heading.id) {
        heading.id = slugify(text);
      }

      tocItems.push({ id: heading.id, text });
    });

    setItems(tocItems);

    // Set up IntersectionObserver for active section tracking
    observerRef.current = new IntersectionObserver(
      (entries) => {
        // Find the first heading that is intersecting or above the viewport
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);

        if (visible.length > 0) {
          setActiveId(visible[0].target.id);
        }
      },
      { rootMargin: '-80px 0px -60% 0px', threshold: 0 }
    );

    headings.forEach((heading) => {
      if (heading.id) observerRef.current?.observe(heading);
    });

    return () => observerRef.current?.disconnect();
  }, []);

  if (items.length < 3) return null;

  return (
    <nav
      className="hidden xl:block sticky top-24 self-start w-48 flex-shrink-0"
      aria-label="Table of contents"
    >
      <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
        On this page
      </p>
      <ul className="space-y-1.5 border-l border-border pl-3">
        {items.map((item) => (
          <li key={item.id}>
            <a
              href={`#${item.id}`}
              onClick={(e) => {
                e.preventDefault();
                document.getElementById(item.id)?.scrollIntoView({ behavior: 'smooth' });
              }}
              className={`block text-xs leading-snug py-0.5 transition-colors ${
                activeId === item.id
                  ? 'text-foreground font-medium'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {item.text}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
