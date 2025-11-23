'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import { useSectionScroll } from '../../hooks/useSectionScroll';
import { useScrollLock } from '../../hooks/useScrollLock';
import ScrollIndicator from '../ui/ScrollIndicator';
import StreamingText from '../ui/StreamingText';
import RollingNumber from '../ui/RollingNumber';

interface Section2BlackHoleProps {
  isActive: boolean;
  onComplete: () => void;
  onAnimationStart: () => void;
}

const AI_CONTENT = "🌍 Climate tech isn't just about saving the planet—it's about building a $2T economy. From carbon capture to green hydrogen, innovation is accelerating...";

// Helper function to format current date/time
const getCurrentDateTime = () => {
  const now = new Date();
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const month = months[now.getMonth()];
  const day = now.getDate();
  let hours = now.getHours();
  const minutes = now.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // 0 should be 12
  const minutesStr = minutes < 10 ? '0' + minutes : minutes;
  return `${month} ${day} at ${hours}:${minutesStr} ${ampm}`;
};

export default function Section2BlackHole({ isActive, onComplete, onAnimationStart }: Section2BlackHoleProps) {
  const [animationStep, setAnimationStep] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [canAnimate, setCanAnimate] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);
  const [hasBeenActive, setHasBeenActive] = useState(false);
  const [engagement, setEngagement] = useState({ likes: 0, comments: 0, shares: 0 });
  const [showCopyAnimation, setShowCopyAnimation] = useState(false);
  const [streamingComplete, setStreamingComplete] = useState(false);
  const [postDateTime] = useState(getCurrentDateTime());

  const { sectionRef } = useSectionScroll({
    sectionIndex: 2,
    isActive,
    onScrollComplete: () => setCanAnimate(true)
  });

  useEffect(() => {
    if (canAnimate && !hasAnimated) {
      console.log('[Section2] Starting animation');
      setHasAnimated(true);
      onAnimationStart();
      setIsAnimating(true);
      
      // Start animation sequence
      const steps = [0, 1, 2];
      let currentStep = 0;

      const interval = setInterval(() => {
        if (currentStep < steps.length) {
          setAnimationStep(steps[currentStep]);
          currentStep++;
        } else {
          clearInterval(interval);
          // Wait for streaming to complete before continuing
          // The rest of the animation will be triggered by streamingComplete
        }
      }, 700);
    }
  }, [canAnimate, hasAnimated]);

  // Helper function to scroll element into view smoothly
  const scrollToElement = (selector: string, delay: number = 0) => {
    setTimeout(() => {
      const element = document.querySelector(selector);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, delay);
  };

  // Continue animation after streaming completes
  useEffect(() => {
    if (streamingComplete && animationStep === 2) {
      console.log('[Section2] Streaming complete, continuing animation');
      
      // Small delay after streaming, then show copy animation
      setTimeout(() => {
        setAnimationStep(3);
        setShowCopyAnimation(true);
        setTimeout(() => setShowCopyAnimation(false), 1000);
        
        // Continue with rest of animation
        setTimeout(() => {
          setAnimationStep(4);
          
          setTimeout(() => {
            setAnimationStep(5);
            
            // Animate engagement numbers going up
            let count = 0;
            const engagementInterval = setInterval(() => {
              count += 1;
              setEngagement({
                likes: Math.floor(26000 * (count / 30)),
                comments: Math.floor(157 * (count / 30)),
                shares: Math.floor(1500 * (count / 30))
              });
              if (count >= 30) clearInterval(engagementInterval);
            }, 40);
            
            setTimeout(() => {
              setAnimationStep(6);
              // Scroll to show the "Connection Lost" warning
              scrollToElement('[data-animation="connection-lost"]', 200);
              
              setTimeout(() => {
                setAnimationStep(7);
                // Scroll to show "What you're missing"
                scrollToElement('[data-animation="missing-data"]', 200);
                
                setTimeout(() => {
                  setAnimationStep(8);
                  // Scroll to show the final cost message
                  scrollToElement('[data-animation="final-cost"]', 200);
                  
                  // Complete animation
                  setTimeout(() => {
                    console.log('[Section2] Animation complete');
                    setIsAnimating(false);
                    onComplete();
                  }, 500);
                }, 700);
              }, 700);
            }, 1500); // Wait for engagement animation
          }, 700);
        }, 1200); // Wait for copy animation
      }, 300);
    }
  }, [streamingComplete, animationStep, onComplete]);
  
  // Debug logging
  // Track if section has ever been active
  useEffect(() => {
    if (isActive && !hasBeenActive) {
      setHasBeenActive(true);
    }
  }, [isActive, hasBeenActive]);

  useEffect(() => {
    console.log('[Section2] isActive changed:', isActive);
  }, [isActive]);
  
  // Lock scroll during animation
  useScrollLock(isAnimating);

  return (
    <section 
      ref={sectionRef}
      data-section="2" 
      className="min-h-screen flex items-center px-4 sm:px-6 md:px-8 py-12 sm:py-16 md:py-20 bg-gradient-to-br from-slate-50 via-white to-slate-100 scroll-mt-0"
    >
      <div className="max-w-7xl mx-auto w-full">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={(isActive || hasBeenActive) ? { opacity: 1 } : { opacity: 0 }}
          className="mb-6 sm:mb-8 text-center"
        >
          <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-slate-900 mb-3 sm:mb-4">
            The Performance{' '}
            <span className="text-red-600">Black Hole</span>
          </h2>
          <p className="text-base sm:text-lg md:text-xl text-slate-600">
            Your AI content goes viral. But you have <span className="text-red-600 font-semibold">no idea why</span>.
          </p>
        </motion.div>

        {/* Side-by-Side: AI Chat + Social Media */}
        {animationStep >= 1 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mb-8 max-w-6xl mx-auto">
            {/* Left: AI Chat Interface */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white border-2 border-blue-200 rounded-xl p-4 md:p-6 shadow-lg"
            >
              <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-200">
                <div className="text-xl md:text-2xl">🤖</div>
                <div className="font-semibold text-slate-900 text-sm md:text-base">AI Chat</div>
              </div>
              
              {/* User Prompt */}
              <div className="mb-4">
                <div className="bg-slate-100 rounded-lg p-2.5 md:p-3 inline-block max-w-[85%]">
                  <div className="text-xs md:text-sm text-slate-700">&quot;Write a social media post about climate tech&quot;</div>
                </div>
              </div>

              {/* AI Response */}
              {animationStep >= 2 && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-3"
                >
                  <div className="bg-blue-50 rounded-lg p-3 md:p-4 border border-blue-100 ml-auto max-w-[95%]">
                    <div className="text-[10px] md:text-xs text-blue-600 mb-2">
                      <span className="font-semibold">gpt-4-turbo</span> • temp: 0.7
                    </div>
                    <div className="text-xs md:text-sm text-slate-800 italic leading-relaxed">
                      <StreamingText 
                        text={AI_CONTENT} 
                        speed={4}
                        onComplete={() => setStreamingComplete(true)}
                      />
                    </div>
                    {streamingComplete && (
                      <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-[10px] md:text-xs text-green-600 mt-2 flex items-center gap-1"
                      >
                        <span>✓</span>
                        <span>Generated</span>
                      </motion.div>
                    )}
                  </div>
                </motion.div>
              )}
            </motion.div>

            {/* Right: Social Media Site (Facebook-style Light Theme) */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-blue-50 rounded-xl shadow-lg relative overflow-hidden border border-blue-100 @container"
            >
              {/* Social Header with Encypher Logo */}
              <div className="bg-white px-3 md:px-4 py-2.5 md:py-3 flex items-center gap-2 md:gap-3 border-b border-blue-100">
                <img 
                  src="/encypher_icon_nobg_color.png" 
                  alt="Encypher" 
                  className="w-6 h-6 md:w-8 md:h-8 flex-shrink-0"
                />
                <div className="font-bold text-slate-900 text-sm md:text-base truncate">Encypher Social</div>
              </div>

              {/* Post Content */}
              {animationStep >= 3 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white m-2 md:m-2.5 lg:m-3 rounded-lg shadow-sm"
                >
                  {/* Post Header */}
                  <div className="px-3 md:px-3.5 lg:px-4 pt-3 md:pt-3.5 lg:pt-4 pb-2 md:pb-2.5 lg:pb-3">
                    <div className="flex items-center gap-2 md:gap-2.5 lg:gap-3 mb-2 md:mb-2.5 lg:mb-3">
                      <div className="w-8 h-8 md:w-9 md:h-9 lg:w-10 lg:h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-white font-semibold text-xs md:text-[13px] lg:text-sm">TE</span>
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="font-semibold text-slate-900 text-xs md:text-[13px] lg:text-sm truncate">Tech Enthusiast</div>
                        <div className="text-[10px] md:text-[11px] lg:text-xs text-slate-500 flex items-center gap-1">
                          <span className="truncate">{postDateTime}</span> · 🌍
                        </div>
                      </div>
                    </div>
                    
                    {/* Post Text Content */}
                    <div className="text-slate-800 text-xs md:text-[13px] lg:text-[15px] leading-relaxed mb-2 md:mb-2.5 lg:mb-3">
                      {AI_CONTENT}
                    </div>
                  </div>

                  {/* Engagement Stats */}
                  {animationStep >= 5 && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="px-3 md:px-3.5 lg:px-4 pb-2"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-0 text-slate-900 text-[11px] md:text-xs lg:text-sm border-b border-slate-200 pb-2 md:pb-2.5 lg:pb-3">
                        {/* Reactions - Stack on mobile, inline on larger screens */}
                        <div className="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-1">
                          <div className="flex items-center">
                            <div className="w-4 h-4 md:w-[17px] md:h-[17px] lg:w-[18px] lg:h-[18px] bg-[#0866FF] rounded-full flex items-center justify-center text-[8px] md:text-[9px] lg:text-[10px] border-2 border-white">
                              👍
                            </div>
                            <div className="w-4 h-4 md:w-[17px] md:h-[17px] lg:w-[18px] lg:h-[18px] bg-[#F33E58] rounded-full flex items-center justify-center text-[8px] md:text-[9px] lg:text-[10px] -ml-1 border-2 border-white">
                              ❤️
                            </div>
                            <div className="w-4 h-4 md:w-[17px] md:h-[17px] lg:w-[18px] lg:h-[18px] bg-[#F7B125] rounded-full flex items-center justify-center text-[8px] md:text-[9px] lg:text-[10px] -ml-1 border-2 border-white">
                              😮
                            </div>
                          </div>
                          <span className="ml-0 sm:ml-0.5 md:ml-0.5 lg:ml-1 font-semibold">
                            <RollingNumber 
                              value={engagement.likes} 
                              format={(n) => n > 0 ? `${(n / 1000).toFixed(1)}K` : '0'}
                            />
                          </span>
                        </div>
                        
                        {/* Comments and Shares */}
                        <div className="flex items-center gap-2 sm:gap-3 text-[10px] sm:text-[11px] md:text-xs lg:text-sm text-slate-600">
                          <span className="font-medium">
                            <span className="text-slate-900 font-semibold">
                              <RollingNumber 
                                value={engagement.comments} 
                                format={(n) => n.toString()}
                              />
                            </span> comments
                          </span>
                          <span className="font-medium">
                            <span className="text-slate-900 font-semibold">
                              <RollingNumber 
                                value={engagement.shares} 
                                format={(n) => n > 0 ? `${(n / 1000).toFixed(1)}K` : '0'}
                              />
                            </span> shares
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {/* Action Buttons */}
                  {animationStep >= 5 && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="px-1 @[280px]:px-2 @[320px]:px-3 @[400px]:px-4 py-1 flex items-center justify-around gap-1"
                    >
                      <button className="flex items-center justify-center gap-0.5 @[280px]:gap-1 @[400px]:gap-1.5 @[500px]:gap-2 px-2 @[280px]:px-2 @[320px]:px-2.5 @[400px]:px-3 @[500px]:px-4 py-1.5 @[400px]:py-2 hover:bg-slate-100 rounded-md transition-colors text-slate-700 flex-1 min-w-0">
                        <span className="text-base @[280px]:text-base @[400px]:text-lg @[500px]:text-xl flex-shrink-0">👍</span>
                        <span className="font-semibold text-[10px] @[280px]:text-xs @[400px]:text-[13px] @[500px]:text-sm hidden @[280px]:inline truncate">Like</span>
                      </button>
                      <button className="flex items-center justify-center gap-0.5 @[280px]:gap-1 @[400px]:gap-1.5 @[500px]:gap-2 px-2 @[280px]:px-2 @[320px]:px-2.5 @[400px]:px-3 @[500px]:px-4 py-1.5 @[400px]:py-2 hover:bg-slate-100 rounded-md transition-colors text-slate-700 flex-1 min-w-0">
                        <span className="text-base @[280px]:text-base @[400px]:text-lg @[500px]:text-xl flex-shrink-0">💬</span>
                        <span className="font-semibold text-[10px] @[280px]:text-xs @[400px]:text-[13px] @[500px]:text-sm hidden @[280px]:inline truncate">Comment</span>
                      </button>
                      <button className="flex items-center justify-center gap-0.5 @[280px]:gap-1 @[400px]:gap-1.5 @[500px]:gap-2 px-2 @[280px]:px-2 @[320px]:px-2.5 @[400px]:px-3 @[500px]:px-4 py-1.5 @[400px]:py-2 hover:bg-slate-100 rounded-md transition-colors text-slate-700 flex-1 min-w-0">
                        <span className="text-base @[280px]:text-base @[400px]:text-lg @[500px]:text-xl flex-shrink-0">↗️</span>
                        <span className="font-semibold text-[10px] @[280px]:text-xs @[400px]:text-[13px] @[500px]:text-sm hidden @[280px]:inline truncate">Share</span>
                      </button>
                    </motion.div>
                  )}
                </motion.div>
              )}

              {/* Copy Animation Overlay */}
              <AnimatePresence>
                {showCopyAnimation && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.5, x: -100 }}
                    animate={{ opacity: 1, scale: 1, x: 0 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-blue-500 text-white px-6 py-3 rounded-lg shadow-2xl font-semibold text-lg z-10"
                  >
                    📋 Copied!
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </div>
        )}

        {/* Step 3: The Black Hole - No connection */}
        {animationStep >= 6 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-300 rounded-xl p-6 shadow-lg mb-6"
            data-animation="connection-lost"
          >
            <div className="text-center">
              <div className="text-5xl mb-3">⚠️</div>
              <div className="text-xl font-bold text-red-700 mb-2">Connection Lost</div>
              <div className="text-slate-700 mb-4">
                Your AI company has <span className="text-red-600 font-semibold">zero visibility</span> into this viral content
              </div>
              <div className="inline-flex items-center gap-2 bg-white rounded-lg px-4 py-2 border border-red-200">
                <span className="text-2xl">❌</span>
                <span className="text-sm text-red-600 font-medium">No analytics connection</span>
              </div>
            </div>
          </motion.div>
        )}

        {/* Step 4: What you're missing */}
        {animationStep >= 7 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-slate-900 text-white rounded-xl p-6 shadow-lg mb-6"
            data-animation="missing-data"
          >
            <div className="text-sm font-semibold text-slate-400 mb-3">What Your R&D Team Can&apos;t See:</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="bg-slate-800 rounded-lg p-3">
                <div className="text-xs text-slate-400">Model ID</div>
                <div className="text-sm font-mono text-red-400">Unknown</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-3">
                <div className="text-xs text-slate-400">Temperature</div>
                <div className="text-sm font-mono text-red-400">Unknown</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-3">
                <div className="text-xs text-slate-400">Prompt Pattern</div>
                <div className="text-sm font-mono text-red-400">Unknown</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-3">
                <div className="text-xs text-slate-400">Performance Data</div>
                <div className="text-sm font-mono text-red-400">Unknown</div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Step 5: The cost */}
        {animationStep >= 8 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
            data-animation="final-cost"
          >
            <div className="inline-block bg-gradient-to-r from-red-600 to-orange-600 text-white rounded-xl px-8 py-6 shadow-xl mb-8">
              <div className="text-3xl font-bold mb-2">$2.7B in R&D</div>
              <div className="text-lg">Flying blind without performance data</div>
            </div>
            <ScrollIndicator delay={0.5} />
          </motion.div>
        )}
      </div>
    </section>
  );
}
