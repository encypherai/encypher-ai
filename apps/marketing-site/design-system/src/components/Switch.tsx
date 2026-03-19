/**
 * Encypher Switch Component
 * Toggle switch for boolean settings
 */

import * as React from 'react';
import { cn } from '../utils/cn';

export interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  id?: string;
}

const trackSizes = {
  sm: 'h-4 w-8',
  md: 'h-5 w-10',
  lg: 'h-6 w-12',
} as const;

const thumbSizes = {
  sm: 'h-3 w-3',
  md: 'h-4 w-4',
  lg: 'h-5 w-5',
} as const;

const thumbTranslate = {
  sm: 'translate-x-4',
  md: 'translate-x-5',
  lg: 'translate-x-6',
} as const;

export const Switch = React.forwardRef<HTMLButtonElement, SwitchProps>(
  ({ checked, onChange, disabled = false, size = 'md', label, id }, ref) => {
    return (
      <div className="inline-flex items-center gap-2">
        <button
          ref={ref}
          id={id}
          type="button"
          role="switch"
          aria-checked={checked}
          disabled={disabled}
          onClick={() => onChange(!checked)}
          className={cn(
            'relative inline-flex shrink-0 cursor-pointer rounded-full',
            'transition-all duration-200',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
            'disabled:cursor-not-allowed disabled:opacity-50',
            trackSizes[size],
            checked ? 'bg-blue-ncs' : 'bg-muted',
          )}
        >
          <span
            className={cn(
              'pointer-events-none inline-block rounded-full bg-white shadow-sm',
              'transition-transform duration-200',
              thumbSizes[size],
              'translate-x-0.5 translate-y-0.5',
              checked && thumbTranslate[size],
            )}
          />
        </button>
        {label && (
          <label
            htmlFor={id}
            className={cn(
              'text-sm font-medium leading-none',
              disabled && 'cursor-not-allowed opacity-50',
            )}
          >
            {label}
          </label>
        )}
      </div>
    );
  }
);

Switch.displayName = 'Switch';
