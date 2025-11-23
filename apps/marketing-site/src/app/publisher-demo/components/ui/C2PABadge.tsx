'use client';

import { motion } from 'framer-motion';
import { Lock, CheckCircle, Shield } from 'lucide-react';

export default function C2PABadge() {
  return (
    <motion.div
      className="bg-gradient-to-br from-blue-900/50 to-purple-900/50 p-6 rounded-lg border-2 border-blue-500/50 shadow-xl"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-center gap-3 mb-4">
        <Lock className="w-6 h-6 text-blue-400" />
        <h3 className="text-xl font-bold text-white">C2PA Content Credentials</h3>
      </div>

      <div className="space-y-3 text-slate-100">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-slate-300">Publisher:</span>
            <p className="font-semibold text-white">The Encypher Times</p>
          </div>
          <div>
            <span className="text-slate-300">Asset ID:</span>
            <p className="font-mono text-sm text-white">GT-20251014-ARTCL-001</p>
          </div>
          <div className="col-span-2">
            <span className="text-slate-300">Created:</span>
            <p className="text-white">October 14, 2025 14:32 UTC</p>
          </div>
        </div>

        <div className="border-t border-slate-700 pt-4 mt-4 space-y-2">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-400" />
            <span className="text-sm">Cryptographically signed</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-400" />
            <span className="text-sm">Tamper-evident at sentence level</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-400" />
            <span className="text-sm">Persistent across platforms</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-400" />
            <span className="text-sm">Machine-readable licensing terms</span>
          </div>
        </div>

        <div className="bg-blue-950/50 p-3 rounded border border-blue-500/30 mt-4">
          <div className="flex items-start gap-2">
            <Shield className="w-4 h-4 text-blue-300 flex-shrink-0 mt-0.5" />
            <div className="text-xs">
              <p className="font-semibold text-blue-200 mb-1">License:</p>
              <p className="text-slate-100">Commercial use requires written permission</p>
              <p className="text-slate-300 mt-1">Contact: licensing@encyphertimes.com</p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
