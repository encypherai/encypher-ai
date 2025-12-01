'use client';

import { useState, useEffect } from 'react';
import { Button } from '@encypher/design-system';
import Link from 'next/link';

const ONBOARDING_STORAGE_KEY = 'encypher_onboarding_completed';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  action?: {
    label: string;
    href: string;
  };
  completed?: boolean;
}

const onboardingSteps: OnboardingStep[] = [
  {
    id: 'welcome',
    title: 'Welcome to Encypher!',
    description: 'You\'re all set up and ready to start authenticating your AI-generated content with cryptographic signatures.',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
      </svg>
    ),
  },
  {
    id: 'api-key',
    title: 'Create your first API key',
    description: 'Generate an API key to start signing and verifying content. Keep it safe - you\'ll only see it once!',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
      </svg>
    ),
    action: {
      label: 'Create API Key',
      href: '/api-keys',
    },
  },
  {
    id: 'docs',
    title: 'Explore the documentation',
    description: 'Learn how to integrate Encypher into your applications with our comprehensive guides and API reference.',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
    action: {
      label: 'View Docs',
      href: 'https://docs.encypherai.com',
    },
  },
  {
    id: 'complete',
    title: 'You\'re ready to go!',
    description: 'Start authenticating your content and building trust with your audience. We\'re here to help if you need anything.',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
];

interface OnboardingModalProps {
  isNewUser?: boolean;
}

export function OnboardingModal({ isNewUser = false }: OnboardingModalProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    // Check if onboarding has been completed
    const completed = localStorage.getItem(ONBOARDING_STORAGE_KEY);
    if (!completed && isNewUser) {
      // Small delay to let the page load
      const timer = setTimeout(() => setIsOpen(true), 500);
      return () => clearTimeout(timer);
    }
  }, [isNewUser]);

  const handleNext = () => {
    if (currentStep < onboardingSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handleSkip = () => {
    localStorage.setItem(ONBOARDING_STORAGE_KEY, 'true');
    setIsOpen(false);
  };

  const handleComplete = () => {
    setShowConfetti(true);
    localStorage.setItem(ONBOARDING_STORAGE_KEY, 'true');
    setTimeout(() => {
      setIsOpen(false);
      setShowConfetti(false);
    }, 2000);
  };

  if (!isOpen) return null;

  const step = onboardingSteps[currentStep];
  const isLastStep = currentStep === onboardingSteps.length - 1;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        {/* Modal */}
        <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden animate-in fade-in zoom-in-95 duration-300">
          {/* Progress bar */}
          <div className="h-1 bg-slate-100">
            <div
              className="h-full bg-gradient-to-r from-blue-ncs to-delft-blue transition-all duration-500"
              style={{ width: `${((currentStep + 1) / onboardingSteps.length) * 100}%` }}
            />
          </div>

          {/* Content */}
          <div className="p-8 text-center">
            {/* Icon */}
            <div className={`w-16 h-16 mx-auto mb-6 rounded-2xl flex items-center justify-center ${
              isLastStep 
                ? 'bg-green-100 text-green-600' 
                : 'bg-blue-ncs/10 text-blue-ncs'
            }`}>
              {step.icon}
            </div>

            {/* Title */}
            <h2 className="text-2xl font-bold text-delft-blue mb-3">
              {step.title}
            </h2>

            {/* Description */}
            <p className="text-slate-600 mb-8 leading-relaxed">
              {step.description}
            </p>

            {/* Action button (if step has one) */}
            {step.action && (
              <div className="mb-6">
                {step.action.href.startsWith('http') ? (
                  <a
                    href={step.action.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-lg transition-colors"
                  >
                    {step.action.label}
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                ) : (
                  <Link
                    href={step.action.href}
                    onClick={() => setIsOpen(false)}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-lg transition-colors"
                  >
                    {step.action.label}
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                )}
              </div>
            )}

            {/* Navigation buttons */}
            <div className="flex items-center justify-between">
              <button
                onClick={handleSkip}
                className="text-sm text-slate-500 hover:text-slate-700 transition-colors"
              >
                Skip tour
              </button>

              <div className="flex items-center gap-3">
                {/* Step indicators */}
                <div className="flex gap-1.5">
                  {onboardingSteps.map((_, idx) => (
                    <div
                      key={idx}
                      className={`w-2 h-2 rounded-full transition-colors ${
                        idx === currentStep
                          ? 'bg-blue-ncs'
                          : idx < currentStep
                          ? 'bg-blue-ncs/50'
                          : 'bg-slate-200'
                      }`}
                    />
                  ))}
                </div>

                <Button
                  variant="primary"
                  onClick={handleNext}
                  className="min-w-[100px]"
                >
                  {isLastStep ? 'Get Started' : 'Next'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Confetti effect on completion */}
      {showConfetti && (
        <div className="fixed inset-0 z-[60] pointer-events-none overflow-hidden">
          {[...Array(50)].map((_, i) => (
            <div
              key={i}
              className="absolute animate-confetti"
              style={{
                left: `${Math.random() * 100}%`,
                top: '-10px',
                animationDelay: `${Math.random() * 0.5}s`,
                backgroundColor: ['#1B3A5F', '#2E6DB4', '#8ECAE6', '#FFD700', '#FF6B6B'][Math.floor(Math.random() * 5)],
                width: `${Math.random() * 10 + 5}px`,
                height: `${Math.random() * 10 + 5}px`,
                borderRadius: Math.random() > 0.5 ? '50%' : '0',
              }}
            />
          ))}
        </div>
      )}

      <style jsx>{`
        @keyframes confetti {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
          }
        }
        .animate-confetti {
          animation: confetti 3s ease-out forwards;
        }
      `}</style>
    </>
  );
}

// Hook to check if user is new (for use in dashboard)
export function useIsNewUser(): boolean {
  const [isNew, setIsNew] = useState(false);

  useEffect(() => {
    const completed = localStorage.getItem(ONBOARDING_STORAGE_KEY);
    setIsNew(!completed);
  }, []);

  return isNew;
}

// Function to reset onboarding (for testing)
export function resetOnboarding() {
  localStorage.removeItem(ONBOARDING_STORAGE_KEY);
}
