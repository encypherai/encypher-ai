'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import { useScrollLock } from '../../hooks/useScrollLock';
import { sendArticleMessage } from '../ArticleIframe';
// CopyPasteAnimation not used in this section
// import CopyPasteAnimation from '../animations/CopyPasteAnimation';
import ChatbotInterface from '../ui/ChatbotInterface';
import AlertBox from '../ui/AlertBox';
import { ChevronDown } from 'lucide-react';

interface Section4BurdenShiftProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

export default function Section4BurdenShift({ isActive, onComplete, onAnimationStart }: Section4BurdenShiftProps) {
  const [animationStage, setAnimationStage] = useState<'idle' | 'copying' | 'alert' | 'explanation' | 'complete'>('idle');
  const [isAnimating, setIsAnimating] = useState(false);
  const [canAnimate, setCanAnimate] = useState(false);
  
  const { sectionRef } = useSectionScroll({ 
    sectionIndex: 4, 
    isActive,
    onScrollComplete: () => setCanAnimate(true)
  });
  
  useScrollLock(isAnimating);

  useEffect(() => {
    if (canAnimate && animationStage === 'idle') {
      onAnimationStart();
      setIsAnimating(true);
      
      // Repeat copy-paste animation
      setTimeout(() => {
        sendArticleMessage({ type: 'highlightParagraph' });
        setAnimationStage('copying');
      }, 500);

      setTimeout(() => {
        setAnimationStage('alert');
        sendArticleMessage({ type: 'removeHighlight' });
      }, 3500);

      setTimeout(() => {
        setAnimationStage('explanation');
      }, 5000);
      
      // Unlock scroll after 1 second
      setTimeout(() => {
        setIsAnimating(false);
      }, 1000);
      
      // Complete animation sequence
      setTimeout(() => {
        setAnimationStage('complete');
        onComplete(); // Mark section as complete
      }, 8000);
    }
  }, [canAnimate, animationStage, onComplete, onAnimationStart]);

  return (
    <section
      ref={sectionRef}
      data-section="4"
      className="min-h-screen flex items-start lg:items-center justify-center px-4 sm:px-6 lg:px-16 pt-4 pb-12 sm:py-16 lg:py-20"
    >
      <div className="max-w-5xl w-full">
        {/* Progress indicator during copying animation */}
        {animationStage === 'copying' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="lg:mb-12 mb-4"
          >
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 sm:p-6">
              <h3 className="text-base sm:text-lg font-semibold text-slate-900 mb-3">Re-analyzing article content...</h3>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <motion.div
                  className="h-full bg-blue-500"
                  initial={{ width: '0%' }}
                  animate={{ width: '100%' }}
                  transition={{ duration: 3, ease: 'linear' }}
                />
              </div>
              <p className="text-xs sm:text-sm text-slate-600 mt-2">Detecting C2PA metadata and cryptographic notice</p>
            </div>
          </motion.div>
        )}

        {/* Keep chatbot and alert visible after animation */}
        {(animationStage === 'alert' || animationStage === 'explanation' || animationStage === 'complete') && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-8">
              <ChatbotInterface
                isProcessing={false}
                showOutput={false}
                showAlert={true}
              />
            </div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <AlertBox />
            </motion.div>
          </motion.div>
        )}

        <AnimatePresence mode="wait">
          {(animationStage === 'explanation' || animationStage === 'complete') && (
            <motion.div
              key="explanation"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className="mt-12"
            >
              <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-slate-900 mb-4 sm:mb-6">
                You Just Turned &quot;We Didn&apos;t Know&quot; Into &quot;Willful Infringement.&quot;
              </h2>

              <div className="text-lg text-slate-700 space-y-6">
                <p className="text-xl font-semibold text-slate-900">
                  The burden of proof has shifted.
                </p>

                <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                  <p className="mb-4">
                    <span className="text-red-600 font-semibold">Before Encypher:</span> You had to prove they used your content.
                  </p>
                  <p>
                    <span className="text-green-600 font-semibold">Now:</span> They have to prove they didn&apos;t receive the notice.
                  </p>
                </div>

                <p>
                  The act of ignoring or stripping this notice is a provable action. You&apos;ve moved from:
                </p>

                <div className="flex flex-col gap-4 pl-8 border-l-4 border-blue-500">
                  <div>
                    <p className="text-slate-500 line-through">&quot;Prove they used it&quot;</p>
                  </div>
                  <div className="text-2xl text-blue-600">↓</div>
                  <div>
                    <p className="text-green-600 font-semibold">&quot;Prove they ignored you&quot;</p>
                  </div>
                </div>

                <div className="grid md:grid-cols-3 gap-4 mt-8">
                  <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                    <p className="text-sm text-slate-600 mb-2">This is the difference between</p>
                    <p className="font-semibold text-slate-900">Negligence and Willful Infringement</p>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                    <p className="text-sm text-slate-600 mb-2">This is the difference between</p>
                    <p className="font-semibold text-slate-900">Statutory Damages and Treble Damages</p>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                    <p className="text-sm text-slate-600 mb-2">This is the difference between</p>
                    <p className="font-semibold text-slate-900">A Settlement and A Precedent</p>
                  </div>
                </div>
              </div>
              
              {animationStage === 'complete' && (
                <motion.div
                  className="flex flex-col items-center gap-4 text-slate-600 mt-12"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5, delay: 1 }}
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
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}
