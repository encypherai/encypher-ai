'use client';

import { useEffect } from 'react';

export function useScrollLock(isLocked: boolean) {
  useEffect(() => {
    if (isLocked) {
      // Save current scroll position
      const scrollY = window.scrollY;
      
      // Calculate scrollbar width to prevent content shift
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
      
      // Lock scroll
      document.body.style.overflow = 'hidden';
      document.body.style.position = 'fixed';
      document.body.style.top = `-${scrollY}px`;
      document.body.style.width = '100%';
      document.body.style.paddingRight = `${scrollbarWidth}px`;
      
      return () => {
        // Unlock scroll
        document.body.style.overflow = '';
        document.body.style.position = '';
        document.body.style.top = '';
        document.body.style.width = '';
        document.body.style.paddingRight = '';
        
        // Restore scroll position
        window.scrollTo(0, scrollY);
      };
    }
  }, [isLocked]);
}
