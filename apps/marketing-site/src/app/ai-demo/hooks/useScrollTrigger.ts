import { useState, useEffect, RefObject } from 'react';

interface UseScrollTriggerOptions {
  threshold?: number;
  triggerOnce?: boolean;
  rootMargin?: string;
}

export function useScrollTrigger(
  ref: RefObject<HTMLElement>,
  options: UseScrollTriggerOptions = {}
) {
  const { threshold = 0.3, triggerOnce = false, rootMargin = '0px' } = options;
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (triggerOnce) {
            observer.unobserve(element);
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
      observer.unobserve(element);
    };
  }, [ref, threshold, triggerOnce, rootMargin]);

  return isVisible;
}
