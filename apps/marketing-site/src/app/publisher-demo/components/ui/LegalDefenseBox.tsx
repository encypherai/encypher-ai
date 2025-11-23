'use client';

import { motion } from 'framer-motion';
import { Scale } from 'lucide-react';

export default function LegalDefenseBox() {
  return (
    <motion.div
      className="bg-amber-50 p-6 rounded-lg border-2 border-amber-300"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-start gap-4">
        <Scale className="w-6 h-6 text-amber-600 flex-shrink-0 mt-1" />
        <div>
          <h3 className="text-lg font-bold text-slate-900 mb-3">
            AI Corp. Legal Defense Statement
          </h3>
          <p className="text-slate-700 italic leading-relaxed mb-4">
            &quot;We cannot control what users paste into our systems. We have no technical means of knowing the source or licensing requirements of this text. Our terms of service place responsibility on users to ensure they have appropriate rights to any content they provide.&quot;
          </p>
          <p className="text-sm text-slate-600">
            — Standard AI Industry Defense (2024)
          </p>
        </div>
      </div>
    </motion.div>
  );
}
