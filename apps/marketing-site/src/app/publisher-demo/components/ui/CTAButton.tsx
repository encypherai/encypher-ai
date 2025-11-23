'use client';

import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

interface CTAButtonProps {
  onClick: () => void;
}

export default function CTAButton({ onClick }: CTAButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      className="group relative px-12 py-6 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg text-white font-bold text-xl overflow-hidden shadow-2xl"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Glow effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 opacity-0 group-hover:opacity-30 transition-opacity duration-300"
        animate={{
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />

      {/* Button content */}
      <span className="relative flex items-center gap-3">
        Request a Private Briefing
        <motion.div
          animate={{
            x: [0, 5, 0],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          <ArrowRight className="w-6 h-6" />
        </motion.div>
      </span>

      {/* Shimmer effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20"
        initial={{ x: '-100%' }}
        animate={{ x: '200%' }}
        transition={{
          duration: 2,
          repeat: Infinity,
          repeatDelay: 1,
          ease: 'easeInOut',
        }}
      />
    </motion.button>
  );
}
