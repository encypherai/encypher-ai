'use client';

import { motion } from 'framer-motion';

export default function EmptyDashboard() {
  return (
    <div className="h-full flex flex-col">
      <div className="text-slate-600 text-xs sm:text-sm mb-3 sm:mb-4 md:mb-6">Model Performance Dashboard</div>

      {/* Empty Chart Area */}
      <div className="flex-1 min-h-0 border-2 border-dashed border-slate-300 rounded-lg flex items-center justify-center mb-3 sm:mb-4 md:mb-6">
        <div className="text-center">
          <div className="text-3xl sm:text-4xl md:text-6xl mb-2 sm:mb-3 md:mb-4">📊</div>
          <div className="text-slate-500 text-xs sm:text-sm">No data available</div>
        </div>
      </div>

      {/* Greyed Out Metrics */}
      <div className="grid grid-cols-2 gap-2 sm:gap-3 md:gap-4">
        <div className="bg-slate-100 rounded p-2 sm:p-3 md:p-4 opacity-50">
          <div className="text-[10px] sm:text-xs text-slate-500 mb-0.5 sm:mb-1">Model Performance</div>
          <div className="text-lg sm:text-xl md:text-2xl text-slate-400">--</div>
        </div>
        <div className="bg-slate-100 rounded p-2 sm:p-3 md:p-4 opacity-50">
          <div className="text-[10px] sm:text-xs text-slate-500 mb-0.5 sm:mb-1">User Engagement</div>
          <div className="text-lg sm:text-xl md:text-2xl text-slate-400">--</div>
        </div>
        <div className="bg-slate-100 rounded p-2 sm:p-3 md:p-4 opacity-50">
          <div className="text-[10px] sm:text-xs text-slate-500 mb-0.5 sm:mb-1">Parameter Insights</div>
          <div className="text-lg sm:text-xl md:text-2xl text-slate-400">--</div>
        </div>
        <div className="bg-slate-100 rounded p-2 sm:p-3 md:p-4 opacity-50">
          <div className="text-[10px] sm:text-xs text-slate-500 mb-0.5 sm:mb-1">ROI per Model</div>
          <div className="text-lg sm:text-xl md:text-2xl text-slate-400">--</div>
        </div>
      </div>
    </div>
  );
}
