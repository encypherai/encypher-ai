'use client';

import { useEffect, useState, useRef } from 'react';
import DemoLayout from './DemoLayout';
import Section1Value from './sections/Section1Value';
import Section2Loophole from './sections/Section2Loophole';
import Section3Notice from './sections/Section3Notice';
import Section4BurdenShift from './sections/Section4BurdenShift';
import Section5LegalReality from './sections/Section5LegalReality';
import Section6Coalition from './sections/Section6Coalition';
import { useScrollProgress } from '../hooks/useScrollProgress';
import { trackEvent } from '../lib/analytics';

export default function PublisherDemo() {
  const [isMounted, setIsMounted] = useState(false);
  const [activeSection, setActiveSection] = useState(1);
  const [completedSections, setCompletedSections] = useState<Set<number>>(new Set());
  const [isAnimating, setIsAnimating] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const advancingRef = useRef(false);
  const trackedSectionsRef = useRef<Set<number>>(new Set());
  const hasLoadedRef = useRef(false);
  const scrollProgress = useScrollProgress();

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
      trackEvent('publisher_demo_loaded', {});
    }

    return () => {
      window.removeEventListener('resize', checkMobile);
      trackEvent('publisher_demo_exit', {
        scrollProgress,
        timeOnPage: Date.now(),
      });
    };
  }, []);

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
        1: 'value_vulnerability',
        2: 'loophole_demonstration',
        3: 'c2pa_infrastructure',
        4: 'burden_shift',
        5: 'legal_reality',
        6: 'coalition_cta',
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

  const handleSectionComplete = (sectionNumber: number) => {
    // Only track if section hasn't been completed before
    if (!completedSections.has(sectionNumber)) {
      setCompletedSections(prev => new Set(prev).add(sectionNumber));
      
      // Track section completion
      const sectionNames: Record<number, string> = {
        1: 'value_vulnerability',
        2: 'loophole_demonstration',
        3: 'c2pa_infrastructure',
        4: 'burden_shift',
        5: 'legal_reality',
        6: 'coalition_cta',
      };
      
      trackEvent('section_completed', {
        section: sectionNumber,
        sectionName: sectionNames[sectionNumber],
      });
    }
    
    setIsAnimating(false);
  };

  const handleAnimationStart = () => {
    setIsAnimating(true);
  };

  return (
    <DemoLayout activeSection={activeSection}>
      <Section1Value 
        isActive={activeSection === 1}
        onComplete={() => handleSectionComplete(1)}
        onAnimationStart={handleAnimationStart}
      />
      <Section2Loophole 
        isActive={activeSection === 2}
        onComplete={() => handleSectionComplete(2)}
        onAnimationStart={handleAnimationStart}
      />
      <Section3Notice 
        isActive={activeSection === 3}
        onComplete={() => handleSectionComplete(3)}
        onAnimationStart={handleAnimationStart}
      />
      <Section4BurdenShift 
        isActive={activeSection === 4}
        onComplete={() => handleSectionComplete(4)}
        onAnimationStart={handleAnimationStart}
      />
      <Section5LegalReality 
        isActive={activeSection === 5}
        onComplete={() => handleSectionComplete(5)}
        onAnimationStart={handleAnimationStart}
      />
      <Section6Coalition 
        isActive={activeSection === 6}
        onComplete={() => handleSectionComplete(6)}
        onAnimationStart={handleAnimationStart}
      />
    </DemoLayout>
  );
}
