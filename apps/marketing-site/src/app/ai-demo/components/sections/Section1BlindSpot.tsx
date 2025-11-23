'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import ScrollIndicator from '../ui/ScrollIndicator';

interface Section1BlindSpotProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

export default function Section1BlindSpot({ isActive, onComplete, onAnimationStart }: Section1BlindSpotProps) {
  const [hasBeenActive, setHasBeenActive] = useState(false);
  
  const { sectionRef } = useSectionScroll({
    sectionIndex: 1,
    isActive,
    onScrollComplete: () => {}
  });

  // Track if section has ever been active
  useEffect(() => {
    if (isActive && !hasBeenActive) {
      setHasBeenActive(true);
    }
  }, [isActive, hasBeenActive]);

  // Mark Section 1 as complete immediately on mount
  useEffect(() => {
    console.log('[Section1] Marking as complete immediately');
    onAnimationStart();
    // Complete after brief delay to allow fade-in
    const timer = setTimeout(() => {
      console.log('[Section1] Animation complete');
      onComplete();
    }, 800);
    
    return () => clearTimeout(timer);
  }, []); // Empty deps - run once on mount

  // Debug logging
  useEffect(() => {
    console.log('[Section1] isActive changed:', isActive);
  }, [isActive]);

  return (
    <section 
      ref={sectionRef}
      data-section="1" 
      className="min-h-screen flex items-center px-4 sm:px-6 md:px-8 py-12 sm:py-16 md:py-20 bg-gradient-to-br from-slate-50 via-white to-slate-100 scroll-mt-0"
    >
      <div className="max-w-4xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={(isActive || hasBeenActive) ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-7xl font-bold text-slate-900 mb-4 sm:mb-6">
            AI Labs Spend{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-600">
              $2.7 Billion
            </span>{' '}
            Per Model.
          </h1>

          <p className="text-lg sm:text-xl md:text-2xl lg:text-3xl text-slate-600 mb-8 sm:mb-12">
            They have zero performance analytics.
          </p>

          <ScrollIndicator delay={0.8} />
        </motion.div>
      </div>
    </section>
  );
}
