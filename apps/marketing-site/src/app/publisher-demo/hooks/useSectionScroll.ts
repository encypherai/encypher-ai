'use client';

import { useEffect, useRef } from 'react';

interface UseSectionScrollOptions {
  sectionIndex: number;
  isActive: boolean;
  onScrollComplete?: () => void;
}

export function useSectionScroll({ sectionIndex, isActive, onScrollComplete }: UseSectionScrollOptions) {
  const sectionRef = useRef<HTMLElement>(null);
  const hasActivated = useRef(false);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // When section becomes active, auto-scroll to it and start animation
    if (isActive && !hasActivated.current) {
      if (!sectionRef.current) {
        // Retry after a brief delay to allow ref to be set
        setTimeout(() => {
          if (sectionRef.current && !hasActivated.current) {
            activateSection();
          }
        }, 50);
        return;
      }
      
      activateSection();
    }
    
    function activateSection() {
      if (!sectionRef.current) return;
      
      hasActivated.current = true;
      
      // Detect if mobile (< 1024px, matching DemoLayout breakpoint)
      const isMobile = window.innerWidth < 1024;
      
      // Calculate offset based on layout
      let offset: number;
      if (isMobile) {
        // Mobile: navbar (64px) + sticky article (40vh) + small buffer (16px for pt-4)
        const navBarHeight = 64;
        const articleHeight = window.innerHeight * 0.4; // 40vh
        const buffer = 16;
        offset = navBarHeight + articleHeight + buffer;
      } else {
        // Desktop: just navbar height
        offset = 80;
      }
      
      const elementPosition = sectionRef.current.getBoundingClientRect().top + window.scrollY;
      const offsetPosition = elementPosition - offset;
      
      // Smooth scroll with calculated offset
      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth',
      });
      
      // Wait for scroll to complete, then lock position and start animation
      scrollTimeoutRef.current = setTimeout(() => {
        // Ensure we're at the exact position after smooth scroll
        if (sectionRef.current) {
          const finalPosition = sectionRef.current.getBoundingClientRect().top + window.scrollY - offset;
          window.scrollTo({
            top: finalPosition,
            behavior: 'auto', // Instant snap to position
          });
        }
        
        if (onScrollComplete) {
          onScrollComplete();
        }
      }, 1000); // 800ms scroll + 200ms pause
    }
    
    // Reset when section becomes inactive
    if (!isActive) {
      hasActivated.current = false;
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    }
    
    return () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [isActive, sectionIndex]); // onScrollComplete intentionally excluded to prevent timeout cancellation

  return { 
    sectionRef
  };
}
