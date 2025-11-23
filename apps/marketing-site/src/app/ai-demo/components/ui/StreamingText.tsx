'use client';

import { useState, useEffect } from 'react';

interface StreamingTextProps {
  text: string;
  speed?: number; // characters per interval
  onComplete?: () => void;
}

export default function StreamingText({ text, speed = 3, onComplete }: StreamingTextProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timer = setTimeout(() => {
        setDisplayedText(text.slice(0, currentIndex + speed));
        setCurrentIndex(currentIndex + speed);
      }, 30); // 30ms interval for smooth streaming

      return () => clearTimeout(timer);
    } else if (onComplete && currentIndex >= text.length) {
      onComplete();
    }
  }, [currentIndex, text, speed, onComplete]);

  return (
    <>
      {displayedText}
      {currentIndex < text.length && (
        <span className="inline-block w-1 h-4 bg-blue-600 ml-0.5 animate-pulse" />
      )}
    </>
  );
}
