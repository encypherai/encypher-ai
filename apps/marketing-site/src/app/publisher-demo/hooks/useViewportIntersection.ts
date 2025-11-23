'use client';

import { useEffect, useState, RefObject } from 'react';

interface UseViewportIntersectionOptions {
  threshold?: number | number[];
  rootMargin?: string;
}

export function useViewportIntersection(
  ref: RefObject<HTMLElement | null>,
  options: UseViewportIntersectionOptions = {}
) {
  const { threshold = 0, rootMargin = '0px' } = options;
  const [entry, setEntry] = useState<IntersectionObserverEntry | null>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setEntry(entry);
      },
      {
        threshold,
        rootMargin,
      }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [ref, threshold, rootMargin]);

  return {
    isIntersecting: entry?.isIntersecting ?? false,
    intersectionRatio: entry?.intersectionRatio ?? 0,
    entry,
  };
}
