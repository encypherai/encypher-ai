'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import { useScrollLock } from '../../hooks/useScrollLock';
import FlowchartAnimation from '../animations/FlowchartAnimation';
import { ChevronDown } from 'lucide-react';

interface Section5LegalRealityProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

export default function Section5LegalReality({ isActive, onComplete, onAnimationStart }: Section5LegalRealityProps) {
  const [showContent, setShowContent] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [canAnimate, setCanAnimate] = useState(false);
  
  const { sectionRef } = useSectionScroll({ 
    sectionIndex: 5, 
    isActive,
    onScrollComplete: () => setCanAnimate(true)
  });
  
  useScrollLock(isAnimating);

  useEffect(() => {
    if (canAnimate && !showContent) {
      onAnimationStart();
      setIsAnimating(true);
      
      setTimeout(() => {
        setShowContent(true);
      }, 300);

      // Unlock scroll after 1 second
      setTimeout(() => {
        setIsAnimating(false);
      }, 1000);

      // Complete animation sequence
      setTimeout(() => {
        onComplete(); // Mark section as complete
      }, 4500);
    }
  }, [canAnimate, onComplete, onAnimationStart]);

  return (
    <section
      ref={sectionRef}
      data-section="5"
      className="min-h-screen flex items-start lg:items-center justify-center px-4 sm:px-6 lg:px-16 pt-4 pb-12 sm:py-16 lg:py-20"
    >
      <div className="max-w-6xl w-full">
        <AnimatePresence mode="wait">
          {showContent && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <motion.h2
                className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-slate-900 mb-4 text-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                From Discovery Hell to Inevitable Revenue.
              </motion.h2>

              <motion.p
                className="text-base sm:text-lg md:text-xl text-slate-700 mb-8 sm:mb-12 text-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                This is the new legal framework for the AI economy.<br />
                It is built on the mathematical certainty of our infrastructure.
              </motion.p>

              <FlowchartAnimation />

              <motion.div
                className="mt-12 p-8 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border border-blue-200"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 2 }}
              >
                <h3 className="text-2xl font-bold text-slate-900 mb-4">
                  The Mathematical Certainty of Provenance
                </h3>
                <div className="grid md:grid-cols-2 gap-6 text-slate-700">
                  <div>
                    <h4 className="font-semibold text-red-600 mb-2">Traditional Copyright:</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• Burden on plaintiff to prove use</li>
                      <li>• Requires forensic analysis</li>
                      <li>• Defendant can claim ignorance</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold text-green-600 mb-2">With Encypher:</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• Cryptographic proof of notice delivery</li>
                      <li>• Timestamped, immutable record</li>
                      <li>• Defendant must prove they didn&apos;t receive notice</li>
                    </ul>
                  </div>
                </div>
                <p className="mt-6 text-xl font-semibold text-slate-900 text-center">
                  With mathematical proof as the foundation, content licensing is no longer a negotiation, it&apos;s an accounts receivable process
                </p>
              </motion.div>
              
              {/* Scroll to continue indicator */}
              <motion.div
                className="flex flex-col items-center gap-4 text-slate-600 mt-12"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5, delay: 2.5 }}
              >
                <p className="text-sm uppercase tracking-wider">Continue scrolling</p>
                <motion.div
                  animate={{
                    y: [0, 10, 0],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                >
                  <ChevronDown className="w-8 h-8" />
                </motion.div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}
