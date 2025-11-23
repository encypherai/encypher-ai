'use client';

import { motion } from 'framer-motion';
import React, { useState, useEffect } from 'react';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import { useScrollLock } from '../../hooks/useScrollLock';
import ScrollIndicator from '../ui/ScrollIndicator';

interface Section5SafeHarborProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

const benefits = [
  {
    icon: '🎯',
    title: 'R&D Intelligence',
    items: [
      'Performance analytics',
      'Parameter optimization',
      'Model A/B testing',
      'User feedback loop',
      'ROI per model',
    ],
    color: 'from-blue-500 to-cyan-500',
  },
  {
    icon: '🤝',
    title: 'Publisher Access',
    items: [
      'Only enhanced C2PA',
      'Coalition access',
      'Pre-filter training',
      'License leverage',
      'Market access',
    ],
    color: 'from-purple-500 to-pink-500',
  },
  {
    icon: '⚖️',
    title: 'Regulatory Shield',
    items: [
      'All regions',
      'One integration',
      'Auto updates',
      'Safe harbor',
      'GDPR aligned',
    ],
    color: 'from-green-500 to-emerald-500',
  },
];

export default function Section5SafeHarbor({ isActive, onComplete, onAnimationStart }: Section5SafeHarborProps) {
  const [isAnimating, setIsAnimating] = useState(false);
  const [canAnimate, setCanAnimate] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);
  const [hasBeenActive, setHasBeenActive] = useState(false);
  
  const { sectionRef } = useSectionScroll({
    sectionIndex: 5,
    isActive,
    onScrollComplete: () => setCanAnimate(true)
  });

  useEffect(() => {
    if (canAnimate && !hasAnimated) {
      console.log('[Section5] Starting animation');
      setHasAnimated(true);
      onAnimationStart();
      setIsAnimating(true);
      
      // Complete after animation
      setTimeout(() => {
        console.log('[Section5] Animation complete');
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
    console.log('[Section5] isActive changed:', isActive);
  }, [isActive]);
  
  // Lock scroll during animation
  useScrollLock(isAnimating);

  return (
    <section 
      ref={sectionRef}
      data-section="5" 
      className="min-h-screen flex items-center px-4 sm:px-6 md:px-8 py-12 sm:py-16 md:py-20 bg-gradient-to-br from-slate-50 via-white to-slate-100 scroll-mt-0"
    >
      <div className="max-w-7xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0 }}
          animate={(isActive || hasBeenActive) ? { opacity: 1 } : { opacity: 0 }}
          className="mb-12 text-center"
        >
          <h2 className="text-4xl md:text-6xl font-bold text-slate-900 mb-6">
            One Integration.{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-600">
              Three Critical Problems
            </span>{' '}
            Solved.
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Your competitors are implementing compliance. You&apos;re deploying intelligence.
          </p>
        </motion.div>

        {/* Three Column Benefits */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {benefits.map((benefit, index) => (
            <motion.div
              key={benefit.title}
              initial={{ opacity: 0, y: 30 }}
              animate={(isActive || hasBeenActive) ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
              transition={{ delay: index * 0.2, duration: 0.6 }}
              className="relative group"
            >
              <div className="bg-white border border-slate-200 rounded-lg p-6 h-full hover:border-slate-300 transition-colors shadow-lg">
                <div className="text-5xl mb-4">{benefit.icon}</div>
                <h3 className="text-2xl font-bold text-slate-900 mb-4">
                  {benefit.title}
                </h3>
                <ul className="space-y-3">
                  {benefit.items.map((item) => (
                    <li key={item} className="flex items-start gap-2">
                      <span className="text-green-600 mt-1">✓</span>
                      <span className="text-slate-700">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Gradient glow effect on hover */}
              <div
                className={`absolute -inset-px bg-gradient-to-r ${benefit.color} opacity-0 group-hover:opacity-20 rounded-lg -z-10 blur-xl transition-opacity`}
              />
            </motion.div>
          ))}
        </div>

        {/* Summary Text */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={(isActive || hasBeenActive) ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ delay: 0.8 }}
          className="max-w-4xl mx-auto"
        >
          <div className="bg-white border border-slate-200 rounded-lg p-8 shadow-lg">
            <h3 className="text-2xl font-bold text-slate-900 mb-6">
              One integration solves:
            </h3>
            <div className="space-y-4 text-slate-700">
              <div>
                <strong className="text-slate-900">1. LITIGATION EXPOSURE</strong> ($5B+ active claims)
                <br />
                <span className="text-slate-600">
                  Technical defense + publisher compatibility
                </span>
              </div>
              <div>
                <strong className="text-slate-900">2. R&D BLIND SPOT</strong> ($2.7B per version)
                <br />
                <span className="text-slate-600">
                  Real-world performance analytics
                </span>
              </div>
              <div>
                <strong className="text-slate-900">3. REGULATORY REQUIREMENT</strong> (12+ jurisdictions)
                <br />
                <span className="text-slate-600">
                  One integration, all compliance
                </span>
              </div>
            </div>
            <p className="text-xl text-slate-900 mt-6 font-semibold">
              This is infrastructure for the AI economy.
            </p>
            <div className="mt-8">
              <ScrollIndicator delay={0.5} />
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
