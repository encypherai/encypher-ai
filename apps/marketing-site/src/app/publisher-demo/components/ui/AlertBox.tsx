'use client';

import { motion } from 'framer-motion';
import { AlertTriangle, ExternalLink, Mail } from 'lucide-react';

export default function AlertBox() {
  return (
    <motion.div
      className="bg-red-950 border-2 border-red-500 rounded-lg p-6 shadow-xl"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ 
        opacity: 1, 
        scale: 1,
      }}
      transition={{ duration: 0.5 }}
    >
      <motion.div
        animate={{
          x: [0, -3, 3, -3, 3, 0],
        }}
        transition={{
          duration: 0.5,
          delay: 0.3,
        }}
      >
        <div className="flex items-center gap-3 mb-4">
          <AlertTriangle className="w-8 h-8 text-yellow-400" />
          <h3 className="text-2xl font-bold text-white">LICENSING NOTICE SERVED</h3>
        </div>

        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-red-300 font-medium">Source:</span>
              <span className="text-white ml-2">The Encypher Times</span>
            </div>
            <div>
              <span className="text-red-300 font-medium">Asset ID:</span>
              <span className="text-white ml-2">GT-20251014-ARTCL-001</span>
            </div>
            <div className="col-span-2">
              <span className="text-red-300 font-medium">Timestamp:</span>
              <span className="text-white ml-2">2025-10-14 14:35:22 UTC</span>
            </div>
          </div>

          <div className="bg-red-900/60 p-4 rounded border border-red-400/50 mt-4">
            <p className="font-bold mb-2 text-yellow-300">REQUIREMENT:</p>
            <p className="text-sm text-white leading-relaxed">
              This content requires a license for use in AI training datasets or derivative works.
            </p>
          </div>

          <div className="flex gap-3 mt-4">
            <button className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-sm font-semibold text-white transition-colors">
              <ExternalLink className="w-4 h-4" />
              View Full Terms
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-sm font-semibold text-white transition-colors">
              <Mail className="w-4 h-4" />
              Contact Publisher
            </button>
          </div>

          <div className="bg-red-900/60 p-3 rounded border border-red-400/50 mt-4">
            <p className="text-xs text-white leading-relaxed">
              <strong className="text-yellow-300">WARNING:</strong> Proceeding without a license may constitute willful copyright infringement under 17 U.S.C. § 504(c)
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
