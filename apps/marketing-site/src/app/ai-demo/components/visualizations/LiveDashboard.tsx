'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';

interface LiveDashboardProps {
  isActive: boolean;
}

export default function LiveDashboard({ isActive }: LiveDashboardProps) {
  const [impressions, setImpressions] = useState(0);
  const [engagementRate, setEngagementRate] = useState(0);

  useEffect(() => {
    if (isActive) {
      // Animate impression counter
      const impressionTarget = 2134567;
      const impressionDuration = 2000;
      const impressionSteps = 50;
      const impressionIncrement = impressionTarget / impressionSteps;

      let impressionCount = 0;
      const impressionInterval = setInterval(() => {
        impressionCount += 1;
        if (impressionCount <= impressionSteps) {
          setImpressions(Math.floor(impressionIncrement * impressionCount));
        } else {
          setImpressions(impressionTarget);
          clearInterval(impressionInterval);
        }
      }, impressionDuration / impressionSteps);

      // Animate engagement rate
      const engagementTarget = 23.4;
      const engagementDuration = 2000;
      const engagementSteps = 50;
      const engagementIncrement = engagementTarget / engagementSteps;

      let engagementCount = 0;
      const engagementInterval = setInterval(() => {
        engagementCount += 1;
        if (engagementCount <= engagementSteps) {
          setEngagementRate(Number((engagementIncrement * engagementCount).toFixed(1)));
        } else {
          setEngagementRate(engagementTarget);
          clearInterval(engagementInterval);
        }
      }, engagementDuration / engagementSteps);

      return () => {
        clearInterval(impressionInterval);
        clearInterval(engagementInterval);
      };
    } else {
      setImpressions(0);
      setEngagementRate(0);
    }
  }, [isActive]);

  return (
    <div className="flex flex-col">
      <AnimatePresence>
        {isActive && (
          <div>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-3 sm:mb-4"
            >
              <div className="inline-flex items-center gap-1 sm:gap-2 bg-orange-100 border border-orange-300 rounded px-2 sm:px-3 py-1">
                <span className="text-orange-600 text-sm sm:text-base">🔥</span>
                <span className="text-orange-700 text-[11px] sm:text-xs md:text-sm font-semibold">
                  VIRAL PERFORMANCE DETECTED
                </span>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mb-3 sm:mb-4"
            >
              <div className="text-[11px] sm:text-xs font-semibold text-slate-600 mb-2">Model Configuration:</div>
              {/* Table-like layout for model config */}
              <div className="grid grid-cols-2 gap-x-3 gap-y-1.5 text-[10px] sm:text-xs text-slate-700">
                <div className="flex justify-between">
                  <span className="text-slate-500">Model:</span>
                  <span className="font-mono text-slate-900 text-[9px] sm:text-[10px]">GPT-4-turbo</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Temp:</span>
                  <span className="text-blue-600 font-semibold">0.7</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Top-P:</span>
                  <span className="text-blue-600 font-semibold">0.9</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Context:</span>
                  <span className="text-blue-600 font-semibold">8,192</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mb-3 sm:mb-4"
            >
              <div className="text-[11px] sm:text-xs font-semibold text-slate-600 mb-2">Real-World Engagement:</div>
              {/* Horizontal layout for engagement metrics */}
              <div className="grid grid-cols-3 gap-2 sm:gap-3">
                <div className="text-center">
                  <div className="text-[9px] sm:text-[10px] text-slate-500 mb-1">Impressions</div>
                  <div className="text-sm sm:text-base md:text-lg font-bold text-slate-900">
                    {impressions.toLocaleString()}
                  </div>
                </div>
                <div className="text-center border-x border-slate-200">
                  <div className="text-[9px] sm:text-[10px] text-slate-500 mb-1">Engagement</div>
                  <div className="text-sm sm:text-base md:text-lg font-bold text-green-600">
                    {engagementRate}%
                  </div>
                  <div className="text-[8px] sm:text-[9px] text-slate-500">
                    ↑15.2% avg
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-[9px] sm:text-[10px] text-slate-500 mb-1">Viral Coef.</div>
                  <div className="text-sm sm:text-base md:text-lg font-bold text-blue-600">2.3x</div>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <div className="text-[11px] sm:text-xs font-semibold text-slate-600 mb-2">🎯 Automated Insights:</div>
              <ul className="space-y-1 text-[10px] sm:text-xs text-slate-700">
                <li className="flex items-start gap-1.5">
                  <span className="text-blue-600 flex-shrink-0">•</span>
                  <span>Higher temp (0.7) drove creative phrasing</span>
                </li>
                <li className="flex items-start gap-1.5">
                  <span className="text-blue-600 flex-shrink-0">•</span>
                  <span>Educational tone = 3.2x engagement</span>
                </li>
                <li className="flex items-start gap-1.5">
                  <span className="text-blue-600 flex-shrink-0">•</span>
                  <span>Optimal length: 250-400 words</span>
                </li>
              </ul>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {!isActive && (
        <div className="h-full flex items-center justify-center text-slate-600">
          Waiting for data...
        </div>
      )}
    </div>
  );
}
