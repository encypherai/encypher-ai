'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import React from 'react';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import { useScrollLock } from '../../hooks/useScrollLock';
import DemoRequestModal from '../ui/DemoRequestModal';

interface Section6IntegrationProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

export default function Section6Integration({ isActive, onComplete, onAnimationStart }: Section6IntegrationProps) {
  const [showModal, setShowModal] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [canAnimate, setCanAnimate] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);
  const [hasBeenActive, setHasBeenActive] = useState(false);

  const { sectionRef } = useSectionScroll({
    sectionIndex: 6,
    isActive,
    onScrollComplete: () => setCanAnimate(true)
  });

  useEffect(() => {
    if (canAnimate && !hasAnimated) {
      console.log('[Section6] Starting animation');
      setHasAnimated(true);
      onAnimationStart();
      setIsAnimating(true);
      
      // Complete after animation
      setTimeout(() => {
        console.log('[Section6] Animation complete');
        setIsAnimating(false);
        onComplete();
      }, 1000);
    }
  }, [canAnimate, hasAnimated, onComplete, onAnimationStart]);

  // Track if section has ever been active
  useEffect(() => {
    if (isActive && !hasBeenActive) {
      setHasBeenActive(true);
    }
  }, [isActive, hasBeenActive]);

  // Debug logging
  useEffect(() => {
    console.log('[Section6] isActive changed:', isActive);
  }, [isActive]);
  
  // Lock scroll during animation
  useScrollLock(isAnimating);

  return (
    <section 
      ref={sectionRef}
      data-section="6" 
      className="min-h-screen flex items-center px-4 sm:px-6 md:px-8 py-12 sm:py-16 md:py-20 bg-gradient-to-br from-slate-50 via-white to-slate-100 scroll-mt-0"
    >
      <div className="max-w-7xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0 }}
          animate={(isActive || hasBeenActive) ? { opacity: 1 } : { opacity: 0 }}
          className="mb-12 text-center"
        >
          <h2 className="text-4xl md:text-6xl font-bold text-slate-900 mb-6">
            Integration in{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-600">
              Hours, Not Months
            </span>
            .
          </h2>
          <p className="text-xl text-slate-600">
            Three lines of code. Billions of insights.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
          {/* Architecture Diagram */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={(isActive || hasBeenActive) ? { opacity: 1, x: 0 } : { opacity: 0, x: -30 }}
            transition={{ delay: 0.2 }}
            className="bg-white border border-slate-200 rounded-lg p-8 shadow-lg"
          >
            <h3 className="text-xl font-bold text-slate-900 mb-6">Architecture</h3>
            <div className="space-y-4 text-slate-700">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-blue-400" />
                <span>Your Model API</span>
              </div>
              <div className="pl-6 text-slate-500">↓</div>
              <div className="flex items-center gap-3 bg-blue-500/10 border border-blue-500/30 rounded p-3">
                <div className="w-3 h-3 rounded-full bg-cyan-400" />
                <span className="font-semibold text-blue-700">Encypher SDK (3 lines)</span>
              </div>
              <div className="pl-6 text-slate-500">↓</div>
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-green-400" />
                <span>Content + Metadata</span>
              </div>
              <div className="pl-6 text-slate-500">↓</div>
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-purple-400" />
                <span>User → Internet → Engagement</span>
              </div>
              <div className="pl-6 text-slate-500">↓</div>
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-cyan-400" />
                <span>Analytics Dashboard</span>
              </div>
            </div>
          </motion.div>

          {/* Code Example */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={(isActive || hasBeenActive) ? { opacity: 1, x: 0 } : { opacity: 0, x: 30 }}
            transition={{ delay: 0.4 }}
            className="bg-slate-900 border border-slate-700 rounded-lg p-6 overflow-x-auto"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="text-xs text-slate-400">Enterprise Python SDK</div>
              <div className="inline-flex items-center gap-1.5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-[10px] font-semibold px-2.5 py-1 rounded-full">
                <span>✨</span>
                <span>COMING SOON</span>
              </div>
            </div>
            <pre className="text-[11px] sm:text-xs text-slate-200 leading-relaxed">
              <code>{`# Streaming Support (Critical for Chat Applications)
from encypher_enterprise import StreamingSigner

signer = StreamingSigner(client)
for chunk in openai_stream:
    signed_chunk = signer.process_chunk(chunk)
    print(signed_chunk, end='')
final_text = signer.finalize()  # Complete signed text

# OpenAI Integration (Drop-in Replacement)
from encypher_enterprise.integrations.openai import EncypherOpenAI

client = EncypherOpenAI(
    openai_api_key="sk-...",
    encypher_api_key="encypher_..."
)
# Normal OpenAI usage - automatically signed with C2PA!
response = client.chat.completions.create(model="gpt-4", ...)

# Simple API
from encypher_enterprise import EncypherClient

client = EncypherClient(api_key="encypher_...")
result = client.sign("Content to sign", title="My Document")
verification = client.verify(result.signed_text)`}</code>
            </pre>
          </motion.div>
        </div>

        {/* Technical Specs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={(isActive || hasBeenActive) ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ delay: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12"
        >
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-lg">
            <h4 className="text-lg font-semibold text-slate-900 mb-3">⚡ Performance</h4>
            <ul className="space-y-2 text-slate-700 text-sm">
              <li>&lt;10ms latency</li>
              <li>100K req/sec</li>
              <li>99.9% SLA</li>
            </ul>
          </div>
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-lg">
            <h4 className="text-lg font-semibold text-slate-900 mb-3">🔌 Compatible</h4>
            <ul className="space-y-2 text-slate-700 text-sm">
              <li>OpenAI, Anthropic</li>
              <li>Google, Cohere</li>
              <li>Custom models</li>
            </ul>
          </div>
          <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-lg">
            <h4 className="text-lg font-semibold text-slate-900 mb-3">📊 Analytics</h4>
            <ul className="space-y-2 text-slate-700 text-sm">
              <li>Live in 24 hours</li>
              <li>Real-time insights</li>
              <li>API access</li>
            </ul>
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={(isActive || hasBeenActive) ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ delay: 0.8 }}
          className="text-center"
        >
          <button
            onClick={() => setShowModal(true)}
            className="group relative inline-flex items-center gap-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-12 py-6 rounded-lg text-xl font-semibold hover:scale-105 transition-transform shadow-lg shadow-blue-500/50"
          >
            <span>Schedule Technical Deep Dive</span>
            <svg
              className="w-6 h-6 group-hover:translate-x-1 transition-transform"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 8l4 4m0 0l-4 4m4-4H3"
              />
            </svg>
          </button>

          {/* <div className="mt-8 flex flex-wrap justify-center gap-6 text-slate-600">
            <a href="#" className="hover:text-slate-900 transition-colors">
              Download SDK Docs
            </a>
            <a href="#" className="hover:text-slate-900 transition-colors">
              View Examples
            </a>
            <a href="#" className="hover:text-slate-900 transition-colors">
              Calculate ROI
            </a>
            <a href="#" className="hover:text-slate-900 transition-colors">
              Read Whitepaper
            </a>
          </div> */}
        </motion.div>

        {/* Demo Request Modal */}
        <AnimatePresence>
          {showModal && (
            <DemoRequestModal onClose={() => setShowModal(false)} />
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}
