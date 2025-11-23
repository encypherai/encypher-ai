'use client';

import { motion } from 'framer-motion';
import { Bot, Loader2 } from 'lucide-react';

interface ChatbotInterfaceProps {
  isProcessing: boolean;
  showOutput: boolean;
  showAlert?: boolean;
}

export default function ChatbotInterface({ isProcessing, showOutput, showAlert = false }: ChatbotInterfaceProps) {
  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="bg-slate-900 px-4 py-3 border-b border-slate-700 flex items-center gap-3">
        <Bot className="w-5 h-5 text-blue-400" />
        <span className="font-semibold text-white">AI Training Assistant v3.2</span>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Input */}
        <div>
          <label className="text-sm text-slate-400 mb-2 block">Paste training data:</label>
          <div className="bg-slate-900 p-3 rounded border border-slate-700 text-slate-300 text-sm">
            The creative and media industries are facing an existential crisis. Their business models, already strained by two decades of digital disruption, are now threatened by the exponential rise of generative AI...
          </div>
        </div>

        {/* Processing */}
        {isProcessing && (
          <motion.div
            className="flex items-center gap-2 text-blue-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Processing...</span>
          </motion.div>
        )}

        {/* Output */}
        {showOutput && !showAlert && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="bg-slate-900 p-3 rounded border border-green-500/30 text-slate-300 text-sm">
              <div className="flex items-center gap-2 text-green-400 mb-2">
                <span className="text-xs">✓</span>
                <span className="font-semibold">Summary generated:</span>
              </div>
              <p className="mb-3">
                &quot;Media industry analysis discussing AI disruption, content licensing, and intellectual property challenges. Key themes: generative AI impact, attribution issues, business model transformation.&quot;
              </p>
              <p className="text-xs text-slate-500">
                Added to training dataset: media_industry_batch_2025_10
              </p>
            </div>
          </motion.div>
        )}

        {/* Alert (for Section 4) */}
        {showAlert && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <div className="text-sm text-slate-400">
              Analyzing article content... This appears to be from &apos;The Encypher Times&apos;. Checking licensing requirements...
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
