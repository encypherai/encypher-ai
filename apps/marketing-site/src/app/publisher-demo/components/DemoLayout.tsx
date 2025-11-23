'use client';

import { ReactNode, useEffect, useState } from 'react';
import ArticleIframe from './ArticleIframe';
import { useScrollProgress } from '../hooks/useScrollProgress';

interface DemoLayoutProps {
  children: ReactNode;
  activeSection?: number;
}

export default function DemoLayout({ children, activeSection = 1 }: DemoLayoutProps) {
  const [isMobile, setIsMobile] = useState(false);
  const scrollProgress = useScrollProgress();

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 relative">
      {/* Scroll Progress Indicator */}
      <div className="fixed top-0 left-0 w-full h-1 bg-slate-200 z-50">
        <div 
          className="h-full bg-gradient-to-r from-orange-500 to-red-500 transition-all duration-300 ease-out"
          style={{ width: `${scrollProgress}%` }}
        />
      </div>

      {/* Section Progress Dots */}
      <div className="fixed right-4 top-1/2 transform -translate-y-1/2 z-40 space-y-2 opacity-40 hover:opacity-100 transition-opacity">
        {[1, 2, 3, 4, 5, 6].map((section) => (
          <div
            key={section}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              section === activeSection
                ? 'bg-orange-500 scale-110'
                : section < activeSection
                ? 'bg-orange-400'
                : 'bg-slate-400'
            }`}
            title={`Section ${section}`}
          />
        ))}
      </div>

      <div className="max-w-[1920px] mx-auto">
        {isMobile ? (
          // Mobile: Stacked layout
          <div className="flex flex-col">
            <div className="sticky top-16 z-10 h-[40vh] border-b border-slate-200 shadow-lg">
              <ArticleIframe />
            </div>
            <div className="flex-1 pt-4">
              {children}
            </div>
          </div>
        ) : (
          // Desktop: Floating article with main content
          <div className="min-h-screen relative">
            {/* Floating Article Preview - Stationary */}
            <div className="fixed left-8 top-24 w-[380px] h-[calc(100vh-12rem)] z-20 pointer-events-none">
              <div className="relative w-full h-full rounded-3xl overflow-hidden shadow-2xl border-4 border-orange-400 bg-white pointer-events-auto">
                <ArticleIframe />
              </div>
            </div>

            {/* Main Content Area - Scrollable */}
            <div className="ml-[440px] min-h-screen">
              {children}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
