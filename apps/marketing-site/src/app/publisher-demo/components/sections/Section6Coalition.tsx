'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import { trackCTAClick } from '../../lib/analytics';
import CTAButton from '../ui/CTAButton';
import DemoRequestModal from '../ui/DemoRequestModal';
import { FileText, Users, Mail } from 'lucide-react';

interface Section6CoalitionProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

export default function Section6Coalition({ isActive, onComplete, onAnimationStart }: Section6CoalitionProps) {
  const [showModal, setShowModal] = useState(false);
  const [canAnimate, setCanAnimate] = useState(false);
  const [hasCompleted, setHasCompleted] = useState(false);
  
  const { sectionRef } = useSectionScroll({ 
    sectionIndex: 6, 
    isActive,
    onScrollComplete: () => setCanAnimate(true)
  });

  useEffect(() => {
    if (canAnimate && !hasCompleted) {
      onAnimationStart();
      onComplete(); // Final section, mark complete immediately
      setHasCompleted(true);
    }
  }, [canAnimate, hasCompleted, onAnimationStart, onComplete]);

  const handleCTAClick = () => {
    trackCTAClick('primary_demo_request');
    setShowModal(true);
  };

  const handleSecondaryClick = (type: string) => {
    trackCTAClick(type);
  };

  return (
    <section
      ref={sectionRef}
      data-section="6"
      className="min-h-screen flex items-start lg:items-center justify-center px-4 sm:px-6 lg:px-16 pt-4 pb-12 sm:py-16 lg:py-20"
    >
      <div className="max-w-5xl w-full">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isActive ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
        >
          <motion.h2
            className="text-2xl sm:text-3xl md:text-4xl lg:text-6xl font-bold text-slate-900 mb-6 sm:mb-8 text-center"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={isActive ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            First Movers Define the Standard.
          </motion.h2>

          <motion.div
            className="text-base sm:text-lg text-slate-700 space-y-4 sm:space-y-6 mb-8 sm:mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={isActive ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <p className="text-xl">
              A coalition of the world&apos;s leading publishers is forming to make this the non-negotiable standard for AI engagement.
            </p>
            <p>
              Early members don&apos;t just get preferential terms; they co-author the legal and technical precedent for the entire industry.
            </p>
            <p>
              This is not about blocking AI. This is about ensuring that the value created by your content flows back to you. This is about making licensing inevitable, not optional.
            </p>
            <p className="text-xl font-semibold text-slate-900 pt-4">
              The question is not whether this becomes the standard.<br />
              The question is whether you help define it.
            </p>
          </motion.div>

          <motion.div
            className="bg-slate-50 p-8 rounded-lg border border-slate-200 mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={isActive ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <h3 className="text-2xl font-bold text-slate-900 mb-6">Early Coalition Members Receive:</h3>
            <div className="grid md:grid-cols-2 gap-4 text-slate-700">
              <div className="flex items-start gap-3">
                <span className="text-green-400 text-xl">✓</span>
                <span>Preferential pricing on infrastructure</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-400 text-xl">✓</span>
                <span>Input on technical standards development</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-400 text-xl">✓</span>
                <span>Coordinated legal strategy and resources</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-400 text-xl">✓</span>
                <span>Shared intelligence on AI company behavior</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-400 text-xl">✓</span>
                <span>Priority access to licensing marketplace</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-400 text-xl">✓</span>
                <span>Co-marketing and thought leadership opportunities</span>
              </div>
            </div>
          </motion.div>

          <motion.div
            className="flex flex-col items-center gap-8"
            initial={{ opacity: 0, y: 30 }}
            animate={isActive ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.8 }}
          >
            <CTAButton onClick={handleCTAClick} />

            {/* <div className="flex flex-wrap justify-center gap-6 text-sm">
              <button
                onClick={() => handleSecondaryClick('whitepaper')}
                className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors"
              >
                <FileText className="w-4 h-4" />
                Download Technical Whitepaper
              </button>
              <button
                onClick={() => handleSecondaryClick('coalition')}
                className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors"
              >
                <Users className="w-4 h-4" />
                View Coalition Members
              </button>
              <button
                onClick={() => handleSecondaryClick('contact')}
                className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors"
              >
                <Mail className="w-4 h-4" />
                Contact Sales Team
              </button>
            </div> */}
          </motion.div>
        </motion.div>
      </div>

      <AnimatePresence>
        {showModal && (
          <DemoRequestModal onClose={() => setShowModal(false)} />
        )}
      </AnimatePresence>
    </section>
  );
}
