'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import DemoLayout from './DemoLayout';
import Section1BlindSpot from './sections/Section1BlindSpot';
import Section2BlackHole from './sections/Section2BlackHole';
import Section3Regulatory from './sections/Section3Regulatory';
import Section4Analytics from './sections/Section4Analytics';
import Section5SafeHarbor from './sections/Section5SafeHarbor';
import Section6Integration from './sections/Section6Integration';
import { useScrollProgress } from '../hooks/useScrollProgress';
import { trackEvent } from '../lib/analytics';

export default function AIDemo() {
  const [isMounted, setIsMounted] = useState(false);
  const [activeSection, setActiveSection] = useState(1);
  const [completedSections, setCompletedSections] = useState<Set<number>>(new Set());
  const [isAnimating, setIsAnimating] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const advancingRef = useRef(false);
  const trackedSectionsRef = useRef<Set<number>>(new Set());
  const hasLoadedRef = useRef(false);
  const shouldTrackExitRef = useRef(false);
  const scrollProgress = useScrollProgress();

  // Define callbacks before any conditional returns to maintain hook order
  const handleSectionComplete = useCallback((sectionNumber: number) => {
    // Only track if section hasn't been completed before
    if (!completedSections.has(sectionNumber)) {
      setCompletedSections(prev => new Set(prev).add(sectionNumber));
      
      // Track section completion
      const sectionNames: Record<number, string> = {
        1: 'blind_spot',
        2: 'performance_black_hole',
        3: 'analytics_engine',
        4: 'regulatory_tsunami',
        5: 'technical_safe_harbor',
        6: 'integration_cta',
      };
      
      trackEvent('section_completed', {
        section: sectionNumber,
        sectionName: sectionNames[sectionNumber],
      });
    }
    
    setIsAnimating(false);
  }, [completedSections]);

  const handleAnimationStart = useCallback(() => {
    setIsAnimating(true);
  }, []);

  useEffect(() => {
    setIsMounted(true);
    
    // Check if mobile
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    // Only track load once
    if (!hasLoadedRef.current) {
      hasLoadedRef.current = true;
      trackEvent('ai_demo_loaded', {});
    }

    // Set flag after a delay to indicate real session (not strict mode)
    const timer = setTimeout(() => {
      shouldTrackExitRef.current = true;
    }, 100);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', checkMobile);
      // Only track exit if this is a real unmount (not strict mode)
      if (shouldTrackExitRef.current) {
        trackEvent('ai_demo_exit', {
          timeOnPage: Date.now(),
        });
      }
    };
  }, []); // Empty dependency array - only run on mount/unmount

  // Detect when user scrolls past current section to trigger next
  useEffect(() => {
    const handleScroll = () => {
      if (isAnimating || isTransitioning || advancingRef.current) {
        return; // Don't advance during animation or transition
      }
      
      // Only check for advancement if current section is complete
      if (!completedSections.has(activeSection)) {
        return;
      }

      const currentSection = document.querySelector(`[data-section="${activeSection}"]`);
      if (!currentSection) return;

      const rect = currentSection.getBoundingClientRect();
      // Use more aggressive threshold on mobile (40% vs 50% on desktop)
      const threshold = isMobile ? 0.6 : 0.5;
      const scrolledPastThreshold = rect.bottom < window.innerHeight * threshold;

      // If user scrolled past current section and next section exists
      if (scrolledPastThreshold && activeSection < 6 && !advancingRef.current) {
        const nextSection = activeSection + 1;
        
        // Immediately block further advancements
        advancingRef.current = true;
        setIsTransitioning(true);
        setActiveSection(nextSection);
        
        // Allow transitions again after section has scrolled into view
        setTimeout(() => {
          advancingRef.current = false;
          setIsTransitioning(false);
        }, 1500); // Give time for auto-scroll to complete
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Check initial position
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, [activeSection, completedSections, isAnimating, isTransitioning, isMobile]);

  // Track section progression (only once per section)
  useEffect(() => {
    if (activeSection > 0 && !trackedSectionsRef.current.has(activeSection)) {
      trackedSectionsRef.current.add(activeSection);
      
      const sectionNames: Record<number, string> = {
        1: 'blind_spot',
        2: 'performance_black_hole',
        3: 'analytics_engine',
        4: 'regulatory_tsunami',
        5: 'technical_safe_harbor',
        6: 'integration_cta',
      };
      
      trackEvent('section_reached', {
        section: activeSection,
        sectionName: sectionNames[activeSection],
      });
    }
  }, [activeSection]);

  if (!isMounted) {
    return null;
  }

  return (
    <DemoLayout activeSection={activeSection}>
      <Section1BlindSpot 
        isActive={activeSection === 1}
        onComplete={() => handleSectionComplete(1)}
        onAnimationStart={handleAnimationStart}
      />
      <Section2BlackHole 
        isActive={activeSection === 2}
        onComplete={() => handleSectionComplete(2)}
        onAnimationStart={handleAnimationStart}
      />
      <Section4Analytics 
        isActive={activeSection === 3}
        onComplete={() => handleSectionComplete(3)}
        onAnimationStart={handleAnimationStart}
      />
      <Section3Regulatory 
        isActive={activeSection === 4}
        onComplete={() => handleSectionComplete(4)}
        onAnimationStart={handleAnimationStart}
      />
      <Section5SafeHarbor 
        isActive={activeSection === 5}
        onComplete={() => handleSectionComplete(5)}
        onAnimationStart={handleAnimationStart}
      />
      <Section6Integration 
        isActive={activeSection === 6}
        onComplete={() => handleSectionComplete(6)}
        onAnimationStart={handleAnimationStart}
      />
    </DemoLayout>
  );
}
