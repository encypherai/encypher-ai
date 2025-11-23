'use client';

import { motion } from 'framer-motion';
import { XCircle, CheckCircle, AlertTriangle, Scale } from 'lucide-react';

export default function FlowchartAnimation() {
  return (
    <div className="space-y-12">
      {/* Current State */}
      <motion.div
        className="bg-red-50 p-6 rounded-lg border border-red-300"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <h3 className="text-xl font-bold text-red-700 mb-4">CURRENT STATE: The Discovery Problem</h3>
        <div className="flex flex-col gap-4">
          <motion.div
            className="flex items-center gap-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.8 }}
          >
            <div className="bg-slate-200 text-slate-900 px-4 py-2 rounded font-semibold">Publisher</div>
            <div className="flex-1 border-t-2 border-slate-300"></div>
          </motion.div>

          <motion.div
            className="flex items-center gap-4 pl-8"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 1 }}
          >
            <span className="text-slate-700 italic">&quot;You used our content&quot;</span>
          </motion.div>

          <motion.div
            className="flex items-center gap-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 1.2 }}
          >
            <div className="bg-slate-200 text-slate-900 px-4 py-2 rounded font-semibold">AI Lab</div>
            <div className="flex-1 border-t-2 border-slate-300"></div>
          </motion.div>

          <motion.div
            className="flex items-center gap-4 pl-8"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 1.4 }}
          >
            <span className="text-slate-700 italic">&quot;Prove it&quot;</span>
          </motion.div>

          <motion.div
            className="flex items-center gap-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 1.6 }}
          >
            <div className="bg-red-100 text-slate-900 px-4 py-2 rounded border border-red-400 flex items-center gap-2">
              <XCircle className="w-5 h-5 text-red-600" />
              <span>Years of litigation, millions in fees, uncertain outcome</span>
            </div>
          </motion.div>
        </div>
      </motion.div>

      {/* With Encypher */}
      <motion.div
        className="bg-green-50 p-6 rounded-lg border border-green-300"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 1.8 }}
      >
        <h3 className="text-xl font-bold text-green-700 mb-4">WITH ENCYPHER: The Burden Shifts</h3>
        <div className="flex flex-col gap-4">
          <motion.div
            className="flex items-center gap-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 2 }}
          >
            <div className="bg-slate-200 text-slate-900 px-4 py-2 rounded font-semibold">Publisher</div>
            <div className="flex-1 border-t-2 border-slate-300"></div>
          </motion.div>

          <motion.div
            className="flex items-center gap-4 pl-8"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 2.2 }}
          >
            <span className="text-slate-700">Embeds C2PA metadata & serves cryptographic notice</span>
          </motion.div>

          <motion.div
            className="flex items-center gap-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 2.4 }}
          >
            <div className="bg-slate-200 text-slate-900 px-4 py-2 rounded font-semibold">AI Lab Receives Notice</div>
            <div className="flex-1 border-t-2 border-slate-300"></div>
          </motion.div>

          <motion.div
            className="grid md:grid-cols-3 gap-4 pl-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 2.6 }}
          >
            <motion.div
              className="bg-green-100 text-slate-900 p-3 rounded border border-green-400 flex flex-col gap-2"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 2.8 }}
            >
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="font-semibold">Option 1</span>
              </div>
              <span className="text-sm">Filter & License</span>
              <span className="text-xs text-slate-600">Compliant, sustainable</span>
            </motion.div>

            <motion.div
              className="bg-yellow-100 text-slate-900 p-3 rounded border border-yellow-400 flex flex-col gap-2"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 3 }}
            >
              <div className="flex items-center gap-2">
                <Scale className="w-5 h-5 text-yellow-600" />
                <span className="font-semibold">Option 2</span>
              </div>
              <span className="text-sm">Ignore Notice</span>
              <span className="text-xs text-slate-600">Negligence, higher damages</span>
            </motion.div>

            <motion.div
              className="bg-red-100 text-slate-900 p-3 rounded border border-red-400 flex flex-col gap-2"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 3.2 }}
            >
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-600" />
                <span className="font-semibold">Option 3</span>
              </div>
              <span className="text-sm">Strip Notice</span>
              <span className="text-xs text-slate-600">DMCA violation, willful</span>
            </motion.div>
          </motion.div>

          <motion.div
            className="flex items-center gap-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 3.4 }}
          >
            <div className="bg-green-100 text-slate-900 px-4 py-2 rounded border border-green-400 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span>Strong legal position, clear evidence, inevitable licensing</span>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
