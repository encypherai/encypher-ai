'use client';

import { ReactNode, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import EmptyDashboard from './visualizations/EmptyDashboard';
import LiveDashboard from './visualizations/LiveDashboard';

interface VisualizationAreaProps {
  activeSection?: number;
  className?: string;
}

export default function VisualizationArea({ activeSection = 1, className = '' }: VisualizationAreaProps) {
  const [currentViz, setCurrentViz] = useState<'empty' | 'live'>('empty');

  useEffect(() => {
    // Switch to live dashboard when reaching section 3 (Analytics Engine - now in position 3)
    if (activeSection >= 3) {
      setCurrentViz('live');
    } else {
      setCurrentViz('empty');
    }
  }, [activeSection]);

  return (
    <motion.div
      className={`h-full ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <div className="relative h-full rounded-xl bg-white border border-slate-200 shadow-lg p-3 sm:p-4 md:p-6">
        {currentViz === 'empty' ? (
          <EmptyDashboard />
        ) : (
          <LiveDashboard isActive={activeSection >= 3} />
        )}
      </div>
    </motion.div>
  );
}
