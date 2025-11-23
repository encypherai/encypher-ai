'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import { useScrollLock } from '../../hooks/useScrollLock';
import ScrollIndicator from '../ui/ScrollIndicator';
import LiveDashboard from '../visualizations/LiveDashboard';

interface Section4AnalyticsProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

export default function Section4Analytics({ isActive, onComplete, onAnimationStart }: Section4AnalyticsProps) {
  const [showDashboard, setShowDashboard] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [canAnimate, setCanAnimate] = useState(false);
  const [hasBeenActive, setHasBeenActive] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  const { sectionRef } = useSectionScroll({
    sectionIndex: 3,
    isActive,
    onScrollComplete: () => setCanAnimate(true)
  });

  // Check if mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    if (canAnimate && !showDashboard) {
      console.log('[Section4] Starting animation');
      onAnimationStart();
      setIsAnimating(true);
      setShowDashboard(true);
      
      // Complete immediately - no animation needed for "no data" state
      setTimeout(() => {
        console.log('[Section4] Animation complete');
        setIsAnimating(false);
        onComplete();
      }, 800);
    }
  }, [canAnimate, showDashboard, onComplete, onAnimationStart]);

  // Track if section has ever been active
  useEffect(() => {
    if (isActive && !hasBeenActive) {
      setHasBeenActive(true);
    }
  }, [isActive, hasBeenActive]);

  // Debug logging
  useEffect(() => {
    console.log('[Section4] isActive changed:', isActive);
  }, [isActive]);
  
  // Lock scroll during animation
  useScrollLock(isAnimating);

  return (
    <section 
      ref={sectionRef}
      data-section="3" 
      className="min-h-screen flex items-center px-4 sm:px-6 md:px-8 py-12 sm:py-16 md:py-20 bg-gradient-to-br from-slate-50 via-white to-slate-100 scroll-mt-0"
    >
      <div className="max-w-4xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0 }}
          animate={(isActive || hasBeenActive) ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: 0.8 }}
        >
            <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-6xl font-bold text-slate-900 mb-4 sm:mb-6">
              This Is{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-600">
                "Google Analytics" 
              </span>{' '}
              for AI.
            </h2>

            <p className="text-base sm:text-lg md:text-xl text-slate-600 mb-6 sm:mb-8">
              Compliance is the baseline. <span className="text-blue-600 font-semibold">Intelligence is the opportunity</span>.
            </p>

            {/* Mobile Dashboard - Embedded below title */}
            {isMobile && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={(isActive || hasBeenActive) ? { opacity: 1, y: 0 } : { opacity: 0, y: -20 }}
                transition={{ duration: 0.6 }}
                className="mb-6 sm:mb-8 border border-slate-200 rounded-xl bg-white shadow-lg p-3 sm:p-4"
              >
                <LiveDashboard isActive={isActive} />
              </motion.div>
            )}

            <div className="space-y-4 sm:space-y-6 mb-6 sm:mb-8">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={showDashboard ? { opacity: 1, x: 0 } : { opacity: 0, x: -20 }}
                transition={{ delay: 0.3 }}
                className="bg-white border border-slate-200 rounded-lg p-4 sm:p-5 md:p-6 shadow-lg"
              >
                <h3 className="text-sm sm:text-base md:text-lg font-semibold text-slate-900 mb-2 sm:mb-3">
                  When users engage with AI content anywhere
                </h3>
                <ul className="space-y-1.5 sm:space-y-2 text-xs sm:text-sm md:text-base text-slate-700">
                  <li className="flex items-start gap-1.5 sm:gap-2">
                    <span className="text-green-600 flex-shrink-0">✓</span>
                    <span>Exact model ID and version</span>
                  </li>
                  <li className="flex items-start gap-1.5 sm:gap-2">
                    <span className="text-green-600 flex-shrink-0">✓</span>
                    <span>All parameter settings (temp, top-p, etc.)</span>
                  </li>
                  <li className="flex items-start gap-1.5 sm:gap-2">
                    <span className="text-green-600 flex-shrink-0">✓</span>
                    <span>Context window size and usage</span>
                  </li>
                  <li className="flex items-start gap-1.5 sm:gap-2">
                    <span className="text-green-600 flex-shrink-0">✓</span>
                    <span>Use case and content type</span>
                  </li>
                </ul>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={showDashboard ? { opacity: 1, x: 0 } : { opacity: 0, x: -20 }}
                transition={{ delay: 0.6 }}
                className="bg-white border border-slate-200 rounded-lg p-4 sm:p-5 md:p-6 shadow-lg"
              >
                <h3 className="text-sm sm:text-base md:text-lg font-semibold text-slate-900 mb-2 sm:mb-3">
                  We measure real-world performance
                </h3>
                <ul className="space-y-1.5 sm:space-y-2 text-xs sm:text-sm md:text-base text-slate-700">
                  <li className="flex items-start gap-1.5 sm:gap-2">
                    <span className="text-blue-600 flex-shrink-0">✓</span>
                    <span>Engagement rates across platforms</span>
                  </li>
                  <li className="flex items-start gap-1.5 sm:gap-2">
                    <span className="text-blue-600 flex-shrink-0">✓</span>
                    <span>Time to viral (or time to ignore)</span>
                  </li>
                  <li className="flex items-start gap-1.5 sm:gap-2">
                    <span className="text-blue-600 flex-shrink-0">✓</span>
                    <span>A/B test model versions in production</span>
                  </li>
                  <li className="flex items-start gap-1.5 sm:gap-2">
                    <span className="text-blue-600 flex-shrink-0">✓</span>
                    <span>Parameter impact analysis</span>
                  </li>
                </ul>
              </motion.div>
            </div>

            <motion.p
              initial={{ opacity: 0 }}
              animate={showDashboard ? { opacity: 1 } : { opacity: 0 }}
              transition={{ delay: 0.9 }}
              className="text-sm sm:text-base md:text-lg text-slate-700"
            >
              This feedback loop is what AI labs have been missing to qualify thier $2.7B+ in R&D spend per model.
              <br />
              <strong className="text-slate-900">
                With Encypher, optimize for what actually matters: user engagement. This is your competitive advantage.
              </strong>
            </motion.p>
            <div className="mt-6 sm:mt-8">
              <ScrollIndicator delay={1.2} />
            </div>
        </motion.div>
      </div>
    </section>
  );
}
