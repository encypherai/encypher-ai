'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';

interface RollingNumberProps {
  value: number;
  format?: (n: number) => string;
}

export default function RollingNumber({ value, format = (n) => n.toString() }: RollingNumberProps) {
  const [displayValue, setDisplayValue] = useState(0);
  const [prevValue, setPrevValue] = useState(0);

  useEffect(() => {
    if (value !== prevValue) {
      setPrevValue(displayValue);
      setDisplayValue(value);
    }
  }, [value, prevValue, displayValue]);

  const formattedValue = format(displayValue);
  const formattedPrev = format(prevValue);

  return (
    <div className="inline-block relative overflow-hidden">
      <AnimatePresence mode="popLayout">
        <motion.span
          key={displayValue}
          initial={{ y: 20 }}
          animate={{ y: 0 }}
          exit={{ y: -20 }}
          transition={{ 
            type: "spring",
            stiffness: 300,
            damping: 30,
            duration: 0.3
          }}
          className="inline-block"
        >
          {formattedValue}
        </motion.span>
      </AnimatePresence>
    </div>
  );
}
