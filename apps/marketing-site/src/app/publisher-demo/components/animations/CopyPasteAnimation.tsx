'use client';

import { motion } from 'framer-motion';
import { Copy } from 'lucide-react';

export default function CopyPasteAnimation() {
  return (
    <div className="relative flex items-center justify-center h-32">
      {/* Cursor */}
      <motion.div
        className="absolute left-0"
        initial={{ x: 0, y: 0, opacity: 0 }}
        animate={{
          x: [0, 200, 200],
          y: [0, 0, 0],
          opacity: [0, 1, 1],
        }}
        transition={{
          duration: 1.5,
          times: [0, 0.5, 1],
          ease: 'easeInOut',
        }}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
          <path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z" />
        </svg>
      </motion.div>

      {/* Copy icon flash */}
      <motion.div
        className="absolute left-[200px]"
        initial={{ scale: 0, opacity: 0 }}
        animate={{
          scale: [0, 1.2, 1, 1.2, 1, 1.2, 1],
          opacity: [0, 1, 1, 1, 1, 1, 0],
        }}
        transition={{
          duration: 1.5,
          delay: 1.5,
          times: [0, 0.15, 0.3, 0.45, 0.6, 0.75, 1],
        }}
      >
        <Copy className="w-8 h-8 text-blue-400" />
      </motion.div>

      {/* Text block flying */}
      <motion.div
        className="absolute left-[200px] bg-slate-700 p-3 rounded shadow-lg max-w-xs text-xs text-slate-300"
        initial={{ x: 0, y: 0, opacity: 0, scale: 0.8 }}
        animate={{
          x: [0, 300],
          y: [0, -20],
          opacity: [0, 1, 1, 0],
          scale: [0.8, 1, 1, 0.9],
        }}
        transition={{
          duration: 1.2,
          delay: 3,
          ease: [0.43, 0.13, 0.23, 0.96],
        }}
      >
        Recent data from the International Climate Research Institute reveals...
      </motion.div>
    </div>
  );
}
