'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import { useScrollLock } from '../../hooks/useScrollLock';
import { sendArticleMessage } from '../ArticleIframe';
// CopyPasteAnimation not used in this section
// import CopyPasteAnimation from '../animations/CopyPasteAnimation';
import ChatbotInterface from '../ui/ChatbotInterface';
import LegalDefenseBox from '../ui/LegalDefenseBox';
import { ChevronDown } from 'lucide-react';

interface Section2LoopholeProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

export default function Section2Loophole({ isActive, onComplete, onAnimationStart }: Section2LoopholeProps) {
  const [animationStage, setAnimationStage] = useState<'idle' | 'copying' | 'chatbot' | 'defense' | 'complete'>('idle');
  const [isAnimating, setIsAnimating] = useState(false);
  const [canAnimate, setCanAnimate] = useState(false);
  
  const { sectionRef } = useSectionScroll({ 
    sectionIndex: 2, 
    isActive,
    onScrollComplete: () => setCanAnimate(true)
  });
  
  // Lock scroll during animation
  useScrollLock(isAnimating);

  useEffect(() => {
    if (canAnimate && animationStage === 'idle') {
      onAnimationStart();
      setIsAnimating(true);
      
      // Start animation sequence
      setTimeout(() => {
        sendArticleMessage({ type: 'highlightParagraph' });
        setAnimationStage('copying');
      }, 500);

      setTimeout(() => {
        setAnimationStage('chatbot');
      }, 3500);

      setTimeout(() => {
        setAnimationStage('defense');
        sendArticleMessage({ type: 'removeHighlight' });
      }, 6000);
      
      // Unlock scroll after 1 second, but continue animations
      setTimeout(() => {
        setIsAnimating(false);
      }, 1000);
      
      // Complete animation sequence
      setTimeout(() => {
        setAnimationStage('complete');
        onComplete(); // Mark section as complete
      }, 9000);
    }
  }, [canAnimate, animationStage, onComplete, onAnimationStart]);

  return (
    <section
      ref={sectionRef}
      data-section="2"
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
              <h3 className="text-base sm:text-lg font-semibold text-slate-900 mb-3">Analyzing article content...</h3>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <motion.div
                  className="h-full bg-blue-500"
                  initial={{ width: '0%' }}
                  animate={{ width: '100%' }}
                  transition={{ duration: 3, ease: 'linear' }}
                />
              </div>
              <p className="text-xs sm:text-sm text-slate-600 mt-2">Extracting text and preparing for AI ingestion</p>
            </div>
          </motion.div>
        )}

        {/* Keep chatbot visible after animation */}
        {(animationStage === 'chatbot' || animationStage === 'defense' || animationStage === 'complete') && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-12"
          >
            <ChatbotInterface
              isProcessing={animationStage === 'chatbot'}
              showOutput={animationStage === 'defense' || animationStage === 'complete'}
            />
          </motion.div>
        )}

        <AnimatePresence mode="wait">
          {(animationStage === 'defense' || animationStage === 'complete') && (
            <motion.div
              key="defense"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <LegalDefenseBox />

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.6 }}
                className="mt-12"
              >
                <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-slate-900 mb-4 sm:mb-6">
                  Their Best Defense is Your Biggest Cost.
                </h2>
                <div className="text-lg text-slate-700 space-y-4">
                  <p>
                    This is the &quot;discovery hell&quot; the publishing industry is paying millions to fight.
                  </p>
                  <p>
                    Without persistent provenance, their plausible deniability is stronger than your proof of use. You must prove:
                  </p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li>They accessed your content</li>
                    <li>They ingested it into training data</li>
                    <li>They knew it was protected</li>
                    <li>They chose to use it anyway</li>
                  </ul>
                  <p className="pt-4">
                    Each step requires expensive forensic analysis, legal discovery, and expert testimony. Meanwhile, they simply say: <span className="text-slate-700 font-semibold italic bg-slate-100 px-2 py-1 rounded">&quot;We didn&apos;t know.&quot;</span>
                  </p>
                </div>
              </motion.div>
              
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
