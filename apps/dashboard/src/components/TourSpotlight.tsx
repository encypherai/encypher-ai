'use client';

import { useEffect, useState } from 'react';

interface TourSpotlightProps {
  active: boolean;
  targetSelector?: string;
  message: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  onNext?: () => void;
  onSkip?: () => void;
  showSkip?: boolean;
  nextLabel?: string;
}

export function TourSpotlight({
  active,
  targetSelector,
  message,
  position = 'bottom',
  onNext,
  onSkip,
  showSkip = true,
  nextLabel = 'Next',
}: TourSpotlightProps) {
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

  useEffect(() => {
    if (!active || !targetSelector) {
      setTargetRect(null);
      return;
    }

    const updatePosition = () => {
      const element = document.querySelector(targetSelector);
      if (element) {
        setTargetRect(element.getBoundingClientRect());
      }
    };

    updatePosition();
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition);

    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition);
    };
  }, [active, targetSelector]);

  if (!active) return null;

  const getTooltipPosition = () => {
    if (!targetRect) return { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' };

    const padding = 16;
    const tooltipOffset = 12;

    switch (position) {
      case 'top':
        return {
          top: `${targetRect.top - tooltipOffset}px`,
          left: `${targetRect.left + targetRect.width / 2}px`,
          transform: 'translate(-50%, -100%)',
        };
      case 'bottom':
        return {
          top: `${targetRect.bottom + tooltipOffset}px`,
          left: `${targetRect.left + targetRect.width / 2}px`,
          transform: 'translate(-50%, 0)',
        };
      case 'left':
        return {
          top: `${targetRect.top + targetRect.height / 2}px`,
          left: `${targetRect.left - tooltipOffset}px`,
          transform: 'translate(-100%, -50%)',
        };
      case 'right':
        return {
          top: `${targetRect.top + targetRect.height / 2}px`,
          left: `${targetRect.right + tooltipOffset}px`,
          transform: 'translate(0, -50%)',
        };
      default:
        return {
          top: `${targetRect.bottom + tooltipOffset}px`,
          left: `${targetRect.left + targetRect.width / 2}px`,
          transform: 'translate(-50%, 0)',
        };
    }
  };

  return (
    <>
      {/* Four overlay panels that don't cover the target */}
      {targetRect && (
        <>
          {/* Top overlay */}
          <div
            className="fixed left-0 right-0 bg-black/60 z-[9998]"
            style={{
              top: 0,
              height: `${targetRect.top - 8}px`,
              pointerEvents: 'none',
            }}
          />
          
          {/* Bottom overlay */}
          <div
            className="fixed left-0 right-0 bg-black/60 z-[9998]"
            style={{
              top: `${targetRect.bottom + 8}px`,
              bottom: 0,
              pointerEvents: 'none',
            }}
          />
          
          {/* Left overlay */}
          <div
            className="fixed bg-black/60 z-[9998]"
            style={{
              top: `${targetRect.top - 8}px`,
              left: 0,
              width: `${targetRect.left - 8}px`,
              height: `${targetRect.height + 16}px`,
              pointerEvents: 'none',
            }}
          />
          
          {/* Right overlay */}
          <div
            className="fixed bg-black/60 z-[9998]"
            style={{
              top: `${targetRect.top - 8}px`,
              left: `${targetRect.right + 8}px`,
              right: 0,
              height: `${targetRect.height + 16}px`,
              pointerEvents: 'none',
            }}
          />

          {/* Highlight ring around target */}
          <div
            className="fixed z-[9999] pointer-events-none"
            style={{
              top: `${targetRect.top - 8}px`,
              left: `${targetRect.left - 8}px`,
              width: `${targetRect.width + 16}px`,
              height: `${targetRect.height + 16}px`,
              border: '3px solid rgba(59, 130, 246, 0.8)',
              borderRadius: '8px',
              boxShadow: '0 0 20px 4px rgba(59, 130, 246, 0.5)',
              animation: 'pulse 2s ease-in-out infinite',
            }}
          />
        </>
      )}

      {/* Tooltip */}
      <div
        className="fixed z-[10000] max-w-sm"
        style={getTooltipPosition()}
      >
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700 p-4">
          <p className="text-sm text-slate-700 dark:text-slate-300 mb-3">{message}</p>
          <div className="flex gap-2 justify-end">
            {showSkip && onSkip && (
              <button
                onClick={onSkip}
                className="px-3 py-1.5 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
              >
                Skip Tour
              </button>
            )}
            {onNext && nextLabel && (
              <button
                onClick={onNext}
                className="px-4 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
              >
                {nextLabel}
              </button>
            )}
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes pulse {
          0%, 100% {
            box-shadow: 0 0 20px 4px rgba(59, 130, 246, 0.5);
          }
          50% {
            box-shadow: 0 0 30px 8px rgba(59, 130, 246, 0.8);
          }
        }
      `}</style>
    </>
  );
}
