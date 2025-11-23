'use client';

import { motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

interface ScrollIndicatorProps {
  delay?: number;
}

export default function ScrollIndicator({ delay = 1 }: ScrollIndicatorProps) {
  return (
    <motion.div
      className="flex flex-col items-center gap-4 text-slate-600 mt-12"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5, delay }}
    >
      <p className="text-sm uppercase tracking-wider">Continue scrolling</p>
      <motion.div
        animate={{
          y: [0, 10, 0],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        <ChevronDown className="w-6 h-6" />
      </motion.div>
    </motion.div>
  );
}
