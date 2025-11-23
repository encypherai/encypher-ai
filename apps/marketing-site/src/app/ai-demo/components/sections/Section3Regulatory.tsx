'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import { useScrollLock } from '../../hooks/useScrollLock';
import ScrollIndicator from '../ui/ScrollIndicator';

interface Section3RegulatoryProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

const regulations = [
  {
    region: 'EU',
    flag: '🇪🇺',
    name: 'EU AI Act',
    penalty: '€35M or 7% revenue',
    color: 'from-blue-500 to-indigo-500',
  },
  {
    region: 'China',
    flag: '🇨🇳',
    name: 'Watermarking Mandate',
    penalty: 'Business suspension',
    color: 'from-red-500 to-orange-500',
  },
  {
    region: 'California',
    flag: '🇺🇸',
    name: 'AB-2013',
    penalty: '$5K/violation',
    color: 'from-cyan-500 to-blue-500',
  },
  {
    region: 'Italy',
    flag: '🇮🇹',
    name: 'Transparency Law',
    penalty: 'GDPR-level fines',
    color: 'from-green-500 to-emerald-500',
  },
];

export default function Section3Regulatory({ isActive, onComplete, onAnimationStart }: Section3RegulatoryProps) {
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [isAnimating, setIsAnimating] = useState(false);
  const [canAnimate, setCanAnimate] = useState(false);
  const [hasBeenActive, setHasBeenActive] = useState(false);

  const { sectionRef } = useSectionScroll({
    sectionIndex: 4,
    isActive,
    onScrollComplete: () => setCanAnimate(true)
  });

  useEffect(() => {
    if (canAnimate && highlightedIndex === -1) {
      console.log('[Section3] Starting animation');
      onAnimationStart();
      setIsAnimating(true);
      
      // Start regulation highlighting sequence
      let index = 0;
      const interval = setInterval(() => {
        if (index < regulations.length) {
          setHighlightedIndex(index);
          
          // Scroll to show the highlighted regulation card (especially important on mobile)
          setTimeout(() => {
            const card = document.querySelector(`[data-regulation-index="${index}"]`);
            if (card) {
              card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          }, 100);
          
          index++;
        } else {
          clearInterval(interval);
          // Complete after highlighting sequence
          setTimeout(() => {
            console.log('[Section3] Animation complete');
            setIsAnimating(false);
            onComplete();
          }, 200);
        }
      }, 600);
    }
  }, [canAnimate, highlightedIndex, onComplete, onAnimationStart]);

  // Track if section has ever been active
  useEffect(() => {
    if (isActive && !hasBeenActive) {
      setHasBeenActive(true);
    }
  }, [isActive, hasBeenActive]);

  // Debug logging
  useEffect(() => {
    console.log('[Section3] isActive changed:', isActive);
  }, [isActive]);
  
  // Lock scroll during animation
  useScrollLock(isAnimating);

  return (
    <section 
      ref={sectionRef}
      data-section="4" 
      className="min-h-screen flex items-center px-4 sm:px-6 md:px-8 py-12 sm:py-16 md:py-20 bg-gradient-to-br from-slate-50 via-white to-slate-100 scroll-mt-0"
    >
      <div className="max-w-7xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0 }}
          animate={(isActive || hasBeenActive) ? { opacity: 1 } : { opacity: 0 }}
          className="mb-12"
        >
          <h2 className="text-4xl md:text-6xl font-bold text-slate-900 mb-6">
            Four Continents. Seven Regulations.{' '}
            <span className="text-red-600">Zero Excuses.</span>
          </h2>
          <p className="text-xl text-slate-600">
            While you were optimizing benchmarks, <span className="text-red-600 font-semibold">the legal landscape changed</span>.
          </p>
        </motion.div>

        {/* Regulatory Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          {regulations.map((reg, index) => (
            <motion.div
              key={reg.region}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={
                highlightedIndex >= index
                  ? { opacity: 1, scale: 1 }
                  : { opacity: 0.3, scale: 0.9 }
              }
              transition={{ duration: 0.5 }}
              className="relative"
              data-regulation-index={index}
            >
              <div
                className={`bg-white border rounded-lg p-6 shadow-lg ${
                  highlightedIndex === index
                    ? 'border-blue-400 shadow-blue-200'
                    : 'border-slate-200'
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="text-4xl mb-2">{reg.flag}</div>
                    <h3 className="text-xl font-bold text-slate-900">{reg.name}</h3>
                  </div>
                  {highlightedIndex === index && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-3 h-3 rounded-full bg-green-500"
                    />
                  )}
                </div>
                <div className="text-slate-600 mb-2">{reg.region}</div>
                <div className="text-red-600 font-semibold">
                  Penalty: {reg.penalty}
                </div>
              </div>

              {highlightedIndex === index && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className={`absolute -inset-px bg-gradient-to-r ${reg.color} opacity-20 rounded-lg -z-10 blur-xl`}
                />
              )}
            </motion.div>
          ))}
        </div>

        {/* Body Text */}
        {highlightedIndex >= regulations.length - 1 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="max-w-3xl"
          >
            <p className="text-lg text-slate-700 mb-4">
              These regulations are <strong className="text-green-600 font-bold">LIVE</strong>. There's no other infrastructure for compliance that also provides business value.
            </p>
            <p className="text-lg text-slate-700">
              We are the only text watermarking solution that meets ALL requirements, works with publisher infrastructure, and provides massive R&D value beyond compliance.
            </p>
            <div className="mt-8">
              <ScrollIndicator delay={0.8} />
            </div>
          </motion.div>
        )}
      </div>
    </section>
  );
}
