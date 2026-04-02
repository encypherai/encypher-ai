'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import { trackCTAClick } from '../../lib/analytics';
import CTAButton from '../ui/CTAButton';
import DemoRequestModal from '../ui/DemoRequestModal';
import { FileText, Users, Mail, Shield, TrendingUp, DollarSign } from 'lucide-react';

interface Section6CoalitionProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

export default function Section6Coalition({ isActive, onComplete, onAnimationStart }: Section6CoalitionProps) {
  const [showModal, setShowModal] = useState(false);
  const [canAnimate, setCanAnimate] = useState(false);
  const [hasCompleted, setHasCompleted] = useState(false);

  const { sectionRef } = useSectionScroll({
    sectionIndex: 6,
    isActive,
    onScrollComplete: () => setCanAnimate(true)
  });

  useEffect(() => {
    if (canAnimate && !hasCompleted) {
      onAnimationStart();
      onComplete(); // Final section, mark complete immediately
      setHasCompleted(true);
    }
  }, [canAnimate, hasCompleted, onAnimationStart, onComplete]);

  const handleCTAClick = () => {
    trackCTAClick('primary_demo_request');
    setShowModal(true);
  };

  const handleSecondaryClick = (type: string) => {
    trackCTAClick(type);
  };

  return (
    <section
      ref={sectionRef}
      data-section="6"
      className="min-h-screen flex items-start lg:items-center justify-center px-4 sm:px-6 lg:px-16 pt-4 pb-12 sm:py-16 lg:py-20"
    >
      <div className="max-w-5xl w-full">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isActive ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
        >
          <motion.h2
            className="text-2xl sm:text-3xl md:text-4xl lg:text-6xl font-bold text-slate-900 mb-6 sm:mb-8 text-center"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={isActive ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            First Movers Define the Standard.
          </motion.h2>

          <motion.div
            className="text-base sm:text-lg text-slate-700 space-y-4 sm:space-y-6 mb-8 sm:mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={isActive ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <p className="text-xl">
              A coalition of the world&apos;s leading publishers is forming to make this the non-negotiable standard for AI engagement.
            </p>
            <p>
              Early members don&apos;t just get preferential terms; they co-author the legal and technical precedent for the entire industry.
            </p>
            <p>
              This is not about blocking AI. This is about ensuring that the value created by your content flows back to you. This is about making licensing inevitable, not optional.
            </p>
            <p className="text-xl font-semibold text-slate-900 pt-4">
              The question is not whether this becomes the standard.<br />
              The question is whether you help define it.
            </p>
          </motion.div>

          {/* Bridge Value Section */}
          <motion.div
            className="bg-blue-50 p-8 rounded-lg border border-blue-100 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={isActive ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <h3 className="text-xl font-bold text-slate-900 mb-2">What You Get While the Coalition Scales</h3>
            <p className="text-slate-600 text-sm mb-6">Licensing revenue builds over time. Encypher delivers real value from the first article you sign.</p>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="flex items-start gap-3">
                <Shield className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-slate-800 text-sm">Protected corpus builds daily</p>
                  <p className="text-slate-600 text-xs mt-1">Every article you publish is cryptographically signed. Your provably owned content corpus grows every day.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <TrendingUp className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-slate-800 text-sm">Evidence accumulates automatically</p>
                  <p className="text-xs text-slate-600 mt-1">Every external provenance check is logged. At 500 verifications, you qualify to serve Formal Notice to AI companies.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <DollarSign className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-slate-800 text-sm">Content spread analytics</p>
                  <p className="text-xs text-slate-600 mt-1">See where your signed content appears across the internet - independent value, regardless of where licensing negotiations stand.</p>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            className="bg-slate-50 p-8 rounded-lg border border-slate-200 mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={isActive ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <h3 className="text-2xl font-bold text-slate-900 mb-6">Founding Coalition Members (First 20) Receive:</h3>
            <div className="grid md:grid-cols-2 gap-4 text-slate-700">
              <div className="flex items-start gap-3">
                <span className="text-green-400 text-xl">✓</span>
                <span>Implementation fee waived for founding members</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-400 text-xl">✓</span>
                <span>Same licensing revenue splits as all publishers — majority to content creator</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-400 text-xl">✓</span>
                <span>Syracuse Symposium seat — define market licensing frameworks</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-400 text-xl">✓</span>
                <span>Advisory board participation</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-400 text-xl">✓</span>
                <span>Priority coalition positioning in all licensing negotiations</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-400 text-xl">✓</span>
                <span>Free signing infrastructure — unlimited everything</span>
              </div>
            </div>
          </motion.div>

          <motion.div
            className="flex flex-col items-center gap-8"
            initial={{ opacity: 0, y: 30 }}
            animate={isActive ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.8 }}
          >
            <CTAButton onClick={handleCTAClick} />

            <div className="flex flex-wrap justify-center gap-6 text-sm">
              <a
                href="/pricing"
                onClick={() => handleSecondaryClick('pricing')}
                className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors"
              >
                <FileText className="w-4 h-4" />
                View Pricing & Add-Ons
              </a>
              <a
                href="/solutions/publishers"
                onClick={() => handleSecondaryClick('publisher_solutions')}
                className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors"
              >
                <Users className="w-4 h-4" />
                Publisher Solutions
              </a>
              <a
                href="/contact"
                onClick={() => handleSecondaryClick('contact')}
                className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors"
              >
                <Mail className="w-4 h-4" />
                Contact Sales Team
              </a>
            </div>
          </motion.div>
        </motion.div>
      </div>

      <AnimatePresence>
        {showModal && (
          <DemoRequestModal onClose={() => setShowModal(false)} />
        )}
      </AnimatePresence>
    </section>
  );
}
