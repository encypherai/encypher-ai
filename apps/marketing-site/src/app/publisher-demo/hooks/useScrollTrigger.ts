'use client';

import { useEffect, useState, RefObject } from 'react';

interface UseScrollTriggerOptions {
  threshold?: number;
  rootMargin?: string;
  triggerOnce?: boolean;
}

export function useScrollTrigger(
  ref: RefObject<HTMLElement | null>,
  options: UseScrollTriggerOptions = {}
) {
  const { threshold = 0.3, rootMargin = '-100px', triggerOnce = true } = options;
  const [isVisible, setIsVisible] = useState(false);
  const [hasTriggered, setHasTriggered] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (triggerOnce) {
            setHasTriggered(true);
          }
        } else if (!triggerOnce) {
          setIsVisible(false);
        }
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
  }, [ref, threshold, rootMargin, triggerOnce]);

  return triggerOnce ? hasTriggered : isVisible;
}
