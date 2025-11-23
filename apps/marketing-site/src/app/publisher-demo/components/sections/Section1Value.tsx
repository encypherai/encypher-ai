'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import { ChevronDown } from 'lucide-react';

interface Section1ValueProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

export default function Section1Value({ isActive, onComplete, onAnimationStart }: Section1ValueProps) {
  const [hasTracked, setHasTracked] = useState(false);
  
  const { sectionRef } = useSectionScroll({ 
    sectionIndex: 1, 
    isActive,
    onScrollComplete: () => {}
  });

  useEffect(() => {
    // Section 1 is immediately visible, so complete it right away
    if (isActive && !hasTracked) {
      onAnimationStart();
      setHasTracked(true);
      onComplete(); // Mark as complete immediately
    }
  }, [isActive, hasTracked, onComplete, onAnimationStart]);

  return (
    <section
      ref={sectionRef}
      data-section="1"
      className="min-h-screen flex items-start lg:items-center justify-center px-4 sm:px-6 lg:px-16 pt-4 pb-12 sm:py-16 lg:py-20"
    >
      <div className="max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          <motion.h1
            className="text-3xl sm:text-4xl md:text-5xl lg:text-7xl font-bold text-slate-900 mb-4 sm:mb-6 leading-tight"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            Your Archive is the Most Valuable Asset You Own.
          </motion.h1>

          <motion.p
            className="text-lg sm:text-xl md:text-2xl lg:text-3xl text-slate-700 mb-8 sm:mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            In the Age of AI, It&apos;s Also Your Greatest Liability & Strategic Risk.
          </motion.p>

          <motion.div
            className="flex flex-col items-center gap-4 text-slate-600"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1 }}
          >
            <p className="text-sm uppercase tracking-wider">Scroll to see how</p>
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
      </div>
    </section>
  );
}
