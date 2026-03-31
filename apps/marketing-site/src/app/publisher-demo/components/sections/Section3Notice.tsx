'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import { useScrollLock } from '../../hooks/useScrollLock';
import { sendArticleMessage } from '../ArticleIframe';
import C2PABadge from '../ui/C2PABadge';
import { ChevronDown } from 'lucide-react';

interface Section3NoticeProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

export default function Section3Notice({ isActive, onComplete, onAnimationStart }: Section3NoticeProps) {
  const [showContent, setShowContent] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [canAnimate, setCanAnimate] = useState(false);

  const { sectionRef } = useSectionScroll({
    sectionIndex: 3,
    isActive,
    onScrollComplete: () => setCanAnimate(true)
  });

  useScrollLock(isAnimating);

  useEffect(() => {
    if (canAnimate && !showContent) {
      onAnimationStart();
      setIsAnimating(true);

      // Trigger scanner animation in iframe
      setTimeout(() => {
        sendArticleMessage({ type: 'startScan' });
      }, 300);

      // Unlock scroll after 1 second
      setTimeout(() => {
        setIsAnimating(false);
      }, 1000);

      // Show content after animations
      setTimeout(() => {
        setShowContent(true);
        onComplete(); // Mark section as complete
      }, 2000);
    }
  }, [canAnimate, showContent, onComplete, onAnimationStart]);

  return (
    <section
      ref={sectionRef}
      data-section="3"
      className="min-h-screen flex items-start lg:items-center justify-center px-4 sm:px-6 lg:px-16 pt-4 pb-12 sm:py-16 lg:py-20"
    >
      <div className="max-w-5xl w-full">
        {/* Progress indicator during scanning animation */}
        {!showContent && canAnimate && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="lg:mb-12 mb-4"
          >
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 sm:p-6">
              <h3 className="text-base sm:text-lg font-semibold text-slate-900 mb-3">Embedding C2PA metadata into article...</h3>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <motion.div
                  className="h-full bg-green-500"
                  initial={{ width: '0%' }}
                  animate={{ width: '100%' }}
                  transition={{ duration: 1.5, ease: 'linear' }}
                />
              </div>
              <p className="text-xs sm:text-sm text-slate-600 mt-2">Creating cryptographic proof and licensing manifest</p>
            </div>
          </motion.div>
        )}

        <AnimatePresence mode="wait">
          {showContent && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <motion.h2
                className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-slate-900 mb-4 sm:mb-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.1 }}
              >
                The Infrastructure, Not An Application.
              </motion.h2>

              <motion.div
                className="text-lg text-slate-700 space-y-4 mb-12"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.2 }}
              >
                <p>
                  We authored Section A.7 of the C2PA 2.3 specification. Our infrastructure embeds a persistent, cryptographic notice of your licensing requirements directly into your content.
                </p>
                <p className="text-xl font-semibold text-slate-900">
                  Stripping it is a provable act of willfulness.<br />
                  Ignoring it is a provable act of negligence.<br />
                  It&apos;s a mathematically verifiable proof that turns their actions into your evidence.
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4, delay: 0.3 }}
              >
                <C2PABadge />
              </motion.div>

              <motion.div
                className="mt-12 p-6 bg-slate-50 rounded-lg border border-slate-200"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.4 }}
              >
                <h3 className="text-xl font-bold text-slate-900 mb-4">How it works:</h3>
                <ol className="space-y-3 text-slate-700">
                  <li className="flex gap-3">
                    <span className="font-bold text-blue-600">1.</span>
                    <div>
                      <strong>Establish a Verifiable State</strong>
                      <ul className="list-disc list-inside ml-4 mt-1 text-sm text-slate-600">
                        <li>We embed a cryptographic fingerprint into your content</li>
                      </ul>
                    </div>
                  </li>
                  <li className="flex gap-3">
                    <span className="font-bold text-blue-600">2.</span>
                    <div>
                      <strong>Create a Persistent Notice</strong>
                      <ul className="list-disc list-inside ml-4 mt-1 text-sm text-slate-600">
                        <li>Your licensing terms are bound into the content itself</li>
                      </ul>
                    </div>
                  </li>
                  <li className="flex gap-3">
                    <span className="font-bold text-blue-600">3.</span>
                    <div>
                      <strong>Shift the Legal Burden</strong>
                      <ul className="list-disc list-inside ml-4 mt-1 text-sm text-slate-600">
                        <li>Any system that reads the content is now provably &apos;on notice,&apos;</li>
                        <li>Ignorance is no longer a valid defense</li>
                      </ul>
                    </div>
                  </li>
                </ol>
              </motion.div>

              {/* Scroll to continue indicator */}
              <motion.div
                className="flex flex-col items-center gap-4 text-slate-600 mt-12"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.4, delay: 0.5 }}
              >
                <p className="text-sm uppercase tracking-wider">Continue scrolling</p>
                <motion.div
                  animate={{
                    y: [0, 10, 0],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                >
                  <ChevronDown className="w-8 h-8" />
                </motion.div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}
