import { useState, useEffect } from 'react';

interface AnimationStep {
  step: number;
  duration: number;
}

export function useAnimationState(
  isActive: boolean,
  steps: AnimationStep[]
): number {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (!isActive) {
      setCurrentStep(0);
      return;
    }

    let timeoutId: NodeJS.Timeout;
    let currentIndex = 0;

    const executeNextStep = () => {
      if (currentIndex < steps.length) {
        setCurrentStep(steps[currentIndex].step);
        timeoutId = setTimeout(() => {
          currentIndex++;
          executeNextStep();
        }, steps[currentIndex].duration);
      }
    };

    executeNextStep();

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [isActive, steps]);

  return currentStep;
}
